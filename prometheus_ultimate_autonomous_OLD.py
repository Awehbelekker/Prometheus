#!/usr/bin/env python3
"""
PROMETHEUS ULTIMATE AUTONOMOUS TRADING SYSTEM
==============================================
The complete system that:
1. LEARNS continuously from backtesting
2. ADAPTS strategies based on market conditions
3. EXECUTES autonomous trades using best strategies
4. IMPROVES from every trade result

THIS IS THE ULTIMATE PROMETHEUS - THE LEADING TRADESMAN
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
import logging
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('prometheus_ultimate.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# Import the learning engine components
from PROMETHEUS_ULTIMATE_LEARNING_ENGINE import (
    UltimateLearningEngine,
    EnhancedStrategyDatabase,
    MarketRegimeDetector,
    StrategyEnsemble,
    KellyPositionSizer,
    TradingStrategy,
    MarketRegime
)


class PrometheusUltimateTrader:
    """
    THE ULTIMATE PROMETHEUS TRADING SYSTEM
    
    Combines:
    - Continuous learning from historical data
    - Real-time market regime detection
    - Kelly-optimal position sizing
    - Ensemble strategy voting
    - Autonomous trade execution
    - Performance feedback loop
    """
    
    def __init__(self, 
                 initial_capital: float = 100000,
                 max_position_pct: float = 0.10,
                 min_confidence: float = 0.6):
        
        # Core components
        self.strategy_db = EnhancedStrategyDatabase()
        self.regime_detector = MarketRegimeDetector()
        self.ensemble = StrategyEnsemble(min_consensus=3)
        self.position_sizer = KellyPositionSizer()
        
        # Trading state
        self.capital = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.max_position_pct = max_position_pct
        self.min_confidence = min_confidence
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.total_pnl = 0.0
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0
        
        # Trading universe
        self.universe = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
            'NFLX', 'SPY', 'QQQ', 'DIS', 'PYPL', 'INTC', 'CRM', 'ADBE'
        ]
        
        # Current market state
        self.current_regime = MarketRegime.SIDEWAYS
        self.market_data_cache: Dict[str, Dict] = {}
        
        # Control flags
        self.running = False
        self.learning_engine: Optional[UltimateLearningEngine] = None
        
        logger.info("PROMETHEUS ULTIMATE TRADER initialized")
        logger.info(f"  Capital: ${initial_capital:,.2f}")
        logger.info(f"  Max Position: {max_position_pct*100:.0f}%")
        logger.info(f"  Min Confidence: {min_confidence*100:.0f}%")
    
    async def get_market_data(self, symbol: str, days: int = 60) -> Optional[Dict]:
        """Get current market data for a symbol"""
        cache_key = f"{symbol}_{days}"
        
        # Check cache (refresh every 5 minutes)
        if cache_key in self.market_data_cache:
            cached = self.market_data_cache[cache_key]
            if (datetime.now() - cached['timestamp']).seconds < 300:
                return cached['data']
        
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = ticker.history(start=start_date, end=end_date)
            
            if not df.empty:
                bars = []
                for idx, row in df.iterrows():
                    bars.append({
                        'date': idx.strftime('%Y-%m-%d'),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    })
                
                data = {
                    'symbol': symbol,
                    'bars': bars,
                    'current_price': bars[-1]['close'] if bars else 0
                }
                
                self.market_data_cache[cache_key] = {
                    'data': data,
                    'timestamp': datetime.now()
                }
                
                return data
                
        except Exception as e:
            logger.warning(f"Error getting data for {symbol}: {e}")
        
        return None
    
    def detect_market_regime(self, prices: List[float]) -> MarketRegime:
        """Detect current market regime"""
        analysis = self.regime_detector.detect_regime(prices)
        self.current_regime = analysis.regime
        return analysis.regime
    
    def get_best_strategies_for_regime(self, n: int = 5) -> List[TradingStrategy]:
        """Get top strategies suitable for current regime"""
        return self.strategy_db.get_top(n, self.current_regime)
    
    def generate_signal(self, symbol: str, data: Dict) -> Optional[Dict]:
        """
        Generate trading signal using ensemble of strategies
        
        This is where LEARNING meets TRADING:
        - Uses strategies that have PROVEN performance from backtesting
        - Combines multiple strategies for higher confidence
        - Adapts to current market regime
        """
        
        if not data or not data.get('bars'):
            return None
        
        bars = data['bars']
        if len(bars) < 50:
            return None
        
        prices = [b['close'] for b in bars]
        current_price = prices[-1]
        
        # Detect regime
        regime = self.detect_market_regime(prices)
        
        # Get best strategies for this regime
        strategies = self.get_best_strategies_for_regime(5)
        
        if not strategies:
            return None
        
        # Generate signals from each strategy
        signals = {}
        for strategy in strategies:
            signal = self._calculate_strategy_signal(strategy, bars)
            signals[strategy.id] = signal
        
        # Ensemble voting
        final_signal, confidence = self.ensemble.get_ensemble_signal(
            strategies, signals, regime
        )
        
        # Only trade if confidence exceeds threshold
        if confidence < self.min_confidence:
            return None
        
        if final_signal == 'hold':
            return None
        
        # Calculate position size using Kelly
        best_strategy = strategies[0]
        position_size = self.position_sizer.calculate_position_size(
            best_strategy,
            self.capital,
            self.max_position_pct
        )
        
        return {
            'symbol': symbol,
            'signal': final_signal,  # 'buy' or 'sell'
            'confidence': confidence,
            'position_size': position_size,
            'current_price': current_price,
            'regime': regime.value,
            'strategies_used': [s.name for s in strategies],
            'best_strategy': best_strategy.name,
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_strategy_signal(self, strategy: TradingStrategy, bars: List[Dict]) -> str:
        """Calculate signal for a single strategy"""
        
        prices = [b['close'] for b in bars]
        lookback = min(strategy.parameters.get('lookback_period', 20), len(prices) - 1)
        lookback_prices = prices[-lookback:]
        current = bars[-1]
        
        if strategy.strategy_type == 'momentum':
            momentum = (current['close'] - prices[-lookback]) / prices[-lookback]
            threshold = strategy.parameters.get('momentum_threshold', 0.02)
            if momentum > threshold:
                return 'buy'
            elif momentum < -threshold:
                return 'sell'
                
        elif strategy.strategy_type == 'mean_reversion':
            avg = sum(lookback_prices) / len(lookback_prices)
            std = (sum((p - avg) ** 2 for p in lookback_prices) / len(lookback_prices)) ** 0.5
            z_score = (current['close'] - avg) / std if std > 0 else 0
            threshold = strategy.parameters.get('std_threshold', 2.0)
            if z_score < -threshold:
                return 'buy'
            elif z_score > threshold:
                return 'sell'
                
        elif strategy.strategy_type == 'trend_following':
            fast_ma = strategy.parameters.get('fast_ma', 10)
            slow_ma = strategy.parameters.get('slow_ma', 30)
            if len(prices) >= slow_ma:
                fast_avg = sum(prices[-fast_ma:]) / fast_ma
                slow_avg = sum(prices[-slow_ma:]) / slow_ma
                if fast_avg > slow_avg * 1.01:
                    return 'buy'
                elif fast_avg < slow_avg * 0.99:
                    return 'sell'
        
        elif strategy.strategy_type == 'indicator':
            # RSI
            gains, losses = [], []
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                gains.append(max(0, change))
                losses.append(max(0, -change))
            
            period = strategy.parameters.get('rsi_period', 14)
            avg_gain = sum(gains[-period:]) / period if len(gains) >= period else 0.001
            avg_loss = sum(losses[-period:]) / period if len(losses) >= period else 0.001
            rs = avg_gain / avg_loss if avg_loss > 0 else 1
            rsi = 100 - (100 / (1 + rs))
            
            if rsi < strategy.parameters.get('rsi_oversold', 30):
                return 'buy'
            elif rsi > strategy.parameters.get('rsi_overbought', 70):
                return 'sell'
        
        return 'hold'
    
    async def execute_trade(self, signal: Dict) -> bool:
        """
        Execute a trade based on signal
        
        In production, this would:
        1. Connect to broker (Alpaca, IB, etc.)
        2. Submit the order
        3. Track the position
        
        For now, we simulate execution
        """
        
        symbol = signal['symbol']
        action = signal['signal']
        price = signal['current_price']
        position_size = signal['position_size']
        
        if action == 'buy':
            shares = int(position_size / price)
            if shares > 0 and position_size <= self.capital:
                cost = shares * price
                self.capital -= cost
                self.positions[symbol] = {
                    'shares': shares,
                    'entry_price': price,
                    'entry_time': datetime.now().isoformat(),
                    'strategy': signal['best_strategy']
                }
                
                logger.info(f"BUY {shares} {symbol} @ ${price:.2f} = ${cost:,.2f}")
                logger.info(f"  Confidence: {signal['confidence']:.1%} | Strategy: {signal['best_strategy']}")
                return True
                
        elif action == 'sell' and symbol in self.positions:
            pos = self.positions[symbol]
            shares = pos['shares']
            proceeds = shares * price
            pnl = proceeds - (shares * pos['entry_price'])
            pnl_pct = pnl / (shares * pos['entry_price'])
            
            self.capital += proceeds
            self.total_trades += 1
            self.total_pnl += pnl
            
            if pnl > 0:
                self.winning_trades += 1
            
            # Record trade for learning
            trade_record = {
                'symbol': symbol,
                'entry_price': pos['entry_price'],
                'exit_price': price,
                'shares': shares,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'strategy': pos['strategy'],
                'exit_time': datetime.now().isoformat()
            }
            self.trade_history.append(trade_record)
            
            # Update strategy performance from REAL trade
            self._update_strategy_from_trade(trade_record)
            
            del self.positions[symbol]
            
            logger.info(f"SELL {shares} {symbol} @ ${price:.2f} = ${proceeds:,.2f}")
            logger.info(f"  PnL: ${pnl:,.2f} ({pnl_pct:+.1%}) | Strategy: {pos['strategy']}")
            return True
        
        return False
    
    def _update_strategy_from_trade(self, trade: Dict):
        """
        Update strategy performance from REAL trade results
        
        THIS IS THE FEEDBACK LOOP:
        - Real trades update the strategy database
        - Better strategies get higher Kelly allocations
        - Poor strategies get pruned
        """
        
        strategy_name = trade['strategy']
        
        # Find the strategy
        for sid, strategy in self.strategy_db.strategies.items():
            if strategy.name == strategy_name:
                # Update with real trade result
                if trade['pnl'] > 0:
                    strategy.performance['wins'] = strategy.performance.get('wins', 0) + 1
                else:
                    strategy.performance['losses'] = strategy.performance.get('losses', 0) + 1
                
                strategy.total_trades += 1
                strategy.profit += trade['pnl']
                
                # Recalculate win rate
                total = strategy.performance['wins'] + strategy.performance['losses']
                if total > 0:
                    strategy.win_rate = strategy.performance['wins'] / total
                
                # Update avg win/loss
                if trade['pnl'] > 0:
                    strategy.avg_win = (strategy.avg_win * 0.9 + trade['pnl_pct'] * 0.1)
                else:
                    strategy.avg_loss = (strategy.avg_loss * 0.9 + trade['pnl_pct'] * 0.1)
                
                # Save immediately
                self.strategy_db.save()
                
                logger.info(f"  Updated {strategy.name}: Win={strategy.win_rate:.1%}, Trades={strategy.total_trades}")
                break
    
    def update_drawdown(self):
        """Track maximum drawdown"""
        total_value = self.capital + sum(
            pos['shares'] * pos['entry_price'] for pos in self.positions.values()
        )
        self.peak_capital = max(self.peak_capital, total_value)
        drawdown = (self.peak_capital - total_value) / self.peak_capital
        self.max_drawdown = max(self.max_drawdown, drawdown)
    
    async def trading_loop(self):
        """Main autonomous trading loop"""
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("STARTING AUTONOMOUS TRADING")
        logger.info("=" * 70)
        
        cycle = 0
        
        while self.running:
            cycle += 1
            
            logger.info("")
            logger.info(f"[TRADING] Cycle {cycle} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("-" * 60)
            
            # Analyze each symbol in universe
            signals = []
            
            for symbol in self.universe:
                data = await self.get_market_data(symbol)
                if data:
                    signal = self.generate_signal(symbol, data)
                    if signal:
                        signals.append(signal)
            
            logger.info(f"Generated {len(signals)} trading signals")
            
            # Execute top signals (limit concurrent trades)
            sorted_signals = sorted(signals, key=lambda s: s['confidence'], reverse=True)
            
            for signal in sorted_signals[:3]:  # Max 3 trades per cycle
                if signal['signal'] == 'buy' and signal['symbol'] not in self.positions:
                    await self.execute_trade(signal)
                elif signal['signal'] == 'sell' and signal['symbol'] in self.positions:
                    await self.execute_trade(signal)
            
            # Check stop-loss on existing positions
            await self.check_positions()
            
            # Update tracking
            self.update_drawdown()
            
            # Log status
            win_rate = self.winning_trades / self.total_trades if self.total_trades > 0 else 0
            logger.info("")
            logger.info(f"Portfolio: ${self.capital:,.2f} | Positions: {len(self.positions)}")
            logger.info(f"Trades: {self.total_trades} | Win Rate: {win_rate:.1%} | PnL: ${self.total_pnl:,.2f}")
            logger.info(f"Max Drawdown: {self.max_drawdown:.1%}")
            
            # Wait before next cycle (5 minutes during market hours)
            await asyncio.sleep(300)
    
    async def check_positions(self):
        """Check existing positions for stop-loss/take-profit"""
        
        for symbol, pos in list(self.positions.items()):
            data = await self.get_market_data(symbol)
            if not data:
                continue
            
            current_price = data['current_price']
            entry_price = pos['entry_price']
            pnl_pct = (current_price - entry_price) / entry_price
            
            # Stop loss at -5%
            if pnl_pct < -0.05:
                signal = {
                    'symbol': symbol,
                    'signal': 'sell',
                    'current_price': current_price,
                    'confidence': 1.0,
                    'best_strategy': pos['strategy']
                }
                logger.info(f"STOP LOSS triggered for {symbol}")
                await self.execute_trade(signal)
            
            # Take profit at +10%
            elif pnl_pct > 0.10:
                signal = {
                    'symbol': symbol,
                    'signal': 'sell',
                    'current_price': current_price,
                    'confidence': 1.0,
                    'best_strategy': pos['strategy']
                }
                logger.info(f"TAKE PROFIT triggered for {symbol}")
                await self.execute_trade(signal)
    
    async def run(self):
        """Run the complete Prometheus system"""
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("PROMETHEUS ULTIMATE - THE LEADING TRADESMAN")
        logger.info("=" * 70)
        logger.info("")
        logger.info("CAPABILITIES:")
        logger.info("  [OK] Continuous Learning from Backtests")
        logger.info("  [OK] Market Regime Adaptation")
        logger.info("  [OK] Kelly Optimal Position Sizing")
        logger.info("  [OK] Ensemble Strategy Voting")
        logger.info("  [OK] Autonomous Trade Execution")
        logger.info("  [OK] Real-Time Performance Feedback")
        logger.info("")
        logger.info("Starting all systems...")
        logger.info("=" * 70)
        
        self.running = True
        
        # Start learning engine in background
        self.learning_engine = UltimateLearningEngine()
        self.learning_engine.running = True
        
        # Run both learning and trading concurrently
        await asyncio.gather(
            self.learning_engine.learning_loop(),
            self.learning_engine.evolution_loop(),
            self.trading_loop()
        )


async def main():
    """Main entry point"""
    
    print()
    print("=" * 70)
    print("PROMETHEUS ULTIMATE AUTONOMOUS TRADING SYSTEM")
    print("The Leading Tradesman - Learns, Adapts, Executes")
    print("=" * 70)
    print()
    
    trader = PrometheusUltimateTrader(
        initial_capital=100000,
        max_position_pct=0.10,
        min_confidence=0.6
    )
    
    await trader.run()


if __name__ == "__main__":
    asyncio.run(main())
