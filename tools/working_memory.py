from langchain.tools import (
    tool,
    ToolRuntime,
)

from langchain.messages import (
    ToolMessage,
)

from langgraph.types import (
    Command,
)


@tool
def update_working_memory(
    runtime: ToolRuntime,

    current_goal: str | None = None,

    current_task: str | None = None,

    fact_key: str | None = None,

    fact_value: str | None = None,
) -> str | Command:
    """
    更新当前 Thread 的 Working Memory。

    用于维护当前任务的：
    - 总体目标
    - 当前步骤
    - 后续仍需要使用的重要事实

    fact_key 和 fact_value 必须一起提供。
    """

    update = {}

    # =========================
    # 1. 更新Goal
    # =========================

    if current_goal:

        update[
            "current_goal"
        ] = current_goal.strip()

    # =========================
    # 2. 更新Current Task
    # =========================

    if current_task:

        update[
            "current_task"
        ] = current_task.strip()

    # =========================
    # 3. 更新Fact
    # =========================

    if fact_key and fact_value:

        facts = dict(
            runtime.state.get(
                "important_facts",
                {},
            )
        )

        facts[
            fact_key.strip()
        ] = fact_value.strip()

        update[
            "important_facts"
        ] = facts

    # =========================
    # 4. 没有任何更新
    # =========================

    if not update:

        return (
            "没有提供有效的 "
            "Working Memory 更新。"
        )

    # =========================
    # 5. 返回State Update
    # =========================

    return Command(
        update={
            **update,

            "messages": [
                ToolMessage(
                    content=(
                        "Working Memory "
                        "已更新。"
                    ),

                    tool_call_id=(
                        runtime.tool_call_id
                    ),
                )
            ],
        }
    )
    
@tool
def clear_working_memory(
    runtime: ToolRuntime,

    clear_goal: bool = False,

    clear_task: bool = False,

    fact_key: str | None = None,

    clear_all_facts: bool = False,
) -> str | Command:
    """
    清理当前 Thread 中已经失效的 Working Memory。

    Args:
        clear_goal:
            清除当前总体目标。

        clear_task:
            清除当前正在执行的任务。

        fact_key:
            删除某一条已经过期或错误的重要事实。

        clear_all_facts:
            清除所有当前任务事实。
    """

    update = {}

    # =========================
    # Goal
    # =========================

    if clear_goal:

        update[
            "current_goal"
        ] = ""

    # =========================
    # Current Task
    # =========================

    if clear_task:

        update[
            "current_task"
        ] = ""

    # =========================
    # Facts
    # =========================

    facts = dict(
        runtime.state.get(
            "important_facts",
            {},
        )
    )

    if clear_all_facts:

        facts = {}

        update[
            "important_facts"
        ] = facts

    elif fact_key:

        facts.pop(
            fact_key,
            None,
        )

        update[
            "important_facts"
        ] = facts

    if not update:

        return (
            "没有提供需要清理的 "
            "Working Memory。"
        )

    return Command(
        update={
            **update,

            "messages": [
                ToolMessage(
                    content=(
                        "Working Memory "
                        "已清理。"
                    ),

                    tool_call_id=(
                        runtime.tool_call_id
                    ),
                )
            ],
        }
    )