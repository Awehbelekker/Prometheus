from ib_insync import IB, Stock, LimitOrder, util
import time

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=94)
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
print(f'[CONTRACT] {contract.symbol} conId={contract.conId} exchange={contract.exchange} primaryExchange={contract.primaryExchange}')

# Get market data to calculate reasonable limit price
ticker = ib.reqMktData(contract)
util.sleep(2)
bid = ticker.bid if ticker.bid > 0 else None
ask = ticker.ask if ticker.ask > 0 else None
print(f'[MARKET] bid={bid} ask={ask}')

# Use a limit price just below the bid (5% below current)
current_price = pfe_pos.avgCost if not bid else bid
limit_price = current_price * 0.95 if current_price else 25.0
print(f'[LIMIT_PRICE] {limit_price}')

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
util.sleep(3)

# Check position again
positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[POSITIONS_AFTER] {[(p.account, p.position) for p in positions_after]}')

ib.disconnect()
