"""
Configuration API routes
"""

from fastapi import APIRouter
from core.config import (
    llm_config, 
    whisper_config, 
    update_llm_config, 
    update_whisper_config,
    LLMConfig,
    WhisperConfig,
    GEMINI_API_KEY,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY
)

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
async def get_config():
    """Get current LLM and Whisper configuration"""
    return {
        "llm": {
            "provider": llm_config.provider,
            "model": llm_config.model,
            "base_url": llm_config.base_url,
            "has_api_key": bool(llm_config.get_api_key()),
            "api_key_source": "env" if (
                (llm_config.provider == "gemini" and GEMINI_API_KEY) or
                (llm_config.provider == "openai" and OPENAI_API_KEY) or
                (llm_config.provider == "anthropic" and ANTHROPIC_API_KEY)
            ) else ("config" if llm_config.api_key else None)
        },
        "whisper": {
            "provider": whisper_config.provider,
            "model": whisper_config.model,
            "language": whisper_config.language
        },
        "env_keys_configured": {
            "gemini": bool(GEMINI_API_KEY),
            "openai": bool(OPENAI_API_KEY),
            "anthropic": bool(ANTHROPIC_API_KEY)
        }
    }


@router.post("")
async def update_config(config: LLMConfig):
    """Update LLM configuration"""
    update_llm_config(config)
    return {
        "status": "ok", 
        "config": {
            "provider": config.provider,
            "model": config.model,
            "base_url": config.base_url,
            "has_api_key": bool(config.api_key)
        }
    }


@router.post("/whisper")
async def update_whisper(config: WhisperConfig):
    """Update Whisper configuration"""
    update_whisper_config(config)
    return {"status": "ok", "config": config.model_dump()}
