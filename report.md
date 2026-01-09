# Technical Report: Local LLM Council (Ollama)

## Overview
This project runs a fully local 3-stage LLM Council using Ollama. Stage 1 collects parallel model responses, Stage 2 performs anonymized peer review with strict JSON output, and Stage 3 synthesizes a final answer using a distinct chairman model.

## Architecture
- **Frontend:** React + Vite UI with stage tabs, peer-review rankings, and aggregate scoring.
- **Backend:** FastAPI server with:
  - **Ollama client** (`backend/ollama.py`) using `/api/chat` and `/api/tags` with enforced HTTP timeouts.
  - **Council orchestration** (`backend/council.py`) for Stage 1/2/3, anonymization, strict JSON parsing, and aggregation.
  - **API layer** (`backend/main.py`) for conversation endpoints and SSE streaming.
- **Storage:** JSON files per conversation in `data/conversations/`.

## Stage 2 JSON Contract
Reviewers are instructed (system + user prompts) to return STRICT JSON only:
```
{
  "ranking": ["Model A", "Model B", "Model C"],
  "justifications": {
    "Model A": "short reason",
    "Model B": "short reason",
    "Model C": "short reason"
  }
}
```
Parsing logic attempts `json.loads`, then extracts the first `{...}` block and retries. If parsing still fails, `parse_status` is set to `unparsed` and processing continues.

## Model Configuration
Default model set:
- **Council models:** `["phi3", "mistral", "llama3"]`
- **Chairman:** `"llama3:instruct"`
These defaults can be overridden via `.env` variables.

## Health Check
`GET /health` calls `/api/tags` to verify Ollama availability and returns:
- `ok` boolean (all required models present)
- required vs available model lists
- a per-model presence map

## Limitations
- Performance depends on local hardware and model sizes.
- If reviewers ignore JSON requirements, rankings may be unparsed.
- No automatic model downloads; missing models must be pulled manually.
