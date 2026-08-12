# Forex Trading Agent

Full-stack AI system for real-time forex trading analysis — agentic backend with a Server-Driven UI Flutter frontend, personalized per user by an AI gateway.

## Stack
**Backend:** FastAPI · LangGraph · PostgreSQL · Docker · OpenRouter  
**Frontend:** Flutter Web · Server-Driven UI (SDUI)

## Highlights
- **Agentic AI** — LangGraph deep agent autonomously chains up to 4 tool calls, fetching live ECB forex prices, sentiment, and strategy context for any currency pair
- **Token streaming** — responses stream word by word via `astream_events()`, with real-time tool call notifications
- **AI-personalized UI** — server sends a JSON screen definition to Flutter based on each user's risk tolerance and preferences; the frontend renders only what the AI selects
- **Session memory** — conversation context persists across disconnects via LangGraph AsyncPostgresSaver
- **Production patterns** — async non-blocking server, connection pooling, structured logging, graceful error handling, Dockerized

## Run it
```bash
cp backend/.env.example backend/.env
cd backend && docker-compose up --build
```

## Test it
```bash
cd backend
python test_client.py        
python test_checkpoint.py    
```

## Frontend
```bash
cd frontend
flutter run -d chrome --web-browser-flag "--disable-web-security"
```