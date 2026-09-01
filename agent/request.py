from dataclasses import dataclass


@dataclass
class AgentRequest:
    """
    Agent 的统一输入格式。

    不管消息来自：
    - 微信
    - Web
    - Telegram
    - 测试代码

    最后都应该转换成 AgentRequest。
    """

    # 消息来自哪个平台
    channel: str

    # 用户真正发送的文本
    message: str

    # 群 / 频道 ID
    group_id: str | None = None

    # 当前发送者 ID
    user_id: str | None = None

    # 当前会话 ID
    conversation_id: str | None = None

    # 当前消息唯一 ID
    message_id: str | None = None