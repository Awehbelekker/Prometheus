#!/usr/bin/env python3
"""
PROMETHEUS LIVE STATS DASHBOARD
Real-time monitoring with comprehensive statistics
"""

import sys
import time
import threading
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv('.env.ib.live')

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

class StatsDashboard(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        
        self.connected = False
        self.next_order_id = None
        
        # Account data
        self.account_id = os.getenv('IB_ACCOUNT_ID', 'U21922116')
        self.cash = 0.0
        self.equity = 0.0
        self.buying_power = 0.0
        self.positions = {}
        self.orders = {}
        
        # Phase 2 settings
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', '10'))
        self.max_position_size = float(os.getenv('MAX_SINGLE_POSITION_DOLLARS', '12.50'))
        self.max_daily_loss = float(os.getenv('MAX_DAILY_LOSS_DOLLARS', '50.0'))
        
        # Stats
        self.starting_capital = 250.0
        self.trades_today = 0
        self.total_pnl = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        
        self.data_received = {
            'account': False,
            'positions': False,
            'orders': False
        }
    
    def error(self, reqId, errorCode, errorString):
        if errorCode not in [2104, 2106, 2158]:
            print(f"[WARNING]️  {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        self.next_order_id = orderId
        self.connected = True
    
    def accountSummary(self, reqId, account, tag, value, currency):
        try:
            if tag == "TotalCashValue":
                self.cash = float(value)
            elif tag == "NetLiquidation":
                self.equity = float(value)
            elif tag == "BuyingPower":
                self.buying_power = float(value)
            elif tag == "RealizedPnL":
                self.realized_pnl = float(value)
            elif tag == "UnrealizedPnL":
                self.unrealized_pnl = float(value)
        except:
            pass
    
    def accountSummaryEnd(self, reqId):
        self.data_received['account'] = True
    
    def position(self, account, contract, position, avgCost):
        if position != 0:
            self.positions[contract.symbol] = {
                'qty': position,
                'cost': avgCost,
                'symbol': contract.symbol
            }
    
    def positionEnd(self):
        self.data_received['positions'] = True
    
    def openOrder(self, orderId, contract, order, orderState):
        self.orders[orderId] = {
            'symbol': contract.symbol,
            'action': order.action,
            'qty': order.totalQuantity,
            'status': orderState.status
        }
    
    def openOrderEnd(self):
        self.data_received['orders'] = True
    
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, *args):
        if orderId in self.orders:
            self.orders[orderId]['status'] = status
            if status == "Filled":
                self.trades_today += 1
    
    def print_dashboard(self):
        """Print comprehensive stats dashboard"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("\n" + "="*80)
        print("  🚀 PROMETHEUS LIVE TRADING DASHBOARD - PHASE 2")
        print("="*80)
        print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Account: {self.account_id}")
        print("="*80 + "\n")
        
        # Account Summary
        print("💰 ACCOUNT SUMMARY")
        print("-" * 80)
        print(f"  Starting Capital:    ${self.starting_capital:,.2f}")
        print(f"  Current Equity:      ${self.equity:,.2f}")
        print(f"  Cash Available:      ${self.cash:,.2f}")
        print(f"  Buying Power:        ${self.buying_power:,.2f}")
        print()
        
        # P&L Summary
        total_return_pct = ((self.equity - self.starting_capital) / self.starting_capital * 100) if self.starting_capital > 0 else 0
        
        print("📊 PROFIT & LOSS")
        print("-" * 80)
        print(f"  Realized P&L:        ${self.realized_pnl:,.2f}")
        print(f"  Unrealized P&L:      ${self.unrealized_pnl:,.2f}")
        print(f"  Total P&L:           ${self.realized_pnl + self.unrealized_pnl:,.2f}")
        print(f"  Total Return:        {total_return_pct:+.2f}%")
        print()
        
        # Positions
        print("📈 CURRENT POSITIONS")
        print("-" * 80)
        if self.positions:
            total_position_value = 0.0
            for symbol, pos in self.positions.items():
                qty = pos['qty']
                cost = pos['cost']
                position_value = qty * cost
                total_position_value += position_value
                
                print(f"  {symbol:6s} | Qty: {qty:>6.0f} | Avg Cost: ${cost:>8.2f} | Value: ${position_value:>10.2f}")
            
            print("-" * 80)
            print(f"  Total Position Value: ${total_position_value:,.2f}")
            print(f"  Capital Deployed:     {(total_position_value/self.starting_capital*100):.1f}%")
        else:
            print("  No open positions")
        print()
        
        # Open Orders
        print("📋 OPEN ORDERS")
        print("-" * 80)
        if self.orders:
            for order_id, order in self.orders.items():
                print(f"  Order {order_id}: {order['action']} {order['qty']} {order['symbol']} - {order['status']}")
        else:
            print("  No open orders")
        print()
        
        # Trading Activity
        print("🎯 TRADING ACTIVITY (TODAY)")
        print("-" * 80)
        print(f"  Trades Executed:     {self.trades_today} / {self.max_daily_trades}")
        print(f"  Trades Remaining:    {max(0, self.max_daily_trades - self.trades_today)}")
        
        trades_pct = (self.trades_today / self.max_daily_trades * 100) if self.max_daily_trades > 0 else 0
        print(f"  Daily Limit Used:    {trades_pct:.1f}%")
        print()
        
        # Phase 2 Configuration
        print("⚙️  PHASE 2 CONFIGURATION")
        print("-" * 80)
        print(f"  Max Daily Trades:    {self.max_daily_trades}")
        print(f"  Max Position Size:   ${self.max_position_size}")
        print(f"  Max Daily Loss:      ${self.max_daily_loss}")
        print()
        
        # Performance Targets
        print("🎯 PERFORMANCE TARGETS")
        print("-" * 80)
        daily_target_6pct = self.starting_capital * 0.06
        daily_target_8pct = self.starting_capital * 0.08
        
        current_pnl = self.realized_pnl + self.unrealized_pnl
        progress_6pct = (current_pnl / daily_target_6pct * 100) if daily_target_6pct > 0 else 0
        progress_8pct = (current_pnl / daily_target_8pct * 100) if daily_target_8pct > 0 else 0
        
        print(f"  6% Daily Target:     ${daily_target_6pct:.2f}")
        print(f"  Progress to 6%:      {progress_6pct:.1f}%")
        print(f"  8% Daily Target:     ${daily_target_8pct:.2f}")
        print(f"  Progress to 8%:      {progress_8pct:.1f}%")
        print()
        
        # Status Indicators
        print("[CHECK] STATUS")
        print("-" * 80)
        print(f"  Connection:          {'🟢 Connected' if self.connected else '🔴 Disconnected'}")
        print(f"  Trading:             {'🟢 Active' if self.trades_today < self.max_daily_trades else '🔴 Limit Reached'}")
        print(f"  Risk Status:         {'🟢 Normal' if abs(current_pnl) < self.max_daily_loss else '🔴 Risk Limit'}")
        print()
        
        print("="*80)
        print("  Press Ctrl+C to stop monitoring")
        print("="*80 + "\n")

# Create dashboard
dashboard = StatsDashboard()

print("\n" + "="*80)
print("  🚀 LAUNCHING PROMETHEUS STATS DASHBOARD")
print("="*80)
print("  Connecting to IB Gateway...")
print("="*80 + "\n")

# Connect
dashboard.connect("127.0.0.1", 7496, 3)
threading.Thread(target=dashboard.run, daemon=True).start()

# Wait for connection
for _ in range(50):
    if dashboard.connected:
        break
    time.sleep(0.1)

if not dashboard.connected:
    print("[ERROR] Connection failed\n")
    sys.exit(1)

print("[CHECK] Connected! Loading data...\n")

try:
    while True:
        # Request fresh data
        dashboard.reqAccountSummary(9001, "All", "$LEDGER")
        time.sleep(1)
        
        dashboard.reqPositions()
        time.sleep(1)
        
        dashboard.reqOpenOrders()
        time.sleep(1)
        
        # Wait for all data
        time.sleep(2)
        
        # Print dashboard
        dashboard.print_dashboard()
        
        # Update every 30 seconds
        time.sleep(30)

except KeyboardInterrupt:
    print("\n\n" + "="*80)
    print("  🛑 STOPPING DASHBOARD")
    print("="*80)
    
    # Print final stats
    dashboard.print_dashboard()
    
    dashboard.disconnect()
    print("\n[CHECK] Disconnected from IB Gateway")
    print("="*80 + "\n")

