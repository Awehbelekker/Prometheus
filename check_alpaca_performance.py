"""
Check Alpaca Account Performance
"""

import os
import sys
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
headers = {
    'APCA-API-KEY-ID': key,
    'APCA-API-SECRET-KEY': secret
}

print("=" * 70)
print("ALPACA ACCOUNT PERFORMANCE REPORT")
print("=" * 70)

# Get account info
account = requests.get('https://paper-api.alpaca.markets/v2/account', headers=headers).json()

print("\n📊 ACCOUNT SUMMARY:")
print("-" * 70)
equity = float(account.get('equity', 0))
cash = float(account.get('cash', 0))
buying_power = float(account.get('buying_power', 0))
portfolio_value = float(account.get('portfolio_value', 0))
last_equity = float(account.get('last_equity', 0))

print(f"Current Equity:    ${equity:.2f}")
print(f"Cash:              ${cash:.2f}")
print(f"Buying Power:      ${buying_power:.2f}")
print(f"Portfolio Value:   ${portfolio_value:.2f}")
print(f"Last Equity:       ${last_equity:.2f}")

if last_equity > 0:
    profit = equity - last_equity
    profit_pct = (profit / last_equity) * 100
    print(f"\nToday's P/L:       ${profit:.2f} ({profit_pct:+.2f}%)")

# Get positions
positions_response = requests.get('https://paper-api.alpaca.markets/v2/positions', headers=headers)
positions = positions_response.json()

# Check if positions is an error or empty
if not isinstance(positions, list):
    print(f"\n⚠️  Error fetching positions: {positions}")
    positions = []

print(f"\n📈 POSITIONS ({len(positions)} total):")
print("-" * 70)

total_pl = 0
winners = []
losers = []

for p in positions:
    symbol = p['symbol']
    qty = float(p['qty'])
    avg_price = float(p['avg_entry_price'])
    current_price = float(p['current_price'])
    pl = float(p['unrealized_pl'])
    pl_pct = float(p['unrealized_plpc']) * 100
    
    total_pl += pl
    
    if pl > 0:
        winners.append((symbol, pl, pl_pct))
    else:
        losers.append((symbol, pl, pl_pct))
    
    status = "🟢" if pl > 0 else "🔴" if pl < 0 else "⚪"
    print(f"{status} {symbol:8s} | {qty:>10.4f} @ ${avg_price:>8.2f} | Now: ${current_price:>8.2f} | P/L: ${pl:>8.2f} ({pl_pct:>+6.2f}%)")

print("-" * 70)
print(f"Total Unrealized P/L: ${total_pl:.2f}")

# Winners and Losers
print(f"\n🏆 TOP WINNERS ({len(winners)} positions):")
winners.sort(key=lambda x: x[1], reverse=True)
for symbol, pl, pl_pct in winners[:5]:
    print(f"   {symbol:8s}: ${pl:>8.2f} ({pl_pct:>+6.2f}%)")

print(f"\n📉 TOP LOSERS ({len(losers)} positions):")
losers.sort(key=lambda x: x[1])
for symbol, pl, pl_pct in losers[:5]:
    print(f"   {symbol:8s}: ${pl:>8.2f} ({pl_pct:>+6.2f}%)")

# Get recent activities
print("\n📜 RECENT TRADING ACTIVITY (Last 7 Days):")
print("-" * 70)

after = (datetime.now() - timedelta(days=7)).isoformat() + 'Z'
activities = requests.get(
    f'https://paper-api.alpaca.markets/v2/account/activities?after={after}',
    headers=headers
).json()

if isinstance(activities, list):
    print(f"Total Activities: {len(activities)}")
    
    # Count by type
    fills = [a for a in activities if a.get('activity_type') == 'FILL']
    buys = [a for a in fills if a.get('side') == 'buy']
    sells = [a for a in fills if a.get('side') == 'sell']
    
    print(f"   Fills: {len(fills)} (Buys: {len(buys)}, Sells: {len(sells)})")
    
    print("\nRecent Trades:")
    for act in fills[:10]:
        symbol = act.get('symbol', '')
        side = act.get('side', '').upper()
        qty = act.get('qty', '')
        price = act.get('price', '')
        timestamp = act.get('transaction_time', '')[:19]
        
        side_icon = "🟢 BUY " if side == 'BUY' else "🔴 SELL"
        print(f"   {timestamp} | {side_icon} | {symbol:8s} | {qty:>6s} @ ${price}")
else:
    print("No recent activities or error")

print("\n" + "=" * 70)
print("PERFORMANCE SUMMARY")
print("=" * 70)
print(f"Account Value:     ${equity:.2f}")
print(f"Total Positions:   {len(positions)}")
print(f"Unrealized P/L:    ${total_pl:.2f}")
print(f"Win Rate:          {len(winners)}/{len(positions)} ({len(winners)/len(positions)*100:.1f}%)" if positions else "N/A")
print("=" * 70)

