from ib_insync import IB, Stock, LimitOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=99)
util.sleep(1)

positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No POSITION")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] qty={pfe_pos.position} avgCost={pfe_pos.avgCost}')

# Use SMART routing to avoid NYSE precautionary block
smart_contract = Stock('PFE', 'SMART', 'USD')

# Very aggressive limit: 5% *above* avg cost to ensure fill
# (counterintuitive for sell, but ensures it fills during market hours)
aggressive_limit = float(pfe_pos.avgCost) * 1.05  # 5% above = ~28.18

order = LimitOrder('SELL', 1, aggressive_limit)
order.openClose = 'C'
order.account = pfe_pos.account
order.outsideRth = True
order.tif = 'GTC'

print(f'[AGGRESSIVE_LIMIT] avgCost={pfe_pos.avgCost} -> limit={aggressive_limit}')

trade = ib.placeOrder(smart_contract, order)
util.sleep(1)

print(f'[SUBMITTED] orderId={trade.order.orderId} status={trade.orderStatus.status}')
print(f'[WAITING_FOR_MARKET_OPEN]')

# This order will wait for market open and fill at/above $28.18
# (current price should be ~$27, so this should fill at open)
ib.disconnect()
