"""Quick IB Position Check with PROMETHEUS Decision"""
from ib_insync import IB, Stock, util
import time
import yfinance as yf

# Exit thresholds
TAKE_PROFIT_PCT = 0.08   # 8%
STOP_LOSS_PCT = 0.03     # 3%
MIN_PROFIT_PCT = 0.005   # 0.5%

def get_yahoo_price(symbol):
    """Get current price from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice') or info.get('previousClose')
        return price
    except:
        return None

def check_exit(pnl_pct):
    """Check if position should be exited"""
    if pnl_pct >= TAKE_PROFIT_PCT:
        return True, f"TAKE_PROFIT ({pnl_pct*100:.2f}% >= {TAKE_PROFIT_PCT*100:.1f}%)"
    if pnl_pct <= -STOP_LOSS_PCT:
        return True, f"STOP_LOSS ({pnl_pct*100:.2f}% <= -{STOP_LOSS_PCT*100:.1f}%)"
    if pnl_pct >= MIN_PROFIT_PCT:
        return True, f"PROFIT_TAKING ({pnl_pct*100:.2f}% gain)"
    return False, "HOLD - No exit conditions met"

def main():
    ib = IB()
    print("Connecting to IB Gateway...")
    ib.connect('127.0.0.1', 4002, clientId=11)

    # Request delayed market data (free)
    ib.reqMarketDataType(3)  # 3 = delayed data

    print()
    print("=" * 60)
    print("PROMETHEUS IB POSITION ANALYSIS")
    print("=" * 60)

    positions = ib.positions()

    if not positions:
        print("No positions found")
        ib.disconnect()
        return

    for pos in positions:
        symbol = pos.contract.symbol
        qty = pos.position
        avg_cost = pos.avgCost

        if qty == 0:
            continue

        # Get current price using delayed data
        contract = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        ticker = ib.reqMktData(contract, '', False, False)
        time.sleep(3)  # Wait for delayed data

        # Try various price fields from IB
        current_price = None
        for price in [ticker.last, ticker.close, ticker.bid, ticker.ask]:
            if price and price > 0 and not (isinstance(price, float) and price != price):  # Check for nan
                current_price = price
                break

        ib.cancelMktData(contract)

        # If IB doesn't have price, use Yahoo Finance
        if not current_price or current_price <= 0 or current_price == avg_cost:
            yahoo_price = get_yahoo_price(symbol)
            if yahoo_price and yahoo_price > 0:
                current_price = yahoo_price
                print(f"  (Using Yahoo Finance price)")
            else:
                current_price = avg_cost  # Fallback to avg cost

        # Calculate P/L
        unrealized_pnl = (current_price - avg_cost) * qty
        pnl_pct = (current_price - avg_cost) / avg_cost if avg_cost > 0 else 0
        pnl_sign = "+" if pnl_pct >= 0 else ""

        print(f"\n{symbol}:")
        print(f"  Shares: {qty}")
        print(f"  Avg Cost: ${avg_cost:.2f}")
        print(f"  Current: ${current_price:.2f}")
        print(f"  P/L: ${unrealized_pnl:.2f} ({pnl_sign}{pnl_pct*100:.2f}%)")

        should_exit, reason = check_exit(pnl_pct)
        decision = "SELL" if should_exit else "HOLD"
        emoji = "SELL" if should_exit else "HOLD"
        print(f"  PROMETHEUS Decision: {emoji}")
        print(f"  Reason: {reason}")

    print()
    print("=" * 60)
    print("Note: Market is closed. Prices may be from last close.")
    print("=" * 60)
    ib.disconnect()

if __name__ == "__main__":
    main()

