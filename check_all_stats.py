#!/usr/bin/env python3
"""Check all trading stats: Crypto, Realized P/L, IB positions"""
import asyncio
import os
import sys
import sqlite3
import random
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from brokers.alpaca_broker import AlpacaBroker
from brokers.interactive_brokers_broker import InteractiveBrokersBroker

async def check_crypto():
    """Check Alpaca crypto positions"""
    print("="*70)
    print("1. ALPACA CRYPTO POSITIONS")
    print("="*70)
    
    broker = AlpacaBroker({
        'api_key': os.getenv('ALPACA_LIVE_KEY'),
        'secret_key': os.getenv('ALPACA_LIVE_SECRET'),
        'paper_trading': False
    })
    await broker.connect()
    
    # Get all positions - crypto have / in symbol or end with USD
    positions = broker.api.list_positions()
    crypto_positions = [p for p in positions if '/' in p.symbol or p.symbol.endswith('USD')]
    stock_positions = [p for p in positions if '/' not in p.symbol and not p.symbol.endswith('USD')]
    
    if crypto_positions:
        print(f"{'Symbol':<12} {'Qty':>12} {'Entry':>10} {'Current':>10} {'P/L':>10} {'%':>8}")
        print("-"*70)
        crypto_total_cost = 0
        crypto_total_pl = 0
        for p in crypto_positions:
            qty = float(p.qty)
            entry = float(p.avg_entry_price)
            current = float(p.current_price)
            pl = float(p.unrealized_pl)
            cost = qty * entry
            pct = (pl/cost)*100 if cost > 0 else 0
            crypto_total_cost += cost
            crypto_total_pl += pl
            print(f"{p.symbol:<12} {qty:>12.6f} ${entry:>9.4f} ${current:>9.4f} ${pl:>+9.2f} {pct:>+7.1f}%")
        print("-"*70)
        print(f"CRYPTO TOTAL COST: ${crypto_total_cost:,.2f}")
        print(f"CRYPTO UNREALIZED P/L: ${crypto_total_pl:+,.2f}")
    else:
        print("No crypto positions found in Alpaca account")
        print("(Crypto trades may be in a separate crypto account)")
    
    await broker.disconnect()

def check_realized_pl():
    """Check realized P/L from database"""
    print("\n" + "="*70)
    print("2. REALIZED P/L - TRADE HISTORY")
    print("="*70)
    
    db = sqlite3.connect('prometheus_learning.db')
    c = db.cursor()
    
    # First check the schema
    c.execute("PRAGMA table_info(trade_history)")
    columns = [col[1] for col in c.fetchall()]
    print(f"Available columns: {', '.join(columns)}")
    
    # Get trades with profit_loss
    if 'profit_loss' in columns:
        c.execute('''SELECT symbol, action, profit_loss, timestamp 
                     FROM trade_history 
                     WHERE profit_loss IS NOT NULL AND profit_loss != 0
                     ORDER BY timestamp DESC LIMIT 20''')
        trades = c.fetchall()
        
        if trades:
            print(f"\n{'Time':<10} {'Symbol':<12} {'Action':<6} {'P/L':>12}")
            print("-"*45)
            for t in trades:
                symbol, action, pl, ts = t
                time_str = ts[11:19] if ts else 'N/A'
                print(f"{time_str:<10} {symbol:<12} {action:<6} ${pl:>+11.2f}")
        
        # Get totals
        c.execute('SELECT COUNT(*), SUM(profit_loss) FROM trade_history WHERE profit_loss IS NOT NULL AND profit_loss != 0')
        totals = c.fetchone()
        c.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss > 0')
        wins = c.fetchone()[0]
        c.execute('SELECT COUNT(*) FROM trade_history WHERE profit_loss < 0')
        losses = c.fetchone()[0]
        
        print("-"*45)
        print(f"TOTAL CLOSED TRADES: {totals[0] or 0}")
        print(f"TOTAL REALIZED P/L: ${totals[1] or 0:+,.2f}")
        if wins + losses > 0:
            print(f"WINS: {wins} | LOSSES: {losses} | WIN RATE: {wins/(wins+losses)*100:.1f}%")
    else:
        print("No profit_loss column found - trades may not be closed yet")
    
    # Show recent trades
    print("\n--- Recent Trades (last 10) ---")
    c.execute('SELECT timestamp, symbol, action, confidence FROM trade_history ORDER BY timestamp DESC LIMIT 10')
    for row in c.fetchall():
        ts, sym, act, conf = row
        time_str = ts[11:19] if ts else 'N/A'
        conf_str = f"{conf*100:.0f}%" if conf else "N/A"
        print(f"{time_str} | {sym:<12} | {act:<4} | {conf_str}")
    
    db.close()

async def check_ib():
    """Check IB positions"""
    print("\n" + "="*70)
    print("3. INTERACTIVE BROKERS POSITIONS")
    print("="*70)
    
    broker = InteractiveBrokersBroker({
        'host': '127.0.0.1',
        'port': 4002,
        'client_id': random.randint(50, 99),
        'paper_trading': False
    })
    
    connected = await broker.connect()
    if not connected:
        print("IB NOT CONNECTED - Gateway may not be running or client ID conflict")
        return
    
    print("IB Connected!")
    account = await broker.get_account()
    if account:
        print(f"Net Liquidation: ${float(account.get('NetLiquidation', 0)):,.2f}")
        print(f"Total Cash: ${float(account.get('TotalCashValue', 0)):,.2f}")
    
    positions = await broker.get_positions()
    if positions:
        print(f"\n{'Symbol':<12} {'Qty':>10} {'Entry':>10} {'Current':>10} {'P/L':>12}")
        print("-"*60)
        total_pl = 0
        for p in positions:
            symbol = p.get('symbol', 'N/A')
            qty = float(p.get('qty', 0))
            entry = float(p.get('avg_entry_price', 0))
            current = float(p.get('current_price', 0))
            pl = float(p.get('unrealized_pl', 0))
            total_pl += pl
            print(f"{symbol:<12} {qty:>10.2f} ${entry:>9.2f} ${current:>9.2f} ${pl:>+11.2f}")
        print("-"*60)
        print(f"IB TOTAL UNREALIZED P/L: ${total_pl:+,.2f}")
    else:
        print("No IB positions found")
    
    await broker.disconnect()

async def main():
    await check_crypto()
    check_realized_pl()
    await check_ib()
    print("\n" + "="*70)
    print("STATS CHECK COMPLETE")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())

