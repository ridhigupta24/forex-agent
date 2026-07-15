from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from agent.state import AgentState
from prompts.store import get_prompt
from config import OPENROUTER_API_KEY, MODEL_NAME
import re

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

def synthesis_node(state: AgentState) -> AgentState:
    """
    Takes all tool results from the conversation history and
    synthesizes them into a clean, final response for the user.
    Adapts response style based on user profile.
    """
    profile = state.get("user_profile", {})
    response_style = profile.get("response_style", "detailed")
    risk_tolerance = profile.get("risk_tolerance", "medium")

    # Build system prompt with personalization context
    system_content = get_prompt("synthesis_system")
    system_content += f"\n\nUser preferences:\n- Response style: {response_style}\n- Risk tolerance: {risk_tolerance}"

    if response_style == "brief":
        system_content += "\n- Keep response under 100 words, be very concise"
    else:
        system_content += "\n- Provide detailed analysis with bullet points"

    system_prompt = SystemMessage(content=system_content)

    # Pass full conversation history including all tool results
    messages = [system_prompt] + state["messages"]

    response = llm.invoke(messages)

    clean_response = response.content
    clean_response = re.sub(r'<think.*?>.*?</think.*?>', '', clean_response, flags=re.DOTALL).strip()
    clean_response = re.sub(r'<tool_calls.*?>.*?</tool_calls.*?>', '', clean_response, flags=re.DOTALL).strip()
    clean_response = re.sub(r'<tool_call.*?>.*?</tool_call.*?>', '', clean_response, flags=re.DOTALL).strip()

    return {
        **state,
        "messages": state["messages"] + [response],
        "final_response": clean_response
    }
