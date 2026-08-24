import os

from dotenv import load_dotenv
from wx4py import AsyncCallbackHandler, WeChatClient

from agent.core import ask_agent

load_dotenv()

GROUPS = [
    "我和我老婆"
]

BOT_NAMES = tuple(
    name.strip()
    for name in os.getenv("BOT_NICKNAME", "").split(",")
    if name.strip()
)


def ai_reply(event):
    """
    微信群有新消息时执行
    """

    print("=" * 60)
    print("收到消息")
    print("群聊：", event.group)
    print("内容：", event.content)
    print("是否@我：", event.is_at_me)
    print("被@名单：", event.mentioned)

    # 没 @ 机器人，不回复
    if not event.is_at_me:
        return ""

    try:
        print("正在调用 Agent...")

        thread_id = (
            f"wechat-group:{event.group}"
        )
        print(
            "当前Thread:",
            thread_id
        )
        answer = ask_agent(
            user_message=event.content,
            thread_id=thread_id,
        )

        print("Agent回答：")
        print(answer)

        return answer

    except Exception as e:
        print("Agent发生异常：", e)

        return "🤖 Agent 暂时出现了一点问题，请稍后再试。"


def run_wechat_bot():
    print("正在启动微信 Agent...")
    if not BOT_NAMES:
        print("警告：未配置 BOT_NICKNAME（.env），@ 判定将依赖群昵称自动读取")

    with WeChatClient(auto_connect=True) as wx:
        print("微信连接成功")

        wx.process_groups(
            GROUPS,
            [
                AsyncCallbackHandler(
                    ai_reply,
                    auto_reply=True,
                    reply_on_at=True,
                )
            ],
            block=True,
            bot_names=BOT_NAMES,
        )