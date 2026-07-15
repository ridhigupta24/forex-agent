import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter directly
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "openrouter/meta-llama/llama-3.2-3b-instruct:free")

# Postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin123@localhost:5432/litellm"
)

# Agent settings
MAX_ORCHESTRATOR_DEPTH = 4

# Rate limiting
RATE_LIMIT_PER_MINUTE = 10