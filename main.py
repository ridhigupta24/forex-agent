from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_core.messages import HumanMessage
from agent.graph import init_agent, get_agent, close_agent
from agent.state import AgentState
from agent.utils import is_greeting, is_out_of_scope
from db.database import init_db, close_pool
from logger import setup_logger
import json
import re
from api.ui_gateway import router as ui_router
from fastapi.middleware.cors import CORSMiddleware

logger = setup_logger("main")
app = FastAPI(title="Forex Trading Agent")
app.include_router(ui_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows Flutter web to call the API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()
    await init_agent()
    logger.info("Forex Agent started")


@app.on_event("shutdown")
async def shutdown():
    close_pool()
    await close_agent()
    logger.info("Forex Agent shutdown complete")


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "forex-trading-agent"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, user_id: str = "default-user"):
    await websocket.accept()

    thread_id = user_id
    logger.info(f"New session started — thread_id: {thread_id}")
    logger.info("Client connected")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()

            try:
                payload = json.loads(data)
                user_message = payload.get("message", "")
            except json.JSONDecodeError:
                user_message = data

            if not user_message.strip():
                await websocket.send_text(json.dumps({"error": "Empty message"}))
                continue

            logger.info(f"Received: {user_message}")

            # --- Fast-path checks ---
            if is_greeting(user_message):
                await websocket.send_text(json.dumps({"type": "thinking"}))
                await websocket.send_text(json.dumps({
                    "type": "done",
                    "response": "Hello! I'm your forex trading assistant. Ask me about currency pairs like EUR/USD, GBP/USD, USD/JPY and more!",
                    "tool_calls_made": 0,
                    "is_fast_path": True
                }))
                continue

            if is_out_of_scope(user_message):
                await websocket.send_text(json.dumps({"type": "thinking"}))
                await websocket.send_text(json.dumps({
                    "type": "done",
                    "response": "I'm specialized in forex trading only. I can help you with currency pairs like EUR/USD, GBP/USD, USD/JPY, USD/CHF, and AUD/USD.",
                    "tool_calls_made": 0,
                    "is_fast_path": True
                }))
                continue

            # --- Real forex message ---
            current_message = HumanMessage(content=user_message)
            initial_state: AgentState = {
                "messages": [current_message],
                "forex_data": None,
                "api_data": None,
                "rag_context": None,
                "tool_calls_count": 0,
                "max_depth": 4,
                "user_profile": {},
                "user_id": user_id,
                "classifier_output": None,
                "final_response": None,
                "is_fast_path": False,
            }

            config = {"configurable": {"thread_id": thread_id}}
            agent = get_agent()

            # Tell client agent is thinking
            await websocket.send_text(json.dumps({"type": "thinking"}))

            tool_calls_made = 0
            full_response = ""
            streaming_started = False

            try:
                async for event in agent.astream_events(
                    initial_state,
                    config=config,
                    version="v2"
                ):
                    event_name = event.get("event")
                    event_data = event.get("data", {})
                    node_name = event.get("metadata", {}).get("langgraph_node", "")

                    # Notify client of tool calls in real time
                    if event_name == "on_tool_start":
                        tool_name = event.get("name", "unknown")
                        await websocket.send_text(json.dumps({
                            "type": "tool_call",
                            "tool": tool_name
                        }))
                        tool_calls_made += 1
                        logger.info(f"Tool started: {tool_name}")

                    # Stream tokens from synthesis node only
                    # Synthesis uses free-form LLM so tokens are clean human-readable text
                    elif event_name == "on_chat_model_stream" and node_name == "synthesis":
                        chunk = event_data.get("chunk")
                        if chunk and hasattr(chunk, "content") and chunk.content:
                            token = chunk.content
                            if not streaming_started:
                                streaming_started = True
                            full_response += token
                            await websocket.send_text(json.dumps({
                                "type": "token",
                                "token": token
                            }))

                # Safety fallback — if no tokens streamed, get from state
                if not full_response:
                    logger.warning("No tokens streamed, fetching from state")
                    state_snapshot = await agent.aget_state(config)
                    full_response = state_snapshot.values.get(
                        "final_response",
                        "Sorry, I could not generate a response."
                    )

                # Send completion signal with full response
                await websocket.send_text(json.dumps({
                    "type": "done",
                    "response": full_response,
                    "tool_calls_made": tool_calls_made,
                    "is_fast_path": False
                }))

                logger.info(f"Response sent ({tool_calls_made} tool calls made)")

            except Exception as e:
                logger.error(f"Agent error: {str(e)}", exc_info=True)
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "response": "Something went wrong while processing your request. Please try again.",
                    "tool_calls_made": 0,
                    "is_fast_path": False
                }))

    except WebSocketDisconnect:
        logger.error("Client disconnected")