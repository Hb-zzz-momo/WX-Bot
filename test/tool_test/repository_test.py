from database.repository import (
    upsert_user_memory,
    get_active_user_memory,
    get_user_memories,
    revoke_user_memory,
)

from memory.validator import (
    normalize_memory_key,
)

upsert_user_memory(
    "test-user",
    "response_style",
    "简洁",
    "explicit_user",
    1.0,
)

row = get_active_user_memory(
    "test-user",
    "response_style",
)

print(
    dict(row)
)

print(
    normalize_memory_key(
        "answer_style"
    )
)

print(
    normalize_memory_key(
        "reply-style"
    )
)

upsert_user_memory(
    "test-user",
    "response_style",
    "简洁",
    "explicit_user",
    1.0,
)

upsert_user_memory(
    "test-user",
    "database_project",
    "正在开发WX-Bot",
    "explicit_user",
    1.0,
)

upsert_user_memory(
    "test-user",
    "favorite_food",
    "火锅",
    "explicit_user",
    1.0,
)

upsert_user_memory(
    "test-user",
    "preferred_language",
    "中文",
    "explicit_user",
    1.0,
)

rows = get_user_memories(
    "test-user"
)

items = memory_rows_to_items(
    rows
)

selected = select_user_memories(
    items,
    query="WX-Bot数据库现在做到哪里了？",
)

for item in selected:
    print(
        item.key,
        item.value,
        item.relevance_score,
    )