import urllib.request, json, sys

url = "http://127.0.0.1:8000/api/admin/full-status"
try:
    data = json.loads(urllib.request.urlopen(url, timeout=60).read())
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("=== RESPONSE KEYS ===")
print(", ".join(sorted(data.keys())))

for section in ["ib_broker", "alpaca_paper", "autonomous_trading", "guardian"]:
    if section in data and data[section] is not None:
        print(f"\n=== {section.upper()} ===")
        print(json.dumps(data[section], indent=2, default=str)[:1500])

print("\n=== TRADING ACTIVITY ===")
ta = data.get("trading_activity", {})
print(json.dumps(ta, indent=2, default=str)[:1000])
