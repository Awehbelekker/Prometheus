#!/usr/bin/env python3
"""PROMETHEUS Autonomous Trading & Learning Status"""
import sys
sys.path.insert(0, '.')
import sqlite3
import json

print('='*70)
print('PROMETHEUS AUTONOMOUS TRADING & LEARNING STATUS')
print('='*70)

conn = sqlite3.connect('prometheus_trading.db')
cursor = conn.cursor()

# 1. Recent Trade Performance
print('\n1. RECENT TRADE PERFORMANCE')
print('-'*40)
try:
    cursor.execute('''
        SELECT COUNT(*) as total,
               SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
               SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losses,
               SUM(profit_loss) as total_pnl
        FROM trade_history WHERE exit_timestamp IS NOT NULL
    ''')
    row = cursor.fetchone()
    if row and row[0] and row[0] > 0:
        total, wins, losses, total_pnl = row
        wins = wins or 0
        losses = losses or 0
        total_pnl = total_pnl or 0
        win_rate = (wins / total * 100) if total > 0 else 0
        print(f'   Total Closed Trades: {total}')
        print(f'   Wins: {wins} | Losses: {losses}')
        print(f'   Win Rate: {win_rate:.1f}%')
        print(f'   Total P/L: ${total_pnl:.2f}')
    else:
        print('   No closed trades with P/L data yet')
except Exception as e:
    print(f'   Error: {e}')

# 2. Learning Engine Status
print('\n2. LEARNING ENGINE STATUS')
print('-'*40)
try:
    cursor.execute('SELECT COUNT(*) FROM learned_patterns')
    count = cursor.fetchone()[0]
    print(f'   Learned Patterns: {count}')
except:
    print('   learned_patterns table not found')

try:
    cursor.execute('SELECT COUNT(*) FROM learning_feedback')
    count = cursor.fetchone()[0]
    print(f'   Learning Feedbacks: {count}')
except:
    pass

# 3. AI Attribution
print('\n3. AI SYSTEM CONTRIBUTIONS')
print('-'*40)
try:
    cursor.execute('''
        SELECT ai_system, COUNT(*) as signals,
               AVG(CASE WHEN outcome = 1 THEN 1.0 ELSE 0.0 END) as success_rate
        FROM ai_signal_attribution GROUP BY ai_system ORDER BY signals DESC LIMIT 10
    ''')
    rows = cursor.fetchall()
    if rows:
        for ai_system, signals, success_rate in rows:
            success_pct = (success_rate or 0) * 100
            print(f'   {ai_system}: {signals} signals ({success_pct:.1f}% success)')
    else:
        print('   No AI attribution data yet')
except Exception as e:
    print(f'   Table issue: {e}')

# 4. Training Sessions
print('\n4. TRAINING SESSIONS')
print('-'*40)
try:
    cursor.execute('SELECT COUNT(*), MAX(timestamp) FROM training_sessions')
    row = cursor.fetchone()
    if row and row[0] > 0:
        print(f'   Total Sessions: {row[0]}')
        print(f'   Last Session: {row[1]}')
    else:
        print('   No training sessions recorded')
except:
    print('   training_sessions table not found')

conn.close()

# 5. Visual Pattern Integration
print('\n5. VISUAL PATTERN INTEGRATION')
print('-'*40)
try:
    with open('visual_ai_patterns.json', 'r') as f:
        data = json.load(f)

    total_charts = len(data.get('patterns', {}))
    successful = sum(1 for p in data.get('patterns', {}).values() if p.get('patterns_detected'))
    total_patterns = sum(len(p.get('patterns_detected', [])) for p in data.get('patterns', {}).values())

    print(f'   Charts Analyzed: {total_charts}')
    print(f'   With Detections: {successful}')
    print(f'   Total Patterns: {total_patterns}')

    from core.visual_pattern_provider import get_visual_pattern_provider
    provider = get_visual_pattern_provider()

    test_symbols = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'GOOGL']
    print('\n   Symbol Trend Analysis:')
    for sym in test_symbols:
        consensus = provider.get_trend_consensus(sym)
        if consensus['charts_analyzed'] > 0:
            print(f'   {sym}: {consensus["trend"]} ({consensus["confidence"]:.0%} conf)')
except Exception as e:
    print(f'   Error: {e}')

# 6. System Readiness
print('\n6. SYSTEM READINESS')
print('-'*40)
try:
    from core.ai_learning_engine import ai_learning_engine
    print('   AI Learning Engine: READY')
except Exception as e:
    print(f'   AI Learning Engine: {e}')

try:
    vpp = get_visual_pattern_provider()
    print(f'   Visual Patterns: {len(vpp.patterns)} loaded')
except Exception as e:
    print(f'   Visual Pattern Provider: {e}')

print('\n' + '='*70)
