"""
Speech-to-text service using faster-whisper or OpenAI Whisper API.
"""

import os
import tempfile
from typing import Optional, Tuple
from fastapi import HTTPException, UploadFile
from core.config import whisper_config, AUDIO_UPLOAD_DIR

_whisper_model = None


def get_whisper_model():
    """Lazy load faster-whisper model."""
    global _whisper_model
    
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            _whisper_model = WhisperModel(
                whisper_config.model,
                device="cpu",
                compute_type="int8"
            )
            print(f"Loaded Whisper model: {whisper_config.model}")
        except ImportError:
            raise HTTPException(
                status_code=500,
                detail="faster-whisper not installed. Run: pip install faster-whisper"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to load Whisper model: {str(e)}"
            )
    
    return _whisper_model


async def correct_transcription(text: str, language: str = "German", chat_history: list = None) -> str:
    """Use LLM to correct transcription errors using chat context."""
    from services.llm_service import call_llm_raw
    
    if not text or not text.strip():
        return text
    
    context_section = ""
    if chat_history and len(chat_history) > 0:
        recent_messages = chat_history[-10:]
        context_lines = []
        for msg in recent_messages:
            role = "User" if msg.get("role") == "user" else "Assistant"
            context_lines.append(f"{role}: {msg.get('content', '')}")
        
        context_section = f"""
Recent conversation context:
---
{chr(10).join(context_lines)}
---

Use this context to better understand what words the user likely said.
"""

    correction_prompt = f"""You are a {language} language transcription corrector. 
The following text was transcribed from speech and may contain errors due to accent or pronunciation issues.
{context_section}
Your task:
1. Fix any misheard words based on context (e.g., "Robys" should be "Hobbys" if discussing hobbies)
2. Fix spelling errors
3. Keep the original meaning and intent
4. Do NOT translate - keep it in {language}
5. Do NOT add explanations - only output the corrected text
6. If the text seems contextually correct, return it unchanged

Transcribed text: {text}

Corrected text:"""

    try:
        corrected = await call_llm_raw(correction_prompt)
        corrected = corrected.strip().strip('"\'')
        if corrected and len(corrected) > 0:
            return corrected
        return text
    except Exception as e:
        print(f"Transcription correction failed: {e}")
        return text


async def transcribe_audio(
    audio_file: UploadFile,
    language: Optional[str] = None,
    correct: bool = True,
    chat_history: list = None
) -> Tuple[str, str, Optional[str], Optional[float]]:
    """Transcribe audio file to text with optional LLM correction."""
    
    if whisper_config.provider == "openai":
        original_text, lang, conf = await transcribe_with_openai(audio_file, language)
    else:
        original_text, lang, conf = await transcribe_with_faster_whisper(audio_file, language)
    
    corrected_text = original_text
    
    if correct and original_text:
        lang_names = {
            "de": "German", "en": "English", "es": "Spanish", "fr": "French",
            "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "pl": "Polish",
            "ru": "Russian", "ja": "Japanese", "zh": "Chinese", "ko": "Korean",
        }
        lang_name = lang_names.get(lang or language or whisper_config.language, "German")
        corrected_text = await correct_transcription(original_text, lang_name, chat_history)
    
    return corrected_text, original_text, lang, conf


async def transcribe_with_faster_whisper(
    audio_file: UploadFile,
    language: Optional[str] = None
) -> Tuple[str, Optional[str], Optional[float]]:
    """Transcribe using local faster-whisper."""
    temp_path = None
    try:
        content = await audio_file.read()
        ext = os.path.splitext(audio_file.filename or "audio.wav")[1] or ".wav"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        model = get_whisper_model()
        transcribe_language = language or whisper_config.language
        
        segments, info = model.transcribe(
            temp_path,
            language=transcribe_language if transcribe_language else None,
            task="transcribe",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        text_parts = [segment.text.strip() for segment in segments]
        full_text = " ".join(text_parts)
        
        return full_text, info.language, info.language_probability
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


# async def transcribe_with_openai(
#     audio_file: UploadFile,
#     language: Optional[str] = None
# ) -> Tuple[str, Optional[str], Optional[float]]:
#     """Transcribe using OpenAI Whisper API."""
#     import httpx
#     from core.config import llm_config
    
#     if not llm_config.api_key:
#         raise HTTPException(status_code=400, detail="OpenAI API key required for Whisper API")
    
#     content = await audio_file.read()
    
#     async with httpx.AsyncClient(timeout=60.0) as client:
#         files = {
#             "file": (audio_file.filename or "audio.wav", content, audio_file.content_type or "audio/wav"),
#             "model": (None, "whisper-1"),
#         }
#         if language:
#             files["language"] = (None, language)
        
#         response = await client.post(
#             "https://api.openai.com/v1/audio/transcriptions",
#             headers={"Authorization": f"Bearer {llm_config.api_key}"},
#             files=files
#         )
        
#         if response.status_code != 200:
#             raise HTTPException(status_code=response.status_code, detail=f"OpenAI Whisper API error: {response.text}")
        
#         result = response.json()
#         return result["text"], language, None


def get_supported_audio_formats() -> list:
    return [
        "audio/wav", "audio/wave", "audio/x-wav", "audio/mp3", "audio/mpeg",
        "audio/mp4", "audio/m4a", "audio/x-m4a", "audio/ogg", "audio/webm", "audio/flac",
    ]


def validate_audio_file(file: UploadFile) -> bool:
    content_type = file.content_type or ""
    if any(fmt in content_type for fmt in ["audio/", "video/"]):
        return True
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        return ext in [".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac", ".mp4"]
    return False
