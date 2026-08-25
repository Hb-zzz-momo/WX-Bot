from database.repository import (
    get_enabled_groups,
    get_recent_messages,
)


groups = get_enabled_groups()


for group in groups:

    group_name = group["name"]

    print()
    print("=" * 70)
    print(group_name)
    print("=" * 70)

    messages = get_recent_messages(
        group_name,
        limit=20,
    )

    for message in messages:

        print(
            f"[{message['role']}] "
            f"{message['content']}"
        )