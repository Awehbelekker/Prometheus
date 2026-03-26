import os
import sys
import json
import sqlite3
from datetime import datetime

sys.path.append(os.getcwd())

DB_PATH = os.path.join(os.getcwd(), "paper_trading.db")
SESSIONS_DIR = os.path.join(os.getcwd(), "session_runs")
REPORTS_DIR = os.path.join(os.getcwd(), "reports")


def ensure_dir(path: str):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def find_latest_session_dir() -> str:
    if not os.path.isdir(SESSIONS_DIR):
        return None
    sessions = [d for d in os.listdir(SESSIONS_DIR) if d.startswith("session_")]
    if not sessions:
        return None
    sessions.sort()
    return os.path.join(SESSIONS_DIR, sessions[-1])


def load_snapshots(session_dir: str):
    p = os.path.join(session_dir, "snapshots.jsonl")
    if not os.path.isfile(p):
        return []
    data = []
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data.append(json.loads(line))
            except Exception:
                pass
    return data


def aggregate_sources_from_db(limit=1000):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        SELECT data_source, COUNT(1) FROM (
            SELECT data_source
            FROM market_data
            ORDER BY timestamp DESC
            LIMIT ?
        ) t
        GROUP BY data_source
        """,
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return { (r[0] or "unknown"): r[1] for r in rows }


def get_trades_summary():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM paper_trades")
    count, tmin, tmax = c.fetchone()
    conn.close()
    return int(count or 0), tmin, tmax


def get_portfolio_summary():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT SUM(pnl), SUM(intended_investment), COUNT(1) FROM paper_portfolios")
    pnl_sum, invest_sum, n = c.fetchone()
    conn.close()
    return float(pnl_sum or 0.0), float(invest_sum or 0.0), int(n or 0)


def write_report(session_dir: str, snapshots: list, db_sources: dict, trades_summary, portfolio_summary):
    ensure_dir(REPORTS_DIR)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(REPORTS_DIR, f"SESSION_EVIDENCE_{ts}.md")

    total_snaps = len(snapshots)
    open_snaps = sum(1 for s in snapshots if s.get("market_open"))

    lines = []
    lines.append("# Session-Level Evidence Report\n")
    lines.append(f"Generated: {datetime.now().isoformat()}\n")
    lines.append(f"Session directory: {session_dir}\n")
    lines.append("")

    # Summary
    lines.append("## Summary\n")
    lines.append(f"- Snapshots collected: {total_snaps} (market open snapshots: {open_snaps})")
    lines.append(f"- DB provider distribution (last 1000 rows): {db_sources}")
    lines.append("")

    # Trades summary
    tcount, tmin, tmax = trades_summary
    lines.append("## Trades Summary\n")
    lines.append(f"- Total trades recorded: {tcount}")
    lines.append(f"- First trade timestamp: {tmin}")
    lines.append(f"- Last trade timestamp: {tmax}\n")

    # Portfolio summary
    pnl_sum, invest_sum, n = portfolio_summary
    lines.append("## Portfolios Summary\n")
    lines.append(f"- Portfolios: {n}")
    lines.append(f"- Sum(PnL): {pnl_sum:.2f}")
    lines.append(f"- Sum(Intended Investment): {invest_sum:.2f}\n")

    # Snapshot excerpts
    lines.append("## Snapshot Excerpts (up to last 15)\n")
    for s in snapshots[-15:]:
        lines.append(
            f"- {s.get('timestamp')} | open={s.get('market_open')} | recent={s.get('recent_records')} | "
            f"trades={s.get('total_trades')} | pnl_sum={s.get('portfolio_pnl_sum'):.2f} | sources={s.get('by_source')}"
        )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Session report written:", out_path)


if __name__ == "__main__":
    session_dir = find_latest_session_dir()
    if not session_dir:
        print("No session runs found.")
        sys.exit(0)

    snaps = load_snapshots(session_dir)
    db_src = aggregate_sources_from_db(limit=1000)
    trades = get_trades_summary()
    portfolios = get_portfolio_summary()

    write_report(session_dir, snaps, db_src, trades, portfolios)

