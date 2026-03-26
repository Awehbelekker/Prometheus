"""Full Prometheus Report - March 3, 2026"""
import sqlite3
import os
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ── TRADING DATABASE ──
section("TRADING DATABASE OVERVIEW")
tdb = os.path.join(BASE, 'prometheus_trading.db')
if os.path.exists(tdb):
    db = sqlite3.connect(tdb)
    db.row_factory = sqlite3.Row
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Tables: {len(tables)}")
    for t in sorted(tables):
        try:
            cnt = db.execute(f'SELECT COUNT(*) FROM [{t}]').fetchone()[0]
            if cnt > 0:
                print(f"  {t}: {cnt:,} rows")
        except:
            pass

    section("SHADOW TRADE HISTORY")
    try:
        row = db.execute("SELECT COUNT(*) as cnt, MIN(timestamp) as first, MAX(timestamp) as last FROM shadow_trade_history").fetchone()
        print(f"Total shadow trades: {row[0]:,}")
        print(f"First: {row[1]}")
        print(f"Last:  {row[2]}")
        
        print("\nLast 20 shadow trades:")
        recent = db.execute("SELECT timestamp, symbol, action, confidence, price FROM shadow_trade_history ORDER BY timestamp DESC LIMIT 20").fetchall()
        for r in recent:
            ts = str(r[0])[:19]
            print(f"  {ts}  {r[1]:<6}  {r[2]:<5}  conf={r[3]*100:.1f}%  ${r[4]:.2f}")
    except Exception as e:
        print(f"Error: {e}")

    section("TRADE DISTRIBUTION BY SYMBOL")
    try:
        rows = db.execute("""
            SELECT symbol, COUNT(*) as trades, 
                   SUM(CASE WHEN action='BUY' THEN 1 ELSE 0 END) as buys,
                   SUM(CASE WHEN action='SELL' THEN 1 ELSE 0 END) as sells
            FROM shadow_trade_history 
            GROUP BY symbol ORDER BY trades DESC LIMIT 25
        """).fetchall()
        print(f"{'Symbol':<8} {'Total':<7} {'Buys':<7} {'Sells':<7}")
        print("-" * 30)
        for r in rows:
            print(f"{r[0]:<8} {r[1]:<7} {r[2]:<7} {r[3]:<7}")
    except Exception as e:
        print(f"Error: {e}")

    section("TODAY'S TRADES (March 3, 2026)")
    try:
        today = db.execute("""
            SELECT timestamp, symbol, action, confidence, price 
            FROM shadow_trade_history 
            WHERE timestamp >= '2026-03-03'
            ORDER BY timestamp
        """).fetchall()
        print(f"Trades today: {len(today)}")
        for r in today:
            ts = str(r[0])[:19]
            print(f"  {ts}  {r[1]:<6}  {r[2]:<5}  conf={r[3]*100:.1f}%  ${r[4]:.2f}")
    except Exception as e:
        print(f"Error: {e}")

    section("IB EXECUTIONS")
    try:
        row = db.execute("SELECT COUNT(*) as cnt, MIN(timestamp) as first, MAX(timestamp) as last FROM ib_executions").fetchone()
        print(f"Total IB executions: {row[0]:,}")
        print(f"First: {row[1]}")
        print(f"Last:  {row[2]}")
        recent = db.execute("SELECT timestamp, symbol, side, quantity, price FROM ib_executions ORDER BY timestamp DESC LIMIT 10").fetchall()
        if recent:
            print("\nLast 10 IB executions:")
            for r in recent:
                print(f"  {str(r[0])[:19]}  {r[1]:<6}  {r[2]:<5}  qty={r[3]}  ${r[4]:.2f}")
    except Exception as e:
        print(f"Error: {e}")

    section("AI ATTRIBUTION SUMMARY")
    try:
        total = db.execute("SELECT COUNT(*) FROM ai_attribution").fetchone()[0]
        print(f"Total AI votes: {total:,}")
        top = db.execute("""
            SELECT model_name, COUNT(*) as cnt, AVG(confidence) as avg_conf 
            FROM ai_attribution GROUP BY model_name ORDER BY cnt DESC LIMIT 15
        """).fetchall()
        print(f"\n{'Model':<35} {'Votes':<8} {'Avg Conf':<10}")
        print("-" * 55)
        for r in top:
            print(f"{r[0]:<35} {r[1]:<8} {r[2]:.4f}")
    except Exception as e:
        print(f"Error: {e}")

    section("SIGNAL PREDICTIONS")
    try:
        row = db.execute("SELECT COUNT(*) as cnt, MIN(timestamp) as first, MAX(timestamp) as last FROM signal_predictions").fetchone()
        print(f"Total predictions: {row[0]:,}")
        print(f"First: {row[1]}")
        print(f"Last:  {row[2]}")
        
        # Accuracy if available
        try:
            acc = db.execute("""
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN correct=1 THEN 1 ELSE 0 END) as correct
                FROM signal_predictions WHERE correct IS NOT NULL
            """).fetchone()
            if acc[0] > 0:
                print(f"Evaluated: {acc[0]:,}  Correct: {acc[1]:,}  Accuracy: {acc[1]/acc[0]*100:.1f}%")
        except:
            pass
    except Exception as e:
        print(f"Error: {e}")

    db.close()
else:
    print("Trading DB not found!")

# ── LEARNING DATABASE ──
section("LEARNING DATABASE")
ldb = os.path.join(BASE, 'prometheus_learning.db')
if os.path.exists(ldb):
    db = sqlite3.connect(ldb)
    db.row_factory = sqlite3.Row
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print(f"Tables: {len(tables)}")
    for t in sorted(tables):
        try:
            cnt = db.execute(f'SELECT COUNT(*) FROM [{t}]').fetchone()[0]
            print(f"  {t}: {cnt:,} rows")
        except:
            pass

    # Live trade outcomes
    try:
        row = db.execute("SELECT COUNT(*) FROM live_trade_outcomes").fetchone()
        if row[0] > 0:
            print(f"\nLive trade outcomes: {row[0]:,}")
            recent = db.execute("SELECT * FROM live_trade_outcomes ORDER BY rowid DESC LIMIT 5").fetchall()
            for r in recent:
                print(f"  {dict(r)}")
    except:
        pass

    # AI weight history
    try:
        row = db.execute("SELECT COUNT(*) FROM ai_weight_history").fetchone()
        if row[0] > 0:
            print(f"\nAI weight updates: {row[0]:,}")
            recent = db.execute("SELECT * FROM ai_weight_history ORDER BY rowid DESC LIMIT 5").fetchall()
            for r in recent:
                print(f"  {dict(r)}")
    except:
        pass

    # Model retrain log
    try:
        row = db.execute("SELECT COUNT(*) FROM model_retrain_log").fetchone()
        if row[0] > 0:
            print(f"\nModel retrains: {row[0]:,}")
            recent = db.execute("SELECT * FROM model_retrain_log ORDER BY rowid DESC LIMIT 5").fetchall()
            for r in recent:
                print(f"  {dict(r)}")
    except:
        pass

    # Learning insights
    try:
        row = db.execute("SELECT COUNT(*) FROM learning_insights").fetchone()
        if row[0] > 0:
            print(f"\nLearning insights: {row[0]:,}")
    except:
        pass

    db.close()
else:
    print("Learning DB not found!")

# ── MODEL FILES ──
section("ML MODELS STATUS")
model_dir = os.path.join(BASE, 'models')
if os.path.exists(model_dir):
    models = [f for f in os.listdir(model_dir) if f.endswith('.joblib') or f.endswith('.pkl')]
    print(f"Total model files: {len(models)}")
    
    # Group by type
    direction_models = [m for m in models if 'direction' in m.lower()]
    price_models = [m for m in models if 'price' in m.lower()]
    meta_models = [m for m in models if 'meta' in m.lower() or 'ensemble' in m.lower()]
    other_models = [m for m in models if m not in direction_models + price_models + meta_models]
    
    print(f"  Direction models: {len(direction_models)}")
    print(f"  Price models: {len(price_models)}")
    print(f"  Meta/Ensemble models: {len(meta_models)}")
    print(f"  Other models: {len(other_models)}")
    
    # Check staleness
    now = datetime.now()
    stale = []
    fresh = []
    for m in models:
        fp = os.path.join(model_dir, m)
        mtime = datetime.fromtimestamp(os.path.getmtime(fp))
        age_hours = (now - mtime).total_seconds() / 3600
        if age_hours > 48:
            stale.append((m, age_hours))
        else:
            fresh.append((m, age_hours))
    
    print(f"\n  Fresh (<48h): {len(fresh)}")
    print(f"  Stale (>48h): {len(stale)}")
    if fresh:
        print("\n  Recently updated models:")
        for m, h in sorted(fresh, key=lambda x: x[1])[:10]:
            print(f"    {m:<50}  {h:.1f}h ago")
else:
    print("Models directory not found!")

# ── UPTIME & SYSTEM ──
section("SYSTEM STATUS SUMMARY")
import psutil
proc = psutil.Process(15684)
uptime = datetime.now() - proc.create_time()
uptime_td = timedelta(seconds=datetime.now().timestamp() - proc.create_time())
print(f"PID: 15684")
print(f"Uptime: {uptime_td}")
print(f"CPU time: {proc.cpu_times().user:.0f}s user + {proc.cpu_times().system:.0f}s system")
print(f"Memory: {proc.memory_info().rss / 1024**2:.0f} MB")
print(f"Threads: {proc.num_threads()}")

# System resources
print(f"\nSystem RAM: {psutil.virtual_memory().percent}% used")
print(f"System CPU: {psutil.cpu_percent(interval=1)}%")
print(f"Disk: {psutil.disk_usage('C:').percent}% used")

# ── LOG STATS ──
section("LOG FILE STATS")
log_file = os.path.join(BASE, 'prometheus_headless.log')
if os.path.exists(log_file):
    size_mb = os.path.getsize(log_file) / 1024**2
    print(f"Log size: {size_mb:.1f} MB")
    
    # Count errors and warnings today
    errors = 0
    warnings = 0
    info = 0
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if '2026-03-03' in line:
                if '[ERROR]' in line:
                    errors += 1
                elif '[WARNING]' in line:
                    warnings += 1
                elif '[INFO]' in line:
                    info += 1
    print(f"Today's log entries:")
    print(f"  INFO:    {info:,}")
    print(f"  WARNING: {warnings:,}")
    print(f"  ERROR:   {errors:,}")

print(f"\n{'='*60}")
print(f"  REPORT GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}")
