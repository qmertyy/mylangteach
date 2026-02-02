"""
Core configuration and settings.
"""

from pydantic import BaseModel
from typing import Optional, Literal
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_PATH", "language_teacher.db")
AUDIO_UPLOAD_DIR = os.getenv("AUDIO_UPLOAD_DIR", "./audio_uploads")
MAX_AUDIO_SIZE_MB = 25

os.makedirs(AUDIO_UPLOAD_DIR, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "ollama")
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "llama3.2")


class LLMConfig(BaseModel):
    provider: Literal["ollama", "openai", "anthropic", "gemini"] = DEFAULT_LLM_PROVIDER
    model: str = DEFAULT_LLM_MODEL
    base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    api_key: Optional[str] = None
    
    def get_api_key(self) -> Optional[str]:
        if self.api_key:
            return self.api_key
        if self.provider == "gemini":
            return GEMINI_API_KEY
        elif self.provider == "openai":
            return OPENAI_API_KEY
        elif self.provider == "anthropic":
            return ANTHROPIC_API_KEY
        return None


class WhisperConfig(BaseModel):
    provider: Literal["local", "openai", "faster-whisper"] = "faster-whisper"
    model: str = os.getenv("WHISPER_MODEL", "base")
    language: str = os.getenv("WHISPER_LANGUAGE", "de")
    task: str = "transcribe"


llm_config = LLMConfig()
whisper_config = WhisperConfig()


def update_llm_config(config: LLMConfig):
    global llm_config
    llm_config = config


def update_whisper_config(config: WhisperConfig):
    global whisper_config
    whisper_config = config
