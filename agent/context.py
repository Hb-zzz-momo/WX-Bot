from dataclasses import dataclass


@dataclass
class AgentContext:

    group_name: str

    recent_group_context: str = ""

    # 当前发送者
    user_id: str | None = None

    # 当前用户长期Memory
    user_memory: str = ""