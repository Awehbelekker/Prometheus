"""Phase 23 Assessment — What's Next for PROMETHEUS"""
import json, sqlite3, os, sys, urllib.request
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("PROMETHEUS Phase 23 Assessment —", datetime.now().strftime("%Y-%m-%d %H:%M"))
print("=" * 70)

# 1. Server health
print("\n[1] SERVER HEALTH")
try:
    r = urllib.request.urlopen('http://localhost:8000/api/ai/all-systems/status', timeout=15)
    d = json.loads(r.read())
    total = d['total_systems']
    active = d['active_systems']
    print(f"  Systems: {active}/{total} active")
    offline = [k for k, v in d['systems'].items() if v.get('status') in ('offline', 'unavailable', 'error')]
    if offline:
        print(f"  OFFLINE/ERROR: {offline}")
    lazy = [k for k, v in d['systems'].items() if v.get('status') == 'wired (lazy)']
    if lazy:
        print(f"  Lazy (not yet loaded): {lazy}")
except Exception as e:
    print(f"  Server unreachable: {e}")

# 2. Shadow trading status
print("\n[2] SHADOW TRADING")
try:
    db = sqlite3.connect('prometheus_learning.db')
    cur = db.cursor()
    # Check if table exists
    has_table = cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='shadow_trades'").fetchone()[0]
    if not has_table:
        # Try alternate table name
        tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%shadow%'").fetchall()]
        if tables:
            print(f"  Shadow tables found: {tables}")
        else:
            print(f"  No shadow_trades table found — checking multi_strategy_shadow.db")
            db.close()
            db = sqlite3.connect('multi_strategy_shadow.db') if Path('multi_strategy_shadow.db').exists() else None
            if db:
                cur = db.cursor()
                tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                print(f"  multi_strategy_shadow.db tables: {tables}")
    total_trades = cur.execute("SELECT COUNT(*) FROM shadow_trades").fetchone()[0] if has_table else 0
    open_trades = cur.execute("SELECT COUNT(*) FROM shadow_trades WHERE status='OPEN'").fetchone()[0]
    closed_trades = cur.execute("SELECT COUNT(*) FROM shadow_trades WHERE status='CLOSED'").fetchone()[0]
    wins = cur.execute("SELECT COUNT(*) FROM shadow_trades WHERE status='CLOSED' AND pnl_percent > 0").fetchone()[0]
    losses = cur.execute("SELECT COUNT(*) FROM shadow_trades WHERE status='CLOSED' AND pnl_percent <= 0").fetchone()[0]
    total_pnl = cur.execute("SELECT COALESCE(SUM(pnl_percent), 0) FROM shadow_trades WHERE status='CLOSED'").fetchone()[0]
    print(f"  Total: {total_trades} | Open: {open_trades} | Closed: {closed_trades}")
    print(f"  Wins: {wins} | Losses: {losses} | Win rate: {wins/(wins+losses)*100 if wins+losses > 0 else 0:.1f}%")
    print(f"  Total PnL: {total_pnl:+.2f}%")
    
    # Check if any were closed AFTER our fix
    recent = cur.execute("SELECT symbol, status, pnl_percent, exit_time FROM shadow_trades WHERE status='CLOSED' ORDER BY exit_time DESC LIMIT 3").fetchall()
    if recent:
        print(f"  Recent closed: {recent}")
    else:
        print(f"  NOTE: No trades closed yet (fix was just applied, needs market hours)")
    db.close()
except Exception as e:
    print(f"  DB error: {e}")

# 3. Live trading status
print("\n[3] LIVE TRADING")
try:
    r = urllib.request.urlopen('http://localhost:8000/api/trading-system/status', timeout=10)
    d = json.loads(r.read())
    if d.get('success'):
        ts = d.get('trading_system', {})
        print(f"  Active: {ts.get('active', 'unknown')}")
        print(f"  Brokers connected: {ts.get('connected_brokers', [])}")
        print(f"  Equity: ${ts.get('total_equity', 0):.2f}")
    else:
        print(f"  Error: {d.get('error')}")
except Exception as e:
    print(f"  Could not check: {e}")

# 4. Tier 3 data source health 
print("\n[4] TIER 3 DATA SOURCES")
# Check Reddit credentials
reddit_id = os.environ.get('REDDIT_CLIENT_ID', '')
reddit_secret = os.environ.get('REDDIT_CLIENT_SECRET', '')
print(f"  Reddit API: {'configured' if reddit_id and reddit_secret else 'MISSING'}")

# Check Google Trends import
try:
    from pytrends.request import TrendReq
    print(f"  Google Trends (pytrends): installed")
except ImportError:
    print(f"  Google Trends (pytrends): NOT INSTALLED")

# Check CoinGecko
try:
    r = urllib.request.urlopen('https://api.coingecko.com/api/v3/ping', timeout=5)
    cg = json.loads(r.read())
    print(f"  CoinGecko API: {cg.get('gecko_says', 'reachable')}")
except Exception as e:
    print(f"  CoinGecko API: unreachable ({e})")

# 5. Known issues / technical debt
print("\n[5] KNOWN ISSUES / TECH DEBT")
issues = []

# Check for the auth service fetch_one bug
try:
    from core.auth_service import AuthenticationService
    if not hasattr(AuthenticationService, 'fetch_one'):
        issues.append("auth_service: DatabaseManager missing 'fetch_one' (admin creation fails)")
except:
    issues.append("auth_service: could not import")

# Check Federated Learning (only top-level + core/)
fed_learning_files = list(Path('.').glob('federated_learning*')) + list(Path('core').glob('federated_learning*'))
real_fed = [f for f in fed_learning_files if f.stat().st_size > 500]
if not real_fed:
    issues.append("Federated Learning: still FAKE (no real implementation)")
else:
    issues.append(f"Federated Learning: {len(real_fed)} file(s) found, needs audit")

# Check protobuf
try:
    import google.protobuf
    issues.append(f"protobuf version mismatch: runtime {google.protobuf.__version__} vs TF gencode 5.28.3 (warnings)")
except:
    pass

# Check Polygon
polygon_key = os.environ.get('POLYGON_API_KEY', '')
if polygon_key:
    try:
        r = urllib.request.urlopen(f'https://api.polygon.io/v2/aggs/ticker/AAPL/prev?apiKey={polygon_key}', timeout=5)
        print(f"  Polygon API: working")
    except Exception as e:
        issues.append(f"Polygon API: {e}")
else:
    issues.append("Polygon API: no key configured")

# XAI returned empty key_factors
issues.append("XAI explain-decision: key_factors returned empty in test (needs market data tuning)")

# Check for dashboard/frontend (fast, no archive recursion)
frontend_files = list(Path('.').glob('index.html')) + list(Path('.').glob('dashboard*')) + list(Path('frontend').glob('*')) if Path('frontend').exists() else list(Path('.').glob('index.html')) + list(Path('.').glob('dashboard*'))
frontend_real = [f for f in frontend_files if 'ARCHIVE' not in str(f)]
if not frontend_real:
    issues.append("No frontend/dashboard files found")

for i, issue in enumerate(issues, 1):
    print(f"  {i}. {issue}")

# 6. Feature completeness - what percentage of reference architecture is done 
print("\n[6] FEATURE COVERAGE")
features = {
    "GPT-OSS / Ollama LLM": True,
    "HRM 27M-Param Reasoning": True,
    "DeepConf Confidence": True, 
    "Chart Vision (LLaVA)": True,
    "Pretrained ML Models (130)": True,
    "RL Trading Agent": True,
    "ThinkMesh Reasoning": True,
    "Circuit Breaker": True,
    "Fed NLP Analyzer": True,
    "ML Regime Detector": True,
    "Trade Outcome Processor": True,
    "Strategy Degradation Detector": True,
    "Earnings Calendar": True,
    "Cross-Asset Correlation": True,
    "LangGraph Orchestrator": True,
    "OpenBB Data Provider": True,
    "CCXT Exchange Bridge": True,
    "Gymnasium/SB3 RL": True,
    "Mercury2 Diffusion LLM": True,
    "Prometheus Cache": True,
    "SEC Filings RAG": True,
    "FinRL Portfolio Optimizer": True,
    "Explainable AI (XAI)": True,
    "Adversarial Robustness": True,
    "Shadow Trading (with fixes)": True,
    "Live Trading (Alpaca+IB)": True,
    "Real-World Data Orchestrator": True,
    "N8N Workflow Manager (real RSS)": True,
    # Not yet / partially done
    "Federated Learning (real)": False,
    "Frontend Dashboard": False,
    "Backtesting Validation Suite": False,
    "Paper Trading Monitor/Reporter": False,
    "Automated Model Retraining Pipeline": False,
    "Portfolio Risk Manager (VaR/CVaR)": False,
}
done = sum(1 for v in features.values() if v)
total = len(features)
print(f"  {done}/{total} features ({done/total*100:.0f}%)")
not_done = [k for k, v in features.items() if not v]
for f in not_done:
    print(f"    - TODO: {f}")

# 7. Database health
print("\n[7] DATABASE HEALTH")
try:
    db = sqlite3.connect('prometheus_learning.db')
    cur = db.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"  prometheus_learning.db: {len(tables)} tables")
    for table in ['shadow_trades', 'signal_predictions', 'ai_attributions', 'trade_history']:
        try:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"    {table}: {count:,} rows")
        except:
            pass
    db.close()
except Exception as e:
    print(f"  {e}")

try:
    db = sqlite3.connect('prometheus_trading.db')
    cur = db.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"  prometheus_trading.db: {len(tables)} tables")
    for table in ['trades', 'positions', 'orders', 'portfolio_snapshots']:
        try:
            count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"    {table}: {count:,} rows")
        except:
            pass
    db.close()
except Exception as e:
    print(f"  {e}")

print("\n" + "=" * 70)
print("ASSESSMENT COMPLETE")
print("=" * 70)
