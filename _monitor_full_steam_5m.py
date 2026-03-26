import sqlite3
import time
from datetime import datetime
import psutil


def get_prometheus_procs():
    procs = []
    for p in psutil.process_iter(["pid", "name", "cmdline", "cpu_percent", "memory_info"]):
        try:
            cmd = " ".join(p.info.get("cmdline") or [])
            if "unified_production_server.py" in cmd:
                procs.append(
                    {
                        "pid": p.info["pid"],
                        "cpu": p.cpu_percent(interval=0.1),
                        "mem_mb": round((p.info["memory_info"].rss if p.info.get("memory_info") else 0) / 1024 / 1024, 1),
                    }
                )
        except Exception:
            continue
    return procs


def db_snapshot():
    con = sqlite3.connect("prometheus_learning.db")
    cur = con.cursor()

    def q(sql):
        try:
            cur.execute(sql)
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception:
            return None

    data = {
        "signal_predictions_total": q("SELECT COUNT(*) FROM signal_predictions"),
        "signal_predictions_5m": q("SELECT COUNT(*) FROM signal_predictions WHERE timestamp >= datetime('now','-5 minutes')"),
        "trade_history_total": q("SELECT COUNT(*) FROM trade_history"),
        "trade_history_5m": q("SELECT COUNT(*) FROM trade_history WHERE timestamp >= datetime('now','-5 minutes')"),
    }

    try:
        cur.execute("SELECT ib_count, alpaca_count, updated_at FROM routing_policy_stats WHERE id = 1")
        row = cur.fetchone()
        data["routing_policy_stats"] = row
    except Exception:
        data["routing_policy_stats"] = None

    con.close()
    return data


print("=== PROMETHEUS 5-MINUTE FULL-STEAM MONITOR ===")
start = datetime.now()
start_db = db_snapshot()
print(f"Start: {start.isoformat(timespec='seconds')}")
print(f"Start DB: {start_db}")

for i in range(1, 6):
    now = datetime.now()
    procs = get_prometheus_procs()
    snap = db_snapshot()
    print(f"\nMinute {i} @ {now.isoformat(timespec='seconds')}")
    print(f"Prometheus processes: {len(procs)} -> {procs}")
    print(f"DB snapshot: {snap}")
    if i < 5:
        time.sleep(60)

end = datetime.now()
end_db = db_snapshot()
print("\n=== SUMMARY ===")
print(f"End: {end.isoformat(timespec='seconds')}")
print(f"End DB: {end_db}")

try:
    sp_delta = (end_db.get("signal_predictions_total") or 0) - (start_db.get("signal_predictions_total") or 0)
    tr_delta = (end_db.get("trade_history_total") or 0) - (start_db.get("trade_history_total") or 0)
    print(f"signal_predictions_total delta: {sp_delta}")
    print(f"trade_history_total delta: {tr_delta}")
except Exception as e:
    print(f"Delta calc error: {e}")
