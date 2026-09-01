from dataclasses import dataclass, field


@dataclass
class AgentResponse:
    text: str

    thread_id: str | None = None

    metadata: dict = field(
        default_factory=dict
    )