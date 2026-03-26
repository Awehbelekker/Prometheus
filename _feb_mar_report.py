"""Feb-Mar 2026 Trading Report"""
import sqlite3
from collections import defaultdict

c = sqlite3.connect('prometheus_learning.db')

print("=" * 80)
print(" PROMETHEUS TRADING REPORT: FEB 1 - MAR 16, 2026")
print("=" * 80)

# All trades from Feb onward
rows = c.execute("""
    SELECT id, symbol, action, quantity, price, total_value, broker, confidence,
           timestamp, status, profit_loss, exit_price, exit_timestamp, 
           hold_duration_seconds, ai_confidence, exit_reason
    FROM trade_history 
    WHERE timestamp >= '2026-02-01' 
    ORDER BY timestamp ASC
""").fetchall()

print(f"\nTotal trades Feb 1 - now: {len(rows)}")

# Separate closed vs pending
closed = [r for r in rows if r[11] is not None]  # has exit_price
pending = [r for r in rows if r[11] is None]
print(f"Closed: {len(closed)} | Still pending: {len(pending)}")

# Win/Loss for closed
wins = [r for r in closed if r[10] and r[10] > 0]
losses = [r for r in closed if r[10] and r[10] < 0]
even = [r for r in closed if not r[10] or r[10] == 0]
print(f"Wins: {len(wins)} | Losses: {len(losses)} | Breakeven: {len(even)}")
if closed:
    wr = len(wins) / len(closed) * 100
    print(f"Win Rate: {wr:.1f}%")

# PnL
total_pnl = sum(r[10] for r in closed if r[10])
print(f"Total PnL (closed): ${total_pnl:.4f}")

# By symbol
print(f"\n{'─' * 80}")
print(f"{'SYMBOL':12s} {'TRADES':>7s} {'CLOSED':>7s} {'WINS':>6s} {'LOSSES':>7s} {'WIN%':>6s} {'PNL':>12s} {'BROKER':>10s}")
print(f"{'─' * 80}")

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
    wr_s = f"{w/len(cl)*100:.0f}%" if cl else "—"
    print(f"{sym:12s} {len(trades):7d} {len(cl):7d} {w:6d} {l:7d} {wr_s:>6s} ${pnl:>11.4f} {','.join(brokers) or '—':>10s}")

# By week
print(f"\n{'─' * 80}")
print("BY WEEK:")
print(f"{'─' * 80}")
by_week = defaultdict(list)
for r in rows:
    ts = r[8][:10] if r[8] else 'unknown'
    # ISO week
    from datetime import datetime
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
    pnl = sum(r[10] for r in cl if r[10])
    syms = list(set(r[1] for r in trades))
    print(f"  {wk}: {len(trades)} trades, {len(cl)} closed, {w} wins, PnL: ${pnl:.4f} — {', '.join(syms[:6])}")

# Recent trades detail
print(f"\n{'─' * 80}")
print("RECENT TRADES (NEWEST FIRST):")
print(f"{'─' * 80}")
print(f"{'DATE':22s} {'SYM':10s} {'ACT':5s} {'PRICE':>12s} {'EXIT':>12s} {'PNL':>10s} {'STATUS':8s} {'BROKER':10s}")
for r in reversed(rows[-30:]):
    ts = r[8][:19] if r[8] else '?'
    sym = r[1] or '?'
    act = r[2] or '?'
    price = f"${r[4]:.2f}" if r[4] else '—'
    exit_p = f"${r[11]:.2f}" if r[11] else '—'
    pnl = f"${r[10]:.4f}" if r[10] else '—'
    status = r[9] or '?'
    broker = r[6] or '?'
    print(f"{ts:22s} {sym:10s} {act:5s} {price:>12s} {exit_p:>12s} {pnl:>10s} {status:8s} {broker:10s}")

# Pending orders that should be resolved
print(f"\n{'─' * 80}")
print(f"PENDING/OPEN ORDERS ({len(pending)}):")
print(f"{'─' * 80}")
for r in pending:
    ts = r[8][:19] if r[8] else '?'
    print(f"  {ts} | {r[1]:10s} | {r[2]:5s} | ${r[4]:.2f} | broker={r[6]} | conf={r[7]}")

# Overall stats
print(f"\n{'═' * 80}")
print(f" OVERALL ALL-TIME STATS")
print(f"{'═' * 80}")
all_rows = c.execute("SELECT COUNT(*) FROM trade_history").fetchone()[0]
all_closed = c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL").fetchone()[0]
all_wins = c.execute("SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0 AND exit_price IS NOT NULL").fetchone()[0]
all_pnl = c.execute("SELECT COALESCE(SUM(profit_loss), 0) FROM trade_history WHERE exit_price IS NOT NULL").fetchone()[0]
all_pending = c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NULL").fetchone()[0]
print(f"Total trades: {all_rows}")
print(f"Closed: {all_closed} | Pending: {all_pending}")
print(f"Wins: {all_wins} | Win Rate: {all_wins/all_closed*100:.1f}%" if all_closed else "No closed trades")
print(f"Total PnL: ${all_pnl:.4f}")

# Last trade date
last = c.execute("SELECT MAX(timestamp) FROM trade_history").fetchone()[0]
print(f"Last trade: {last}")
print(f"Days since last trade: {(datetime.now() - datetime.fromisoformat(last)).days}")

c.close()
