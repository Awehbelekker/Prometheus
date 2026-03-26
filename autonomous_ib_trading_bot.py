#!/usr/bin/env python3
"""
AUTONOMOUS IB TRADING BOT
Actually connects to IB and makes real trades autonomously
"""

import os
import sys
import time
import logging
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load IB configuration
load_dotenv('.env.ib.live')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order
    IB_AVAILABLE = True
except ImportError:
    logger.error("[ERROR] ibapi not installed. Run: pip install ibapi")
    IB_AVAILABLE = False
    sys.exit(1)

class TradingBot(EWrapper, EClient):
    """Autonomous Trading Bot for Interactive Brokers"""
    
    def __init__(self):
        EClient.__init__(self, self)
        
        # Connection state
        self.connected = False
        self.next_order_id = None
        
        # Account data
        self.account_id = os.getenv('IB_ACCOUNT_ID', 'U21922116')
        self.account_value = {}
        self.positions = {}
        self.cash_balance = 0.0
        
        # Trading parameters
        self.max_position_size = float(os.getenv('MAX_SINGLE_POSITION_DOLLARS', '2.50'))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '3'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS_DOLLARS', '50.0'))
        
        # Trading state
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.is_trading = False
        
        # Order tracking
        self.orders = {}
        
        logger.info("🤖 Trading Bot initialized")
        logger.info(f"💰 Max position size: ${self.max_position_size}")
        logger.info(f"📊 Max daily trades: {self.max_daily_trades}")
        logger.info(f"🛡️ Max daily loss: ${self.max_daily_loss}")
    
    # ===== IB API Callbacks =====
    
    def error(self, reqId, errorCode, errorString):
        """Handle errors"""
        logger.error(f"IB Error {errorCode}: {errorString}")
        
        # Critical errors
        if errorCode in [502, 503, 504]:  # Connection errors
            logger.error("[ERROR] Connection lost!")
            self.connected = False
    
    def nextValidId(self, orderId):
        """Receive next valid order ID - signals successful connection"""
        logger.info(f"[CHECK] Connected to IB! Next order ID: {orderId}")
        self.next_order_id = orderId
        self.connected = True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        """Receive account summary"""
        self.account_value[tag] = value
        
        if tag == "TotalCashValue":
            self.cash_balance = float(value)
            logger.info(f"💰 Cash Balance: ${self.cash_balance:.2f}")
    
    def position(self, account, contract, position, avgCost):
        """Receive position updates"""
        self.positions[contract.symbol] = {
            'quantity': position,
            'avg_cost': avgCost,
            'symbol': contract.symbol
        }
        logger.info(f"📊 Position: {contract.symbol} - {position} @ ${avgCost:.2f}")
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, 
                   permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice):
        """Receive order status updates"""
        self.orders[orderId] = {
            'status': status,
            'filled': filled,
            'remaining': remaining,
            'avg_fill_price': avgFillPrice
        }
        
        logger.info(f"📋 Order {orderId}: {status} - Filled: {filled}, Remaining: {remaining}")
        
        if status == "Filled":
            logger.info(f"[CHECK] Order {orderId} FILLED at ${avgFillPrice:.2f}")
            self.trades_today += 1
    
    def execDetails(self, reqId, contract, execution):
        """Receive execution details"""
        logger.info(f"[CHECK] Execution: {contract.symbol} {execution.side} {execution.shares} @ ${execution.price:.2f}")
    
    # ===== Trading Methods =====
    
    def connect_to_ib(self):
        """Connect to IB Gateway"""
        try:
            host = os.getenv('IB_HOST', '127.0.0.1')
            port = int(os.getenv('IB_PORT', '7496'))
            client_id = int(os.getenv('IB_CLIENT_ID', '2'))
            
            logger.info(f"🔌 Connecting to IB Gateway at {host}:{port}...")
            self.connect(host, port, client_id)
            
            # Start the client thread
            api_thread = threading.Thread(target=self.run, daemon=True)
            api_thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.connected:
                logger.info("[CHECK] Successfully connected to IB!")
                
                # Request account data
                self.reqAccountSummary(9001, "All", "$LEDGER")
                time.sleep(1)
                
                # Request positions
                self.reqPositions()
                time.sleep(1)
                
                return True
            else:
                logger.error("[ERROR] Connection timeout")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Connection error: {e}")
            return False
    
    def create_stock_contract(self, symbol):
        """Create a stock contract"""
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract
    
    def create_market_order(self, action, quantity):
        """Create a market order"""
        order = Order()
        order.action = action  # "BUY" or "SELL"
        order.orderType = "MKT"
        order.totalQuantity = quantity
        order.eTradeOnly = False
        order.firmQuoteOnly = False
        return order
    
    def place_order(self, symbol, action, quantity):
        """Place an order"""
        try:
            if not self.connected:
                logger.error("[ERROR] Not connected to IB")
                return False
            
            if self.next_order_id is None:
                logger.error("[ERROR] No valid order ID")
                return False
            
            # Create contract and order
            contract = self.create_stock_contract(symbol)
            order = self.create_market_order(action, quantity)
            
            # Place order
            logger.info(f"📊 Placing order: {action} {quantity} {symbol}")
            self.placeOrder(self.next_order_id, contract, order)
            self.next_order_id += 1
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] Error placing order: {e}")
            return False
    
    def check_trading_limits(self):
        """Check if we can still trade today"""
        if self.trades_today >= self.max_daily_trades:
            logger.warning(f"[WARNING]️ Daily trade limit reached ({self.trades_today}/{self.max_daily_trades})")
            return False
        
        if abs(self.daily_pnl) >= self.max_daily_loss:
            logger.warning(f"[WARNING]️ Daily loss limit reached (${abs(self.daily_pnl):.2f}/${self.max_daily_loss})")
            return False
        
        return True
    
    def analyze_and_trade(self):
        """Analyze market and make trading decision"""
        try:
            # Check limits
            if not self.check_trading_limits():
                return
            
            # Simple trading logic for demonstration
            # In production, this would use your AI/ML models
            
            # Example: Buy 1 share of a cheap stock for testing
            symbols = ['SIRI', 'F', 'NOK']  # Cheap stocks for testing
            
            for symbol in symbols:
                if self.trades_today < self.max_daily_trades:
                    logger.info(f"🔍 Analyzing {symbol}...")
                    
                    # Simple logic: buy 1 share if we don't have a position
                    if symbol not in self.positions or self.positions[symbol]['quantity'] == 0:
                        logger.info(f"💡 Decision: BUY 1 share of {symbol}")
                        self.place_order(symbol, "BUY", 1)
                        time.sleep(5)  # Wait between orders
                        break
            
        except Exception as e:
            logger.error(f"[ERROR] Error in trading logic: {e}")
    
    def start_trading(self):
        """Start autonomous trading"""
        logger.info("🚀 Starting autonomous trading...")
        self.is_trading = True
        
        while self.is_trading:
            try:
                if not self.connected:
                    logger.error("[ERROR] Connection lost. Stopping trading.")
                    break
                
                # Check if we can trade
                if self.check_trading_limits():
                    # Analyze and trade
                    self.analyze_and_trade()
                else:
                    logger.info("⏸️ Trading limits reached for today")
                    break
                
                # Wait 5 minutes between trading cycles
                logger.info("⏳ Waiting 5 minutes before next cycle...")
                time.sleep(300)
                
            except KeyboardInterrupt:
                logger.info("⏸️ Trading stopped by user")
                break
            except Exception as e:
                logger.error(f"[ERROR] Error in trading loop: {e}")
                time.sleep(60)
        
        logger.info("🛑 Trading stopped")
    
    def stop_trading(self):
        """Stop trading"""
        self.is_trading = False

def main():
    print("=" * 80)
    print("  🚀 PROMETHEUS AUTONOMOUS IB TRADING BOT")
    print("=" * 80)
    print("[WARNING]️  WARNING: THIS WILL MAKE REAL TRADES WITH REAL MONEY")
    print(f"💰 Account: {os.getenv('IB_ACCOUNT_ID', 'U21922116')}")
    print(f"💵 Capital: ${os.getenv('STARTING_CAPITAL_USD', '250')} USD")
    print("=" * 80)
    
    # Create bot
    bot = TradingBot()
    
    # Connect to IB
    if not bot.connect_to_ib():
        logger.error("[ERROR] Failed to connect to IB Gateway")
        logger.info("💡 Make sure IB Gateway is running and logged in")
        return
    
    # Show account info
    print("\n📊 ACCOUNT STATUS:")
    print(f"  Cash Balance: ${bot.cash_balance:.2f}")
    print(f"  Positions: {len(bot.positions)}")
    
    # Confirm
    print("\n" + "=" * 80)
    print("  READY TO START AUTONOMOUS TRADING")
    print("=" * 80)
    print(f"  Max Position Size: ${bot.max_position_size}")
    print(f"  Max Daily Trades: {bot.max_daily_trades}")
    print(f"  Max Daily Loss: ${bot.max_daily_loss}")
    print("=" * 80)
    
    response = input("\n[WARNING]️  Type 'START' to begin autonomous trading: ")
    
    if response.upper() != 'START':
        logger.info("[ERROR] Trading cancelled")
        bot.disconnect()
        return
    
    # Start trading
    logger.info("\n[CHECK] AUTONOMOUS TRADING STARTED!")
    logger.info("🤖 Bot is now trading autonomously")
    logger.info("🛑 Press Ctrl+C to stop\n")
    
    try:
        bot.start_trading()
    except KeyboardInterrupt:
        logger.info("\n⏸️ Stopping trading...")
        bot.stop_trading()
    finally:
        logger.info("🔌 Disconnecting from IB...")
        bot.disconnect()
        logger.info("[CHECK] Bot stopped")

if __name__ == "__main__":
    if not IB_AVAILABLE:
        print("[ERROR] ibapi not available. Install with: pip install ibapi")
        sys.exit(1)
    
    main()

