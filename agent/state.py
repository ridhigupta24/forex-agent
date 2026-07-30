from typing import Annotated, Any, Optional
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from agent.schemas import ForexAnalysis

class AgentState(TypedDict):
    # Conversation history
    messages: Annotated[list, add_messages]

    # Tool results storage
    forex_data: dict | None
    api_data: dict | None
    rag_context: str | None

    # Orchestrator loop control
    tool_calls_count: int
    max_depth: int

    # Personalization
    user_profile: dict

    # Classifier output — structured data extracted from tool results
    classifier_output: Optional[ForexAnalysis]

    # Final response — set by synthesis node, streamed to client
    final_response: str | None

    # Fast-path flag
    is_fast_path: bool