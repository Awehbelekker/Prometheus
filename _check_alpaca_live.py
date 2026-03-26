import requests

headers = {
    'APCA-API-KEY-ID': 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z',
    'APCA-API-SECRET-KEY': 'At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX'
}
base = 'https://api.alpaca.markets'

# Account
acct = requests.get(f'{base}/v2/account', headers=headers, timeout=10).json()
print("=== ALPACA LIVE ACCOUNT ===")
print(f"  Status:        {acct.get('status')}")
print(f"  Cash:          ${float(acct.get('cash', 0)):.2f}")
print(f"  Portfolio:     ${float(acct.get('portfolio_value', 0)):.2f}")
print(f"  Buying power:  ${float(acct.get('buying_power', 0)):.2f}")
print(f"  Equity:        ${float(acct.get('equity', 0)):.2f}")
print(f"  Long value:    ${float(acct.get('long_market_value', 0)):.2f}")
print()

# Open positions
pos = requests.get(f'{base}/v2/positions', headers=headers, timeout=10).json()
print("=== OPEN POSITIONS ===")
if not pos:
    print("  (none)")
for p in pos:
    sym  = p['symbol']
    qty  = p['qty']
    entry = float(p['avg_entry_price'])
    curr  = float(p['current_price'])
    pl    = float(p['unrealized_pl'])
    plpct = float(p['unrealized_plpc']) * 100
    print(f"  {sym:<6}  qty={qty:<5}  entry=${entry:.2f}  now=${curr:.2f}  P/L=${pl:.2f} ({plpct:+.1f}%)")

print()

# Recent orders
orders = requests.get(f'{base}/v2/orders?status=all&limit=20&direction=desc', headers=headers, timeout=10).json()
print("=== LAST 20 ORDERS ===")
if not orders:
    print("  (none)")
for o in orders:
    date   = o['submitted_at'][:10] if o.get('submitted_at') else '?'
    side   = o['side'].upper()
    qty    = o.get('qty', o.get('notional', '?'))
    sym    = o['symbol']
    status = o['status']
    price  = f"${float(o['filled_avg_price']):.2f}" if o.get('filled_avg_price') else 'unfilled'
    print(f"  {date}  {side:<4}  {qty}x {sym:<6}  {status:<12}  filled@{price}")
