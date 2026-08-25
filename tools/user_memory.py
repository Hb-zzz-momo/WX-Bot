from langchain.tools import (
    ToolRuntime,
    tool,
)

from agent.context import AgentContext

from database.repository import (
    upsert_user_memory,
)


@tool
def remember_user_memory(
    memory_key: str,
    memory_value: str,
    runtime: ToolRuntime[AgentContext],
) -> str:
    """
    保存当前用户明确要求长期记住的信息。

    只有用户明确要求“记住”“以后按照这个偏好”等
    长期信息时才应该调用。

    Args:
        memory_key:
            简洁的记忆类别。

        memory_value:
            需要长期保存的内容。
    """

    user_id = runtime.context.user_id

    if not user_id:

        return (
            "当前无法可靠识别微信群消息发送者，"
            "因此不能安全地保存用户级长期记忆。"
        )

    upsert_user_memory(
        external_user_id=user_id,
        memory_key=memory_key,
        memory_value=memory_value,
    )

    return (
        f"已经保存用户记忆："
        f"{memory_key} = {memory_value}"
    )