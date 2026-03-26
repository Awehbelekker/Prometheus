#!/usr/bin/env python3
"""Test selling AMD to diagnose why stop loss isn't working"""
import alpaca_trade_api as tradeapi
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY')
secret_key = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET')
api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets')

print("=" * 70)
print("  TEST: SELL AMD (diagnose stop loss failure)")
print(f"  Time: {datetime.now()}")
print("=" * 70)

# Check if market is open
clock = api.get_clock()
print(f"\nMarket Status:")
print(f"  Is Open: {clock.is_open}")
print(f"  Next Open: {clock.next_open}")
print(f"  Next Close: {clock.next_close}")

# Get AMD position
positions = api.list_positions()
amd_pos = [p for p in positions if p.symbol == 'AMD']

if not amd_pos:
    print("\n❌ No AMD position found")
    exit()

p = amd_pos[0]
qty = float(p.qty)
print(f"\nAMD Position:")
print(f"  Quantity: {qty}")
print(f"  P/L: {float(p.unrealized_plpc)*100:.2f}%")

# Test getting latest bar (required for extended hours limit order)
print("\n1. Testing get_latest_bar for AMD...")
try:
    bar = api.get_latest_bar('AMD')
    if bar:
        price = float(bar.c)
        print(f"   ✅ Got latest bar: price=${price:.2f}")
    else:
        print("   ⚠️ Bar is None")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test getting latest quote instead
print("\n2. Testing get_latest_quote for AMD...")
try:
    quote = api.get_latest_quote('AMD')
    if quote:
        bid = float(quote.bp) if hasattr(quote, 'bp') else 0
        ask = float(quote.ap) if hasattr(quote, 'ap') else 0
        print(f"   ✅ Got latest quote: bid=${bid:.2f}, ask=${ask:.2f}")
    else:
        print("   ⚠️ Quote is None")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check 24hr stock list
ALPACA_24HR_STOCKS = {'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX', 'AMD'}
print(f"\n3. Is AMD a 24-hour stock? {'Yes' if 'AMD' in ALPACA_24HR_STOCKS else 'No'}")

# Try submitting a test sell order (SIMULATION - don't actually execute)
print("\n4. Simulating sell order logic...")

is_crypto = '/' in 'AMD' or 'AMD'.endswith('USD')
is_24hr_stock = not is_crypto and ('AMD' in ALPACA_24HR_STOCKS)
extended_hours = is_24hr_stock

print(f"   is_crypto: {is_crypto}")
print(f"   is_24hr_stock: {is_24hr_stock}")
print(f"   extended_hours: {extended_hours}")

if extended_hours:
    print("   Extended hours mode: Need limit order")
    try:
        bar = api.get_latest_bar('AMD')
        if bar:
            current_price = float(bar.c)
            limit_price = round(current_price * 0.995, 2)  # 0.5% below
            print(f"   Limit price would be: ${limit_price:.2f}")
        else:
            print("   ❌ FAILURE POINT: bar is None, cannot get limit price!")
    except Exception as e:
        print(f"   ❌ FAILURE POINT: {e}")
else:
    print("   Market order mode")

print("\n" + "=" * 70)
print("DIAGNOSIS:")
print("-" * 70)

# Actually attempt a real sell
print("\n*** Would you like to manually sell AMD now? ***")
print("(This will execute a real sell order)")
response = input("Type 'SELL' to proceed: ")

if response == 'SELL':
    print("\nAttempting to sell AMD...")
    try:
        # Get current price for limit order
        bar = api.get_latest_bar('AMD')
        if bar:
            current_price = float(bar.c)
            limit_price = round(current_price * 0.995, 2)
            
            order = api.submit_order(
                symbol='AMD',
                qty=qty,
                side='sell',
                type='limit',
                time_in_force='day',
                limit_price=limit_price,
                extended_hours=True
            )
            print(f"✅ SELL order submitted!")
            print(f"   Order ID: {order.id}")
            print(f"   Status: {order.status}")
        else:
            print("❌ Could not get price for limit order")
    except Exception as e:
        print(f"❌ Sell failed: {e}")
else:
    print("\nSkipped - no sell executed")

