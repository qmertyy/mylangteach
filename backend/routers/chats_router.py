"""
Chat API routes
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from models import ChatCreate, ChatMessage
from services.chat_service import (
    create_chat,
    get_chat,
    get_all_chats,
    delete_chat,
    send_message
)

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.get("")
async def list_chats(mode: Optional[str] = None, category_id: Optional[str] = None):
    """List all chats, optionally filtered by mode or category"""
    return get_all_chats(mode, category_id)


@router.post("")
async def create_new_chat(chat: ChatCreate):
    """Create a new chat"""
    return await create_chat(
        title=chat.title,
        mode=chat.mode,
        category_id=chat.category_id,
        document_id=chat.document_id
    )


@router.get("/{chat_id}")
async def get_chat_detail(chat_id: str):
    """Get a specific chat with all messages"""
    chat, messages = get_chat(chat_id)
    return {"chat": chat, "messages": messages}


@router.delete("/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    """Delete a chat and all its messages"""
    delete_chat(chat_id)
    return {"status": "deleted"}


@router.post("/{chat_id}/messages")
async def send_chat_message(chat_id: str, message: ChatMessage):
    """Send a message and get LLM response"""
    return await send_message(
        chat_id=chat_id,
        content=message.content,
        detect_grammar=message.detect_grammar
    )
