from agent.state import AgentState
from db.database import save_user_profile, get_user_profile
from logger import setup_logger

logger = setup_logger("personalization")

DEFAULT_PROFILE = {
    "risk_tolerance": "medium",
    "preferred_pairs": ["EUR/USD"],
    "response_style": "detailed",
}

def personalization_node(state: AgentState) -> AgentState:
    """
    Detects user preferences from conversation and persists them to DB.
    Also loads existing profile from DB if available.
    """
    # Get user_id from state if available, otherwise use default
    user_id = state.get("user_id", "default-user")

    # Load existing profile from DB
    profile = get_user_profile(user_id)

    last_message = state["messages"][-1].content.lower() if state["messages"] else ""

    # Detect risk tolerance
    if any(word in last_message for word in ["conservative", "safe", "low risk"]):
        profile["risk_tolerance"] = "low"
    elif any(word in last_message for word in ["aggressive", "high risk", "risky"]):
        profile["risk_tolerance"] = "high"

    # Detect preferred pairs
    pairs = ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD"]
    mentioned = [p for p in pairs if p.lower() in last_message]
    if mentioned:
        profile["preferred_pairs"] = mentioned

    # Detect response style
    if any(word in last_message for word in ["brief", "short", "quick", "summary"]):
        profile["response_style"] = "brief"
    elif any(word in last_message for word in ["detailed", "full", "explain", "analysis"]):
        profile["response_style"] = "detailed"

    # Save updated profile to DB
    save_user_profile(user_id, profile)
    logger.info(f"Profile updated for user {user_id}: {profile}")

    return {
        **state,
        "user_profile": profile
    }