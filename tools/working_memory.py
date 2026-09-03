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

    important_fact: str | None = None,
) -> str | Command:
    """
    更新当前 Thread 的 Working Memory。

    当当前用户明确建立或修改当前任务目标、
    当前正在执行的任务，
    或提供后续完成当前任务仍然需要的重要事实时，
    使用这个工具。

    这是当前 Thread 的短期工作记忆，
    不是用户长期记忆。

    Args:
        current_goal:
            当前 Thread 的总体目标。
            只有目标发生变化或需要明确建立目标时填写。

        current_task:
            当前正在执行的具体任务。
            只有当前步骤发生变化时填写。

        important_fact:
            当前任务后续仍然需要使用的一条重要事实。
            不要保存闲聊、重复信息或无关信息。
    """

    update = {}

    # =====================================
    # 1. Goal
    # =====================================

    if current_goal:

        update[
            "current_goal"
        ] = current_goal.strip()

    # =====================================
    # 2. Current Task
    # =====================================

    if current_task:

        update[
            "current_task"
        ] = current_task.strip()

    # =====================================
    # 3. Important Facts
    # =====================================

    if important_fact:

        fact = (
            important_fact.strip()
        )

        existing_facts = list(
            runtime.state.get(
                "important_facts",
                [],
            )
        )

        # 防止重复
        if (
            fact
            and fact
            not in existing_facts
        ):

            existing_facts.append(
                fact
            )

        update[
            "important_facts"
        ] = existing_facts

    # =====================================
    # 4. 没有真正更新
    # =====================================

    if not update:

        return (
            "没有提供需要更新的 "
            "Working Memory 内容。"
        )

    # =====================================
    # 5. State Update
    # =====================================

    return Command(
        update={
            **update,

            # Tool Call 必须有对应结果消息
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