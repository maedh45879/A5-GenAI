"""Deprecated OpenRouter shim (kept for backwards compatibility)."""

from typing import List, Dict, Any, Optional
from .ollama import query_model as ollama_query_model, query_models_parallel as ollama_query_models_parallel
from .config import MAX_TOKENS, TEMPERATURE_STAGE1, TIMEOUT_SECONDS


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = TIMEOUT_SECONDS
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via Ollama (OpenRouter shim).
    """
    response = await ollama_query_model(
        model,
        messages,
        temperature=TEMPERATURE_STAGE1,
        max_tokens=MAX_TOKENS,
        timeout=timeout,
    )
    if response.get("error"):
        return None
    return {
        "content": response.get("content", ""),
        "reasoning_details": None,
    }


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel via Ollama.
    """
    responses = await ollama_query_models_parallel(
        models,
        messages,
        temperature=TEMPERATURE_STAGE1,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT_SECONDS,
    )
    return {
        model: ({"content": response.get("content", ""), "reasoning_details": None}
                if not response.get("error") else None)
        for model, response in responses.items()
    }
