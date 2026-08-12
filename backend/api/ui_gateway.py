from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from db.database import get_user_profile
from agent.tools.trade_ledger import fetch_and_store_forex_price, get_price_history
from agent.tools.api_tools import get_market_sentiment
from config import OPENROUTER_API_KEY, MODEL_NAME, LLM_BASE_URL
from logger import setup_logger
import json

logger = setup_logger("ui_gateway")
router = APIRouter()

#Component Schemas 

class PriceCardComponent(BaseModel):
    type: str = "price_card"
    pair: str
    price: Optional[float] = None
    source: str = "frankfurter.dev"

class SentimentWidgetComponent(BaseModel):
    type: str = "sentiment_widget"
    pair: str
    sentiment: Optional[str] = None
    score: Optional[float] = None
    signals: list[str] = []

class HistoryChartComponent(BaseModel):
    type: str = "history_chart"
    pair: str
    data: list[dict] = []

class AlertBannerComponent(BaseModel):
    type: str = "alert_banner"
    message: str
    severity: str = "info"  # info, warning, danger

class TradingStrategyComponent(BaseModel):
    type: str = "trading_strategy"
    pair: str
    tips: list[str] = []

class UserProfileCardComponent(BaseModel):
    type: str = "user_profile_card"
    user_id: str
    risk_tolerance: str
    preferred_pairs: list[str]
    response_style: str

class ScreenDefinition(BaseModel):
    user_id: str
    screen: str = "dashboard"
    theme: str = "dark"
    components: list[dict] = []

#LLM for component selection 

llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=OPENROUTER_API_KEY,
    base_url=LLM_BASE_URL,
    temperature=0,
)

#Endpoint 

@router.get("/ui/dashboard")
async def get_dashboard(user_id: str = "default-user"):
    """
    AI Gateway — returns a personalized UI screen definition for the given user.
    Flutter calls this endpoint and renders whatever components come back.
    """
    logger.info(f"Dashboard requested for user: {user_id}")

    # 1. Load user profile from DB
    profile = get_user_profile(user_id)
    risk_tolerance = profile.get("risk_tolerance", "medium")
    preferred_pairs = profile.get("preferred_pairs", ["EUR/USD"])
    response_style = profile.get("response_style", "detailed")

    if isinstance(preferred_pairs, str):
        preferred_pairs = [preferred_pairs]

    logger.info(f"Profile loaded — risk: {risk_tolerance}, pairs: {preferred_pairs}")

    # 2. Fetch live data for preferred pairs
    live_data = {}
    for pair in preferred_pairs[:2]:  # max 2 pairs to avoid slow response
        try:
            price_result = fetch_and_store_forex_price.invoke({"currency_pair": pair})
            sentiment_result = get_market_sentiment.invoke({"currency_pair": pair})
            history_result = get_price_history.invoke({"currency_pair": pair, "limit": 7})
            live_data[pair] = {
                "price": price_result,
                "sentiment": sentiment_result,
                "history": history_result
            }
        except Exception as e:
            logger.error(f"Failed to fetch data for {pair}: {e}")

    # 3. Ask LLM which components to show and in what order
    system_prompt = """You are a UI personalization engine for a forex trading app.
Based on the user's profile and live market data, select and order the UI components to show.

Available components:
- price_card: shows current price for a pair
- sentiment_widget: shows market sentiment
- history_chart: shows 7-day price history
- alert_banner: shows important warnings
- trading_strategy: shows trading tips
- user_profile_card: shows user's profile summary

Rules:
- Low risk users: always show alert_banner with risk warnings, avoid aggressive signals
- High risk users: show sentiment_widget and trading_strategy prominently
- Medium risk users: balanced mix
- Brief response style: max 3 components
- Detailed response style: up to 6 components
- Always include price_card for each preferred pair
- Always include user_profile_card last

Respond with ONLY a JSON array of component types in order, like:
["price_card", "history_chart", "sentiment_widget", "alert_banner", "user_profile_card"]
"""

    user_prompt = f"""User profile:
- risk_tolerance: {risk_tolerance}
- preferred_pairs: {preferred_pairs}
- response_style: {response_style}

Available market data pairs: {list(live_data.keys())}

Select and order the components."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        # Parse component order from LLM response
        raw = response.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        component_order = json.loads(raw)
        logger.info(f"LLM selected components: {component_order}")

    except Exception as e:
        logger.error(f"LLM component selection failed: {e}")
        # Fallback component order
        component_order = ["price_card", "sentiment_widget", "user_profile_card"]

    # 4. Build actual component data based on LLM selection
    components = []
    added_pairs = set()

    for component_type in component_order:
        pair = preferred_pairs[0] if preferred_pairs else "EUR/USD"
        data = live_data.get(pair, {})

        if component_type == "price_card" and "price_card" not in [c["type"] for c in components]:
            for p in preferred_pairs[:2]:
                p_data = live_data.get(p, {})
                price_info = p_data.get("price", {})
                components.append({
                    "type": "price_card",
                    "pair": p,
                    "price": price_info.get("price"),
                    "source": price_info.get("source", "frankfurter.dev")
                })

        elif component_type == "sentiment_widget":
            sentiment_info = data.get("sentiment", {})
            components.append({
                "type": "sentiment_widget",
                "pair": pair,
                "sentiment": sentiment_info.get("sentiment", "neutral"),
                "score": sentiment_info.get("score", 0.5),
                "signals": sentiment_info.get("signals", [])
            })

        elif component_type == "history_chart":
            history = data.get("history", [])
            chart_data = []
            for entry in history:
                if isinstance(entry, dict) and "timestamp" in entry:
                    chart_data.append({
                        "date": str(entry.get("timestamp", ""))[:10],
                        "price": float(entry.get("price", 0))
                    })
            components.append({
                "type": "history_chart",
                "pair": pair,
                "data": chart_data
            })

        elif component_type == "alert_banner":
            # Risk-based alerts
            alerts = {
                "low": {"message": "⚠️ Low risk mode — focus on stable major pairs and avoid volatile sessions", "severity": "info"},
                "medium": {"message": "📊 Monitor ECB and Fed announcements this week for EUR/USD volatility", "severity": "warning"},
                "high": {"message": "🔥 High volatility detected — BoJ intervention risk on USD/JPY", "severity": "danger"}
            }
            alert = alerts.get(risk_tolerance, alerts["medium"])
            components.append({
                "type": "alert_banner",
                "message": alert["message"],
                "severity": alert["severity"]
            })

        elif component_type == "trading_strategy":
            strategy_tips = {
                "EUR/USD": ["Trade during London/NY overlap (13:00-17:00 UTC)", "Watch ECB rate decisions", "Key support at 1.08, resistance at 1.15"],
                "GBP/USD": ["High volatility around UK data releases", "Watch BOE guidance", "Spreads widen during off-hours"],
                "AUD/USD": ["Sensitive to commodity prices and China data", "Most active during Asian session", "Watch RBA policy meetings"],
            }
            components.append({
                "type": "trading_strategy",
                "pair": pair,
                "tips": strategy_tips.get(pair, ["Monitor central bank policy", "Watch economic calendar", "Use proper risk management"])
            })

        elif component_type == "user_profile_card":
            components.append({
                "type": "user_profile_card",
                "user_id": user_id,
                "risk_tolerance": risk_tolerance,
                "preferred_pairs": preferred_pairs,
                "response_style": response_style
            })

    screen = ScreenDefinition(
        user_id=user_id,
        screen="dashboard",
        theme="dark",
        components=components
    )

    logger.info(f"Dashboard built — {len(components)} components for user {user_id}")
    return screen