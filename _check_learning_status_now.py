import sqlite3, json

db = sqlite3.connect('prometheus_learning.db')
db.row_factory = sqlite3.Row

results = {}

# 1. learning_outcomes - did Phase 5 write new rows past the old latest?
r = db.execute("SELECT COUNT(*) as cnt, MAX(timestamp) as latest FROM learning_outcomes WHERE timestamp > '2026-03-16 14:45'").fetchone()
results['learning_outcomes_new_rows'] = dict(r)

r_total = db.execute("SELECT COUNT(*) as cnt, MAX(timestamp) as latest FROM learning_outcomes").fetchone()
results['learning_outcomes_total'] = dict(r_total)

# 2. risk_adaptation_log
r2 = db.execute("SELECT COUNT(*) as cnt, MAX(timestamp) as latest FROM risk_adaptation_log").fetchone()
results['risk_adaptation_log'] = dict(r2)

# 3. signal_predictions outcome backfill status
r3 = db.execute("SELECT outcome_recorded, COUNT(*) as cnt FROM signal_predictions GROUP BY outcome_recorded").fetchall()
results['signal_predictions_backfill'] = [dict(x) for x in r3]

# 4. shadow_trade_history recent closes (column is exit_time)
r4 = db.execute("SELECT COUNT(*) as cnt, MAX(exit_time) as latest_close FROM shadow_trade_history WHERE exit_time > '2026-03-18'").fetchone()
results['shadow_recent_closes'] = dict(r4)

# 5. live_trade_outcomes
try:
    r5 = db.execute("SELECT COUNT(*) as cnt, MAX(timestamp) as latest FROM live_trade_outcomes").fetchone()
    results['live_trade_outcomes'] = dict(r5)
except Exception as e:
    results['live_trade_outcomes'] = f'error: {e}'

# 6. learning_patterns
r6 = db.execute("SELECT COUNT(*) as cnt, MAX(created_at) as latest FROM learning_patterns WHERE created_at > '2026-03-16'").fetchone()
results['learning_patterns_recent'] = dict(r6)

db.close()
print(json.dumps(results, indent=2))
