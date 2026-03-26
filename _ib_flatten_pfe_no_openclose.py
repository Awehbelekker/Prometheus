from ib_insync import IB, Stock, LimitOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=102)
util.sleep(1)

positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] qty={pfe_pos.position}')

# Try SMART without explicit openClose attribute
smart_contract = Stock('PFE', 'SMART', 'USD')

# Aggressive limit to ensure fill (near bid/ask midpoint)
limit_price = float(pfe_pos.avgCost) * 0.99  # 1% below = ~26.57

order = LimitOrder('SELL', 1, limit_price)
# NO openClose attribute - let IB infer it
order.tif = 'DAY'

print(f'[SUBMIT] SELL 1 @ {limit_price} (no explicit openClose)')

trade = ib.placeOrder(smart_contract, order)
util.sleep(2)

print(f'[STATUS] orderId={trade.order.orderId} status={trade.orderStatus.status}')

for i in range(8):
    util.sleep(1)
    print(f'  [{i+1}s] {trade.orderStatus.status} filled={trade.orderStatus.filled}')
    if trade.orderStatus.filled > 0:
        break

positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[FINAL] {[(p.position, p.avgCost) for p in positions_after]}')

ib.disconnect()
