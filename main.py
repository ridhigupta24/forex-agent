from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage
from agent.graph import forex_agent
from agent.state import AgentState
from agent.utils import is_greeting, is_out_of_scope
from db.database import init_db
import json
import re
import asyncio
from functools import partial

app = FastAPI(title="Forex Trading Agent")

@app.on_event("startup")
async def startup():
    """Initialize DB on startup"""
    init_db()
    print("Forex Agent started")

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "forex-trading-agent"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected")

    # Only store non-fast-path messages in history
    conversation_history = []

    try:
        while True:
            data = await websocket.receive_text()

            try:
                payload = json.loads(data)
                user_message = payload.get("message", "")
            except json.JSONDecodeError:
                user_message = data

            if not user_message.strip():
                await websocket.send_text(json.dumps({"error": "Empty message"}))
                continue

            print(f"Received: {user_message}")

            # Check fast-path BEFORE building state
            # so we never add OOS/greeting messages to history
            message_lower = user_message.lower().strip()
            import re

            # Clean single-source fast-path check
            if is_greeting(user_message):
                await websocket.send_text(json.dumps({"status": "thinking"}))
                await websocket.send_text(json.dumps({
                    "status": "done",
                    "response": "Hello! I'm your forex trading assistant. Ask me about currency pairs like EUR/USD, GBP/USD, USD/JPY and more!",
                    "tool_calls_made": 0,
                    "is_fast_path": True
                }))
                continue

            if is_out_of_scope(user_message):
                await websocket.send_text(json.dumps({"status": "thinking"}))
                await websocket.send_text(json.dumps({
                    "status": "done",
                    "response": "I'm specialized in forex trading only. I can help you with currency pairs like EUR/USD, GBP/USD, USD/JPY, USD/CHF, and AUD/USD.",
                    "tool_calls_made": 0,
                    "is_fast_path": True
                }))
                continue

            # Only real forex messages reach here and get added to history
            current_message = HumanMessage(content=user_message)

            initial_state: AgentState = {
                "messages": conversation_history + [current_message],
                "forex_data": None,
                "api_data": None,
                "rag_context": None,
                "tool_calls_count": 0,
                "max_depth": 4,
                "user_profile": {},
                "final_response": None,
                "is_fast_path": False,
            }

            await websocket.send_text(json.dumps({"status": "thinking"}))

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                partial(forex_agent.invoke, initial_state)
                )

            final_response = result.get("final_response", "Sorry, I could not generate a response.")
            final_response = re.sub(r'<think.*?>.*?</think.*?>', '', final_response, flags=re.DOTALL).strip()
            final_response = re.sub(r'<tool_calls.*?>.*?</tool_calls.*?>', '', final_response, flags=re.DOTALL).strip()
            final_response = re.sub(r'<tool_call.*?>.*?</tool_call.*?>', '', final_response, flags=re.DOTALL).strip()

            # Update history only with real forex conversation
            conversation_history = list(result["messages"])

            await websocket.send_text(json.dumps({
                "status": "done",
                "response": final_response,
                "tool_calls_made": result.get("tool_calls_count", 0),
                "is_fast_path": False
            }))

            print(f"Response sent ({result.get('tool_calls_count', 0)} tool calls made)")

    except WebSocketDisconnect:
        print("Client disconnected")