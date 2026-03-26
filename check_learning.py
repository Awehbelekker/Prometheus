import sqlite3
conn = sqlite3.connect('prometheus_learning.db')
cur = conn.cursor()

print("=== AI SYSTEM WEIGHTS ===")
try:
    cur.execute('SELECT system_name, adaptive_weight FROM ai_system_weights ORDER BY adaptive_weight DESC')
    for name, weight in cur.fetchall():
        bar = '#' * int(weight * 20)
        trend = 'STRONG' if weight > 1.1 else 'WEAK' if weight < 0.9 else 'NEUTRAL'
        print(f'  {name:25s} {weight:.3f}x  {bar}  [{trend}]')
except Exception as e:
    print(f'Error: {e}')

print("\n=== LEARNING OUTCOMES ===")
try:
    cur.execute('SELECT COUNT(*) FROM learning_outcomes')
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM learning_outcomes WHERE was_correct=1')
    correct = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM learning_outcomes WHERE was_correct=0')
    wrong = cur.fetchone()[0]
    print(f'Total: {total}, Correct: {correct}, Wrong: {wrong}')
    if correct+wrong > 0:
        print(f'Accuracy: {correct/(correct+wrong)*100:.1f}%')
    cur.execute('SELECT AVG(profit_loss), SUM(profit_loss) FROM learning_outcomes WHERE profit_loss IS NOT NULL')
    r = cur.fetchone()
    if r[0]: print(f'Avg P/L: ${r[0]:.4f}, Total: ${r[1]:.2f}')
except Exception as e:
    print(f'Error: {e}')

print("\n=== SHADOW TRADE SUMMARY ===")
try:
    cur.execute('SELECT COUNT(*) FROM shadow_trade_history')
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='CLOSED'")
    closed = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='OPEN'")
    opened = cur.fetchone()[0]
    print(f'Total: {total}, Open: {opened}, Closed: {closed}')
    if closed > 0:
        cur.execute("SELECT COUNT(*) FROM shadow_trade_history WHERE status='CLOSED' AND pnl > 0")
        wins = cur.fetchone()[0]
        cur.execute("SELECT SUM(pnl), AVG(pnl), AVG(pnl_pct) FROM shadow_trade_history WHERE status='CLOSED'")
        r = cur.fetchone()
        print(f'Win rate: {wins}/{closed} = {wins/closed*100:.1f}%')
        print(f'Total P/L: ${r[0]:.2f}, Avg: ${r[1]:.2f}, Avg%: {r[2]:.2f}%')
except Exception as e:
    print(f'Error: {e}')

print("\n=== LIVE TRADES ===")
try:
    cur.execute('SELECT COUNT(*) FROM trade_history')
    total = cur.fetchone()[0]
    print(f'Total live trades: {total}')
    if total > 0:
        cur.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0')
        wins = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss < 0')
        losses = cur.fetchone()[0]
        cur.execute('SELECT SUM(profit_loss), AVG(profit_loss) FROM trade_history WHERE profit_loss IS NOT NULL AND profit_loss != 0')
        r = cur.fetchone()
        if wins+losses > 0:
            print(f'Win/Loss: {wins}W / {losses}L = {wins/(wins+losses)*100:.1f}%')
        if r[0]: print(f'Total P/L: ${r[0]:.2f}, Avg: ${r[1]:.4f}')
except Exception as e:
    print(f'Error: {e}')

print("\n=== SIGNAL PREDICTIONS ===")
try:
    cur.execute('SELECT COUNT(*) FROM signal_predictions')
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_recorded=1")
    recorded = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM signal_predictions WHERE outcome_recorded=1 AND actual_pnl > 0")
    correct = cur.fetchone()[0]
    print(f'Total predictions: {total}, Outcomes recorded: {recorded}')
    if recorded > 0:
        print(f'Profitable: {correct}/{recorded} = {correct/recorded*100:.1f}%')
except Exception as e:
    print(f'Error: {e}')

conn.close()

