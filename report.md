# Technical Report: Local LLM Council (Ollama)

## Overview
This refactor converts the original multi-provider LLM Council into a fully local pipeline using Ollama. All model calls run on a single machine, preserving the 3-stage workflow (individual answers, anonymous peer review with ranking, chairman synthesis).

## Architecture
- **Frontend:** React + Vite UI that renders Stage 1 tabs, Stage 2 reviewer rankings/justifications with an aggregate scoreboard, and the Stage 3 final synthesis.
- **Backend:** FastAPI server with three core responsibilities:
  - **Ollama client wrapper** (`backend/ollama.py`) for `/api/chat` requests and `/api/tags` health checks.
  - **Council orchestration** (`backend/council.py`) to run Stage 1/2/3, anonymize answers, parse JSON rankings robustly, and aggregate scores.
  - **API layer** (`backend/main.py`) for conversation endpoints and streaming SSE updates.
- **Storage:** JSON files per conversation in `data/conversations/`.

## Key Changes From Original
- Replaced OpenRouter usage with local Ollama calls only.
- Added configuration defaults for local models and generation settings.
- Implemented strict JSON outputs for Stage 2 with fallback parsing.
- Added model availability health checks.
- Ensured chairman model is distinct from council models.

## Local Deployment
Ollama runs at `http://localhost:11434`. The backend uses `/api/chat` for all LLM calls and `/api/tags` to report missing models. The UI and backend run locally with no cloud dependencies.

## Limitations
- Performance depends on local hardware and model size.
- Reviewer JSON parsing can still degrade if models ignore format requirements.
- No automatic model downloading; missing models must be pulled manually.

## Future Work
- Add configurable reviewer sets and weighting strategies.
- Improve resilience for partial failures and add retries.
- Optional streaming responses per model.
