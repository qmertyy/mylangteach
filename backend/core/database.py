"""
Database initialization and helpers
"""

import sqlite3
from typing import Optional, List, Any
from core.config import DB_PATH


def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Categories table (for organizing chats)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('topic', 'grammar', 'document')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    """)
    
    # Chats table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            category_id TEXT,
            title TEXT NOT NULL,
            mode TEXT NOT NULL CHECK(mode IN ('free_talk', 'grammar', 'document')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)
    
    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            chat_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
        )
    """)
    
    # Documents table (for document mode)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            extracted_words TEXT,
            extracted_sentences TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Grammar rules learned
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grammar_rules (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            examples TEXT,
            chat_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
    """)
    
    conn.commit()
    conn.close()


def get_db():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dict_from_row(row) -> Optional[dict]:
    """Convert sqlite row to dict"""
    return dict(row) if row else None


def execute_query(query: str, params: tuple = ()) -> List[dict]:
    """Execute a SELECT query and return results as list of dicts"""
    conn = get_db()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


def execute_write(query: str, params: tuple = ()) -> None:
    """Execute an INSERT/UPDATE/DELETE query"""
    conn = get_db()
    conn.execute(query, params)
    conn.commit()
    conn.close()


def execute_write_returning(query: str, params: tuple, select_query: str, select_params: tuple) -> Optional[dict]:
    """Execute a write query and return the affected row"""
    conn = get_db()
    conn.execute(query, params)
    conn.commit()
    row = conn.execute(select_query, select_params).fetchone()
    conn.close()
    return dict_from_row(row)
