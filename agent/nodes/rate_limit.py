from datetime import datetime, timedelta
from agent.state import AgentState
import re

# Simple in-memory rate limiter (per session)
request_timestamps = []
RATE_LIMIT_PER_MINUTE = 10

# Fast-path keywords 
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
OUT_OF_SCOPE = ["stock", "crypto", "bitcoin", "ethereum", "nft", "real estate", "gold", "silver"]

def rate_limit_node(state: AgentState) -> AgentState:
    """
    Two jobs:
    1. Check if user has exceeded rate limit (10 requests/min)
    2. Check if message is a greeting or out-of-scope — if so, set fast-path flag
    """
    global request_timestamps

    # --- Rate limiting ---
    now = datetime.utcnow()
    
    request_timestamps = [t for t in request_timestamps if now - t < timedelta(minutes=1)]

    if len(request_timestamps) >= RATE_LIMIT_PER_MINUTE:
        return {
            **state,
            "is_fast_path": True,
            "final_response": "Rate limit exceeded. Please wait a moment before sending another message."
        }

    request_timestamps.append(now)

    # --- Fast-path check ---
    last_message = state["messages"][-1].content.lower().strip()

    # Check for greetings
    if any(re.search(rf'\b{re.escape(greet)}\b', last_message) for greet in GREETINGS):
        if len(last_message.split()) <= 4:
            return {
                **state,
                "is_fast_path": True,
                "final_response": "Hello! I'm your forex trading assistant. Ask me about currency pairs like EUR/USD, GBP/USD, USD/JPY and more!"
            }

    # Check for out-of-scope
    if any(re.search(rf'\b{re.escape(oos)}\b', last_message) for oos in OUT_OF_SCOPE):
        return {
            **state,
            "is_fast_path": True,
            "final_response": "I'm specialized in forex trading only. I can help you with currency pairs like EUR/USD, GBP/USD, USD/JPY, USD/CHF, and AUD/USD."
        }

    
    return {
        **state,
        "is_fast_path": False
    }