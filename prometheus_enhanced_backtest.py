#!/usr/bin/env python3
"""
PROMETHEUS ENHANCED HISTORICAL BACKTESTING SYSTEM
Enhanced backtesting with improved trading logic and performance optimization
"""

import asyncio
import logging
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrometheusEnhancedBacktester:
    """
    Enhanced backtesting system with improved trading logic
    """
    
    def __init__(self, start_date: str = "2022-01-01", end_date: str = "2024-12-31"):
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = 100000  # $100k starting capital
        self.current_capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.portfolio_values = []
        self.daily_returns = []
        
        # Enhanced trading parameters
        self.max_position_size = 0.15  # 15% max position
        self.stop_loss_pct = 0.05      # 5% stop loss
        self.take_profit_pct = 0.10    # 10% take profit
        self.min_confidence = 0.65     # 65% minimum confidence
        self.max_positions = 3         # Max 3 concurrent positions
        
        # Symbols to test (focused on liquid assets)
        self.symbols = [
            'SPY', 'QQQ', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'
        ]
        
        # Enhanced metrics tracking
        self.metrics = {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'average_win_loss_ratio': 0.0,
            'calmar_ratio': 0.0,
            'sortino_ratio': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'gross_profit': 0.0,
            'gross_loss': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0,
            'volatility': 0.0,
            'beta': 0.0,
            'alpha': 0.0
        }
        
        logger.info(f"[INIT] Enhanced PROMETHEUS Backtester initialized")
        logger.info(f"[PERIOD] {start_date} to {end_date}")
        logger.info(f"[CAPITAL] Initial Capital: ${self.initial_capital:,}")
        logger.info(f"[SYMBOLS] {len(self.symbols)} symbols")

    async def download_historical_data(self) -> Dict[str, pd.DataFrame]:
        """Download historical data for all symbols"""
        logger.info("[DOWNLOAD] Downloading historical data...")
        
        data = {}
        for symbol in self.symbols:
            try:
                logger.info(f"  [SYMBOL] Downloading {symbol}...")
                ticker = yf.Ticker(symbol)
                df = ticker.history(start=self.start_date, end=self.end_date)
                
                if not df.empty:
                    # Add enhanced technical indicators
                    df = self._add_enhanced_indicators(df)
                    data[symbol] = df
                    logger.info(f"  [SUCCESS] {symbol}: {len(df)} days of data")
                else:
                    logger.warning(f"  [WARNING] No data for {symbol}")
                    
            except Exception as e:
                logger.error(f"  [ERROR] Error downloading {symbol}: {e}")
        
        logger.info(f"[DATA] Downloaded data for {len(data)} symbols")
        return data

    def _add_enhanced_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add enhanced technical indicators"""
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
        
        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()
        df['EMA_12'] = df['Close'].ewm(span=12).mean()
        df['EMA_26'] = df['Close'].ewm(span=26).mean()
        
        # Volume indicators
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # Price momentum
        df['Price_Change_1d'] = df['Close'].pct_change(1)
        df['Price_Change_5d'] = df['Close'].pct_change(5)
        df['Price_Change_20d'] = df['Close'].pct_change(20)
        
        # Volatility
        df['Volatility_20d'] = df['Price_Change_1d'].rolling(window=20).std() * np.sqrt(252)
        
        # Support and Resistance levels
        df['High_20'] = df['High'].rolling(window=20).max()
        df['Low_20'] = df['Low'].rolling(window=20).min()
        
        return df

    async def simulate_enhanced_decision(self, symbol: str, data: pd.Series, date: datetime) -> Dict[str, Any]:
        """Simulate enhanced PROMETHEUS decision making"""
        try:
            # Extract market data
            market_data = {
                'symbol': symbol,
                'price': float(data['Close']),
                'volume': float(data['Volume']),
                'indicators': {
                    'rsi': float(data.get('RSI', 50)),
                    'macd': float(data.get('MACD', 0)),
                    'macd_signal': float(data.get('MACD_Signal', 0)),
                    'macd_histogram': float(data.get('MACD_Histogram', 0)),
                    'bollinger_upper': float(data.get('BB_Upper', data['Close'])),
                    'bollinger_lower': float(data.get('BB_Lower', data['Close'])),
                    'bollinger_position': float(data.get('BB_Position', 0.5)),
                    'sma_20': float(data.get('SMA_20', data['Close'])),
                    'sma_50': float(data.get('SMA_50', data['Close'])),
                    'sma_200': float(data.get('SMA_200', data['Close'])),
                    'volume_ratio': float(data.get('Volume_Ratio', 1.0)),
                    'price_change_1d': float(data.get('Price_Change_1d', 0)),
                    'price_change_5d': float(data.get('Price_Change_5d', 0)),
                    'price_change_20d': float(data.get('Price_Change_20d', 0)),
                    'volatility_20d': float(data.get('Volatility_20d', 0.2)),
                    'high_20': float(data.get('High_20', data['Close'])),
                    'low_20': float(data.get('Low_20', data['Close']))
                }
            }
            
            # Enhanced decision making
            decision = await self._make_enhanced_decision(market_data)
            
            return decision
            
        except Exception as e:
            logger.error(f"[ERROR] Error in decision making for {symbol}: {e}")
            return {'action': 'HOLD', 'confidence': 0.5, 'position_size': 0.0}

    async def _make_enhanced_decision(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced decision making with multiple strategies"""
        try:
            indicators = market_data['indicators']
            price = market_data['price']
            
            # Strategy 1: Trend Following
            trend_score = self._trend_following_strategy(indicators, price)
            
            # Strategy 2: Mean Reversion
            mean_reversion_score = self._mean_reversion_strategy(indicators, price)
            
            # Strategy 3: Breakout
            breakout_score = self._breakout_strategy(indicators, price)
            
            # Strategy 4: Momentum
            momentum_score = self._momentum_strategy(indicators, price)
            
            # Strategy 5: Volume Analysis
            volume_score = self._volume_strategy(indicators)
            
            # Combine strategies with weights
            strategy_weights = {
                'trend': 0.25,
                'mean_reversion': 0.20,
                'breakout': 0.20,
                'momentum': 0.20,
                'volume': 0.15
            }
            
            combined_score = (
                trend_score * strategy_weights['trend'] +
                mean_reversion_score * strategy_weights['mean_reversion'] +
                breakout_score * strategy_weights['breakout'] +
                momentum_score * strategy_weights['momentum'] +
                volume_score * strategy_weights['volume']
            )
            
            # Market regime detection
            market_regime = self._detect_market_regime(indicators)
            
            # Confidence calibration
            confidence = self._calibrate_confidence(combined_score, market_regime, indicators)
            
            # Determine action
            if confidence >= self.min_confidence:
                if combined_score > 0.6:
                    action = 'BUY'
                elif combined_score < 0.4:
                    action = 'SELL'
                else:
                    action = 'HOLD'
            else:
                action = 'HOLD'
            
            # Calculate position size
            position_size = self._calculate_position_size(confidence, market_regime, indicators)
            
            return {
                'action': action,
                'confidence': confidence,
                'position_size': position_size,
                'decision_score': combined_score,
                'market_regime': market_regime,
                'strategy_scores': {
                    'trend': trend_score,
                    'mean_reversion': mean_reversion_score,
                    'breakout': breakout_score,
                    'momentum': momentum_score,
                    'volume': volume_score
                }
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Error in enhanced decision: {e}")
            return {'action': 'HOLD', 'confidence': 0.5, 'position_size': 0.0}

    def _trend_following_strategy(self, indicators: Dict[str, float], price: float) -> float:
        """Trend following strategy"""
        score = 0.5
        
        # Moving average alignment
        if indicators['sma_20'] > indicators['sma_50'] > indicators['sma_200']:
            score += 0.3  # Strong uptrend
        elif indicators['sma_20'] < indicators['sma_50'] < indicators['sma_200']:
            score -= 0.3  # Strong downtrend
        
        # Price above/below moving averages
        if price > indicators['sma_20']:
            score += 0.1
        else:
            score -= 0.1
            
        # MACD trend
        if indicators['macd'] > indicators['macd_signal']:
            score += 0.1
        else:
            score -= 0.1
            
        return max(0.0, min(1.0, score))

    def _mean_reversion_strategy(self, indicators: Dict[str, float], price: float) -> float:
        """Mean reversion strategy"""
        score = 0.5
        
        # RSI extremes
        if indicators['rsi'] < 30:  # Oversold
            score += 0.3
        elif indicators['rsi'] > 70:  # Overbought
            score -= 0.3
        
        # Bollinger Bands position
        if indicators['bollinger_position'] < 0.2:  # Near lower band
            score += 0.2
        elif indicators['bollinger_position'] > 0.8:  # Near upper band
            score -= 0.2
            
        # Price vs moving averages
        if price < indicators['sma_20'] * 0.95:  # 5% below SMA
            score += 0.1
        elif price > indicators['sma_20'] * 1.05:  # 5% above SMA
            score -= 0.1
            
        return max(0.0, min(1.0, score))

    def _breakout_strategy(self, indicators: Dict[str, float], price: float) -> float:
        """Breakout strategy"""
        score = 0.5
        
        # Breakout above resistance
        if price > indicators['high_20']:
            score += 0.4
            
        # Breakout below support
        if price < indicators['low_20']:
            score -= 0.4
            
        # Volume confirmation
        if indicators['volume_ratio'] > 1.5:  # High volume
            score += 0.2
        elif indicators['volume_ratio'] < 0.5:  # Low volume
            score -= 0.1
            
        return max(0.0, min(1.0, score))

    def _momentum_strategy(self, indicators: Dict[str, float], price: float) -> float:
        """Momentum strategy"""
        score = 0.5
        
        # Short-term momentum
        if indicators['price_change_1d'] > 0.02:  # 2% daily gain
            score += 0.2
        elif indicators['price_change_1d'] < -0.02:  # 2% daily loss
            score -= 0.2
            
        # Medium-term momentum
        if indicators['price_change_5d'] > 0.05:  # 5% weekly gain
            score += 0.2
        elif indicators['price_change_5d'] < -0.05:  # 5% weekly loss
            score -= 0.2
            
        # Long-term momentum
        if indicators['price_change_20d'] > 0.1:  # 10% monthly gain
            score += 0.1
        elif indicators['price_change_20d'] < -0.1:  # 10% monthly loss
            score -= 0.1
            
        return max(0.0, min(1.0, score))

    def _volume_strategy(self, indicators: Dict[str, float]) -> float:
        """Volume analysis strategy"""
        score = 0.5
        
        # Volume surge
        if indicators['volume_ratio'] > 2.0:  # 2x average volume
            score += 0.3
        elif indicators['volume_ratio'] > 1.5:  # 1.5x average volume
            score += 0.1
        elif indicators['volume_ratio'] < 0.5:  # Low volume
            score -= 0.2
            
        return max(0.0, min(1.0, score))

    def _detect_market_regime(self, indicators: Dict[str, float]) -> str:
        """Detect market regime"""
        volatility = indicators['volatility_20d']
        rsi = indicators['rsi']
        price_change_20d = indicators['price_change_20d']
        
        if volatility > 0.3:
            return 'volatile'
        elif price_change_20d > 0.05 and rsi > 50:
            return 'bullish'
        elif price_change_20d < -0.05 and rsi < 50:
            return 'bearish'
        else:
            return 'sideways'

    def _calibrate_confidence(self, base_score: float, market_regime: str, indicators: Dict[str, float]) -> float:
        """Calibrate confidence based on market conditions"""
        confidence = base_score
        
        # Adjust for market regime
        regime_adjustments = {
            'volatile': 0.7,  # Lower confidence in volatile markets
            'bullish': 1.1,
            'bearish': 1.1,
            'sideways': 0.9
        }
        
        confidence *= regime_adjustments.get(market_regime, 1.0)
        
        # Adjust for data quality
        if indicators['volume_ratio'] > 0.8:  # Good volume
            confidence *= 1.1
        else:
            confidence *= 0.9
            
        # Adjust for volatility
        if indicators['volatility_20d'] < 0.2:  # Low volatility
            confidence *= 1.1
        elif indicators['volatility_20d'] > 0.4:  # High volatility
            confidence *= 0.8
            
        return max(0.1, min(0.95, confidence))

    def _calculate_position_size(self, confidence: float, market_regime: str, indicators: Dict[str, float]) -> float:
        """Calculate position size based on confidence and market conditions"""
        base_size = self.max_position_size
        
        # Adjust for confidence
        confidence_factor = confidence * 0.5 + 0.5  # 0.5 to 1.0
        
        # Adjust for market regime
        regime_factors = {
            'volatile': 0.6,  # Smaller positions in volatile markets
            'bullish': 1.0,
            'bearish': 1.0,
            'sideways': 0.8
        }
        
        regime_factor = regime_factors.get(market_regime, 1.0)
        
        # Adjust for volatility
        volatility_factor = max(0.5, 1.0 - indicators['volatility_20d'])
        
        position_size = base_size * confidence_factor * regime_factor * volatility_factor
        return max(0.02, min(0.2, position_size))

    async def run_backtest(self) -> Dict[str, Any]:
        """Run enhanced backtest"""
        logger.info("[START] Starting Enhanced PROMETHEUS Backtest")
        logger.info("=" * 60)
        
        # Download historical data
        historical_data = await self.download_historical_data()
        
        if not historical_data:
            logger.error("[ERROR] No historical data available")
            return {}
        
        # Run backtest
        logger.info("[BACKTEST] Running enhanced backtest simulation...")
        
        # Get all trading dates
        all_dates = set()
        for symbol, df in historical_data.items():
            all_dates.update(df.index)
        
        trading_dates = sorted(list(all_dates))
        logger.info(f"[DATES] Trading {len(trading_dates)} days from {trading_dates[0]} to {trading_dates[-1]}")
        
        # Simulate trading
        for i, date in enumerate(trading_dates):
            if i % 100 == 0:  # Progress update every 100 days
                logger.info(f"[PROGRESS] Processing day {i+1}/{len(trading_dates)}: {date.strftime('%Y-%m-%d')}")
            
            # Update portfolio value
            portfolio_value = self._calculate_portfolio_value(historical_data, date)
            self.portfolio_values.append({
                'date': date,
                'value': portfolio_value,
                'capital': self.current_capital
            })
            
            # Process each symbol
            for symbol, df in historical_data.items():
                if date in df.index:
                    data = df.loc[date]
                    
                    # Get enhanced decision
                    decision = await self.simulate_enhanced_decision(symbol, data, date)
                    
                    # Execute trade if confidence is high enough and we have capacity
                    if (decision['confidence'] >= self.min_confidence and 
                        len(self.positions) < self.max_positions):
                        await self._execute_enhanced_trade(symbol, data, decision, date)
        
        # Calculate final metrics
        logger.info("[METRICS] Calculating performance metrics...")
        metrics = self._calculate_metrics()
        
        # Generate report
        self._generate_report(metrics)
        
        return metrics

    def _calculate_portfolio_value(self, historical_data: Dict[str, pd.DataFrame], date: datetime) -> float:
        """Calculate current portfolio value"""
        total_value = self.current_capital
        
        for symbol, position in self.positions.items():
            if symbol in historical_data and date in historical_data[symbol].index:
                current_price = historical_data[symbol].loc[date, 'Close']
                position_value = position['shares'] * current_price
                total_value += position_value
                
        return total_value

    async def _execute_enhanced_trade(self, symbol: str, data: pd.Series, decision: Dict[str, Any], date: datetime):
        """Execute enhanced trade with better risk management"""
        try:
            action = decision['action']
            confidence = decision['confidence']
            position_size = decision['position_size']
            current_price = data['Close']
            
            if action == 'BUY' and symbol not in self.positions:
                # Calculate position size
                position_value = self.current_capital * position_size
                shares = position_value / current_price
                
                # Execute buy
                self.positions[symbol] = {
                    'shares': shares,
                    'entry_price': current_price,
                    'entry_date': date,
                    'confidence': confidence,
                    'stop_loss': current_price * (1 - self.stop_loss_pct),
                    'take_profit': current_price * (1 + self.take_profit_pct)
                }
                
                self.current_capital -= position_value
                
                logger.debug(f"  [BUY] {symbol}: {shares:.2f} shares @ ${current_price:.2f} (Confidence: {confidence:.2f})")
                
            elif action == 'SELL' and symbol in self.positions:
                position = self.positions[symbol]
                shares = position['shares']
                entry_price = position['entry_price']
                
                # Calculate P&L
                pnl = shares * (current_price - entry_price)
                pnl_pct = (current_price - entry_price) / entry_price
                
                # Record trade
                trade = {
                    'symbol': symbol,
                    'action': 'SELL',
                    'entry_date': position['entry_date'],
                    'exit_date': date,
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'shares': shares,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'confidence': confidence,
                    'holding_days': (date - position['entry_date']).days
                }
                
                self.trades.append(trade)
                
                # Update capital
                self.current_capital += shares * current_price
                
                # Update metrics
                if pnl > 0:
                    self.metrics['winning_trades'] += 1
                    self.metrics['gross_profit'] += pnl
                else:
                    self.metrics['losing_trades'] += 1
                    self.metrics['gross_loss'] += abs(pnl)
                
                self.metrics['total_trades'] += 1
                
                # Remove position
                del self.positions[symbol]
                
                logger.debug(f"  [SELL] {symbol}: {shares:.2f} shares @ ${current_price:.2f} (P&L: ${pnl:.2f}, {pnl_pct:.2%})")
                
        except Exception as e:
            logger.error(f"[ERROR] Error executing trade for {symbol}: {e}")

    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive trading metrics"""
        logger.info("[METRICS] Calculating performance metrics...")
        
        if not self.portfolio_values:
            logger.error("[ERROR] No portfolio data available")
            return {}
        
        # Convert to DataFrame for easier calculation
        df = pd.DataFrame(self.portfolio_values)
        df['date'] = pd.to_datetime(df['date'], utc=True)
        df = df.set_index('date').sort_index()
        
        # Calculate returns
        df['returns'] = df['value'].pct_change()
        df['cumulative_returns'] = (1 + df['returns']).cumprod() - 1
        
        # Total return
        total_return = (df['value'].iloc[-1] / df['value'].iloc[0]) - 1
        self.metrics['total_return'] = total_return
        
        # Annualized return
        days = (df.index[-1] - df.index[0]).days
        years = days / 365.25
        annualized_return = (1 + total_return) ** (1 / years) - 1
        
        # Sharpe ratio
        risk_free_rate = 0.02  # 2% risk-free rate
        excess_returns = df['returns'].mean() * 252 - risk_free_rate
        volatility = df['returns'].std() * np.sqrt(252)
        sharpe_ratio = excess_returns / volatility if volatility > 0 else 0
        self.metrics['sharpe_ratio'] = sharpe_ratio
        
        # Maximum drawdown
        rolling_max = df['value'].expanding().max()
        drawdown = (df['value'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        self.metrics['max_drawdown'] = abs(max_drawdown)
        
        # Win rate
        if self.metrics['total_trades'] > 0:
            win_rate = self.metrics['winning_trades'] / self.metrics['total_trades']
            self.metrics['win_rate'] = win_rate
        
        # Profit factor
        if self.metrics['gross_loss'] > 0:
            profit_factor = self.metrics['gross_profit'] / self.metrics['gross_loss']
            self.metrics['profit_factor'] = profit_factor
        
        # Average win/loss ratio
        if self.metrics['winning_trades'] > 0 and self.metrics['losing_trades'] > 0:
            avg_win = self.metrics['gross_profit'] / self.metrics['winning_trades']
            avg_loss = self.metrics['gross_loss'] / self.metrics['losing_trades']
            self.metrics['average_win'] = avg_win
            self.metrics['average_loss'] = avg_loss
            self.metrics['average_win_loss_ratio'] = avg_win / avg_loss
        
        # Calmar ratio
        if self.metrics['max_drawdown'] > 0:
            calmar_ratio = annualized_return / self.metrics['max_drawdown']
            self.metrics['calmar_ratio'] = calmar_ratio
        
        # Sortino ratio
        downside_returns = df['returns'][df['returns'] < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252)
        if downside_volatility > 0:
            sortino_ratio = excess_returns / downside_volatility
            self.metrics['sortino_ratio'] = sortino_ratio
        
        # Volatility
        self.metrics['volatility'] = volatility
        
        # Additional metrics
        self.metrics['final_capital'] = df['value'].iloc[-1]
        self.metrics['total_pnl'] = df['value'].iloc[-1] - self.initial_capital
        self.metrics['annualized_return'] = annualized_return
        
        return self.metrics

    def _generate_report(self, metrics: Dict[str, Any]):
        """Generate comprehensive backtest report"""
        logger.info("[REPORT] Generating enhanced backtest report...")
        
        print("\n" + "=" * 80)
        print("PROMETHEUS ENHANCED HISTORICAL BACKTEST RESULTS")
        print("=" * 80)
        
        print(f"\n[PERIOD] BACKTEST PERIOD: {self.start_date} to {self.end_date}")
        print(f"[CAPITAL] INITIAL CAPITAL: ${self.initial_capital:,}")
        print(f"[CAPITAL] FINAL CAPITAL: ${metrics.get('final_capital', 0):,.2f}")
        print(f"[P&L] TOTAL P&L: ${metrics.get('total_pnl', 0):,.2f}")
        
        print(f"\n[METRICS] CRITICAL TRADING METRICS:")
        print("-" * 50)
        
        # Total Return
        total_return = metrics.get('total_return', 0)
        print(f"[RETURN] Total Return: {total_return:.2%}")
        if total_return > 0.1:
            print("   [EXCELLENT] (>10%)")
        elif total_return > 0.05:
            print("   [GOOD] (>5%)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        # Sharpe Ratio
        sharpe = metrics.get('sharpe_ratio', 0)
        print(f"[SHARPE] Sharpe Ratio: {sharpe:.2f}")
        if sharpe > 2.0:
            print("   [EXCELLENT] (>2.0)")
        elif sharpe > 1.0:
            print("   [GOOD] (>1.0)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        # Max Drawdown
        max_dd = metrics.get('max_drawdown', 0)
        print(f"[DRAWDOWN] Max Drawdown: {max_dd:.2%}")
        if max_dd < 0.1:
            print("   [EXCELLENT] (<10%)")
        elif max_dd < 0.2:
            print("   [GOOD] (<20%)")
        else:
            print("   [HIGH RISK] (>20%)")
        
        # Win Rate
        win_rate = metrics.get('win_rate', 0)
        print(f"[WIN RATE] Win Rate: {win_rate:.2%}")
        if win_rate > 0.6:
            print("   [EXCELLENT] (>60%)")
        elif win_rate > 0.5:
            print("   [GOOD] (>50%)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        # Profit Factor
        pf = metrics.get('profit_factor', 0)
        print(f"[PROFIT FACTOR] Profit Factor: {pf:.2f}")
        if pf > 2.0:
            print("   [EXCELLENT] (>2.0)")
        elif pf > 1.5:
            print("   [GOOD] (>1.5)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        # Average Win/Loss Ratio
        awl = metrics.get('average_win_loss_ratio', 0)
        print(f"[WIN/LOSS] Avg Win/Loss Ratio: {awl:.2f}")
        if awl > 2.0:
            print("   [EXCELLENT] (>2.0)")
        elif awl > 1.5:
            print("   [GOOD] (>1.5)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        # Calmar Ratio
        calmar = metrics.get('calmar_ratio', 0)
        print(f"[CALMAR] Calmar Ratio: {calmar:.2f}")
        if calmar > 2.0:
            print("   [EXCELLENT] (>2.0)")
        elif calmar > 1.0:
            print("   [GOOD] (>1.0)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        # Sortino Ratio
        sortino = metrics.get('sortino_ratio', 0)
        print(f"[SORTINO] Sortino Ratio: {sortino:.2f}")
        if sortino > 2.0:
            print("   [EXCELLENT] (>2.0)")
        elif sortino > 1.0:
            print("   [GOOD] (>1.0)")
        else:
            print("   [NEEDS IMPROVEMENT]")
        
        print(f"\n[STATS] TRADING STATISTICS:")
        print("-" * 50)
        print(f"[TOTAL] Total Trades: {metrics.get('total_trades', 0)}")
        print(f"[WINS] Winning Trades: {metrics.get('winning_trades', 0)}")
        print(f"[LOSSES] Losing Trades: {metrics.get('losing_trades', 0)}")
        print(f"[PROFIT] Gross Profit: ${metrics.get('gross_profit', 0):,.2f}")
        print(f"[LOSS] Gross Loss: ${metrics.get('gross_loss', 0):,.2f}")
        print(f"[AVG WIN] Average Win: ${metrics.get('average_win', 0):,.2f}")
        print(f"[AVG LOSS] Average Loss: ${metrics.get('average_loss', 0):,.2f}")
        print(f"[ANNUAL] Annualized Return: {metrics.get('annualized_return', 0):.2%}")
        print(f"[VOLATILITY] Volatility: {metrics.get('volatility', 0):.2%}")
        
        # Overall Assessment
        print(f"\n[ASSESSMENT] OVERALL ASSESSMENT:")
        print("-" * 50)
        
        score = 0
        max_score = 8
        
        if total_return > 0.1: score += 1
        if sharpe > 1.0: score += 1
        if max_dd < 0.2: score += 1
        if win_rate > 0.5: score += 1
        if pf > 1.5: score += 1
        if awl > 1.5: score += 1
        if calmar > 1.0: score += 1
        if sortino > 1.0: score += 1
        
        percentage = (score / max_score) * 100
        
        print(f"[SCORE] Performance Score: {score}/{max_score} ({percentage:.1f}%)")
        
        if percentage >= 75:
            print("[EXCELLENT] System ready for live trading!")
        elif percentage >= 50:
            print("[GOOD] System shows promise, minor optimizations needed")
        else:
            print("[NEEDS IMPROVEMENT] Significant optimizations required")
        
        print("\n" + "=" * 80)
        
        # Save results
        self._save_results(metrics)

    def _save_results(self, metrics: Dict[str, Any]):
        """Save backtest results to file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prometheus_enhanced_backtest_results_{timestamp}.json"
            
            results = {
                'backtest_info': {
                    'start_date': self.start_date,
                    'end_date': self.end_date,
                    'initial_capital': self.initial_capital,
                    'symbols_tested': self.symbols,
                    'timestamp': timestamp,
                    'version': 'enhanced'
                },
                'metrics': metrics,
                'trades': self.trades,
                'portfolio_values': self.portfolio_values
            }
            
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"[SAVE] Results saved to: {filename}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error saving results: {e}")

async def main():
    """Main function to run the enhanced backtest"""
    print("PROMETHEUS ENHANCED HISTORICAL BACKTESTING SYSTEM")
    print("=" * 60)
    
    # Initialize enhanced backtester
    backtester = PrometheusEnhancedBacktester(
        start_date="2022-01-01",  # 3 years of data
        end_date="2024-12-31"
    )
    
    # Run backtest
    results = await backtester.run_backtest()
    
    if results:
        print("\n[SUCCESS] Enhanced backtest completed successfully!")
        print("[REPORT] Check the generated report above for detailed results.")
    else:
        print("\n[ERROR] Enhanced backtest failed. Check logs for details.")

if __name__ == "__main__":
    asyncio.run(main())
