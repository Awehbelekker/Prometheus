"""Quick DB dump for report"""
import sqlite3, os
from datetime import datetime

BASE = r'c:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform'
db = sqlite3.connect(os.path.join(BASE, 'prometheus_learning.db'))
db.row_factory = sqlite3.Row

print("=== SHADOW TRADE HISTORY ===")
row = db.execute("SELECT COUNT(*) as cnt, MIN(timestamp) as first, MAX(timestamp) as last FROM shadow_trade_history").fetchone()
print(f"Total: {row[0]}  First: {row[1]}  Last: {row[2]}")
recent = db.execute("SELECT timestamp, symbol, action, confidence, entry_price, pnl, status FROM shadow_trade_history ORDER BY timestamp DESC LIMIT 20").fetchall()
for r in recent:
    pnl = f"P/L=${r[5]:.2f}" if r[5] else ""
    print(f"  {str(r[0])[:19]}  {r[1]:<6}  {r[2]:<5}  conf={float(r[3])*100:.1f}%  entry=${r[4]:.2f}  {r[6] or ''}  {pnl}")

print("\n=== TRADE HISTORY (most recent 20) ===")
row = db.execute("SELECT COUNT(*) as cnt, MIN(timestamp) as first, MAX(timestamp) as last FROM trade_history").fetchone()
print(f"Total: {row[0]}  First: {row[1]}  Last: {row[2]}")
recent = db.execute("SELECT timestamp, symbol, action, quantity, price, profit_loss FROM trade_history ORDER BY timestamp DESC LIMIT 20").fetchall()
for r in recent:
    pl = f"P/L=${r[5]:.2f}" if r[5] else ""
    print(f"  {str(r[0])[:19]}  {r[1]:<6}  {r[2]:<5}  qty={r[3]}  price={r[4]}  {pl}")

print("\n=== TODAY'S SHADOW TRADES ===")
today = db.execute("SELECT timestamp, symbol, action, confidence, entry_price, pnl, status FROM shadow_trade_history WHERE timestamp >= '2026-03-03' ORDER BY timestamp").fetchall()
print(f"Trades today: {len(today)}")
for r in today:
    pnl = f"P/L=${r[5]:.2f}" if r[5] else ""
    print(f"  {str(r[0])[:19]}  {r[1]:<6}  {r[2]:<5}  conf={float(r[3])*100:.1f}%  entry=${r[4]:.2f}  {r[6] or ''}  {pnl}")

print("\n=== TODAY'S TRADE HISTORY ===")
today2 = db.execute("SELECT timestamp, symbol, action, quantity, price, profit_loss FROM trade_history WHERE timestamp >= '2026-03-03' ORDER BY timestamp").fetchall()
print(f"Trades today: {len(today2)}")
for r in today2:
    pl = f"P/L=${r[5]:.2f}" if r[5] else ""
    print(f"  {str(r[0])[:19]}  {r[1]:<6}  {r[2]:<5}  qty={r[3]}  price={r[4]}  {pl}")

print("\n=== TRADE P/L BY SYMBOL ===")
rows = db.execute("""
    SELECT symbol, COUNT(*) as trades,
           SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as buys,
           SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as sells,
           ROUND(SUM(COALESCE(profit_loss, 0)), 2) as total_pl
    FROM trade_history GROUP BY symbol ORDER BY trades DESC
""").fetchall()
print(f"{'Symbol':<8} {'Trades':<8} {'Buys':<7} {'Sells':<7} {'Total P/L'}")
print("-" * 45)
for r in rows:
    print(f"{r[0]:<8} {r[1]:<8} {r[2]:<7} {r[3]:<7} ${r[4]:.2f}")

print("\n=== OPEN POSITIONS ===")
try:
    pos = db.execute("SELECT * FROM open_positions").fetchall()
    print(f"Open: {len(pos)}")
    for p in pos:
        print(f"  {dict(p)}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== POSITION TRACKING ===")
try:
    pos = db.execute("SELECT * FROM position_tracking ORDER BY rowid DESC LIMIT 10").fetchall()
    for p in pos:
        print(f"  {dict(p)}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== SHADOW SESSIONS ===")
row = db.execute("SELECT COUNT(*) as cnt, MIN(started_at) as first, MAX(started_at) as last FROM shadow_sessions").fetchone()
print(f"Total sessions: {row[0]}  First: {row[1]}  Last: {row[2]}")
ss = db.execute("SELECT session_id, config_name, starting_capital, current_capital, total_trades, winning_trades, total_pnl, win_rate, status FROM shadow_sessions ORDER BY rowid DESC LIMIT 5").fetchall()
for s in ss:
    print(f"  {s[1] or 'default':<20} capital=${s[2]:.0f}->${s[3]:.0f}  trades={s[4]}  wins={s[5]}  P/L=${s[6]:.2f}  WR={s[7]*100 if s[7] else 0:.1f}%  {s[8]}")

print("\n=== PERFORMANCE METRICS ===")
try:
    recent = db.execute("SELECT * FROM performance_metrics ORDER BY rowid DESC LIMIT 5").fetchall()
    for r in recent:
        print(f"  {dict(r)}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== AI ATTRIBUTION TOP MODELS ===")
total = db.execute("SELECT COUNT(*) FROM ai_attribution").fetchone()[0]
print(f"Total AI votes: {total:,}")
top = db.execute("""
    SELECT ai_system, COUNT(*) as cnt, ROUND(AVG(confidence), 4) as avg_conf
    FROM ai_attribution GROUP BY ai_system ORDER BY cnt DESC LIMIT 15
""").fetchall()
print(f"{'Model':<40} {'Votes':<8} {'Avg Conf'}")
print("-" * 60)
for r in top:
    print(f"{r[0]:<40} {r[1]:<8} {r[2]}")

print("\n=== SIGNAL PREDICTIONS ===")
row = db.execute("SELECT COUNT(*) as cnt, MIN(timestamp) as first, MAX(timestamp) as last FROM signal_predictions").fetchone()
print(f"Total: {row[0]:,}  First: {row[1]}  Last: {row[2]}")
# Signal breakdown
sigs = db.execute("""
    SELECT action, COUNT(*) as cnt FROM signal_predictions GROUP BY action ORDER BY cnt DESC
""").fetchall()
for s in sigs:
    print(f"  {s[0]}: {s[1]:,}")

print("\n=== MODEL RETRAIN LOG (last 10) ===")
retrains = db.execute("SELECT timestamp, symbol, model_type, success, new_metric, samples, reason FROM model_retrain_log ORDER BY id DESC LIMIT 10").fetchall()
for r in retrains:
    status = "OK" if r[3] else "FAIL"
    reason = r[5] if not r[3] else ""
    metric = f"metric={r[4]:.3f}" if r[4] is not None else "metric=N/A"
    print(f"  {str(r[0])[:19]}  {r[1]:<6}  {r[2]:<10}  {status}  {metric}  n={r[5]}  {r[6]}")

print("\n=== LEARNING OUTCOMES ===")
row = db.execute("SELECT COUNT(*) FROM learning_outcomes").fetchone()
print(f"Total outcomes: {row[0]}")
try:
    recent = db.execute("SELECT * FROM learning_outcomes ORDER BY rowid DESC LIMIT 5").fetchall()
    for r in recent:
        d = dict(r)
        print(f"  {d}")
except:
    pass

print("\n=== MULTI-STRATEGY LEADERBOARD ===")
try:
    strats = db.execute("SELECT * FROM multi_strategy_leaderboard ORDER BY rowid DESC LIMIT 10").fetchall()
    for s in strats:
        print(f"  {dict(s)}")
except:
    pass

db.close()

# System stats
print("\n=== SYSTEM STATS ===")
import psutil
try:
    proc = psutil.Process(15684)
    ct = datetime.fromtimestamp(proc.create_time())
    uptime = datetime.now() - ct
    print(f"PID: 15684")
    print(f"Started: {ct.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Uptime: {uptime}")
    print(f"CPU time: {proc.cpu_times().user:.0f}s user + {proc.cpu_times().system:.0f}s system")
    print(f"Memory: {proc.memory_info().rss / 1024**2:.0f} MB")
    print(f"Threads: {proc.num_threads()}")
except Exception as e:
    print(f"Error: {e}")

print(f"\nSystem RAM: {psutil.virtual_memory().percent}% used ({psutil.virtual_memory().used/1024**3:.1f}GB / {psutil.virtual_memory().total/1024**3:.1f}GB)")
print(f"System CPU: {psutil.cpu_percent(interval=1)}%")

# Log stats
print("\n=== LOG FILE STATS ===")
log_file = os.path.join(BASE, 'prometheus_headless.log')
if os.path.exists(log_file):
    size_mb = os.path.getsize(log_file) / 1024**2
    print(f"Log size: {size_mb:.1f} MB")
    errors = warnings = info = 0
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '2026-03-03' in line:
                if '[ERROR]' in line: errors += 1
                elif '[WARNING]' in line: warnings += 1
                elif '[INFO]' in line: info += 1
    print(f"Today's entries: INFO={info:,}  WARNING={warnings:,}  ERROR={errors:,}")

# Models
print("\n=== ML MODELS ===")
for d in ['models', 'ml_models', 'trained_models']:
    md = os.path.join(BASE, d)
    if os.path.exists(md):
        files = os.listdir(md)
        models = [f for f in files if any(f.endswith(e) for e in ['.joblib', '.pkl', '.h5', '.pt'])]
        print(f"  {d}/: {len(models)} model files, {len(files)} total files")
        if models:
            for m in sorted(models)[:10]:
                fp = os.path.join(md, m)
                age_h = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(fp))).total_seconds() / 3600
                sz = os.path.getsize(fp) / 1024
                print(f"    {m:<50} {sz:.0f}KB  {age_h:.1f}h ago")

# Check all directories for model files
print("\n  Searching for model files in subdirectories...")
for root, dirs, files in os.walk(BASE):
    for f in files:
        if f.endswith('.joblib') or f.endswith('.pkl'):
            fp = os.path.join(root, f)
            rel = os.path.relpath(fp, BASE)
            age_h = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(fp))).total_seconds() / 3600
            sz = os.path.getsize(fp) / 1024
            if age_h < 72:  # Show models updated in last 3 days
                print(f"    {rel:<60} {sz:.0f}KB  {age_h:.1f}h ago")

print(f"\n{'='*60}")
print(f"  REPORT COMPLETE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}")
