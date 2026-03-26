#!/usr/bin/env python3
"""Quick check of Alpaca account state and trading environment"""
import os
from dotenv import load_dotenv
load_dotenv()

print('=== ENV VARIABLE STATUS ===')
print(f'ALWAYS_LIVE = {os.getenv("ALWAYS_LIVE", "0")}')
print(f'ENABLE_LIVE_ORDER_EXECUTION = {os.getenv("ENABLE_LIVE_ORDER_EXECUTION", "0")}')
print(f'LIVE_TRADING_ENABLED = {os.getenv("LIVE_TRADING_ENABLED", "false")}')
print(f'PAPER_TRADING_ONLY = {os.getenv("PAPER_TRADING_ONLY", "not set")}')
print(f'ALLOW_LIVE_TRADING = {os.getenv("ALLOW_LIVE_TRADING", "not set")}')
print(f'ALPACA_BASE_URL = {os.getenv("ALPACA_BASE_URL", "not set")}')
print(f'ALPACA_PAPER_TRADING = {os.getenv("ALPACA_PAPER_TRADING", "not set")}')

import requests
key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
base = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
h = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}

print('\n=== ALPACA ACCOUNT STATUS ===')
r = requests.get(base + '/v2/account', headers=h, timeout=10)
if r.status_code == 200:
    a = r.json()
    print(f'Status: {a["status"]}')
    print(f'Equity: ${float(a["equity"]):,.2f}')
    print(f'Cash: ${float(a["cash"]):,.2f}')
    print(f'Buying Power: ${float(a["buying_power"]):,.2f}')
    print(f'Portfolio Value: ${float(a["portfolio_value"]):,.2f}')
    print(f'Trading Blocked: {a.get("trading_blocked")}')
    print(f'Account Blocked: {a.get("account_blocked")}')
    print(f'Pattern Day Trader: {a.get("pattern_day_trader")}')
    print(f'Day Trade Count: {a.get("daytrade_count")}')
    print(f'Shorting Enabled: {a.get("shorting_enabled")}')
    print(f'Crypto Status: {a.get("crypto_status", "N/A")}')
else:
    print(f'Error: {r.status_code} {r.text[:200]}')

print('\n=== RECENT ORDERS (All) ===')
r2 = requests.get(base + '/v2/orders?status=all&limit=10', headers=h, timeout=10)
if r2.status_code == 200:
    orders = r2.json()
    print(f'Total orders returned: {len(orders)}')
    for o in orders:
        print(f'  {o["created_at"][:19]} {o["symbol"]} {o["side"]} qty={o["qty"]} status={o["status"]} type={o["type"]}')
else:
    print(f'Error: {r2.status_code}')

print('\n=== POSITIONS ===')
r3 = requests.get(base + '/v2/positions', headers=h, timeout=10)
if r3.status_code == 200:
    pos = r3.json()
    print(f'Open positions: {len(pos)}')
    for p in pos:
        print(f'  {p["symbol"]}: qty={p["qty"]} market_value=${float(p["market_value"]):,.2f} PnL=${float(p["unrealized_pl"]):,.2f}')
else:
    print(f'Positions: {r3.status_code} - {r3.text[:100]}')

# Position size calculations
print('\n=== POSITION SIZE ANALYSIS ($99.11 account) ===')
equity = 99.11
pct = 0.15  # 15% for accounts < $500
trade_amount = equity * pct
print(f'Position size %: {pct*100}%')
print(f'Trade amount per position: ${trade_amount:.2f}')

sample_prices = {'AAPL': 230, 'MSFT': 420, 'GOOGL': 180, 'TSLA': 350, 'NVDA': 130, 'SPY': 600, 'BTC/USD': 95000, 'ETH/USD': 3500}
for sym, price in sample_prices.items():
    qty = trade_amount / price
    if '/' in sym:
        qty = round(qty, 6)
    else:
        qty = round(qty, 4)
    notional = qty * price
    print(f'  {sym}: {qty} shares @ ${price} = ${notional:.2f} notional')
