"""
Categories API routes
"""

import uuid
from fastapi import APIRouter
from typing import Optional

from models import CategoryCreate
from core.database import get_db, dict_from_row

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("")
async def list_categories(type: Optional[str] = None):
    """List all categories, optionally filtered by type"""
    conn = get_db()
    
    if type:
        rows = conn.execute(
            "SELECT * FROM categories WHERE type = ? ORDER BY created_at DESC",
            (type,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM categories ORDER BY type, created_at DESC"
        ).fetchall()
    
    conn.close()
    return [dict_from_row(r) for r in rows]


@router.post("")
async def create_category(category: CategoryCreate):
    """Create a new category"""
    conn = get_db()
    cat_id = str(uuid.uuid4())
    
    conn.execute(
        "INSERT INTO categories (id, name, type) VALUES (?, ?, ?)",
        (cat_id, category.name, category.type)
    )
    conn.commit()
    
    row = conn.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
    conn.close()
    
    return dict_from_row(row)


@router.delete("/{category_id}")
async def delete_category(category_id: str):
    """Delete a category"""
    conn = get_db()
    conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
