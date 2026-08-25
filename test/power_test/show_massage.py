from database.repository import (
    get_recent_messages
)


GROUP_NAME = "我和我老婆"


messages = get_recent_messages(
    GROUP_NAME,
    limit=50,
)


for message in messages:

    print(
        message["role"],
        "：",
        message["content"],
    )