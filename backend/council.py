"""3-stage LLM Council orchestration."""

from typing import List, Dict, Any, Tuple, Optional
import json
import re

from .ollama import query_models_parallel, query_model
from .config import (
    COUNCIL_MODELS,
    CHAIRMAN_MODEL,
    MAX_TOKENS,
    TEMPERATURE_STAGE1,
    TEMPERATURE_REVIEW,
    TEMPERATURE_CHAIRMAN,
    TIMEOUT_SECONDS,
)


def _build_display_ids(models: List[str]) -> Dict[str, str]:
    return {model: f"Model {chr(65 + i)}" for i, model in enumerate(models)}


def _ensure_chairman_distinct() -> Optional[str]:
    if CHAIRMAN_MODEL in COUNCIL_MODELS:
        return "CHAIRMAN_MODEL must be distinct from COUNCIL_MODELS."
    return None


async def stage1_collect_responses(user_query: str) -> List[Dict[str, Any]]:
    """
    Stage 1: Collect individual responses from all council models.

    Returns:
        List of dicts with model, display_id, response, error keys.
    """
    messages = [{"role": "user", "content": user_query}]
    display_ids = _build_display_ids(COUNCIL_MODELS)

    responses = await query_models_parallel(
        COUNCIL_MODELS,
        messages,
        temperature=TEMPERATURE_STAGE1,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT_SECONDS,
    )

    stage1_results = []
    for model in COUNCIL_MODELS:
        response = responses.get(model, {})
        error = response.get("error")
        content = response.get("content", "")
        stage1_results.append({
            "model": model,
            "display_id": display_ids[model],
            "response": content if not error else f"Error: {error}",
            "error": error,
        })

    return stage1_results


async def stage2_collect_rankings(
    user_query: str,
    stage1_results: List[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], Dict[str, str]]:
    """
    Stage 2: Each model ranks the anonymized responses.

    Returns:
        Tuple of (rankings list, label_to_model mapping)
    """
    successful = [r for r in stage1_results if not r.get("error")]
    labels = [result["display_id"] for result in successful]
    label_to_model = {result["display_id"]: result["model"] for result in successful}

    responses_text = "\n\n".join([
        f"{result['display_id']}:\n{result['response']}"
        for result in successful
    ])

    example_label = labels[0] if labels else "Model A"

    ranking_prompt = f"""You are evaluating different responses to the following question.

Question: {user_query}

Here are the responses from different models (anonymized):

{responses_text}

Rank the responses by accuracy and insight. Return ONLY valid JSON with this schema:
{{
  "reviewer_model": "<your model name>",
  "ranking": ["{example_label}", "..."],
  "justification": {{
    "{example_label}": "<short justification>",
    "...": "..."
  }}
}}

Rules:
- Use ONLY the provided labels for ranking.
- Provide a complete ordering best to worst.
- Keep justifications short (1-2 sentences each).
- Output JSON only. No extra text.
"""

    messages = [{"role": "user", "content": ranking_prompt}]

    responses = await query_models_parallel(
        COUNCIL_MODELS,
        messages,
        temperature=TEMPERATURE_REVIEW,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT_SECONDS,
    )

    stage2_results = []
    for model in COUNCIL_MODELS:
        response = responses.get(model, {})
        full_text = response.get("content", "")
        error = response.get("error")
        parsed = parse_reviewer_output(full_text, labels)
        stage2_results.append({
            "reviewer_model": model,
            "raw_text": full_text,
            "ranking": parsed["ranking"],
            "justification": parsed["justification"],
            "parse_status": parsed["parse_status"],
            "error": error,
        })

    return stage2_results, label_to_model


async def stage3_synthesize_final(
    user_query: str,
    stage1_results: List[Dict[str, Any]],
    stage2_results: List[Dict[str, Any]],
    aggregate_rankings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Stage 3: Chairman synthesizes final response.
    """
    stage1_text = "\n\n".join([
        f"{result['display_id']} ({result['model']}):\n{result['response']}"
        for result in stage1_results
        if not result.get("error")
    ])

    stage2_text = "\n\n".join([
        f"Reviewer: {result['reviewer_model']}\n"
        f"Ranking: {result['ranking']}\n"
        f"Justification: {result['justification']}"
        for result in stage2_results
        if not result.get("error")
    ])

    aggregate_text = "\n".join([
        f"{item['model']}: {item['score']} points"
        for item in aggregate_rankings
    ])

    chairman_prompt = f"""You are the Chairman of an LLM Council. Multiple AI models have provided responses, and then ranked each other's responses.

Original Question: {user_query}

STAGE 1 - Individual Responses (anonymized labels with actual model names):
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

AGGREGATE SCORES (higher is better):
{aggregate_text}

Synthesize the best possible final answer to the original question. Focus on accuracy, insight, and clarity."""

    messages = [{"role": "user", "content": chairman_prompt}]

    response = await query_model(
        CHAIRMAN_MODEL,
        messages,
        temperature=TEMPERATURE_CHAIRMAN,
        max_tokens=MAX_TOKENS,
        timeout=TIMEOUT_SECONDS,
    )

    if response.get("error"):
        return {
            "model": CHAIRMAN_MODEL,
            "response": f"Error: {response['error']}"
        }

    return {
        "model": CHAIRMAN_MODEL,
        "response": response.get("content", "")
    }


def _extract_labels_from_text(text: str, labels: List[str]) -> List[str]:
    if not labels:
        return []
    pattern = "(" + "|".join(re.escape(label) for label in labels) + ")"
    found = re.findall(pattern, text)
    seen = set()
    ordered = []
    for label in found:
        if label not in seen:
            ordered.append(label)
            seen.add(label)
    return ordered


def _try_parse_json(text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return None
    return None


def parse_reviewer_output(text: str, labels: List[str]) -> Dict[str, Any]:
    """
    Parse reviewer JSON output with a fallback to text extraction.
    """
    parsed_json = _try_parse_json(text)
    ranking: List[str] = []
    justification: Dict[str, str] = {}
    parse_status = "unparsed"

    if isinstance(parsed_json, dict):
        raw_ranking = parsed_json.get("ranking", [])
        if isinstance(raw_ranking, list):
            ranking = [item for item in raw_ranking if item in labels]
        raw_justification = parsed_json.get("justification", {})
        if isinstance(raw_justification, dict):
            justification = {
                label: str(raw_justification.get(label, "")).strip()
                for label in labels
                if raw_justification.get(label) is not None
            }
        if ranking:
            parse_status = "parsed_json"

    if not ranking:
        ranking = _extract_labels_from_text(text, labels)
        if ranking:
            parse_status = "fallback_text"

    if ranking:
        for label in labels:
            if label not in ranking:
                ranking.append(label)

    return {
        "ranking": ranking,
        "justification": justification,
        "parse_status": parse_status,
    }


def calculate_aggregate_rankings(
    stage2_results: List[Dict[str, Any]],
    label_to_model: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Calculate aggregate rankings across all models using a point system.
    """
    from collections import defaultdict

    scores = defaultdict(int)
    vote_counts = defaultdict(int)
    labels = list(label_to_model.keys())
    total = len(labels)

    for result in stage2_results:
        ranking = result.get("ranking", [])
        if not ranking:
            continue
        for idx, label in enumerate(ranking):
            if label not in label_to_model:
                continue
            points = total - idx
            model_name = label_to_model[label]
            scores[model_name] += points
            vote_counts[model_name] += 1

    aggregate = []
    for model_name, score in scores.items():
        aggregate.append({
            "model": model_name,
            "score": score,
            "votes": vote_counts.get(model_name, 0),
        })

    aggregate.sort(key=lambda x: x["score"], reverse=True)
    return aggregate


async def generate_conversation_title(user_query: str) -> str:
    """
    Generate a short title for a conversation based on the first user message.
    """
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following question.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Question: {user_query}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]

    response = await query_model(
        CHAIRMAN_MODEL,
        messages,
        temperature=0.2,
        max_tokens=30,
        timeout=30.0,
    )

    if response.get("error"):
        return "New Conversation"

    title = response.get("content", "New Conversation").strip()
    title = title.strip('"\'')
    if len(title) > 50:
        title = title[:47] + "..."
    return title


async def run_full_council(user_query: str) -> Tuple[List, List, Dict, Dict]:
    """
    Run the complete 3-stage council process.
    """
    config_error = _ensure_chairman_distinct()
    if config_error:
        return [], [], {
            "model": "error",
            "response": f"Configuration error: {config_error}"
        }, {}

    stage1_results = await stage1_collect_responses(user_query)
    successful = [r for r in stage1_results if not r.get("error")]

    if not successful:
        return stage1_results, [], {
            "model": "error",
            "response": "All models failed to respond. Please check Ollama and model availability."
        }, {}

    stage2_results, label_to_model = await stage2_collect_rankings(user_query, stage1_results)
    aggregate_rankings = calculate_aggregate_rankings(stage2_results, label_to_model)

    stage3_result = await stage3_synthesize_final(
        user_query,
        stage1_results,
        stage2_results,
        aggregate_rankings,
    )

    metadata = {
        "label_to_model": label_to_model,
        "aggregate_rankings": aggregate_rankings
    }

    return stage1_results, stage2_results, stage3_result, metadata
