#!/usr/bin/env python3
"""Probe runtime broker routing decisions without placing orders."""
import asyncio

from launch_ultimate_prometheus_LIVE_TRADING import main as init_trading_system


async def run_probe():
    launcher = await init_trading_system(standalone_mode=False)
    if not launcher:
        print("ERROR: launcher init failed")
        return

    alpaca = launcher.systems.get('alpaca_broker')
    ib = launcher.systems.get('ib_broker')

    print("AUTONOMOUS_ROUTING_ENABLED:", launcher.autonomous_routing_enabled)
    print("ALPACA_24HR_HARD_OVERRIDE:", launcher.alpaca_24hr_hard_override)
    print("IB_MIN_ALLOCATION_PCT:", launcher.ib_min_allocation_pct)
    print("IB_CONNECTED:", bool(ib and getattr(ib, 'connected', False)))

    symbols = ["DIA", "AAPL", "QQQ", "MSFT", "XOM", "ETH/USD"]

    for symbol in symbols:
        if launcher.autonomous_routing_enabled:
            _, broker_name, meta = await launcher._select_broker_for_symbol(symbol, alpaca, ib)
        else:
            _, broker_name, meta = await launcher._select_legacy_broker_for_symbol(symbol, alpaca, ib)

        print(
            f"{symbol:8} -> {broker_name:7} | reason={meta.get('reason')} | "
            f"ib_cash={meta.get('ib_cash')} alpaca_cash={meta.get('alpaca_cash')} "
            f"ib_share={meta.get('ib_allocation_share', 'n/a')}"
        )


if __name__ == "__main__":
    asyncio.run(run_probe())
