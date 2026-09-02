import re

from context_engine.models import ContextItem


# =============================
# 1. 提取查询关键词
# =============================

def extract_query_terms(
    query: str,
) -> list[str]:
    """
    从用户问题中提取用于 V1 相关性匹配的关键词。

    当前先使用简单规则：
    - 英文/数字作为完整 token
    - 中文使用连续两个字的 bigram

    后续可以替换成：
    Embedding / Vector Search / Reranker
    """

    query = query.lower().strip()

    terms: set[str] = set()

    # -------------------------
    # 英文 / 数字
    # -------------------------

    english_tokens = re.findall(
        r"[a-zA-Z0-9_./-]+",
        query,
    )

    for token in english_tokens:

        if len(token) >= 2:
            terms.add(token)

    # -------------------------
    # 中文
    # -------------------------

    chinese_blocks = re.findall(
        r"[\u4e00-\u9fff]+",
        query,
    )

    for block in chinese_blocks:

        # 如果只有1~2个字，直接保留
        if len(block) <= 2:

            terms.add(block)

            continue

        # 例如：
        #
        # 杭州周六几点集合
        #
        # ↓
        #
        # 杭州
        # 州周
        # 周六
        # 六几
        # 几点
        # 点集
        # 集合

        for index in range(
            len(block) - 1
        ):

            term = block[
                index:index + 2
            ]

            terms.add(term)

    return list(terms)


# =============================
# 2. 单条 Context 相关性评分
# =============================

def calculate_relevance(
    item: ContextItem,
    terms: list[str],
) -> float:

    content = item.content.lower()

    score = 0.0

    for term in terms:

        if term in content:

            score += 1.0

    return score


# =============================
# 3. 选择群聊 Context
# =============================

def select_group_context(
    items: list[ContextItem],
    query: str,
    limit: int = 10,
    recent_fallback: int = 3,
) -> list[ContextItem]:
    """
    从候选群聊中选择和当前问题最相关的信息。

    V1策略：

    1. 计算关键词相关性
    2. 优先选择相关消息
    3. 保留少量最近消息作为兜底
    4. 最多返回 limit 条
    """

    if not items:
        return []

    terms = extract_query_terms(query)

    # =========================
    # 1. 计算相关性
    # =========================

    for item in items:

        item.relevance_score = (
            calculate_relevance(
                item,
                terms,
            )
        )

    # =========================
    # 2. 找出真正相关消息
    # =========================

    relevant_items = [
        item
        for item in items
        if item.relevance_score > 0
    ]

    # 相关性高的优先
    relevant_items.sort(
        key=lambda item: (
            item.relevance_score
        ),
        reverse=True,
    )

    selected = relevant_items[
        :limit
    ]

    # =========================
    # 3. 最近消息兜底
    # =========================

    # 即使关键词没有完全匹配，
    # 仍保留最近几条，
    # 防止完全失去当前聊天语境。

    recent_items = items[
        -recent_fallback:
    ]

    for item in recent_items:

        if item not in selected:

            selected.append(item)

        if len(selected) >= limit:
            break

    # =========================
    # 4. 最后恢复时间顺序
    # =========================

    selected.sort(
        key=lambda item: (
            item.timestamp or ""
        )
    )

    return selected