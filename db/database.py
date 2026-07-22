from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from config import DATABASE_URL
from logger import setup_logger

logger = setup_logger("database")

_pool: ConnectionPool = None

def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            DATABASE_URL,
            min_size=2,
            max_size=10,
            kwargs={"row_factory": dict_row}
        )
        logger.info("Database connection pool created")
    return _pool

def close_pool():
    global _pool
    if _pool:
        _pool.close()
        logger.info("Database connection pool closed")

async def init_db():
    pool = get_pool()
    with pool.connection() as conn:
        conn.execute("""
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
    logger.info("Database initialized — forex_trade_ledger table ready")

def fetch_latest_price(currency_pair: str):
    pool = get_pool()
    with pool.connection() as conn:
        result = conn.execute("""
            SELECT * FROM forex_trade_ledger
            WHERE currency_pair = %s
            ORDER BY timestamp DESC
            LIMIT 1;
        """, (currency_pair,)).fetchone()
        return dict(result) if result else None

def fetch_price_history(currency_pair: str, limit: int = 10):
    pool = get_pool()
    with pool.connection() as conn:
        results = conn.execute("""
            SELECT * FROM forex_trade_ledger
            WHERE currency_pair = %s
            ORDER BY timestamp DESC
            LIMIT %s;
        """, (currency_pair, limit)).fetchall()
        return [dict(r) for r in results]

def insert_price(currency_pair: str, price: float, base: str, quote: str):
    pool = get_pool()
    with pool.connection() as conn:
        conn.execute("""
            INSERT INTO forex_trade_ledger (currency_pair, price, base_currency, quote_currency)
            VALUES (%s, %s, %s, %s);
        """, (currency_pair, price, base, quote))
    logger.info(f"Inserted price for {currency_pair}: {price}")