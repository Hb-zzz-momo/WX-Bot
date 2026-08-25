from database.db import get_connection
import json

def get_or_create_group(
    group_name: str
) -> int:

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT id
            FROM groups
            WHERE name = ?
            """,
            (group_name,),
        )

        row = cursor.fetchone()

        if row:
            return row["id"]

        cursor = connection.execute(
            """
            INSERT INTO groups (name)
            VALUES (?)
            """,
            (group_name,),
            #外部group_name用来替换内部？，同时（group_name,)中的“，”代表这是一个元组，而不是一个字符串
            #这保障了？的安全性，防止SQL注入攻击
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
        
def save_message(
    group_name: str,
    content: str,
    role: str,
    sender_name: str | None = None,
    user_id: int | None = None,
    is_at_me: bool = False,
) -> int:

    group_id = get_or_create_group(
        group_name
    )

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO messages (
                group_id,
                user_id,
                sender_name,
                role,
                content,
                is_at_me
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                group_id,
                user_id,
                sender_name,
                role,
                content,
                int(is_at_me),
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
        
def get_recent_messages(
    group_name: str,
    limit: int = 20,
):

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT
                messages.id,
                messages.sender_name,
                messages.role,
                messages.content,
                messages.created_at

            FROM messages

            JOIN groups
                ON groups.id =
                   messages.group_id

            WHERE groups.name = ?

            ORDER BY messages.id DESC

            LIMIT ?
            """,
            (
                group_name,
                limit,
            ),
        )

        rows = cursor.fetchall()

        return list(
            reversed(rows)
        )

    finally:
        connection.close()
        
def create_reminder(
    group_name: str,
    content: str,
    scheduled_at: str,
    user_id: int | None = None,
) -> int:

    group_id = get_or_create_group(
        group_name
    )

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            INSERT INTO reminders (
                group_id,
                user_id,
                content,
                scheduled_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                group_id,
                user_id,
                content,
                scheduled_at,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
        
def save_tool_log(
    tool_name: str,
    arguments: dict,
    result: str,
    success: bool,
    group_name: str | None = None,
):

    group_id = None

    if group_name:

        group_id = get_or_create_group(
            group_name
        )

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO tool_logs (
                group_id,
                tool_name,
                arguments,
                result,
                success
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                group_id,
                tool_name,

                json.dumps(
                    arguments,
                    ensure_ascii=False,
                ),

                result,

                int(success),
            ),
        )

        connection.commit()

    finally:
        connection.close()
        
def upsert_group(
    group_name: str,
    enabled: bool = True,
    ai_enabled: bool = True,
):

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO groups (
                name,
                enabled,
                ai_enabled
            )

            VALUES (?, ?, ?)

            ON CONFLICT(name)
            DO UPDATE SET

                enabled = excluded.enabled,

                ai_enabled = excluded.ai_enabled
            """,
            (
                group_name,
                int(enabled),
                int(ai_enabled),
            ),
        )

        connection.commit()

    finally:
        connection.close()
        
def upsert_group(
    group_name: str,
    enabled: bool = True,
    ai_enabled: bool = True,
):

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO groups (
                name,
                enabled,
                ai_enabled
            )

            VALUES (?, ?, ?)

            ON CONFLICT(name)
            DO UPDATE SET

                enabled = excluded.enabled,

                ai_enabled = excluded.ai_enabled
            """,
            (
                group_name,
                int(enabled),
                int(ai_enabled),
            ),
        )

        connection.commit()

    finally:
        connection.close()
        
def get_enabled_groups():

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                id,
                name,
                enabled,
                ai_enabled

            FROM groups

            WHERE enabled = 1

            ORDER BY id
            """
        ).fetchall()

        return rows

    finally:
        connection.close()

def get_group_config(
    group_name: str
):

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                id,
                name,
                enabled,
                ai_enabled

            FROM groups

            WHERE name = ?
            """,
            (group_name,),
        ).fetchone()

        return row

    finally:
        connection.close()
        
def get_recent_ambient_messages(
    group_name: str,
    limit: int = 20,
):
    """
    获取最近普通群消息。

    这里只取：
    role=user
    且没有 @机器人

    用于给 Agent 提供群聊环境上下文。
    """

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                messages.id,
                messages.sender_name,
                messages.content,
                messages.created_at

            FROM messages

            JOIN groups
                ON groups.id = messages.group_id

            WHERE groups.name = ?
              AND messages.role = 'user'
              AND messages.is_at_me = 0

            ORDER BY messages.id DESC

            LIMIT ?
            """,
            (
                group_name,
                limit,
            ),
        ).fetchall()

        return list(reversed(rows))

    finally:
        connection.close()
        
def get_or_create_user(
    external_user_id: str,
    display_name: str | None = None,
) -> int:

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT id
            FROM users
            WHERE external_user_id = ?
            """,
            (external_user_id,),
        ).fetchone()

        if row:
            return row["id"]

        cursor = connection.execute(
            """
            INSERT INTO users (
                external_user_id,
                display_name
            )
            VALUES (?, ?)
            """,
            (
                external_user_id,
                display_name,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()
        
def upsert_user_memory(
    external_user_id: str,
    memory_key: str,
    memory_value: str,
):

    user_id = get_or_create_user(
        external_user_id
    )

    connection = get_connection()

    try:

        connection.execute(
            """
            INSERT INTO user_memories (
                user_id,
                memory_key,
                memory_value
            )

            VALUES (?, ?, ?)

            ON CONFLICT(
                user_id,
                memory_key
            )

            DO UPDATE SET

                memory_value =
                    excluded.memory_value,

                updated_at =
                    CURRENT_TIMESTAMP
            """,
            (
                user_id,
                memory_key,
                memory_value,
            ),
        )

        connection.commit()

    finally:
        connection.close()
        
def get_user_memories(
    external_user_id: str,
):

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                user_memories.memory_key,
                user_memories.memory_value

            FROM user_memories

            JOIN users
                ON users.id =
                   user_memories.user_id

            WHERE users.external_user_id = ?

            ORDER BY
                user_memories.updated_at DESC
            """,
            (
                external_user_id,
            ),
        ).fetchall()

        return rows

    finally:
        connection.close()