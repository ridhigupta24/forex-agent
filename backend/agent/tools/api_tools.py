from langchain_core.tools import tool

@tool
def get_market_sentiment(currency_pair: str) -> dict:
    """
    Returns market sentiment for a forex currency pair.
    """
    mock_data = {
        "EUR/USD": {"sentiment": "bullish", "score": 0.65, "signals": ["ECB hawkish tone", "USD weakness"]},
        "GBP/USD": {"sentiment": "neutral", "score": 0.50, "signals": ["Brexit uncertainty", "mixed UK data"]},
        "USD/JPY": {"sentiment": "bearish", "score": 0.35, "signals": ["BoJ intervention risk", "risk-off mood"]},
        "USD/CHF": {"sentiment": "bearish", "score": 0.40, "signals": ["safe haven CHF demand"]},
        "AUD/USD": {"sentiment": "bullish", "score": 0.60, "signals": ["commodity rally", "China recovery"]},
    }
    # Return mock for known pairs, generic neutral for unknown
    return mock_data.get(currency_pair, {
        "sentiment": "neutral",
        "score": 0.50,
        "signals": ["insufficient data for this pair — sentiment mocked as neutral"],
        "note": "This pair is not in the sentiment database. Data is approximated."
    })


@tool
def get_economic_calendar(currency_pair: str) -> dict:
    """
    Returns upcoming economic events relevant to a currency pair.
    Use this when the user asks about upcoming events or news that may affect prices.
    """
    # MOCKED — returns fake calendar data
    mock_events = {
        "EUR/USD": [
            {"event": "ECB Interest Rate Decision", "date": "2026-07-18", "impact": "high"},
            {"event": "US CPI Data", "date": "2026-07-15", "impact": "high"},
        ],
        "GBP/USD": [
            {"event": "Bank of England Meeting", "date": "2026-07-20", "impact": "high"},
            {"event": "UK GDP Release", "date": "2026-07-16", "impact": "medium"},
        ],
        "USD/JPY": [
            {"event": "Bank of Japan Policy Meeting", "date": "2026-07-22", "impact": "high"},
            {"event": "US NFP Data", "date": "2026-07-10", "impact": "high"},
        ],
    }
    return {
        "currency_pair": currency_pair,
        "events": mock_events.get(currency_pair, [{"event": "No upcoming events", "impact": "none"}])
    }