"""
LLM integration service - handles communication with various LLM providers
"""

import httpx
from typing import List, Optional
from fastapi import HTTPException
from core.config import llm_config


# System prompts for different modes
SYSTEM_PROMPTS = {
    "free_talk": """You are a friendly and encouraging language teacher. Your role is to:
1. Help the user practice conversation on various topics
2. Gently correct grammar mistakes when they occur
3. When you notice a grammar rule the user might benefit from learning, mention it and ask if they'd like to explore it further
4. Keep the conversation natural and engaging
5. Adapt to the user's level

When you detect a grammar issue, format it like this:
[GRAMMAR_DETECTED: rule_name | brief_explanation]

Then continue the conversation naturally. The app will use this to offer creating a grammar lesson.""",

    "grammar": """You are a language teacher focused on teaching a specific grammar rule. Your role is to:
1. Explain the grammar rule clearly with examples
2. Create practice exercises
3. Provide feedback on the user's attempts
4. Use progressive difficulty
5. Celebrate progress and encourage the learner

Structure your lessons with:
- Clear explanation
- Multiple examples
- Practice exercises
- Corrections with explanations""",

    "document": """You are a language teacher helping the user learn vocabulary and sentence structures from a specific document. Your role is to:
1. Create conversations using words and phrases from the provided content
2. Quiz the user on vocabulary
3. Create fill-in-the-blank exercises
4. Use the words in new contexts
5. Build up from individual words to full sentences

The document content will be provided. Focus on helping the user internalize the vocabulary and structures naturally."""
}


async def call_llm_raw(prompt: str) -> str:
    """
    Call LLM with a simple prompt string (no chat history).
    Used for utility tasks like transcription correction.
    """
    messages = [{"role": "user", "content": prompt}]
    
    if llm_config.provider == "ollama":
        return await call_ollama(messages)
    elif llm_config.provider == "openai":
        return await call_openai(messages)
    elif llm_config.provider == "anthropic":
        return await call_anthropic(messages)
    elif llm_config.provider == "gemini":
        return await call_gemini(messages)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {llm_config.provider}")


async def call_llm(messages: List[dict], mode: str = "free_talk", document_content: str = None) -> str:
    """Call the configured LLM provider with chat context"""
    
    system_prompt = SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["free_talk"])
    if document_content:
        system_prompt += f"\n\n[DOCUMENT CONTENT]\n{document_content}"
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    if llm_config.provider == "ollama":
        return await call_ollama(full_messages)
    elif llm_config.provider == "openai":
        return await call_openai(full_messages)
    elif llm_config.provider == "anthropic":
        return await call_anthropic(full_messages)
    elif llm_config.provider == "gemini":
        return await call_gemini(full_messages)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown provider: {llm_config.provider}")


async def call_ollama(messages: List[dict]) -> str:
    """Call Ollama API"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{llm_config.base_url}/api/chat",
                json={
                    "model": llm_config.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_ctx": 8192  # Context window size (default is 2048)
                    }
                }
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Ollama API error: {response.text}"
                )
            return response.json()["message"]["content"]
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503, 
                detail="Cannot connect to Ollama. Is it running? Start it with 'ollama serve'"
            )


async def call_openai(messages: List[dict]) -> str:
    """Call OpenAI-compatible API"""
    api_key = llm_config.get_api_key()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        response = await client.post(
            f"{llm_config.base_url}/v1/chat/completions",
            headers=headers,
            json={
                "model": llm_config.model,
                "messages": messages
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="OpenAI API error")
        return response.json()["choices"][0]["message"]["content"]


async def call_anthropic(messages: List[dict]) -> str:
    """Call Anthropic API"""
    api_key = llm_config.get_api_key()
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Anthropic API key required. Set ANTHROPIC_API_KEY in .env file."
        )
    
    # Extract system message
    system = ""
    chat_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system += msg["content"] + "\n"
        else:
            chat_messages.append(msg)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": llm_config.model,
                "max_tokens": 4096,
                "system": system.strip(),
                "messages": chat_messages
            }
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Anthropic API error")
        return response.json()["content"][0]["text"]


async def call_gemini(messages: List[dict]) -> str:
    """Call Google Gemini API"""
    
    api_key = llm_config.get_api_key()
    
    if not api_key:
        raise HTTPException(
            status_code=400,
            detail="Gemini API key required. Set GEMINI_API_KEY in .env file or get one free at: https://aistudio.google.com/app/apikey"
        )
    
    # Convert messages to Gemini format
    # Gemini uses "user" and "model" roles, and system goes in systemInstruction
    system_instruction = ""
    gemini_contents = []
    
    for msg in messages:
        if msg["role"] == "system":
            system_instruction += msg["content"] + "\n"
        elif msg["role"] == "user":
            gemini_contents.append({
                "role": "user",
                "parts": [{"text": msg["content"]}]
            })
        elif msg["role"] == "assistant":
            gemini_contents.append({
                "role": "model",
                "parts": [{"text": msg["content"]}]
            })
    
    # Use model from config or default to gemini-2.0-flash
    model = llm_config.model if llm_config.model else "gemini-2.0-flash-lite"
    
    # Gemini API endpoint
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        request_body = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 4096,
            }
        }
        
        # Add system instruction if present
        if system_instruction.strip():
            request_body["systemInstruction"] = {
                "parts": [{"text": system_instruction.strip()}]
            }
        
        response = await client.post(
            api_url,
            params={"key": api_key},
            headers={"Content-Type": "application/json"},
            json=request_body
        )
        
        if response.status_code != 200:
            error_detail = response.text
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_detail = error_json["error"].get("message", error_detail)
            except:
                pass
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Gemini API error: {error_detail}"
            )
        
        result = response.json()
        
        # Extract text from response
        try:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected Gemini response format: {result}"
            )


def get_system_prompt(mode: str) -> str:
    """Get system prompt for a mode"""
    return SYSTEM_PROMPTS.get(mode, SYSTEM_PROMPTS["free_talk"])
