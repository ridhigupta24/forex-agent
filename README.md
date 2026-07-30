# Forex Trading Agent

Real-time agentic AI system for forex trading analysis — built with LangGraph and FastAPI.

## What it does
A deep agent that fetches live forex prices, analyzes trends, retrieves sentiment, and streams responses word by word over WebSockets. Supports any valid currency pair.

## Stack
FastAPI · LangGraph · PostgreSQL · Docker · psycopg_pool · AsyncPostgresSaver

## Highlights
- **Autonomous tool chaining** — agent independently decides which tools to call and in what order, up to 4 calls per query
- **Real-time streaming** — responses appear token by token, users see tool calls happening live as the agent thinks
- **Memory across sessions** — disconnect and reconnect, agent remembers the full conversation via Postgres-backed checkpointing
- **Handles any forex pair** — not limited to a fixed list, fetches live data from ECB reference rates for any valid BASE/QUOTE pair
- **Production-ready patterns** — async non-blocking server, connection pooling, structured logging, graceful error handling, Dockerized

## Run it
```bash
cp .env.example .env  
docker-compose up --build
```

## Test it
```bash
python test_client.py       
python test_checkpoint.py  
```