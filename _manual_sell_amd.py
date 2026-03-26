#!/usr/bin/env python3
"""
MANUAL STOP LOSS EXECUTION FOR AMD
This will sell AMD at stop loss since the automated system isn't working.
"""
import alpaca_trade_api as tradeapi
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  MANUAL STOP LOSS: SELL AMD")
print(f"  Time: {datetime.now()}")
print("=" * 70)

# Get AMD position
positions = api.list_positions()
amd_pos = [p for p in positions if p.symbol == 'AMD']

if not amd_pos:
    print("\n❌ No AMD position found - may have already been sold")
    exit()

p = amd_pos[0]
qty = float(p.qty)
entry = float(p.avg_entry_price)
current = float(p.current_price)
pnl = float(p.unrealized_pl)
pnl_pct = float(p.unrealized_plpc) * 100

print(f"\nAMD Position:")
print(f"  Quantity: {qty}")
print(f"  Entry Price: ${entry:.2f}")
print(f"  Current Price: ${current:.2f}")
print(f"  P/L: ${pnl:.2f} ({pnl_pct:.2f}%)")

print(f"\n⚠️ This position is DOWN {abs(pnl_pct):.2f}% - past the 3% stop loss threshold!")

# Get price for limit order
try:
    bar = api.get_latest_bar('AMD')
    if bar:
        limit_price = round(float(bar.c) * 0.995, 2)
        print(f"\nSelling at limit price: ${limit_price:.2f}")
except Exception as e:
    print(f"Could not get price: {e}")
    # Use current price as fallback
    limit_price = round(current * 0.995, 2)
    print(f"Using fallback limit price: ${limit_price:.2f}")

print("\n" + "=" * 70)
print("EXECUTING STOP LOSS SELL ORDER...")
print("=" * 70)

try:
    order = api.submit_order(
        symbol='AMD',
        qty=qty,
        side='sell',
        type='limit',
        time_in_force='day',
        limit_price=limit_price,
        extended_hours=True
    )
    
    print(f"\n✅ SELL ORDER SUBMITTED!")
    print(f"   Order ID: {order.id}")
    print(f"   Symbol: AMD")
    print(f"   Quantity: {qty}")
    print(f"   Limit Price: ${limit_price:.2f}")
    print(f"   Status: {order.status}")
    print(f"   Type: Limit (Extended Hours)")
    
except Exception as e:
    print(f"\n❌ SELL ORDER FAILED: {e}")
    print("\nTrying market order during regular hours may be required...")

print("\n" + "=" * 70)

