#!/usr/bin/env python3
import asyncio
from decimal import Decimal

from brokers.interactive_brokers_broker import InteractiveBrokersBroker
from brokers.universal_broker_interface import Order, OrderSide, OrderType


async def main() -> int:
    broker = InteractiveBrokersBroker({
        'host': '127.0.0.1',
        'port': 4002,
        'client_id': 93,
        'paper_trading': False,
        'account_id': 'U21922116',
    })
    ok = await broker.connect()
    print('CONNECTED', ok)
    if not ok:
        return 2

    try:
        pos = await broker.get_position('PFE')
        qty = int(round(float(pos.quantity))) if pos else 0
        print('PFE_POSITION', qty)
        if qty <= 0:
            print('NO_POSITION_TO_FLATTEN')
            return 0

        order = Order(
            symbol='PFE',
            quantity=Decimal(str(qty)),
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            price=Decimal('24.00'),
            limit_price=Decimal('24.00'),
            time_in_force='day',
        )
        order = await broker.submit_order(order)
        print('SELL_SUBMITTED', order.broker_order_id)
        await asyncio.sleep(10)
        pos2 = await broker.get_position('PFE')
        qty2 = float(pos2.quantity) if pos2 else 0.0
        print('PFE_POSITION_AFTER', qty2)
        return 0 if qty2 == 0.0 else 1
    finally:
        await broker.disconnect()


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
