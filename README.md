# Forex Trading Agent

A LangGraph-based agentic AI system for forex trading analysis.
## Architecture
- **WebSocket server** — FastAPI
- **Agent framework** — LangGraph (deep agent, max depth 4)
- **LLM provider** — OpenRouter
- **Database** — PostgreSQL (trade ledger)
- **Forex data** — frankfurter.dev (free, no API key needed)

## Features
- Real-time forex price fetching and storage
- 7-day historical price seeding and trend analysis
- Market sentiment analysis (mocked)
- Trading strategy context (mocked RAG)
- Rate limiting + fast-path for greetings/OOS queries
- Personalization layer (risk tolerance, response style)
- Prompt store for easy prompt management

## Setup
1. Copy `.env.example` to `.env` and fill in your keys
2. Start PostgreSQL
3. Run `pip install -r requirements.txt`
4. Run `uvicorn main:app --reload --port 8000`

## Testing
```bash
python test_client.py
```