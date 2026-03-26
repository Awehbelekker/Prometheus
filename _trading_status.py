#!/usr/bin/env python3
"""Get comprehensive trading status for today"""
import alpaca_trade_api as tradeapi
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

# Get today's orders
today = datetime.now().strftime('%Y-%m-%d')
orders = api.list_orders(status='all', limit=50, after=f'{today}T00:00:00Z')

print('=' * 70)
print(f'  PROMETHEUS TRADING ACTIVITY - TODAY ({today})')
print('=' * 70)

# Count trades
buys = [o for o in orders if o.side == 'buy' and o.status == 'filled']
sells = [o for o in orders if o.side == 'sell' and o.status == 'filled']
pending = [o for o in orders if o.status in ['accepted', 'pending_new', 'new']]

print(f'\n📊 TRADE SUMMARY:')
print(f'   Total Orders: {len(orders)}')
print(f'   Filled Buys: {len(buys)}')
print(f'   Filled Sells: {len(sells)}')
print(f'   Pending: {len(pending)}')

# Calculate total volume
total_buy_value = sum(float(o.filled_qty or 0) * float(o.filled_avg_price or 0) for o in buys)
total_sell_value = sum(float(o.filled_qty or 0) * float(o.filled_avg_price or 0) for o in sells)

print(f'   Total Buy Volume: ${total_buy_value:.2f}')
print(f'   Total Sell Volume: ${total_sell_value:.2f}')

print(f'\n📋 ALL ORDERS TODAY:')
print('-' * 70)
for o in orders:
    filled_qty = float(o.filled_qty) if o.filled_qty else 0
    filled_price = float(o.filled_avg_price) if o.filled_avg_price else 0
    value = filled_qty * filled_price
    time_str = o.submitted_at.strftime('%H:%M:%S') if o.submitted_at else 'N/A'
    print(f'   {time_str} | {o.symbol:8} | {o.side:4} | {filled_qty:8.4f} @ ${filled_price:8.2f} | ${value:7.2f} | {o.status}')

# Get account
account = api.get_account()
day_pl = float(account.equity) - float(account.last_equity)
day_pl_pct = (day_pl / float(account.last_equity)) * 100 if float(account.last_equity) > 0 else 0

print(f'\n💰 ACCOUNT STATUS:')
print(f'   Equity: ${float(account.equity):.2f}')
print(f'   Cash: ${float(account.cash):.2f}')
print(f'   Buying Power: ${float(account.buying_power):.2f}')
print(f'   Day P/L: ${day_pl:+.2f} ({day_pl_pct:+.2f}%)')

# Get positions
positions = api.list_positions()
print(f'\n📈 CURRENT POSITIONS ({len(positions)}):')
print('-' * 70)
total_value = 0
total_pl = 0
for p in positions:
    qty = float(p.qty)
    price = float(p.current_price)
    cost = float(p.avg_entry_price)
    value = float(p.market_value)
    pl = float(p.unrealized_pl)
    pl_pct = float(p.unrealized_plpc) * 100
    total_value += value
    total_pl += pl
    print(f'   {p.symbol:8} | {qty:8.4f} @ ${cost:8.2f} -> ${price:8.2f} | ${value:7.2f} | P/L: ${pl:+6.2f} ({pl_pct:+.2f}%)')

print(f'\n   TOTAL POSITION VALUE: ${total_value:.2f}')
print(f'   TOTAL UNREALIZED P/L: ${total_pl:+.2f}')
print('=' * 70)

