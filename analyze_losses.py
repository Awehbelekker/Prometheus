#!/usr/bin/env python3
"""Analyze why trades are losing"""
import sqlite3
import json

print('='*70)
print('TRADE LOSS ANALYSIS')
print('='*70)

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

# 1. Analyze trade patterns
print('\n1. TRADE BREAKDOWN BY SYMBOL')
print('-'*50)
cursor.execute('''
    SELECT symbol, COUNT(*) as trades, 
           SUM(profit_loss) as total_pnl,
           AVG(profit_loss) as avg_pnl
    FROM trade_history
    GROUP BY symbol
    ORDER BY total_pnl ASC
    LIMIT 15
''')
for row in cursor.fetchall():
    sym, trades, total_pnl, avg_pnl = row
    total_pnl = total_pnl or 0
    avg_pnl = avg_pnl or 0
    print(f'   {sym}: {trades} trades, Total: ${total_pnl:.4f}, Avg: ${avg_pnl:.6f}')

# 2. Trade confidence distribution
print('\n2. TRADE CONFIDENCE DISTRIBUTION')
print('-'*50)
cursor.execute('''
    SELECT 
        CASE 
            WHEN confidence < 0.5 THEN 'Low (<50%)'
            WHEN confidence < 0.7 THEN 'Medium (50-70%)'
            WHEN confidence < 0.85 THEN 'High (70-85%)'
            ELSE 'Very High (>85%)'
        END as conf_range,
        COUNT(*) as trades,
        SUM(profit_loss) as total_pnl,
        AVG(profit_loss) as avg_pnl
    FROM trade_history
    GROUP BY conf_range
''')
for row in cursor.fetchall():
    conf_range, trades, total_pnl, avg_pnl = row
    total_pnl = total_pnl or 0
    avg_pnl = avg_pnl or 0
    print(f'   {conf_range}: {trades} trades, Total: ${total_pnl:.4f}')

# 3. Check if trades have proper exit data
print('\n3. TRADE STATUS CHECK')
print('-'*50)
cursor.execute('SELECT status, COUNT(*) FROM trade_history GROUP BY status')
for row in cursor.fetchall():
    print(f'   {row[0]}: {row[1]} trades')

cursor.execute('SELECT COUNT(*) FROM trade_history WHERE exit_price IS NULL OR exit_price = 0')
no_exit = cursor.fetchone()[0]
print(f'   Trades without exit price: {no_exit}')

# 4. Check AI attribution outcomes
print('\n4. AI SYSTEM OUTCOMES')
print('-'*50)
cursor.execute('''
    SELECT ai_system, COUNT(*) as total,
           SUM(CASE WHEN eventual_pnl > 0 THEN 1 ELSE 0 END) as wins,
           SUM(eventual_pnl) as total_pnl
    FROM ai_attribution
    WHERE eventual_pnl IS NOT NULL
    GROUP BY ai_system
    ORDER BY total DESC
''')
rows = cursor.fetchall()
if rows:
    for ai_sys, total, wins, total_pnl in rows:
        wins = wins or 0
        total_pnl = total_pnl or 0
        win_rate = (wins/total*100) if total > 0 else 0
        print(f'   {ai_sys}: {total} signals, {win_rate:.0f}% win, ${total_pnl:.4f}')
else:
    print('   No outcome data recorded yet')

# 5. Sample recent trades to understand pattern
print('\n5. SAMPLE RECENT TRADES')
print('-'*50)
cursor.execute('''
    SELECT symbol, action, price, exit_price, profit_loss, confidence, reasoning
    FROM trade_history
    ORDER BY id DESC
    LIMIT 5
''')
for row in cursor.fetchall():
    sym, action, price, exit_price, pnl, conf, reason = row
    pnl = pnl or 0
    price = price or 0
    exit_price = exit_price or 0
    conf = conf or 0
    print(f'\n   {sym}: {action}')
    print(f'   Entry: ${price:.4f} -> Exit: ${exit_price:.4f} = ${pnl:.6f}')
    print(f'   Confidence: {conf:.2%}')
    if reason:
        print(f'   Reason: {reason[:80]}...')

conn.close()

# 6. Visual Pattern Usage Analysis
print('\n6. VISUAL PATTERN INFLUENCE')
print('-'*50)
try:
    from core.visual_pattern_provider import get_visual_pattern_provider
    provider = get_visual_pattern_provider()
    
    # Check if crypto symbols have visual data
    crypto_syms = ['SOL/USD', 'ETH/USD', 'BTC/USD', 'PEPE/USD', 'SHIB/USD']
    stock_syms = ['AAPL', 'TSLA', 'NVDA', 'AMD', 'GOOGL']
    
    print('   Crypto symbol coverage:')
    for sym in crypto_syms:
        has_data = provider.has_data_for_symbol(sym.replace('/USD', ''))
        print(f'   {sym}: {"YES" if has_data else "NO"}')
    
    print('\n   Stock symbol coverage:')
    for sym in stock_syms:
        has_data = provider.has_data_for_symbol(sym)
        consensus = provider.get_trend_consensus(sym)
        print(f'   {sym}: {consensus["trend"]} ({consensus["confidence"]:.0%})')
except Exception as e:
    print(f'   Error: {e}')

print('\n' + '='*70)
print('DIAGNOSIS SUMMARY')
print('='*70)

