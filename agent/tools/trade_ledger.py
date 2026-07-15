import httpx
from langchain_core.tools import tool
from db.database import insert_price, fetch_latest_price, fetch_price_history
from datetime import datetime, timedelta

@tool
def fetch_and_store_forex_price(currency_pair: str) -> dict:
    """
    Fetches the latest forex price for a currency pair from frankfurter.app 
    and stores it in the trade ledger database.
    """
    if "/" not in currency_pair:
        return {"error": "Invalid format. Use BASE/QUOTE e.g. EUR/USD"}

    base, quote = currency_pair.split("/")
    try:
        response = httpx.get(
            f"https://api.frankfurter.dev/v1/latest",
            params={"from": base, "to": quote},
            timeout=10
        )
        data = response.json()
        price = data["rates"][quote]

        # Store in DB
        insert_price(currency_pair, price, base, quote)

        return {
            "currency_pair": currency_pair,
            "price": price,
            "base": base,
            "quote": quote,
            "source": "frankfurter.app"
        }

    except Exception as e:
        return {"error": f"Failed to fetch price: {str(e)}"}


@tool
def get_latest_price_from_db(currency_pair: str) -> dict:
    """
    Retrieves the most recently stored price for a currency pair from the database.
    Use this when you want the last known price without making a new API call.
    """
    result = fetch_latest_price(currency_pair)
    if not result:
        return {"error": f"No data found for {currency_pair} in database. Try fetching live price first."}
    return result


@tool
def get_price_history(currency_pair: str, limit: int = 5) -> list:
    """
    Retrieves recent price history for a currency pair from the database.
    Use this when the user asks about price trends or historical data.
    """
    results = fetch_price_history(currency_pair, limit)
    if not results:
        return [{"error": f"No history found for {currency_pair}. Try fetching live price first."}]
    return results

@tool
def seed_price_history(currency_pair: str) -> dict:
    """
    Seeds the database with historical prices for the last 7 days.
    Use this when the user asks for price history but no data exists yet.
    This fetches one price per day for the past 7 days from frankfurter.
    """
    if "/" not in currency_pair:
        return {"error": "Invalid format. Use BASE/QUOTE e.g. EUR/USD"}

    base, quote = currency_pair.split("/")
    seeded = []

    # Fetch last 7 days of historical rates
    for days_ago in range(7, 0, -1):
        date = (datetime.utcnow() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        try:
            response = httpx.get(
                f"https://api.frankfurter.dev/v1/{date}",
                params={"from": base, "to": quote},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                price = data["rates"][quote]
                insert_price(currency_pair, price, base, quote)
                seeded.append({"date": date, "price": price})
        except Exception as e:
            continue

    return {
        "currency_pair": currency_pair,
        "seeded_records": len(seeded),
        "history": seeded
    }