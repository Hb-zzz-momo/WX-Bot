from langchain.agents import AgentState

from typing_extensions import (
    NotRequired,
)


class WeChatAgentState(
    AgentState
):
    """
    微信 Agent 的 Thread State。

    AgentState 已经自带：
    - messages

    我们额外加入 Working Memory。
    """

    # 当前 Thread 的总体目标
    current_goal: NotRequired[str]

    # 当前正在执行的任务
    current_task: NotRequired[str]

    # 当前任务中后续仍需要使用的重要事实
    important_facts: NotRequired[
        list[str]
    ]