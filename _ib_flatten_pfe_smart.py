from ib_insync import IB, Stock, LimitOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=98)
util.sleep(1)

# Get current position
positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position found")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] {pfe_pos.account} {pfe_pos.contract.symbol} qty={pfe_pos.position} avgCost={pfe_pos.avgCost}')

# Create SMART-routed contract instead of NYSE
smart_contract = Stock('PFE', 'SMART', 'USD')
print(f'[SMART_CONTRACT] {smart_contract.symbol} exchange={smart_contract.exchange}')

# Limit price slightly below avg cost for likely fill
limit_price = float(pfe_pos.avgCost) * 0.97  # 3% below = ~26

order = LimitOrder('SELL', 1, limit_price)
order.openClose = 'C'
order.account = pfe_pos.account
order.outsideRth = True
order.tif = 'GTC'

print(f'[ORDER] SELL 1 {smart_contract.symbol} @ {limit_price} openClose={order.openClose} TIF={order.tif}')

trade = ib.placeOrder(smart_contract, order)
util.sleep(2)

print(f'[SUBMITTED] orderId={trade.order.orderId} status={trade.orderStatus.status}')

# Wait for fill
for i in range(6):
    util.sleep(1)
    if trade.orderStatus.status in ['Filled', 'Cancelled', 'Rejected']:
        break
    print(f'  [{i+1}s] {trade.orderStatus.status}')

positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[POSITIONS_AFTER] {[(p.account, p.position, p.avgCost) for p in positions_after]}')

ib.disconnect()
