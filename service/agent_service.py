from agent.request import AgentRequest
from agent.response import AgentResponse
from agent.core import ask_agent

from database.repository import (
    get_recent_ambient_messages,
    get_user_memories,
    save_message,
)

from memory.context_builder import (
    build_recent_group_context,
)


def handle_agent_request(
    request: AgentRequest
) -> AgentResponse:

    # =============================
    # 1. Thread
    # =============================

    thread_id = (
        request.conversation_id
        or f"{request.channel}:default"
    )

    # =============================
    # 2. 最近群聊上下文
    # =============================

    recent_group_context = ""

    if request.group_id:

        recent_messages = (
            get_recent_ambient_messages(
                group_name=request.group_id,
                limit=20,
            )
        )

        recent_group_context = (
            build_recent_group_context(
                recent_messages
            )
        )

    # =============================
    # 3. 用户长期 Memory
    # =============================

    user_memory = ""

    if request.user_id:

        rows = get_user_memories(
            request.user_id
        )

        user_memory = "\n".join(
            f"{row['memory_key']}："
            f"{row['memory_value']}"
            for row in rows
        )

    # =============================
    # 4. 调 Agent
    # =============================

    answer = ask_agent(
        user_message=request.message,

        thread_id=thread_id,

        group_name=(
            request.group_id or ""
        ),

        recent_group_context=(
            recent_group_context
        ),

        user_id=request.user_id,

        user_memory=user_memory,
    )

    # =============================
    # 5. 保存 AI 回复
    # =============================

    if request.group_id:

        save_message(
            group_name=request.group_id,
            content=answer,
            role="assistant",
            sender_name="AI Agent",
        )

    # =============================
    # 6. 返回统一 Response
    # =============================

    return AgentResponse(
        text=answer,
        thread_id=thread_id,
        metadata={
            "channel": request.channel,
        },
    )