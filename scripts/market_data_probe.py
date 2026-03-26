import asyncio
import sqlite3
import sys, os
sys.path.append(os.getcwd())
from core.internal_paper_trading import paper_trading_engine

DB_PATH = r"C:\\Users\\Judy\\Desktop\\PROMETHEUS-Trading-Platform\\paper_trading.db"

async def main():
    # Update a single symbol to force a fresh market_data record
    await paper_trading_engine._update_real_market_data('AAPL')

if __name__ == "__main__":
    asyncio.run(main())
    
    # Query recent records and print data sources
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT symbol, price, data_source, timestamp FROM market_data ORDER BY timestamp DESC LIMIT 5")
    rows = c.fetchall()
    for r in rows:
        print(r)
    conn.close()

