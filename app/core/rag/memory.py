import sqlite3
import os
import json
from typing import List, Dict

class SqliteMemoryManager:
    """
    Manages short-term memory (Chat History) using SQLite.
    Guarantees persistence and low memory overhead.
    """
    def __init__(self, db_path: str = "./chroma_db/chat_history.db", max_messages: int = 10):
        self.db_path = db_path
        self.max_messages = max_messages
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_session ON chat_history(session_id)")
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str):
        """Save a new message to the session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """Retrieve recent chat history for a given session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Get the latest max_messages, ordered chronologically
            cursor.execute("""
                SELECT role, content FROM (
                    SELECT role, content, timestamp FROM chat_history
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ) ORDER BY timestamp ASC
            """, (session_id, self.max_messages))
            
            rows = cursor.fetchall()
            return [{"role": row[0], "content": row[1]} for row in rows]

    def clear_history(self, session_id: str):
        """Clear memory for a session (Useful for 'New Chat' feature)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
            conn.commit()

    def get_all_sessions(self) -> List[str]:
        """Retrieve all unique session IDs that have chat history."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT session_id FROM chat_history ORDER BY id DESC")
            rows = cursor.fetchall()
            return [row[0] for row in rows]

