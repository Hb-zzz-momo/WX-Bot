import os
import time

from dotenv import load_dotenv
from wx4py import AsyncCallbackHandler, WeChatClient,CallbackHandler

from agent.core import ask_agent

from database.repository import (
    get_enabled_groups,
    get_group_config,
    get_recent_ambient_messages,
    save_message,
    get_user_memories,
)

from memory.context_builder import build_recent_group_context

from wechat.identity import resolve_user_id

load_dotenv()



BOT_NAMES = tuple(
    name.strip()
    for name in os.getenv("BOT_NICKNAME", "").split(",")
    if name.strip()
)

# 防回声：同一群相同内容在 N 秒内只允许触发一次
ECHO_DEDUP_WINDOW = 60


def persist_message(event):

    group_name = str(
        event.group
    )

    content = str(
        event.content
    )

    print(
        f"[记录消息] [{group_name}] {content}"
    )

    save_message(
        group_name=group_name,

        content=content,

        role="user",

        # wx4py当前不能稳定获取群消息发送者
        sender_name=None,

        is_at_me=bool(
            event.is_at_me
        ),
    )

    return ""




def ai_reply(event):
    """
    微信群有新消息时执行
    """
    group_name = str(event.group)
    content = str(event.content)
    
    
    # =========================
    # 0. 查询数据库配置
    # =========================

    group_config = get_group_config(
        group_name
    )

    if not group_config:
        return ""

    # 群已停用
    if not group_config["enabled"]:
        return ""

    # 这个群只监听，不启AI
    if not group_config["ai_enabled"]:
        return ""

    # 没有 @机器人
    if not event.is_at_me:
        return ""

    try:

        # =============================
        # 1. 群 Thread Memory
        # =============================

        thread_id = (
            f"wechat-group:{group_name}"
        )

        # =============================
        # 2. 最近普通群聊 Memory
        # =============================

        recent_messages = (
            get_recent_ambient_messages(
                group_name=group_name,
                limit=20,
            )
        )

        recent_group_context = (
            build_recent_group_context(
                recent_messages
            )
        )

        # =============================
        # 3. 用户身份
        # =============================

        user_id = resolve_user_id(
            event
        )
        user_memory = ""

        if user_id is not None:

            rows = get_user_memories(
                user_id
            )

            user_memory = "\n".join(
                f"{row['memory_key']}："
                f"{row['memory_value']}"
                for row in rows
            )

        # =============================
        # 4. Agent
        # =============================

        answer = ask_agent(
            user_message=content,

            thread_id=thread_id,

            group_name=group_name,

            recent_group_context=
                recent_group_context,

            user_id=user_id,

            user_memory=user_memory,
        )

        # =============================
        # 5. 保存AI回复
        # =============================

        save_message(
            group_name=group_name,
            content=answer,
            role="assistant",
            sender_name="AI Agent",
        )

        return answer

    except Exception as e:

        print(
            f"[Agent异常] {e}"
        )

        return "🤖 Agent 暂时出现问题。"


def run_wechat_bot():
    print("正在启动微信 Agent...")
    if not BOT_NAMES:
        print("警告：未配置 BOT_NICKNAME（.env），@ 判定将依赖群昵称自动读取")

    # =========================
    # 1. 从数据库读取监听群
    # =========================

    group_rows = get_enabled_groups()

    groups = [
        row["name"]
        for row in group_rows
    ]

    if not groups:

        raise RuntimeError(
            "数据库中没有启用的微信群。"
            "请先运行 manage_groups.py add"
        )

    print("准备监听以下微信群：")

    for row in group_rows:

        mode = (
            "AI回复"
            if row["ai_enabled"]
            else "仅记录"
        )

        print(
            f"  - {row['name']} [{mode}]"
        )

    # =========================
    # 2. 连接微信
    # =========================

    with WeChatClient(
        auto_connect=True
    ) as wx:

        print("微信连接成功")

        # =========================
        # 3. 一次监听多个群
        # =========================

        wx.process_groups(
            groups,

            [
                # Handler 1：
                # 所有消息进入 business.db
                CallbackHandler(
                    persist_message,
                    auto_reply=False,
                ),

                # Handler 2：
                # 只有 @机器人 才调用Agent
                AsyncCallbackHandler(
                    ai_reply,
                    auto_reply=True,
                    reply_on_at=True,
                ),
            ],

            # 忽略机器人自己发出去的消息回流
            ignore_client_sent=True,

            # @ 判定的名字来源：
            # 1. 优先用 .env 里 BOT_NICKNAME 配置的机器人名（多个群通用）
            # 2. 为空时才尝试自动读取“我在本群的昵称”
            bot_names=BOT_NAMES,

            block=True,
        )