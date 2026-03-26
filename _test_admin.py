import urllib.request, json, sys

print("Testing admin endpoint...")
try:
    r = urllib.request.urlopen('http://localhost:8000/api/admin/full-status', timeout=30)
    d = json.loads(r.read())
    print("ADMIN ENDPOINT: OK")
    for k in d:
        if isinstance(d[k], dict):
            print(f"  {k}: {json.dumps(d[k])[:120]}")
        else:
            print(f"  {k}: {d[k]}")
except urllib.error.HTTPError as e:
    print(f"ADMIN ENDPOINT: HTTP {e.code}")
except Exception as e:
    print(f"ADMIN ENDPOINT: ERROR - {e}")

print()
print("Testing dashboard...")
try:
    r2 = urllib.request.urlopen('http://localhost:8000/dashboard', timeout=10)
    content = r2.read().decode()
    has_prom = "PROMETHEUS" in content
    print(f"DASHBOARD: OK ({len(content)} bytes, has PROMETHEUS: {has_prom})")
except urllib.error.HTTPError as e:
    print(f"DASHBOARD: HTTP {e.code}")
except Exception as e:
    print(f"DASHBOARD: ERROR - {e}")

print()
print("Testing route boundary...")
for url in ['/health', '/api/ai-trading/health', '/api/admin/dashboard', '/api/trading/system/status']:
    try:
        r = urllib.request.urlopen(f'http://localhost:8000{url}', timeout=10)
        print(f"  {url}: {r.status}")
    except urllib.error.HTTPError as e:
        print(f"  {url}: HTTP {e.code}")
    except Exception as e:
        print(f"  {url}: ERROR ({type(e).__name__})")
