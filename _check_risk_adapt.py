import sqlite3
db = sqlite3.connect('prometheus_learning.db')
db.row_factory = sqlite3.Row

# live_trade_outcomes stats
r = db.execute("SELECT COUNT(*) as cnt, SUM(CASE WHEN outcome='WIN' THEN 1 ELSE 0 END) as wins, ROUND(SUM(pnl),2) as total_pnl, MAX(captured_at) as latest FROM live_trade_outcomes").fetchone()
print('live_trade_outcomes:', dict(r))
win_rate = r['wins'] / r['cnt'] if r['cnt'] else 0
print(f'  Win rate: {win_rate*100:.1f}%  (threshold: 35% low / 60% high)')

# risk_adaptation_log
r2 = db.execute("SELECT COUNT(*) as cnt FROM risk_adaptation_log").fetchone()
print('risk_adaptation_log rows:', r2['cnt'])
if r2['cnt'] > 0:
    rows = db.execute("SELECT * FROM risk_adaptation_log ORDER BY rowid DESC LIMIT 5").fetchall()
    for row in rows:
        print('  ', dict(row))
else:
    print('  (none yet - win rate check requires >=5 trades in last 24h AND win rate <35% or >60%)')
    # Check how many trades in last 24h
    r3 = db.execute("SELECT COUNT(*) as cnt FROM live_trade_outcomes WHERE captured_at > datetime('now','-1 day')").fetchone()
    print(f'  Trades in last 24h: {r3[0]}  (need >=5 to trigger)')

db.close()
