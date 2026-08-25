import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DB_PATH = DATA_DIR / "business.db"


def get_connection():

    connection = sqlite3.connect(
        str(DB_PATH),

        # 等数据库锁最多30秒
        timeout=30,

        # wx4py / Agent可能存在多线程
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    # 开启外键
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    # 多读单写场景性能更合适
    connection.execute(
        "PRAGMA journal_mode = WAL"
    )

    # 遇到写锁时不要马上失败
    connection.execute(
        "PRAGMA busy_timeout = 30000"
    )

    return connection


def column_exists(
    connection,
    table_name: str,
    column_name: str,
) -> bool:

    rows = connection.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    return any(
        row["name"] == column_name
        for row in rows
    )


def init_database():

    connection = get_connection()

    try:

        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS groups (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL UNIQUE,

                enabled INTEGER NOT NULL DEFAULT 1,

                ai_enabled INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                external_user_id TEXT UNIQUE,

                display_name TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                group_id INTEGER NOT NULL,

                user_id INTEGER,

                sender_name TEXT,

                role TEXT NOT NULL,

                content TEXT NOT NULL,

                is_at_me INTEGER NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (group_id)
                    REFERENCES groups(id),

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            );


            CREATE TABLE IF NOT EXISTS reminders (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                group_id INTEGER NOT NULL,

                user_id INTEGER,

                content TEXT NOT NULL,

                scheduled_at TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'pending',

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (group_id)
                    REFERENCES groups(id),

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            );


            CREATE TABLE IF NOT EXISTS tool_logs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                group_id INTEGER,

                tool_name TEXT NOT NULL,

                arguments TEXT,

                result TEXT,

                success INTEGER NOT NULL DEFAULT 1,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (group_id)
                    REFERENCES groups(id)
            );
            CREATE TABLE IF NOT EXISTS user_memories (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                memory_key TEXT NOT NULL,

                memory_value TEXT NOT NULL,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                UNIQUE (
                    user_id,
                    memory_key
                ),

                FOREIGN KEY (user_id)
                    REFERENCES users(id)
            );
            """
        )

        # 兼容你之前已经创建过的 business.db
        if not column_exists(
            connection,
            "groups",
            "ai_enabled",
        ):
            connection.execute(
                """
                ALTER TABLE groups
                ADD COLUMN ai_enabled
                INTEGER NOT NULL DEFAULT 1
                """
            )

        connection.commit()

    finally:
        connection.close()