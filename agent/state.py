from langchain.agents import (
    AgentState,
)

from typing_extensions import (
    NotRequired,
)


class WeChatAgentState(
    AgentState
):
    """
    当前 Thread 的短期状态。

    AgentState 本身已经有 messages。
    """

    # Thread总体目标
    current_goal: NotRequired[str]

    # 当前正在做的步骤
    current_task: NotRequired[str]

    # 当前任务仍然需要使用的关键事实
    #
    # key   = 事实名称
    # value = 当前事实内容
    important_facts: NotRequired[
        dict[str, str]
    ]