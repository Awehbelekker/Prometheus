#!/usr/bin/env python3
"""Reset shadow trading and paper trading stats for fresh start with $100K paper account."""
import sqlite3
import sys

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# List all tables with counts
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
print("=== CURRENT DB STATE ===")
for t in tables:
    c.execute(f'SELECT COUNT(*) FROM [{t}]')
    cnt = c.fetchone()[0]
    print(f"  {t}: {cnt} rows")

# All shadow/paper tables to reset for fresh start
reset_tables = [
    'shadow_sessions',          # Shadow session configs
    'shadow_trades',            # Shadow trade records (if exists)
    'shadow_trade_history',     # Shadow trade history
    'shadow_position_tracking', # Shadow position tracking
    'multi_strategy_leaderboard', # Multi-strategy leaderboard
    'multi_strategy_snapshots',   # Multi-strategy snapshots
    'position_tracking',        # Enhancement position tracking (trailing stop, DCA etc)
    'live_shadow_comparison',   # Live vs shadow comparison
    'open_positions',           # Open position records (stale from old session)
    'position_stops',           # Position stop loss tracking
]

print("\n=== TABLES TO RESET ===")
for t in reset_tables:
    if t in tables:
        c.execute(f'SELECT COUNT(*) FROM [{t}]')
        cnt = c.fetchone()[0]
        print(f"  {t}: {cnt} rows -> 0")

if '--execute' in sys.argv:
    print("\n=== EXECUTING RESET ===")
    for t in reset_tables:
        if t in tables:
            c.execute(f'DELETE FROM [{t}]')
            print(f"  Cleared {t}")
    
    db.commit()
    print("\n  Shadow & paper stats reset complete!")
    print("  Ready for fresh $100K paper trading session")
else:
    print("\n  DRY RUN - pass --execute to actually reset")

db.close()
