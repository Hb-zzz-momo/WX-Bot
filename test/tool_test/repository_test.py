from database.repository import (
    upsert_user_memory,
    get_user_memories,
    revoke_user_memory,
)

upsert_user_memory(
    external_user_id="test-user-001",

    memory_key="response_style",

    memory_value="回答简洁",

    source_type="explicit_user",

    confidence=1.0,
)

rows = get_user_memories(
    "test-user-001"
)

for row in rows:
    print(dict(row))
    
print(
    revoke_user_memory(
        "test-user-001",
        "response_style",
    )
)

rows = get_user_memories(
    "test-user-001"
)

print(
    [dict(row) for row in rows]
)

upsert_user_memory(
    external_user_id="test-user-001",

    memory_key="response_style",

    memory_value="回答详细",

    source_type="explicit_user",

    confidence=1.0,
)

rows = get_user_memories(
    "test-user-001"
)

print(
    [dict(row) for row in rows]
)

