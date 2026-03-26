"""Wait for server to be ready, then test Phase 23 endpoints."""
import urllib.request
import json
import time
import sys

BASE = "http://localhost:8000"

# Wait for server to be ready
print("Waiting for server to accept connections...")
for i in range(60):  # up to 5 min
    try:
        r = urllib.request.urlopen(f"{BASE}/api/paper-trading/status", timeout=5)
        print(f"  Server ready after {(i+1)*5}s!")
        break
    except Exception:
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)
else:
    print("\nServer not ready after 5 minutes. Aborting.")
    sys.exit(1)

print()

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

tests = [
    ("GET",  "/api/risk/portfolio"),
    ("GET",  "/api/risk/position/AAPL"),
    ("GET",  "/api/risk/position-size/AAPL"),
    ("GET",  "/api/retrainer/status"),
    ("GET",  "/api/federated/status"),
    ("GET",  "/api/paper-trading/report"),
    ("GET",  "/api/paper-trading/open-positions"),
    ("GET",  "/api/paper-trading/status"),
]

ok = 0
fail = 0
print("=" * 70)
print("PHASE 23 ENDPOINT TESTS (8 GET endpoints)")
print("=" * 70)
for method, path in tests:
    code, body = get(BASE + path) if method == "GET" else post(BASE + path)
    success = code == 200 and body.get("success") is not False
    tag = "PASS" if success else "WARN" if code == 200 else "FAIL"
    if success:
        ok += 1
    else:
        fail += 1
    print(f"  [{tag}] {method:4s} {path}")
    print(f"         {str(body)[:120]}")
    print()

print("=" * 70)
print(f"Results: {ok} passed, {fail} failed out of {ok+fail}")
print("=" * 70)
