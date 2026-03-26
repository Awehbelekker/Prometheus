#!/usr/bin/env python3
"""
Safe smoke test for revolutionary session order routing.
- Imports RevolutionaryTradingSession
- Attempts to route a small paper order via Alpaca service
- Skips if market is closed
- Always defaults to paper (ALLOW_LIVE_TRADING forced false)
"""
import os
import sys
import asyncio

async def main():
    os.environ['ALLOW_LIVE_TRADING'] = 'false'
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from revolutionary_trading_session import RevolutionaryTradingSession
    session = RevolutionaryTradingSession(starting_capital=10000.0, session_hours=1)
    # Attempt a tiny order routing; should skip off-hours
    await session.execute_real_trade('STOCK', 'AAPL', 'BUY', 100.0, 0.001, 226.50)
    print('Trades logged:', len(session.portfolio['trades']))

if __name__ == '__main__':
    asyncio.run(main())

