from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.rate_limit import rate_limit_node
from agent.nodes.orchestrator import orchestrator_node, should_continue
from agent.nodes.personalization import personalization_node
from agent.nodes.synthesis import synthesis_node
from config import MAX_ORCHESTRATOR_DEPTH

def create_graph():
    """
    Builds and compiles the LangGraph agent graph.
    
    Flow:
    rate_limit - (fast path?) - orchestrator - (loop up to 4x) - personalization - synthesis
    """
    graph = StateGraph(AgentState)

    # Add all nodes 
    graph.add_node("rate_limit", rate_limit_node)
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("personalization", personalization_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("rate_limit")

    # Rate limit → fast path OR orchestrator 
    def after_rate_limit(state: AgentState) -> str:
        if state.get("is_fast_path"):
            return "end"  # skip agent, return instant reply
        return "orchestrator"

    graph.add_conditional_edges(
        "rate_limit",
        after_rate_limit,
        {
            "end": END,
            "orchestrator": "orchestrator"
        }
    )

    # Orchestrator loop (max depth 4) 
    graph.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "continue": "orchestrator",   # loop back
            "synthesize": "personalization"  # move forward
        }
    )

    graph.add_edge("personalization", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()


# Compile once at import time
forex_agent = create_graph()