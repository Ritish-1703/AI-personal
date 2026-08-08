import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "notes.db"


def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            done        INTEGER NOT NULL DEFAULT 0,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def add_task(title: str) -> int:
    conn = _get_connection()
    cursor = conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def get_tasks(include_done: bool = True) -> list[tuple]:
    conn = _get_connection()
    if include_done:
        rows = conn.execute(
            "SELECT id, title, done, created_at FROM tasks ORDER BY done, created_at DESC"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, title, done, created_at FROM tasks WHERE done = 0 ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return rows


def complete_task(task_id: int) -> int:
    conn = _get_connection()
    cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
    conn.commit()
    updated = cursor.rowcount
    conn.close()
    return updated


def delete_task(task_id: int) -> int:
    conn = _get_connection()
    cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted
