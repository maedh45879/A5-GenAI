# CLAUDE.md - Technical Notes for LLM Council

This file contains technical details, architectural decisions, and important implementation notes for future development sessions.

## Project Overview

LLM Council is a 3-stage deliberation system where multiple LLMs collaboratively answer user questions. The key innovation is anonymized peer review in Stage 2, preventing models from playing favorites.

## Architecture

### Backend Structure (`backend/`)

**`config.py`**
- Contains `COUNCIL_MODELS` (list of Ollama model identifiers)
- Contains `CHAIRMAN_MODEL` (model that synthesizes final answer)
- Uses `OLLAMA_BASE_URL` from `.env` (defaults to `http://localhost:11434`)
- Backend runs on **port 8001** (NOT 8000 - user had another app on 8000)

**`ollama.py`**
- `query_model()`: Single async model query to `/api/chat`
- `query_models_parallel()`: Parallel queries using `asyncio.gather()`
- Returns dict with `content` and `error` when failures occur
- `list_models()` hits `/api/tags` for availability

**`council.py`** - The Core Logic
- `stage1_collect_responses()`: Parallel queries to all council models
- `stage2_collect_rankings()`:
  - Anonymizes responses as "Model A, Model B, Model C, etc."
  - Creates `label_to_model` mapping for de-anonymization
  - Prompts models for strict JSON ranking + justification
  - Returns tuple: (rankings_list, label_to_model_dict) with parse status
- `stage3_synthesize_final()`: Chairman synthesizes from all responses + rankings
- `parse_reviewer_output()`: Parses strict JSON with fallback label extraction
- `calculate_aggregate_rankings()`: Computes point-based aggregate scores

**`storage.py`**
- JSON-based conversation storage in `data/conversations/`
- Each conversation: `{id, created_at, messages[]}`
- Assistant messages contain: `{role, stage1, stage2, stage3, metadata}`

**`main.py`**
- FastAPI app with CORS enabled for localhost:5173 and localhost:3000
- POST `/api/conversations/{id}/message` returns metadata in addition to stages
- Metadata includes: label_to_model mapping and aggregate_rankings
- GET `/health` returns Ollama availability and missing models

### Frontend Structure (`frontend/src/`)

**`App.jsx`**
- Main orchestration: manages conversations list and current conversation
- Handles message sending and metadata storage
- Important: metadata is stored in the UI state for display but not persisted to backend JSON

**`components/ChatInterface.jsx`**
- Multiline textarea (3 rows, resizable)
- Enter to send, Shift+Enter for new line
- User messages wrapped in markdown-content class for padding

**`components/Stage1.jsx`**
- Tab view of individual model responses
- ReactMarkdown rendering with markdown-content wrapper

**`components/Stage2.jsx`**
- Tab view showing each reviewer ranking + justification
- De-anonymization happens CLIENT-SIDE for display
- Shows aggregate rankings with point totals

**`components/Stage3.jsx`**
- Final synthesized answer from chairman
- Green-tinted background (#f0fff0) to highlight conclusion

**Styling (`*.css`)**
- Light mode theme (not dark mode)
- Primary color: #4a90e2 (blue)
- Global markdown styling in `index.css` with `.markdown-content` class
- 12px padding on all markdown content to prevent cluttered appearance

## Key Design Decisions

### Stage 2 Prompt Format
Stage 2 requires strict JSON output with `ranking` and `justification` fields to improve parsing reliability.

### De-anonymization Strategy
- Models receive: "Model A", "Model B", etc.
- Backend creates mapping: `{"Model A": "llama3", ...}`
- Frontend displays model names for readability
- This prevents bias while maintaining transparency

### Error Handling Philosophy
- Continue with successful responses if some models fail (graceful degradation)
- Never fail the entire request due to single model failure
- Return error fields in stage outputs when a model fails

### UI/UX Transparency
- All raw outputs are inspectable via tabs
- Parsed rankings shown below raw text for validation
- Users can verify system's interpretation of model outputs
- This builds trust and allows debugging of edge cases

## Important Implementation Details

### Relative Imports
All backend modules use relative imports (e.g., `from .config import ...`) not absolute imports. This is critical for Python's module system to work correctly when running as `python -m backend.main`.

### Port Configuration
- Backend: 8001 (changed from 8000 to avoid conflict)
- Frontend: 5173 (Vite default)
- Update both `backend/main.py` and `frontend/src/api.js` if changing

### Markdown Rendering
All ReactMarkdown components must be wrapped in `<div className="markdown-content">` for proper spacing. This class is defined globally in `index.css`.

### Model Configuration
Models are configured in `backend/config.py` or `.env`. `CHAIRMAN_MODEL` must be distinct from `COUNCIL_MODELS`.

## Common Gotchas

1. **Module Import Errors**: Always run backend as `python -m backend.main` from project root, not from backend directory
2. **CORS Issues**: Frontend must match allowed origins in `main.py` CORS middleware
3. **Ranking Parse Failures**: If models don't follow JSON format, fallback label extraction is used
4. **Missing Metadata**: Metadata is ephemeral (not persisted), only available in API responses

## Future Enhancement Ideas

- Configurable council/chairman via UI instead of config file
- Streaming responses instead of batch loading
- Export conversations to markdown/PDF
- Model performance analytics over time
- Custom ranking criteria (not just accuracy/insight)
- Support for reasoning models (o1, etc.) with special handling

## Testing Notes

Use `/health` to verify Ollama connectivity and check for missing models before running the council.

## Data Flow Summary

```
User Query
    ↓
Stage 1: Parallel queries → [individual responses]
    ↓
Stage 2: Anonymize → Parallel ranking queries → [evaluations + parsed rankings]
    ↓
Aggregate Rankings Calculation → [sorted by avg position]
    ↓
Stage 3: Chairman synthesis with full context
    ↓
Return: {stage1, stage2, stage3, metadata}
    ↓
Frontend: Display with tabs + validation UI
```

The entire flow is async/parallel where possible to minimize latency.
