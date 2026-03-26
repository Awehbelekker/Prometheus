"""Quick test of all 4 Phase 23 endpoints."""
import urllib.request
import json

endpoints = [
    "http://localhost:8000/api/risk/portfolio",
    "http://localhost:8000/api/retrainer/status",
    "http://localhost:8000/api/federated/status",
    "http://localhost:8000/api/paper-trading/status",
    "http://localhost:8000/api/paper-trading/open-positions",
]

for url in endpoints:
    try:
        r = urllib.request.urlopen(url, timeout=30)
        data = json.loads(r.read())
        label = url.split("/api/")[1]
        print(f"  {label}: {data.get('success', '?')} — {json.dumps({k:v for k,v in data.items() if k != 'risk_metrics'}, indent=None)[:120]}")
    except Exception as e:
        print(f"  FAIL {url}: {e}")

print("\nAll Phase 23 endpoints tested.")
