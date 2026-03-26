"""Comprehensive Prometheus live system status check."""
import requests, json, sqlite3, os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

W = 70

def section(title):
    print(f"\n{'='*W}")
    print(f"  {title}")
    print(f"{'='*W}")

section("PROMETHEUS LIVE SYSTEM STATUS CHECK - " + datetime.now().strftime("%Y-%m-%d %H:%M"))

# ── 1. Server Health ──────────────────────────────────────────────────────────
section("1. SERVER HEALTH")
server_up = False
try:
    r = requests.get("http://localhost:8000/health", timeout=5)
    h = r.json()
    server_up = True
    uptime = h.get("uptime_seconds", 0)
    hrs = uptime / 3600
    print(f"  Status       : {h.get('status', '?')}")
    print(f"  Uptime       : {uptime:.0f}s ({hrs:.1f}h)")
    print(f"  AI Systems   : {h.get('ai_systems_count', '?')}")
    print(f"  Version      : {h.get('version', 'n/a')}")
except Exception as e:
    print(f"  SERVER DOWN: {e}")

# ── 2. Environment Config ────────────────────────────────────────────────────
section("2. ENVIRONMENT CONFIG")
live_enabled = os.getenv("LIVE_TRADING_ENABLED", "false")
paper_mode = os.getenv("ALPACA_PAPER_TRADING", "true")
ib_enabled = os.getenv("IB_LIVE_ENABLED", "false")
ib_port = os.getenv("IB_PORT", "7497")
ib_account = os.getenv("IB_ACCOUNT", "n/a")
alpaca_key = os.getenv("ALPACA_API_KEY", "")[:10] + "..."
alpaca_base = os.getenv("ALPACA_BASE_URL", "n/a")
openai_key = "set" if os.getenv("OPENAI_API_KEY") else "MISSING"
polygon_key = "set" if os.getenv("POLYGON_API_KEY") else "MISSING"

print(f"  LIVE_TRADING_ENABLED : {live_enabled}")
print(f"  ALPACA_PAPER_TRADING : {paper_mode}")
print(f"  IB_LIVE_ENABLED      : {ib_enabled}")
print(f"  IB_PORT              : {ib_port}")
print(f"  IB_ACCOUNT           : {ib_account}")
print(f"  ALPACA_API_KEY       : {alpaca_key}")
print(f"  ALPACA_BASE_URL      : {alpaca_base}")
print(f"  OPENAI_API_KEY       : {openai_key}")
print(f"  POLYGON_API_KEY      : {polygon_key}")

is_live = live_enabled.lower() in ("true", "1", "yes")
is_paper = paper_mode.lower() in ("true", "1", "yes")
is_ib = ib_enabled.lower() in ("true", "1", "yes")
print(f"\n  => Mode: {'LIVE' if is_live and not is_paper else 'PAPER'} trading")
print(f"  => IB:   {'enabled' if is_ib else 'disabled'}")

# ── 3. Live Trading API Status ───────────────────────────────────────────────
section("3. LIVE TRADING STATUS (API)")
if server_up:
    try:
        r = requests.get("http://localhost:8000/api/live-trading/status", timeout=5)
        lt = r.json()
        print(f"  Active           : {lt.get('active')}")
        print(f"  Enabled globally : {lt.get('enabled_globally')}")
        for k, v in lt.items():
            if k not in ("active", "enabled_globally") and not isinstance(v, (dict, list)):
                print(f"  {k:<18}: {v}")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("  (server down)")

# ── 4. AI Systems Status ─────────────────────────────────────────────────────
section("4. AI SYSTEMS STATUS")
if server_up:
    try:
        r = requests.get("http://localhost:8000/api/ai-systems/status", timeout=10)
        data = r.json()
        systems = []
        if isinstance(data, dict):
            systems = data.get("systems", data.get("ai_systems", []))
            if not isinstance(systems, list):
                systems = []
        elif isinstance(data, list):
            systems = data

        active_count = 0
        inactive_count = 0
        for s in systems:
            name = s.get("name", s.get("system", "?"))
            status = s.get("status", "active" if s.get("active") else "inactive")
            is_active = status.lower() in ("active", "running", "true") or s.get("active") is True
            if is_active:
                active_count += 1
                marker = "OK"
            else:
                inactive_count += 1
                marker = "XX"
            print(f"  [{marker}] {name:<40} {status}")

        if not systems:
            print(f"  (raw response): {json.dumps(data)[:400]}")

        print(f"\n  TOTAL: {active_count} active / {inactive_count} inactive / {len(systems)} total")
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("  (server down)")

# ── 5. Alpaca Broker ─────────────────────────────────────────────────────────
section("5. ALPACA BROKER")
try:
    import alpaca_trade_api as tradeapi
    api_key = os.getenv("ALPACA_API_KEY", "")
    secret = os.getenv("ALPACA_SECRET_KEY", "")
    base = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
    api = tradeapi.REST(api_key, secret, base)
    acct = api.get_account()
    print(f"  Account ID     : {acct.account_number}")
    print(f"  Status         : {acct.status}")
    print(f"  Cash           : ${float(acct.cash):.2f}")
    print(f"  Portfolio Value: ${float(acct.portfolio_value):.2f}")
    print(f"  Buying Power   : ${float(acct.buying_power):.2f}")
    print(f"  Day Trades     : {acct.daytrade_count}")

    positions = api.list_positions()
    print(f"  Open Positions : {len(positions)}")
    total_unrealized = 0.0
    for p in positions:
        upl = float(p.unrealized_pl)
        total_unrealized += upl
        print(f"    {p.symbol:<10} qty={p.qty:<10} entry=${float(p.avg_entry_price):.4f}  upl=${upl:+.4f}")
    print(f"  Total Unrealized PnL: ${total_unrealized:+.4f}")

    orders = api.list_orders(status="open")
    print(f"  Open Orders    : {len(orders)}")

    recent = api.list_orders(status="all", limit=5)
    if recent:
        print(f"  Last 5 orders:")
        for o in recent:
            print(f"    {o.symbol:<8} {o.side:<4} {o.status:<12} {str(o.created_at)[:19]}")
except Exception as e:
    print(f"  Alpaca Error: {e}")

# ── 6. IB Gateway ────────────────────────────────────────────────────────────
section("6. INTERACTIVE BROKERS")
if is_ib:
    try:
        from ibapi.client import EClient
        from ibapi.wrapper import EWrapper
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(("127.0.0.1", int(ib_port)))
        sock.close()
        if result == 0:
            print(f"  IB Gateway port {ib_port}: CONNECTED")
            print(f"  Account: {ib_account}")
        else:
            print(f"  IB Gateway port {ib_port}: NOT REACHABLE (code {result})")
    except Exception as e:
        print(f"  IB Check Error: {e}")
else:
    print(f"  IB_LIVE_ENABLED=false - IB broker DISABLED")

# ── 7. Shadow Trading Process ────────────────────────────────────────────────
section("7. SHADOW TRADING")
import subprocess
try:
    result = subprocess.run(
        ["powershell", "-c", "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, StartTime"],
        capture_output=True, text=True, timeout=5
    )
    python_procs = result.stdout.strip()
    print(f"  Python processes:\n{python_procs}")
except:
    pass

try:
    db = sqlite3.connect("prometheus_learning.db", timeout=5)
    db.row_factory = sqlite3.Row
    r = db.execute("SELECT COUNT(*) as n FROM shadow_sessions WHERE status IN ('ACTIVE','COMPLETED')").fetchone()
    print(f"  Shadow sessions (active+completed): {r['n']}")
    r = db.execute("SELECT COUNT(*) as n FROM shadow_trade_history").fetchone()
    print(f"  Shadow trades total: {r['n']}")
    r = db.execute("SELECT MAX(timestamp) as last FROM shadow_trade_history").fetchone()
    print(f"  Last shadow trade: {r['last']}")
    r = db.execute("SELECT COUNT(*) as n FROM signal_predictions").fetchone()
    print(f"  Signal predictions: {r['n']:,}")
    r = db.execute("SELECT MAX(timestamp) as last FROM signal_predictions").fetchone()
    print(f"  Last signal: {r['last']}")
    db.close()
except Exception as e:
    print(f"  DB Error: {e}")

# ── 8. Learning & AI Metrics ─────────────────────────────────────────────────
section("8. LEARNING & AI METRICS")
try:
    db = sqlite3.connect("prometheus_learning.db", timeout=5)
    db.row_factory = sqlite3.Row
    r = db.execute("SELECT COUNT(*) as n, SUM(was_correct) as correct FROM learning_outcomes").fetchone()
    total = r['n']
    correct = r['correct'] or 0
    print(f"  Learning outcomes   : {total}")
    print(f"  Prediction accuracy : {correct}/{total} ({correct/total*100:.1f}%)" if total else "  No outcomes yet")

    r = db.execute("SELECT COUNT(*) as n FROM ai_attribution WHERE outcome_recorded=1").fetchone()
    total_attr = db.execute("SELECT COUNT(*) as n FROM ai_attribution").fetchone()['n']
    print(f"  AI attribution      : {r['n']}/{total_attr} with outcomes ({r['n']/total_attr*100:.1f}%)" if total_attr else "  No attributions")

    r = db.execute("SELECT COUNT(*) as n FROM ai_system_metrics").fetchone()
    print(f"  AI system metrics   : {r['n']} rows")

    r = db.execute("SELECT COUNT(*) as n FROM learning_insights").fetchone()
    print(f"  Learning insights   : {r['n']} rows")

    r = db.execute("SELECT COUNT(*) as n FROM trade_history").fetchone()
    total_trades = r['n']
    r = db.execute("SELECT COUNT(*) as n FROM trade_history WHERE profit_loss IS NOT NULL AND profit_loss != 0").fetchone()
    closed = r['n']
    print(f"  Trade history       : {total_trades} total, {closed} with P/L")

    r = db.execute("SELECT COUNT(*) as n FROM performance_metrics").fetchone()
    print(f"  Performance metrics : {r['n']} snapshots")

    db.close()
except Exception as e:
    print(f"  DB Error: {e}")

# ── 9. Benchmark Results ─────────────────────────────────────────────────────
section("9. BENCHMARK STATUS")
try:
    import glob
    results = sorted(glob.glob("full_test_results_*.json"), reverse=True)
    if results:
        latest = results[0]
        with open(latest) as f:
            data = json.load(f)
        passed = data.get("passed", 0)
        failed = data.get("failed", 0)
        total = data.get("total", passed + failed)
        print(f"  Latest: {latest}")
        print(f"  Result: {passed}/{total} passed ({passed/total*100:.0f}%)")
        print(f"  Time  : {data.get('duration_seconds', '?')}s")
    else:
        print("  No benchmark results found")
except Exception as e:
    print(f"  Error: {e}")

# ── 10. Critical File Checks ─────────────────────────────────────────────────
section("10. CRITICAL FILES & MODELS")
model_dir = Path("models/direction")
if model_dir.exists():
    models = list(model_dir.glob("*.joblib"))
    print(f"  Direction models: {len(models)}")
    for m in sorted(models):
        size = m.stat().st_size
        mod_time = datetime.fromtimestamp(m.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        print(f"    {m.name:<30} {size:>8} bytes  {mod_time}")
else:
    print("  models/direction/ NOT FOUND")

# Check key config/env files
for f in [".env", "advanced_paper_trading_config.json", "ai_signal_weights_config.json"]:
    p = Path(f)
    if p.exists():
        print(f"  {f}: EXISTS ({p.stat().st_size} bytes)")
    else:
        print(f"  {f}: MISSING")

# ── SUMMARY ──────────────────────────────────────────────────────────────────
section("OVERALL VERDICT")
issues = []
if not server_up:
    issues.append("Server is DOWN")
if not is_live:
    issues.append("LIVE_TRADING_ENABLED is not true")
if is_paper:
    issues.append("ALPACA_PAPER_TRADING is true (paper mode)")
if openai_key == "MISSING":
    issues.append("OPENAI_API_KEY is missing")
if polygon_key == "MISSING":
    issues.append("POLYGON_API_KEY is missing")

if issues:
    print("  ISSUES FOUND:")
    for i in issues:
        print(f"    [!] {i}")
else:
    print("  ALL SYSTEMS GO - Prometheus is fully live")

print(f"\n{'='*W}")
