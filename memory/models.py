from dataclasses import (
    dataclass,
)


@dataclass
class MemoryItem:

    key: str

    value: str

    source_type: str

    confidence: float

    updated_at: str | None = None

    relevance_score: float = 0.0