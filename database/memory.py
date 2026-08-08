import sqlite3
from pathlib import Path

# Absolute path — works regardless of working directory
DB_PATH = Path(__file__).parent.parent / "data" / "notes.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_memory(key: str, value: str) -> str:
    conn = _get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO memory (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()
    return f"Memory saved: {key} = {value}"


def get_memory(key: str):
    conn = _get_connection()
    row = conn.execute(
        "SELECT value FROM memory WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row[0] if row else None


def get_all_memories() -> list[tuple]:
    """Return all (key, value) rows."""
    conn = _get_connection()
    rows = conn.execute("SELECT key, value FROM memory ORDER BY key").fetchall()
    conn.close()
    return rows


def delete_memory(key: str) -> int:
    conn = _get_connection()
    cursor = conn.execute("DELETE FROM memory WHERE key = ?", (key,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted