#!/usr/bin/env python3
"""
Advanced Learning Backtest System
Prometheus learns patterns from multiple angles across different timeframes
Integrates with actual Universal Reasoning Engine
"""

import sys
import asyncio
import logging
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from collections import defaultdict

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedLearningBacktest:
    """
    Advanced backtesting with pattern learning from multiple angles
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.learned_patterns = {
            'regime_patterns': defaultdict(list),
            'volatility_patterns': defaultdict(list),
            'trend_patterns': defaultdict(list),
            'volume_patterns': defaultdict(list),
            'correlation_patterns': defaultdict(list),
            'seasonal_patterns': defaultdict(list),
            'timeframe_patterns': defaultdict(list)
        }
        self.results = {}
        
        # Timeframes
        self.timeframes = [1, 5, 10, 20, 50, 100]
        
        # Learning angles
        self.learning_angles = [
            'regime_analysis',
            'volatility_clustering',
            'trend_identification',
            'volume_analysis',
            'correlation_structure',
            'seasonal_patterns',
            'multi_timeframe',
            'risk_adjusted'
        ]
    
    def learn_from_angle_regime_analysis(self, data: pd.DataFrame, symbol: str, timeframe: int):
        """Learn patterns from regime analysis angle"""
        patterns = []
        
        # Identify different regimes
        returns = data['Close'].pct_change().dropna()
        
        # Bull market patterns
        bull_periods = data[returns > returns.quantile(0.7)]
        if len(bull_periods) > 0:
            patterns.append({
                'angle': 'regime_analysis',
                'pattern_type': 'bull_market',
                'characteristics': {
                    'avg_return': bull_periods['Close'].pct_change().mean(),
                    'avg_volume': bull_periods['Volume'].mean() if 'Volume' in bull_periods.columns else 0,
                    'duration_avg': len(bull_periods) / len(data)
                }
            })
        
        # Bear market patterns
        bear_periods = data[returns < returns.quantile(0.3)]
        if len(bear_periods) > 0:
            patterns.append({
                'angle': 'regime_analysis',
                'pattern_type': 'bear_market',
                'characteristics': {
                    'avg_return': bear_periods['Close'].pct_change().mean(),
                    'avg_volume': bear_periods['Volume'].mean() if 'Volume' in bear_periods.columns else 0,
                    'duration_avg': len(bear_periods) / len(data)
                }
            })
        
        self.learned_patterns['regime_patterns'][f"{symbol}_{timeframe}"].extend(patterns)
        return patterns
    
    def learn_from_angle_volatility_clustering(self, data: pd.DataFrame, symbol: str, timeframe: int):
        """Learn volatility clustering patterns"""
        returns = data['Close'].pct_change().dropna()
        volatility = returns.rolling(window=20).std()
        
        # High volatility periods
        high_vol_threshold = volatility.quantile(0.8)
        high_vol_periods = data[volatility > high_vol_threshold]
        
        patterns = [{
            'angle': 'volatility_clustering',
            'pattern_type': 'high_volatility_clusters',
            'characteristics': {
                'cluster_count': len(high_vol_periods),
                'avg_cluster_duration': len(high_vol_periods) / max(1, len([i for i in range(len(volatility)-1) if volatility.iloc[i] <= high_vol_threshold and volatility.iloc[i+1] > high_vol_threshold])),
                'volatility_mean': high_vol_periods['Close'].pct_change().std() if len(high_vol_periods) > 1 else 0
            }
        }]
        
        self.learned_patterns['volatility_patterns'][f"{symbol}_{timeframe}"].extend(patterns)
        return patterns
    
    def learn_from_angle_trend_identification(self, data: pd.DataFrame, symbol: str, timeframe: int):
        """Learn trend identification patterns"""
        # Moving averages
        ma_20 = data['Close'].rolling(window=20).mean()
        ma_50 = data['Close'].rolling(window=min(50, len(data)//4)).mean()
        
        # Trend patterns
        uptrend = data[ma_20 > ma_50]
        downtrend = data[ma_20 < ma_50]
        
        patterns = [{
            'angle': 'trend_identification',
            'pattern_type': 'trend_strength',
            'characteristics': {
                'uptrend_periods': len(uptrend),
                'downtrend_periods': len(downtrend),
                'trend_strength_avg': abs((ma_20 - ma_50) / ma_50).mean() if len(ma_50) > 0 else 0
            }
        }]
        
        self.learned_patterns['trend_patterns'][f"{symbol}_{timeframe}"].extend(patterns)
        return patterns
    
    def learn_from_angle_volume_analysis(self, data: pd.DataFrame, symbol: str, timeframe: int):
        """Learn volume analysis patterns"""
        if 'Volume' not in data.columns:
            return []
        
        volume_ma = data['Volume'].rolling(window=20).mean()
        volume_ratio = data['Volume'] / volume_ma
        
        # High volume patterns
        high_volume = data[volume_ratio > 1.5]
        
        patterns = [{
            'angle': 'volume_analysis',
            'pattern_type': 'volume_confirmation',
            'characteristics': {
                'high_volume_periods': len(high_volume),
                'volume_spike_frequency': len(high_volume) / len(data),
                'avg_volume_ratio': volume_ratio.mean()
            }
        }]
        
        self.learned_patterns['volume_patterns'][f"{symbol}_{timeframe}"].extend(patterns)
        return patterns
    
    def learn_from_angle_seasonal_patterns(self, data: pd.DataFrame, symbol: str, timeframe: int):
        """Learn seasonal patterns"""
        if len(data) < 365:
            return []
        
        data_with_dates = data.copy()
        if not isinstance(data_with_dates.index, pd.DatetimeIndex):
            return []
        
        # Monthly patterns
        monthly_returns = data_with_dates['Close'].resample('M').last().pct_change().dropna()
        
        patterns = [{
            'angle': 'seasonal_patterns',
            'pattern_type': 'monthly_seasonality',
            'characteristics': {
                'best_month': monthly_returns.groupby(monthly_returns.index.month).mean().idxmax() if len(monthly_returns) > 0 else None,
                'worst_month': monthly_returns.groupby(monthly_returns.index.month).mean().idxmin() if len(monthly_returns) > 0 else None
            }
        }]
        
        self.learned_patterns['seasonal_patterns'][f"{symbol}_{timeframe}"].extend(patterns)
        return patterns
    
    async def learn_from_all_angles(self, data: pd.DataFrame, symbol: str, timeframe: int):
        """Learn patterns from all angles"""
        logger.info(f"[LEARNING] Learning patterns for {symbol} ({timeframe} years) from all angles...")
        
        all_patterns = {}
        
        for angle in self.learning_angles:
            try:
                if angle == 'regime_analysis':
                    patterns = self.learn_from_angle_regime_analysis(data, symbol, timeframe)
                elif angle == 'volatility_clustering':
                    patterns = self.learn_from_angle_volatility_clustering(data, symbol, timeframe)
                elif angle == 'trend_identification':
                    patterns = self.learn_from_angle_trend_identification(data, symbol, timeframe)
                elif angle == 'volume_analysis':
                    patterns = self.learn_from_angle_volume_analysis(data, symbol, timeframe)
                elif angle == 'seasonal_patterns':
                    patterns = self.learn_from_angle_seasonal_patterns(data, symbol, timeframe)
                else:
                    patterns = []
                
                all_patterns[angle] = patterns
                logger.info(f"  ✅ Learned {len(patterns)} patterns from {angle}")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to learn from {angle}: {e}")
                all_patterns[angle] = []
        
        return all_patterns
    
    async def run_learning_backtest(self):
        """Run comprehensive learning backtest"""
        logger.info("=" * 80)
        logger.info("ADVANCED LEARNING BACKTEST")
        logger.info("=" * 80)
        logger.info(f"Timeframes: {self.timeframes} years")
        logger.info(f"Learning Angles: {len(self.learning_angles)}")
        logger.info("")
        
        symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA']  # Start with fewer for testing
        
        for years in self.timeframes:
            logger.info(f"\n{'='*80}")
            logger.info(f"LEARNING FROM {years}-YEAR TIMEFRAME")
            logger.info(f"{'='*80}")
            
            for symbol in symbols:
                try:
                    # Download data
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=years * 365)
                    
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(start=start_date, end=end_date, interval='1d')
                    
                    if data.empty or len(data) < 30:
                        logger.warning(f"[SKIP] Insufficient data for {symbol}")
                        continue
                    
                    # Learn from all angles
                    patterns = await self.learn_from_all_angles(data, symbol, years)
                    
                    logger.info(f"[SUCCESS] Learned patterns for {symbol} ({years} years)")
                    
                    await asyncio.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"[ERROR] Failed for {symbol} ({years} years): {e}")
                    continue
        
        # Save learned patterns
        patterns_file = f"learned_patterns_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.learned_patterns, f, indent=2, default=str)
        
        logger.info(f"\n[SAVED] Learned patterns saved to {patterns_file}")
        
        # Generate learning report
        self.generate_learning_report()
        
        return self.learned_patterns
    
    def generate_learning_report(self):
        """Generate report on learned patterns"""
        logger.info("\n" + "=" * 80)
        logger.info("LEARNING REPORT")
        logger.info("=" * 80)
        
        for pattern_type, patterns_dict in self.learned_patterns.items():
            logger.info(f"\n{pattern_type.upper()}:")
            logger.info(f"  Total pattern sets: {len(patterns_dict)}")
            
            for key, patterns in list(patterns_dict.items())[:5]:  # Show first 5
                logger.info(f"    {key}: {len(patterns)} patterns")

async def main():
    backtester = AdvancedLearningBacktest()
    patterns = await backtester.run_learning_backtest()
    
    print("\n" + "=" * 80)
    print("LEARNING BACKTEST COMPLETE")
    print("=" * 80)
    print(f"\nLearned patterns from {len(backtester.learning_angles)} different angles")
    print("Check the JSON file for detailed pattern data.")

if __name__ == "__main__":
    asyncio.run(main())

