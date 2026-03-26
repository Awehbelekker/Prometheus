from ib_insync import IB, Stock, LimitOrder, util
import time

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=95)
util.sleep(1)

# Get current position
positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position found")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] {pfe_pos.account} {pfe_pos.contract.symbol} qty={pfe_pos.position} avgCost={pfe_pos.avgCost}')

# Use the held position's contract
contract = pfe_pos.contract
print(f'[CONTRACT] {contract.symbol} conId={contract.conId} exchange={contract.exchange}')

# Use avg cost as baseline (position was filled at $27.0781, now $26.8367)
# Try limit price slightly below avg cost (conservative)
avg_cost = pfe_pos.avgCost
limit_price = avg_cost * 0.98  # 2% below avg cost = ~26.38
print(f'[LIMIT_PRICE] avgCost={avg_cost} limit={limit_price}')

# Create close-only SELL order
order = LimitOrder('SELL', 1, limit_price)
order.openClose = 'C'  # Explicit close semantics
order.account = pfe_pos.account
order.tif = 'GTC'
order.outsideRth = True

print(f'[ORDER_SETUP] account={order.account} openClose={order.openClose} qty=1 price={limit_price}')

# Submit order
trade = ib.placeOrder(contract, order)
util.sleep(1)

print(f'[SELL_SUBMITTED] orderId={trade.order.orderId}')
print(f'[STATUS] {trade.orderStatus.status} Filled={trade.orderStatus.filled}/{trade.orderStatus.remaining}')

# Wait a bit for potential fill
util.sleep(4)

# Check position again
positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[POSITIONS_AFTER] {[(p.account, p.position) for p in positions_after]}')

# Check if order filled
print(f'[FINAL_STATUS] {trade.orderStatus.status} Filled={trade.orderStatus.filled}/{trade.orderStatus.remaining}')

ib.disconnect()
