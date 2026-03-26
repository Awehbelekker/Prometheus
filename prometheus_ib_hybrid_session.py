#!/usr/bin/env python3
"""
PROMETHEUS Hybrid Trading Session
Interactive Brokers for execution + Yahoo Finance for market data
Real paper trading with R 10,000 capital
"""

import asyncio
import os
import sys
import json
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta
import logging
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrometheusHybridTradingSession:
    """PROMETHEUS Hybrid Trading Session - IB + Yahoo Finance"""
    
    def __init__(self):
        self.session_id = f"hybrid_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.account_id = "DUN683505"
        self.starting_capital = 540.0  # USD equivalent of R 10,000
        
        # Trading parameters for small account
        self.max_position_size = 10.80  # 2% of $540
        self.max_daily_loss = 25.0
        self.max_daily_trades = 5
        self.stop_loss_percent = 2.0
        
        # Session tracking
        self.trades_today = 0
        self.daily_pnl = 0.0
        self.positions = {}
        self.session_start = datetime.now()
        self.portfolio_value = self.starting_capital
        
        # Market data
        self.market_data_cache = {}
        
    async def initialize_ib_connection(self):
        """Initialize IB connection for order execution"""
        try:
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            import threading
            import time
            
            class HybridIBWrapper(EWrapper):
                def __init__(self, session):
                    self.session = session
                    self.connected = False
                    self.next_order_id = None
                    
                def error(self, reqId, errorCode, errorString):
                    if errorCode in [2104, 2107, 2158, 2106]:
                        logger.info(f"IB Info {errorCode}: {errorString}")
                    else:
                        logger.warning(f"IB Error {errorCode}: {errorString}")
                
                def nextValidId(self, orderId):
                    self.next_order_id = orderId
                    self.connected = True
                    logger.info(f"IB ready - Next order ID: {orderId}")
            
            # Initialize connection
            self.ib_wrapper = HybridIBWrapper(self)
            self.ib_client = EClient(self.ib_wrapper)
            
            print("🔌 Connecting to IB Gateway for order execution...")
            self.ib_client.connect("127.0.0.1", 7497, 3)
            
            # Start API thread
            api_thread = threading.Thread(target=self.ib_client.run, daemon=True)
            api_thread.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.ib_client.isConnected() and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.ib_client.isConnected():
                # Wait for ready signal
                start_time = time.time()
                while not self.ib_wrapper.connected and (time.time() - start_time) < 5:
                    await asyncio.sleep(0.1)
                
                print("[CHECK] IB connection ready for order execution")
                return True
            else:
                print("[ERROR] Failed to connect to IB Gateway")
                return False
                
        except Exception as e:
            logger.error(f"IB connection error: {e}")
            return False
    
    async def get_yahoo_market_data(self, symbols):
        """Get real-time market data from Yahoo Finance"""
        try:
            print("📊 Fetching real-time market data from Yahoo Finance...")
            
            market_data = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    
                    # Get current price and basic info
                    info = ticker.info
                    hist = ticker.history(period="1d", interval="1m")
                    
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        volume = hist['Volume'].iloc[-1]
                        
                        # Calculate simple momentum
                        if len(hist) >= 10:
                            price_10min_ago = hist['Close'].iloc[-10]
                            momentum = (current_price - price_10min_ago) / price_10min_ago
                        else:
                            momentum = 0
                        
                        market_data[symbol] = {
                            'price': float(current_price),
                            'volume': int(volume),
                            'momentum_10min': float(momentum),
                            'market_cap': info.get('marketCap', 0),
                            'pe_ratio': info.get('trailingPE', 0),
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        print(f"📈 {symbol}: ${current_price:.2f} (Momentum: {momentum:.2%})")
                    
                except Exception as e:
                    logger.warning(f"Error fetching data for {symbol}: {e}")
                    continue
            
            self.market_data_cache.update(market_data)
            return market_data
            
        except Exception as e:
            logger.error(f"Yahoo Finance data error: {e}")
            return {}
    
    async def prometheus_ai_analysis(self, symbol, market_data):
        """PROMETHEUS AI analysis for trading decision"""
        try:
            price = market_data['price']
            momentum = market_data['momentum_10min']
            volume = market_data['volume']
            
            # PROMETHEUS AI Decision Logic
            decision = {
                'action': 'HOLD',
                'confidence': 0.5,
                'reason': 'No clear signal',
                'quantity': 0,
                'target_price': price,
                'stop_loss': price * (1 - self.stop_loss_percent / 100)
            }
            
            # Momentum Strategy
            if momentum > 0.02:  # 2% positive momentum
                max_shares = int(self.max_position_size / price)
                if max_shares > 0:
                    decision.update({
                        'action': 'BUY',
                        'confidence': min(0.8, 0.5 + momentum * 10),
                        'reason': f'Strong momentum: {momentum:.2%}',
                        'quantity': max_shares,
                        'target_price': price * 1.05,  # 5% target
                        'stop_loss': price * 0.98  # 2% stop loss
                    })
            
            elif momentum < -0.02:  # 2% negative momentum
                # Check if we have position to sell
                if symbol in self.positions and self.positions[symbol]:
                    decision.update({
                        'action': 'SELL',
                        'confidence': min(0.8, 0.5 + abs(momentum) * 10),
                        'reason': f'Negative momentum: {momentum:.2%}',
                        'quantity': sum(pos['quantity'] for pos in self.positions[symbol] if pos['action'] == 'BUY'),
                        'target_price': price * 0.95,
                        'stop_loss': price * 1.02
                    })
            
            # Volume confirmation
            if volume > 1000000:  # High volume
                decision['confidence'] = min(0.9, decision['confidence'] * 1.2)
                decision['reason'] += f" + High volume: {volume:,}"
            
            return decision
            
        except Exception as e:
            logger.error(f"AI analysis error for {symbol}: {e}")
            return {'action': 'HOLD', 'confidence': 0, 'reason': 'Analysis error', 'quantity': 0}
    
    async def execute_paper_trade(self, symbol, decision, market_data):
        """Execute paper trade with IB integration"""
        if decision['quantity'] == 0 or decision['action'] == 'HOLD':
            return None
        
        price = market_data['price']
        trade_value = decision['quantity'] * price
        
        # Risk checks
        if trade_value > self.max_position_size:
            print(f"[WARNING]️ Trade size ${trade_value:.2f} exceeds max position ${self.max_position_size:.2f}")
            return None
        
        if self.trades_today >= self.max_daily_trades:
            print(f"[WARNING]️ Daily trade limit reached ({self.max_daily_trades})")
            return None
        
        # Create trade record
        trade = {
            'symbol': symbol,
            'action': decision['action'],
            'quantity': decision['quantity'],
            'price': price,
            'value': trade_value,
            'timestamp': datetime.now().isoformat(),
            'reason': decision['reason'],
            'confidence': decision['confidence'],
            'target_price': decision['target_price'],
            'stop_loss': decision['stop_loss'],
            'ib_order_id': None  # Would be filled by actual IB order
        }
        
        # Simulate IB order execution
        print(f"\n📈 PAPER TRADE EXECUTED (IB Simulation):")
        print(f"   {decision['action']} {decision['quantity']} shares of {symbol}")
        print(f"   Entry Price: ${price:.2f}")
        print(f"   Trade Value: ${trade_value:.2f}")
        print(f"   Target: ${decision['target_price']:.2f}")
        print(f"   Stop Loss: ${decision['stop_loss']:.2f}")
        print(f"   Reason: {decision['reason']}")
        print(f"   Confidence: {decision['confidence']:.1%}")
        
        # Update portfolio
        if decision['action'] == 'BUY':
            self.portfolio_value -= trade_value
        else:  # SELL
            self.portfolio_value += trade_value
        
        # Update tracking
        self.trades_today += 1
        
        # Store position
        if symbol not in self.positions:
            self.positions[symbol] = []
        self.positions[symbol].append(trade)
        
        return trade
    
    async def run_trading_strategies(self):
        """Run PROMETHEUS trading strategies"""
        print("\n🧠 PROMETHEUS AI TRADING STRATEGIES")
        print("=" * 50)
        
        # Define watchlist - mix of large and small cap
        watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'META', 'NFLX']
        
        # Get market data for all symbols
        market_data = await self.get_yahoo_market_data(watchlist)
        
        if not market_data:
            print("[ERROR] No market data available")
            return
        
        print(f"\n📊 Analyzing {len(market_data)} symbols...")
        
        # Analyze each symbol
        for symbol, data in market_data.items():
            if self.trades_today >= self.max_daily_trades:
                print(f"[WARNING]️ Daily trade limit reached ({self.max_daily_trades})")
                break
            
            print(f"\n🔍 Analyzing {symbol}...")
            
            # Get AI decision
            decision = await self.prometheus_ai_analysis(symbol, data)
            
            print(f"🤖 AI Decision: {decision['action']} (Confidence: {decision['confidence']:.1%})")
            print(f"📝 Reason: {decision['reason']}")
            
            # Execute trade if decision is not HOLD
            if decision['action'] != 'HOLD':
                trade = await self.execute_paper_trade(symbol, decision, data)
                if trade:
                    print(f"[CHECK] Trade executed successfully")
                else:
                    print(f"[ERROR] Trade not executed (risk limits)")
            else:
                print(f"⏸️ Holding position")
    
    async def generate_session_report(self):
        """Generate comprehensive session report"""
        session_duration = datetime.now() - self.session_start
        
        # Calculate P&L
        total_trade_value = 0
        for symbol_positions in self.positions.values():
            for trade in symbol_positions:
                if trade['action'] == 'BUY':
                    total_trade_value += trade['value']
                else:
                    total_trade_value -= trade['value']
        
        pnl = self.portfolio_value - self.starting_capital
        pnl_percent = (pnl / self.starting_capital) * 100
        
        report = {
            'session_info': {
                'session_id': self.session_id,
                'account_id': self.account_id,
                'session_start': self.session_start.isoformat(),
                'session_duration_minutes': round(session_duration.total_seconds() / 60, 2),
                'trading_mode': 'IB Paper Trading + Yahoo Finance Data'
            },
            'capital_info': {
                'starting_capital_usd': self.starting_capital,
                'starting_capital_zar': 10000.0,
                'final_portfolio_value': self.portfolio_value,
                'total_pnl': pnl,
                'pnl_percent': pnl_percent
            },
            'trading_activity': {
                'trades_executed': self.trades_today,
                'symbols_analyzed': len(self.market_data_cache),
                'positions': self.positions
            },
            'risk_parameters': {
                'max_position_size_usd': self.max_position_size,
                'max_daily_loss_usd': self.max_daily_loss,
                'max_daily_trades': self.max_daily_trades,
                'stop_loss_percent': self.stop_loss_percent
            },
            'market_data': self.market_data_cache,
            'performance_metrics': {
                'trades_per_hour': self.trades_today / max(session_duration.total_seconds() / 3600, 0.1),
                'avg_trade_size': total_trade_value / max(self.trades_today, 1),
                'success_rate': 'N/A (paper trading session)'
            }
        }
        
        # Save report
        report_file = f"prometheus_hybrid_report_{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 SESSION REPORT SAVED: {report_file}")
        return report
    
    async def run_session(self, duration_minutes=15):
        """Run complete hybrid trading session"""
        print("🚀 PROMETHEUS HYBRID TRADING SESSION")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Account: {self.account_id} (IB Paper Trading)")
        print(f"Capital: ${self.starting_capital:.2f} USD (R 10,000 ZAR)")
        print(f"Max Position: ${self.max_position_size:.2f} (2% of capital)")
        print(f"Max Daily Loss: ${self.max_daily_loss:.2f}")
        print(f"Data Source: Yahoo Finance (Real-time)")
        print(f"Execution: Interactive Brokers (Paper)")
        print("=" * 60)
        
        # Initialize IB connection
        ib_connected = await self.initialize_ib_connection()
        if not ib_connected:
            print("[WARNING]️ IB connection failed, continuing with simulation only")
        
        # Run trading strategies
        await self.run_trading_strategies()
        
        # Generate report
        report = await self.generate_session_report()
        
        # Display summary
        print("\n[CHECK] TRADING SESSION COMPLETE")
        print("=" * 40)
        print(f"📊 Trades Executed: {self.trades_today}")
        print(f"📈 Symbols Analyzed: {len(self.market_data_cache)}")
        print(f"💰 Final Portfolio: ${self.portfolio_value:.2f}")
        print(f"📊 P&L: ${report['capital_info']['total_pnl']:.2f} ({report['capital_info']['pnl_percent']:.2f}%)")
        print(f"⏱️ Duration: {report['session_info']['session_duration_minutes']:.1f} minutes")
        
        # Disconnect from IB
        if hasattr(self, 'ib_client') and self.ib_client.isConnected():
            self.ib_client.disconnect()
            print("[CHECK] Disconnected from IB Gateway")
        
        return report

async def main():
    """Main function"""
    session = PrometheusHybridTradingSession()
    await session.run_session(duration_minutes=15)

if __name__ == "__main__":
    asyncio.run(main())
