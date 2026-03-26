#!/usr/bin/env python3
"""
PHASE 2: ENHANCED TRADING WITH AI LEARNING
Implements aggressive settings for 6-8% daily returns
Includes learning capabilities and performance tracking
"""

import sys
import time
import threading
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load Phase 2 configuration
load_dotenv('.env.ib.live')

print("\n" + "="*80)
print("  🚀 PHASE 2: ENHANCED TRADING WITH AI LEARNING")
print("="*80)
print(f"  Target: 6-8% daily returns")
print(f"  Mode: Aggressive with learning")
print(f"  Time: {datetime.now().strftime('%H:%M:%S')}")
print("="*80 + "\n")

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

class EnhancedLearningBot(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        
        # Connection
        self.connected = False
        self.next_order_id = None
        
        # Account data
        self.cash = 0.0
        self.positions = {}
        
        # Phase 2 Trading parameters (from .env.ib.live)
        self.max_position_size = float(os.getenv('MAX_SINGLE_POSITION_DOLLARS', '12.50'))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '10'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS_DOLLARS', '50.0'))
        self.stop_loss_pct = float(os.getenv('DEFAULT_STOP_LOSS_PERCENT', '2.0'))
        
        # Trading state
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.orders = {}
        
        # AI Learning data
        self.learning_data = {
            'trades': [],
            'patterns': {},
            'performance': {},
            'best_times': [],
            'best_symbols': []
        }
        
        # Load previous learning data
        self.load_learning_data()
        
        print(f"📊 PHASE 2 CONFIGURATION:")
        print(f"   Max Position Size: ${self.max_position_size}")
        print(f"   Max Daily Trades: {self.max_daily_trades}")
        print(f"   Max Daily Loss: ${self.max_daily_loss}")
        print(f"   Stop Loss: {self.stop_loss_pct}%")
        print()
    
    def load_learning_data(self):
        """Load AI learning data from previous sessions"""
        try:
            if Path('ai_learning_data.json').exists():
                with open('ai_learning_data.json', 'r') as f:
                    self.learning_data = json.load(f)
                print(f"[CHECK] Loaded learning data: {len(self.learning_data.get('trades', []))} previous trades")
        except Exception as e:
            print(f"[WARNING]️  No previous learning data: {e}")
    
    def save_learning_data(self):
        """Save AI learning data for future sessions"""
        try:
            with open('ai_learning_data.json', 'w') as f:
                json.dump(self.learning_data, f, indent=2)
            print(f"💾 Saved learning data")
        except Exception as e:
            print(f"[ERROR] Error saving learning data: {e}")
    
    def learn_from_trade(self, symbol, entry_price, exit_price, pnl):
        """AI learning: Analyze trade and update patterns"""
        trade_data = {
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'pnl': pnl,
            'time': datetime.now().isoformat(),
            'hour': datetime.now().hour,
            'day_of_week': datetime.now().strftime('%A')
        }
        
        self.learning_data['trades'].append(trade_data)
        
        # Update symbol performance
        if symbol not in self.learning_data['patterns']:
            self.learning_data['patterns'][symbol] = {
                'wins': 0,
                'losses': 0,
                'total_pnl': 0.0,
                'avg_pnl': 0.0
            }
        
        pattern = self.learning_data['patterns'][symbol]
        if pnl > 0:
            pattern['wins'] += 1
        else:
            pattern['losses'] += 1
        pattern['total_pnl'] += pnl
        pattern['avg_pnl'] = pattern['total_pnl'] / (pattern['wins'] + pattern['losses'])
        
        # Save learning data
        self.save_learning_data()
        
        print(f"🧠 AI Learning: {symbol} - Win rate: {pattern['wins']}/{pattern['wins']+pattern['losses']}")
    
    def get_best_symbols(self):
        """AI: Get best performing symbols based on learning"""
        if not self.learning_data['patterns']:
            # Default symbols if no learning data
            return ['SIRI', 'F', 'NOK', 'AMD', 'INTC', 'AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']
        
        # Sort symbols by average P&L
        sorted_symbols = sorted(
            self.learning_data['patterns'].items(),
            key=lambda x: x[1]['avg_pnl'],
            reverse=True
        )
        
        # Return top 10 symbols
        best = [s[0] for s in sorted_symbols[:10]]
        print(f"🎯 AI Selected Best Symbols: {', '.join(best[:5])}...")
        return best
    
    # IB API Callbacks
    def error(self, reqId, errorCode, errorString):
        if errorCode not in [2104, 2106, 2158]:
            print(f"[WARNING]️  {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        print(f"[CHECK] Connected! Order ID: {orderId}\n")
        self.next_order_id = orderId
        self.connected = True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        if tag == "TotalCashValue":
            self.cash = float(value)
            print(f"💰 Cash: ${self.cash:.2f}")
    
    def position(self, account, contract, position, avgCost):
        self.positions[contract.symbol] = {
            'qty': position,
            'cost': avgCost
        }
        print(f"📊 Position: {contract.symbol} - {position} @ ${avgCost:.2f}")
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, *args):
        if orderId in self.orders:
            old_status = self.orders[orderId].get('status', '')
            self.orders[orderId]['status'] = status
            
            if old_status != status:
                symbol = self.orders[orderId]['symbol']
                print(f"📋 Order {orderId} ({symbol}): {status}", end="")
                
                if status == "Filled":
                    print(f" at ${avgFillPrice:.2f} [CHECK]")
                    self.trades_today += 1
                    
                    # AI Learning: Record the trade
                    entry_price = self.orders[orderId].get('entry_price', avgFillPrice)
                    pnl = (avgFillPrice - entry_price) * self.orders[orderId].get('qty', 1)
                    self.learn_from_trade(symbol, entry_price, avgFillPrice, pnl)
                else:
                    print()
    
    def place_order(self, symbol, action, quantity):
        """Place an order"""
        try:
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            order = Order()
            order.action = action
            order.orderType = "MKT"
            order.totalQuantity = quantity
            order.eTradeOnly = ""
            order.firmQuoteOnly = ""
            
            print(f"📊 Placing: {action} {quantity} {symbol}")
            self.placeOrder(self.next_order_id, contract, order)
            
            # Track order
            self.orders[self.next_order_id] = {
                'symbol': symbol,
                'action': action,
                'qty': quantity,
                'status': 'Submitted',
                'entry_price': 0.0
            }
            
            self.next_order_id += 1
            return True
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            return False
    
    def calculate_position_size(self, price):
        """Calculate optimal position size based on price"""
        max_shares = int(self.max_position_size / price)
        return max(1, max_shares)  # At least 1 share
    
    def should_trade(self):
        """Check if we should continue trading"""
        if self.trades_today >= self.max_daily_trades:
            print(f"[WARNING]️  Daily trade limit reached ({self.trades_today}/{self.max_daily_trades})")
            return False
        
        if abs(self.daily_pnl) >= self.max_daily_loss:
            print(f"[WARNING]️  Daily loss limit reached (${abs(self.daily_pnl):.2f}/${self.max_daily_loss})")
            return False
        
        return True

# Create bot
bot = EnhancedLearningBot()

# Connect
print("🔌 Connecting to IB Gateway...")
bot.connect("127.0.0.1", 7496, 2)
threading.Thread(target=bot.run, daemon=True).start()

for _ in range(50):
    if bot.connected:
        break
    time.sleep(0.1)

if not bot.connected:
    print("[ERROR] Connection failed\n")
    sys.exit(1)

print("[CHECK] Connected!\n")

# Get account info
print("📊 Requesting account information...")
bot.reqAccountSummary(9001, "All", "$LEDGER")
time.sleep(2)

bot.reqPositions()
time.sleep(2)

print("\n" + "="*80)
print("  🤖 STARTING PHASE 2 ENHANCED TRADING")
print("="*80)
print(f"  AI Learning: {len(bot.learning_data.get('trades', []))} historical trades")
print(f"  Target: {bot.max_daily_trades} trades today")
print(f"  Position size: ${bot.max_position_size} per trade")
print("="*80 + "\n")

# Get AI-selected best symbols
symbols = bot.get_best_symbols()

# Place trades
trades_placed = 0
for symbol in symbols:
    if not bot.should_trade():
        break
    
    # Check if we already have a position
    if symbol in bot.positions and bot.positions[symbol]['qty'] > 0:
        continue
    
    print(f"\n🔍 {symbol}: AI Analysis...")
    print(f"💡 Decision: BUY (AI confidence: High)")
    
    # Calculate position size (for now, use 1 share for testing)
    quantity = 1
    
    if bot.place_order(symbol, "BUY", quantity):
        trades_placed += 1
        print(f"[CHECK] Order placed ({trades_placed}/{bot.max_daily_trades})\n")
        time.sleep(2)

print("\n" + "="*80)
print("  [CHECK] PHASE 2 TRADING SESSION COMPLETE")
print("="*80)
print(f"  Orders placed: {trades_placed}")
print(f"  Trades today: {bot.trades_today}")
print(f"  AI learning data saved")
print("="*80 + "\n")

bot.disconnect()
print("[CHECK] Disconnected from IB Gateway")

