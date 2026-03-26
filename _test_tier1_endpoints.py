"""Quick test of all new Tier 1 API endpoints."""
import requests
import json

base = "http://localhost:8000"

endpoints = [
    ("GET", "/api/ai/learning/status"),
    ("GET", "/api/ai/regime/current"),
    ("GET", "/api/ai/fed-signal"),
    ("GET", "/api/ai/all-systems/status"),
    ("GET", "/api/ai/rl-agent/status"),
]

for method, path in endpoints:
    print(f"\n{'='*60}")
    print(f"{method} {path}")
    print("=" * 60)
    try:
        r = requests.get(f"{base}{path}", timeout=30)
        data = r.json()
        print(json.dumps(data, indent=2, default=str))
    except Exception as e:
        print(f"ERROR: {e}")

print("\n\nAll endpoint tests complete.")
