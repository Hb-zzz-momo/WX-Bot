from context_engine.selector import (
    extract_query_terms,
)

from memory.models import (
    MemoryItem,
)

# ==========================================
# 无论当前问题是什么，
# 都通常值得保留的少数全局Preference
# ==========================================

ALWAYS_ON_MEMORY_KEYS = {
    "response_style",
    "preferred_language",
    "preferred_name",
}


def calculate_memory_relevance(
    item: MemoryItem,
    terms: list[str],
) -> float:

    text = (
        f"{item.key} "
        f"{item.value}"
    ).lower()

    score = 0.0

    for term in terms:

        if term in text:
            score += 1.0

    return score

def select_user_memories(
    items: list[MemoryItem],
    query: str,
    limit: int = 8,
) -> list[MemoryItem]:
    """
    从用户长期Memory中，
    选出当前问题真正需要的内容。

    和Group Context不同：
    不使用recent_fallback。
    """

    if not items:
        return []

    terms = (
        extract_query_terms(
            query
        )
    )

    selected = []

    # ======================================
    # 1. 全局Preference
    # ======================================

    for item in items:

        if (
            item.key
            in ALWAYS_ON_MEMORY_KEYS
        ):

            item.relevance_score = (
                100.0
            )

            selected.append(
                item
            )

    # ======================================
    # 2. Query Relevance
    # ======================================

    relevant = []

    for item in items:

        if item in selected:
            continue

        item.relevance_score = (
            calculate_memory_relevance(
                item,
                terms,
            )
        )

        if (
            item.relevance_score > 0
        ):
            relevant.append(
                item
            )

    relevant.sort(
        key=lambda item: (
            item.relevance_score,
            item.confidence,
        ),
        reverse=True,
    )

    for item in relevant:

        if len(selected) >= limit:
            break

        selected.append(
            item
        )

    return selected[:limit]