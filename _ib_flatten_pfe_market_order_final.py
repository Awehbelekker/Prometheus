from ib_insync import IB, Stock, MarketOrder, util

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=104)
util.sleep(1)

positions = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
if not positions:
    print("No PFE position")
    ib.disconnect()
    exit(1)

pfe_pos = positions[0]
print(f'[POSITION] qty={pfe_pos.position}')

smart_contract = Stock('PFE', 'SMART', 'USD')

# Try MARKET order (not LIMIT)
order = MarketOrder('SELL', 1)
order.tif = 'DAY'

print(f'[SUBMIT] MARKET SELL 1 PFE on SMART')

trade = ib.placeOrder(smart_contract, order)
util.sleep(2)

print(f'[STATUS] {trade.orderStatus.status}')
print(f'[LOG]')
for entry in trade.log:
    if entry.message:
        print(f'  {entry.status}: {entry.message} (code={entry.errorCode})')

# Wait for fill
for i in range(6):
    util.sleep(1)
    print(f'  [{i+1}s] {trade.orderStatus.status} filled={trade.orderStatus.filled}')
    if trade.orderStatus.filled > 0 or 'Cancelled' in trade.orderStatus.status:
        break

positions_after = [p for p in ib.positions() if 'PFE' in p.contract.symbol]
print(f'[FINAL] {[(p.position) for p in positions_after] if positions_after else "FLAT"}')

ib.disconnect()
