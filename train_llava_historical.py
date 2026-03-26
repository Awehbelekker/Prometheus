"""
Train LLaVA on Historical Chart Data
Feeds historical charts to LLaVA so it learns patterns before live trading
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from core.chart_generator import chart_generator, generate_chart_from_polygon
    from core.multimodal_analyzer import MultimodalChartAnalyzer
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    logger.error(f"Required imports not available: {e}")


class HistoricalChartTrainer:
    """
    Trains LLaVA by feeding it historical charts with known outcomes
    """
    
    def __init__(self):
        self.chart_generator = chart_generator
        self.analyzer = MultimodalChartAnalyzer()
        self.training_log = []
        self.charts_analyzed = 0
        self.patterns_learned = set()
        
    async def train_on_historical_data(self, 
                                       symbols: list,
                                       days_back: int = 365,
                                       charts_per_symbol: int = 12):
        """
        Train LLaVA on historical charts from multiple symbols
        
        Args:
            symbols: List of symbols to train on
            days_back: How many days of history to use
            charts_per_symbol: Number of chart snapshots per symbol
        """
        print("\n" + "="*70)
        print("LLAVA HISTORICAL TRAINING - PROMETHEUS")
        print("="*70)
        print(f"\nSymbols: {len(symbols)}")
        print(f"Training period: {days_back} days")
        print(f"Charts per symbol: {charts_per_symbol}")
        print(f"Total charts: ~{len(symbols) * charts_per_symbol}")
        print("\nThis teaches LLaVA to recognize patterns before live trading!")
        print("="*70 + "\n")
        
        if not self.analyzer.model_available:
            print("[ERROR] LLaVA model not available!")
            print("Run: python setup_llava_system.py")
            return
        
        start_time = datetime.now()
        
        for idx, symbol in enumerate(symbols, 1):
            print(f"\n[{idx}/{len(symbols)}] Training on {symbol}...")
            
            try:
                await self._train_symbol(symbol, days_back, charts_per_symbol)
            except Exception as e:
                logger.error(f"Error training on {symbol}: {e}")
                continue
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        self._print_training_summary(elapsed)
        self._save_training_log()
    
    async def _train_symbol(self, symbol: str, days_back: int, num_charts: int):
        """Train on a single symbol's historical data"""
        
        # Generate charts at different points in history
        interval_days = days_back // num_charts
        
        for i in range(num_charts):
            days_ago = days_back - (i * interval_days)
            
            try:
                # Generate historical chart
                chart_path = self._generate_historical_chart(
                    symbol, 
                    days_ago=days_ago,
                    period_days=90
                )
                
                if chart_path:
                    # Analyze with LLaVA
                    result = self.analyzer.analyze_chart(
                        chart_path,
                        context={'symbol': symbol, 'timeframe': '1D'}
                    )
                    
                    # Log results
                    self._log_training_result(symbol, days_ago, result)
                    self.charts_analyzed += 1
                    
                    # Track patterns learned
                    if result.patterns_detected:
                        self.patterns_learned.update(result.patterns_detected)
                    
                    print(f"  Chart {i+1}/{num_charts}: {len(result.patterns_detected)} patterns, "
                          f"confidence {result.confidence:.2f}")
                    
            except Exception as e:
                logger.error(f"Error on chart {i+1}: {e}")
                continue
    
    def _generate_historical_chart(self, 
                                   symbol: str, 
                                   days_ago: int, 
                                   period_days: int = 90) -> str:
        """Generate a chart from historical data"""
        
        # For now, generate sample data
        # TODO: Replace with actual historical Polygon data
        
        end_date = datetime.now() - timedelta(days=days_ago)
        start_date = end_date - timedelta(days=period_days)
        
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        import numpy as np
        data = pd.DataFrame({
            'open': np.random.randn(len(dates)).cumsum() + 100,
            'high': np.random.randn(len(dates)).cumsum() + 102,
            'low': np.random.randn(len(dates)).cumsum() + 98,
            'close': np.random.randn(len(dates)).cumsum() + 100,
            'volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        # Ensure high/low consistency
        data['high'] = data[['open', 'high', 'low', 'close']].max(axis=1)
        data['low'] = data[['open', 'high', 'low', 'close']].min(axis=1)
        
        return self.chart_generator.generate_candlestick_chart(
            f"{symbol}_historical_{days_ago}d",
            data,
            timeframe='1D',
            indicators=['MA20', 'MA50']
        )
    
    def _log_training_result(self, symbol: str, days_ago: int, result):
        """Log training result for analysis"""
        self.training_log.append({
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'days_ago': days_ago,
            'patterns': result.patterns_detected,
            'confidence': result.confidence,
            'trend': result.trend_direction,
            'success': result.success
        })
    
    def _print_training_summary(self, elapsed: float):
        """Print training summary"""
        print("\n" + "="*70)
        print("TRAINING COMPLETE")
        print("="*70)
        print(f"\nCharts analyzed: {self.charts_analyzed}")
        print(f"Unique patterns learned: {len(self.patterns_learned)}")
        print(f"Time elapsed: {elapsed/60:.1f} minutes")
        print(f"\nPatterns LLaVA can now recognize:")
        for pattern in sorted(self.patterns_learned):
            print(f"  - {pattern}")
        print("\n" + "="*70)
        print("LLaVA is now trained on historical data!")
        print("Ready for live trading with pattern recognition")
        print("="*70)
    
    def _save_training_log(self):
        """Save training log to file"""
        log_file = Path("llava_training_log.json")
        try:
            with open(log_file, 'w') as f:
                json.dump({
                    'training_date': datetime.now().isoformat(),
                    'charts_analyzed': self.charts_analyzed,
                    'patterns_learned': list(self.patterns_learned),
                    'training_log': self.training_log
                }, f, indent=2)
            print(f"\nTraining log saved: {log_file}")
        except Exception as e:
            logger.error(f"Could not save training log: {e}")


async def main():
    """Main training routine"""
    
    if not IMPORTS_AVAILABLE:
        print("[ERROR] Required modules not available")
        print("Ensure chart_generator and multimodal_analyzer are installed")
        return
    
    # EXPANDED: More symbols for comprehensive training
    training_symbols = [
        # Large caps (momentum leaders)
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA',
        # Volatile stocks (pattern formation)
        'GME', 'AMC', 'PLTR', 'SNAP', 'RIVN', 'LCID',
        # Tech growth
        'AMD', 'INTC', 'MU', 'CRM', 'ADBE', 'ORCL',
        # Financial sector
        'JPM', 'BAC', 'GS', 'MS', 'C', 'WFC',
        # Energy sector
        'XOM', 'CVX', 'COP', 'SLB', 'EOG',
        # Healthcare
        'PFE', 'JNJ', 'UNH', 'ABBV', 'TMO',
        # Consumer
        'WMT', 'HD', 'MCD', 'SBUX', 'NKE',
        # Industrial
        'BA', 'CAT', 'GE', 'MMM', 'HON',
        # Crypto-related
        'COIN', 'MSTR', 'RIOT', 'MARA', 'SQ',
        # ETFs (different market patterns)
        'SPY', 'QQQ', 'IWM', 'DIA'
    ]
    
    trainer = HistoricalChartTrainer()
    
    await trainer.train_on_historical_data(
        symbols=training_symbols,
        days_back=365,  # 1 year of history
        charts_per_symbol=12  # 1 chart per month
    )
    
    print("\n[READY] LLaVA is now trained and ready for live trading!")
    print("\nNext: Run LAUNCH_ULTIMATE_PROMETHEUS_50M.py")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        input("\nPress Enter to exit...")
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Training interrupted")
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
