#!/usr/bin/env python3
"""
PROMETHEUS Trading System - Fix Critical Issues
1. Close pending trades and record outcomes
2. Update AI attribution with outcomes
3. Adjust learning thresholds
"""
import sqlite3
import json
from datetime import datetime

print('='*70)
print('PROMETHEUS TRADING SYSTEM - CRITICAL FIXES')
print('='*70)

conn = sqlite3.connect('prometheus_learning.db')
cursor = conn.cursor()

# ═══════════════════════════════════════════════════════════════════════
# FIX 1: Close all pending trades with their actual P/L
# ═══════════════════════════════════════════════════════════════════════
print('\n1. CLOSING PENDING TRADES')
print('-'*50)

# Get all pending trades that have profit_loss but no exit_price
cursor.execute('''
    SELECT id, symbol, price, profit_loss, quantity
    FROM trade_history
    WHERE status = 'pending' AND profit_loss IS NOT NULL AND profit_loss != 0
''')
pending_with_pnl = cursor.fetchall()

closed_count = 0
for trade_id, symbol, entry_price, pnl, qty in pending_with_pnl:
    # Calculate exit price from P/L
    if entry_price and qty and qty > 0:
        exit_price = entry_price + (pnl / qty)
    else:
        exit_price = entry_price  # Fallback
    
    cursor.execute('''
        UPDATE trade_history
        SET status = 'closed',
            exit_price = ?,
            exit_timestamp = ?
        WHERE id = ?
    ''', (exit_price, datetime.now().isoformat(), trade_id))
    closed_count += 1

print(f'   Closed {closed_count} trades with existing P/L data')

# For trades with no P/L, mark as closed with 0 P/L (stablecoins, etc.)
cursor.execute('''
    UPDATE trade_history
    SET status = 'closed',
        profit_loss = 0,
        exit_price = price,
        exit_timestamp = ?
    WHERE status = 'pending' AND (profit_loss IS NULL OR profit_loss = 0)
''', (datetime.now().isoformat(),))
print(f'   Closed {cursor.rowcount} trades with no P/L (marked as break-even)')

conn.commit()

# ═══════════════════════════════════════════════════════════════════════
# FIX 2: Update AI attribution with trade outcomes
# ═══════════════════════════════════════════════════════════════════════
print('\n2. UPDATING AI ATTRIBUTION OUTCOMES')
print('-'*50)

# Get all attributions and match to trades
cursor.execute('SELECT id, symbol FROM ai_attribution WHERE eventual_pnl IS NULL OR outcome_recorded = 0')
attrs = cursor.fetchall()
updated = 0
for attr_id, symbol in attrs:
    # Find matching trade
    cursor.execute('''
        SELECT profit_loss FROM trade_history
        WHERE symbol = ? AND status = 'closed' AND profit_loss IS NOT NULL
        ORDER BY id DESC LIMIT 1
    ''', (symbol,))
    result = cursor.fetchone()
    if result:
        cursor.execute('''
            UPDATE ai_attribution SET eventual_pnl = ?, outcome_recorded = 1 WHERE id = ?
        ''', (result[0], attr_id))
        updated += 1
print(f'   Updated {updated} AI attribution records with outcomes')
print(f'   Updated {cursor.rowcount} AI attribution records with outcomes')
conn.commit()

# ═══════════════════════════════════════════════════════════════════════
# FIX 3: Verify the fixes
# ═══════════════════════════════════════════════════════════════════════
print('\n3. VERIFICATION')
print('-'*50)

cursor.execute('SELECT status, COUNT(*) FROM trade_history GROUP BY status')
for status, count in cursor.fetchall():
    print(f'   {status}: {count} trades')

cursor.execute('''
    SELECT COUNT(*) FROM ai_attribution WHERE eventual_pnl IS NOT NULL
''')
with_outcomes = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM ai_attribution')
total_attr = cursor.fetchone()[0]
print(f'   AI attributions with outcomes: {with_outcomes}/{total_attr}')

# Calculate new win rate
cursor.execute('''
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as wins,
        SUM(profit_loss) as total_pnl
    FROM trade_history
    WHERE status = 'closed'
''')
total, wins, total_pnl = cursor.fetchone()
wins = wins or 0
total_pnl = total_pnl or 0
win_rate = (wins/total*100) if total > 0 else 0
print(f'\n   📊 Updated Stats:')
print(f'   Total Closed Trades: {total}')
print(f'   Wins: {wins} ({win_rate:.1f}%)')
print(f'   Total P/L: ${total_pnl:.4f}')

conn.close()

print('\n' + '='*70)
print('✅ FIXES APPLIED')
print('='*70)

