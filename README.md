# Forex Trading Agent

A LangGraph-based agentic AI system for real-time forex trading analysis.

## Stack
- **FastAPI** — async WebSocket server
- **LangGraph** — deep agent, tool-calling loop (max depth 4)
- **OpenRouter** — LLM provider
- **PostgreSQL** — trade ledger + conversation checkpoints
- **Docker** — containerized deployment

## Features
- Live forex price fetching for any valid currency pair (frankfurter.dev)
- 7-day historical price seeding and trend analysis
- Mocked sentiment, economic calendar, and RAG tools
- Conversation persistence across sessions (LangGraph PostgresSaver)
- Structured Pydantic response schema
- Async non-blocking agent via thread pool
- Structured logging and LLM error handling

## Setup

**Docker (recommended):**
```bash
cp .env.example .env   # add your OpenRouter API key
docker-compose up --build
```

**Local:**
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## Testing
```bash
python test_client.py        # full test suite
python test_checkpoint.py    # session persistence
```

