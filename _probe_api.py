import time
import urllib.request

URLS = [
    "http://localhost:8000/api/admin/full-status",
    "http://127.0.0.1:8000/api/admin/full-status",
]

for url in URLS:
    ok = 0
    fail = 0
    last_error = ""
    for _ in range(15):
        try:
            with urllib.request.urlopen(url, timeout=5) as resp:
                if resp.status == 200:
                    ok += 1
                else:
                    fail += 1
                    last_error = f"HTTP {resp.status}"
        except Exception as exc:
            fail += 1
            last_error = str(exc)
        time.sleep(0.4)
    print(f"{url} ok={ok} fail={fail} last_error={last_error}")
