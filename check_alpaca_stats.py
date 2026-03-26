#!/usr/bin/env python3
"""Quick script to check Alpaca trading stats and positions"""
import asyncio
import os
import sys
sys.path.insert(0, '.')

# Load .env file
from dotenv import load_dotenv
load_dotenv()

from brokers.alpaca_broker import AlpacaBroker

async def main():
    broker = AlpacaBroker({
        'api_key': os.getenv('ALPACA_LIVE_KEY'),
        'secret_key': os.getenv('ALPACA_LIVE_SECRET'),
        'paper_trading': False
    })

    await broker.connect()

    # Get account info
    account = await broker.get_account()
    print("=" * 70)
    print("ALPACA ACCOUNT STATUS")
    print("=" * 70)
    # Account is an object, not a dict
    cash = float(getattr(account, 'cash', 0))
    portfolio_value = float(getattr(account, 'portfolio_value', 0))
    buying_power = float(getattr(account, 'buying_power', 0))
    equity = float(getattr(account, 'equity', 0))
    print(f"Cash:            ${cash:>15,.2f}")
    print(f"Portfolio Value: ${portfolio_value:>15,.2f}")
    print(f"Buying Power:    ${buying_power:>15,.2f}")
    print(f"Equity:          ${equity:>15,.2f}")
    
    # Get positions
    positions = await broker.get_positions()
    print("")
    print("=" * 70)
    print(f"CURRENT POSITIONS ({len(positions)} total)")
    print("=" * 70)
    print(f"{'Symbol':<12} {'Qty':>10} {'Entry':>10} {'Current':>10} {'P/L':>12} {'%':>8}")
    print("-" * 70)
    
    total_unrealized = 0
    total_cost = 0
    for p in positions:
        # Position is an object, not a dict
        symbol = getattr(p, 'symbol', 'N/A')
        qty = float(getattr(p, 'qty', 0))
        avg_price = float(getattr(p, 'avg_entry_price', 0))
        current = float(getattr(p, 'current_price', 0))
        unrealized = float(getattr(p, 'unrealized_pl', 0))
        pct = float(getattr(p, 'unrealized_plpc', 0)) * 100
        cost = qty * avg_price
        total_unrealized += unrealized
        total_cost += cost
        print(f"{symbol:<12} {qty:>10.4f} ${avg_price:>9.2f} ${current:>9.2f} ${unrealized:>+11.2f} {pct:>+7.1f}%")
    
    print("=" * 70)
    print(f"TOTAL COST BASIS:    ${total_cost:>15,.2f}")
    print(f"TOTAL UNREALIZED P/L: ${total_unrealized:>+14,.2f}")
    if total_cost > 0:
        total_pct = (total_unrealized / total_cost) * 100
        print(f"TOTAL RETURN:         {total_pct:>+14.2f}%")
    
    await broker.disconnect()

if __name__ == "__main__":
    asyncio.run(main())

