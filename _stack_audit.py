"""Quick audit of PROMETHEUS current stack"""
import sqlite3, os, glob

# DB tables
for db in ["prometheus_trading.db", "prometheus_learning.db"]:
    if os.path.exists(db):
        c = sqlite3.connect(db)
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"\n{db}: {len(tables)} tables")
        for t in tables:
            cnt = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
            if cnt > 0:
                print(f"  {t}: {cnt:,} rows")
        c.close()

# Model files
pkl_files = glob.glob("models_pretrained/*.pkl")
pt_files = glob.glob("*.pt") + glob.glob("**/*.pt", recursive=True)
print(f"\nModel files: {len(pkl_files)} .pkl, {len(set(pt_files))} .pt")

# Key integration files
key_files = [
    "core/langgraph_trading_orchestrator.py",
    "core/mercury2_adapter.py",
    "core/gymnasium_trading_env.py",
    "core/openbb_data_provider.py",
    "core/ccxt_exchange_bridge.py",
    "core/reinforcement_learning_trading.py",
    "core/hierarchical_agent_coordinator.py",
    "core/fed_nlp_analyzer.py",
    "core/ml_regime_detector.py",
    "core/continuous_learning_engine.py",
    "core/trade_outcome_processor.py",
    "core/real_ai_trading_intelligence.py",
    "core/strategy_degradation_detector.py",
    "core/earnings_calendar_integration.py",
    "core/cross_asset_correlation.py",
    "core/chart_vision_analyzer.py",
    "core/hrm_official_integration.py",
    "core/redis_cache.py",
]
print("\nKey integration files:")
for f in key_files:
    exists = os.path.exists(f)
    size = os.path.getsize(f) if exists else 0
    status = f"{size//1024}KB" if exists else "MISSING"
    print(f"  {'Y' if exists else 'N'} {f} ({status})")

# Ollama models
try:
    import urllib.request, json
    r = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
    models = json.loads(r.read()).get("models", [])
    print(f"\nOllama: {len(models)} models installed")
    for m in models:
        print(f"  {m['name']} ({round(m.get('size',0)/1e9,1)} GB)")
except:
    print("\nOllama: not reachable")
