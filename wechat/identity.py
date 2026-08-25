def resolve_user_id(event) -> str | None:
    """
    获取当前群消息发送者唯一 ID。

    当前 wx4py 无法稳定提供发送者 ID，
    所以暂时返回 None。

    后续如果找到可靠的 sender_id 来源，
    只需要修改这个函数。
    """

    return None