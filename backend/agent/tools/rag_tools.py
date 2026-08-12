from langchain_core.tools import tool

@tool
def get_trading_strategy_context(currency_pair: str) -> str:
    """
    Retrieves trading strategy knowledge base context for a currency pair.
    Use this when the user asks for trading advice, strategies, or analysis tips.
    Supported pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD
    """
    # MOCKED — returns fake RAG context as if retrieved from a vector DB
    mock_context = {
        "EUR/USD": """
            EUR/USD is the most traded forex pair. Key strategies:
            - Trend following works well during ECB/Fed divergence periods
            - Support at 1.08, resistance at 1.15 are key levels
            - High liquidity during London/NY session overlap (13:00-17:00 UTC)
            - Avoid trading during low liquidity Asian session
        """,
        "GBP/USD": """
            GBP/USD (Cable) is highly volatile. Key strategies:
            - News trading effective around UK economic releases
            - Watch for BOE guidance on interest rates
            - Key support at 1.25, resistance at 1.32
            - Spreads widen significantly during off-hours
        """,
        "USD/JPY": """
            USD/JPY is sensitive to risk sentiment. Key strategies:
            - Safe haven flows strengthen JPY during market stress
            - BOJ intervention risk above 155 level
            - Carry trade popular when rate differential is wide
            - Asian session most active for this pair
        """,
    }
    context = mock_context.get(currency_pair, f"No strategy context available for {currency_pair}")
    return f"Trading Strategy Context for {currency_pair}:\n{context}"