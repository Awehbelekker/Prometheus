from ib_insync import IB, Stock, MarketOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=97)
util.sleep(1)

# Get current position
positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position found")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] {pfe_pos.account} {pfe_pos.contract.symbol} qty={pfe_pos.position}')

contract = pfe_pos.contract

# Try LIMIT order with GTC (good til cance) TIF which works after-hours
from decimal import Decimal
limit_price = float(pfe_pos.avgCost) * 0.99  # Aggressive: 1% below avg

order = MarketOrder('SELL', 1)
order.openClose = 'C'
order.account = pfe_pos.account
order.outsideRth = True
order.tif = 'IOC'  # Immediate or Cancel - try this for after-hours

print(f'[ORDER_TIF_IOC] account={order.account} openClose={order.openClose} tif={order.tif}')

try:
    trade = ib.placeOrder(contract, order)
    util.sleep(2)
    print(f'[SELL_SUBMITTED] orderId={trade.order.orderId}')
    print(f'[STATUS] {trade.orderStatus.status}')
except Exception as e:
    print(f'[ERROR] {e}')

ib.disconnect()
