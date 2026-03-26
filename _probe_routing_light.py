#!/usr/bin/env python3
"""Lightweight routing probe using direct broker connections (no full system init)."""
import asyncio
import os
from launch_ultimate_prometheus_LIVE_TRADING import PrometheusLiveTradingLauncher
from brokers.alpaca_broker import AlpacaBroker
from brokers.interactive_brokers_broker import InteractiveBrokersBroker


async def main():
    launcher = PrometheusLiveTradingLauncher(standalone_mode=False)

    # Build brokers directly
    alpaca = AlpacaBroker(
        config={
            'api_key': os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY'),
            'secret_key': os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET'),
            'paper_trading': False,
        }
    )

    ib = InteractiveBrokersBroker(
        config={
            'host': os.getenv('IB_HOST', '127.0.0.1'),
            'port': int(os.getenv('IB_PORT', '4002')),
            'client_id': 98,
            'paper_trading': False,
            'account_id': os.getenv('IB_ACCOUNT', 'U21922116'),
        }
    )

    # Connect both
    await alpaca.connect()
    ib_ok = await ib.connect()

    print(f"AUTONOMOUS_ROUTING_ENABLED={launcher.autonomous_routing_enabled}")
    print(f"ALPACA_24HR_HARD_OVERRIDE={launcher.alpaca_24hr_hard_override}")
    print(f"IB_MIN_ALLOCATION_PCT={launcher.ib_min_allocation_pct}")
    print(f"IB_CONNECTED={bool(ib_ok and ib.connected)}")

    symbols = ["DIA", "AAPL", "QQQ", "MSFT", "XOM", "ETH/USD"]
    for s in symbols:
        if launcher.autonomous_routing_enabled:
            _, broker_name, meta = await launcher._select_broker_for_symbol(s, alpaca, ib)
        else:
            _, broker_name, meta = await launcher._select_legacy_broker_for_symbol(s, alpaca, ib)
        print(f"{s:8} -> {broker_name:7} | reason={meta.get('reason')} | ib_cash={meta.get('ib_cash')} alpaca_cash={meta.get('alpaca_cash')}")

    # Clean disconnect
    try:
        await ib.disconnect()
    except Exception:
        pass
    try:
        await alpaca.disconnect()
    except Exception:
        pass


if __name__ == '__main__':
    asyncio.run(main())
