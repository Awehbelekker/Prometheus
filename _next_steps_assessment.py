"""Quick assessment of PROMETHEUS current state to identify next steps."""
import glob, sqlite3, json, os, sys

print("=" * 60)
print("PROMETHEUS NEXT STEPS ASSESSMENT")
print("=" * 60)

# 1. Model files
print("\n--- MODEL FILES ---")
root_pkl = glob.glob("*.pkl")
trained_pkl = glob.glob("trained_models/*.pkl")
trained_pt = glob.glob("trained_models/*.pt")
all_pt = glob.glob("**/*.pt", recursive=True)
print(f"Root .pkl files: {len(root_pkl)}")
if root_pkl:
    for f in root_pkl[:10]:
        print(f"  {f}")
    if len(root_pkl) > 10:
        print(f"  ... and {len(root_pkl)-10} more")
print(f"trained_models/ .pkl files: {len(trained_pkl)}")
for f in trained_pkl:
    print(f"  {f}")
print(f".pt files: {len(all_pt)}")
for f in all_pt:
    print(f"  {f}")

# 2. Database stats
print("\n--- DATABASE: prometheus_trading.db ---")
try:
    conn = sqlite3.connect("prometheus_trading.db")
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Tables: {len(tables)}")
    for t in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cur.fetchone()[0]
            if cnt > 0:
                print(f"  {t}: {cnt} rows")
        except:
            pass
    conn.close()
except Exception as e:
    print(f"Error: {e}")

print("\n--- DATABASE: prometheus_learning.db ---")
try:
    conn2 = sqlite3.connect("prometheus_learning.db")
    cur2 = conn2.cursor()
    cur2.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables2 = [r[0] for r in cur2.fetchall()]
    print(f"Tables: {len(tables2)}")
    for t in tables2:
        try:
            cur2.execute(f"SELECT COUNT(*) FROM [{t}]")
            cnt = cur2.fetchone()[0]
            if cnt > 0:
                print(f"  {t}: {cnt} rows")
        except:
            pass
    conn2.close()
except Exception as e:
    print(f"Error: {e}")

# 3. API checks
print("\n--- API ENDPOINTS ---")
try:
    import httpx
    c = httpx.Client(timeout=30)
    
    endpoints = [
        "/api/health",
        "/health",
        "/api/trading/status",
        "/api/ai/all-systems/status",
        "/api/ai/signal-weights",
        "/api/shadow-trading/status",
        "/api/positions",
        "/api/portfolio/summary",
    ]
    
    for ep in endpoints:
        try:
            r = c.get(f"http://localhost:8000{ep}")
            status = r.status_code
            if status == 200:
                d = r.json()
                # Summary based on endpoint
                if "all-systems" in ep:
                    print(f"  {ep}: {status} - Total:{d.get('total_systems')} Active:{d.get('active_systems')}")
                elif "shadow" in ep:
                    print(f"  {ep}: {status} - Running:{d.get('is_running', d.get('running', 'N/A'))}")
                elif "signal-weights" in ep:
                    weights = d.get('weights', d.get('signal_weights', []))
                    print(f"  {ep}: {status} - {len(weights)} weights")
                elif "positions" in ep:
                    pos = d if isinstance(d, list) else d.get('positions', [])
                    print(f"  {ep}: {status} - {len(pos)} positions")
                else:
                    # Just show first few keys
                    keys = list(d.keys())[:5] if isinstance(d, dict) else f"{len(d)} items"
                    print(f"  {ep}: {status} - keys: {keys}")
            else:
                print(f"  {ep}: {status}")
        except Exception as e:
            print(f"  {ep}: ERROR - {e}")
    
    c.close()
except ImportError:
    print("  httpx not available")

# 4. Check key file sizes
print("\n--- KEY FILE SIZES ---")
key_files = [
    "unified_production_server.py",
    "parallel_shadow_trading.py",
    "launch_ultimate_prometheus_LIVE_TRADING.py",
    "core/langgraph_trading_orchestrator.py",
    "core/mercury2_adapter.py",
    "core/llamaindex_sec_analyzer.py",
    "core/finrl_portfolio_optimizer.py",
    "core/redis_cache.py",
    "core/ccxt_exchange_bridge.py",
    "core/gymnasium_trading_env.py",
]
for f in key_files:
    if os.path.exists(f):
        sz = os.path.getsize(f)
        lines = sum(1 for _ in open(f, encoding="utf-8", errors="ignore"))
        print(f"  {f}: {lines} lines ({sz:,} bytes)")
    else:
        print(f"  {f}: MISSING")

# 5. Check .env keys
print("\n--- ENVIRONMENT CONFIG ---")
if os.path.exists(".env"):
    with open(".env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key = line.split("=")[0]
                val = line.split("=", 1)[1] if "=" in line else ""
                # Mask sensitive values
                if any(s in key.upper() for s in ["KEY", "SECRET", "PASSWORD", "TOKEN"]):
                    print(f"  {key}={'***SET***' if val else 'EMPTY'}")
                else:
                    print(f"  {key}={val[:50]}")

# 6. Check what's NOT working
print("\n--- GAPS / ISSUES ---")
gaps = []

# Check if FinRL actually works
try:
    from finrl.agents.stablebaselines3.models import DRLAgent
    print("  FinRL DRLAgent: IMPORTABLE")
except Exception as e:
    gaps.append(f"FinRL DRLAgent not importable: {e}")
    print(f"  FinRL DRLAgent: FAILED - {e}")

# Check if signal weights endpoint exists
try:
    import httpx
    r = httpx.get("http://localhost:8000/api/ai/signal-weights", timeout=10)
    if r.status_code != 200:
        gaps.append("Signal weights API endpoint missing (404)")
        print("  Signal weights API: MISSING (404)")
    else:
        print("  Signal weights API: OK")
except:
    gaps.append("Signal weights API unreachable")

# Check trained model coverage
print(f"\n  Trained models in trained_models/: {len(trained_pkl)}")
if len(trained_pkl) < 10:
    gaps.append(f"Only {len(trained_pkl)} models in trained_models/ (need ~70+)")
    
# Check if shadow trading is running
try:
    import httpx
    r = httpx.get("http://localhost:8000/api/shadow-trading/status", timeout=10)
    if r.status_code == 200:
        d = r.json()
        print(f"  Shadow trading: {json.dumps(d)[:200]}")
    else:
        gaps.append("Shadow trading status endpoint returned non-200")
except:
    pass

print(f"\n--- TOTAL GAPS FOUND: {len(gaps)} ---")
for i, g in enumerate(gaps, 1):
    print(f"  {i}. {g}")

print("\n" + "=" * 60)
print("ASSESSMENT COMPLETE")
print("=" * 60)
