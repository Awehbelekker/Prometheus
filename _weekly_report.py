#!/usr/bin/env python3
"""PROMETHEUS Weekly Trading Report"""
import alpaca_trade_api as tradeapi
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  PROMETHEUS WEEKLY TRADING REPORT")
print("  " + datetime.now().strftime("%Y-%m-%d %H:%M"))
print("=" * 70)

# Get orders from past 7 days
week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
orders = api.list_orders(status='all', limit=500, after=f'{week_ago}T00:00:00Z')

print(f"\nTotal orders in past 7 days: {len(orders)}")

# Group by day
by_day = defaultdict(list)
for o in orders:
    if o.submitted_at:
        day = o.submitted_at.strftime('%Y-%m-%d')
        by_day[day].append(o)

print("\n" + "=" * 70)
print("  DAILY BREAKDOWN")
print("=" * 70)

total_buys = 0
total_sells = 0
total_buy_vol = 0
total_sell_vol = 0

for day in sorted(by_day.keys()):
    day_orders = by_day[day]
    filled = [o for o in day_orders if o.status == 'filled']
    buys = [o for o in filled if o.side == 'buy']
    sells = [o for o in filled if o.side == 'sell']
    
    buy_vol = sum(float(o.filled_qty or 0) * float(o.filled_avg_price or 0) for o in buys)
    sell_vol = sum(float(o.filled_qty or 0) * float(o.filled_avg_price or 0) for o in sells)
    
    total_buys += len(buys)
    total_sells += len(sells)
    total_buy_vol += buy_vol
    total_sell_vol += sell_vol
    
    weekday = datetime.strptime(day, '%Y-%m-%d').strftime('%a')
    print(f"\n{day} ({weekday}):")
    print(f"   Orders: {len(day_orders)} total, {len(filled)} filled")
    print(f"   Buys: {len(buys)} (${buy_vol:.2f})")
    print(f"   Sells: {len(sells)} (${sell_vol:.2f})")

print("\n" + "-" * 70)
print(f"WEEKLY TOTALS:")
print(f"   Total Buys: {total_buys} (${total_buy_vol:.2f})")
print(f"   Total Sells: {total_sells} (${total_sell_vol:.2f})")
print(f"   Net Investment: ${total_buy_vol - total_sell_vol:.2f}")

# Symbol breakdown
print("\n" + "=" * 70)
print("  TOP TRADED SYMBOLS (Past Week)")
print("=" * 70)

symbol_trades = defaultdict(lambda: {'count': 0, 'volume': 0})
for o in orders:
    if o.status == 'filled':
        vol = float(o.filled_qty or 0) * float(o.filled_avg_price or 0)
        symbol_trades[o.symbol]['count'] += 1
        symbol_trades[o.symbol]['volume'] += vol

sorted_symbols = sorted(symbol_trades.items(), key=lambda x: x[1]['count'], reverse=True)
print("\n   Symbol   | Trades | Volume")
print("   " + "-" * 35)
for sym, data in sorted_symbols[:15]:
    print(f"   {sym:8} | {data['count']:6} | ${data['volume']:.2f}")

# Account and portfolio history
print("\n" + "=" * 70)
print("  ACCOUNT & PORTFOLIO HISTORY")
print("=" * 70)

account = api.get_account()
print(f"\n   Current Equity: ${float(account.equity):.2f}")
print(f"   Cash: ${float(account.cash):.2f}")

try:
    history = api.get_portfolio_history(period='1W', timeframe='1D')
    if history and hasattr(history, 'equity') and history.equity:
        equities = history.equity
        timestamps = history.timestamp
        pls = history.profit_loss if hasattr(history, 'profit_loss') else [0] * len(equities)
        
        print("\n   Daily Equity History:")
        print("   " + "-" * 40)
        
        start_equity = None
        for i, (ts, eq) in enumerate(zip(timestamps, equities)):
            if eq:
                if start_equity is None:
                    start_equity = eq
                day = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %a')
                pl = pls[i] if pls and i < len(pls) and pls[i] else 0
                print(f"   {day}: ${eq:.2f} (P/L: ${pl:+.2f})")
        
        if start_equity and equities[-1]:
            week_change = equities[-1] - start_equity
            week_pct = (week_change / start_equity) * 100
            print("\n   " + "-" * 40)
            print(f"   WEEKLY CHANGE: ${week_change:+.2f} ({week_pct:+.2f}%)")
            
except Exception as e:
    print(f"   Could not get portfolio history: {e}")

print("\n" + "=" * 70)

