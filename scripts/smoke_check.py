#!/usr/bin/env python3
"""
Simple smoke test for PROMETHEUS services.
Checks:
- Backend (8000): /health
- Backend-proxied Real Data: /real-data/api/ai-trading/health
- Real Data direct (8002): /api/ai-trading/health (optional)
- Nginx (8080): /health and /real-data/api/ai-trading/health (optional)

Exit code 0 on success; non-zero on failure. Prints concise results.
"""

import sys
import json
import time
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

TIMEOUT = 5

TARGETS = [
    ("backend", "http://localhost:8000/health"),
    ("backend->realdata", "http://localhost:8000/real-data/api/ai-trading/health"),
    ("realdata", "http://localhost:8002/api/ai-trading/health"),
    ("nginx", "http://localhost:8080/health"),
    ("nginx->realdata", "http://localhost:8080/real-data/api/ai-trading/health"),
]


def get_json(url: str):
    req = Request(url, headers={"User-Agent": "smoke-check"})
    with urlopen(req, timeout=TIMEOUT) as resp:
        ctype = resp.headers.get("Content-Type", "")
        data = resp.read().decode("utf-8", errors="ignore")
        try:
            return json.loads(data), resp.status, ctype
        except json.JSONDecodeError:
            return {"raw": data}, resp.status, ctype


def main():
    failed = []
    for name, url in TARGETS:
        try:
            data, status, ctype = get_json(url)
            ok = (200 <= status < 300)
            print(f"[OK] {name}: {url} -> {status} {ctype}") if ok else print(f"[WARN] {name}: {url} -> {status}")
            # Basic payload sanity for known endpoints
            if name.endswith("realdata") and isinstance(data, dict):
                if not data.get("success", True):
                    print(f"  note: payload success=false for {name}")
        except HTTPError as e:
            print(f"[ERR] {name}: {url} -> HTTP {e.code}")
            failed.append(name)
        except URLError as e:
            print(f"[ERR] {name}: {url} -> {e.reason}")
            failed.append(name)
        except Exception as e:
            print(f"[ERR] {name}: {url} -> {e}")
            failed.append(name)

    if failed:
        print(f"\nSmoke check failed for: {', '.join(failed)}")
        sys.exit(1)

    print("\nSmoke check passed.")


if __name__ == "__main__":
    main()

