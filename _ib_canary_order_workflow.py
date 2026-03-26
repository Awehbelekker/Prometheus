#!/usr/bin/env python3
"""
Tiny controlled IB canary workflow:
1) Connect to IB
2) Submit tiny BUY (default 1 share of F)
3) Verify position delta
4) Submit SELL to flatten back to baseline
"""

import asyncio
import os
import sys
from datetime import datetime
from decimal import Decimal
from urllib.request import urlopen
import json
import logging

from brokers.interactive_brokers_broker import InteractiveBrokersBroker
from brokers.universal_broker_interface import Order, OrderSide, OrderType
from core.real_time_market_data import get_stock_price


CANARY_SYMBOL = os.getenv("IB_CANARY_SYMBOL", "F").strip().upper()
MAX_NOTIONAL_USD = float(os.getenv("IB_CANARY_MAX_NOTIONAL", "30"))
DEFAULT_QTY = int(float(os.getenv("IB_CANARY_QTY", "1")))


def quiet_logs() -> None:
    for name in (
        "ibapi",
        "brokers.interactive_brokers_broker",
        "services.performance_monitor",
        "monitoring.ib_execution_tracker",
        "core.real_time_market_data",
        "core.polygon_premium_provider",
    ):
        logging.getLogger(name).setLevel(logging.WARNING)


async def get_qty_for_symbol(broker: InteractiveBrokersBroker, symbol: str) -> int:
    qty = DEFAULT_QTY
    try:
        md = await broker.get_market_data(symbol)
        px = float(md.get("price") or 0)
        if px > 0:
            capped_qty = max(1, int(MAX_NOTIONAL_USD // px))
            qty = min(DEFAULT_QTY, int(capped_qty))
            print(f"[CANARY] Market price={px:.4f}, qty={qty}, max_notional={MAX_NOTIONAL_USD:.2f}")
        else:
            print("[CANARY] Market price unavailable; using default qty")
    except Exception as exc:
        print(f"[CANARY] Market data error; using default qty. details={exc}")
    return max(1, int(qty))


async def get_reference_price(broker: InteractiveBrokersBroker, symbol: str) -> float:
    # IB quote first.
    try:
        md = await broker.get_market_data(symbol)
        for key in ("price", "last", "ask", "bid", "close"):
            v = float(md.get(key) or 0)
            if v > 0:
                print(f"[CANARY] Reference price from IB {key}={v:.4f}")
                return v
    except Exception as exc:
        print(f"[CANARY] IB quote unavailable. details={exc}")

    # Internal market-data fallback (Yahoo/Polygon orchestrated by project code).
    try:
        px = float(await get_stock_price(symbol))
        if px > 0:
            print(f"[CANARY] Reference price from market orchestrator={px:.4f}")
            return px
    except Exception as exc:
        print(f"[CANARY] Market orchestrator unavailable. details={exc}")

    # Direct Yahoo fallback for risk-model input.
    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        with urlopen(url, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        result = payload.get("quoteResponse", {}).get("result", [])
        if result:
            px = float(result[0].get("regularMarketPrice") or 0)
            if px > 0:
                print(f"[CANARY] Reference price from Yahoo={px:.4f}")
                return px
    except Exception as exc:
        print(f"[CANARY] Yahoo fallback unavailable. details={exc}")

    return 0.0


async def get_position_qty(broker: InteractiveBrokersBroker, symbol: str) -> float:
    pos = await broker.get_position(symbol)
    if not pos:
        return 0.0
    return float(pos.quantity)


async def main() -> int:
    quiet_logs()
    print("=" * 70)
    print(f"IB CANARY WORKFLOW START {datetime.now().isoformat(timespec='seconds')}")
    print(f"Symbol={CANARY_SYMBOL}")

    config = {
        "host": os.getenv("IB_HOST", "127.0.0.1"),
        "port": int(os.getenv("IB_PORT", "4002")),
        "client_id": int(os.getenv("IB_CLIENT_ID", "92")),
        "paper_trading": False,
        "account_id": os.getenv("IB_ACCOUNT_ID", "U21922116"),
    }

    broker = InteractiveBrokersBroker(config)
    connected = await broker.connect()
    if not connected:
        print("[FAIL] Could not connect to IB")
        return 2

    try:
        account = await broker.get_account()
        print(
            f"[CHECK] Account={account.account_id} cash=${account.cash:.2f} equity=${account.equity:.2f}"
        )

        qty = await get_qty_for_symbol(broker, CANARY_SYMBOL)
        ref_price = await get_reference_price(broker, CANARY_SYMBOL)
        base_qty = await get_position_qty(broker, CANARY_SYMBOL)
        print(f"[CHECK] Baseline position {CANARY_SYMBOL}={base_qty}")

        if ref_price <= 0:
            print("[FAIL] Could not determine reference price for risk validation")
            return 6

        if account.cash < 10:
            print("[FAIL] Not enough cash for safe canary")
            return 3

        buy_qty = Decimal(str(qty))
        ref_price_dec = Decimal(str(ref_price))

        buy_limit = (ref_price_dec * Decimal("1.05")).quantize(Decimal("0.01"))
        buy = Order(
            symbol=CANARY_SYMBOL,
            quantity=buy_qty,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=buy_limit,
            limit_price=buy_limit,
            time_in_force="day",
        )
        buy = await broker.submit_order(buy)
        print(
            f"[CHECK] BUY submitted broker_order_id={buy.broker_order_id} qty={buy_qty} limit={buy_limit}"
        )

        await asyncio.sleep(6)
        after_buy_qty = await get_position_qty(broker, CANARY_SYMBOL)
        delta = after_buy_qty - base_qty
        sell_qty = int(round(delta))
        print(f"[CHECK] Position after BUY {CANARY_SYMBOL}={after_buy_qty} delta={delta}")

        if sell_qty <= 0:
            print("[FAIL] BUY did not create positive position delta; not sending flatten SELL")
            return 4

        sell_limit = (ref_price_dec * Decimal("0.95")).quantize(Decimal("0.01"))
        sell = Order(
            symbol=CANARY_SYMBOL,
            quantity=Decimal(str(sell_qty)),
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=sell_limit,
            limit_price=sell_limit,
            time_in_force="day",
        )
        sell = await broker.submit_order(sell)
        print(
            f"[CHECK] SELL submitted broker_order_id={sell.broker_order_id} qty={sell_qty} limit={sell_limit}"
        )

        await asyncio.sleep(8)
        final_qty = await get_position_qty(broker, CANARY_SYMBOL)
        print(f"[CHECK] Final position {CANARY_SYMBOL}={final_qty} (target baseline={base_qty})")

        if abs(final_qty - base_qty) > 1e-6:
            print("[WARN] Position not fully flattened to baseline")
            return 5

        print("[PASS] IB canary workflow completed and flattened successfully")
        return 0

    finally:
        await broker.disconnect()
        print("[CHECK] Disconnected from IB")
        print("=" * 70)


if __name__ == "__main__":
    try:
        code = asyncio.run(main())
    except Exception as exc:
        print(f"[FAIL] Unhandled exception: {exc}")
        code = 9
    sys.exit(code)
