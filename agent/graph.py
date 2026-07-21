from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
from agent.state import AgentState
from agent.nodes.orchestrator import orchestrator_node, should_continue
from agent.nodes.personalization import personalization_node
from agent.nodes.synthesis import synthesis_node
from config import DATABASE_URL
from logger import setup_logger
import psycopg

logger = setup_logger("graph")

# Global checkpointer instance
_checkpointer = None
_forex_agent = None

def get_agent():
    global _checkpointer, _forex_agent

    if _forex_agent is not None:
        return _forex_agent, _checkpointer

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

    # Connect to Postgres for checkpointing
    conn = psycopg.connect(DATABASE_URL, autocommit=True)
    _checkpointer = PostgresSaver(conn)
    _checkpointer.setup()  # creates checkpoint tables in Postgres

    _forex_agent = graph.compile(checkpointer=_checkpointer)
    logger.info("Graph compiled with Postgres checkpointer")

    return _forex_agent, _checkpointer

# Initialize at import time
forex_agent, checkpointer = get_agent()