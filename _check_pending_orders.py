#!/usr/bin/env python3
"""Check for pending orders that might be blocking sells"""
import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  PENDING ORDERS CHECK")
print("=" * 70)

# Get all open/pending orders
orders = api.list_orders(status='open')
print(f"\nOpen orders: {len(orders)}")

if orders:
    for o in orders:
        print(f"\n  Order ID: {o.id}")
        print(f"  Symbol: {o.symbol}")
        print(f"  Side: {o.side}")
        print(f"  Qty: {o.qty}")
        print(f"  Type: {o.type}")
        print(f"  Status: {o.status}")
        print(f"  Submitted: {o.submitted_at}")
        if o.limit_price:
            print(f"  Limit Price: ${o.limit_price}")
else:
    print("  (No open orders)")

# Check for AMD specifically
amd_orders = [o for o in orders if o.symbol == 'AMD']
print(f"\n" + "=" * 70)
print(f"AMD Orders: {len(amd_orders)}")
if amd_orders:
    for o in amd_orders:
        print(f"\n  *** AMD ORDER FOUND ***")
        print(f"  Order ID: {o.id}")
        print(f"  Side: {o.side}")
        print(f"  Status: {o.status}")
        print(f"  This is likely blocking new sell orders!")
else:
    print("  No AMD orders found")

# If there are AMD orders, offer to cancel them
if amd_orders:
    print("\n" + "=" * 70)
    print("RECOMMENDATION: Cancel the pending AMD order(s)")
    print("=" * 70)
    
    for o in amd_orders:
        print(f"\nCancelling AMD order {o.id}...")
        try:
            api.cancel_order(o.id)
            print(f"  ✅ Cancelled!")
        except Exception as e:
            print(f"  ❌ Failed: {e}")

print("\n" + "=" * 70)

