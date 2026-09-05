from memory.models import (
    MemoryItem,
)


def memory_rows_to_items(
    rows,
) -> list[MemoryItem]:

    items = []

    for row in rows:

        items.append(
            MemoryItem(
                key=(
                    row[
                        "memory_key"
                    ]
                ),

                value=(
                    row[
                        "memory_value"
                    ]
                ),

                source_type=(
                    row[
                        "source_type"
                    ]
                ),

                confidence=float(
                    row[
                        "confidence"
                    ]
                ),

                updated_at=(
                    row[
                        "updated_at"
                    ]
                ),
            )
        )

    return items


def build_user_memory_context(
    items: list[MemoryItem],
) -> str:

    if not items:
        return ""

    lines = []

    for item in items:

        lines.append(
            (
                f"{item.key}: "
                f"{item.value}"
            )
        )

    return "\n".join(
        lines
    )