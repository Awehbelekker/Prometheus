
import asyncio
import os
import sys
os.environ['LIVE_TRADING_ENABLED'] = 'true'
os.environ['ALPACA_PAPER_TRADING'] = 'true'
os.environ['PRIMARY_BROKER'] = 'IB'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prometheus_active_trading_session import PrometheusActiveTradingSession

async def main():
    session = PrometheusActiveTradingSession(session_id=f"ib_dual_broker_{os.getpid()}")
    await session.initialize_ib_connection()
    duration_minutes = 480
    await session.run_session(duration_minutes=duration_minutes)

if __name__ == "__main__":
    asyncio.run(main())
