import os, sqlite3, json
from datetime import datetime

ROOT = r"C:\\Users\\Judy\\Desktop\\PROMETHEUS-Trading-Platform"

def probe_db(db_name, queries):
    path = os.path.join(ROOT, db_name)
    print(f"\n=== {db_name} ===")
    print("exists:", os.path.exists(path))
    if not os.path.exists(path):
        return
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cur.fetchall()]
        print("tables:", tables)
        for label, sql in queries:
            try:
                cur.execute(sql)
                rows = cur.fetchall()
                print(f"-- {label}: {len(rows)} rows")
                for r in rows:
                    print("   ", r)
            except Exception as e:
                print(f"-- {label} error: {e}")
        conn.close()
    except Exception as e:
        print("DB open error:", e)

if __name__ == "__main__":
    # Probe Alpaca request tracker
    probe_db("alpaca_requests.db", [
        ("recent_requests", "SELECT request_id, endpoint, status_code, timestamp FROM alpaca_requests ORDER BY id DESC LIMIT 5"),
        ("failed_24h", "SELECT request_id, endpoint, status_code, error_message FROM alpaca_requests WHERE status_code >= 400 ORDER BY id DESC LIMIT 5"),
    ])

    # Probe internal paper trading DB
    probe_db("paper_trading.db", [
        ("counts", "SELECT COUNT(*) FROM paper_trades"),
        ("recent_trades", "SELECT user_id, symbol, side, quantity, price, timestamp FROM paper_trades ORDER BY timestamp DESC LIMIT 5"),
        ("recent_market_data", "SELECT symbol, price, timestamp, data_source FROM market_data ORDER BY timestamp DESC LIMIT 5"),
    ])

    # Probe revolutionary session reports presence
    for fn in sorted(os.listdir(ROOT)):
        if fn.startswith("revolutionary_session_report_") and fn.endswith(".json"):
            print("found session report:", fn)
            try:
                with open(os.path.join(ROOT, fn), 'r') as f:
                    data = json.load(f)
                summary = data.get('session_summary', {})
                print("  summary:", {k: summary.get(k) for k in ['start_time','end_time','starting_capital','final_value','total_pnl','total_trades']})
            except Exception as e:
                print("  read error:", e)

