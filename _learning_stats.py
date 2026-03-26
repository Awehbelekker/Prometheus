#!/usr/bin/env python3
"""Get PROMETHEUS learning statistics and insights"""
import sqlite3
from datetime import datetime, timedelta

print("=" * 70)
print("  PROMETHEUS LEARNING & AI INSIGHTS")
print("=" * 70)

# Connect to learning database
conn = sqlite3.connect('prometheus_learning.db', timeout=30)
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"\n📊 Learning Database Tables: {tables}")

# Trade History Stats
print("\n" + "=" * 70)
print("  TRADE HISTORY ANALYSIS")
print("=" * 70)

cursor.execute("SELECT COUNT(*) FROM trade_history")
total_trades = cursor.fetchone()[0]
print(f"\n📈 Total Trades Recorded: {total_trades}")

if total_trades > 0:
    # Get trade breakdown
    cursor.execute("SELECT action, COUNT(*), SUM(total_value) FROM trade_history GROUP BY action")
    for row in cursor.fetchall():
        action, count, value = row
        value = value or 0
        print(f"   {action}: {count} trades (${value:.2f} volume)")
    
    # Get trades by symbol
    print("\n📊 Trades by Symbol:")
    cursor.execute("""
        SELECT symbol, COUNT(*) as cnt, SUM(total_value) as vol 
        FROM trade_history 
        GROUP BY symbol 
        ORDER BY cnt DESC 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        symbol, count, vol = row
        vol = vol or 0
        print(f"   {symbol}: {count} trades (${vol:.2f})")

    # Get recent trades
    print("\n📋 Recent Trades (Last 10):")
    cursor.execute("""
        SELECT timestamp, symbol, action, quantity, price, total_value, broker
        FROM trade_history 
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        ts, sym, action, qty, price, val, broker = row
        ts_short = ts[11:19] if ts else "N/A"
        print(f"   {ts_short} | {sym:6} | {action:4} | {qty:.4f} @ ${price:.2f} | {broker}")

# Learning Outcomes
print("\n" + "=" * 70)
print("  LEARNING OUTCOMES (What PROMETHEUS Learned)")
print("=" * 70)

if 'learning_outcomes' in tables:
    cursor.execute("SELECT COUNT(*) FROM learning_outcomes")
    outcomes = cursor.fetchone()[0]
    print(f"\n🧠 Total Learning Outcomes: {outcomes}")
    
    if outcomes > 0:
        # Accuracy stats
        cursor.execute("SELECT COUNT(*) FROM learning_outcomes WHERE was_correct = 1")
        correct = cursor.fetchone()[0]
        accuracy = (correct / outcomes * 100) if outcomes > 0 else 0
        print(f"   Prediction Accuracy: {correct}/{outcomes} ({accuracy:.1f}%)")
        
        # Profit stats
        cursor.execute("SELECT SUM(profit_loss), AVG(profit_loss), AVG(profit_pct) FROM learning_outcomes")
        total_pl, avg_pl, avg_pct = cursor.fetchone()
        total_pl = total_pl or 0
        avg_pl = avg_pl or 0
        avg_pct = avg_pct or 0
        print(f"   Total P/L from Closed Trades: ${total_pl:.2f}")
        print(f"   Average P/L per Trade: ${avg_pl:.2f} ({avg_pct*100:.2f}%)")
        
        # Best and worst
        cursor.execute("SELECT symbol, profit_loss, profit_pct FROM learning_outcomes ORDER BY profit_loss DESC LIMIT 1")
        best = cursor.fetchone()
        if best:
            print(f"   Best Trade: {best[0]} +${best[1]:.2f} ({best[2]*100:.2f}%)")
        
        cursor.execute("SELECT symbol, profit_loss, profit_pct FROM learning_outcomes ORDER BY profit_loss ASC LIMIT 1")
        worst = cursor.fetchone()
        if worst:
            print(f"   Worst Trade: {worst[0]} ${worst[1]:.2f} ({worst[2]*100:.2f}%)")

# Learning Insights
print("\n" + "=" * 70)
print("  AI LEARNING INSIGHTS")
print("=" * 70)

if 'learning_insights' in tables:
    cursor.execute("SELECT COUNT(*) FROM learning_insights")
    insights = cursor.fetchone()[0]
    print(f"\n💡 Total Insights Generated: {insights}")
    
    if insights > 0:
        cursor.execute("""
            SELECT timestamp, insight_type, symbol, description 
            FROM learning_insights 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        print("\n📝 Recent Insights:")
        for row in cursor.fetchall():
            ts, itype, sym, desc = row
            ts_short = ts[11:19] if ts else "N/A"
            sym = sym or "GENERAL"
            print(f"   [{ts_short}] {itype}: {sym} - {desc[:60]}...")

# Signal Predictions
if 'signal_predictions' in tables:
    print("\n" + "=" * 70)
    print("  AI SIGNAL PREDICTIONS")
    print("=" * 70)
    
    cursor.execute("SELECT COUNT(*) FROM signal_predictions")
    predictions = cursor.fetchone()[0]
    print(f"\n🎯 Total Predictions Made: {predictions}")
    
    if predictions > 0:
        cursor.execute("SELECT action, COUNT(*) FROM signal_predictions GROUP BY action")
        print("   Signal Breakdown:")
        for row in cursor.fetchall():
            print(f"      {row[0]}: {row[1]}")

conn.close()
print("\n" + "=" * 70)

