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