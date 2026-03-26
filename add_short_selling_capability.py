#!/usr/bin/env python3
"""
Add SHORT SELLING Capability to PROMETHEUS - WITHOUT DISRUPTING TRADING
This script adds position tracking and short selling logic
"""

import sqlite3
from datetime import datetime

print("=" * 80)
print("🚀 ADDING SHORT SELLING CAPABILITY TO PROMETHEUS")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}")
print()

# Step 1: Create position tracking table
print("📊 Step 1: Creating Position Tracking System")
print("-" * 80)

db = sqlite3.connect('prometheus_learning.db')
cursor = db.cursor()

# Create positions table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS open_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        side TEXT NOT NULL,
        quantity REAL NOT NULL,
        entry_price REAL NOT NULL,
        current_price REAL,
        unrealized_pl REAL DEFAULT 0,
        broker TEXT NOT NULL,
        opened_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE(symbol, broker)
    )
""")

db.commit()
print("[CHECK] Position tracking table created")
print()

# Step 2: Check existing schema
print("📋 Step 2: Checking Database Schema")
print("-" * 80)

cursor.execute("PRAGMA table_info(trade_history)")
columns = [col[1] for col in cursor.fetchall()]

# Add position_side column if missing
if 'position_side' not in columns:
    cursor.execute("ALTER TABLE trade_history ADD COLUMN position_side TEXT DEFAULT 'LONG'")
    db.commit()
    print("[CHECK] Added 'position_side' column to trade_history")
else:
    print("[CHECK] 'position_side' column already exists")

# Add position_action column if missing
if 'position_action' not in columns:
    cursor.execute("ALTER TABLE trade_history ADD COLUMN position_action TEXT")
    db.commit()
    print("[CHECK] Added 'position_action' column to trade_history")
else:
    print("[CHECK] 'position_action' column already exists")

print()

# Step 3: Create position management functions file
print("📝 Step 3: Creating Position Management Module")
print("-" * 80)

position_manager_code = '''"""
Position Manager for SHORT SELLING Capability
Tracks open positions and determines trade intent
"""

import sqlite3
from typing import Dict, Optional, Tuple
from datetime import datetime

class PositionManager:
    """Manages open positions for LONG and SHORT trading"""
    
    def __init__(self, db_path='prometheus_learning.db'):
        self.db_path = db_path
    
    def get_position(self, symbol: str, broker: str = 'Alpaca') -> Optional[Dict]:
        """Get current position for a symbol"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT symbol, side, quantity, entry_price, current_price, 
                   unrealized_pl, broker, opened_at, updated_at
            FROM open_positions
            WHERE symbol = ? AND broker = ?
        """, (symbol, broker))
        
        row = cursor.fetchone()
        db.close()
        
        if row:
            return {
                'symbol': row[0],
                'side': row[1],
                'quantity': row[2],
                'entry_price': row[3],
                'current_price': row[4],
                'unrealized_pl': row[5],
                'broker': row[6],
                'opened_at': row[7],
                'updated_at': row[8]
            }
        return None
    
    def determine_trade_intent(self, symbol: str, action: str, broker: str = 'Alpaca') -> Tuple[str, str]:
        """
        Determine if trade should OPEN or CLOSE a position
        Returns: (position_action, position_side)
        
        position_action: 'OPEN_LONG', 'CLOSE_LONG', 'OPEN_SHORT', 'CLOSE_SHORT'
        position_side: 'LONG', 'SHORT'
        """
        position = self.get_position(symbol, broker)
        
        if action in ['BUY', 'STRONG_BUY']:
            if position is None:
                # No position - open LONG
                return ('OPEN_LONG', 'LONG')
            elif position['side'] == 'SHORT':
                # Have SHORT position - close it (cover)
                return ('CLOSE_SHORT', 'SHORT')
            else:
                # Have LONG position - add to it (or ignore if max position)
                return ('ADD_LONG', 'LONG')
        
        elif action in ['SELL', 'STRONG_SELL']:
            if position is None:
                # No position - open SHORT
                return ('OPEN_SHORT', 'SHORT')
            elif position['side'] == 'LONG':
                # Have LONG position - close it
                return ('CLOSE_LONG', 'LONG')
            else:
                # Have SHORT position - add to it (or ignore if max position)
                return ('ADD_SHORT', 'SHORT')
        
        return ('HOLD', 'NONE')
    
    def open_position(self, symbol: str, side: str, quantity: float, 
                     entry_price: float, broker: str = 'Alpaca'):
        """Open a new position"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO open_positions
            (symbol, side, quantity, entry_price, current_price, broker, opened_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (symbol, side, quantity, entry_price, entry_price, broker, now, now))
        
        db.commit()
        db.close()
    
    def close_position(self, symbol: str, broker: str = 'Alpaca') -> Optional[Dict]:
        """Close a position and return its details"""
        position = self.get_position(symbol, broker)
        
        if position:
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            cursor.execute("""
                DELETE FROM open_positions
                WHERE symbol = ? AND broker = ?
            """, (symbol, broker))
            
            db.commit()
            db.close()
        
        return position
    
    def update_position_price(self, symbol: str, current_price: float, broker: str = 'Alpaca'):
        """Update current price and calculate unrealized P/L"""
        position = self.get_position(symbol, broker)
        
        if position:
            entry_price = position['entry_price']
            quantity = position['quantity']
            side = position['side']
            
            # Calculate unrealized P/L
            if side == 'LONG':
                unrealized_pl = (current_price - entry_price) * quantity
            else:  # SHORT
                unrealized_pl = (entry_price - current_price) * quantity
            
            db = sqlite3.connect(self.db_path)
            cursor = db.cursor()
            
            cursor.execute("""
                UPDATE open_positions
                SET current_price = ?, unrealized_pl = ?, updated_at = ?
                WHERE symbol = ? AND broker = ?
            """, (current_price, unrealized_pl, datetime.now().isoformat(), symbol, broker))
            
            db.commit()
            db.close()
    
    def get_all_positions(self, broker: str = None) -> list:
        """Get all open positions"""
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        if broker:
            cursor.execute("""
                SELECT symbol, side, quantity, entry_price, current_price, 
                       unrealized_pl, broker, opened_at, updated_at
                FROM open_positions
                WHERE broker = ?
            """, (broker,))
        else:
            cursor.execute("""
                SELECT symbol, side, quantity, entry_price, current_price, 
                       unrealized_pl, broker, opened_at, updated_at
                FROM open_positions
            """)
        
        positions = []
        for row in cursor.fetchall():
            positions.append({
                'symbol': row[0],
                'side': row[1],
                'quantity': row[2],
                'entry_price': row[3],
                'current_price': row[4],
                'unrealized_pl': row[5],
                'broker': row[6],
                'opened_at': row[7],
                'updated_at': row[8]
            })
        
        db.close()
        return positions
'''

with open('position_manager.py', 'w') as f:
    f.write(position_manager_code)

print("[CHECK] Created position_manager.py")
print()

# Step 4: Create the enhanced trading logic file
print("📝 Step 4: Creating Enhanced Trading Logic")
print("-" * 80)

enhanced_logic_code = '''"""
Enhanced Trading Logic with SHORT SELLING Support
This module provides the logic to integrate with the launcher
"""

from position_manager import PositionManager
from brokers.universal_broker_interface import OrderSide

class EnhancedTradingLogic:
    """Enhanced trading logic with SHORT selling capability"""
    
    def __init__(self):
        self.position_manager = PositionManager()
    
    def determine_order_details(self, symbol: str, action: str, current_price: float, 
                                equity: float, position_size_pct: float, 
                                broker_name: str = 'Alpaca'):
        """
        Determine order side, quantity, and position intent
        
        Returns:
            dict with keys: order_side, quantity, position_action, position_side, should_trade
        """
        # Get trade intent
        position_action, position_side = self.position_manager.determine_trade_intent(
            symbol, action, broker_name
        )
        
        # Get current position if exists
        current_position = self.position_manager.get_position(symbol, broker_name)
        
        # Determine if we should trade
        should_trade = True
        order_side = None
        quantity = 0
        
        if position_action == 'OPEN_LONG':
            # Open new LONG position
            order_side = OrderSide.BUY
            trade_amount = equity * position_size_pct
            quantity = trade_amount / current_price
            
        elif position_action == 'CLOSE_LONG':
            # Close existing LONG position
            order_side = OrderSide.SELL
            quantity = current_position['quantity']
            
        elif position_action == 'OPEN_SHORT':
            # Open new SHORT position
            order_side = OrderSide.SELL
            trade_amount = equity * position_size_pct
            quantity = trade_amount / current_price
            
        elif position_action == 'CLOSE_SHORT':
            # Close existing SHORT position (cover)
            order_side = OrderSide.BUY
            quantity = abs(current_position['quantity'])
            
        elif position_action in ['ADD_LONG', 'ADD_SHORT']:
            # Don't add to existing positions for now (can be enabled later)
            should_trade = False
            
        else:  # HOLD
            should_trade = False
        
        return {
            'order_side': order_side,
            'quantity': quantity,
            'position_action': position_action,
            'position_side': position_side,
            'should_trade': should_trade,
            'current_position': current_position
        }
    
    def record_trade_execution(self, symbol: str, position_action: str, position_side: str,
                              quantity: float, price: float, broker_name: str = 'Alpaca'):
        """Record trade execution and update positions"""
        
        if position_action == 'OPEN_LONG':
            self.position_manager.open_position(symbol, 'LONG', quantity, price, broker_name)
            
        elif position_action == 'OPEN_SHORT':
            self.position_manager.open_position(symbol, 'SHORT', quantity, price, broker_name)
            
        elif position_action == 'CLOSE_LONG':
            self.position_manager.close_position(symbol, broker_name)
            
        elif position_action == 'CLOSE_SHORT':
            self.position_manager.close_position(symbol, broker_name)
        
        # Update price for any remaining positions
        self.position_manager.update_position_price(symbol, price, broker_name)
'''

with open('enhanced_trading_logic.py', 'w') as f:
    f.write(enhanced_logic_code)

print("[CHECK] Created enhanced_trading_logic.py")
print()

# Step 5: Summary
print("=" * 80)
print("[CHECK] SHORT SELLING CAPABILITY ADDED!")
print("=" * 80)
print()
print("📊 What Was Created:")
print("-" * 80)
print("1. [CHECK] Position tracking database table (open_positions)")
print("2. [CHECK] Enhanced trade_history schema (position_side, position_action)")
print("3. [CHECK] position_manager.py - Position tracking module")
print("4. [CHECK] enhanced_trading_logic.py - SHORT selling logic")
print()
print("🔧 Next Steps:")
print("-" * 80)
print("1. Integrate enhanced_trading_logic.py into launcher")
print("2. Update execute_trade_from_signal() to use new logic")
print("3. Test with small positions first")
print()
print("💡 How It Works:")
print("-" * 80)
print("BULLISH Signal + No Position → OPEN LONG (BUY)")
print("BULLISH Signal + SHORT Position → CLOSE SHORT (BUY to cover)")
print("BEARISH Signal + No Position → OPEN SHORT (SELL)")
print("BEARISH Signal + LONG Position → CLOSE LONG (SELL)")
print()
print("=" * 80)
print("🚀 Ready to enable SHORT SELLING!")
print("=" * 80)

db.close()

