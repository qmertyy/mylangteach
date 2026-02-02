"""
Speech/Audio API routes - handles audio transcription
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional

from models import TranscriptionResponse
from services.speech_service import (
    transcribe_audio,
    get_supported_audio_formats,
    validate_audio_file
)
from services.chat_service import send_message

router = APIRouter(prefix="/api/audio", tags=["audio"])


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio_endpoint(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None),
    correct: bool = Form(False)
):
    """
    Transcribe audio file to text.
    
    Accepts: WAV, MP3, M4A, OGG, WebM, FLAC
    
    Args:
        audio: Audio file
        language: Optional language code (e.g., 'en', 'de', 'es'). Auto-detects if not provided.
        correct: Whether to use LLM to correct transcription errors (default: False) -> this might create hallucinated results if True :)
    
    Returns:
        Transcribed text with detected language and confidence
    """
    # Validate audio file
    if not validate_audio_file(audio):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio file. Supported formats: {', '.join(get_supported_audio_formats())}"
        )
    
    # Transcribe (with optional LLM correction)
    corrected_text, original_text, detected_lang, confidence = await transcribe_audio(audio, language, correct=correct)
    
    return TranscriptionResponse(
        text=corrected_text,
        original_text=original_text,
        language=detected_lang,
        confidence=confidence,
        was_corrected=(corrected_text != original_text)
    )


@router.post("/transcribe-and-send")
async def transcribe_and_send_message(
    audio: UploadFile = File(...),
    chat_id: str = Form(...),
    language: Optional[str] = Form(None),
    detect_grammar: bool = Form(True),
    correct: bool = Form(True)
):
    """
    Transcribe audio and send as chat message in one request.
    
    This is a convenience endpoint that combines transcription and message sending.
    Uses chat history for context-aware transcription correction.
    
    Args:
        audio: Audio file with speech
        chat_id: Chat to send message to
        language: Optional language code for transcription
        detect_grammar: Whether to detect grammar issues
        correct: Whether to use LLM to correct transcription errors (default: True)
    
    Returns:
        Transcription result plus chat response
    """
    from core.database import get_db
    
    # Validate audio file
    if not validate_audio_file(audio):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid audio file. Supported formats: {', '.join(get_supported_audio_formats())}"
        )
    
    # Get chat history for context-aware correction
    chat_history = []
    if correct:
        conn = get_db()
        messages = conn.execute(
            "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY created_at ASC",
            (chat_id,)
        ).fetchall()
        conn.close()
        chat_history = [{"role": m["role"], "content": m["content"]} for m in messages]
    
    # Transcribe (with optional LLM correction using chat context)
    corrected_text, original_text, detected_lang, confidence = await transcribe_audio(
        audio, language, correct=correct, chat_history=chat_history
    )
    
    if not corrected_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not transcribe any speech from the audio"
        )
    
    # Send corrected text as message
    chat_response = await send_message(
        chat_id=chat_id,
        content=corrected_text,
        detect_grammar=detect_grammar
    )
    
    return {
        "transcription": {
            "text": corrected_text,
            "original_text": original_text,
            "language": detected_lang,
            "confidence": confidence,
            "was_corrected": (corrected_text != original_text)
        },
        "chat_response": chat_response
    }


@router.get("/formats")
async def get_formats():
    """Get list of supported audio formats"""
    return {
        "formats": get_supported_audio_formats(),
        "max_size_mb": 25,
        "correction_enabled": True,
        "correction_info": "LLM-based correction fixes accent and pronunciation errors"
    }
