#!/usr/bin/env python3
from ib_insync import IB, Stock, LimitOrder
import sys
import time


def main() -> int:
    ib = IB()
    try:
        ib.connect('127.0.0.1', 4002, clientId=94, timeout=15)
        positions = ib.positions()
        pfe = None
        for pos in positions:
            if pos.contract.symbol == 'PFE':
                pfe = pos
                break

        if not pfe or int(round(pfe.position)) <= 0:
            print('NO_POSITION_TO_FLATTEN')
            return 0

        qty = int(round(pfe.position))
        print('PFE_POSITION', qty, 'AVG_COST', float(pfe.avgCost))
        qualified = ib.qualifyContracts(Stock('PFE', 'SMART', 'USD'))
        if not qualified:
            print('SMART_QUALIFY_FAILED')
            return 2
        contract = qualified[0]
        print('SMART_CONTRACT', contract.conId, contract.exchange, contract.primaryExchange)
        order = LimitOrder('SELL', qty, 24.00, tif='GTC', outsideRth=True)
        trade = ib.placeOrder(contract, order)
        print('SELL_SUBMITTED', trade.order.orderId)

        deadline = time.time() + 20
        while time.time() < deadline:
            ib.waitOnUpdate(timeout=2)
            status = trade.orderStatus.status
            filled = float(trade.orderStatus.filled or 0)
            remaining = float(trade.orderStatus.remaining or 0)
            print('STATUS', status, 'FILLED', filled, 'REMAINING', remaining)
            if status in ('Filled', 'Cancelled', 'Inactive') or remaining == 0:
                break

        positions_after = ib.positions()
        qty_after = 0
        for pos in positions_after:
            if pos.contract.symbol == 'PFE':
                qty_after = float(pos.position)
                break
        print('PFE_POSITION_AFTER', qty_after)
        return 0 if qty_after == 0 else 1
    finally:
        if ib.isConnected():
            ib.disconnect()


if __name__ == '__main__':
    sys.exit(main())
