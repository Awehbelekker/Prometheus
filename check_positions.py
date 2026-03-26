#!/usr/bin/env python
"""Quick script to check Alpaca positions and account status"""
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

client = TradingClient(os.getenv('ALPACA_API_KEY'), os.getenv('ALPACA_SECRET_KEY'), paper=False)

print('=' * 60)
print('PROMETHEUS TRADING PLATFORM - POSITION STATUS')
print('=' * 60)

# Get account
account = client.get_account()
print(f'\nACCOUNT STATUS:')
print(f'  Cash: ${float(account.cash):.2f}')
print(f'  Buying Power: ${float(account.buying_power):.2f}')
print(f'  Portfolio Value: ${float(account.portfolio_value):.2f}')
print(f'  Daytrade Count: {account.daytrade_count}')

# Get positions
positions = client.get_all_positions()
print(f'\nPOSITIONS ({len(positions)} total):')
print('-' * 60)

total_value = 0
total_pnl = 0

for p in positions:
    pnl_pct = float(p.unrealized_plpc) * 100
    pnl_usd = float(p.unrealized_pl)
    market_value = float(p.market_value)
    total_value += market_value
    total_pnl += pnl_usd
    
    emoji = '+' if pnl_pct >= 0 else '-'
    status = ''
    if pnl_pct >= 0.5:
        status = ' [PROFIT - SELL]'
    elif pnl_pct <= -3.0:
        status = ' [STOP-LOSS - SELL]'
    
    print(f'  {emoji} {p.symbol}: {pnl_pct:+.2f}% (${pnl_usd:+.2f}) | Value: ${market_value:.2f} | Qty: {p.qty}{status}')

print('-' * 60)
print(f'  TOTAL VALUE: ${total_value:.2f}')
print(f'  TOTAL P/L: ${total_pnl:+.2f}')

# Get open orders
orders = client.get_orders()
print(f'\nOPEN ORDERS ({len(orders)} total):')
print('-' * 60)
for o in orders:
    print(f'  {o.symbol}: {o.side} {o.qty} @ {o.type} - Status: {o.status}')

print('\n' + '=' * 60)

