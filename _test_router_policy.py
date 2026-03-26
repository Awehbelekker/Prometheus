#!/usr/bin/env python3
"""Deterministic test for broker router policy using current env settings."""
import asyncio
import os

from launch_ultimate_prometheus_LIVE_TRADING import PrometheusLiveTradingLauncher


class DummyBroker:
    pass


async def main():
    launcher = PrometheusLiveTradingLauncher(standalone_mode=False)

    print("AUTONOMOUS_ROUTING_ENABLED:", launcher.autonomous_routing_enabled)
    print("ALPACA_24HR_HARD_OVERRIDE:", launcher.alpaca_24hr_hard_override)
    print("IB_MIN_ALLOCATION_PCT:", launcher.ib_min_allocation_pct)

    # Force deterministic routing stats so IB floor can be tested.
    launcher.routing_execution_counts = {"ib": 0, "alpaca": 10}

    async def fake_balances(alpaca_broker, ib_broker):
        return {"ib_cash": 246.82, "alpaca_cash": 13.69}

    launcher._get_broker_cash_balances = fake_balances

    ib = DummyBroker()
    alpaca = DummyBroker()

    for symbol in ["DIA", "AAPL", "QQQ", "MSFT", "XOM"]:
        if launcher.autonomous_routing_enabled:
            broker, broker_name, meta = await launcher._select_broker_for_symbol(symbol, alpaca, ib)
        else:
            broker, broker_name, meta = await launcher._select_legacy_broker_for_symbol(symbol, alpaca, ib)
        print(f"{symbol:5} -> {broker_name:7} | reason={meta.get('reason')} | ib_cash={meta.get('ib_cash')} alpaca_cash={meta.get('alpaca_cash')}")


if __name__ == "__main__":
    asyncio.run(main())
