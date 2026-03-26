"""
Backfill exit_price / profit_loss for 478 abandoned trades.

These are BUY entries in trade_history that have no exit_price,
and the position is no longer open at Alpaca — meaning the
position was sold at some point but the exit was never recorded
due to the symbol-format mismatch bug.

Strategy:
  1. Get current Alpaca open positions (the 98 truly-open ones).
  2. For every BUY row with exit_price IS NULL, if the symbol is
     NOT in current open positions, mark it as reconciled with
     the best available data.
  3. Try to find matching SELL rows in trade_history for exit price.
  4. Failing that, use the entry_price as exit (P/L = 0, conservative).
"""

import sqlite3, os
from datetime import datetime

DB = os.path.join(os.path.dirname(__file__), 'prometheus_learning.db')

def symbol_variants(s):
    v = [s]
    if '/' not in s and s.endswith('USD') and len(s) > 3:
        v.append(s[:-3] + '/USD')
    if '/' in s:
        v.append(s.replace('/', ''))
    return v

def main():
    conn = sqlite3.connect(DB, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # ── 1. Get current open positions from Alpaca ──
    # We'll read open_positions table — it's refreshed by the live engine
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='open_positions'")
    open_syms = set()
    if cur.fetchone():
        cur.execute("SELECT DISTINCT symbol FROM open_positions")
        for row in cur.fetchall():
            for v in symbol_variants(row[0]):
                open_syms.add(v)

    print(f"Currently open symbols (will NOT backfill): {open_syms or '{none}'}")

    # ── 2. Find all BUY rows missing exit data ──
    cur.execute("""
        SELECT id, symbol, price, quantity, timestamp, status
        FROM trade_history
        WHERE action = 'BUY'
        AND (exit_price IS NULL OR exit_price = 0)
    """)
    orphans = cur.fetchall()
    print(f"\nTotal BUY rows without exit: {len(orphans)}")

    backfilled = 0
    skipped_open = 0
    used_sell_row = 0
    used_conservative = 0

    for oid, sym, price, qty, ts, status in orphans:
        entry_price = price or 0
        # Skip if position still open
        if sym in open_syms:
            skipped_open += 1
            continue

        variants = symbol_variants(sym)
        placeholders = ','.join('?' * len(variants))

        # Try to find a matching SELL row
        cur.execute(f"""
            SELECT price, timestamp FROM trade_history
            WHERE symbol IN ({placeholders}) AND action = 'SELL'
            AND timestamp > ?
            ORDER BY timestamp ASC LIMIT 1
        """, variants + [ts or '2000-01-01'])

        sell_row = cur.fetchone()
        if sell_row and sell_row[0] and sell_row[0] > 0:
            exit_price = sell_row[0]
            exit_ts = sell_row[1]
            used_sell_row += 1
        else:
            # Conservative fallback: assume break-even
            exit_price = entry_price or 0
            exit_ts = datetime.now().isoformat()
            used_conservative += 1

        pnl = ((exit_price - entry_price) * (qty or 1)) if entry_price else 0

        # Calculate hold duration
        hold_secs = 0
        if ts:
            try:
                hold_secs = int((datetime.fromisoformat(exit_ts) - datetime.fromisoformat(ts)).total_seconds())
            except Exception:
                pass

        cur.execute("""
            UPDATE trade_history
            SET exit_price = ?,
                exit_timestamp = ?,
                profit_loss = ?,
                hold_duration_seconds = ?,
                exit_reason = ?,
                status = 'closed'
            WHERE id = ?
        """, (exit_price, exit_ts, round(pnl, 4), max(hold_secs, 0),
              'BACKFILL_RECONCILED', oid))

        backfilled += 1

    conn.commit()

    # ── 3. Summary ──
    print(f"\n{'='*50}")
    print(f"BACKFILL COMPLETE")
    print(f"{'='*50}")
    print(f"  Backfilled:           {backfilled}")
    print(f"    - From SELL rows:   {used_sell_row}")
    print(f"    - Conservative $0:  {used_conservative}")
    print(f"  Skipped (still open): {skipped_open}")
    print(f"  Total processed:      {backfilled + skipped_open}")

    # Verify
    cur.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NULL OR exit_price = 0")
    remaining = cur.fetchone()[0]
    print(f"\n  Remaining without exit: {remaining}")

    conn.close()

if __name__ == '__main__':
    main()
