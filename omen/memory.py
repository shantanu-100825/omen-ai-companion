import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("omen_memory.db")

class MemoryStore:
    """SQLite memory for notes explicitly saved by the user."""
    def __init__(self, db_path=DB_PATH):
        self.db_path = str(db_path)
        with self._connect() as con:
            con.execute("""CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL
            )""")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def save_note(self, content):
        content = content.strip()
        if not content:
            raise ValueError("A note cannot be empty.")
        with self._connect() as con:
            con.execute("INSERT INTO notes(content, created_at) VALUES (?, ?)",
                        (content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        return "Saved that to persistent memory."

    def search_notes(self, query):
        with self._connect() as con:
            rows = con.execute(
                "SELECT content, created_at FROM notes WHERE content LIKE ? ORDER BY id DESC LIMIT 10",
                (f"%{query}%",)
            ).fetchall()
        return [{"content": r[0], "created_at": r[1]} for r in rows]

    def list_notes(self):
        with self._connect() as con:
            rows = con.execute(
                "SELECT content, created_at FROM notes ORDER BY id DESC LIMIT 50"
            ).fetchall()
        return [{"content": r[0], "created_at": r[1]} for r in rows]
