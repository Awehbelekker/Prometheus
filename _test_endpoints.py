"""Quick test of Phase 23 endpoints."""
import urllib.request
import json

endpoints = [
    ("GET", "http://localhost:8000/api/risk/portfolio"),
    ("GET", "http://localhost:8000/api/retrainer/status"),
    ("GET", "http://localhost:8000/api/federated/status"),
    ("GET", "http://localhost:8000/api/paper-trading/status"),
    ("GET", "http://localhost:8000/api/paper-trading/open-positions"),
]

for method, url in endpoints:
    try:
        r = urllib.request.urlopen(url, timeout=15)
        body = r.read().decode()[:300]
        print(f"  OK  {url} -> {r.status} {body}")
    except urllib.error.HTTPError as e:
        print(f"  FAIL {url} -> HTTP {e.code} {e.reason}")
    except Exception as e:
        print(f"  ERR  {url} -> {type(e).__name__}: {e}")

print("\nDone.")
