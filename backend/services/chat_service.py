"""
Chat service - handles chat and message operations
"""

import json
import uuid
import re
from typing import List, Optional, Tuple

from core.database import get_db, dict_from_row
from services.llm_service import call_llm


async def create_chat(
    title: str, 
    mode: str, 
    category_id: Optional[str] = None,
    document_id: Optional[str] = None
) -> dict:
    """Create a new chat"""
    conn = get_db()
    chat_id = str(uuid.uuid4())
    metadata = json.dumps({"document_id": document_id}) if document_id else None
    
    conn.execute(
        "INSERT INTO chats (id, category_id, title, mode, metadata) VALUES (?, ?, ?, ?, ?)",
        (chat_id, category_id, title, mode, metadata)
    )
    conn.commit()
    
    row = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    conn.close()
    
    return dict_from_row(row)


def get_chat(chat_id: str) -> Tuple[dict, List[dict]]:
    """Get chat with all messages"""
    conn = get_db()
    
    chat = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    if not chat:
        conn.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Chat not found")
    
    messages = conn.execute(
        "SELECT * FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
        (chat_id,)
    ).fetchall()
    
    conn.close()
    
    return dict_from_row(chat), [dict_from_row(m) for m in messages]


def get_all_chats(mode: Optional[str] = None, category_id: Optional[str] = None) -> List[dict]:
    """Get all chats, optionally filtered"""
    conn = get_db()
    
    query = "SELECT * FROM chats WHERE 1=1"
    params = []
    
    if mode:
        query += " AND mode = ?"
        params.append(mode)
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
    
    query += " ORDER BY updated_at DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    
    return [dict_from_row(r) for r in rows]


def delete_chat(chat_id: str) -> None:
    """Delete a chat and all its messages"""
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE chat_id = ?", (chat_id,))
    conn.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()


async def send_message(
    chat_id: str, 
    content: str, 
    detect_grammar: bool = True
) -> dict:
    """
    Send a message and get LLM response.
    
    Returns:
        Dict with user_message, assistant_message, and optional grammar_detected
    """
    conn = get_db()
    
    # Get chat info
    chat = conn.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
    if not chat:
        conn.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Chat not found")
    
    chat_dict = dict_from_row(chat)
    mode = chat_dict["mode"]
    
    # Get document content if in document mode
    document_content = None
    if mode == "document" and chat_dict.get("metadata"):
        metadata = json.loads(chat_dict["metadata"])
        if metadata.get("document_id"):
            doc = conn.execute(
                "SELECT content FROM documents WHERE id = ?",
                (metadata["document_id"],)
            ).fetchone()
            if doc:
                document_content = doc["content"]
    
    # Save user message
    user_msg_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO messages (id, chat_id, role, content) VALUES (?, ?, ?, ?)",
        (user_msg_id, chat_id, "user", content)
    )
    conn.commit()
    
    # Get conversation history
    history = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
        (chat_id,)
    ).fetchall()
    
    messages_for_llm = [{"role": h["role"], "content": h["content"]} for h in history]
    
    # Get LLM response
    response = await call_llm(messages_for_llm, mode, document_content)
    
    # Check for grammar detection
    grammar_detected = None
    if detect_grammar and "[GRAMMAR_DETECTED:" in response:
        match = re.search(r'\[GRAMMAR_DETECTED:\s*([^|]+)\s*\|\s*([^\]]+)\]', response)
        if match:
            grammar_detected = {
                "rule_name": match.group(1).strip(),
                "explanation": match.group(2).strip()
            }
            # Clean the response
            response = re.sub(r'\[GRAMMAR_DETECTED:[^\]]+\]', '', response).strip()
    
    # Save assistant message
    assistant_msg_id = str(uuid.uuid4())
    msg_metadata = json.dumps({"grammar_detected": grammar_detected}) if grammar_detected else None
    conn.execute(
        "INSERT INTO messages (id, chat_id, role, content, metadata) VALUES (?, ?, ?, ?, ?)",
        (assistant_msg_id, chat_id, "assistant", response, msg_metadata)
    )
    
    # Update chat timestamp
    conn.execute(
        "UPDATE chats SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (chat_id,)
    )
    
    conn.commit()
    
    # Get the saved messages
    user_msg = conn.execute("SELECT * FROM messages WHERE id = ?", (user_msg_id,)).fetchone()
    assistant_msg = conn.execute("SELECT * FROM messages WHERE id = ?", (assistant_msg_id,)).fetchone()
    
    conn.close()
    
    return {
        "user_message": dict_from_row(user_msg),
        "assistant_message": {
            **dict_from_row(assistant_msg),
            "grammar_detected": grammar_detected
        }
    }
