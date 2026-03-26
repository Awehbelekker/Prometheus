"""Quick status check for learning DB and trading state"""
import sqlite3, os
from datetime import datetime, timedelta

def check_db(path):
    if not os.path.exists(path):
        print(f"  {path}: NOT FOUND")
        return
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"\n=== {path} ===")
    for t in sorted(tables):
        cnt = cur.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        if cnt > 0:
            print(f"  {t}: {cnt:,} rows")
    conn.close()

# Learning DB
check_db("prometheus_learning.db")

# Check recent outcomes
if os.path.exists("prometheus_learning.db"):
    conn = sqlite3.connect("prometheus_learning.db")
    cur = conn.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    
    cutoff_7d = (datetime.now() - timedelta(days=7)).isoformat()
    cutoff_1d = (datetime.now() - timedelta(days=1)).isoformat()
    
    if "learning_outcomes" in tables:
        n7 = cur.execute("SELECT COUNT(*) FROM learning_outcomes WHERE timestamp > ?", (cutoff_7d,)).fetchone()[0]
        n1 = cur.execute("SELECT COUNT(*) FROM learning_outcomes WHERE timestamp > ?", (cutoff_1d,)).fetchone()[0]
        print(f"\n  Learning outcomes: {n1} (24h), {n7} (7d)")
    
    if "signal_predictions" in tables:
        n = cur.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_pnl IS NOT NULL").fetchone()[0]
        print(f"  Signals with outcomes: {n}")
    
    if "guardian_blocks" in tables:
        rows = cur.execute("""
            SELECT block_reason, COUNT(*) FROM guardian_blocks 
            WHERE timestamp > ? GROUP BY block_reason 
            ORDER BY COUNT(*) DESC LIMIT 5
        """, (cutoff_1d,)).fetchall()
        if rows:
            print(f"\n  Guardian blocks (24h):")
            for reason, cnt in rows:
                print(f"    [{cnt}x] {reason[:70]}")
    conn.close()

# Shadow DBs
for sdb in ["multi_strategy_shadow.db", "shadow_trading.db"]:
    check_db(sdb)

# Check if live trading is running
import subprocess
try:
    result = subprocess.run(["powershell", "-c", 
        "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id,CPU,WorkingSet64 | Format-Table"],
        capture_output=True, text=True, timeout=5)
    if result.stdout.strip():
        print(f"\n=== PYTHON PROCESSES ===")
        print(result.stdout.strip())
except:
    pass
