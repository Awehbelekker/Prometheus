import sqlite3

db = sqlite3.connect('prometheus_learning.db')

# 1. Win rate trend
r = db.execute('''
SELECT 
  (SELECT COUNT(*) FROM live_trade_outcomes WHERE outcome='WIN' AND captured_at > datetime('now','-7 days')) as wins_7d,
  (SELECT COUNT(*) FROM live_trade_outcomes WHERE captured_at > datetime('now','-7 days')) as total_7d,
  (SELECT COUNT(*) FROM live_trade_outcomes WHERE outcome='WIN') as wins_all,
  (SELECT COUNT(*) FROM live_trade_outcomes) as total_all
''').fetchone()

print('=== TRADING PERFORMANCE ===')
w7, t7, wa, ta = r
print(f'Last 7 days: {w7}/{t7} = {(w7/t7*100) if t7 else 0:.1f}%')
print(f'All-time: {wa}/{ta} = {(wa/ta*100) if ta else 0:.1f}%')

# 2. Signal backfill
try:
    r2 = db.execute('''
    SELECT 
      SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) as outcomes_marked,
      COUNT(*) as total_predictions
    FROM signal_predictions
    WHERE created_at > datetime('now','-7 days')
    ''').fetchone()
    
    marked, total = r2
    print(f'\nSignal Backfill (7d): {marked}/{total} = {(marked/total*100) if total else 0:.1f}%')
except Exception as e:
    print(f'\nSignal Backfill: query error - {e}')

# 3. Hold time & exits
r3 = db.execute('''
SELECT 
  AVG(hold_seconds) as avg_hold_sec,
  SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as exits_profit,
  SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as exits_loss,
  SUM(CASE WHEN pnl = 0 THEN 1 ELSE 0 END) as exits_breakeven
FROM live_trade_outcomes
''').fetchone()

avg_s, wins_cnt, loss_cnt, breakeven_cnt = r3
print(f'\nTrade Duration: avg {avg_s:.0f}s ({avg_s/60:.1f}m)')
print(f'Exit Distribution: +{wins_cnt} / -{loss_cnt} / ={breakeven_cnt}')

# 4. Worst symbols
r4 = db.execute('''
SELECT symbol, COUNT(*) as cnt, ROUND(SUM(pnl),2) as total_pnl, ROUND(AVG(pnl),2) as avg_pnl
FROM live_trade_outcomes 
WHERE pnl < 0
GROUP BY symbol
ORDER BY AVG(pnl)
LIMIT 5
''').fetchall()

print(f'\nWorst Performers:')
for sym, cnt, tp, avg in r4:
    print(f'  {sym}: {cnt} trades, avg {avg:.2f} ({tp:.2f} total)')

db.close()
