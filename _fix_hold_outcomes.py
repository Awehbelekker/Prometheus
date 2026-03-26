"""
One-time fix: backfill was_correct for HOLD predictions in learning_outcomes.
Previously was_correct was always False for HOLD (no HOLD branch in the formula).
New rule: HOLD is correct if |profit_pct| < 1.0%  (price barely moved — holding was right).
"""
import sqlite3

conn = sqlite3.connect("prometheus_learning.db")
cursor = conn.cursor()

# Check current state
before = cursor.execute(
    "SELECT COUNT(*) FROM learning_outcomes WHERE predicted_action='HOLD' AND was_correct=1"
).fetchone()[0]
total_hold = cursor.execute(
    "SELECT COUNT(*) FROM learning_outcomes WHERE predicted_action='HOLD'"
).fetchone()[0]
print(f"Before: {before}/{total_hold} HOLD outcomes marked correct")

# Fix: HOLD correct if |profit_pct| < 1.0
cursor.execute("""
    UPDATE learning_outcomes
    SET was_correct = CASE
        WHEN ABS(COALESCE(profit_pct, 0)) < 1.0 THEN 1
        ELSE 0
    END
    WHERE predicted_action = 'HOLD'
""")
conn.commit()

after = cursor.execute(
    "SELECT COUNT(*) FROM learning_outcomes WHERE predicted_action='HOLD' AND was_correct=1"
).fetchone()[0]
print(f"After:  {after}/{total_hold} HOLD outcomes marked correct")

# Show overall accuracy now
r = cursor.execute("""
    SELECT
        COUNT(*) as total,
        SUM(was_correct) as correct,
        ROUND(SUM(was_correct)*100.0/COUNT(*), 1) as pct
    FROM learning_outcomes
""").fetchone()
print(f"\nOverall accuracy: {r[1]}/{r[0]}  ({r[2]}%)")

# Breakdown by action
print("\nBy predicted action:")
rows = cursor.execute("""
    SELECT predicted_action,
           COUNT(*) as n,
           SUM(was_correct) as correct,
           ROUND(SUM(was_correct)*100.0/COUNT(*),1) as pct
    FROM learning_outcomes
    GROUP BY predicted_action
""").fetchall()
for row in rows:
    print(f"  {row[0]:<5}: {row[2]}/{row[1]}  ({row[3]}%)")

conn.close()
print("\nDone.")
