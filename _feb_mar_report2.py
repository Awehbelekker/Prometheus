"""Feb-Mar 2026 Trading Report (ASCII safe)"""
import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.environ['PYTHONIOENCODING'] = 'utf-8'
from collections import defaultdict
from datetime import datetime

c = sqlite3.connect('prometheus_learning.db')

print("=" * 80)
print(" PROMETHEUS TRADING REPORT: FEB 1 - MAR 16, 2026")
print("=" * 80)

rows = c.execute("""
    SELECT id, symbol, action, quantity, price, total_value, broker, confidence,
           timestamp, status, profit_loss, exit_price, exit_timestamp, 
           hold_duration_seconds, ai_confidence, exit_reason
    FROM trade_history 
    WHERE timestamp >= '2026-02-01' 
    ORDER BY timestamp ASC
""").fetchall()

print(f"\nTotal trades Feb 1 - now: {len(rows)}")

closed = [r for r in rows if r[11] is not None]
pending = [r for r in rows if r[11] is None]
print(f"Closed: {len(closed)} | Still pending: {len(pending)}")

wins = [r for r in closed if r[10] and r[10] > 0]
losses = [r for r in closed if r[10] and r[10] < 0]
even = [r for r in closed if not r[10] or r[10] == 0]
print(f"Wins: {len(wins)} | Losses: {len(losses)} | Breakeven: {len(even)}")
if closed:
    wr = len(wins) / len(closed) * 100
    print(f"Win Rate (excl breakeven): {len(wins)}/{len(wins)+len(losses)}={len(wins)/(len(wins)+len(losses))*100:.1f}%" if (len(wins)+len(losses))>0 else "")
    print(f"Win Rate (all closed): {wr:.1f}%")

total_pnl = sum(r[10] for r in closed if r[10])
print(f"Total PnL (closed): ${total_pnl:.4f}")

print("\n" + "-" * 80)
print(f"{'SYMBOL':12s} {'TRADES':>7s} {'CLOSED':>7s} {'WINS':>6s} {'LOSS':>6s} {'WIN%':>6s} {'PNL':>12s} {'BROKER':>10s}")
print("-" * 80)

by_sym = defaultdict(list)
for r in rows:
    by_sym[r[1]].append(r)

for sym in sorted(by_sym.keys()):
    trades = by_sym[sym]
    cl = [r for r in trades if r[11] is not None]
    w = len([r for r in cl if r[10] and r[10] > 0])
    l = len([r for r in cl if r[10] and r[10] < 0])
    pnl = sum(r[10] for r in cl if r[10])
    brokers = set(r[6] for r in trades if r[6])
    wr_s = f"{w/(w+l)*100:.0f}%" if (w+l)>0 else "--"
    print(f"{sym:12s} {len(trades):7d} {len(cl):7d} {w:6d} {l:6d} {wr_s:>6s} ${pnl:>11.4f} {','.join(brokers) or '--':>10s}")

print("\n" + "-" * 80)
print("BY WEEK:")
print("-" * 80)
by_week = defaultdict(list)
for r in rows:
    try:
        dt = datetime.fromisoformat(r[8])
        wk = dt.strftime('%Y-W%U')
        by_week[wk].append(r)
    except:
        pass

for wk in sorted(by_week.keys()):
    trades = by_week[wk]
    cl = [r for r in trades if r[11] is not None]
    w = len([r for r in cl if r[10] and r[10] > 0])
    l = len([r for r in cl if r[10] and r[10] < 0])
    pnl = sum(r[10] for r in cl if r[10])
    syms = list(set(r[1] for r in trades))
    print(f"  {wk}: {len(trades)} trades, {len(cl)} closed, {w}W/{l}L, PnL: ${pnl:.4f} -- {', '.join(syms[:6])}")

print("\n" + "-" * 80)
print("LAST 30 TRADES (NEWEST FIRST):")
print("-" * 80)
print(f"{'DATE':20s} {'SYM':10s} {'ACT':5s} {'PRICE':>10s} {'EXIT':>10s} {'PNL':>10s} {'STATUS':8s} {'BROKER':10s}")
for r in reversed(rows[-30:]):
    ts = (r[8][:16] if r[8] else '?').replace('T',' ')
    sym = r[1] or '?'
    act = r[2] or '?'
    price = f"${r[4]:.2f}" if r[4] else '--'
    exit_p = f"${r[11]:.2f}" if r[11] else '--'
    pnl = f"${r[10]:.4f}" if r[10] else '--'
    status = r[9] or '?'
    broker = r[6] or '?'
    print(f"{ts:20s} {sym:10s} {act:5s} {price:>10s} {exit_p:>10s} {pnl:>10s} {status:8s} {broker:10s}")

print(f"\n" + "-" * 80)
print(f"PENDING/OPEN ORDERS ({len(pending)}):")
print("-" * 80)
for r in pending:
    ts = (r[8][:16] if r[8] else '?').replace('T',' ')
    print(f"  {ts} | {r[1]:10s} | {r[2]:5s} | ${r[4]:.2f} | broker={r[6]} | conf={r[7]}")

print(f"\n" + "=" * 80)
print(f" ALL-TIME STATS")
print("=" * 80)
all_rows = c.execute("SELECT COUNT(*) FROM trade_history").fetchone()[0]
all_closed = c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL").fetchone()[0]
all_wins = c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL").fetchone()[0]
all_losses = c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss < 0 AND exit_price IS NOT NULL").fetchone()[0]
all_pnl = c.execute("SELECT COALESCE(SUM(profit_loss), 0) FROM trade_history WHERE exit_price IS NOT NULL").fetchone()[0]
all_pending = c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NULL").fetchone()[0]
print(f"Total trades: {all_rows}")
print(f"Closed: {all_closed} | Pending: {all_pending}")
if all_closed:
    print(f"Wins: {all_wins} | Losses: {all_losses} | Win Rate: {all_wins/(all_wins+all_losses)*100:.1f}%" if (all_wins+all_losses) else "")
print(f"Total PnL: ${all_pnl:.4f}")
last = c.execute("SELECT MAX(timestamp) FROM trade_history").fetchone()[0]
print(f"Last trade: {last}")
try:
    days_ago = (datetime.now() - datetime.fromisoformat(last)).days
    print(f"Days since last trade: {days_ago}")
except: pass

c.close()
