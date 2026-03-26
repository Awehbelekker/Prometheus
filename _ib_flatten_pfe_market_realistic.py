from ib_insync import IB, Stock, LimitOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=100)
util.sleep(1)

positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] qty={pfe_pos.position} avgCost={pfe_pos.avgCost}')

# Use SMART routing
smart_contract = Stock('PFE', 'SMART', 'USD')

# Conservative limit: slightly BELOW current market (should fill quickly)
# Use avgCost as baseline, go 0.5% below it
limit_price = float(pfe_pos.avgCost) * 0.995  # ~26.72

order = LimitOrder('SELL', 1, limit_price)
order.openClose = 'C'
order.account = pfe_pos.account
order.outsideRth = True
order.tif = 'DAY'  # During market hours, DAY is fine

print(f'[SELL] qty=1 limit={limit_price} avgCost={pfe_pos.avgCost}')

trade = ib.placeOrder(smart_contract, order)
util.sleep(1)

print(f'[SUBMITTED] orderId={trade.order.orderId} status={trade.orderStatus.status}')

# Wait for fill during market hours
for i in range(10):
    util.sleep(1)
    print(f'  [{i+1}s] status={trade.orderStatus.status} filled={trade.orderStatus.filled}')
    if 'Filled' in trade.orderStatus.status or 'Cancelled' in trade.orderStatus.status:
        break

positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if positions_after:
    print(f'[STILL_OPEN] qty={positions_after[0].position}')
else:
    print(f'[FLAT] Position closed successfully!')

ib.disconnect()
