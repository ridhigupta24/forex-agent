from typing import Annotated, Any
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class AgentState(TypedDict):
    # Conversation history — add_messages means new messages get appended, not overwritten
    messages: Annotated[list, add_messages]
    
    # Tool results storage
    forex_data: dict | None          # filled by trade ledger tool
    api_data: dict | None            # filled by mock API tool
    rag_context: str | None          # filled by mock RAG tool
    
    # Orchestrator loop control
    tool_calls_count: int            
    max_depth: int                   
    
    # Personalization
    user_profile: dict             
    
    # Response
    final_response: str | None      
    
    # Fast-path flag
    is_fast_path: bool               # True if greeting/out-of-scope, skip agent entirely