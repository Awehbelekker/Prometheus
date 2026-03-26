"""Quick live health check for all Prometheus endpoints."""
import requests, json

endpoints = [
    ("Health", "http://localhost:8000/health"),
    ("System Status", "http://localhost:8000/api/system/status"),
    ("Trading System", "http://localhost:8000/api/health/trading-system"),
    ("System Health", "http://localhost:8000/api/system/health"),
]

for name, url in endpoints:
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        print(f"\n{'='*60}")
        print(f"{name} ({r.status_code})")
        print(f"{'='*60}")
        for k in ["status", "success", "ready_for_live_trading", "system_health",
                   "uptime_seconds", "errors_total"]:
            if k in data:
                print(f"  {k}: {data[k]}")
        if "services" in data:
            print(f"  services:")
            svcs = data["services"]
            for sk, sv in svcs.items():
                print(f"    {sk}: {sv}")
        if "summary" in data:
            print(f"  summary:")
            for sk, sv in data["summary"].items():
                print(f"    {sk}: {sv}")
        if "health_checks" in data:
            hc = data["health_checks"]
            for svc, info in hc.items():
                if isinstance(info, dict):
                    st = info.get("status", info.get("connected", "?"))
                    print(f"  {svc}: {st}")
                else:
                    print(f"  {svc}: {info}")
    except requests.exceptions.ConnectionError:
        print(f"\n{'='*60}")
        print(f"{name}: CONNECTION REFUSED")
        print(f"{'='*60}")
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"{name}: ERROR - {e}")
        print(f"{'='*60}")
