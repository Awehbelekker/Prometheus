"""
PROMETHEUS IB Position Monitor
Monitors IB positions and executes SELL orders when exit conditions are met
Uses AI-based decision making for optimal exit timing
"""

from ib_insync import IB, Stock, MarketOrder
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrometheusIBPositionMonitor:
    """Monitors IB positions and executes AI-driven exits"""
    
    def __init__(self, host='127.0.0.1', port=4002, client_id=10):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
        
        # Exit parameters
        self.take_profit_pct = 0.08      # 8% take profit
        self.stop_loss_pct = 0.03        # 3% stop loss  
        self.min_profit_pct = 0.005      # 0.5% min profit to consider exit
        self.trailing_stop_pct = 0.025   # 2.5% trailing stop
        
    async def connect(self) -> bool:
        """Connect to IB Gateway"""
        try:
            await self.ib.connectAsync(self.host, self.port, clientId=self.client_id)
            self.connected = True
            logger.info(f"✅ Connected to IB Gateway at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from IB Gateway"""
        if self.connected:
            self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB Gateway")
    
    async def get_positions(self) -> List[Dict]:
        """Get all current positions with P/L calculations"""
        positions = []
        
        for pos in self.ib.positions():
            symbol = pos.contract.symbol
            qty = pos.position
            avg_cost = pos.avgCost
            
            if qty == 0:
                continue
                
            # Get current market price
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)
            ticker = self.ib.reqMktData(contract, '', False, False)
            await asyncio.sleep(1)  # Wait for data
            
            current_price = ticker.marketPrice() if ticker.marketPrice() > 0 else ticker.last
            self.ib.cancelMktData(contract)
            
            if current_price and current_price > 0:
                unrealized_pnl = (current_price - avg_cost) * qty
                pnl_pct = (current_price - avg_cost) / avg_cost
            else:
                unrealized_pnl = 0
                pnl_pct = 0
                current_price = avg_cost
            
            positions.append({
                'symbol': symbol,
                'quantity': qty,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'unrealized_pnl': unrealized_pnl,
                'pnl_pct': pnl_pct,
                'market_value': current_price * qty
            })
        
        return positions
    
    def check_exit_conditions(self, position: Dict) -> tuple:
        """Check if position should be exited. Returns (should_exit, reason)"""
        pnl_pct = position['pnl_pct']
        symbol = position['symbol']
        
        # 1. TAKE PROFIT
        if pnl_pct >= self.take_profit_pct:
            return True, f"💰 TAKE_PROFIT ({pnl_pct*100:.2f}% >= {self.take_profit_pct*100:.1f}%)"
        
        # 2. STOP LOSS
        if pnl_pct <= -self.stop_loss_pct:
            return True, f"🛑 STOP_LOSS ({pnl_pct*100:.2f}% <= -{self.stop_loss_pct*100:.1f}%)"
        
        # 3. SMALL PROFIT - build balance
        if pnl_pct >= self.min_profit_pct:
            return True, f"📈 PROFIT_TAKING ({pnl_pct*100:.2f}% gain)"
        
        return False, "HOLD"
    
    async def execute_sell(self, symbol: str, quantity: float) -> bool:
        """Execute a sell order"""
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)
            order = MarketOrder('SELL', quantity)
            trade = self.ib.placeOrder(contract, order)
            
            # Wait for fill
            for _ in range(30):
                await asyncio.sleep(1)
                if trade.orderStatus.status == 'Filled':
                    logger.info(f"✅ SOLD {symbol}: {quantity} shares @ ${trade.orderStatus.avgFillPrice:.2f}")
                    return True
                elif trade.orderStatus.status in ['Cancelled', 'ApiCancelled']:
                    logger.error(f"❌ Order cancelled for {symbol}")
                    return False
            
            logger.warning(f"⏳ Order pending for {symbol}: {trade.orderStatus.status}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error selling {symbol}: {e}")
            return False
    
    async def monitor_and_exit(self) -> Dict:
        """Main monitoring loop - check positions and execute exits"""
        if not self.connected:
            if not await self.connect():
                return {'error': 'Connection failed'}
        
        logger.info("🔍 PROMETHEUS Position Monitor - Checking IB positions...")
        positions = await self.get_positions()
        
        if not positions:
            logger.info("📊 No open positions")
            return {'positions': 0, 'exits': 0}
        
        logger.info(f"📊 Found {len(positions)} position(s)")
        exits_executed = 0
        
        for pos in positions:
            symbol = pos['symbol']
            pnl_emoji = "🟢" if pos['pnl_pct'] >= 0 else "🔴"
            logger.info(f"  {pnl_emoji} {symbol}: {pos['quantity']} @ ${pos['avg_cost']:.2f} → ${pos['current_price']:.2f} ({pos['pnl_pct']*100:+.2f}%)")
            
            should_exit, reason = self.check_exit_conditions(pos)
            
            if should_exit:
                logger.info(f"  🚨 EXIT: {symbol} - {reason}")
                if await self.execute_sell(symbol, pos['quantity']):
                    exits_executed += 1
        
        return {'positions': len(positions), 'exits': exits_executed}

    async def run_continuous(self, interval_seconds: int = 60):
        """Run continuous monitoring loop"""
        logger.info(f"🚀 Starting PROMETHEUS IB Position Monitor (interval: {interval_seconds}s)")
        logger.info(f"   Take Profit: {self.take_profit_pct*100}% | Stop Loss: {self.stop_loss_pct*100}%")

        if not await self.connect():
            return

        try:
            while True:
                result = await self.monitor_and_exit()
                logger.info(f"📊 Cycle complete: {result['positions']} positions, {result['exits']} exits")
                await asyncio.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("⏹️ Monitor stopped by user")
        finally:
            self.disconnect()


async def main():
    """Main entry point"""
    print("=" * 60)
    print("🔥 PROMETHEUS IB POSITION MONITOR")
    print("=" * 60)
    print("Monitors IB positions and executes AI-driven exits")
    print("Exit conditions: 8% take profit, 3% stop loss, 0.5% min profit")
    print("=" * 60)

    monitor = PrometheusIBPositionMonitor()

    # Single check or continuous?
    mode = input("\nMode: (1) Single check  (2) Continuous monitor: ").strip()

    if mode == "2":
        interval = input("Check interval in seconds (default 60): ").strip()
        interval = int(interval) if interval else 60
        await monitor.run_continuous(interval)
    else:
        await monitor.connect()
        result = await monitor.monitor_and_exit()
        print(f"\nResult: {result}")
        monitor.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

