"""
PROMETHEUS FULL SYSTEM AUDIT
============================
Deep dive into every system, every config, every trade.
No fluff. Just facts.
"""
import os
import sys
import json
import sqlite3
import time
import socket
import glob
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter

BASE = Path(__file__).parent
os.chdir(BASE)

def section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")

def subsection(title):
    print(f"\n  --- {title} ---")

# ============================================================================
# 1. TRADING DATABASE — REAL TRADES
# ============================================================================
section("1. TRADING DATABASE — REAL TRADE HISTORY")

for db_name in ["prometheus_learning.db", "prometheus_trading.db"]:
    db_path = BASE / db_name
    if not db_path.exists():
        print(f"  {db_name}: NOT FOUND")
        continue
    
    size_mb = db_path.stat().st_size / (1024*1024)
    conn = sqlite3.connect(str(db_path), timeout=10)
    cur = conn.cursor()
    
    # List all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"\n  {db_name} ({size_mb:.1f} MB, {len(tables)} tables)")
    print(f"  Tables: {', '.join(tables[:15])}{'...' if len(tables) > 15 else ''}")
    
    # Trade history deep dive
    if "trade_history" in tables:
        subsection(f"{db_name} — trade_history")
        cur.execute("SELECT COUNT(*) FROM trade_history")
        total = cur.fetchone()[0]
        print(f"  Total trades: {total}")
        
        if total > 0:
            # Date range
            cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM trade_history")
            min_ts, max_ts = cur.fetchone()
            print(f"  Date range: {min_ts} to {max_ts}")
            
            # By broker
            cur.execute("SELECT broker, COUNT(*) FROM trade_history GROUP BY broker ORDER BY COUNT(*) DESC")
            print(f"  By broker:")
            for broker, cnt in cur.fetchall():
                print(f"    {broker or 'NULL'}: {cnt} trades")
            
            # By action
            cur.execute("SELECT action, COUNT(*) FROM trade_history GROUP BY action ORDER BY COUNT(*) DESC")
            print(f"  By action:")
            for action, cnt in cur.fetchall():
                print(f"    {action}: {cnt}")
            
            # By symbol (top 15)
            cur.execute("SELECT symbol, COUNT(*) FROM trade_history GROUP BY symbol ORDER BY COUNT(*) DESC LIMIT 15")
            print(f"  Top symbols:")
            for sym, cnt in cur.fetchall():
                print(f"    {sym}: {cnt} trades")
            
            # P/L analysis
            cur.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL")
            closed = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NULL")
            open_trades = cur.fetchone()[0]
            print(f"\n  Closed trades: {closed}")
            print(f"  Open/no-exit trades: {open_trades}")
            
            if closed > 0:
                cur.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL")
                wins = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss <= 0 AND exit_price IS NOT NULL")
                losses = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(profit_loss), 0) FROM trade_history WHERE exit_price IS NOT NULL")
                total_pnl = cur.fetchone()[0]
                cur.execute("SELECT AVG(profit_loss) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL")
                avg_win = cur.fetchone()[0] or 0
                cur.execute("SELECT AVG(profit_loss) FROM trade_history WHERE profit_loss <= 0 AND exit_price IS NOT NULL")
                avg_loss = cur.fetchone()[0] or 0
                cur.execute("SELECT MAX(profit_loss) FROM trade_history WHERE exit_price IS NOT NULL")
                best = cur.fetchone()[0] or 0
                cur.execute("SELECT MIN(profit_loss) FROM trade_history WHERE exit_price IS NOT NULL")
                worst = cur.fetchone()[0] or 0
                
                win_rate = round(wins / closed * 100, 1) if closed > 0 else 0
                print(f"\n  P/L SUMMARY:")
                print(f"    Wins: {wins}, Losses: {losses}")
                print(f"    Win Rate: {win_rate}%")
                print(f"    Total P/L: ${total_pnl:.2f}")
                print(f"    Avg Win: ${avg_win:.2f}")
                print(f"    Avg Loss: ${avg_loss:.2f}")
                print(f"    Best Trade: ${best:.2f}")
                print(f"    Worst Trade: ${worst:.2f}")
                if avg_loss != 0:
                    print(f"    Win/Loss Ratio: {abs(avg_win/avg_loss):.2f}")
            
            # Monthly breakdown
            subsection("Monthly P/L Breakdown")
            cur.execute("""
                SELECT strftime('%Y-%m', timestamp) as month, 
                       COUNT(*) as trades,
                       SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
                       COALESCE(SUM(profit_loss), 0) as pnl
                FROM trade_history 
                WHERE exit_price IS NOT NULL
                GROUP BY month ORDER BY month
            """)
            rows = cur.fetchall()
            if rows:
                print(f"    {'Month':<10} {'Trades':>7} {'Wins':>6} {'WinRate':>8} {'P/L':>12}")
                print(f"    {'-'*45}")
                for month, trades, wins, pnl in rows:
                    wr = round(wins/trades*100,1) if trades > 0 else 0
                    print(f"    {month:<10} {trades:>7} {wins:>6} {wr:>7.1f}% ${pnl:>10.2f}")
            
            # Recent 20 trades
            subsection("Last 20 Trades")
            cur.execute("""
                SELECT symbol, action, price, quantity, timestamp, profit_loss, broker,
                       COALESCE(exit_price, 0) as ep, COALESCE(exit_reason, '') as er
                FROM trade_history ORDER BY id DESC LIMIT 20
            """)
            rows = cur.fetchall()
            print(f"    {'Symbol':<12} {'Action':<6} {'Price':>10} {'Qty':>8} {'P/L':>10} {'Broker':<12} {'Time'}")
            print(f"    {'-'*85}")
            for sym, action, price, qty, ts, pnl, broker, ep, er in rows:
                pnl_str = f"${pnl:.2f}" if pnl else "open"
                print(f"    {sym:<12} {action:<6} ${price or 0:>9.2f} {qty or 0:>8.4f} {pnl_str:>10} {broker or 'n/a':<12} {ts}")
    
    # Signal predictions
    if "signal_predictions" in tables:
        subsection(f"{db_name} — signal_predictions")
        cur.execute("SELECT COUNT(*) FROM signal_predictions")
        total = cur.fetchone()[0]
        print(f"  Total signal predictions: {total:,}")
        if total > 0:
            cur.execute("SELECT MIN(timestamp), MAX(timestamp) FROM signal_predictions")
            min_ts, max_ts = cur.fetchone()
            print(f"  Date range: {min_ts} to {max_ts}")
            cur.execute("SELECT predicted_action, COUNT(*) FROM signal_predictions GROUP BY predicted_action ORDER BY COUNT(*) DESC LIMIT 10")
            print(f"  By predicted action:")
            for action, cnt in cur.fetchall():
                print(f"    {action}: {cnt:,}")
    
    # AI attribution
    if "ai_attribution" in tables:
        subsection(f"{db_name} — ai_attribution")
        cur.execute("SELECT COUNT(*) FROM ai_attribution")
        total = cur.fetchone()[0]
        print(f"  Total AI attributions: {total:,}")
        if total > 0:
            try:
                cur.execute("SELECT ai_system, COUNT(*) FROM ai_attribution GROUP BY ai_system ORDER BY COUNT(*) DESC LIMIT 10")
                print(f"  Top AI systems:")
                for sys_name, cnt in cur.fetchall():
                    print(f"    {sys_name}: {cnt:,}")
            except Exception:
                pass
    
    # Learning outcomes
    if "learning_outcomes" in tables:
        subsection(f"{db_name} — learning_outcomes")
        cur.execute("SELECT COUNT(*) FROM learning_outcomes")
        total = cur.fetchone()[0]
        print(f"  Total learning outcomes: {total:,}")
    
    conn.close()

# ============================================================================
# 2. SHADOW TRADING
# ============================================================================
section("2. SHADOW TRADING PERFORMANCE")

for db_name in ["prometheus_learning.db", "multi_strategy_shadow.db", "shadow_trading_results.db"]:
    db_path = BASE / db_name
    if not db_path.exists():
        continue
    conn = sqlite3.connect(str(db_path), timeout=10)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%shadow%'")
    shadow_tables = [r[0] for r in cur.fetchall()]
    
    if shadow_tables:
        print(f"\n  {db_name} shadow tables: {shadow_tables}")
        for tbl in shadow_tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tbl}")
                cnt = cur.fetchone()[0]
                if cnt > 0:
                    print(f"\n    {tbl}: {cnt} records")
                    # Try to get columns
                    cur.execute(f"PRAGMA table_info({tbl})")
                    cols = [r[1] for r in cur.fetchall()]
                    print(f"    Columns: {', '.join(cols[:10])}")
                    
                    if 'profit_loss' in cols:
                        cur.execute(f"SELECT COUNT(*), SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END), COALESCE(SUM(profit_loss), 0) FROM {tbl}")
                        total, wins, pnl = cur.fetchone()
                        wr = round((wins or 0)/total*100,1) if total > 0 else 0
                        print(f"    Trades: {total}, Wins: {wins}, WinRate: {wr}%, P/L: ${pnl:.2f}")
                    
                    if 'timestamp' in cols:
                        cur.execute(f"SELECT MIN(timestamp), MAX(timestamp) FROM {tbl}")
                        mn, mx = cur.fetchone()
                        print(f"    Date range: {mn} to {mx}")
                    
                    # Last 5 shadow trades
                    cur.execute(f"SELECT * FROM {tbl} ORDER BY rowid DESC LIMIT 5")
                    rows = cur.fetchall()
                    if rows:
                        print(f"    Last 5 entries:")
                        for row in rows:
                            print(f"      {row[:8]}...")
            except Exception as e:
                print(f"    {tbl}: ERROR - {e}")
    conn.close()

# ============================================================================
# 3. CONFIGURATION FILES
# ============================================================================
section("3. CONFIGURATION & FINE-TUNING FILES")

config_files = [
    "advanced_paper_trading_config.json",
    "advanced_paper_trading_config_optimized.json",
    "advanced_features_config.json",
    "ai_signal_weights_config.json",
    "ai_consciousness_config.json",
    "aggressive_trading_params.json",
    "prometheus_config.json",
    "production_config.json",
    "trading_config.json",
    "strategy_config.json",
]

for cf in config_files:
    fp = BASE / cf
    if fp.exists():
        try:
            data = json.load(open(fp))
            size = fp.stat().st_size
            print(f"\n  {cf} ({size:,} bytes)")
            # Show top-level keys
            if isinstance(data, dict):
                print(f"    Keys: {list(data.keys())[:10]}")
                # Show interesting values
                for key in ['win_rate', 'sharpe', 'cagr', 'confidence_threshold', 'min_confidence',
                            'stop_loss', 'take_profit', 'max_position_size', 'risk_per_trade',
                            'mode', 'live_trading', 'paper_trading', 'enable_live']:
                    if key in data:
                        print(f"    {key}: {data[key]}")
                # Check nested
                for top_key in data:
                    if isinstance(data[top_key], dict):
                        for sub_key in ['confidence_threshold', 'stop_loss', 'take_profit', 'min_confidence', 
                                        'risk_per_trade', 'max_drawdown', 'position_size']:
                            if sub_key in data[top_key]:
                                print(f"    {top_key}.{sub_key}: {data[top_key][sub_key]}")
        except Exception as e:
            print(f"  {cf}: ERROR reading - {e}")

# Check .env
subsection(".env Configuration")
env_path = BASE / ".env"
if env_path.exists():
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    important_keys = [
        'ENABLE_LIVE_ORDER_EXECUTION', 'ALWAYS_LIVE', 'PAPER_TRADING',
        'ALPACA_API_KEY', 'ALPACA_SECRET_KEY', 'ALPACA_PAPER_API_KEY', 'ALPACA_PAPER_SECRET_KEY',
        'ALPACA_BASE_URL', 'IB_HOST', 'IB_PORT', 'IB_ACCOUNT',
        'CONFIDENCE_THRESHOLD', 'MIN_CONFIDENCE', 'STOP_LOSS', 'RISK_PER_TRADE',
        'MAX_POSITION_SIZE', 'TRADING_MODE', 'OPENAI_API_KEY', 'POLYGON_API_KEY',
        'FRED_API_KEY', 'NEWS_API_KEY',
    ]
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key = line.split('=', 1)[0].strip()
            val = line.split('=', 1)[1].strip()
            # Mask sensitive values
            if any(s in key.upper() for s in ['KEY', 'SECRET', 'PASSWORD', 'TOKEN']):
                display_val = val[:8] + '...' + val[-4:] if len(val) > 15 else ('SET' if val else 'EMPTY')
            else:
                display_val = val
            if any(ik.upper() in key.upper() for ik in important_keys) or key in important_keys:
                print(f"    {key} = {display_val}")

# ============================================================================
# 4. AI & SIGNAL PIPELINE
# ============================================================================
section("4. AI SYSTEMS & SIGNAL PIPELINE")

# Check what AI modules exist
subsection("Core AI Modules")
core_dir = BASE / "core"
if core_dir.exists():
    ai_modules = sorted([f.name for f in core_dir.iterdir() if f.suffix == '.py' and 
                         any(k in f.name for k in ['ai', 'learn', 'signal', 'predict', 'intel', 'reason', 'think', 'gpt', 'rl', 'regime'])])
    print(f"  AI-related modules in core/: {len(ai_modules)}")
    for m in ai_modules:
        size = (core_dir / m).stat().st_size
        print(f"    {m} ({size:,} bytes)")

# Check learning data
subsection("Learning Data Files")
learning_files = list(BASE.glob("*learning*")) + list(BASE.glob("*pattern*")) + list(BASE.glob("*expert*"))
for f in sorted(learning_files)[:20]:
    if f.is_file():
        size = f.stat().st_size
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"    {f.name} ({size:,} bytes, modified {mtime})")

# Check trained models
subsection("Trained Models & Weights")
model_dirs = ["models", "trained_models", "weights", "checkpoints"]
for md in model_dirs:
    mp = BASE / md
    if mp.exists():
        files = list(mp.rglob("*"))
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        print(f"  {md}/: {len(files)} files, {total_size/(1024*1024):.1f} MB")
        for f in sorted(files)[:10]:
            if f.is_file():
                print(f"    {f.relative_to(mp)} ({f.stat().st_size:,} bytes)")

# RL system
subsection("Reinforcement Learning State")
rl_files = list(BASE.glob("*rl_*")) + list(BASE.glob("*reinforcement*")) + list(BASE.rglob("core/*rl*"))
for f in sorted(set(rl_files))[:15]:
    if f.is_file():
        size = f.stat().st_size
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"    {f.name} ({size:,} bytes, modified {mtime})")

# ============================================================================
# 5. BROKER CONNECTIONS
# ============================================================================
section("5. BROKER CONNECTIONS & ACCOUNT STATUS")

# Alpaca
subsection("Alpaca LIVE")
try:
    sys.path.insert(0, str(BASE))
    from dotenv import load_dotenv
    load_dotenv(str(BASE / ".env"))
    
    from core.alpaca_trading_service import AlpacaTradingService
    svc = AlpacaTradingService(use_paper_trading=False)
    info = svc.get_account_info()
    if info and "error" not in info:
        print(f"  Connected: YES")
        print(f"  Account Value: ${float(info.get('portfolio_value', 0)):.2f}")
        print(f"  Cash: ${float(info.get('cash', 0)):.2f}")
        print(f"  Buying Power: ${float(info.get('buying_power', 0)):.2f}")
        print(f"  Day Trade Count: {info.get('daytrade_count', 'n/a')}")
        print(f"  Trading Blocked: {info.get('trading_blocked', 'n/a')}")
        print(f"  Account Blocked: {info.get('account_blocked', 'n/a')}")
        
        # Positions
        try:
            positions = svc.get_positions()
            if positions:
                print(f"\n  Positions ({len(positions)}):")
                total_mv = 0
                total_upl = 0
                for p in positions:
                    if isinstance(p, dict):
                        sym, qty, mv, upl, cp = p.get('symbol',''), float(p.get('qty',0)), float(p.get('market_value',0)), float(p.get('unrealized_pl',0)), float(p.get('current_price',0))
                    else:
                        sym, qty, mv, upl, cp = p.symbol, float(p.qty), float(p.market_value), float(p.unrealized_pl), float(p.current_price)
                    total_mv += mv
                    total_upl += upl
                    pct = float(p.unrealized_plpc if not isinstance(p, dict) else p.get('unrealized_plpc', 0)) * 100
                    print(f"    {sym:<12} qty={qty:>10.4f}  mv=${mv:>10.2f}  upl=${upl:>8.2f} ({pct:>+6.2f}%)  price=${cp:.2f}")
                print(f"    {'TOTAL':<12} {'':>10}  mv=${total_mv:>10.2f}  upl=${total_upl:>8.2f}")
        except Exception as e:
            print(f"  Positions: ERROR - {e}")
        
        # Recent orders
        try:
            if hasattr(svc, 'api'):
                orders = svc.api.list_orders(status='all', limit=15)
                if orders:
                    print(f"\n  Recent Orders ({len(orders)}):")
                    for o in orders[:15]:
                        print(f"    {o.submitted_at[:19]} {o.side:<4} {o.symbol:<8} qty={o.qty} type={o.type} status={o.status} filled_avg={getattr(o, 'filled_avg_price', 'n/a')}")
        except Exception as e:
            print(f"  Orders: ERROR - {e}")
    else:
        print(f"  Connected: NO")
        print(f"  Error: {info}")
except Exception as e:
    print(f"  Alpaca LIVE: ERROR - {e}")

# Alpaca Paper
subsection("Alpaca PAPER")
try:
    psvc = AlpacaTradingService(use_paper_trading=True)
    pinfo = psvc.get_account_info()
    if pinfo and "error" not in pinfo:
        print(f"  Connected: YES")
        print(f"  Account Value: ${float(pinfo.get('portfolio_value', 0)):.2f}")
        print(f"  Cash: ${float(pinfo.get('cash', 0)):.2f}")
    else:
        print(f"  Connected: NO")
        print(f"  Error: {pinfo}")
except Exception as e:
    print(f"  Alpaca PAPER: ERROR - {e}")

# IB
subsection("Interactive Brokers")
try:
    ib_host = os.getenv("IB_HOST", "127.0.0.1")
    ib_port = int(os.getenv("IB_PORT", "4002"))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    reachable = sock.connect_ex((ib_host, ib_port)) == 0
    sock.close()
    print(f"  Host: {ib_host}:{ib_port}")
    print(f"  Port Reachable: {reachable}")
    print(f"  Account: {os.getenv('IB_ACCOUNT', 'not set')}")
except Exception as e:
    print(f"  IB: ERROR - {e}")

# ============================================================================
# 6. SERVER & TRADING ENGINE STATE
# ============================================================================
section("6. SERVER & TRADING ENGINE")

subsection("Server File Stats")
server_file = BASE / "unified_production_server.py"
if server_file.exists():
    size = server_file.stat().st_size
    with open(server_file, 'r', encoding='utf-8', errors='replace') as f:
        lines = sum(1 for _ in f)
    print(f"  unified_production_server.py: {size:,} bytes, {lines:,} lines")

subsection("Server Process")
try:
    import urllib.request
    req = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
    health = json.loads(req.read())
    print(f"  Server: RUNNING (HTTP 200)")
    print(f"  Health: {json.dumps(health, indent=4)[:500]}")
except Exception as e:
    print(f"  Server: NOT RUNNING or unreachable - {e}")

subsection("Admin Dashboard Status")
try:
    req = urllib.request.urlopen("http://localhost:8000/api/admin/full-status", timeout=15)
    data = json.loads(req.read())
    print(f"  Admin API: HTTP 200")
    print(f"  Uptime: {data.get('uptime_seconds', 0):.0f}s")
    print(f"  Live Execution: {data.get('live_execution_enabled')}")
    print(f"  Always Live: {data.get('always_live_mode')}")
    
    at = data.get('autonomous_trading', {})
    print(f"\n  Autonomous Trading:")
    print(f"    Active threads: {at.get('threads', 0)}")
    print(f"    Thread names: {at.get('thread_names', [])}")
    print(f"    Live execution: {at.get('live_execution')}")
    
    ai = data.get('ai_learning', {})
    print(f"\n  AI Learning:")
    print(f"    Total threads: {ai.get('total_threads', 0)}")
    print(f"    Systems: {ai.get('systems', [])}")
except Exception as e:
    print(f"  Admin API: ERROR - {e}")

# ============================================================================
# 7. BENCHMARK RESULTS HISTORY
# ============================================================================
section("7. BENCHMARK RESULTS HISTORY")

bench_files = sorted(BASE.glob("benchmark_results_*.json"), reverse=True)[:5]
bench_files += sorted(BASE.glob("MASTER_BENCHMARK_RESULTS_*.json"), reverse=True)[:3]
bench_files += sorted(BASE.glob("backtest_results_*.json"), reverse=True)[:5]

for bf in bench_files:
    try:
        data = json.load(open(bf))
        mtime = datetime.fromtimestamp(bf.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"\n  {bf.name} (modified {mtime})")
        
        if isinstance(data, dict):
            # Master results
            if 'pass_rate' in data:
                print(f"    Pass Rate: {data['pass_rate']}%, Passed: {data.get('passed')}/{data.get('total_scripts')}")
            # Benchmark results
            if 'score_percent' in data:
                print(f"    Score: {data['score_percent']}%")
            if 'grade' in data:
                print(f"    Grade: {data['grade']}")
            if 'total_return' in data:
                print(f"    Total Return: {data['total_return']}")
            if 'sharpe_ratio' in data:
                print(f"    Sharpe: {data['sharpe_ratio']}")
            if 'max_drawdown' in data:
                print(f"    Max Drawdown: {data['max_drawdown']}")
            if 'win_rate' in data:
                print(f"    Win Rate: {data['win_rate']}")
            if 'cagr' in data:
                print(f"    CAGR: {data['cagr']}")
            # Show a few keys
            keys = list(data.keys())[:8]
            print(f"    Keys: {keys}")
    except Exception as e:
        print(f"  {bf.name}: ERROR - {e}")

# ============================================================================
# 8. FINE-TUNING & ADJUSTMENTS AUDIT
# ============================================================================
section("8. FINE-TUNING & ADJUSTMENTS HISTORY")

subsection("Strategy Optimization Files")
opt_files = sorted(BASE.glob("*optim*")) + sorted(BASE.glob("*tuning*")) + sorted(BASE.glob("*adjust*"))
for f in sorted(set(opt_files))[:15]:
    if f.is_file():
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"    {f.name} ({f.stat().st_size:,} bytes, {mtime})")

subsection("Key Trading Parameters in Server")
# Read critical sections of the server
try:
    with open(server_file, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    # Find confidence thresholds
    import re
    patterns = {
        'confidence_threshold': r'confidence[_\s]*threshold["\s]*[:=]\s*([0-9.]+)',
        'stop_loss': r'stop[_\s]*loss["\s]*[:=]\s*([0-9.]+)',
        'take_profit': r'take[_\s]*profit["\s]*[:=]\s*([0-9.]+)',
        'min_confidence': r'min[_\s]*confidence["\s]*[:=]\s*([0-9.]+)',
        'risk_per_trade': r'risk[_\s]*per[_\s]*trade["\s]*[:=]\s*([0-9.]+)',
        'max_position_size': r'max[_\s]*position[_\s]*size["\s]*[:=]\s*([0-9.]+)',
        'position_size_pct': r'position[_\s]*size[_\s]*pct["\s]*[:=]\s*([0-9.]+)',
    }
    
    for name, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            unique = sorted(set(matches))
            print(f"    {name}: {unique}")
except Exception as e:
    print(f"    Error scanning server: {e}")

# ============================================================================
# 9. WALK-FORWARD & VALIDATION
# ============================================================================
section("9. WALK-FORWARD & VALIDATION RESULTS")

wf_files = sorted(BASE.glob("*walk*forward*")) + sorted(BASE.glob("*monte*carlo*")) + sorted(BASE.glob("*validation*"))
for f in sorted(set(wf_files))[:10]:
    if f.is_file() and f.suffix == '.json':
        try:
            data = json.load(open(f))
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"\n  {f.name} ({mtime})")
            if isinstance(data, dict):
                for k in ['overall_assessment', 'total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate', 'pass_rate', 'confidence_level', 'mean_return', 'var_95']:
                    if k in data:
                        print(f"    {k}: {data[k]}")
        except Exception:
            pass
    elif f.is_file():
        mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"  {f.name} ({f.stat().st_size:,} bytes, {mtime})")

# ============================================================================
# 10. SYSTEM RESOURCES
# ============================================================================
section("10. SYSTEM RESOURCES")
try:
    import psutil
    print(f"  CPU: {psutil.cpu_count()} cores, {psutil.cpu_percent(interval=0.5)}% usage")
    mem = psutil.virtual_memory()
    print(f"  RAM: {mem.total/(1024**3):.1f} GB total, {mem.used/(1024**3):.1f} GB used ({mem.percent}%)")
    disk = psutil.disk_usage('C:\\')
    print(f"  Disk: {disk.total/(1024**3):.0f} GB total, {disk.free/(1024**3):.0f} GB free ({disk.percent}% used)")
    
    # Python processes
    py_procs = [p for p in psutil.process_iter(['name', 'pid', 'memory_info', 'cpu_percent', 'cmdline']) if 'python' in (p.info['name'] or '').lower()]
    print(f"\n  Python processes: {len(py_procs)}")
    for p in py_procs:
        mem_mb = p.info['memory_info'].rss / (1024*1024) if p.info['memory_info'] else 0
        cmd = ' '.join(p.info['cmdline'][:3]) if p.info['cmdline'] else 'n/a'
        print(f"    PID {p.info['pid']}: {mem_mb:.0f} MB RAM, cmd={cmd[:80]}")
except Exception as e:
    print(f"  psutil: {e}")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
section("FULL AUDIT SUMMARY")
print("""
  This audit shows the ACTUAL state of PROMETHEUS as of right now.
  Review each section above for the ground truth.
  No synthetic numbers — only what the databases, configs, and APIs report.
""")

print(f"  Audit completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
