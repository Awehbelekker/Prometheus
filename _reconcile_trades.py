"""
Trade History Reconciliation Script
Marks old BUY trades as reconciled when the position no longer exists.
"""
import sqlite3
from datetime import datetime

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# Get currently open positions
c.execute('SELECT symbol FROM open_positions')
open_syms = set(r[0] for r in c.fetchall())
print(f"Currently open positions: {sorted(open_syms)}")

# Find BUY trades without exit data
c.execute("""
    SELECT symbol, COUNT(*), MIN(timestamp), MAX(timestamp)
    FROM trade_history 
    WHERE action = 'BUY' AND (exit_price IS NULL OR profit_loss = 0)
    GROUP BY symbol ORDER BY COUNT(*) DESC
""")
rows = c.fetchall()

print(f"\nBUY trades without exit data by symbol:")
total_to_reconcile = 0
for r in rows:
    status = 'OPEN' if r[0] in open_syms else 'CLOSED'
    print(f"  {r[0]}: {r[1]} trades ({str(r[2])[:10]} to {str(r[3])[:10]}) - {status}")
    if r[0] not in open_syms:
        total_to_reconcile += r[1]

# For CLOSED positions: keep the MOST RECENT BUY trade open (in case it matches current position under different symbol format)
# For symbols not in open_positions, mark ALL their BUY trades as reconciled
print(f"\nTrades to reconcile (position no longer exists): {total_to_reconcile}")

# Also: For OPEN positions with multiple BUY trades, keep only the LATEST one open
# (the older ones were previous round-trips that got sold)
open_to_reconcile = 0
for r in rows:
    if r[0] in open_syms and r[1] > 1:
        open_to_reconcile += r[1] - 1  # Keep latest, reconcile the rest
        print(f"  {r[0]}: {r[1]-1} old BUY trades for current open position")

print(f"Old round-trip trades for open positions: {open_to_reconcile}")
print(f"Total reconciliation target: {total_to_reconcile + open_to_reconcile}")

# Execute reconciliation
now = datetime.now().isoformat()

# 1. Mark all BUY trades for CLOSED positions
for r in rows:
    sym = r[0]
    if sym not in open_syms:
        c.execute("""
            UPDATE trade_history 
            SET exit_reason = 'RECONCILED_2026_03_AUDIT',
                exit_timestamp = ?
            WHERE symbol = ? AND action = 'BUY' 
            AND (exit_price IS NULL OR profit_loss = 0)
        """, (now, sym))
        print(f"  Reconciled {c.rowcount} trades for {sym}")

# 2. For OPEN positions with multiple BUY trades, keep only the latest
for r in rows:
    sym = r[0]
    if sym in open_syms and r[1] > 1:
        # Get the ID of the latest BUY trade (keep this one)
        c.execute("""
            SELECT id FROM trade_history 
            WHERE symbol = ? AND action = 'BUY' 
            AND (exit_price IS NULL OR profit_loss = 0)
            ORDER BY timestamp DESC LIMIT 1
        """, (sym,))
        latest_id = c.fetchone()[0]
        
        # Mark all older ones as reconciled
        c.execute("""
            UPDATE trade_history 
            SET exit_reason = 'RECONCILED_OLD_ROUNDTRIP',
                exit_timestamp = ?
            WHERE symbol = ? AND action = 'BUY' 
            AND (exit_price IS NULL OR profit_loss = 0)
            AND id != ?
        """, (now, sym, latest_id))
        print(f"  Reconciled {c.rowcount} old round-trip trades for {sym} (kept latest id={latest_id})")

db.commit()

# Verify
c.execute("SELECT COUNT(*) FROM trade_history WHERE action = 'BUY' AND exit_price IS NULL AND profit_loss = 0 AND exit_reason IS NULL")
remaining = c.fetchone()[0]
print(f"\nRemaining unreconciled BUY trades: {remaining}")

db.close()
print("Done.")
