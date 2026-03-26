import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
import sqlite3

# Ensure local imports work
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_root)
from core.internal_paper_trading import paper_trading_engine

SESSIONS_DIR = os.path.join(os.getcwd(), "session_runs")
SESSION_TICK_SECONDS = 60  # snapshot cadence
PROBE_SYMBOLS = ["AAPL", "SPY", "MSFT", "NVDA", "AMZN", "TSLA"]


def ensure_dir(path: str):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def market_close_in_local(now: datetime) -> datetime:
    return now.replace(hour=16, minute=0, second=0, microsecond=0)


def market_open_in_local(now: datetime) -> datetime:
    return now.replace(hour=9, minute=30, second=0, microsecond=0)


def is_weekend(now: datetime) -> bool:
    return now.weekday() >= 5


async def snapshot(session_dir: str):
    # Update a small set of symbols to ensure fresh writes
    for s in PROBE_SYMBOLS:
        try:
            await paper_trading_engine._update_real_market_data(s)
            await asyncio.sleep(0.3)
        except Exception as e:
            print(f"Update failed for {s}: {e}")

    # Read recent rows and aggregate
    db_path = os.path.join(os.getcwd(), "paper_trading.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        """
        SELECT symbol, price, bid, ask, volume, timestamp, data_source
        FROM market_data
        ORDER BY timestamp DESC
        LIMIT 200
        """
    )
    rows = c.fetchall()
    conn.close()

    by_source = {}
    for r in rows:
        src = r[6] or "unknown"
        by_source[src] = by_source.get(src, 0) + 1

    # Trades and portfolios
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM paper_trades")
    total_trades = c.fetchone()[0]
    c.execute("SELECT SUM(pnl), SUM(intended_investment) FROM paper_portfolios")
    pnl_sum, invest_sum = c.fetchone()
    conn.close()

    snapshot_rec = {
        "timestamp": datetime.now().isoformat(),
        "market_open": await paper_trading_engine._is_market_open(),
        "by_source": by_source,
        "recent_records": len(rows),
        "total_trades": int(total_trades or 0),
        "portfolio_pnl_sum": float(pnl_sum or 0.0),
        "portfolio_invest_sum": float(invest_sum or 0.0),
    }

    with open(os.path.join(session_dir, "snapshots.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot_rec) + "\n")


async def run_session(days: int = 2):
    ensure_dir(SESSIONS_DIR)
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(SESSIONS_DIR, f"session_{session_id}")
    ensure_dir(session_dir)

    # Metadata
    meta = {
        "session_id": session_id,
        "created": datetime.now().isoformat(),
        "target_market_days": days,
        "note": "Runs during market hours; collects evidence snapshots."
    }
    with open(os.path.join(session_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Start market data feed
    await paper_trading_engine.start_market_data_feed()

    market_days_seen = set()

    try:
        while True:
            now = datetime.now()

            # Only count weekdays
            if not is_weekend(now):
                # Count a day as soon as market open window arrives (even if closed due to holiday)
                key = now.strftime("%Y-%m-%d")
                market_days_seen.add(key)

            # If we have reached the target days, exit
            if len(market_days_seen) >= days:
                # But wait until after today's market close to finalize
                if now >= market_close_in_local(now):
                    break

            # If market is open, do a snapshot every minute; else sleep until next check
            if await paper_trading_engine._is_market_open():
                await snapshot(session_dir)
                await asyncio.sleep(SESSION_TICK_SECONDS)
            else:
                # Sleep modestly when closed
                await asyncio.sleep(120)

    except Exception as e:
        # Log an error marker
        with open(os.path.join(session_dir, "errors.log"), "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - {e}\n")
        # Continue or exit depending on severity; we'll exit for safety
    finally:
        # Final snapshot
        try:
            await snapshot(session_dir)
        except Exception:
            pass
        # Write completion flag
        with open(os.path.join(session_dir, "completed.flag"), "w", encoding="utf-8") as f:
            f.write(datetime.now().isoformat())


if __name__ == "__main__":
    asyncio.run(run_session(days=2))

