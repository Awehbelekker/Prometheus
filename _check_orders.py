#!/usr/bin/env python3
"""Check Alpaca orders directly"""
import os
from dotenv import load_dotenv
load_dotenv()

import alpaca_trade_api as tradeapi

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')

print(f"Using API Key: {api_key[:8]}...{api_key[-4:]}")
print(f"Base URL: https://api.alpaca.markets")

api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("\n📊 Account Info:")
account = api.get_account()
print(f"   Account ID: {account.account_number}")
print(f"   Equity: ${float(account.equity):,.2f}")
print(f"   Cash: ${float(account.cash):,.2f}")
print(f"   Buying Power: ${float(account.buying_power):,.2f}")

print("\n📋 Recent Orders:")
orders = api.list_orders(status='all', limit=10)
if orders:
    for order in orders:
        print(f"   {order.id[:8]}... | {order.symbol} | {order.side} | {order.qty} | {order.status} | {order.created_at}")
else:
    print("   No orders found")

print("\n📈 Current Positions:")
positions = api.list_positions()
if positions:
    for pos in positions:
        print(f"   {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f} (P/L: ${float(pos.unrealized_pl):.2f})")
else:
    print("   No open positions")

