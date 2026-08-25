def build_recent_group_context(
    messages,
) -> str:

    if not messages:
        return "最近没有普通群聊记录。"

    lines = []

    for message in messages:

        sender = (
            message["sender_name"]
            or "群成员"
        )

        created_at = message["created_at"]

        content = message["content"]

        lines.append(
            f"[{created_at}] "
            f"{sender}：{content}"
        )

    return "\n".join(lines)