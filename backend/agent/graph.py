from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from agent.state import AgentState
from agent.nodes.orchestrator import orchestrator_node, should_continue
from agent.nodes.personalization import personalization_node
from agent.nodes.classifier import classifier_node
from agent.nodes.synthesis import synthesis_node
from config import DATABASE_URL
from logger import setup_logger
from psycopg_pool import AsyncConnectionPool

logger = setup_logger("graph")

_forex_agent = None
_checkpointer = None
_pool = None


async def init_agent():
    """
    Initializes the LangGraph agent with a persistent async connection pool.
    Called once at startup — pool stays open for lifetime of server.
    
    Flow: orchestrator → personalization → classifier → synthesis → END
    - orchestrator: tool-calling loop (max depth 4)
    - personalization: behavioral flags, no LLM
    - classifier: with_structured_output() — extracts structured data from tool results
    - synthesis: free-form LLM — generates human-readable streaming response
    """
    global _forex_agent, _checkpointer, _pool

    # Persistent async connection pool for checkpointer
    _pool = AsyncConnectionPool(
        conninfo=DATABASE_URL,
        max_size=10,
        open=False
    )
    await _pool.open()
    logger.info("Async connection pool created for checkpointer")

    # Async checkpointer — supports astream_events()
    _checkpointer = AsyncPostgresSaver(_pool)
    await _checkpointer.setup()
    logger.info("Async Postgres checkpointer initialized")

    # Build graph
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("personalization", personalization_node)
    graph.add_node("classifier", classifier_node)
    graph.add_node("synthesis", synthesis_node)

    # Entry point
    graph.set_entry_point("orchestrator")

    # Orchestrator loop — keeps calling tools until done or max depth reached
    graph.add_conditional_edges(
        "orchestrator",
        should_continue,
        {
            "continue": "orchestrator",
            "synthesize": "personalization"
        }
    )

    # Linear flow after orchestrator finishes
    graph.add_edge("personalization", "classifier")   # extract structured data
    graph.add_edge("classifier", "synthesis")          # generate streaming response
    graph.add_edge("synthesis", END)

    _forex_agent = graph.compile(checkpointer=_checkpointer)
    logger.info("Graph compiled — flow: orchestrator → personalization → classifier → synthesis")

    return _forex_agent


async def close_agent():
    """Close connection pool on server shutdown"""
    global _pool
    if _pool:
        await _pool.close()
        logger.info("Checkpointer connection pool closed")


def get_agent():
    return _forex_agent