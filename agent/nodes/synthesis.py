from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.schemas import ForexAnalysis
from prompts.store import get_prompt
from config import OPENROUTER_API_KEY, MODEL_NAME
from logger import setup_logger

logger = setup_logger("synthesis")

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

llm_structured = llm.with_structured_output(ForexAnalysis)

def synthesis_node(state: AgentState) -> AgentState:
    profile = state.get("user_profile", {})
    response_style = profile.get("response_style", "detailed")
    risk_tolerance = profile.get("risk_tolerance", "medium")

    system_content = get_prompt("synthesis_system")
    system_content += f"\n\nUser preferences:\n- Response style: {response_style}\n- Risk tolerance: {risk_tolerance}"

    if response_style == "brief":
        system_content += "\n- Keep response concise, max 3 key points"
    else:
        system_content += "\n- Provide detailed analysis, up to 5 key points"

    system_prompt = SystemMessage(content=system_content)
    messages = [system_prompt] + state["messages"]

    try:
        # LLM now returns a ForexAnalysis object directly
        # No manual JSON parsing needed
        validated: ForexAnalysis = llm_structured.invoke(messages)

        # Format into clean readable response
        lines = []
        if validated.currency_pair and validated.current_price:
            lines.append(f"**{validated.currency_pair}**: {validated.current_price}")
        if validated.sentiment:
            score = f" ({validated.sentiment_score})" if validated.sentiment_score else ""
            lines.append(f"**Sentiment**: {validated.sentiment.capitalize()}{score}")
        if validated.key_points:
            lines.append("\n**Analysis:**")
            for point in validated.key_points:
                lines.append(f"- {point}")
        if validated.risk_note:
            lines.append(f"\n**Risk Note**: {validated.risk_note}")
        lines.append(f"\n_{validated.disclaimer}_")
        lines.append(f"\n**Summary**: {validated.summary}")

        clean_response = "\n".join(lines)
        logger.info(f"Synthesis complete — response length: {len(clean_response)} chars")

    except Exception as e:
        logger.error(f"Structured output failed, falling back to raw LLM: {str(e)}")
        # Fallback — call LLM without structured output
        try:
            fallback_response = llm.invoke(messages)
            clean_response = fallback_response.content
            logger.info("Fallback raw response used successfully")
        except Exception as e2:
            logger.error(f"Fallback also failed: {str(e2)}", exc_info=True)
            clean_response = "I was unable to generate a response due to a service error. Please try again."

    from langchain_core.messages import AIMessage
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=clean_response)],
        "final_response": clean_response
    }