"""
PROMETHEUS IB Auto-Exit Monitor
Automatically monitors IB positions and executes sells when exit conditions are met
Runs continuously until all positions are sold or manually stopped

SIMPLE VERSION: Uses ib_insync for cleaner connection management
"""

from ib_insync import IB, Stock, MarketOrder
import time
from datetime import datetime, timedelta
import pytz
import logging
import sys

# Setup logging
log_filename = f'prometheus_ib_auto_exit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Exit thresholds - CONFIGURABLE
TAKE_PROFIT_PCT = 0.08   # 8% profit target
STOP_LOSS_PCT = 0.03     # 3% stop loss
MIN_PROFIT_PCT = 0.005   # 0.5% minimum profit to take

# Connection settings
IB_HOST = '127.0.0.1'
IB_PORT = 4002
CLIENT_ID = 88  # Unique client ID to avoid conflicts

# Global IB instance
ib = IB()

def get_eastern_time():
    """Get current time in Eastern timezone"""
    return datetime.now(pytz.timezone('US/Eastern'))

def is_market_open():
    """Check if US stock market is open"""
    now = get_eastern_time()

    # Weekend check
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False

    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now <= market_close

def time_until_market_open():
    """Calculate time until next market open"""
    now = get_eastern_time()

    # Find next trading day
    next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)

    if now.weekday() >= 5:  # Weekend
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        next_open = next_open + timedelta(days=days_until_monday)
    elif now >= now.replace(hour=16, minute=0, second=0, microsecond=0):  # After close
        next_open = next_open + timedelta(days=1)
        if next_open.weekday() >= 5:  # Skip weekend
            next_open = next_open + timedelta(days=(7 - next_open.weekday()))
    elif now < next_open:  # Before open today
        pass  # next_open is already correct

    return next_open - now

def check_exit_conditions(pnl_pct):
    """Check if position should be exited"""
    if pnl_pct >= TAKE_PROFIT_PCT:
        return True, f"TAKE_PROFIT ({pnl_pct*100:.2f}% >= {TAKE_PROFIT_PCT*100:.1f}%)"
    if pnl_pct <= -STOP_LOSS_PCT:
        return True, f"STOP_LOSS ({pnl_pct*100:.2f}% <= -{STOP_LOSS_PCT*100:.1f}%)"
    if pnl_pct >= MIN_PROFIT_PCT:
        return True, f"PROFIT_TAKING ({pnl_pct*100:.2f}% gain)"
    return False, "HOLD"

def connect_to_ib():
    """Connect to IB Gateway with retry logic"""
    global ib
    max_retries = 3

    for attempt in range(max_retries):
        try:
            if ib.isConnected():
                return True

            logger.info(f"Connecting to IB Gateway at {IB_HOST}:{IB_PORT} (attempt {attempt+1}/{max_retries})...")
            ib.connect(IB_HOST, IB_PORT, clientId=CLIENT_ID, timeout=20)
            ib.reqMarketDataType(3)  # Delayed data
            logger.info("✅ Connected to IB Gateway")
            return True
        except Exception as e:
            logger.error(f"Connection attempt {attempt+1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return False

def disconnect_from_ib():
    """Safely disconnect from IB"""
    global ib
    try:
        if ib.isConnected():
            ib.disconnect()
            logger.info("Disconnected from IB Gateway")
    except:
        pass

def execute_sell(symbol, quantity):
    """Execute a market sell order"""
    global ib
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        order = MarketOrder('SELL', quantity)
        trade = ib.placeOrder(contract, order)

        logger.info(f"📤 SELL ORDER placed for {symbol}, waiting for fill...")

        # Wait for fill (max 60 seconds)
        for _ in range(60):
            ib.sleep(1)
            if trade.orderStatus.status == 'Filled':
                logger.info(f"✅ SOLD {symbol}: {quantity} shares @ ${trade.orderStatus.avgFillPrice:.2f}")
                return True, trade.orderStatus.avgFillPrice
            elif trade.orderStatus.status in ['Cancelled', 'ApiCancelled', 'Inactive']:
                logger.error(f"❌ Order cancelled for {symbol}: {trade.orderStatus.status}")
                return False, 0

        logger.warning(f"⏳ Order still pending for {symbol}: {trade.orderStatus.status}")
        return False, 0
    except Exception as e:
        logger.error(f"❌ Error selling {symbol}: {e}")
        return False, 0

def monitor_positions():
    """Monitor positions and execute exits"""
    global ib

    positions = ib.positions()
    if not positions:
        return []

    results = []
    for pos in positions:
        symbol = pos.contract.symbol
        qty = pos.position
        avg_cost = pos.avgCost

        if qty <= 0:
            continue

        # Get current market price from IB
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            ib.qualifyContracts(contract)
            ticker = ib.reqMktData(contract)
            ib.sleep(2)  # Wait for data

            current_price = ticker.marketPrice()
            if current_price <= 0 or current_price != current_price:  # NaN check
                current_price = ticker.last or ticker.close or avg_cost

            ib.cancelMktData(contract)
        except:
            current_price = avg_cost  # Fallback

        # Calculate P/L
        pnl_pct = (current_price - avg_cost) / avg_cost if avg_cost > 0 else 0
        unrealized_pnl = (current_price - avg_cost) * qty

        emoji = "🟢" if pnl_pct >= 0 else "🔴"
        pnl_sign = "+" if pnl_pct >= 0 else ""
        logger.info(f"  {emoji} {symbol}: ${current_price:.2f} | Cost: ${avg_cost:.2f} | P/L: ${unrealized_pnl:.2f} ({pnl_sign}{pnl_pct*100:.2f}%)")

        # Check exit conditions
        should_exit, reason = check_exit_conditions(pnl_pct)

        if should_exit:
            logger.info(f"  🚨 EXIT SIGNAL: {symbol} - {reason}")
            success, fill_price = execute_sell(symbol, qty)
            if success:
                realized_pnl = (fill_price - avg_cost) * qty
                logger.info(f"  💰 REALIZED P/L: ${realized_pnl:.2f}")
                results.append({'symbol': symbol, 'action': 'SOLD', 'pnl': realized_pnl})
        else:
            results.append({'symbol': symbol, 'action': 'HOLD', 'reason': reason})

    return results

def run_auto_exit_monitor():
    """Main monitoring loop - runs until all positions are closed or stopped"""
    print("=" * 70)
    print("   PROMETHEUS IB AUTO-EXIT MONITOR")
    print("=" * 70)
    print(f"   Exit Thresholds:")
    print(f"     Take Profit: {TAKE_PROFIT_PCT*100:.1f}%")
    print(f"     Stop Loss:   {STOP_LOSS_PCT*100:.1f}%")
    print(f"     Min Profit:  {MIN_PROFIT_PCT*100:.1f}%")
    print(f"   IB Gateway: {IB_HOST}:{IB_PORT}")
    print(f"   Log file: {log_filename}")
    print("=" * 70)
    print("   Press Ctrl+C to stop")
    print("=" * 70)

    # Check if market is open
    now = get_eastern_time()
    if not is_market_open():
        wait_time = time_until_market_open()
        hours = wait_time.total_seconds() / 3600
        next_open = now + wait_time
        print(f"\n⏰ Market is CLOSED")
        print(f"   Current time: {now.strftime('%A, %B %d %Y %H:%M ET')}")
        print(f"   Next open: {next_open.strftime('%A, %B %d %Y %H:%M ET')}")
        print(f"   Time until open: {hours:.1f} hours")
        print(f"\n💤 Waiting for market to open...")
        print("   (Script will automatically start monitoring when market opens)")

    try:
        while True:
            # Wait for market to open
            if not is_market_open():
                now = get_eastern_time()
                # Show status every 30 minutes
                if now.minute in [0, 30] and now.second < 60:
                    wait_time = time_until_market_open()
                    hours = wait_time.total_seconds() / 3600
                    logger.info(f"Market closed. {now.strftime('%A %H:%M ET')} - {hours:.1f}h until open")
                time.sleep(60)
                continue

            # Connect to IB
            if not ib.isConnected():
                if not connect_to_ib():
                    logger.error("Failed to connect. Retrying in 60s...")
                    time.sleep(60)
                    continue

            # Monitor and manage positions
            logger.info(f"📊 Position Check @ {get_eastern_time().strftime('%H:%M:%S ET')}")
            results = monitor_positions()

            if not results:
                logger.info("   No positions found. Checking again in 60s...")

            # Check if all positions are sold
            remaining = [r for r in results if r['action'] == 'HOLD']
            if results and not remaining:
                logger.info("🎉 All positions have been exited!")
                break

            # Wait before next check
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("\n⏹️ Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        disconnect_from_ib()
        logger.info("Monitor shutdown complete")

if __name__ == "__main__":
    run_auto_exit_monitor()

