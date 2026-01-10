"""Configuration for the LLM Council."""

import os
from dotenv import load_dotenv

load_dotenv()

# Ollama connection
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Council members - list of Ollama model identifiers
COUNCIL_MODELS = os.getenv(
    "COUNCIL_MODELS",
    "phi3:latest,mistral:latest,llama3:latest",
).split(",")
COUNCIL_MODELS = [model.strip() for model in COUNCIL_MODELS if model.strip()]

# Chairman model - synthesizes final response (must be distinct)
CHAIRMAN_MODEL = os.getenv("CHAIRMAN_MODEL", "llama3:instruct")

# Generation controls
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "600"))
TEMPERATURE_STAGE1 = float(os.getenv("TEMPERATURE_STAGE1", "0.6"))
TEMPERATURE_REVIEW = float(os.getenv("TEMPERATURE_REVIEW", "0.2"))
TEMPERATURE_CHAIRMAN = float(os.getenv("TEMPERATURE_CHAIRMAN", "0.3"))
TIMEOUT_SECONDS = float(os.getenv("TIMEOUT_SECONDS", "360"))
STREAM = os.getenv("STREAM", "False").lower() == "true"

# Data directory for conversation storage
DATA_DIR = "data/conversations"
