#!/usr/bin/env python3
from ib_insync import IB, LimitOrder
import sys
import time


def main() -> int:
    ib = IB()
    try:
        ib.connect('127.0.0.1', 4002, clientId=99, timeout=15)
        positions = [p for p in ib.positions() if p.contract.symbol == 'PFE']
        print('POSITIONS', [(p.account, p.contract.conId, p.contract.exchange, float(p.position), float(p.avgCost)) for p in positions])
        if not positions:
            print('NO_POSITION')
            return 0

        pfe = positions[0]
        qty = int(round(float(pfe.position)))
        if qty <= 0:
            print('NO_LONG_POSITION')
            return 0

        contract = pfe.contract
        order = LimitOrder('SELL', qty, 24.00, tif='GTC', outsideRth=True)
        order.account = pfe.account
        order.openClose = 'C'
        order.transmit = True
        print('ORDER_SETUP', order.account, order.openClose, contract.conId, contract.exchange)
        trade = ib.placeOrder(contract, order)
        print('SELL_SUBMITTED', trade.order.orderId)

        deadline = time.time() + 20
        while time.time() < deadline:
            ib.waitOnUpdate(timeout=2)
            print('STATUS', trade.orderStatus.status, 'FILLED', float(trade.orderStatus.filled or 0), 'REMAINING', float(trade.orderStatus.remaining or 0))
            if trade.orderStatus.status in ('Filled', 'Cancelled', 'Inactive') or float(trade.orderStatus.remaining or 0) == 0:
                break

        positions_after = [p for p in ib.positions() if p.contract.symbol == 'PFE']
        print('POSITIONS_AFTER', [(p.account, p.contract.conId, p.contract.exchange, float(p.position), float(p.avgCost)) for p in positions_after])
        return 0
    finally:
        if ib.isConnected():
            ib.disconnect()


if __name__ == '__main__':
    sys.exit(main())
