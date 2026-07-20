from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes.orchestrator import orchestrator_node, should_continue
from agent.nodes.personalization import personalization_node
from agent.nodes.synthesis import synthesis_node

def create_graph():
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("personalization", personalization_node)
    graph.add_node("synthesis", synthesis_node)

    graph.set_entry_point("orchestrator")

    graph.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "continue": "orchestrator",
            "synthesize": "personalization"
        }
    )

    graph.add_edge("personalization", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()

forex_agent = create_graph()