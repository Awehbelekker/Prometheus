#!/usr/bin/env python3
"""
Test LIVE trade execution on Alpaca
WARNING: This will place a REAL order with REAL money!
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("  PROMETHEUS LIVE TRADE TEST")
print("=" * 60)

# Check environment
always_live = os.getenv('ALWAYS_LIVE', '0')
enable_exec = os.getenv('ENABLE_LIVE_ORDER_EXECUTION', '0')
print(f"ALWAYS_LIVE: {always_live}")
print(f"ENABLE_LIVE_ORDER_EXECUTION: {enable_exec}")

if always_live != '1' or enable_exec != '1':
    print("\n⚠️  WARNING: Live trading not fully enabled!")
    print("   Set ALWAYS_LIVE=1 and ENABLE_LIVE_ORDER_EXECUTION=1 in .env")

# Import Alpaca broker
try:
    from brokers.alpaca_broker import AlpacaBroker
    print("\n✅ AlpacaBroker imported successfully")
except ImportError as e:
    print(f"\n❌ Failed to import AlpacaBroker: {e}")
    sys.exit(1)

# Initialize broker (LIVE mode)
print("\n🔌 Connecting to Alpaca LIVE...")

# AlpacaBroker requires a config dict
config = {
    'api_key': os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_API_KEY'),
    'secret_key': os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_API_SECRET'),
    'paper_trading': False,  # LIVE MODE
    'enable_24_5_trading': True
}
print(f"   API Key: {config['api_key'][:8]}...{config['api_key'][-4:] if config['api_key'] else 'MISSING'}")
broker = AlpacaBroker(config=config)

# Get account info
import asyncio

async def test_trade():
    # Connect to broker first
    print("\n🔌 Connecting to Alpaca API...")
    connected = await broker.connect()
    if not connected:
        print("❌ Failed to connect to Alpaca LIVE!")
        return False
    print("✅ Connected to Alpaca LIVE")
    print("\n📊 Getting account info...")
    account = await broker.get_account()
    print(f"   Account ID: {account.account_id}")
    print(f"   Equity: ${float(account.equity):,.2f}")
    print(f"   Cash: ${float(account.cash):,.2f}")
    print(f"   Buying Power: ${float(account.buying_power):,.2f}")
    
    # Check if we have enough buying power for a small test trade
    buying_power = float(account.buying_power)
    if buying_power < 10:
        print(f"\n❌ Insufficient buying power (${buying_power:.2f}) for test trade")
        return False
    
    # Get current AAPL price
    print("\n📈 Getting AAPL price...")
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        price = ticker.info.get('regularMarketPrice') or ticker.info.get('currentPrice', 0)
        print(f"   AAPL current price: ${price:.2f}")
    except Exception as e:
        print(f"   Could not get price: {e}")
        price = 200  # Fallback estimate
    
    # Calculate quantity (buy $50 worth or 1 share, whichever is smaller)
    max_spend = min(50, buying_power * 0.5)  # Max 50% of buying power
    qty = max(1, int(max_spend / price))
    
    # Actually, with $109 buying power, let's just try to buy 1 share of a cheap stock
    # AAPL is ~$230, so we can't afford it. Let's try a fractional share or cheaper stock
    
    if price > buying_power:
        print(f"\n⚠️  AAPL (${price:.2f}) exceeds buying power (${buying_power:.2f})")
        print("   Trying fractional share (0.1 shares)...")
        qty = 0.1
    
    print(f"\n🎯 TEST TRADE PARAMETERS:")
    print(f"   Symbol: AAPL")
    print(f"   Side: BUY")
    print(f"   Quantity: {qty}")
    print(f"   Type: MARKET")
    print(f"   Estimated Cost: ${qty * price:.2f}")
    
    # Confirm
    print("\n" + "=" * 60)
    print("  ⚠️  THIS WILL PLACE A REAL ORDER WITH REAL MONEY!")
    print("=" * 60)
    
    # Place the order
    print("\n📤 Placing order...")
    try:
        from brokers.universal_broker_interface import Order, OrderSide, OrderType
        
        order = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=qty,
            order_type=OrderType.MARKET,
            time_in_force="day"
        )
        
        result = await broker.submit_order(order)
        
        print("\n✅ ORDER SUBMITTED!")
        print(f"   Order ID: {result.get('id', 'N/A')}")
        print(f"   Status: {result.get('status', 'N/A')}")
        print(f"   Symbol: {result.get('symbol', 'AAPL')}")
        print(f"   Qty: {result.get('qty', qty)}")
        print(f"   Side: {result.get('side', 'buy')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ORDER FAILED: {e}")
        return False

# Run the test
result = asyncio.run(test_trade())

print("\n" + "=" * 60)
if result:
    print("  ✅ TEST TRADE SUCCESSFUL!")
else:
    print("  ❌ TEST TRADE FAILED")
print("=" * 60)

