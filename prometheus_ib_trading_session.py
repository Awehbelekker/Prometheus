#!/usr/bin/env python3
"""
PROMETHEUS Trading Session with Interactive Brokers
Real paper trading with R 10,000 capital and real market data
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrometheusIBTradingSession:
    """PROMETHEUS Trading Session with Interactive Brokers"""
    
    def __init__(self):
        self.session_id = f"ib_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.account_id = "DUN683505"
        self.starting_capital = 540.0  # USD equivalent of R 10,000
        
        # Trading parameters
        self.max_position_size = 10.80  # 2% of $540
        self.max_daily_loss = 25.0
        self.max_daily_trades = 5
        self.stop_loss_percent = 2.0
        
        # Session tracking
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.positions = {}
        self.session_start = datetime.now()
        
        # Market data cache
        self.market_data_cache = {}
        
    def setup_prometheus_environment(self):
        """Setup environment for PROMETHEUS with IB"""
        print("🔧 Configuring PROMETHEUS for IB paper trading...")
        
        # Core IB settings
        os.environ['IB_ENABLED'] = 'true'
        os.environ['IB_HOST'] = '127.0.0.1'
        os.environ['IB_PORT'] = '7497'
        os.environ['IB_CLIENT_ID'] = '2'  # Different client ID to avoid conflicts
        os.environ['PRIMARY_BROKER'] = 'interactive_brokers'
        
        # Capital and risk management
        os.environ['STARTING_CAPITAL_USD'] = str(self.starting_capital)
        os.environ['MAX_POSITION_SIZE_DOLLARS'] = str(self.max_position_size)
        os.environ['MAX_DAILY_LOSS_DOLLARS'] = str(self.max_daily_loss)
        os.environ['DEFAULT_STOP_LOSS_PERCENT'] = str(self.stop_loss_percent)
        
        # PROMETHEUS trading settings
        os.environ['PAPER_TRADING_ONLY'] = 'true'
        os.environ['ENABLE_AI_TRADING'] = 'true'
        os.environ['ENABLE_QUANTUM_OPTIMIZATION'] = 'true'
        os.environ['VALIDATE_REAL_MARKET_DATA'] = 'true'
        
        print("[CHECK] PROMETHEUS environment configured")
    
    async def initialize_ib_connection(self):
        """Initialize IB connection for PROMETHEUS"""
        try:
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            from ibapi.contract import Contract
            import threading
            import time
            
            class PrometheusIBWrapper(EWrapper):
                def __init__(self, session):
                    self.session = session
                    self.account_data = {}
                    self.market_data = {}
                    self.next_order_id = None
                    
                def error(self, reqId, errorCode, errorString):
                    if errorCode in [2104, 2107, 2158, 2106]:  # Info messages
                        logger.info(f"IB Info {errorCode}: {errorString}")
                    else:
                        logger.warning(f"IB Error {errorCode}: {errorString}")
                
                def nextValidId(self, orderId):
                    self.next_order_id = orderId
                    logger.info(f"Next valid order ID: {orderId}")
                
                def accountSummary(self, reqId, account, tag, value, currency):
                    self.account_data[tag] = value
                
                def tickPrice(self, reqId, tickType, price, attrib):
                    symbol = self.session.req_id_to_symbol.get(reqId)
                    if symbol:
                        if symbol not in self.market_data:
                            self.market_data[symbol] = {}
                        
                        tick_names = {1: 'bid', 2: 'ask', 4: 'last'}
                        if tickType in tick_names:
                            self.market_data[symbol][tick_names[tickType]] = price
                            self.session.market_data_cache[symbol] = self.market_data[symbol]
            
            # Initialize connection
            self.ib_wrapper = PrometheusIBWrapper(self)
            self.ib_client = EClient(self.ib_wrapper)
            self.req_id_to_symbol = {}
            self.req_id_counter = 2000
            
            print("🔌 Connecting PROMETHEUS to Interactive Brokers...")
            self.ib_client.connect("127.0.0.1", 7497, 2)
            
            # Start API thread
            api_thread = threading.Thread(target=self.ib_client.run, daemon=True)
            api_thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.ib_client.isConnected() and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.ib_client.isConnected():
                print("[CHECK] PROMETHEUS connected to IB Gateway!")
                
                # Wait for next order ID
                start_time = time.time()
                while self.ib_wrapper.next_order_id is None and (time.time() - start_time) < 5:
                    await asyncio.sleep(0.1)
                
                return True
            else:
                print("[ERROR] Failed to connect PROMETHEUS to IB")
                return False
                
        except Exception as e:
            logger.error(f"IB connection error: {e}")
            return False
    
    async def get_real_time_price(self, symbol):
        """Get real-time price for symbol"""
        try:
            from ibapi.contract import Contract
            
            # Create contract
            contract = Contract()
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            # Request market data
            req_id = self.req_id_counter
            self.req_id_counter += 1
            self.req_id_to_symbol[req_id] = symbol
            
            self.ib_client.reqMktData(req_id, contract, "", False, False, [])
            
            # Wait for data
            await asyncio.sleep(2)
            
            # Return cached data
            return self.market_data_cache.get(symbol, {})
            
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return {}
    
    async def simulate_prometheus_trading_strategy(self):
        """Simulate PROMETHEUS trading strategies with real market data"""
        print("\n🧠 PROMETHEUS AI TRADING STRATEGIES")
        print("=" * 50)
        
        # Define watchlist
        watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
        
        for symbol in watchlist:
            if self.trades_today >= self.max_daily_trades:
                print(f"[WARNING]️ Daily trade limit reached ({self.max_daily_trades})")
                break
            
            print(f"\n📊 Analyzing {symbol}...")
            
            # Get real-time market data
            market_data = await self.get_real_time_price(symbol)
            
            if not market_data:
                print(f"[ERROR] No market data for {symbol}")
                continue
            
            current_price = market_data.get('last', market_data.get('bid', 0))
            if current_price == 0:
                print(f"[ERROR] Invalid price for {symbol}")
                continue
            
            print(f"💰 {symbol} Current Price: ${current_price:.2f}")
            
            # Simulate PROMETHEUS AI decision
            decision = await self.prometheus_ai_decision(symbol, current_price, market_data)
            
            if decision['action'] != 'HOLD':
                await self.execute_paper_trade(symbol, decision, current_price)
    
    async def prometheus_ai_decision(self, symbol, price, market_data):
        """Simulate PROMETHEUS AI trading decision"""
        # Simple momentum strategy for demo
        bid = market_data.get('bid', price)
        ask = market_data.get('ask', price)
        spread = ask - bid if ask > bid else 0
        
        # Decision logic (simplified)
        if spread < price * 0.001:  # Tight spread
            if price > 100:  # Arbitrary momentum signal
                return {
                    'action': 'BUY',
                    'confidence': 0.75,
                    'reason': 'Momentum signal with tight spread',
                    'quantity': int(self.max_position_size / price)
                }
        
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'reason': 'No clear signal',
            'quantity': 0
        }
    
    async def execute_paper_trade(self, symbol, decision, price):
        """Execute paper trade (simulation)"""
        if decision['quantity'] == 0:
            return
        
        trade_value = decision['quantity'] * price
        
        if trade_value > self.max_position_size:
            print(f"[WARNING]️ Trade size ${trade_value:.2f} exceeds max position ${self.max_position_size:.2f}")
            return
        
        # Simulate trade execution
        trade = {
            'symbol': symbol,
            'action': decision['action'],
            'quantity': decision['quantity'],
            'price': price,
            'value': trade_value,
            'timestamp': datetime.now().isoformat(),
            'reason': decision['reason'],
            'confidence': decision['confidence']
        }
        
        print(f"📈 PAPER TRADE EXECUTED:")
        print(f"   {decision['action']} {decision['quantity']} shares of {symbol}")
        print(f"   Price: ${price:.2f}")
        print(f"   Value: ${trade_value:.2f}")
        print(f"   Reason: {decision['reason']}")
        print(f"   Confidence: {decision['confidence']:.1%}")
        
        # Update tracking
        self.trades_today += 1
        
        # Store position
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(trade)
        
        return trade
    
    async def generate_session_report(self):
        """Generate trading session report"""
        session_duration = datetime.now() - self.session_start
        
        report = {
            'session_id': self.session_id,
            'account_id': self.account_id,
            'session_start': self.session_start.isoformat(),
            'session_duration_minutes': session_duration.total_seconds() / 60,
            'starting_capital': self.starting_capital,
            'trades_executed': self.trades_today,
            'positions': self.positions,
            'market_data_cache': self.market_data_cache,
            'risk_parameters': {
                'max_position_size': self.max_position_size,
                'max_daily_loss': self.max_daily_loss,
                'max_daily_trades': self.max_daily_trades,
                'stop_loss_percent': self.stop_loss_percent
            }
        }
        
        # Save report
        report_file = f"ib_paper_session_report_{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 SESSION REPORT SAVED: {report_file}")
        return report
    
    async def run_trading_session(self, duration_minutes=30):
        """Run complete trading session"""
        print("🚀 PROMETHEUS IB PAPER TRADING SESSION")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Account: {self.account_id}")
        print(f"Capital: ${self.starting_capital:.2f} USD (R 10,000)")
        print(f"Duration: {duration_minutes} minutes")
        print("=" * 60)
        
        # Setup environment
        self.setup_prometheus_environment()
        
        # Connect to IB
        connected = await self.initialize_ib_connection()
        if not connected:
            print("[ERROR] Failed to connect to IB. Session aborted.")
            return
        
        # Run trading strategies
        await self.simulate_prometheus_trading_strategy()
        
        # Generate report
        report = await self.generate_session_report()
        
        print("\n[CHECK] TRADING SESSION COMPLETE")
        print(f"📊 Trades Executed: {self.trades_today}")
        print(f"📈 Symbols Analyzed: {len(self.market_data_cache)}")
        print(f"⏱️ Session Duration: {(datetime.now() - self.session_start).total_seconds() / 60:.1f} minutes")
        
        # Disconnect
        if hasattr(self, 'ib_client') and self.ib_client.isConnected():
            self.ib_client.disconnect()
            print("[CHECK] Disconnected from IB Gateway")

async def main():
    """Main function"""
    session = PrometheusIBTradingSession()
    await session.run_trading_session(duration_minutes=10)  # 10-minute demo session

if __name__ == "__main__":
    asyncio.run(main())
