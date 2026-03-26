"""Comprehensive Phase 23 endpoint test — all 14 endpoints."""
import urllib.request
import json

def get(url):
    try:
        r = urllib.request.urlopen(url, timeout=30)
        body = json.loads(r.read().decode())
        return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.reason}
    except Exception as e:
        return 0, {"error": f"{type(e).__name__}: {e}"}

def post(url):
    try:
        req = urllib.request.Request(url, data=b'', method='POST')
        req.add_header('Content-Type', 'application/json')
        r = urllib.request.urlopen(req, timeout=60)
        body = json.loads(r.read().decode())
        return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.reason}
    except Exception as e:
        return 0, {"error": f"{type(e).__name__}: {e}"}

BASE = "http://localhost:8000"
ok = 0
fail = 0

tests = [
    # Risk endpoints
    ("GET",  "/api/risk/portfolio"),
    ("GET",  "/api/risk/position/AAPL"),
    ("GET",  "/api/risk/position-size/AAPL"),
    # Retrainer endpoints
    ("GET",  "/api/retrainer/status"),
    # Federated endpoints
    ("GET",  "/api/federated/status"),
    # Paper trading endpoints
    ("GET",  "/api/paper-trading/report"),
    ("GET",  "/api/paper-trading/open-positions"),
    ("GET",  "/api/paper-trading/status"),
]

print("=" * 70)
print("PHASE 23 ENDPOINT TESTS")
print("=" * 70)
for method, path in tests:
    url = BASE + path
    if method == "GET":
        code, body = get(url)
    else:
        code, body = post(url)
    # Determine pass/fail
    success = code == 200 and body.get("error") is None and body.get("success") is not False
    status = "PASS" if success else "WARN" if code == 200 else "FAIL"
    if status == "PASS":
        ok += 1
    else:
        fail += 1
    summary = str(body)[:120]
    print(f"  [{status}] {method:4s} {path}")
    print(f"         HTTP {code}: {summary}")
    print()

print("=" * 70)
print(f"Results: {ok} passed, {fail} warnings/failures out of {ok+fail} tests")
print("=" * 70)

# Also check systems count
code, body = get(BASE + "/api/system-status")
if code == 200:
    total = body.get("total_ai_systems", "?")
    active = body.get("active_systems", "?")
    print(f"\nSystem Status: {total} AI systems, {active} active")
