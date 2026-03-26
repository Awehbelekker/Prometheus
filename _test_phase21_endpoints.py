"""Test all Phase 21 API endpoints."""
import httpx, json, sys

BASE = "http://localhost:8000"
tests = [
    ("LangGraph",    f"{BASE}/api/ai/langgraph/status"),
    ("OpenBB",       f"{BASE}/api/data/openbb/status"),
    ("CCXT",         f"{BASE}/api/data/ccxt/status"),
    ("Gymnasium",    f"{BASE}/api/ai/gymnasium/status"),
    ("Mercury2",     f"{BASE}/api/ai/mercury2/status"),
    ("Cache",        f"{BASE}/api/system/cache/stats"),
    ("SEC Filings",  f"{BASE}/api/ai/sec-filings/status"),
    ("FinRL",        f"{BASE}/api/ai/finrl/status"),
]

passed = 0
with httpx.Client(timeout=60) as client:
    for name, url in tests:
        try:
            r = client.get(url)
            d = r.json()
            ok = d.get("success", False)
            status = "PASS" if r.status_code == 200 else f"HTTP {r.status_code}"
            print(f"  [{status}] {name}: success={ok}")
            if r.status_code == 200:
                passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")

    print(f"\nPhase 21 endpoints: {passed}/{len(tests)} responding")

    # Also test all-systems-status
    print("\n--- All Systems Status ---")
    r = client.get(f"{BASE}/api/ai/all-systems/status")
    d = r.json()
    print(f"Total: {d['total_systems']}  Active: {d['active_systems']}")
    for k, v in d["systems"].items():
        print(f"  {k}: {v['status']}")
