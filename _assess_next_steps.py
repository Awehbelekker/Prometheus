"""Quick system health + next-steps assessment."""
import httpx, json

c = httpx.Client(timeout=30, base_url="http://localhost:8000")

# 1. Trading stats
print("=== TRADING STATS ===")
try:
    r = c.get("/api/trading/stats")
    d = r.json()
    for k in ["total_trades","winning_trades","losing_trades","win_rate","total_pnl","average_pnl"]:
        print(f"  {k}: {d.get(k, 'N/A')}")
except Exception as e:
    print(f"  Error: {e}")

# 2. Broker status
print("\n=== BROKER STATUS ===")
try:
    r = c.get("/api/brokers/status")
    d = r.json()
    for b in d.get("brokers", []):
        print(f"  {b.get('name','?')}: {b.get('status','?')}  equity={b.get('equity','?')}")
except Exception as e:
    print(f"  Error: {e}")

# 3. AI voter count
print("\n=== AI SIGNAL VOTERS ===")
try:
    r = c.get("/api/ai/signal-weights")
    d = r.json()
    weights = d.get("weights", d.get("signal_weights", {}))
    print(f"  Total voters: {len(weights)}")
    for name, w in list(weights.items()):
        print(f"    {name}: {w}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Model count
print("\n=== TRAINED MODELS ===")
import glob
pkl_count = len(glob.glob("trained_models/**/*.pkl", recursive=True))
pt_count = len(glob.glob("trained_models/**/*.pt", recursive=True))
print(f"  .pkl models: {pkl_count}")
print(f"  .pt models: {pt_count}")

# 5. New Phase 21 systems usage
print("\n=== PHASE 21 INTEGRATION STATUS ===")
new_systems = [
    ("/api/ai/langgraph/status", "LangGraph"),
    ("/api/data/openbb/status", "OpenBB"),
    ("/api/data/ccxt/status", "CCXT"),
    ("/api/ai/gymnasium/status", "Gymnasium/SB3"),
    ("/api/ai/mercury2/status", "Mercury2"),
    ("/api/system/cache/stats", "Redis Cache"),
    ("/api/ai/sec-filings/status", "SEC Filings RAG"),
    ("/api/ai/finrl/status", "FinRL"),
]
for url, name in new_systems:
    try:
        r = c.get(url)
        d = r.json()
        active = d.get("success", False)
        # Check if actually being used in trade decisions
        print(f"  {name}: {'ACTIVE' if active else 'INACTIVE'} (endpoint responding)")
    except:
        print(f"  {name}: OFFLINE")

# 6. Check which new systems are wired into the VOTING pipeline
print("\n=== VOTING PIPELINE CHECK ===")
print("  Checking if Phase 21 systems feed into trade decisions...")
import ast, re
with open("unified_production_server.py", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
    for system in ["langgraph", "openbb", "ccxt", "mercury2", "sec_filings", "finrl", "gymnasium"]:
        # Check if system contributes to signals/votes
        vote_pattern = re.findall(rf"{system}.*(?:signal|vote|score|confidence|weight)", content, re.IGNORECASE)
        if vote_pattern:
            print(f"  {system}: WIRED into voting ({len(vote_pattern)} references)")
        else:
            print(f"  {system}: NOT in voting pipeline (standalone endpoint only)")
