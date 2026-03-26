"""Quick check of Alpaca trading status"""
import os
from dotenv import load_dotenv
load_dotenv()
import requests

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
base = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
h = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}

# Account
r = requests.get(f'{base}/v2/account', headers=h, timeout=10)
a = r.json()
equity = float(a['equity'])
cash = float(a['cash'])
last_equity = float(a['last_equity'])
day_pl = equity - last_equity

print("=" * 60)
print("ALPACA ACCOUNT STATUS")
print("=" * 60)
print(f"  Equity:         ${equity:.2f}")
print(f"  Cash:           ${cash:.2f}")
print(f"  Buying Power:   ${float(a['buying_power']):.2f}")
print(f"  Portfolio Value: ${float(a['portfolio_value']):.2f}")
print(f"  Last Equity:    ${last_equity:.2f}")
print(f"  Day P/L:        ${day_pl:+.2f}")
print()

# Positions
r2 = requests.get(f'{base}/v2/positions', headers=h, timeout=10)
positions = r2.json()
total_pnl = 0
print(f"OPEN POSITIONS ({len(positions)}):")
print("-" * 60)
if positions:
    for p in positions:
        sym = p['symbol']
        qty = p['qty']
        avg = float(p['avg_entry_price'])
        cur = float(p['current_price'])
        pnl = float(p['unrealized_pl'])
        pnl_pct = float(p['unrealized_plpc']) * 100
        mkt_val = float(p['market_value'])
        total_pnl += pnl
        print(f"  {sym:10s}  qty={qty:>10s}  avg=${avg:>10.4f}  now=${cur:>10.4f}  P/L=${pnl:>+8.2f} ({pnl_pct:>+.2f}%)  val=${mkt_val:.2f}")
    print("-" * 60)
    print(f"  TOTAL UNREALIZED P/L: ${total_pnl:+.2f}")
else:
    print("  No open positions")
print()

# Recent orders
r3 = requests.get(f'{base}/v2/orders?status=all&limit=20&direction=desc', headers=h, timeout=10)
orders = r3.json()
print(f"RECENT ORDERS (last 20):")
print("-" * 60)
for o in orders:
    created = o['created_at'][:19]
    sym = o['symbol']
    side = o['side'].upper()
    qty = o['qty'] or o.get('notional', '?')
    status = o['status']
    filled_price = o.get('filled_avg_price', '-')
    asset_class = o.get('asset_class', '')
    print(f"  {created}  {sym:10s}  {side:4s}  qty={qty:>10s}  status={status:10s}  fill=${filled_price}  {asset_class}")
print()
print("=" * 60)
