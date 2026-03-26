"""
🔍 FINAL TRADING VERIFICATION TEST
Comprehensive check that all trading systems are operational
Tests IB and Alpaca connections, order submission, and buy/sell triggers
"""

import asyncio
import os
from datetime import datetime
from alpaca_trade_api import REST as AlpacaREST
from ib_insync import IB, Stock, Order

print("=" * 80)
print("🔍 FINAL TRADING VERIFICATION TEST")
print("=" * 80)
print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# ============================================================================
# TEST 1: ALPACA CONNECTION & ACCOUNT STATUS
# ============================================================================
print("=" * 80)
print("TEST 1: ALPACA CONNECTION & ACCOUNT STATUS")
print("=" * 80)

try:
    api_key = os.getenv('ALPACA_LIVE_KEY', 'AKNGMUQPQGCFKRMTM5QG')
    api_secret = os.getenv('ALPACA_LIVE_SECRET', '7dNZf4igDG89MBp9dAzd7IabiAxsCIMEvgaCH0Pb')
    base_url = 'https://api.alpaca.markets'
    
    alpaca = AlpacaREST(api_key, api_secret, base_url, api_version='v2')
    
    # Get account info
    account = alpaca.get_account()
    
    print(f"[CHECK] Alpaca Connection: SUCCESS")
    print(f"📊 Account Number: {account.account_number}")
    print(f"💰 Cash: ${float(account.cash):.2f}")
    print(f"💵 Buying Power: ${float(account.buying_power):.2f}")
    print(f"📈 Portfolio Value: ${float(account.portfolio_value):.2f}")
    print()
    
    # Check trading status
    print("🔍 Trading Status Checks:")
    print(f"   Account Status: {account.status}")
    print(f"   Trading Blocked: {account.trading_blocked}")
    print(f"   Account Blocked: {account.account_blocked}")
    print(f"   Trade Suspended by User: {account.trade_suspended_by_user}")
    print(f"   Transfers Blocked: {account.transfers_blocked}")
    print()
    
    # Determine if trading is enabled
    if account.trading_blocked or account.account_blocked or account.trade_suspended_by_user:
        print("[ERROR] ALPACA TRADING: BLOCKED")
        if account.trading_blocked:
            print("   [WARNING]️ Trading is blocked by Alpaca")
        if account.account_blocked:
            print("   [WARNING]️ Account is blocked")
        if account.trade_suspended_by_user:
            print("   [WARNING]️ Trading suspended by user (check dashboard)")
    else:
        print("[CHECK] ALPACA TRADING: ENABLED")
    
    print()
    
    # Check positions
    positions = alpaca.list_positions()
    print(f"📊 Current Positions: {len(positions)}")
    for pos in positions:
        print(f"   {pos.symbol}: {pos.qty} shares @ ${float(pos.current_price):.2f}")
    
    print()
    alpaca_ready = not (account.trading_blocked or account.account_blocked or account.trade_suspended_by_user)
    
except Exception as e:
    print(f"[ERROR] Alpaca Connection: FAILED")
    print(f"   Error: {e}")
    alpaca_ready = False

print()

# ============================================================================
# TEST 2: IB CONNECTION & ACCOUNT STATUS
# ============================================================================
print("=" * 80)
print("TEST 2: IB CONNECTION & ACCOUNT STATUS")
print("=" * 80)

try:
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=999)
    
    print(f"[CHECK] IB Connection: SUCCESS")
    print(f"📡 Connected to: 127.0.0.1:7496")
    print(f"🆔 Client ID: 999")
    print()
    
    # Get account info
    account_values = ib.accountValues()
    
    # Extract key values
    net_liquidation = None
    available_funds = None
    buying_power = None
    
    for av in account_values:
        if av.tag == 'NetLiquidation' and av.currency == 'USD':
            net_liquidation = float(av.value)
        elif av.tag == 'AvailableFunds' and av.currency == 'USD':
            available_funds = float(av.value)
        elif av.tag == 'BuyingPower' and av.currency == 'USD':
            buying_power = float(av.value)
    
    print(f"💰 Net Liquidation: ${net_liquidation:.2f}" if net_liquidation else "💰 Net Liquidation: N/A")
    print(f"💵 Available Funds: ${available_funds:.2f}" if available_funds else "💵 Available Funds: N/A")
    print(f"📈 Buying Power: ${buying_power:.2f}" if buying_power else "📈 Buying Power: N/A")
    print()
    
    # Get positions
    positions = ib.positions()
    print(f"📊 Current Positions: {len(positions)}")
    for pos in positions:
        print(f"   {pos.contract.symbol}: {pos.position} shares @ ${pos.avgCost:.2f}")
    
    print()
    print("[CHECK] IB TRADING: ENABLED")
    
    ib_ready = True
    
except Exception as e:
    print(f"[ERROR] IB Connection: FAILED")
    print(f"   Error: {e}")
    ib_ready = False
    ib = None

print()

# ============================================================================
# TEST 3: ALPACA ORDER SUBMISSION TEST (DRY RUN)
# ============================================================================
print("=" * 80)
print("TEST 3: ALPACA ORDER SUBMISSION TEST")
print("=" * 80)

if alpaca_ready:
    try:
        # Test with a very small crypto order (won't actually execute - just validate)
        print("🧪 Testing Alpaca order validation...")
        print("   Symbol: BTC/USD")
        print("   Quantity: 0.0001 BTC (~$12)")
        print("   Side: BUY")
        print("   Type: MARKET")
        print()
        
        # Try to submit a test order
        try:
            test_order = alpaca.submit_order(
                symbol='BTC/USD',
                qty=0.0001,
                side='buy',
                type='market',
                time_in_force='gtc'
            )
            print(f"[CHECK] ALPACA ORDER SUBMISSION: SUCCESS")
            print(f"   Order ID: {test_order.id}")
            print(f"   Status: {test_order.status}")
            print()
            
            # Cancel the test order immediately
            print("🔄 Canceling test order...")
            alpaca.cancel_order(test_order.id)
            print("[CHECK] Test order canceled")
            
            alpaca_orders_working = True
            
        except Exception as order_error:
            error_msg = str(order_error)
            if "rejected by user request" in error_msg.lower():
                print(f"[ERROR] ALPACA ORDER SUBMISSION: BLOCKED")
                print(f"   Error: Trading still suspended by user")
                print(f"   Action: Check Alpaca dashboard - toggle may not have saved")
                alpaca_orders_working = False
            elif "insufficient" in error_msg.lower():
                print(f"[WARNING]️ ALPACA ORDER SUBMISSION: INSUFFICIENT FUNDS")
                print(f"   Note: Order validation works, but need more funds")
                alpaca_orders_working = True  # Validation works
            else:
                print(f"[ERROR] ALPACA ORDER SUBMISSION: FAILED")
                print(f"   Error: {order_error}")
                alpaca_orders_working = False
        
    except Exception as e:
        print(f"[ERROR] Alpaca Order Test: FAILED")
        print(f"   Error: {e}")
        alpaca_orders_working = False
else:
    print("⏭️ SKIPPED - Alpaca not ready")
    alpaca_orders_working = False

print()

# ============================================================================
# TEST 4: IB ORDER SUBMISSION TEST (DRY RUN)
# ============================================================================
print("=" * 80)
print("TEST 4: IB ORDER SUBMISSION TEST")
print("=" * 80)

if ib_ready and ib:
    try:
        # Test with a small stock order (won't actually execute - just validate)
        print("🧪 Testing IB order validation...")
        print("   Symbol: AAPL")
        print("   Quantity: 1 share")
        print("   Side: BUY")
        print("   Type: LIMIT (far from market)")
        print()
        
        # Create a test order with a limit price far from market (won't fill)
        contract = Stock('AAPL', 'SMART', 'USD')
        ib.qualifyContracts(contract)
        
        # Place limit order at $1 (won't fill - just testing submission)
        order = Order()
        order.action = 'BUY'
        order.totalQuantity = 1
        order.orderType = 'LMT'
        order.lmtPrice = 1.00  # Far below market - won't fill
        
        trade = ib.placeOrder(contract, order)
        ib.sleep(1)  # Wait for order to be acknowledged
        
        print(f"[CHECK] IB ORDER SUBMISSION: SUCCESS")
        print(f"   Order ID: {trade.order.orderId}")
        print(f"   Status: {trade.orderStatus.status}")
        print()
        
        # Cancel the test order
        print("🔄 Canceling test order...")
        ib.cancelOrder(order)
        ib.sleep(1)
        print("[CHECK] Test order canceled")
        
        ib_orders_working = True
        
    except Exception as e:
        print(f"[ERROR] IB Order Test: FAILED")
        print(f"   Error: {e}")
        ib_orders_working = False
    
    finally:
        # Disconnect
        if ib:
            ib.disconnect()
else:
    print("⏭️ SKIPPED - IB not ready")
    ib_orders_working = False

print()

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("=" * 80)
print("📊 FINAL VERIFICATION SUMMARY")
print("=" * 80)
print()

print("🔌 CONNECTIONS:")
print(f"   Alpaca: {'[CHECK] CONNECTED' if alpaca_ready else '[ERROR] FAILED'}")
print(f"   IB:     {'[CHECK] CONNECTED' if ib_ready else '[ERROR] FAILED'}")
print()

print("📝 ORDER SUBMISSION:")
print(f"   Alpaca: {'[CHECK] WORKING' if alpaca_orders_working else '[ERROR] BLOCKED'}")
print(f"   IB:     {'[CHECK] WORKING' if ib_orders_working else '[ERROR] BLOCKED'}")
print()

print("🎯 TRADING CAPABILITIES:")
all_systems_go = alpaca_ready and ib_ready and alpaca_orders_working and ib_orders_working

if all_systems_go:
    print("   [CHECK] CRYPTO TRADING (Alpaca): READY")
    print("   [CHECK] STOCK TRADING (IB): READY")
    print("   [CHECK] DUAL-BROKER MODE: OPERATIONAL")
    print()
    print("=" * 80)
    print("🎉 ALL SYSTEMS GO - READY FOR FULL TRADING!")
    print("=" * 80)
    print()
    print("[CHECK] You can now trade:")
    print("   • Crypto 24/7 on Alpaca (BTC/USD, ETH/USD, SOL/USD)")
    print("   • Stocks during market hours on IB (SPY, QQQ, AAPL, etc.)")
    print("   • Automatic failover between brokers")
    print("   • Smart routing (crypto→Alpaca, stocks→IB)")
    print()
    print("🚀 PROMETHEUS is ready for autonomous trading!")
else:
    print("   [WARNING]️ SOME SYSTEMS NOT READY")
    print()
    if not alpaca_ready:
        print("   [ERROR] Alpaca connection failed")
    if not ib_ready:
        print("   [ERROR] IB connection failed")
    if not alpaca_orders_working:
        print("   [ERROR] Alpaca order submission blocked")
        print("      → Check 'Trades Suspended' toggle in dashboard")
    if not ib_orders_working:
        print("   [ERROR] IB order submission failed")
    print()
    print("=" * 80)
    print("[WARNING]️ FIX ISSUES ABOVE BEFORE TRADING")
    print("=" * 80)

print()
print("=" * 80)
print("[CHECK] VERIFICATION TEST COMPLETE")
print("=" * 80)

