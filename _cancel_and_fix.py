#!/usr/bin/env python3
"""Cancel stuck orders and check buying power after."""
import os
from dotenv import load_dotenv
load_dotenv()
import requests

key = os.getenv('ALPACA_API_KEY')
secret = os.getenv('ALPACA_SECRET_KEY')
base = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
h = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}

# Get open/accepted orders
r = requests.get(f'{base}/v2/orders?status=open', headers=h, timeout=10)
orders = r.json()
print(f"Found {len(orders)} open orders:")
for o in orders:
    oid = o["id"]
    sym = o["symbol"]
    side = o["side"]
    qty = o["qty"]
    status = o["status"]
    created = o["created_at"][:19]
    print(f"  ID: {oid}  {sym} {side} qty={qty} status={status} created={created}")

# Cancel all open orders
if orders:
    print("\nCancelling all open orders...")
    r2 = requests.delete(f'{base}/v2/orders', headers=h, timeout=10)
    print(f"Cancel response: {r2.status_code}")
    
    import time
    time.sleep(2)
    
    # Verify cancellation
    r3 = requests.get(f'{base}/v2/orders?status=open', headers=h, timeout=10)
    remaining = r3.json()
    print(f"Remaining open orders: {len(remaining)}")
else:
    print("No orders to cancel")

# Check account after
print("\n--- ACCOUNT AFTER CANCELLATION ---")
acct = requests.get(f'{base}/v2/account', headers=h, timeout=10).json()
print(f"Equity:       ${float(acct['equity']):.2f}")
print(f"Cash:         ${float(acct['cash']):.2f}")
print(f"Buying Power: ${float(acct['buying_power']):.2f}")
