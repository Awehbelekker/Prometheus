import sqlite3
import json

db = sqlite3.connect('prometheus_learning.db')
db.row_factory = sqlite3.Row

# Compare confidence buckets against actual outcomes
print("=== CONFIDENCE CALIBRATION AUDIT ===\n")

# Last 7 days confidence distribution
r = db.execute("""
SELECT 
  ROUND(confidence, 1) as conf_bucket,
  COUNT(*) as signal_count,
  SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) as outcomes_marked
FROM signal_predictions
WHERE timestamp > datetime('now', '-7 days')
GROUP BY ROUND(confidence, 1)
ORDER BY conf_bucket DESC
""").fetchall()

print("Signal Confidence Distribution (7d):")
for row in r:
    marked = row['outcomes_marked'] or 0
    total = row['signal_count']
    pct = (marked / total * 100) if total else 0
    print(f"  Confidence {row['conf_bucket']}: {total} signals, {marked} outcomes marked ({pct:.0f}%)")

print("\n")

# Shadow trades: confidence at entry vs outcome
r2 = db.execute("""
SELECT 
  CASE WHEN pnl > 0 THEN 'WIN' ELSE 'LOSS' END as outcome,
  COUNT(*) as cnt,
  ROUND(AVG(confidence), 3) as avg_entry_conf,
  MIN(confidence) as min_conf,
  MAX(confidence) as max_conf,
  ROUND(AVG(pnl), 2) as avg_pnl
FROM shadow_trade_history
WHERE exit_price IS NOT NULL
GROUP BY CASE WHEN pnl > 0 THEN 'WIN' ELSE 'LOSS' END
""").fetchall()

print("Shadow Trades: Confidence at Entry vs Outcome:")
for row in r2:
    print(f"  {row['outcome']}: {row['cnt']} trades")
    print(f"    Avg entry confidence: {row['avg_entry_conf']}")
    print(f"    Range: {row['min_conf']:.3f} - {row['max_conf']:.3f}")
    print(f"    Avg P&L: ${row['avg_pnl']:.2f}")

# Check if winners had higher confidence than losers
wins_conf = db.execute("SELECT AVG(confidence) as conf FROM shadow_trade_history WHERE pnl > 0").fetchone()['conf']
loss_conf = db.execute("SELECT AVG(confidence) as conf FROM shadow_trade_history WHERE pnl < 0").fetchone()['conf']

print(f"\n--- Confidence Gap Analysis ---")
print(f"Winners avg confidence: {wins_conf:.3f}" if wins_conf else "Winners: no data")
print(f"Losers avg confidence: {loss_conf:.3f}" if loss_conf else "Losers: no data")
if wins_conf and loss_conf:
    diff = abs(wins_conf - loss_conf)
    print(f"Difference: {diff:.3f} (0 = bad calibration)")

    if diff < 0.05:
        print("⚠️ PROBLEM: Confidence does NOT differentiate between wins/losses!")
        print("   System is overconfident—confidence signal is broken or not predictive.")
    else:
        print("✓ OK: Confidence signal is somewhat predictive.")


# Top losing trades: what was their confidence?
print("\n--- Top Losers by Confidence ---")
r3 = db.execute("""
SELECT symbol, confidence, pnl, pnl_pct, entry_price, exit_price
FROM shadow_trade_history
WHERE pnl < 0
ORDER BY confidence DESC
LIMIT 5
""").fetchall()

for row in r3:
    print(f"  {row['symbol']}: conf={row['confidence']:.2f}, PnL=${row['pnl']:.2f}")

db.close()
