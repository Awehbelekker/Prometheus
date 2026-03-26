from ib_insync import IB, Stock, MarketOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=96)
util.sleep(1)

# Get current position
positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position found")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] {pfe_pos.account} {pfe_pos.contract.symbol} qty={pfe_pos.position} avgCost={pfe_pos.avgCost}')

contract = pfe_pos.contract
print(f'[CONTRACT] {contract.symbol} conId={contract.conId} exchange={contract.exchange}')

# Create close-only MARKET order for immediate fill
order = MarketOrder('SELL', 1)
order.openClose = 'C'  # Explicit close semantics
order.account = pfe_pos.account
order.outsideRth = True

print(f'[ORDER_SETUP] account={order.account} openClose={order.openClose} qty=1 MARKET outsideRth=True')

# Submit order
trade = ib.placeOrder(contract, order)
util.sleep(1)

print(f'[SELL_SUBMITTED] orderId={trade.order.orderId}')
print(f'[STATUS] {trade.orderStatus.status} Filled={trade.orderStatus.filled}/{trade.orderStatus.remaining}')

# Wait for fill
for i in range(8):
    util.sleep(1)
    print(f'  [{i+1}s] status={trade.orderStatus.status} filled={trade.orderStatus.filled}')
    if trade.orderStatus.status in ['Filled', 'Cancelled']:
        break

# Check position
positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[POSITIONS_AFTER] {[(p.account, p.position) for p in positions_after]}')

ib.disconnect()
