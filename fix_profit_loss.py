import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

print("🔧 RECALCULATING PROFIT/LOSS VALUES")
print("=" * 80)

# Get all closed trades
cursor.execute("""
    SELECT id, symbol, price, exit_price, quantity, action
    FROM trade_history
    WHERE status='closed'
""")

trades = cursor.fetchall()
print(f"Found {len(trades)} closed trades\n")

for trade_id, symbol, entry, exit_price, qty, action in trades:
    # Calculate correct P&L
    if action == 'BUY':  # LONG position
        correct_pnl = (exit_price - entry) * qty
    else:  # SHORT position  
        correct_pnl = (entry - exit_price) * qty
    
    pct = ((exit_price - entry) / entry * 100) if entry else 0
    
    # Get current stored value
    cursor.execute("SELECT profit_loss FROM trade_history WHERE id=?", (trade_id,))
    current_pnl = cursor.fetchone()[0]
    
    print(f"{symbol:12} | Entry: ${entry:8.2f} → Exit: ${exit_price:8.2f}")
    print(f"  ❌ Current P&L: ${current_pnl:9.4f}")
    print(f"  ✅ Correct P&L: ${correct_pnl:9.4f} ({pct:+.2f}%)")
    print(f"  📊 Qty: {qty:.4f}")
    
    # Update with correct value
    cursor.execute("""
        UPDATE trade_history
        SET profit_loss = ?
        WHERE id = ?
    """, (correct_pnl, trade_id))
    print(f"  ✓ Updated!\n")

conn.commit()

# Verify updates
cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='closed' AND profit_loss > 0")
positive = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='closed' AND profit_loss < 0")
negative = cursor.fetchone()[0]

print("=" * 80)
print(f"✅ RECALCULATION COMPLETE!")
print(f"   Positive P&L: {positive}")
print(f"   Negative P&L: {negative}")
print(f"   Total updated: {len(trades)}")

conn.close()
