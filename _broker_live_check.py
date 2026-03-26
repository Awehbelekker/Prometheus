import json
import urllib.request
from datetime import datetime

URL = "http://127.0.0.1:8000/api/admin/full-status"

def get_json(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

data = get_json(URL)

alp_live = data.get("alpaca_live", {})
alp_paper = data.get("alpaca_paper", {})
ib = data.get("ib_broker", {})
auto = data.get("autonomous_trading", {})
activity = data.get("trading_activity", {})

print("timestamp", datetime.utcnow().isoformat() + "Z")
print("success", data.get("success"))
print("live_execution_enabled", data.get("live_execution_enabled"))
print("autonomous_live_execution", auto.get("live_execution"))
print("threads", auto.get("threads"))

print("alpaca_live_connected", alp_live.get("connected"))
print("alpaca_live_mode", alp_live.get("mode"))
print("alpaca_live_market_open", alp_live.get("market_open"))
print("alpaca_live_positions", alp_live.get("position_count"))
print("alpaca_live_open_orders", alp_live.get("open_orders"))

print("alpaca_paper_connected", alp_paper.get("connected"))
print("alpaca_paper_mode", alp_paper.get("mode"))
print("alpaca_paper_positions", alp_paper.get("position_count"))
print("alpaca_paper_open_orders", alp_paper.get("open_orders"))

print("ib_connected", ib.get("connected"))
print("ib_status", ib.get("status"))
print("ib_market_open", ib.get("market_open"))
print("ib_positions", ib.get("position_count"))
print("ib_open_orders", ib.get("open_orders"))

print("trades_24h", activity.get("trades_24h"))
print("trades_total", activity.get("trades_total"))
print("stats_since", activity.get("stats_since"))
