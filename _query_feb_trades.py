"""Query trading data from February 2026 onward"""
import sqlite3

c = sqlite3.connect('prometheus_learning.db')

# Schema
cols = [r[1] for r in c.execute('PRAGMA table_info(trade_history)').fetchall()]
print('trade_history columns:', cols)
print()

# Counts
total = c.execute('SELECT COUNT(*) FROM trade_history').fetchone()[0]
print(f'Total trades: {total}')

try:
    closed = c.execute("SELECT COUNT(*) FROM trade_history WHERE exit_price IS NOT NULL").fetchone()[0]
    print(f'Closed (has exit_price): {closed}')
except Exception as e:
    print(f'Error counting closed: {e}')

# Date ranges
earliest = c.execute('SELECT MIN(timestamp) FROM trade_history').fetchone()[0]
latest = c.execute('SELECT MAX(timestamp) FROM trade_history').fetchone()[0]
print(f'Date range: {earliest} to {latest}')
print()

# Feb 2026 trades  
print('=== TRADES FROM FEB 2026 ONWARD ===')
rows = c.execute("""
    SELECT timestamp, symbol, action, price, exit_price, profit_loss, status 
    FROM trade_history 
    WHERE timestamp >= '2026-02-01' 
    ORDER BY timestamp DESC 
    LIMIT 40
""").fetchall()
for r in rows:
    print(f'  {r[0]} | {r[1]:10s} | {r[2] or "":5s} | entry={r[3]} | exit={r[4]} | PnL={r[5]} | {r[6]}')

if not rows:
    print('  No trades found >= Feb 2026. Checking latest trades...')
    latest_rows = c.execute("""
        SELECT timestamp, symbol, action, price, exit_price, profit_loss 
        FROM trade_history 
        ORDER BY timestamp DESC LIMIT 20
    """).fetchall()
    for r in latest_rows:
        print(f'  {r[0]} | {r[1]:10s} | {r[2] or "":5s} | entry={r[3]} | exit={r[4]} | PnL={r[5]}')

# 24h count
print()
print('=== LAST 24 HOURS ===')
recent = c.execute("""
    SELECT COUNT(*) FROM trade_history 
    WHERE timestamp >= datetime('now', '-1 day')
""").fetchone()[0]
print(f'Trades in last 24h: {recent}')

# Also check live_trade_outcomes
print()
print('=== live_trade_outcomes ===')
try:
    cols2 = [r[1] for r in c.execute('PRAGMA table_info(live_trade_outcomes)').fetchall()]
    print(f'Columns: {cols2}')
    total2 = c.execute('SELECT COUNT(*) FROM live_trade_outcomes').fetchone()[0]
    print(f'Total: {total2}')
    rows2 = c.execute("""
        SELECT * FROM live_trade_outcomes 
        ORDER BY rowid DESC LIMIT 10
    """).fetchall()
    for r in rows2:
        print(f'  {r}')
except Exception as e:
    print(f'Error: {e}')

# Check persistent_trading.db too
print()
print('=== persistent_trading.db trades ===')
try:
    c2 = sqlite3.connect('persistent_trading.db')
    for tbl in ['trades', 'trading_history', 'trading_orders']:
        total3 = c2.execute(f'SELECT COUNT(*) FROM {tbl}').fetchone()[0]
        print(f'  {tbl}: {total3} rows')
        if total3 > 0:
            recent3 = c2.execute(f'SELECT * FROM {tbl} ORDER BY rowid DESC LIMIT 3').fetchall()
            for r in recent3:
                print(f'    {str(r)[:200]}')
    c2.close()
except Exception as e:
    print(f'Error: {e}')

# Check prometheus_trades.db
print()
print('=== prometheus_trades.db ===')
try:
    c3 = sqlite3.connect('prometheus_trades.db')
    total4 = c3.execute('SELECT COUNT(*) FROM trades').fetchone()[0]
    print(f'Total: {total4}')
    if total4 > 0:
        cols3 = [r[1] for r in c3.execute('PRAGMA table_info(trades)').fetchall()]
        print(f'Columns: {cols3}')
        rows3 = c3.execute('SELECT * FROM trades ORDER BY rowid DESC LIMIT 5').fetchall()
        for r in rows3:
            print(f'  {str(r)[:200]}')
    c3.close()
except Exception as e:
    print(f'Error: {e}')

c.close()
