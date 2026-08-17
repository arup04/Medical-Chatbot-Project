# src/chat_history.py
import sqlite3
import os
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from src.logger import logging

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "chat_history.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Creates and returns a connection to the SQLite database, ensuring tables exist.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id ON chat_messages(session_id);
        """)
    return conn


def add_message(session_id: str, role: str, content: str, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Adds a message (role='human' or 'ai') to the SQLite history for a given session_id.
    """
    if not session_id or not content or not content.strip():
        return

    try:
        conn = get_db_connection(db_path)
        with conn:
            conn.execute(
                "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id.strip(), role.strip().lower(), content.strip())
            )
    except Exception as e:
        logging.error(f"Failed to write message to SQLite for session {session_id}: {e}")


def get_chat_history(session_id: str, limit: int = 6, db_path: str = DEFAULT_DB_PATH) -> List[BaseMessage]:
    """
    Fetches the most recent `limit` messages for a session and returns them
    as LangChain BaseMessage objects (HumanMessage / AIMessage).
    """
    if not session_id:
        return []

    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        # Fetch the last `limit` messages in chronological order
        cursor.execute("""
            SELECT role, content FROM (
                SELECT id, role, content FROM chat_messages 
                WHERE session_id = ? 
                ORDER BY id DESC 
                LIMIT ?
            ) ORDER BY id ASC
        """, (session_id.strip(), limit))
        
        rows = cursor.fetchall()
        messages: List[BaseMessage] = []
        for row in rows:
            role = row["role"]
            content = row["content"]
            if role == "human":
                messages.append(HumanMessage(content=content))
            elif role == "ai":
                messages.append(AIMessage(content=content))
                
        return messages
    except Exception as e:
        logging.error(f"Failed to fetch chat history from SQLite for session {session_id}: {e}")
        return []


def clear_session_history(session_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """
    Deletes all message history for a specific session_id.
    """
    if not session_id:
        return False

    try:
        conn = get_db_connection(db_path)
        with conn:
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id.strip(),))
        return True
    except Exception as e:
        logging.error(f"Failed to clear session history for {session_id}: {e}")
        return False


def get_all_sessions(db_path: str = DEFAULT_DB_PATH) -> List[str]:
    """
    Returns a list of all distinct session IDs stored in the SQLite database.
    """
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT session_id FROM chat_messages ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        return [row["session_id"] for row in rows]
    except Exception as e:
        logging.error(f"Failed to list session IDs from SQLite: {e}")
        return []
