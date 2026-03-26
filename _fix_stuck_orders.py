#!/usr/bin/env python3
"""Fix stuck orders and sell AMD at stop loss"""
import alpaca_trade_api as tradeapi
import os
import time
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  FIX STUCK ORDERS & EXECUTE STOP LOSS")
print("=" * 70)

# Step 1: Cancel ALL open orders
print("\n1. Cancelling ALL open orders...")
orders = api.list_orders(status='open')
print(f"   Found {len(orders)} open orders")

for o in orders:
    print(f"   Cancelling {o.symbol} {o.side} order {o.id[:8]}...")
    try:
        api.cancel_order(o.id)
        print(f"   ✅ Cancelled")
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Wait for cancels to process
print("\n2. Waiting for cancels to process...")
time.sleep(3)

# Step 2: Check open orders again
orders = api.list_orders(status='open')
print(f"   Open orders after cancel: {len(orders)}")

# Step 3: Get AMD position
print("\n3. Getting AMD position...")
positions = api.list_positions()
amd_pos = [p for p in positions if p.symbol == 'AMD']

if not amd_pos:
    print("   AMD position not found - may have already been sold")
else:
    p = amd_pos[0]
    qty = float(p.qty)
    current = float(p.current_price)
    entry = float(p.avg_entry_price)
    pnl_pct = float(p.unrealized_plpc) * 100
    
    print(f"   AMD: {qty} shares @ ${entry:.2f}")
    print(f"   Current: ${current:.2f}")
    print(f"   P/L: {pnl_pct:.2f}%")
    
    # Step 4: Try to sell with aggressive limit price
    print("\n4. Submitting stop loss sell order...")
    
    # Get latest quote for bid price
    try:
        quote = api.get_latest_quote('AMD')
        bid = float(quote.bp) if hasattr(quote, 'bp') and quote.bp else current * 0.95
        ask = float(quote.ap) if hasattr(quote, 'ap') and quote.ap else current * 1.05
        print(f"   Current bid: ${bid:.2f}, ask: ${ask:.2f}")
        
        # Use bid price (this is what buyers are willing to pay)
        # Slightly below bid to ensure fill
        limit_price = round(bid * 0.99, 2)
        print(f"   Using limit price: ${limit_price:.2f} (1% below bid)")
        
    except Exception as e:
        print(f"   Could not get quote: {e}")
        limit_price = round(current * 0.95, 2)
        print(f"   Using fallback limit price: ${limit_price:.2f}")
    
    try:
        order = api.submit_order(
            symbol='AMD',
            qty=qty,
            side='sell',
            type='limit',
            time_in_force='gtc',  # Good till cancelled
            limit_price=limit_price,
            extended_hours=True
        )
        print(f"\n   ✅ ORDER SUBMITTED!")
        print(f"   Order ID: {order.id}")
        print(f"   Status: {order.status}")
        print(f"   Limit: ${limit_price:.2f}")
        
    except Exception as e:
        print(f"\n   ❌ SELL FAILED: {e}")
        
        # If market order allowed, try that
        print("\n5. Trying market order (may only work during market hours)...")
        try:
            order = api.submit_order(
                symbol='AMD',
                qty=qty,
                side='sell',
                type='market',
                time_in_force='day'
            )
            print(f"   ✅ Market order submitted: {order.id}")
        except Exception as e2:
            print(f"   ❌ Market order also failed: {e2}")
            print("\n   The order will need to wait until market opens")

print("\n" + "=" * 70)
print("FINAL STATUS:")
print("=" * 70)

# Final check
orders = api.list_orders(status='open')
print(f"\nOpen orders: {len(orders)}")
for o in orders:
    print(f"  {o.symbol} {o.side}: {o.status} @ ${o.limit_price if o.limit_price else 'market'}")

positions = api.list_positions()
print(f"\nPositions: {len(positions)}")

