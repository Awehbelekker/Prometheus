"""Quick audit script for PROMETHEUS Trading Platform"""
import sqlite3
import os
from datetime import datetime

print("="*70)
print("📊 PROMETHEUS TRADING PLATFORM - COMPREHENSIVE AUDIT")
print("="*70)
print(f"Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Connect to database
db = sqlite3.connect('prometheus_learning.db')
c = db.cursor()

# 1. Database Tables
print("📁 DATABASE TABLES:")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in c.fetchall()]
for t in sorted(tables):
    try:
        c.execute(f'SELECT COUNT(*) FROM [{t}]')
        count = c.fetchone()[0]
        print(f"  {t}: {count:,} records")
    except Exception as e:
        print(f"  {t}: ERROR - {e}")
print()

# 2. Trading Performance
print("📈 TRADING PERFORMANCE (All Time):")
c.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
        SUM(profit_loss) as total_pnl,
        AVG(profit_loss) as avg_pnl,
        MAX(profit_loss) as best,
        MIN(profit_loss) as worst
    FROM trade_history
""")
row = c.fetchone()
if row and row[0] > 0:
    total, wins, losses, total_pnl, avg_pnl, best, worst = row
    wins = wins or 0
    losses = losses or 0
    total_pnl = total_pnl or 0
    avg_pnl = avg_pnl or 0
    best = best or 0
    worst = worst or 0
    win_rate = (wins / total * 100) if total > 0 else 0
    print(f"  Total Trades: {total:,}")
    print(f"  Wins: {wins:,} | Losses: {losses:,}")
    print(f"  Win Rate: {win_rate:.2f}%")
    print(f"  Total P/L: ${total_pnl:.2f}")
    print(f"  Avg P/L per Trade: ${avg_pnl:.4f}")
    print(f"  Best Trade: ${best:.2f}")
    print(f"  Worst Trade: ${worst:.2f}")
else:
    print("  No trades found")
print()

# 3. AI Attribution Summary
print("🤖 AI ATTRIBUTION SUMMARY:")
c.execute('SELECT COUNT(DISTINCT ai_system) FROM ai_attribution')
systems = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM ai_attribution')
total_attr = c.fetchone()[0]
print(f"  AI Systems Tracked: {systems}")
print(f"  Total Attributions: {total_attr:,}")

# Top AI systems
print("\n  Top 10 AI Systems by Signal Count:")
c.execute("""
    SELECT ai_system, COUNT(*) as cnt
    FROM ai_attribution
    GROUP BY ai_system
    ORDER BY cnt DESC
    LIMIT 10
""")
for row in c.fetchall():
    sys, cnt = row
    print(f"    {sys}: {cnt:,} signals")
print()

# 4. Signal Predictions
print("🎯 SIGNAL PREDICTIONS:")
c.execute('SELECT COUNT(*) FROM signal_predictions')
total_signals = c.fetchone()[0]
print(f"  Total Predictions: {total_signals:,}")
print()

# 5. Position Tracking
print("📍 POSITION TRACKING:")
c.execute('SELECT COUNT(*) FROM position_tracking')
positions = c.fetchone()[0]
print(f"  Current Tracked Positions: {positions}")
print()

# 6. Learning Outcomes
print("📚 LEARNING OUTCOMES:")
c.execute('SELECT COUNT(*) FROM learning_outcomes')
outcomes = c.fetchone()[0]
print(f"  Total Learning Records: {outcomes}")
print()

# 7. Shadow Trading
print("🔵 SHADOW TRADING:")
c.execute('SELECT COUNT(*) FROM shadow_sessions')
shadow_sessions = c.fetchone()[0]
print(f"  Shadow Sessions: {shadow_sessions}")

db.close()

# Database files
print()
print("💾 DATABASE FILES:")
for f in os.listdir('.'):
    if f.endswith('.db'):
        size = os.path.getsize(f) / (1024*1024)
        print(f"  {f}: {size:.2f} MB")

print()
print("="*70)
print("✅ AUDIT COMPLETE")
print("="*70)

