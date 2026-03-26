"""
One-time data repair:
  1. Backfill shadow_sessions totals from shadow_trade_history
  2. Backfill ai_attribution outcomes from known closed trades
"""
import sqlite3
from datetime import datetime

conn = sqlite3.connect("prometheus_learning.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# ── 1. Backfill shadow_sessions ───────────────────────────────────────────────
print("Backfilling shadow_sessions metrics from shadow_trade_history...")
sessions = cur.execute("SELECT session_id FROM shadow_sessions").fetchall()
updated = 0
for (session_id,) in [(r['session_id'],) for r in sessions]:
    r = cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status IN ('CLOSED','closed') AND pnl IS NOT NULL THEN 1 ELSE 0 END) as closed_n,
            SUM(CASE WHEN status IN ('CLOSED','closed') AND pnl > 0 THEN 1 ELSE 0 END) as wins,
            COALESCE(SUM(CASE WHEN pnl IS NOT NULL THEN pnl ELSE 0 END), 0) as total_pnl
        FROM shadow_trade_history
        WHERE session_id = ?
    """, (session_id,)).fetchone()
    closed_n = int(r['closed_n'] or 0)
    wins     = int(r['wins'] or 0)
    total_pnl = float(r['total_pnl'] or 0)
    win_rate  = wins / closed_n if closed_n > 0 else 0
    cur.execute("""
        UPDATE shadow_sessions
        SET total_trades   = ?,
            winning_trades = ?,
            total_pnl      = ?,
            win_rate       = ?,
            status         = CASE WHEN ? > 0 THEN 'COMPLETED' ELSE 'ACTIVE' END,
            last_active    = ?
        WHERE session_id = ?
    """, (closed_n, wins, total_pnl, win_rate, closed_n,
          datetime.now().isoformat(), session_id))
    if closed_n > 0:
        updated += 1

conn.commit()
print(f"  Updated {updated} sessions with closed-trade data")

# Verify
r = conn.execute("""
    SELECT SUM(total_trades) as t, SUM(winning_trades) as w,
           SUM(total_pnl) as pnl, AVG(win_rate) as wr
    FROM shadow_sessions
""").fetchone()
print(f"  Sessions totals: trades={r['t']}, wins={r['w']}, "
      f"pnl=${float(r['pnl'] or 0):+.4f}, avg_wr={float(r['wr'] or 0)*100:.1f}%")

# ── 2. Backfill ai_attribution from trade_history ────────────────────────────
print("\nBackfilling ai_attribution outcomes from trade_history...")
# Find closed trades with known P/L
closed = conn.execute("""
    SELECT symbol, profit_loss, exit_price, exit_timestamp
    FROM trade_history
    WHERE profit_loss IS NOT NULL AND profit_loss != 0
      AND exit_price IS NOT NULL AND exit_price != 0
    ORDER BY exit_timestamp DESC
""").fetchall()
attr_updated = 0
for row in closed:
    sym = row['symbol']
    pnl = float(row['profit_loss'])
    # entry_price can be inferred - get avg entry price from ai_attribution
    entry = conn.execute("""
        SELECT AVG(entry_price) FROM ai_attribution
        WHERE symbol = ? AND outcome_recorded = 0 LIMIT 1
    """, (sym,)).fetchone()[0]
    pnl_pct = (pnl / float(entry)) * 100 if entry and float(entry) > 0 else 0.0

    result = conn.execute("""
        UPDATE ai_attribution
        SET eventual_pnl = ?, pnl_pct = ?, outcome_recorded = 1
        WHERE id IN (
            SELECT id FROM ai_attribution
            WHERE symbol = ? AND outcome_recorded = 0
            ORDER BY timestamp DESC LIMIT 5
        )
    """, (pnl, pnl_pct, sym))
    attr_updated += result.rowcount

conn.commit()
print(f"  Updated {attr_updated} ai_attribution rows with outcomes")

# Verify
r = conn.execute("""
    SELECT COUNT(*) as total,
           SUM(outcome_recorded) as with_outcome,
           ROUND(SUM(outcome_recorded)*100.0/COUNT(*),2) as pct
    FROM ai_attribution
""").fetchone()
print(f"  ai_attribution: {r['with_outcome']}/{r['total']} have outcomes ({r['pct']}%)")

# ── 3. Populate ai_system_metrics from ai_attribution outcomes ────────────────
print("\nPopulating ai_system_metrics from recorded outcomes...")
rows = conn.execute("""
    SELECT ai_system,
           COUNT(*) as total_sigs,
           SUM(outcome_recorded) as executed,
           SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(CASE WHEN eventual_pnl <= 0 AND outcome_recorded=1 THEN 1 ELSE 0 END) as losses,
           COALESCE(SUM(eventual_pnl),0) as total_pnl,
           CASE WHEN SUM(outcome_recorded)>0
                THEN ROUND(SUM(CASE WHEN eventual_pnl>0 THEN 1.0 ELSE 0 END)/SUM(outcome_recorded),4)
                ELSE 0 END as win_rate,
           CASE WHEN SUM(outcome_recorded)>0
                THEN COALESCE(SUM(eventual_pnl),0)/SUM(outcome_recorded)
                ELSE 0 END as avg_pnl
    FROM ai_attribution
    GROUP BY ai_system
""").fetchall()
today = datetime.now().strftime('%Y-%m-%d')
for r in rows:
    conn.execute("""
        INSERT OR REPLACE INTO ai_system_metrics
            (date, ai_system, total_signals, signals_executed,
             winning_trades, losing_trades, total_pnl, win_rate, avg_pnl, sharpe_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (today, r['ai_system'], r['total_sigs'], r['executed'],
          r['wins'], r['losses'], r['total_pnl'], r['win_rate'], r['avg_pnl']))

conn.commit()
n = conn.execute("SELECT COUNT(*) FROM ai_system_metrics").fetchone()[0]
print(f"  ai_system_metrics now has {n} rows")

print("\nAll backfills complete.")
conn.close()
