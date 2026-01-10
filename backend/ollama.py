"""Ollama API client for making local LLM requests."""

from typing import List, Dict, Any, Optional
import httpx

from .config import OLLAMA_BASE_URL, TIMEOUT_SECONDS


class OllamaError(Exception):
    """Raised when an Ollama request fails."""


async def list_models(timeout: float = 10.0) -> List[str]:
    """
    List locally available Ollama models via /api/tags.

    Returns:
        List of model names (e.g., "llama3:instruct").
    """
    try:
        request_timeout = httpx.Timeout(timeout, connect=5.0)
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
    except Exception:
        return []


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: Optional[int],
    timeout: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Query a single model via Ollama /api/chat.

    Returns:
        Dict with keys: content (str), error (str|None)
    """
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    if max_tokens is not None:
        payload["options"]["num_predict"] = max_tokens

    timeout_seconds = TIMEOUT_SECONDS if timeout is None else timeout
    request_timeout = httpx.Timeout(timeout_seconds, connect=10.0)

    try:
        async with httpx.AsyncClient(timeout=request_timeout) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            message = data.get("message", {})
            return {"content": message.get("content", ""), "error": None}
    except httpx.HTTPStatusError as e:
        error_text = e.response.text if e.response is not None else str(e)
        return {"content": "", "error": f"HTTP error: {error_text}"}
    except httpx.ReadTimeout:
        return {"content": "", "error": "Timeout waiting for Ollama response."}
    except Exception as e:
        return {"content": "", "error": f"Request failed: {e}"}


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
    temperature: float,
    max_tokens: Optional[int],
    timeout: Optional[float] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Query multiple models in parallel.

    Returns:
        Dict mapping model name to response dict.
    """
    import asyncio

    tasks = [
        query_model(
            model,
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        for model in models
    ]
    responses = await asyncio.gather(*tasks)
    return {model: response for model, response in zip(models, responses)}
