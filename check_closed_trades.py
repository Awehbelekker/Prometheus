import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

# Count closed trades
cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='closed'")
closed_count = cursor.fetchone()[0]
print(f"✅ Closed trades: {closed_count}")

# Count pending trades
cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='pending'")
pending_count = cursor.fetchone()[0]
print(f"⏳ Pending trades: {pending_count}")

# Show closed trades
print("\n📊 CLOSED TRADES:")
print("=" * 80)
cursor.execute("""
    SELECT symbol, price, exit_price, profit_loss, action, 
           hold_duration_seconds
    FROM trade_history 
    WHERE status='closed' 
    ORDER BY timestamp DESC
""")

total_pnl = 0
for row in cursor.fetchall():
    symbol, entry, exit, pnl, action, duration = row
    pct = ((exit - entry) / entry * 100) if entry else 0
    hours = duration / 3600 if duration else 0
    total_pnl += pnl if pnl else 0
    
    emoji = "💰" if pnl and pnl > 0 else "📉"
    print(f"{emoji} {symbol:12} {action:4} | Entry: ${entry:8.2f} → Exit: ${exit:8.2f}")
    print(f"   P&L: ${pnl:7.2f} ({pct:+.2f}%) | TIME_EXIT | {hours:.1f} hours")
    print()

print("=" * 80)
print(f"💵 Total P&L: ${total_pnl:.2f}")

conn.close()
