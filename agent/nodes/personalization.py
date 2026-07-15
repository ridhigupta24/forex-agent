from agent.state import AgentState

# Default user profile flags
DEFAULT_PROFILE = {
    "risk_tolerance": "medium",        # low / medium / high
    "preferred_pairs": ["EUR/USD"],    
    "response_style": "detailed",      # brief / detailed
    "show_economic_calendar": True,    
    "show_sentiment": True,            
}

def personalization_node(state: AgentState) -> AgentState:
    """
    Applies behavioral flags to the state based on user profile.
    Detects preferences from conversation and updates profile accordingly.
    """
    profile = state.get("user_profile") or DEFAULT_PROFILE.copy()
    last_message = state["messages"][-1].content.lower() if state["messages"] else ""

    # Detect risk tolerance from message
    if any(word in last_message for word in ["conservative", "safe", "low risk"]):
        profile["risk_tolerance"] = "low"
    elif any(word in last_message for word in ["aggressive", "high risk", "risky"]):
        profile["risk_tolerance"] = "high"

    # Detect preferred pairs mentioned in conversation
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD"]
    mentioned = [p for p in pairs if p.lower() in last_message]
    if mentioned:
        profile["preferred_pairs"] = mentioned

    # Detect response style preference
    if any(word in last_message for word in ["brief", "short", "quick", "summary"]):
        profile["response_style"] = "brief"
    elif any(word in last_message for word in ["detailed", "full", "explain", "analysis"]):
        profile["response_style"] = "detailed"

    return {
        **state,
        "user_profile": profile
    }