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
    source_type: str = "explicit_user",
    confidence: float = 1.0,
) -> str:
    """
    创建、更新或重新激活长期Memory。

    返回：
    created
    updated
    reactivated
    unchanged
    """

    user_id = get_or_create_user(
        external_user_id
    )

    connection = get_connection()

    try:

        # =================================
        # 1. 先读取当前数据库状态
        # =================================

        existing = connection.execute(
            """
            SELECT
                memory_value,
                status,
                source_type,
                confidence

            FROM user_memories

            WHERE user_id = ?
              AND memory_key = ?

            LIMIT 1
            """,
            (
                user_id,
                memory_key,
            ),
        ).fetchone()

        # =================================
        # 2. 第一次创建
        # =================================

        if not existing:

            connection.execute(
                """
                INSERT INTO user_memories (
                    user_id,
                    memory_key,
                    memory_value,
                    source_type,
                    confidence,
                    status
                )

                VALUES (?, ?, ?, ?, ?, 'active')
                """,
                (
                    user_id,
                    memory_key,
                    memory_value,
                    source_type,
                    confidence,
                ),
            )

            _save_user_memory_event(
                connection=connection,
                user_id=user_id,
                memory_key=memory_key,
                event_type="create",
                old_value=None,
                new_value=memory_value,
                source_type=source_type,
                confidence=confidence,
            )

            connection.commit()

            return "created"

        old_value = (
            existing["memory_value"]
        )

        old_status = (
            existing["status"]
        )

        # =================================
        # 3. Revoked → Active
        # =================================

        if old_status == "revoked":

            connection.execute(
                """
                UPDATE user_memories

                SET
                    memory_value = ?,
                    source_type = ?,
                    confidence = ?,
                    status = 'active',
                    updated_at = CURRENT_TIMESTAMP

                WHERE user_id = ?
                  AND memory_key = ?
                """,
                (
                    memory_value,
                    source_type,
                    confidence,
                    user_id,
                    memory_key,
                ),
            )

            _save_user_memory_event(
                connection=connection,
                user_id=user_id,
                memory_key=memory_key,
                event_type="reactivate",
                old_value=old_value,
                new_value=memory_value,
                source_type=source_type,
                confidence=confidence,
            )

            connection.commit()

            return "reactivated"

        # =================================
        # 4. 完全相同
        # =================================

        if old_value == memory_value:

            return "unchanged"

        # =================================
        # 5. Active Memory更新
        # =================================

        connection.execute(
            """
            UPDATE user_memories

            SET
                memory_value = ?,
                source_type = ?,
                confidence = ?,
                status = 'active',
                updated_at = CURRENT_TIMESTAMP

            WHERE user_id = ?
              AND memory_key = ?
            """,
            (
                memory_value,
                source_type,
                confidence,
                user_id,
                memory_key,
            ),
        )

        _save_user_memory_event(
            connection=connection,
            user_id=user_id,
            memory_key=memory_key,
            event_type="update",
            old_value=old_value,
            new_value=memory_value,
            source_type=source_type,
            confidence=confidence,
        )

        connection.commit()

        return "updated"

    except Exception:

        connection.rollback()
        raise

    finally:
        connection.close()    
def get_user_memories(
    external_user_id: str,
    limit:int = 100
):

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                user_memories.memory_key,
                user_memories.memory_value,
                user_memories.source_type,
                user_memories.confidence,
                user_memories.created_at,
                user_memories.updated_at

            FROM user_memories

            JOIN users
                ON users.id =
                   user_memories.user_id

            WHERE users.external_user_id = ?

              AND user_memories.status = 'active'

            ORDER BY
                user_memories.updated_at DESC
            LIMIT ?
            """,
            (
                external_user_id,
                limit,
            ),
        ).fetchall()

        return rows

    finally:
        connection.close()
        
def revoke_user_memory(
    external_user_id: str,
    memory_key: str,
) -> bool:

    connection = get_connection()

    try:

        # =================================
        # 1. 获取用户
        # =================================

        user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE external_user_id = ?
            """,
            (
                external_user_id,
            ),
        ).fetchone()

        if not user:
            return False

        user_id = user["id"]

        # =================================
        # 2. 获取当前Memory
        # =================================

        existing = connection.execute(
            """
            SELECT
                memory_value,
                source_type,
                confidence,
                status

            FROM user_memories

            WHERE user_id = ?
              AND memory_key = ?

            LIMIT 1
            """,
            (
                user_id,
                memory_key,
            ),
        ).fetchone()

        if not existing:

            return False

        if (
            existing["status"]
            != "active"
        ):
            return False

        old_value = (
            existing["memory_value"]
        )

        # =================================
        # 3. Soft Delete
        # =================================

        connection.execute(
            """
            UPDATE user_memories

            SET
                status = 'revoked',
                updated_at =
                    CURRENT_TIMESTAMP

            WHERE user_id = ?
              AND memory_key = ?
            """,
            (
                user_id,
                memory_key,
            ),
        )

        # =================================
        # 4. Audit
        # =================================

        _save_user_memory_event(
            connection=connection,
            user_id=user_id,
            memory_key=memory_key,
            event_type="revoke",
            old_value=old_value,
            new_value=None,
            source_type=(
                existing[
                    "source_type"
                ]
            ),
            confidence=(
                existing[
                    "confidence"
                ]
            ),
        )

        connection.commit()

        return True

    except Exception:

        connection.rollback()
        raise

    finally:
        connection.close()
        
def get_active_user_memory(
    external_user_id: str,
    memory_key: str,
):
    """
    获取用户某个Key当前有效的长期记忆。
    """

    connection = get_connection()

    try:

        row = connection.execute(
            """
            SELECT
                user_memories.memory_key,
                user_memories.memory_value,
                user_memories.source_type,
                user_memories.confidence,
                user_memories.created_at,
                user_memories.updated_at

            FROM user_memories

            JOIN users
                ON users.id =
                   user_memories.user_id

            WHERE users.external_user_id = ?

              AND user_memories.memory_key = ?

              AND user_memories.status = 'active'

            LIMIT 1
            """,
            (
                external_user_id,
                memory_key,
            ),
        ).fetchone()

        return row

    finally:
        connection.close()
        
def _save_user_memory_event(
    connection,
    user_id: int,
    memory_key: str,
    event_type: str,
    old_value: str | None,
    new_value: str | None,
    source_type: str,
    confidence: float | None,
) -> None:
    """
    写入长期Memory审计事件。

    这是Repository内部函数，
    不应该直接暴露给LLM Tool。
    """

    connection.execute(
        """
        INSERT INTO user_memory_events (
            user_id,
            memory_key,
            event_type,
            old_value,
            new_value,
            source_type,
            confidence
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            memory_key,
            event_type,
            old_value,
            new_value,
            source_type,
            confidence,
        ),
    )
    
def get_user_memory_events(
    external_user_id: str,
    limit: int = 100,
):

    connection = get_connection()

    try:

        rows = connection.execute(
            """
            SELECT
                user_memory_events.memory_key,
                user_memory_events.event_type,
                user_memory_events.old_value,
                user_memory_events.new_value,
                user_memory_events.source_type,
                user_memory_events.confidence,
                user_memory_events.created_at

            FROM user_memory_events

            JOIN users
                ON users.id =
                   user_memory_events.user_id

            WHERE
                users.external_user_id = ?

            ORDER BY
                user_memory_events.id DESC

            LIMIT ?
            """,
            (
                external_user_id,
                limit,
            ),
        ).fetchall()

        return rows

    finally:
        connection.close()