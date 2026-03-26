#!/usr/bin/env python3
"""Get comprehensive PROMETHEUS trading stats for full day"""
import alpaca_trade_api as tradeapi
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  PROMETHEUS FULL DAY TRADING STATISTICS")
print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 70)

# Get account
account = api.get_account()
equity = float(account.equity)
last_equity = float(account.last_equity)
day_pl = equity - last_equity
day_pl_pct = (day_pl / last_equity * 100) if last_equity > 0 else 0

print(f"\n💰 ACCOUNT SUMMARY")
print(f"   Current Equity: ${equity:.2f}")
print(f"   Previous Close: ${last_equity:.2f}")
print(f"   Day P/L: ${day_pl:+.2f} ({day_pl_pct:+.2f}%)")
print(f"   Cash Available: ${float(account.cash):.2f}")
print(f"   Buying Power: ${float(account.buying_power):.2f}")

# Get all orders from last 2 days
yesterday = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
orders = api.list_orders(status='all', limit=500, after=f'{yesterday}T00:00:00Z')

# Separate by day
today = datetime.now().strftime('%Y-%m-%d')
today_orders = [o for o in orders if o.submitted_at and o.submitted_at.strftime('%Y-%m-%d') == today]
yesterday_orders = [o for o in orders if o.submitted_at and o.submitted_at.strftime('%Y-%m-%d') != today]

print(f"\n📊 ORDER SUMMARY")
print(f"   Today's Orders: {len(today_orders)}")
print(f"   Yesterday's Orders: {len(yesterday_orders)}")

# Today's stats
today_buys = [o for o in today_orders if o.side == 'buy' and o.status == 'filled']
today_sells = [o for o in today_orders if o.side == 'sell' and o.status == 'filled']
today_buy_vol = sum(float(o.filled_qty or 0) * float(o.filled_avg_price or 0) for o in today_buys)
today_sell_vol = sum(float(o.filled_qty or 0) * float(o.filled_avg_price or 0) for o in today_sells)

print(f"\n📈 TODAY'S TRADING")
print(f"   Filled Buys: {len(today_buys)} (${today_buy_vol:.2f})")
print(f"   Filled Sells: {len(today_sells)} (${today_sell_vol:.2f})")
print(f"   Net Flow: ${today_buy_vol - today_sell_vol:+.2f}")

# Current positions
positions = api.list_positions()
print(f"\n📊 CURRENT POSITIONS ({len(positions)})")
print("-" * 70)

winners = []
losers = []
total_value = 0
total_pl = 0

for p in positions:
    qty = float(p.qty)
    entry = float(p.avg_entry_price)
    current = float(p.current_price)
    value = float(p.market_value)
    pl = float(p.unrealized_pl)
    pl_pct = float(p.unrealized_plpc) * 100
    total_value += value
    total_pl += pl
    
    if pl >= 0:
        winners.append((p.symbol, pl, pl_pct))
    else:
        losers.append((p.symbol, pl, pl_pct))
    
    emoji = "🟢" if pl >= 0 else "🔴"
    print(f"   {emoji} {p.symbol:6} | {qty:.4f} @ ${entry:.2f} → ${current:.2f} | ${value:.2f} | P/L: ${pl:+.2f} ({pl_pct:+.2f}%)")

print("-" * 70)
print(f"   TOTAL VALUE: ${total_value:.2f}")
print(f"   TOTAL UNREALIZED P/L: ${total_pl:+.2f}")

# Win/Loss Analysis
print(f"\n🏆 WIN/LOSS ANALYSIS")
print(f"   Winners: {len(winners)} positions")
print(f"   Losers: {len(losers)} positions")
win_rate = len(winners) / len(positions) * 100 if positions else 0
print(f"   Win Rate: {win_rate:.1f}%")

if winners:
    best = max(winners, key=lambda x: x[1])
    print(f"   Best Position: {best[0]} +${best[1]:.2f} ({best[2]:+.2f}%)")
if losers:
    worst = min(losers, key=lambda x: x[1])
    print(f"   Worst Position: {worst[0]} ${worst[1]:.2f} ({worst[2]:+.2f}%)")

# Sector breakdown
print(f"\n📊 POSITION BREAKDOWN")
tech = ['AAPL', 'MSFT', 'NVDA', 'AMD', 'GOOGL', 'META', 'AMZN', 'TSLA', 'NFLX']
etfs = ['SPY', 'QQQ', 'DIA', 'IWM']
tech_positions = [p for p in positions if p.symbol in tech]
etf_positions = [p for p in positions if p.symbol in etfs]
print(f"   Tech Stocks: {len(tech_positions)}")
print(f"   ETFs: {len(etf_positions)}")
print(f"   Other: {len(positions) - len(tech_positions) - len(etf_positions)}")

print("\n" + "=" * 70)

