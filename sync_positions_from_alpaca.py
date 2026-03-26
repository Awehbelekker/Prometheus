#!/usr/bin/env python
"""
🔄 POSITION SYNC: Sync internal database with Alpaca's actual positions
This ensures the trading system always knows what positions it actually holds.
"""
import sqlite3
import os
from datetime import datetime
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv

load_dotenv()

DB_PATH = 'prometheus_learning.db'

def sync_positions():
    """Sync open_positions table with Alpaca's actual positions"""
    print("="*70)
    print("🔄 PROMETHEUS POSITION SYNC - Syncing with Alpaca")
    print("="*70)
    
    # Connect to Alpaca
    client = TradingClient(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        paper=False
    )
    
    # Get actual Alpaca positions
    alpaca_positions = client.get_all_positions()
    print(f"\n📊 Found {len(alpaca_positions)} positions in Alpaca")
    
    # Connect to internal database
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS open_positions (
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            entry_price REAL NOT NULL,
            current_price REAL,
            unrealized_pl REAL,
            broker TEXT DEFAULT 'Alpaca',
            opened_at TEXT,
            updated_at TEXT,
            PRIMARY KEY (symbol, broker)
        )
    """)
    
    # Get current internal positions
    cursor.execute("SELECT symbol, quantity FROM open_positions WHERE broker = 'Alpaca'")
    internal_positions = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"📋 Found {len(internal_positions)} positions in internal database")
    
    # Step 1: Clear all Alpaca positions from internal database
    cursor.execute("DELETE FROM open_positions WHERE broker = 'Alpaca'")
    print("\n🧹 Cleared old internal positions")
    
    # Step 2: Insert all actual Alpaca positions
    now = datetime.now().isoformat()
    synced_count = 0
    
    print("\n📥 Syncing positions from Alpaca:")
    for pos in alpaca_positions:
        symbol = pos.symbol
        qty = float(pos.qty)
        entry_price = float(pos.avg_entry_price)
        current_price = float(pos.current_price)
        unrealized_pl = float(pos.unrealized_pl)
        pnl_pct = float(pos.unrealized_plpc) * 100
        
        # Determine side (all Alpaca positions are LONG since no shorting)
        side = 'LONG' if qty > 0 else 'SHORT'
        qty = abs(qty)
        
        cursor.execute("""
            INSERT INTO open_positions 
            (symbol, side, quantity, entry_price, current_price, unrealized_pl, broker, opened_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 'Alpaca', ?, ?)
        """, (symbol, side, qty, entry_price, current_price, unrealized_pl, now, now))
        
        emoji = "🟢" if pnl_pct >= 0 else "🔴"
        print(f"  {emoji} {symbol}: {qty} @ ${entry_price:.4f} | P/L: {pnl_pct:+.2f}%")
        synced_count += 1
    
    db.commit()
    
    # Verify sync
    cursor.execute("SELECT COUNT(*) FROM open_positions WHERE broker = 'Alpaca'")
    final_count = cursor.fetchone()[0]
    
    db.close()
    
    print(f"\n✅ Sync complete!")
    print(f"   Alpaca positions: {len(alpaca_positions)}")
    print(f"   Internal positions: {final_count}")
    print(f"   Match: {'✅ YES' if len(alpaca_positions) == final_count else '❌ NO'}")
    print("="*70)
    
    return {
        'alpaca_count': len(alpaca_positions),
        'internal_count': final_count,
        'synced': len(alpaca_positions) == final_count
    }


if __name__ == "__main__":
    sync_positions()

