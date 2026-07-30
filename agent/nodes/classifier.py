from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from agent.state import AgentState
from agent.schemas import ForexAnalysis
from prompts.store import get_prompt
from config import OPENROUTER_API_KEY, MODEL_NAME
from logger import setup_logger

logger = setup_logger("classifier")

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

# Structured output — extracts data from tool results into ForexAnalysis object
llm_structured = llm.with_structured_output(ForexAnalysis)

def classifier_node(state: AgentState) -> AgentState:
    """
    Extracts structured data from tool results using with_structured_output().
    Does NOT generate the final response — just classifies and structures the data.
    Output is stored in state.classifier_output for synthesis node to use.
    """
    profile = state.get("user_profile", {})
    risk_tolerance = profile.get("risk_tolerance", "medium")

    system_content = get_prompt("classifier_system")
    system_content += f"\n\nUser risk tolerance: {risk_tolerance}"

    system_prompt = SystemMessage(content=system_content)
    messages = [system_prompt] + state["messages"]

    try:
        validated: ForexAnalysis = llm_structured.invoke(messages)
        logger.info(f"Classifier extracted data — pair: {validated.currency_pair}, sentiment: {validated.sentiment}")

        return {
            **state,
            "classifier_output": validated
        }

    except Exception as e:
        logger.error(f"Classifier failed: {str(e)}", exc_info=True)
        # Return None classifier output — synthesis will handle gracefully
        return {
            **state,
            "classifier_output": None
        }