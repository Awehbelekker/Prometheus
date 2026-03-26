#!/usr/bin/env python3
"""LIVE TRADING - STARTS IMMEDIATELY"""
import sys, time, threading
from datetime import datetime

print("\n" + "="*80)
print("  🚀 PROMETHEUS LIVE TRADING - STARTING NOW")
print("="*80)
print(f"  Account: U21922116 | Capital: $250 | Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*80 + "\n")

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

class Bot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.next_order_id = None
        self.trades = 0
        
    def error(self, reqId, errorCode, errorString):
        if errorCode not in [2104, 2106, 2158]:
            print(f"[WARNING]️  {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        print(f"[CHECK] CONNECTED! Order ID: {orderId}\n")
        self.next_order_id = orderId
        self.connected = True
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, *args):
        print(f"📋 Order {orderId}: {status}", end="")
        if status == "Filled":
            print(f" at ${avgFillPrice:.2f} [CHECK]")
            self.trades += 1
        else:
            print()

bot = Bot()
print("🔌 Connecting...")
bot.connect("127.0.0.1", 7496, 2)
threading.Thread(target=bot.run, daemon=True).start()

for _ in range(50):
    if bot.connected: break
    time.sleep(0.1)

if not bot.connected:
    print("[ERROR] Connection failed\n")
    sys.exit(1)

print("🤖 AUTONOMOUS TRADING ACTIVE\n")
print("="*80)

symbols = ['SIRI', 'F']
max_trades = 3

for symbol in symbols:
    if bot.trades >= max_trades:
        break
    
    print(f"\n🔍 {symbol}: Analyzing...")
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
    # Explicitly disable these attributes
    order.eTradeOnly = ""
    order.firmQuoteOnly = ""

    print(f"📊 Placing: BUY 1 {symbol}")
    bot.placeOrder(bot.next_order_id, contract, order)
    bot.next_order_id += 1
    
    print("⏳ Waiting for fill...")
    time.sleep(15)

print("\n" + "="*80)
print(f"  [CHECK] SESSION COMPLETE | Trades: {bot.trades} | Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*80 + "\n")

bot.disconnect()

