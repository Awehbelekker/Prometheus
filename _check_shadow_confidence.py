import sqlite3

conn = sqlite3.connect("prometheus_learning.db")
cur = conn.cursor()

print("=== CLOSED SHADOW TRADES LAST 5D (CONFIDENCE) ===")
cur.execute(
    """
    SELECT symbol, action, ROUND(confidence,4), ROUND(pnl,2), exit_reason, timestamp, exit_time
    FROM shadow_trade_history
    WHERE status='CLOSED' AND exit_time >= datetime('now','-5 day')
    ORDER BY exit_time DESC
    """
)
rows = cur.fetchall()
for r in rows:
    print(r)

print("\n=== CONFIDENCE BUCKETS (LAST 5D CLOSED SHADOW) ===")
cur.execute(
    """
    SELECT
      CASE
        WHEN confidence >= 0.80 THEN '0.80+'
        WHEN confidence >= 0.70 THEN '0.70-0.79'
        WHEN confidence >= 0.60 THEN '0.60-0.69'
        ELSE '<0.60'
      END AS bucket,
      COUNT(*) as n,
      ROUND(AVG(pnl),2) as avg_pnl,
      ROUND(SUM(pnl),2) as total_pnl
    FROM shadow_trade_history
    WHERE status='CLOSED' AND exit_time >= datetime('now','-5 day')
    GROUP BY bucket
    ORDER BY bucket DESC
    """
)
for r in cur.fetchall():
    print(r)

print("\n=== SIGNAL_PREDICTIONS OUTCOME_RECORDED LAST 5D ===")
cur.execute(
    """
    SELECT outcome_recorded, COUNT(*), MIN(timestamp), MAX(timestamp)
    FROM signal_predictions
    WHERE timestamp >= datetime('now','-5 day')
    GROUP BY outcome_recorded
    ORDER BY outcome_recorded
    """
)
for r in cur.fetchall():
    print(r)

conn.close()
