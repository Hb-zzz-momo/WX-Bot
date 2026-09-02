from context_engine.models import (
    ContextItem,
)


# =============================
# 1. 数据库 Row
#    → ContextItem
# =============================

def group_rows_to_context_items(
    rows,
) -> list[ContextItem]:

    items: list[ContextItem] = []

    for row in rows:

        sender = (
            row["sender_name"]
            or "群成员"
        )

        content = row["content"]

        created_at = row["created_at"]

        # =====================
        # 注意：
        # sender只是数据内容，
        # 不代表这个人具有Agent权限。
        # =====================

        item = ContextItem(
            content=(
                f"{sender}：{content}"
            ),

            source="group_chat",

            trust_level="untrusted",

            timestamp=str(
                created_at
            ),
        )

        items.append(item)

    return items


# =============================
# 2. Selected Items
#    → 最终字符串
# =============================

def build_group_context(
    items: list[ContextItem],
) -> str:

    if not items:

        return (
            "没有找到与当前问题"
            "明显相关的群聊背景。"
        )

    lines = []

    for item in items:

        timestamp = (
            item.timestamp
            or "未知时间"
        )

        lines.append(
            f"[{timestamp}] "
            f"{item.content}"
        )

    return "\n".join(lines)