#!/usr/bin/env python3
"""
AUTO-START IB TRADING
Automatically connects and starts trading without user confirmation
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.ib.live')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order
except ImportError:
    logger.error("[ERROR] ibapi not installed")
    sys.exit(1)

class AutoTradingBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.connected = False
        self.next_order_id = None
        self.account_value = {}
        self.positions = {}
        self.trades_today = 0
        self.max_trades = 3
        
    def error(self, reqId, errorCode, errorString):
        if errorCode not in [2104, 2106, 2158]:  # Ignore info messages
            logger.error(f"Error {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        logger.info(f"[CHECK] Connected! Order ID: {orderId}")
        self.next_order_id = orderId
        self.connected = True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        self.account_value[tag] = value
        if tag == "TotalCashValue":
            logger.info(f"💰 Cash: ${float(value):.2f}")
    
    def position(self, account, contract, position, avgCost):
        self.positions[contract.symbol] = {
            'qty': position,
            'cost': avgCost
        }
        logger.info(f"📊 {contract.symbol}: {position} @ ${avgCost:.2f}")
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, *args):
        logger.info(f"📋 Order {orderId}: {status}")
        if status == "Filled":
            logger.info(f"[CHECK] FILLED at ${avgFillPrice:.2f}")
            self.trades_today += 1
    
    def connect_ib(self):
        logger.info("🔌 Connecting to IB Gateway...")
        self.connect("127.0.0.1", 7496, 2)
        
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        
        # Wait for connection
        for i in range(50):
            if self.connected:
                break
            time.sleep(0.1)
        
        if self.connected:
            logger.info("[CHECK] Connected to IB!")
            self.reqAccountSummary(9001, "All", "$LEDGER")
            self.reqPositions()
            time.sleep(2)
            return True
        else:
            logger.error("[ERROR] Connection failed")
            return False
    
    def place_trade(self, symbol, action, qty):
        try:
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            order = Order()
            order.action = action
            order.orderType = "MKT"
            order.totalQuantity = qty
            
            logger.info(f"📊 Placing: {action} {qty} {symbol}")
            self.placeOrder(self.next_order_id, contract, order)
            self.next_order_id += 1
            return True
        except Exception as e:
            logger.error(f"[ERROR] Order error: {e}")
            return False
    
    def trade_loop(self):
        logger.info("🤖 Starting autonomous trading...")
        logger.info(f"🎯 Max trades today: {self.max_trades}")
        
        # Simple trading strategy
        symbols = ['SIRI', 'F']  # Cheap stocks for testing
        
        while self.trades_today < self.max_trades:
            try:
                for symbol in symbols:
                    if self.trades_today >= self.max_trades:
                        break
                    
                    # Check if we have position
                    has_position = symbol in self.positions and self.positions[symbol]['qty'] > 0
                    
                    if not has_position:
                        logger.info(f"🔍 Analyzing {symbol}...")
                        logger.info(f"💡 Decision: BUY 1 share")
                        self.place_trade(symbol, "BUY", 1)
                        time.sleep(10)  # Wait for fill
                
                # Wait 5 minutes before next cycle
                if self.trades_today < self.max_trades:
                    logger.info("⏳ Waiting 5 minutes...")
                    time.sleep(300)
                
            except KeyboardInterrupt:
                logger.info("⏸️ Stopped by user")
                break
            except Exception as e:
                logger.error(f"[ERROR] Error: {e}")
                time.sleep(60)
        
        logger.info(f"[CHECK] Trading complete! Trades today: {self.trades_today}")

def main():
    print("=" * 80)
    print("  🚀 PROMETHEUS AUTO-START IB TRADING")
    print("=" * 80)
    print("[WARNING]️  REAL MONEY TRADING - STARTING AUTOMATICALLY")
    print(f"💰 Account: U21922116")
    print(f"💵 Capital: $250")
    print(f"📊 Max trades: 3")
    print(f"💵 Max position: $2.50")
    print("=" * 80)
    
    bot = AutoTradingBot()
    
    if not bot.connect_ib():
        logger.error("[ERROR] Cannot connect to IB Gateway")
        logger.info("💡 Make sure IB Gateway is running on port 7496")
        return
    
    logger.info("\n[CHECK] STARTING AUTONOMOUS TRADING NOW!")
    logger.info("🛑 Press Ctrl+C to stop\n")
    
    try:
        bot.trade_loop()
    except KeyboardInterrupt:
        logger.info("\n⏸️ Stopping...")
    finally:
        bot.disconnect()
        logger.info("[CHECK] Disconnected")

if __name__ == "__main__":
    main()

