import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "notes.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


initialize_database()
def create_note(title, content):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO notes (title, content) VALUES (?, ?)",
        (title, content)
    )

    connection.commit()
    note_id = cursor.lastrowid
    connection.close()

    return note_id


def get_notes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, content, created_at, updated_at "
        "FROM notes ORDER BY created_at DESC"
    )

    notes = cursor.fetchall()
    connection.close()

    return notes


def search_notes(keyword):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, content, created_at, updated_at
        FROM notes
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY created_at DESC
        """,
        (f"%{keyword}%", f"%{keyword}%")
    )

    notes = cursor.fetchall()
    connection.close()

    return notes


def update_note(note_id, title, content):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE notes
        SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (title, content, note_id)
    )

    connection.commit()
    updated = cursor.rowcount
    connection.close()

    return updated


def delete_note(note_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE id = ?",
        (note_id,)
    )

    connection.commit()
    deleted = cursor.rowcount
    connection.close()

    return deleted