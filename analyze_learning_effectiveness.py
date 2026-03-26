"""
PROMETHEUS Learning System Effectiveness Analysis
Analyzes whether learning systems are actually improving trading performance
"""
import sqlite3
from datetime import datetime, timedelta
import json

db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

print("=" * 70)
print("PROMETHEUS LEARNING SYSTEM EFFECTIVENESS ANALYSIS")
print("=" * 70)

# 1. Overall Trade Statistics
print("\n📊 OVERALL TRADE STATISTICS")
print("-" * 50)
c.execute('SELECT COUNT(*) FROM trade_history')
total_trades = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0')
wins = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss <= 0')
losses = c.fetchone()[0]
c.execute('SELECT SUM(profit_loss) FROM trade_history')
total_pnl = c.fetchone()[0] or 0
c.execute('SELECT AVG(profit_loss) FROM trade_history WHERE profit_loss IS NOT NULL')
avg_pnl = c.fetchone()[0] or 0

print(f"Total Trades: {total_trades}")
print(f"Wins: {wins} ({wins/total_trades*100:.1f}%)" if total_trades > 0 else "N/A")
print(f"Losses: {losses}")
print(f"Total P/L: ${total_pnl:.2f}")
print(f"Avg P/L per trade: ${avg_pnl:.4f}")

# 2. Performance Over Time (Learning Trend)
print("\n📈 PERFORMANCE OVER TIME (Is Learning Improving Results?)")
print("-" * 50)
c.execute('''
    SELECT 
        date(timestamp) as trade_date,
        COUNT(*) as trades,
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
        SUM(profit_loss) as daily_pnl
    FROM trade_history
    WHERE profit_loss IS NOT NULL
    GROUP BY date(timestamp)
    ORDER BY trade_date
''')
daily_stats = c.fetchall()

if daily_stats:
    print(f"{'Date':<12} {'Trades':>8} {'Wins':>6} {'Win%':>8} {'P/L':>12}")
    print("-" * 50)
    for row in daily_stats[-10:]:  # Last 10 days
        date, trades, wins, pnl = row
        win_pct = (wins/trades*100) if trades > 0 else 0
        print(f"{date:<12} {trades:>8} {wins:>6} {win_pct:>7.1f}% ${pnl:>10.2f}")

# 3. Learning Outcomes Analysis
print("\n📚 LEARNING OUTCOMES TABLE ANALYSIS")
print("-" * 50)
c.execute('SELECT COUNT(*) FROM learning_outcomes')
learning_count = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM learning_outcomes WHERE was_correct = 1')
correct_predictions = c.fetchone()[0]
print(f"Total Learning Records: {learning_count}")
print(f"Correct Predictions: {correct_predictions} ({correct_predictions/learning_count*100:.1f}%)" if learning_count > 0 else "N/A")

# 4. AI Components Performance
print("\n🤖 AI COMPONENTS PERFORMANCE (Which AI systems are profitable?)")
print("-" * 50)
c.execute('''
    SELECT ai_components, 
           COUNT(*) as trades,
           SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
           SUM(profit_loss) as total_pnl
    FROM learning_outcomes
    WHERE ai_components IS NOT NULL AND ai_components != '[]'
    GROUP BY ai_components
    ORDER BY total_pnl DESC
    LIMIT 15
''')
ai_perf = c.fetchall()
if ai_perf:
    print(f"{'AI Components':<50} {'Trades':>7} {'Wins':>5} {'P/L':>10}")
    print("-" * 75)
    for row in ai_perf:
        components, trades, wins, pnl = row
        comp_short = components[:47] + "..." if len(components) > 50 else components
        print(f"{comp_short:<50} {trades:>7} {wins:>5} ${pnl:>9.4f}")

# 5. Check if learning is being applied
print("\n🔄 LEARNING APPLICATION CHECK")
print("-" * 50)
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print(f"Database tables: {tables}")

# Check for any adaptive parameter changes
c.execute("SELECT COUNT(*) FROM performance_metrics")
perf_count = c.fetchone()[0]
print(f"Performance metrics records: {perf_count}")

# 6. Critical Question: Is win rate improving over time?
print("\n❓ CRITICAL: IS WIN RATE IMPROVING OVER TIME?")
print("-" * 50)
if len(daily_stats) >= 5:
    first_half = daily_stats[:len(daily_stats)//2]
    second_half = daily_stats[len(daily_stats)//2:]
    
    first_wins = sum(r[2] for r in first_half)
    first_trades = sum(r[1] for r in first_half)
    second_wins = sum(r[2] for r in second_half)
    second_trades = sum(r[1] for r in second_half)
    
    first_wr = (first_wins/first_trades*100) if first_trades > 0 else 0
    second_wr = (second_wins/second_trades*100) if second_trades > 0 else 0
    
    print(f"First half win rate:  {first_wr:.1f}% ({first_wins}/{first_trades} trades)")
    print(f"Second half win rate: {second_wr:.1f}% ({second_wins}/{second_trades} trades)")
    print(f"Improvement: {second_wr - first_wr:+.1f}%")
    
    if second_wr > first_wr:
        print("✅ Learning appears to be IMPROVING performance")
    else:
        print("❌ Learning is NOT improving performance")
else:
    print("Not enough data to analyze trend")

# 7. Exit Reason Analysis
print("\n🚪 EXIT REASON ANALYSIS")
print("-" * 50)
c.execute('''
    SELECT exit_reason, COUNT(*) as count, AVG(profit_loss) as avg_pnl
    FROM trade_history
    WHERE exit_reason IS NOT NULL
    GROUP BY exit_reason
    ORDER BY count DESC
''')
exit_reasons = c.fetchall()
if exit_reasons:
    for reason, count, avg in exit_reasons:
        print(f"{reason or 'None':<30} {count:>5} trades, avg P/L: ${avg:.4f}")
else:
    print("No exit reasons recorded yet")

db.close()
print("\n" + "=" * 70)

