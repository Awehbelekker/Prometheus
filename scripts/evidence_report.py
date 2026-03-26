import asyncio
import sqlite3
import os
import sys
from datetime import datetime

# Ensure local imports work when run as a script
sys.path.append(os.getcwd())

from core.internal_paper_trading import paper_trading_engine

DB_PATH = os.path.join(os.getcwd(), "paper_trading.db")
REPORTS_DIR = os.path.join(os.getcwd(), "reports")
SYMBOLS = ["AAPL", "SPY", "MSFT", "NVDA", "AMZN", "TSLA"]


def ensure_reports_dir():
    if not os.path.isdir(REPORTS_DIR):
        os.makedirs(REPORTS_DIR, exist_ok=True)


async def fetch_quotes(symbols):
    for s in symbols:
        try:
            await paper_trading_engine._update_real_market_data(s)
            # Small delay to avoid SQLite lock contention and provider rate limits
            await asyncio.sleep(0.4)
        except Exception as e:
            print(f"Failed updating {s}: {e}")


def read_market_data(limit=60):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT symbol, price, bid, ask, volume, timestamp, data_source
        FROM market_data
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = c.fetchall()
    conn.close()
    return rows


def aggregate_by_source(rows):
    agg = {}
    for r in rows:
        src = r[6] or "unknown"
        agg[src] = agg.get(src, 0) + 1
    return agg


def write_report(rows, by_source):
    ensure_reports_dir()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, f"EVIDENCE_REAL_DATA_{ts}.md")

    lines = []
    lines.append(f"# Real Market Data Evidence Report\n")
    lines.append(f"Generated: {datetime.now().isoformat()}\n")
    lines.append("")

    # Environment snapshot (non-secret)
    lines.append("## Environment Snapshot (non-secret)\n")
    for key in [
        "ALPACA_API_KEY",
        "ALPACA_SECRET_KEY",
        "APCA_API_KEY_ID",
        "APCA_API_SECRET_KEY",
        "POLYGON_API_KEY",
        "ALPHA_VANTAGE_API_KEY",
    ]:
        val = os.getenv(key)
        status = "present" if val else "missing"
        lines.append(f"- {key}: {status}")
    lines.append("")

    # Provider distribution
    lines.append("## Provider Distribution (last N records)\n")
    for src, cnt in by_source.items():
        lines.append(f"- {src}: {cnt}")
    lines.append("")

    # Recent records (trim to 15 for display)
    lines.append("## Recent Records (up to 15 shown)\n")
    for r in rows[:15]:
        sym, price, bid, ask, vol, ts_row, src = r
        lines.append(f"- {ts_row} | {sym} | {price:.4f} | bid {bid} | ask {ask} | vol {vol} | src {src}")
    lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path


async def main():
    # Fetch fresh data
    await fetch_quotes(SYMBOLS)
    # Read and aggregate
    rows = read_market_data(limit=120)
    agg = aggregate_by_source(rows)
    # Write report
    report_path = write_report(rows, agg)
    print("Report written:", report_path)


if __name__ == "__main__":
    asyncio.run(main())

