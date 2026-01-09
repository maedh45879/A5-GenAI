# LLM Council

![llmcouncil](header.jpg)

This repo runs a local "LLM Council" on one machine using Ollama. You ask a question once, the council models respond in parallel, they anonymously review each other, and a separate chairman model synthesizes the final answer.

In a bit more detail, here is what happens when you submit a query:

1. **Stage 1: First opinions**. The user query is given to all LLMs individually, and the responses are collected. The individual responses are shown in a "tab view", so that the user can inspect them all one by one.
2. **Stage 2: Review**. Each individual LLM is given the responses of the other LLMs. Under the hood, the LLM identities are anonymized so that the LLM can't play favorites when judging their outputs. The LLM is asked to rank them in accuracy and insight.
3. **Stage 3: Final response**. The designated Chairman of the LLM Council takes all of the model's responses and compiles them into a single final answer that is presented to the user.

## Vibe Code Alert

This project was 99% vibe coded as a fun Saturday hack because I wanted to explore and evaluate a number of LLMs side by side in the process of [reading books together with LLMs](https://x.com/karpathy/status/1990577951671509438). It's nice and useful to see multiple responses side by side, and also the cross-opinions of all LLMs on each other's outputs. I'm not going to support it in any way, it's provided here as is for other people's inspiration and I don't intend to improve it. Code is ephemeral now and libraries are over, ask your LLM to change it in whatever way you like.

## Setup

### 1. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for project management.

**Backend:**
```bash
uv sync
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 2. Install and Run Ollama

Install Ollama from https://ollama.com and start it locally.

Pull the default models:

```bash
ollama pull phi3
ollama pull mistral
ollama pull llama3
ollama pull llama3:instruct
```

### 3. Configure Models (Optional)

Edit `backend/config.py` or set environment variables in a `.env` file:

```python
OLLAMA_BASE_URL = "http://localhost:11434"
COUNCIL_MODELS = ["phi3", "mistral", "llama3"]
CHAIRMAN_MODEL = "llama3:instruct"
MAX_TOKENS = 800
TEMPERATURE_STAGE1 = 0.6
TEMPERATURE_REVIEW = 0.2
TEMPERATURE_CHAIRMAN = 0.3
TIMEOUT_SECONDS = 120
```

Note: `CHAIRMAN_MODEL` must be distinct from entries in `COUNCIL_MODELS`.

## Running the Application

**Option 1: Use the start script**
```bash
./start.sh
```

**Option 2: Run manually**

Terminal 1 (Backend):
```bash
uv run python -m backend.main
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

**Windows (PowerShell)**

Terminal 1 (Backend):
```powershell
uv run python -m backend.main
```

Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Demo Walkthrough

1. Open the UI and create a new conversation.
2. Ask a question (e.g., "Explain backpropagation in simple terms.").
3. Watch Stage 1 tabs for each model response.
4. Review Stage 2 rankings and justifications, plus the aggregate scores.
5. Read the Stage 3 chairman synthesis.

## Health Check

Check model availability:

```bash
curl http://localhost:8001/health
```

## Troubleshooting

- **Model missing:** Run `ollama pull <model-name>` for any missing model listed by `/health`.
- **Ollama not running:** Start the Ollama app/service and verify `http://localhost:11434`.
- **Timeouts:** Increase `TIMEOUT_SECONDS` in `backend/config.py`.

## Verified Steps

- Not run in this environment.

## Deliverables

- `report.md` - short technical report
- `ai_usage_statement.md` - generative AI usage statement

## Tech Stack

- **Backend:** FastAPI (Python 3.10+), async httpx, Ollama local API
- **Frontend:** React + Vite, react-markdown for rendering
- **Storage:** JSON files in `data/conversations/`
- **Package Management:** uv for Python, npm for JavaScript
