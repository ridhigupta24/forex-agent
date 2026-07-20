from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.tools.api_tools import get_market_sentiment, get_economic_calendar
from agent.tools.rag_tools import get_trading_strategy_context
from prompts.store import get_prompt
from config import OPENROUTER_API_KEY, MODEL_NAME
from agent.tools.trade_ledger import (
    fetch_and_store_forex_price,
    get_latest_price_from_db,
    get_price_history,
    seed_price_history
)
from logger import setup_logger

logger = setup_logger("orchestrator")

# All tools available to the orchestrator
TOOLS = [
    fetch_and_store_forex_price,
    get_latest_price_from_db,
    get_price_history,
    seed_price_history,
    get_market_sentiment,
    get_economic_calendar,
    get_trading_strategy_context,
]

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

llm_with_tools = llm.bind_tools(TOOLS)

def orchestrator_node(state: AgentState) -> AgentState:
    """
    Core agent loop — LLM decides which tools to call.
    Runs until LLM stops calling tools or max depth (4) is reached.
    """
    # Build messages with system prompt
    system_prompt = SystemMessage(content=get_prompt("orchestrator_system"))
    messages = [system_prompt] + state["messages"]

    tool_calls = []
    response = None

    try:
        response = llm_with_tools.invoke(messages)
        #logger.debug(f"Orchestrator LLM call successful — tool calls: {len(tool_calls)}")
    except Exception as e:
        error_msg = str(e)
        logger.error(f"LLM call failed in orchestrator: {error_msg}")
        from langchain_core.messages import AIMessage
        return {
            **state,
            "messages": state["messages"] + [
                AIMessage(content=f"I encountered an error while processing your request. Please try again.")
                ],
                "tool_calls_count": state["tool_calls_count"],
                }

    # Check if LLM wants to call any tools
    tool_calls = getattr(response, "tool_calls", [])

    if not tool_calls:
        return {
            **state,
            "messages": state["messages"] + [response],
            "tool_calls_count": state["tool_calls_count"],
        }

    # Execute each tool the LLM requested
    tool_results = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        tool_fn = next((t for t in TOOLS if t.name == tool_name), None)
        if tool_fn:
            try:
                result = tool_fn.invoke(tool_args)
                logger.info(f"Tool called: {tool_name} with args: {tool_args}")
            except Exception as e:
                result = {"error": str(e)}
        else:
            result = {"error": f"Tool {tool_name} not found"}

        # Format result as a tool message
        from langchain_core.messages import ToolMessage
        tool_results.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_id,
                name=tool_name
            )
        )

    new_count = state["tool_calls_count"] + 1

    return {
        **state,
        "messages": state["messages"] + [response] + tool_results,
        "tool_calls_count": new_count,
    }


def should_continue(state: AgentState) -> str:
    """
    Conditional edge — decides what happens after orchestrator runs.
    Returns 'continue' to loop back, or 'synthesize' to move forward.
    """
    # Force synthesis if max depth reached
    if state["tool_calls_count"] >= state["max_depth"]:
        return "synthesize"

    # Check if last message has tool calls
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return "synthesize"

    
    return "continue"