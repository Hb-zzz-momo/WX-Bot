from database.db import init_database

from database.repository import (
    get_recent_messages,
    save_message,
)


GROUP_NAME = "数据库测试群"


def main():

    init_database()

    save_message(
        group_name=GROUP_NAME,
        content="我正在学习HDFS",
        role="user",
        sender_name="测试用户",
    )

    save_message(
        group_name=GROUP_NAME,
        content="好的。",
        role="assistant",
        sender_name="AI Agent",
    )

    messages = get_recent_messages(
        GROUP_NAME,
        limit=10,
    )

    print(
        "\n========== 最近消息 =========="
    )

    for message in messages:

        print(
            message["created_at"],
            message["role"],
            message["sender_name"],
            ":",
            message["content"],
        )


if __name__ == "__main__":
    main()