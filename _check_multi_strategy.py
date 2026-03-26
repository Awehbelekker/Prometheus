"""Check multi-strategy shadow trading sessions and trades"""
import sqlite3

conn = sqlite3.connect('prometheus_learning.db')
cur = conn.cursor()

print("=== MULTI-STRATEGY SESSIONS (Recent 10) ===")
cur.execute('SELECT session_id, config_name, starting_capital, total_trades, total_pnl, status, started_at FROM shadow_sessions ORDER BY id DESC LIMIT 10')
cols = [d[0] for d in cur.description]
for row in cur.fetchall():
    d = dict(zip(cols, row))
    cn = d['config_name'] or 'default'
    sid = d['session_id'] or ''
    print(f"  {cn:20s} | trades={d['total_trades']:3d} | P/L=${d['total_pnl']:8.2f} | {d['status']:8s} | {sid[:50]}")

print("\n=== ALL SHADOW TRADES ===")
cur.execute('SELECT session_id, symbol, action, quantity, entry_price, confidence, status, reason FROM shadow_trade_history ORDER BY id DESC')
rows = cur.fetchall()
if not rows:
    print("  No shadow trades yet")
else:
    for row in rows:
        sid = (row[0] or '')[:45]
        sym = row[1] or '?'
        act = row[2] or '?'
        qty = row[3] or 0
        px = row[4] or 0
        conf = row[5] or 0
        st = row[6] or '?'
        reason = (row[7] or '')[:60]
        print(f"  {sid:45s} | {sym:6s} {act:4s} x{qty:5.0f} @ ${px:8.2f} | conf={conf:.2f} | {st} | {reason}")

print(f"\n  Total shadow trades: {len(rows)}")
conn.close()
