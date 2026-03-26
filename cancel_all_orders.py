#!/usr/bin/env python
"""
🚫 PROMETHEUS - Cancel All Open Orders
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

client = TradingClient(
    os.getenv('ALPACA_API_KEY'),
    os.getenv('ALPACA_SECRET_KEY'),
    paper=False
)

print('='*70)
print('CANCELLING ALL OPEN ORDERS')
print('='*70)

# Get all open orders
open_orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN))
print(f'Found {len(open_orders)} open orders to cancel')
print()

cancelled = 0
for order in open_orders:
    try:
        client.cancel_order_by_id(order.id)
        print(f'  CANCELLED: {order.symbol} {order.side.name} {order.qty}')
        cancelled += 1
    except Exception as e:
        print(f'  FAILED: {order.symbol} - {e}')

print()
print(f'Cancelled: {cancelled}/{len(open_orders)} orders')
print()

# Check new buying power
time.sleep(2)
account = client.get_account()
print('='*70)
print('UPDATED ACCOUNT STATUS')
print('='*70)
print(f'Cash: ${float(account.cash):.2f}')
print(f'Buying Power: ${float(account.buying_power):.2f}')
print(f'Portfolio Value: ${float(account.portfolio_value):.2f}')

