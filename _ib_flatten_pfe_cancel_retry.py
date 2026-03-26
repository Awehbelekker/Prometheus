from ib_insync import IB, Stock, LimitOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=101)
util.sleep(1)

# Cancel all pending orders first
trades = ib.openTrades()
print(f'[OPEN_ORDERS] {len(trades)}')
for t in trades:
    if t.contract.symbol == 'PFE':
        print(f'  Cancelling orderId={t.order.orderId}')
        ib.cancelOrder(t.order)
        util.sleep(1)

# Get fresh position
positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] qty={pfe_pos.position} avgCost={pfe_pos.avgCost}')

# Try with NYSE contract directly (market is open, precautionary block might only apply to certain order types after-hours)
nyse_contract = Stock('PFE', 'NYSE', 'USD')
print(f'[CONTRACT] NYSE direct')

# Limit price at midpoint (should have better fill odds)
limit_price = float(pfe_pos.avgCost) - 0.01  # Just below cost = ~26.83

order = LimitOrder('SELL', 1, limit_price)
order.openClose = 'C'
order.account = pfe_pos.account
order.tif = 'DAY'

print(f'[SUBMIT] SELL 1 @ {limit_price}')

trade = ib.placeOrder(nyse_contract, order)
util.sleep(2)

print(f'[STATUS] orderId={trade.order.orderId} status={trade.orderStatus.status}')

# Wait for fill
for i in range(8):
    util.sleep(1)
    if trade.orderStatus.filled > 0:
        print(f'[FILLED] {trade.orderStatus.filled} shares')
        break
    print(f'  [{i+1}s] {trade.orderStatus.status}')

positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[FINAL] qty={[p.position for p in positions_after] if positions_after else 0.0}')

ib.disconnect()
