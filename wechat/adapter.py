from agent.request import AgentRequest
from wechat.identity import resolve_user_id


def to_agent_request(event) -> AgentRequest:
    """
    把 wx4py 的消息事件转换成 AgentRequest。
    """

    group_name = str(event.group)
    content = str(event.content)

    user_id = resolve_user_id(event)

    return AgentRequest(
        channel="wechat",

        message=content,

        group_id=group_name,

        user_id=user_id,

        conversation_id=(
            f"wechat-group:{group_name}"
        ),

        # wx4py 目前如果没有稳定 message_id，
        # 先保留为空。
        message_id=None,
    )