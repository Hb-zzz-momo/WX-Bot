import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


# =========================
# 1. 确定数据库目录
# =========================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# =========================
# 2. 数据库文件路径
# =========================

DB_PATH = DATA_DIR / "agent_memory.db"


# =========================
# 3. 建立 SQLite 连接
# =========================

connection = sqlite3.connect(
    str(DB_PATH),
    check_same_thread=False,
)


# =========================
# 4. 创建 LangGraph Checkpointer
# =========================

checkpointer = SqliteSaver(connection)


# =========================
# 5. 清理指定 Thread 的历史
# =========================

def purge_thread(thread_id: str) -> int:
    """
    清空某个 thread 的所有对话历史。

    当模型返回内容风控错误（如
    Content Exists Risk）时使用：
    历史里可能残留敏感内容，
    清空后可重新提问。
    """

    conn = sqlite3.connect(
        str(DB_PATH)
    )

    try:
        with conn:

            checkpoints = conn.execute(
                """
                DELETE FROM checkpoints
                WHERE thread_id = ?
                """,
                (thread_id,),
            ).rowcount

            writes = conn.execute(
                """
                DELETE FROM writes
                WHERE thread_id = ?
                """,
                (thread_id,),
            ).rowcount

        return checkpoints + writes

    finally:
        conn.close()