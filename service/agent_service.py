from agent.request import AgentRequest
from agent.response import AgentResponse
from agent.core import ask_agent

from database.repository import (
    get_recent_ambient_messages,
    get_user_memories,
    save_message,
)

from context_engine.builder import (
    group_rows_to_context_items,
    build_group_context,
)

from context_engine.selector import (
    select_group_context,
)

from memory.selector import (
    select_user_memories,
)

from memory.builder import (
    memory_rows_to_items,
    build_user_memory_context,
)

from service.thread_resolver import (
    resolve_thread_id
)

def handle_agent_request(
    request: AgentRequest
) -> AgentResponse:

    # =============================
    # 1. Thread
    # =============================

    thread_id = resolve_thread_id(request)

    # =============================
    # 2. 群聊 Context
    # =============================

    recent_group_context = ""

    if request.group_id:

        # -------------------------
        # Step 1:
        # 从 DB 获取 Candidate Pool
        # -------------------------

        candidate_rows = (
            get_recent_ambient_messages(
                group_name=request.group_id,

                # 原来直接取20条给LLM。
                # 现在先扩大候选池，
                # 后面再筛选。
                limit=50,
            )
        )

        # -------------------------
        # Step 2:
        # DB Row
        # →
        # ContextItem
        # -------------------------

        candidate_items = (
            group_rows_to_context_items(
                candidate_rows
            )
        )

        # -------------------------
        # Step 3:
        # Context Selector
        # -------------------------

        selected_items = (
            select_group_context(
                items=candidate_items,

                # 当前用户的问题
                # 就是相关性判断依据
                query=request.message,

                # 最终最多给LLM 10条
                limit=10,
            )
        )
        print(
            "[Context Selector]"
        )

        for item in selected_items:

            selection_type = (
                "relevance"
                if item.relevance_score > 0
                else "recent_fallback"
            )

            print(
                f"score="
                f"{item.relevance_score} "
                f"type="
                f"{selection_type} "
                f"source="
                f"{item.source} "
                f"content="
                f"{item.content}"
            )

        # -------------------------
        # Step 4:
        # Context Builder
        # -------------------------

        recent_group_context = (
            build_group_context(
                selected_items
            )
        )

    # =============================
    # 3. 用户长期 Memory
    # =============================

    user_memory = ""

    if request.user_id:

        # =====================================
        # Step 1
        # Long-Term Memory Candidate Pool
        # =====================================

        memory_rows = (
            get_user_memories(
                external_user_id=(
                    request.user_id
                ),
                limit=100,
            )
        )

        # =====================================
        # Step 2
        # DB Row → MemoryItem
        # =====================================

        memory_items = (
            memory_rows_to_items(
                memory_rows
            )
        )

        # =====================================
        # Step 3
        # Retrieval Selector
        # =====================================

        selected_memories = (
            select_user_memories(
                items=memory_items,

                query=request.message,

                limit=8,
            )
        )

        print(
            "[Memory Selector]"
        )

        for item in selected_memories:

            print(
                f"score="
                f"{item.relevance_score} "
                f"key="
                f"{item.key} "
                f"value="
                f"{item.value}"
            )

        # =====================================
        # Step 4
        # Memory Builder
        # =====================================

        user_memory = (
            build_user_memory_context(
                selected_memories
            )
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