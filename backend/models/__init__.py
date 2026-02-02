"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import Optional, Literal, List
from datetime import datetime


# ============== Request Models ==============

class MessageCreate(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"] = "user"


class ChatCreate(BaseModel):
    title: str
    mode: Literal["free_talk", "grammar", "document"]
    category_id: Optional[str] = None
    document_id: Optional[str] = None


class CategoryCreate(BaseModel):
    name: str
    type: Literal["topic", "grammar", "document"]


class ChatMessage(BaseModel):
    chat_id: str
    content: str
    detect_grammar: bool = True


class AudioTranscribeRequest(BaseModel):
    language: Optional[str] = None  # None for auto-detect


# ============== Response Models ==============

class Category(BaseModel):
    id: str
    name: str
    type: str
    created_at: str
    metadata: Optional[str] = None


class Chat(BaseModel):
    id: str
    category_id: Optional[str]
    title: str
    mode: str
    created_at: str
    updated_at: str
    metadata: Optional[str] = None


class Message(BaseModel):
    id: str
    chat_id: str
    role: str
    content: str
    created_at: str
    metadata: Optional[str] = None


class Document(BaseModel):
    id: str
    filename: str
    content: Optional[str] = None
    extracted_words: Optional[List[str]] = None
    extracted_sentences: Optional[List[str]] = None
    created_at: str


class GrammarRule(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    examples: Optional[str] = None
    chat_id: Optional[str] = None
    created_at: str


class GrammarDetected(BaseModel):
    rule_name: str
    explanation: str


class ChatResponse(BaseModel):
    user_message: Message
    assistant_message: dict  # includes optional grammar_detected


class TranscriptionResponse(BaseModel):
    text: str  # Corrected text (or original if correction disabled)
    original_text: str  # Original transcription before LLM correction
    language: Optional[str] = None
    confidence: Optional[float] = None
    was_corrected: bool = False  # True if LLM made changes
