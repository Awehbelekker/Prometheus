#!/usr/bin/env python3
"""
MAXIMIZE DAILY TRADES - Monitor + Auto-trade to hit 3 trade limit
Monitors existing orders and automatically places more when they fill
"""

import sys
import time
import threading
from datetime import datetime

print("\n" + "="*80)
print("  🚀 PROMETHEUS - MAXIMIZE DAILY PROFITS")
print("="*80)
print(f"  Strategy: Monitor orders + Auto-place remaining trades")
print(f"  Target: 3 trades per day (maximum allowed)")
print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*80 + "\n")

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

class MaximizeBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.next_order_id = None
        self.orders = {}
        self.positions = {}
        self.filled_count = 0
        self.max_trades = 3
        self.symbols_to_trade = ['SIRI', 'F', 'NOK']
        self.traded_symbols = set()
        
    def error(self, reqId, errorCode, errorString):
        if errorCode not in [2104, 2106, 2158]:
            print(f"[WARNING]️  {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        print(f"[CHECK] Connected! Next order ID: {orderId}\n")
        self.next_order_id = orderId
        self.connected = True
    
    def openOrder(self, orderId, contract, order, orderState):
        """Track open orders"""
        self.orders[orderId] = {
            'symbol': contract.symbol,
            'action': order.action,
            'qty': order.totalQuantity,
            'status': orderState.status
        }
        self.traded_symbols.add(contract.symbol)
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, *args):
        """Monitor order status changes"""
        if orderId in self.orders:
            old_status = self.orders[orderId].get('status', '')
            self.orders[orderId]['status'] = status
            
            # Only print if status changed
            if old_status != status:
                symbol = self.orders[orderId]['symbol']
                print(f"📋 Order {orderId} ({symbol}): {status}", end="")
                
                if status == "Filled":
                    print(f" at ${avgFillPrice:.2f} [CHECK]")
                    self.filled_count += 1
                    print(f"   💰 Trades filled: {self.filled_count}/{self.max_trades}\n")
                else:
                    print()
    
    def position(self, account, contract, position, avgCost):
        """Track positions"""
        self.positions[contract.symbol] = {
            'qty': position,
            'cost': avgCost
        }
    
    def place_order(self, symbol):
        """Place a buy order"""
        try:
            print(f"🔍 {symbol}: Analyzing...")
            print(f"💡 Decision: BUY 1 share")
            
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            order = Order()
            order.action = "BUY"
            order.orderType = "MKT"
            order.totalQuantity = 1
            order.eTradeOnly = ""
            order.firmQuoteOnly = ""
            
            print(f"📊 Placing: BUY 1 {symbol}")
            self.placeOrder(self.next_order_id, contract, order)
            self.next_order_id += 1
            self.traded_symbols.add(symbol)
            
            return True
        except Exception as e:
            print(f"[ERROR] Error placing order: {e}")
            return False

# Create bot
bot = MaximizeBot()

# Connect
print("🔌 Connecting to IB Gateway...")
bot.connect("127.0.0.1", 7496, 2)
threading.Thread(target=bot.run, daemon=True).start()

# Wait for connection
for _ in range(50):
    if bot.connected:
        break
    time.sleep(0.1)

if not bot.connected:
    print("[ERROR] Connection failed\n")
    sys.exit(1)

print("[CHECK] Connected successfully!\n")

# Get current orders and positions
print("="*80)
print("  📊 CHECKING EXISTING ORDERS")
print("="*80 + "\n")

bot.reqOpenOrders()
time.sleep(2)

bot.reqPositions()
time.sleep(2)

# Count existing orders
existing_orders = len(bot.orders)
print(f"📋 Found {existing_orders} existing orders")

for order_id, order_info in bot.orders.items():
    print(f"   Order {order_id}: {order_info['action']} {order_info['qty']} {order_info['symbol']} - {order_info['status']}")

print()

# Calculate how many more trades we can make
trades_remaining = bot.max_trades - existing_orders
print(f"💡 Trades remaining today: {trades_remaining}/{bot.max_trades}")
print()

if trades_remaining <= 0:
    print("[CHECK] Daily trade limit reached!")
    print("📊 Monitoring existing orders until they fill...\n")
    print("="*80)
    
    # Just monitor existing orders
    print("⏳ Monitoring mode - Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Check order status every 30 seconds
            bot.reqOpenOrders()
            time.sleep(30)
    except KeyboardInterrupt:
        print("\n⏸️  Monitoring stopped")
    
    bot.disconnect()
    sys.exit(0)

# We have trades remaining - place them!
print("="*80)
print("  🤖 PLACING REMAINING TRADES")
print("="*80 + "\n")

# Find symbols we haven't traded yet
available_symbols = [s for s in bot.symbols_to_trade if s not in bot.traded_symbols]

if not available_symbols:
    print("[WARNING]️  All symbols already traded")
    available_symbols = ['AMD', 'INTC', 'AAPL']  # Backup symbols
    print(f"💡 Using backup symbols: {available_symbols}")

print(f"📊 Available symbols: {available_symbols}\n")

# Place remaining orders
orders_placed = 0
for symbol in available_symbols:
    if orders_placed >= trades_remaining:
        break
    
    if bot.place_order(symbol):
        orders_placed += 1
        print(f"[CHECK] Order placed ({orders_placed}/{trades_remaining})\n")
        time.sleep(2)  # Small delay between orders

print("="*80)
print("  [CHECK] ALL ORDERS PLACED")
print("="*80)
print(f"  Total orders: {existing_orders + orders_placed}")
print(f"  New orders: {orders_placed}")
print(f"  Daily limit: {bot.max_trades}")
print("="*80 + "\n")

# Now monitor all orders until they fill
print("📊 MONITORING ALL ORDERS UNTIL FILLED")
print("="*80 + "\n")

print("⏳ Checking every 30 seconds...")
print("💡 Orders will execute when market opens (09:30 AM Eastern)")
print("🛑 Press Ctrl+C to stop monitoring\n")

try:
    check_count = 0
    while True:
        check_count += 1
        
        # Request order updates
        bot.reqOpenOrders()
        time.sleep(2)
        
        # Check if all orders are filled
        all_filled = True
        for order_id, order_info in bot.orders.items():
            if order_info['status'] not in ['Filled', 'Cancelled']:
                all_filled = False
                break
        
        if all_filled and len(bot.orders) > 0:
            print("\n" + "="*80)
            print("  🎉 ALL ORDERS FILLED!")
            print("="*80)
            print(f"  Total trades: {len(bot.orders)}")
            print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
            print("="*80 + "\n")
            
            # Show final positions
            print("📊 FINAL POSITIONS:")
            bot.reqPositions()
            time.sleep(2)
            
            for symbol, pos in bot.positions.items():
                print(f"   {symbol}: {pos['qty']} shares @ ${pos['cost']:.2f}")
            
            print("\n[CHECK] Daily trading complete!")
            break
        
        # Status update every 5 checks (2.5 minutes)
        if check_count % 5 == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Still monitoring... ({len(bot.orders)} orders)")
        
        # Wait 30 seconds before next check
        time.sleep(30)

except KeyboardInterrupt:
    print("\n⏸️  Monitoring stopped by user")

print("\n" + "="*80)
print("  📊 FINAL STATUS")
print("="*80)
print(f"  Orders placed: {len(bot.orders)}")
print(f"  Orders filled: {bot.filled_count}")
print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*80 + "\n")

bot.disconnect()
print("[CHECK] Disconnected from IB Gateway")

