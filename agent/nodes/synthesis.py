from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agent.state import AgentState
from config import OPENROUTER_API_KEY, MODEL_NAME
from logger import setup_logger

logger = setup_logger("synthesis")

# Normal LLM — no structured output, supports token streaming
llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

def synthesis_node(state: AgentState) -> AgentState:
    """
    Generates the final human-readable response using free-form LLM generation.
    Takes structured data from classifier_output and turns it into a clean response.
    This node supports token streaming via astream_events().
    """
    profile = state.get("user_profile", {})
    response_style = profile.get("response_style", "detailed")
    risk_tolerance = profile.get("risk_tolerance", "medium")
    classifier_output = state.get("classifier_output")

    # Build context from classifier output if available
    if classifier_output:
        data_context = f"""
Structured data extracted from analysis:
- Currency Pair: {classifier_output.currency_pair or 'N/A'}
- Current Price: {classifier_output.current_price or 'N/A'}
- Sentiment: {classifier_output.sentiment or 'N/A'} (score: {classifier_output.sentiment_score or 'N/A'})
- Key Points: {', '.join(classifier_output.key_points) if classifier_output.key_points else 'N/A'}
- Risk Note: {classifier_output.risk_note or 'N/A'}
- Summary: {classifier_output.summary or 'N/A'}
"""
    else:
        # Classifier failed — extract what we can from conversation history directly
        # Find the last tool message in history and use it
        tool_results = []
        for msg in state["messages"]:
            if hasattr(msg, "name") and msg.name:
                tool_results.append(f"Tool '{msg.name}' returned: {msg.content}")

        if tool_results:
            data_context = f"""The following tool results were retrieved — use them to generate your response:
            {chr(10).join(tool_results)}"""
        else:
            data_context = "Answer based on your forex knowledge for the user's question."

    system_content = f"""You are a forex trading assistant delivering a clear, helpful response.

{data_context}

User preferences:
- Response style: {response_style}
- Risk tolerance: {risk_tolerance}

Guidelines:
- Write in natural, flowing prose — NOT JSON
- Use markdown formatting (bold, bullet points)
- Lead with the most important data point
- Keep response under 200 words
- End with a one-line summary
- Add "Not financial advice." at the end
{"- Be very concise, max 3 bullet points" if response_style == "brief" else "- Provide detailed analysis, up to 5 bullet points"}
"""

    try:
        messages = [SystemMessage(content=system_content)] + state["messages"]
        response = llm.invoke(messages)
        final_response = response.content.strip()

        # If somehow empty, provide a default
        if not final_response:
            final_response = "I was unable to generate a response for this query. Please try again."
        logger.info(f"Synthesis complete — response length: {len(final_response)} chars")

        from langchain_core.messages import AIMessage
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=final_response)],
            "final_response": final_response
        }

    except Exception as e:
        logger.error(f"Synthesis failed: {str(e)}", exc_info=True)
        fallback = "I was unable to generate a response due to a service error. Please try again."
        from langchain_core.messages import AIMessage
        return {
            **state,
            "messages": state["messages"] + [AIMessage(content=fallback)],
            "final_response": fallback
        }