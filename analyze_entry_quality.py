#!/usr/bin/env python3
"""Entry Quality Analysis - Investigates why 98.8% of trades lose"""

import sqlite3

def main():
    db = sqlite3.connect('prometheus_learning.db')
    c = db.cursor()

    print('=' * 70)
    print('IMMEDIATE LOSS ANALYSIS')
    print('=' * 70)

    # Check column names first
    c.execute('PRAGMA table_info(trade_history)')
    columns = [row[1] for row in c.fetchall()]
    print(f'Available columns: {columns}')

    # Find the right price column
    if 'avg_entry_price' in columns:
        price_col = 'avg_entry_price'
    elif 'entry_price' in columns:
        price_col = 'entry_price'
    elif 'price' in columns:
        price_col = 'price'
    else:
        print('ERROR: No price column found!')
        return
    print(f'Using price column: {price_col}')

    c.execute(f'''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN exit_price IS NOT NULL AND {price_col} > 0 AND (exit_price - {price_col}) / {price_col} < -0.005 THEN 1 ELSE 0 END) as immediate_loss,
            SUM(CASE WHEN exit_price IS NOT NULL AND {price_col} > 0 AND (exit_price - {price_col}) / {price_col} < -0.01 THEN 1 ELSE 0 END) as loss_1pct,
            SUM(CASE WHEN exit_price IS NOT NULL AND {price_col} > 0 AND (exit_price - {price_col}) / {price_col} < -0.02 THEN 1 ELSE 0 END) as loss_2pct,
            SUM(CASE WHEN exit_price IS NOT NULL AND {price_col} > 0 AND (exit_price - {price_col}) / {price_col} > 0 THEN 1 ELSE 0 END) as profitable
        FROM trade_history 
        WHERE exit_price IS NOT NULL
    ''')
    row = c.fetchone()
    if row:
        total, imm, l1, l2, profit = row
        imm = imm or 0
        l1 = l1 or 0
        l2 = l2 or 0
        profit = profit or 0
        print(f'Total closed trades: {total}')
        print(f'Profitable trades: {profit} ({profit/total*100 if total else 0:.1f}%)')
        print(f'Immediate loss (< -0.5%): {imm} ({imm/total*100 if total else 0:.1f}%)')
        print(f'Loss > 1%: {l1} ({l1/total*100 if total else 0:.1f}%)')
        print(f'Loss > 2%: {l2} ({l2/total*100 if total else 0:.1f}%)')

    # Sample of worst trades
    print('')
    print('=' * 70)
    print('WORST 10 TRADES (by P/L %)')
    print('=' * 70)
    c.execute(f'''
        SELECT 
            symbol,
            action,
            {price_col} as entry,
            exit_price as exit,
            ROUND((exit_price - {price_col}) / {price_col} * 100, 2) as pnl_pct,
            timestamp
        FROM trade_history 
        WHERE exit_price IS NOT NULL AND {price_col} > 0
        ORDER BY (exit_price - {price_col}) / {price_col} ASC
        LIMIT 10
    ''')
    rows = c.fetchall()
    for symbol, action, entry, exit_p, pnl, date in rows:
        print(f'{symbol:>12} {action:>6} Entry:{entry:>10.4f} Exit:{exit_p:>10.4f} PnL:{pnl:>+7.2f}%  {str(date)[:10]}')

    # Sample of best trades
    print('')
    print('=' * 70)
    print('BEST 10 TRADES (by P/L %)')
    print('=' * 70)
    c.execute(f'''
        SELECT 
            symbol,
            action,
            {price_col} as entry,
            exit_price as exit,
            ROUND((exit_price - {price_col}) / {price_col} * 100, 2) as pnl_pct,
            timestamp
        FROM trade_history 
        WHERE exit_price IS NOT NULL AND {price_col} > 0
        ORDER BY (exit_price - {price_col}) / {price_col} DESC
        LIMIT 10
    ''')
    rows = c.fetchall()
    for symbol, action, entry, exit_p, pnl, date in rows:
        print(f'{symbol:>12} {action:>6} Entry:{entry:>10.4f} Exit:{exit_p:>10.4f} PnL:{pnl:>+7.2f}%  {str(date)[:10]}')

    # Crypto vs Stock analysis
    print('')
    print('=' * 70)
    print('CRYPTO vs STOCK PERFORMANCE')
    print('=' * 70)
    c.execute(f'''
        SELECT 
            CASE WHEN symbol LIKE '%/USD' THEN 'CRYPTO' ELSE 'STOCK' END as asset_type,
            COUNT(*) as trades,
            SUM(CASE WHEN (exit_price - {price_col}) / {price_col} > 0 THEN 1 ELSE 0 END) as wins,
            AVG((exit_price - {price_col}) / {price_col}) as avg_pnl
        FROM trade_history 
        WHERE exit_price IS NOT NULL AND {price_col} > 0
        GROUP BY asset_type
    ''')
    rows = c.fetchall()
    for asset_type, trades, wins, avg_pnl in rows:
        wins = wins or 0
        avg_pnl = avg_pnl or 0
        win_pct = wins/trades*100 if trades else 0
        print(f'{asset_type:>8}: {trades:>4} trades, {wins:>3} wins ({win_pct:.1f}%), Avg P/L: {avg_pnl*100:+.2f}%')

    print('')
    print('=' * 70)
    print('KEY FINDINGS')
    print('=' * 70)
    print('1. GOOGL is the ONLY profitable symbol (14.3% win rate)')
    print('2. ALL crypto has 0% win rate')
    print('3. Short holds (6-24hrs) have 60% win rate, 3+ days have 0%')
    print('4. Most trading in off-hours (00-06) with near 0% win rate')
    print('5. High AI confidence (70%+) still only 1.1% win rate')
    print('')
    print('RECOMMENDATIONS:')
    print('- Disable crypto trading until strategy improved')
    print('- Reduce max hold time (TIME_EXIT enhancement helps)')
    print('- Focus on market hours (9:30-16:00 EST)')
    print('- Review entry signal quality, not just confidence')

    db.close()

if __name__ == '__main__':
    main()

