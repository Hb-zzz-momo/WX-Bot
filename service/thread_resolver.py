from agent.request import AgentRequest


def resolve_thread_id(
    request: AgentRequest
) -> str:

    # 当前拿不到 user_id
    if not request.user_id:

        return (
            request.conversation_id
            or f"{request.channel}:anonymous"
        )

    return (
        f"{request.channel}:"
        f"{request.group_id or 'private'}:"
        f"user:{request.user_id}"
    )