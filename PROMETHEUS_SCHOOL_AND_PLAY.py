#!/usr/bin/env python3
"""
PROMETHEUS SCHOOL + PLAY SYSTEM
===============================
SCHOOL: Continuously learn from historical data (background)
PLAY: Trade live with real money (foreground)
EVOLVE: Get smarter every single day

This system runs WITHOUT stopping current trading!
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
import logging
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('school_and_play.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class TradingStrategy:
    """A trading strategy that can be learned and evolved"""
    id: str
    name: str
    strategy_type: str  # momentum, mean_reversion, breakout, ml_based
    parameters: Dict[str, Any]
    performance: Dict[str, float] = field(default_factory=dict)
    win_rate: float = 0.5
    sharpe_ratio: float = 0.0
    total_trades: int = 0
    profit: float = 0.0
    created_at: str = ""
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.performance:
            self.performance = {'wins': 0, 'losses': 0, 'total_profit': 0}


class StrategyDatabase:
    """Database of learned strategies"""
    
    def __init__(self, filepath: str = "learned_strategies.json"):
        self.filepath = filepath
        self.strategies: Dict[str, TradingStrategy] = {}
        self.load()
    
    def load(self):
        """Load strategies from file"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    for sid, sdata in data.items():
                        self.strategies[sid] = TradingStrategy(**sdata)
                logger.info(f"Loaded {len(self.strategies)} strategies from database")
            except Exception as e:
                logger.error(f"Error loading strategies: {e}")
        
        # Initialize with default strategies if empty
        if not self.strategies:
            self._initialize_default_strategies()
    
    def _initialize_default_strategies(self):
        """Create initial strategy pool"""
        defaults = [
            TradingStrategy(
                id="momentum_1",
                name="Momentum Follower",
                strategy_type="momentum",
                parameters={
                    'lookback_period': 20,
                    'momentum_threshold': 0.02,
                    'stop_loss': 0.03,
                    'take_profit': 0.06
                },
                generation=0
            ),
            TradingStrategy(
                id="mean_rev_1",
                name="Mean Reversion",
                strategy_type="mean_reversion",
                parameters={
                    'lookback_period': 14,
                    'std_threshold': 2.0,
                    'stop_loss': 0.02,
                    'take_profit': 0.04
                },
                generation=0
            ),
            TradingStrategy(
                id="breakout_1",
                name="Breakout Trader",
                strategy_type="breakout",
                parameters={
                    'consolidation_days': 10,
                    'volume_multiplier': 1.5,
                    'stop_loss': 0.025,
                    'take_profit': 0.075
                },
                generation=0
            ),
            TradingStrategy(
                id="ml_ensemble_1",
                name="ML Ensemble",
                strategy_type="ml_based",
                parameters={
                    'confidence_threshold': 0.7,
                    'position_sizing': 'kelly',
                    'stop_loss': 0.03,
                    'take_profit': 0.08
                },
                generation=0
            ),
            TradingStrategy(
                id="rsi_macd_1",
                name="RSI-MACD Combo",
                strategy_type="indicator",
                parameters={
                    'rsi_period': 14,
                    'rsi_oversold': 30,
                    'rsi_overbought': 70,
                    'macd_fast': 12,
                    'macd_slow': 26,
                    'stop_loss': 0.025,
                    'take_profit': 0.05
                },
                generation=0
            )
        ]
        
        for strategy in defaults:
            self.strategies[strategy.id] = strategy
        
        self.save()
        logger.info(f"Initialized {len(defaults)} default strategies")
    
    def save(self):
        """Save strategies to file"""
        data = {}
        for sid, strategy in self.strategies.items():
            data[sid] = {
                'id': strategy.id,
                'name': strategy.name,
                'strategy_type': strategy.strategy_type,
                'parameters': strategy.parameters,
                'performance': strategy.performance,
                'win_rate': strategy.win_rate,
                'sharpe_ratio': strategy.sharpe_ratio,
                'total_trades': strategy.total_trades,
                'profit': strategy.profit,
                'created_at': strategy.created_at,
                'generation': strategy.generation,
                'parent_ids': strategy.parent_ids
            }
        
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add(self, strategy: TradingStrategy):
        """Add a new strategy"""
        self.strategies[strategy.id] = strategy
        self.save()
    
    def get_all(self) -> List[TradingStrategy]:
        """Get all strategies"""
        return list(self.strategies.values())
    
    def get_top(self, n: int = 5) -> List[TradingStrategy]:
        """Get top performing strategies"""
        sorted_strategies = sorted(
            self.strategies.values(),
            key=lambda s: (s.sharpe_ratio, s.win_rate),
            reverse=True
        )
        return sorted_strategies[:n]
    
    def get_profitable(self) -> List[TradingStrategy]:
        """Get strategies with positive profit"""
        return [s for s in self.strategies.values() if s.profit > 0 or s.total_trades < 10]
    
    def update_performance(self, strategy_id: str, result: Dict[str, Any]):
        """Update strategy performance after a trade"""
        if strategy_id in self.strategies:
            s = self.strategies[strategy_id]
            s.total_trades += 1
            s.profit += result.get('profit', 0)
            
            if result.get('profit', 0) > 0:
                s.performance['wins'] = s.performance.get('wins', 0) + 1
            else:
                s.performance['losses'] = s.performance.get('losses', 0) + 1
            
            s.performance['total_profit'] = s.profit
            
            # Update win rate
            total = s.performance.get('wins', 0) + s.performance.get('losses', 0)
            if total > 0:
                s.win_rate = s.performance.get('wins', 0) / total
            
            self.save()


class HistoricalBacktester:
    """Backtest strategies on historical data"""
    
    def __init__(self):
        self.data_provider = None
        
    async def initialize(self):
        """Initialize data provider"""
        try:
            from core.polygon_premium_provider import PolygonPremiumProvider
            self.data_provider = PolygonPremiumProvider()
            logger.info("[OK] Historical data provider initialized")
            return True
        except Exception as e:
            logger.warning(f"Could not initialize premium provider: {e}")
            return True  # Continue anyway
    
    async def get_historical_data(self, symbol: str, days: int = 60) -> Optional[Dict]:
        """Get historical price data for backtesting"""
        try:
            # Try yfinance first (most reliable for historical data)
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
                return {'symbol': symbol, 'bars': bars}
            
            # Fallback: generate synthetic data for testing
            return self._generate_synthetic_data(symbol, days)
            
        except Exception as e:
            logger.warning(f"Error getting historical data: {e}")
            return self._generate_synthetic_data(symbol, days)
    
    def _generate_synthetic_data(self, symbol: str, days: int) -> Dict:
        """Generate synthetic price data for backtesting"""
        import random
        
        prices = []
        price = 100.0 + random.random() * 200  # Random starting price
        
        for i in range(days):
            # Random walk with slight upward bias
            change = random.gauss(0.0002, 0.02)  # Mean 0.02%, std 2%
            price *= (1 + change)
            prices.append({
                'date': (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d'),
                'open': price * (1 + random.gauss(0, 0.005)),
                'high': price * (1 + abs(random.gauss(0, 0.01))),
                'low': price * (1 - abs(random.gauss(0, 0.01))),
                'close': price,
                'volume': random.randint(100000, 10000000)
            })
        
        return {'symbol': symbol, 'bars': prices}
    
    async def backtest_strategy(
        self,
        strategy: TradingStrategy,
        symbol: str,
        days: int = 60,
        initial_capital: float = 100000
    ) -> Dict[str, Any]:
        """Backtest a strategy on historical data"""
        
        data = await self.get_historical_data(symbol, days)
        if not data or not data.get('bars'):
            return {'error': 'No data available'}
        
        bars = data['bars']
        capital = initial_capital
        position = 0
        entry_price = 0
        trades = []
        
        # Simple backtest based on strategy type
        for i in range(strategy.parameters.get('lookback_period', 20), len(bars)):
            current_bar = bars[i]
            lookback = bars[i - strategy.parameters.get('lookback_period', 20):i]
            
            # Calculate signals based on strategy type
            signal = self._calculate_signal(strategy, lookback, current_bar)
            
            # Execute trades
            if signal == 'buy' and position == 0:
                position = capital / current_bar['close']
                entry_price = current_bar['close']
                capital = 0
                
            elif signal == 'sell' and position > 0:
                capital = position * current_bar['close']
                profit = (current_bar['close'] - entry_price) / entry_price
                trades.append({
                    'entry': entry_price,
                    'exit': current_bar['close'],
                    'profit_pct': profit
                })
                position = 0
                entry_price = 0
            
            # Check stop loss / take profit
            if position > 0:
                current_profit = (current_bar['close'] - entry_price) / entry_price
                stop_loss = strategy.parameters.get('stop_loss', 0.03)
                take_profit = strategy.parameters.get('take_profit', 0.06)
                
                if current_profit <= -stop_loss or current_profit >= take_profit:
                    capital = position * current_bar['close']
                    trades.append({
                        'entry': entry_price,
                        'exit': current_bar['close'],
                        'profit_pct': current_profit
                    })
                    position = 0
                    entry_price = 0
        
        # Close any open position
        if position > 0:
            capital = position * bars[-1]['close']
            profit = (bars[-1]['close'] - entry_price) / entry_price
            trades.append({
                'entry': entry_price,
                'exit': bars[-1]['close'],
                'profit_pct': profit
            })
        
        # Calculate results
        total_return = (capital - initial_capital) / initial_capital
        win_trades = [t for t in trades if t['profit_pct'] > 0]
        win_rate = len(win_trades) / len(trades) if trades else 0
        
        # Calculate Sharpe ratio (simplified)
        if trades:
            returns = [t['profit_pct'] for t in trades]
            avg_return = sum(returns) / len(returns)
            std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
            sharpe = avg_return / std_return * (252 ** 0.5) if std_return > 0 else 0
        else:
            sharpe = 0
        
        return {
            'symbol': symbol,
            'strategy': strategy.name,
            'total_return': total_return,
            'win_rate': win_rate,
            'sharpe_ratio': sharpe,
            'total_trades': len(trades),
            'trades': trades
        }
    
    def _calculate_signal(
        self,
        strategy: TradingStrategy,
        lookback: List[Dict],
        current: Dict
    ) -> str:
        """Calculate trading signal based on strategy"""
        
        if strategy.strategy_type == 'momentum':
            # Momentum: buy if price is above recent average
            prices = [b['close'] for b in lookback]
            avg = sum(prices) / len(prices)
            momentum = (current['close'] - prices[0]) / prices[0]
            
            if momentum > strategy.parameters.get('momentum_threshold', 0.02):
                return 'buy'
            elif momentum < -strategy.parameters.get('momentum_threshold', 0.02):
                return 'sell'
                
        elif strategy.strategy_type == 'mean_reversion':
            # Mean reversion: buy when oversold, sell when overbought
            prices = [b['close'] for b in lookback]
            avg = sum(prices) / len(prices)
            std = (sum((p - avg) ** 2 for p in prices) / len(prices)) ** 0.5
            
            z_score = (current['close'] - avg) / std if std > 0 else 0
            threshold = strategy.parameters.get('std_threshold', 2.0)
            
            if z_score < -threshold:
                return 'buy'
            elif z_score > threshold:
                return 'sell'
                
        elif strategy.strategy_type == 'breakout':
            # Breakout: buy on volume surge above recent high
            prices = [b['close'] for b in lookback]
            volumes = [b['volume'] for b in lookback]
            
            recent_high = max(prices)
            avg_volume = sum(volumes) / len(volumes)
            
            if current['close'] > recent_high and current['volume'] > avg_volume * strategy.parameters.get('volume_multiplier', 1.5):
                return 'buy'
            elif current['close'] < min(prices):
                return 'sell'
        
        elif strategy.strategy_type == 'indicator':
            # RSI-based strategy
            prices = [b['close'] for b in lookback]
            
            # Simplified RSI calculation
            gains = []
            losses = []
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0.001
            avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0.001
            rs = avg_gain / avg_loss if avg_loss > 0 else 1
            rsi = 100 - (100 / (1 + rs))
            
            if rsi < strategy.parameters.get('rsi_oversold', 30):
                return 'buy'
            elif rsi > strategy.parameters.get('rsi_overbought', 70):
                return 'sell'
        
        return 'hold'


class StrategyEvolver:
    """Evolve strategies using genetic algorithms"""
    
    def __init__(self, strategy_db: StrategyDatabase):
        self.strategy_db = strategy_db
        self.mutation_rate = 0.2
        self.generation = 0
    
    def breed(self, parent1: TradingStrategy, parent2: TradingStrategy) -> TradingStrategy:
        """Create a child strategy from two parents"""
        
        # Combine parameters from both parents
        child_params = {}
        all_keys = set(parent1.parameters.keys()) | set(parent2.parameters.keys())
        
        for key in all_keys:
            p1_val = parent1.parameters.get(key)
            p2_val = parent2.parameters.get(key)
            
            if p1_val is not None and p2_val is not None:
                # Average numeric values
                if isinstance(p1_val, (int, float)) and isinstance(p2_val, (int, float)):
                    child_params[key] = (p1_val + p2_val) / 2
                else:
                    # Random selection for non-numeric
                    child_params[key] = random.choice([p1_val, p2_val])
            else:
                child_params[key] = p1_val if p1_val is not None else p2_val
        
        # Apply mutation
        child_params = self._mutate(child_params)
        
        # Create child strategy
        self.generation += 1
        child = TradingStrategy(
            id=f"evolved_{self.generation}_{int(time.time())}",
            name=f"Evolved Strategy Gen {self.generation}",
            strategy_type=random.choice([parent1.strategy_type, parent2.strategy_type]),
            parameters=child_params,
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_ids=[parent1.id, parent2.id]
        )
        
        return child
    
    def _mutate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply random mutations to parameters"""
        mutated = params.copy()
        
        for key, value in mutated.items():
            if random.random() < self.mutation_rate:
                if isinstance(value, float):
                    # Mutate by +/- 20%
                    mutation = value * random.uniform(-0.2, 0.2)
                    mutated[key] = max(0.001, value + mutation)
                elif isinstance(value, int):
                    # Mutate by +/- 3
                    mutation = random.randint(-3, 3)
                    mutated[key] = max(1, value + mutation)
        
        return mutated
    
    def evolve_population(self, top_n: int = 3, offspring_count: int = 5) -> List[TradingStrategy]:
        """Evolve new strategies from top performers"""
        
        # Get best strategies
        top_strategies = self.strategy_db.get_top(top_n)
        if len(top_strategies) < 2:
            return []
        
        new_strategies = []
        
        for _ in range(offspring_count):
            # Select two random parents from top performers
            parent1, parent2 = random.sample(top_strategies, 2)
            child = self.breed(parent1, parent2)
            new_strategies.append(child)
            self.strategy_db.add(child)
        
        return new_strategies


class SchoolAndPlaySystem:
    """Main system: Learn from history while trading live"""
    
    def __init__(self):
        self.strategy_db = StrategyDatabase()
        self.backtester = HistoricalBacktester()
        self.evolver = StrategyEvolver(self.strategy_db)
        self.test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD', 'NFLX', 'SPY']
        self.learning_stats = {
            'backtests_run': 0,
            'strategies_evolved': 0,
            'best_sharpe': 0,
            'best_strategy': None,
            'session_start': datetime.now().isoformat()
        }
        self.running = False
    
    async def school_loop(self):
        """SCHOOL: Continuous learning from historical data"""
        logger.info("[SCHOOL] Starting continuous learning loop...")
        
        await self.backtester.initialize()
        
        cycle = 0
        while self.running:
            cycle += 1
            logger.info(f"")
            logger.info(f"[SCHOOL] Learning Cycle {cycle}")
            logger.info("-" * 50)
            
            # Pick random symbol and timeframe
            symbol = random.choice(self.test_symbols)
            days = random.choice([30, 60, 90, 120])
            
            # Test all strategies
            for strategy in self.strategy_db.get_all():
                result = await self.backtester.backtest_strategy(
                    strategy,
                    symbol,
                    days
                )
                
                if 'error' not in result:
                    self.learning_stats['backtests_run'] += 1
                    
                    # Update strategy performance
                    strategy.sharpe_ratio = (strategy.sharpe_ratio * 0.9 + result['sharpe_ratio'] * 0.1)
                    strategy.win_rate = (strategy.win_rate * 0.9 + result['win_rate'] * 0.1)
                    
                    # Track best
                    if result['sharpe_ratio'] > self.learning_stats['best_sharpe']:
                        self.learning_stats['best_sharpe'] = result['sharpe_ratio']
                        self.learning_stats['best_strategy'] = strategy.name
                    
                    logger.info(f"  {strategy.name[:20]:20} | {symbol} | Return: {result['total_return']*100:+.1f}% | Sharpe: {result['sharpe_ratio']:.2f}")
            
            self.strategy_db.save()
            
            # Brief pause before next cycle
            await asyncio.sleep(10)  # Learn every 10 seconds
    
    async def evolution_loop(self):
        """EVOLVE: Create new strategies from winners"""
        logger.info("[EVOLVE] Starting evolution loop...")
        
        while self.running:
            # Wait between evolution cycles
            await asyncio.sleep(300)  # Evolve every 5 minutes
            
            logger.info("")
            logger.info("[EVOLVE] Creating new strategies from winners...")
            
            # Evolve new strategies
            new_strategies = self.evolver.evolve_population(top_n=3, offspring_count=3)
            self.learning_stats['strategies_evolved'] += len(new_strategies)
            
            for s in new_strategies:
                logger.info(f"  Created: {s.name} (Gen {s.generation})")
            
            # Prune worst performers (keep top 20)
            all_strategies = self.strategy_db.get_all()
            if len(all_strategies) > 20:
                sorted_strategies = sorted(
                    all_strategies,
                    key=lambda s: (s.sharpe_ratio, s.win_rate),
                    reverse=True
                )
                
                # Remove worst performers
                to_remove = sorted_strategies[20:]
                for s in to_remove:
                    if s.total_trades > 0:  # Only remove tested strategies
                        del self.strategy_db.strategies[s.id]
                
                self.strategy_db.save()
                logger.info(f"  Pruned {len(to_remove)} underperforming strategies")
    
    async def stats_loop(self):
        """Report learning statistics"""
        while self.running:
            await asyncio.sleep(60)  # Report every minute
            
            top_strategies = self.strategy_db.get_top(5)
            
            logger.info("")
            logger.info("=" * 70)
            logger.info("[STATS] LEARNING PROGRESS")
            logger.info("=" * 70)
            logger.info(f"Backtests completed: {self.learning_stats['backtests_run']}")
            logger.info(f"Strategies evolved: {self.learning_stats['strategies_evolved']}")
            logger.info(f"Total strategies: {len(self.strategy_db.get_all())}")
            logger.info(f"Best Sharpe: {self.learning_stats['best_sharpe']:.2f} ({self.learning_stats['best_strategy']})")
            logger.info("")
            logger.info("Top 5 Strategies:")
            for i, s in enumerate(top_strategies, 1):
                logger.info(f"  {i}. {s.name[:25]:25} | Win: {s.win_rate*100:.1f}% | Sharpe: {s.sharpe_ratio:.2f} | Gen: {s.generation}")
            logger.info("=" * 70)
    
    async def run(self):
        """Run School + Play system"""
        logger.info("=" * 70)
        logger.info("PROMETHEUS SCHOOL + PLAY SYSTEM")
        logger.info("=" * 70)
        logger.info("")
        logger.info("[OK] SCHOOL: Learning from historical data (background)")
        logger.info("[OK] EVOLVE: Creating new strategies (background)")
        logger.info("[OK] Live trading continues normally!")
        logger.info("")
        logger.info("=" * 70)
        
        self.running = True
        
        # Run all loops in parallel
        await asyncio.gather(
            self.school_loop(),
            self.evolution_loop(),
            self.stats_loop()
        )


async def main():
    print()
    print("=" * 70)
    print("PROMETHEUS SCHOOL + PLAY SYSTEM")
    print("Learn from history while trading live")
    print("=" * 70)
    print()
    print("[INFO] This runs in BACKGROUND")
    print("[INFO] Live trading continues normally!")
    print("[INFO] PROMETHEUS gets smarter over time!")
    print()
    print("=" * 70)
    print()
    
    system = SchoolAndPlaySystem()
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())
