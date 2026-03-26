from ib_insync import IB, Stock, LimitOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=103)
util.sleep(1)

positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] qty={pfe_pos.position}')

smart_contract = Stock('PFE', 'SMART', 'USD')
limit_price = float(pfe_pos.avgCost) * 0.99

order = LimitOrder('SELL', 1, limit_price)
order.tif = 'DAY'

print(f'[SUBMIT] qty=1 limit={limit_price}')

trade = ib.placeOrder(smart_contract, order)
util.sleep(3)

# Print detailed trade log
print(f'\n[TRADE_LOG]')
for entry in trade.log:
    print(f'  {entry.time} {entry.status} {entry.message} (code={entry.errorCode})')

print(f'\n[STATUS] {trade.orderStatus.status}')
print(f'[FILLED] {trade.orderStatus.filled}/{trade.order.totalQuantity}')

ib.disconnect()
