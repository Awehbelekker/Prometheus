from ib_insync import IB, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=93)
util.sleep(1)

# Get open orders
orders = ib.openOrders()
print('[OPEN_ORDERS]')
for o in orders:
    print(f'  OrderId={o.orderId} Status={o.status} Action={o.action} Filled={o.filled}/{o.totalQty} LmtPrice={o.lmtPrice}')

# Get positions
positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print('[POSITIONS]')
for p in positions:
    print(f'  {p.account} {p.contract.symbol} qty={p.position}')

ib.disconnect()
