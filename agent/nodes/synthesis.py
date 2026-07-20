from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.schemas import ForexAnalysis
from prompts.store import get_prompt
from config import OPENROUTER_API_KEY, MODEL_NAME
from logger import setup_logger
import re
import json

logger = setup_logger("synthesis")

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

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

    # Add schema instruction to system prompt
    system_content += """

CRITICAL: You MUST respond with a valid JSON object matching this exact schema:
{
    "summary": "one line summary",
    "current_price": 1.1406 or null,
    "currency_pair": "EUR/USD" or null,
    "sentiment": "bullish/bearish/neutral" or null,
    "sentiment_score": 0.65 or null,
    "key_points": ["point 1", "point 2", "point 3"],
    "risk_note": "risk consideration" or null,
    "disclaimer": "Not financial advice."
}
Respond with ONLY the JSON object. No markdown, no backticks, no extra text.
"""

    system_prompt = SystemMessage(content=system_content)
    messages = [system_prompt] + state["messages"]

    try:
        response = llm.invoke(messages)
        raw = response.content

        # Strip think tags and tool call leakage
        raw = re.sub(r'<think.*?>.*?</think.*?>', '', raw, flags=re.DOTALL).strip()
        raw = re.sub(r'<tool_calls.*?>.*?</tool_calls.*?>', '', raw, flags=re.DOTALL).strip()
        raw = re.sub(r'```json|```', '', raw).strip()

        # Parse and validate against schema
        try:
            parsed = json.loads(raw)
            validated = ForexAnalysis(**parsed)

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

        except (json.JSONDecodeError, Exception) as parse_error:
            # If schema parsing fails, fall back to raw response
            logger.warning(f"Schema parsing failed, using raw response: {parse_error}")
            clean_response = raw

    except Exception as e:
        error_msg = str(e)
        logger.error(f"LLM call failed in synthesis: {error_msg}", exc_info=True)
        from langchain_core.messages import AIMessage
        fallback = "I was unable to generate a response due to a service error. Please try again."
        return {
            **state,
            "messages": state["messages"],
            "final_response": fallback
        }

    from langchain_core.messages import AIMessage
    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=clean_response)],
        "final_response": clean_response
    }