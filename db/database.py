import psycopg2
from psycopg2.extras import RealDictCursor
from config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Create trade ledger table if it doesn't exist"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forex_trade_ledger (
            id SERIAL PRIMARY KEY,
            currency_pair VARCHAR(10) NOT NULL,
            price DECIMAL(10, 5) NOT NULL,
            base_currency VARCHAR(5) NOT NULL,
            quote_currency VARCHAR(5) NOT NULL,
            timestamp TIMESTAMP DEFAULT NOW(),
            source VARCHAR(50) DEFAULT 'frankfurter'
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(" Database initialized — forex_trade_ledger table ready")

def fetch_latest_price(currency_pair: str):
    """Fetch latest price for a currency pair from DB"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT * FROM forex_trade_ledger
        WHERE currency_pair = %s
        ORDER BY timestamp DESC
        LIMIT 1;
    """, (currency_pair,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(result) if result else None

def fetch_price_history(currency_pair: str, limit: int = 10):
    """Fetch recent price history for a currency pair"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT * FROM forex_trade_ledger
        WHERE currency_pair = %s
        ORDER BY timestamp DESC
        LIMIT %s;
    """, (currency_pair, limit))
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(r) for r in results]

def insert_price(currency_pair: str, price: float, base: str, quote: str):
    """Insert a new price entry into the trade ledger"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO forex_trade_ledger (currency_pair, price, base_currency, quote_currency)
        VALUES (%s, %s, %s, %s);
    """, (currency_pair, price, base, quote))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Inserted price for {currency_pair}: {price}")

def has_price_history(currency_pair: str, min_records: int = 5) -> bool:
    """Check if we have enough history for a pair"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM forex_trade_ledger WHERE currency_pair = %s",
        (currency_pair,)
    )
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count >= min_records