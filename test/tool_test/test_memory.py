from database.repository import (
    upsert_user_memory,
    revoke_user_memory,
    get_user_memories,
    get_user_memory_events,
)

from time import sleep


print(
    upsert_user_memory(
        external_user_id="test-user",

        memory_key="response_style",

        memory_value="简洁",

        source_type="explicit_user",

        confidence=1.0,
    )
)
sleep(5)

print(
    upsert_user_memory(
        "test-user",
        "response_style",
        "详细",
        "explicit_user",
        1.0,
    )
)
sleep(5)
print(
    upsert_user_memory(
        "test-user",
        "response_style",
        "详细",
        "explicit_user",
        1.0,
    )
)
sleep(5)
print(
    revoke_user_memory(
        "test-user",
        "response_style",
    )
)
sleep(5)
print(
    upsert_user_memory(
        "test-user",
        "response_style",
        "详细",
        "explicit_user",
        1.0,
    )
)
sleep(5)
events = (
    get_user_memory_events(
        "test-user"
    )
)

for event in reversed(
    events
):

    print(
        dict(event)
    )