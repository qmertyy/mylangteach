"""
Grammar rules API routes
"""

import uuid
from fastapi import APIRouter
from typing import Optional

from core.database import get_db, dict_from_row

router = APIRouter(prefix="/api/grammar-rules", tags=["grammar"])


@router.get("")
async def list_grammar_rules():
    """List all learned grammar rules"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM grammar_rules ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]


@router.post("")
async def create_grammar_rule(
    rule_name: str,
    description: Optional[str] = None,
    from_chat_id: Optional[str] = None
):
    """Create a new grammar rule and associated chat for learning it"""
    conn = get_db()
    
    # Create grammar category if not exists
    grammar_cat = conn.execute(
        "SELECT id FROM categories WHERE type = 'grammar' AND name = ?",
        (rule_name,)
    ).fetchone()
    
    if not grammar_cat:
        cat_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO categories (id, name, type) VALUES (?, ?, 'grammar')",
            (cat_id, rule_name)
        )
    else:
        cat_id = grammar_cat["id"]
    
    # Create chat for this grammar rule
    chat_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO chats (id, category_id, title, mode) VALUES (?, ?, ?, 'grammar')",
        (chat_id, cat_id, f"Learning: {rule_name}")
    )
    
    # Create grammar rule record
    rule_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO grammar_rules (id, name, description, chat_id) VALUES (?, ?, ?, ?)",
        (rule_id, rule_name, description, chat_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"rule_id": rule_id, "chat_id": chat_id, "category_id": cat_id}


@router.delete("/{rule_id}")
async def delete_grammar_rule(rule_id: str):
    """Delete a grammar rule"""
    conn = get_db()
    conn.execute("DELETE FROM grammar_rules WHERE id = ?", (rule_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
