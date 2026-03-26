"""
Regime-Adaptive Trading Strategies
Dynamically adjusts strategy based on detected market regime
Integrates with Market Regime Forecaster for proactive positioning
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StrategySignal:
    """Trading signal from regime-adaptive strategy"""
    action: str  # 'buy', 'sell', 'hold', 'close'
    symbol: str
    confidence: float
    position_size: float
    entry_price: float
    stop_loss: float
    take_profit: float
    regime: str
    strategy_type: str
    timestamp: datetime
    reasoning: str

class RegimeAdaptiveStrategy:
    """
    Dynamically switches strategies based on market regime
    Optimizes for each regime's characteristics
    """
    
    def __init__(self):
        # Strategy parameters by regime
        self.regime_strategies = {
            'bull': {
                'strategy_type': 'momentum_long',
                'position_size_multiplier': 1.5,  # Aggressive in bull market
                'stop_loss_pct': 0.03,  # Wider stops
                'take_profit_pct': 0.08,  # Larger targets
                'entry_threshold': 0.60,  # Lower entry bar
                'max_positions': 8,
                'hold_time_days': 5
            },
            'bear': {
                'strategy_type': 'short_bias',
                'position_size_multiplier': 1.2,
                'stop_loss_pct': 0.02,  # Tighter stops
                'take_profit_pct': 0.05,
                'entry_threshold': 0.70,  # Higher entry bar
                'max_positions': 5,
                'hold_time_days': 3
            },
            'volatile': {
                'strategy_type': 'range_trading',
                'position_size_multiplier': 0.6,  # Reduce size
                'stop_loss_pct': 0.015,  # Very tight stops
                'take_profit_pct': 0.03,  # Quick profits
                'entry_threshold': 0.75,  # High confidence only
                'max_positions': 3,
                'hold_time_days': 1
            },
            'sideways': {
                'strategy_type': 'mean_reversion',
                'position_size_multiplier': 1.0,
                'stop_loss_pct': 0.02,
                'take_profit_pct': 0.04,
                'entry_threshold': 0.65,
                'max_positions': 6,
                'hold_time_days': 3
            }
        }
        
        # Performance tracking by regime
        self.regime_performance = {
            'bull': {'wins': 0, 'losses': 0, 'total_return': 0.0},
            'bear': {'wins': 0, 'losses': 0, 'total_return': 0.0},
            'volatile': {'wins': 0, 'losses': 0, 'total_return': 0.0},
            'sideways': {'wins': 0, 'losses': 0, 'total_return': 0.0}
        }
        
        logger.info("✅ Regime-Adaptive Strategy initialized")
    
    async def generate_signal(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        current_regime: str,
        predicted_regime: Optional[str] = None,
        regime_confidence: float = 0.70,
        ai_signals: Optional[Dict[str, Any]] = None
    ) -> Optional[StrategySignal]:
        """
        Generate trading signal adapted to current regime
        
        Args:
            symbol: Trading symbol
            market_data: Historical price data
            current_regime: Current market regime
            predicted_regime: Forecasted regime (if changing)
            regime_confidence: Confidence in regime detection
            ai_signals: Signals from AI systems (HRM, GPT-OSS, etc.)
            
        Returns:
            Trading signal or None
        """
        try:
            # Get strategy parameters for current regime
            params = self.regime_strategies.get(
                current_regime,
                self.regime_strategies['sideways']
            )
            
            # Calculate technical indicators
            indicators = self._calculate_indicators(market_data)
            
            # Generate base signal using regime-specific strategy
            if params['strategy_type'] == 'momentum_long':
                signal = self._momentum_long_strategy(
                    symbol, market_data, indicators, params
                )
            elif params['strategy_type'] == 'short_bias':
                signal = self._short_bias_strategy(
                    symbol, market_data, indicators, params
                )
            elif params['strategy_type'] == 'range_trading':
                signal = self._range_trading_strategy(
                    symbol, market_data, indicators, params
                )
            elif params['strategy_type'] == 'mean_reversion':
                signal = self._mean_reversion_strategy(
                    symbol, market_data, indicators, params
                )
            else:
                return None
            
            if signal is None:
                return None
            
            # Adjust signal based on predicted regime change
            if predicted_regime and predicted_regime != current_regime:
                signal = self._adjust_for_regime_transition(
                    signal, current_regime, predicted_regime, regime_confidence
                )
            
            # Integrate AI signals if available
            if ai_signals:
                signal = self._integrate_ai_signals(signal, ai_signals)
            
            # Validate signal
            if signal.confidence < params['entry_threshold']:
                logger.debug(f"Signal confidence {signal.confidence:.2%} below threshold "
                           f"{params['entry_threshold']:.2%}")
                return None
            
            logger.info(f"📈 Generated {signal.action.upper()} signal for {symbol} "
                       f"in {current_regime} regime (confidence: {signal.confidence:.2%})")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    def _calculate_indicators(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate technical indicators"""
        indicators = {}
        
        # Price-based
        indicators['current_price'] = data['close'].iloc[-1]
        indicators['sma_20'] = data['close'].rolling(20).mean().iloc[-1]
        indicators['sma_50'] = data['close'].rolling(50).mean().iloc[-1]
        indicators['ema_12'] = data['close'].ewm(span=12).mean().iloc[-1]
        indicators['ema_26'] = data['close'].ewm(span=26).mean().iloc[-1]
        
        # Momentum
        indicators['rsi'] = self._calculate_rsi(data['close'], 14)
        indicators['macd'] = indicators['ema_12'] - indicators['ema_26']
        
        # Volatility
        indicators['atr'] = self._calculate_atr(data, 14)
        indicators['bollinger_upper'] = indicators['sma_20'] + (2 * data['close'].rolling(20).std().iloc[-1])
        indicators['bollinger_lower'] = indicators['sma_20'] - (2 * data['close'].rolling(20).std().iloc[-1])
        
        # Volume
        if 'volume' in data.columns:
            indicators['volume_sma'] = data['volume'].rolling(20).mean().iloc[-1]
            indicators['volume_ratio'] = data['volume'].iloc[-1] / indicators['volume_sma'] if indicators['volume_sma'] > 0 else 1.0
        else:
            indicators['volume_ratio'] = 1.0
        
        # Trend strength
        indicators['trend_strength'] = abs(indicators['current_price'] - indicators['sma_50']) / indicators['sma_50']
        
        return indicators
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean().iloc[-1]
        
        return float(atr) if not np.isnan(atr) else 0.0
    
    def _momentum_long_strategy(
        self,
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Optional[StrategySignal]:
        """Bull market momentum strategy"""
        price = indicators['current_price']
        
        # Entry conditions: Strong uptrend
        conditions = [
            indicators['current_price'] > indicators['sma_20'],  # Above short-term average
            indicators['sma_20'] > indicators['sma_50'],  # Golden cross
            indicators['macd'] > 0,  # Positive momentum
            indicators['rsi'] < 70,  # Not overbought
            indicators['volume_ratio'] > 1.0  # Above-average volume
        ]
        
        matches = sum(conditions)
        confidence = matches / len(conditions)
        
        if confidence < params['entry_threshold']:
            return None
        
        # Calculate stops and targets
        stop_loss = price * (1 - params['stop_loss_pct'])
        take_profit = price * (1 + params['take_profit_pct'])
        
        # Position sizing
        position_size = 1.0 * params['position_size_multiplier']
        
        return StrategySignal(
            action='buy',
            symbol=symbol,
            confidence=confidence,
            position_size=position_size,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            regime='bull',
            strategy_type='momentum_long',
            timestamp=datetime.utcnow(),
            reasoning=f"Momentum long: {matches}/{len(conditions)} conditions met"
        )
    
    def _short_bias_strategy(
        self,
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Optional[StrategySignal]:
        """Bear market short strategy"""
        price = indicators['current_price']
        
        # Entry conditions: Strong downtrend
        conditions = [
            indicators['current_price'] < indicators['sma_20'],  # Below short-term average
            indicators['sma_20'] < indicators['sma_50'],  # Death cross
            indicators['macd'] < 0,  # Negative momentum
            indicators['rsi'] > 30,  # Not oversold
            indicators['volume_ratio'] > 1.0  # Above-average volume
        ]
        
        matches = sum(conditions)
        confidence = matches / len(conditions)
        
        if confidence < params['entry_threshold']:
            return None
        
        # Calculate stops and targets
        stop_loss = price * (1 + params['stop_loss_pct'])  # Stop above entry for shorts
        take_profit = price * (1 - params['take_profit_pct'])
        
        position_size = 1.0 * params['position_size_multiplier']
        
        return StrategySignal(
            action='sell',  # Short
            symbol=symbol,
            confidence=confidence,
            position_size=position_size,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            regime='bear',
            strategy_type='short_bias',
            timestamp=datetime.utcnow(),
            reasoning=f"Short bias: {matches}/{len(conditions)} conditions met"
        )
    
    def _range_trading_strategy(
        self,
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Optional[StrategySignal]:
        """Volatile market range trading"""
        price = indicators['current_price']
        
        # Buy at support, sell at resistance
        near_support = price <= indicators['bollinger_lower'] * 1.02
        near_resistance = price >= indicators['bollinger_upper'] * 0.98
        
        if near_support and indicators['rsi'] < 40:
            action = 'buy'
            stop_loss = price * (1 - params['stop_loss_pct'])
            take_profit = indicators['sma_20']  # Target middle of range
            confidence = 0.75
            reasoning = "Range trading: Buy at support"
        elif near_resistance and indicators['rsi'] > 60:
            action = 'sell'
            stop_loss = price * (1 + params['stop_loss_pct'])
            take_profit = indicators['sma_20']
            confidence = 0.75
            reasoning = "Range trading: Sell at resistance"
        else:
            return None
        
        position_size = 1.0 * params['position_size_multiplier']
        
        return StrategySignal(
            action=action,
            symbol=symbol,
            confidence=confidence,
            position_size=position_size,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            regime='volatile',
            strategy_type='range_trading',
            timestamp=datetime.utcnow(),
            reasoning=reasoning
        )
    
    def _mean_reversion_strategy(
        self,
        symbol: str,
        data: pd.DataFrame,
        indicators: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Optional[StrategySignal]:
        """Sideways market mean reversion"""
        price = indicators['current_price']
        sma = indicators['sma_20']
        
        # Calculate deviation from mean
        deviation = (price - sma) / sma
        
        # Buy when below mean, sell when above
        if deviation < -0.02 and indicators['rsi'] < 45:
            action = 'buy'
            stop_loss = price * (1 - params['stop_loss_pct'])
            take_profit = sma  # Revert to mean
            confidence = 0.70 + abs(deviation) * 10  # Higher confidence with larger deviation
            reasoning = f"Mean reversion: {deviation:.2%} below average"
        elif deviation > 0.02 and indicators['rsi'] > 55:
            action = 'sell'
            stop_loss = price * (1 + params['stop_loss_pct'])
            take_profit = sma
            confidence = 0.70 + abs(deviation) * 10
            reasoning = f"Mean reversion: {deviation:.2%} above average"
        else:
            return None
        
        position_size = 1.0 * params['position_size_multiplier']
        
        return StrategySignal(
            action=action,
            symbol=symbol,
            confidence=min(0.95, confidence),
            position_size=position_size,
            entry_price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            regime='sideways',
            strategy_type='mean_reversion',
            timestamp=datetime.utcnow(),
            reasoning=reasoning
        )
    
    def _adjust_for_regime_transition(
        self,
        signal: StrategySignal,
        current_regime: str,
        predicted_regime: str,
        confidence: float
    ) -> StrategySignal:
        """Adjust signal for upcoming regime change"""
        # If high confidence in regime change, reduce position size
        if confidence > 0.75:
            signal.position_size *= 0.7
            signal.reasoning += f" | Reduced for {current_regime}→{predicted_regime} transition"
        
        # Tighten stops ahead of regime change
        if signal.action == 'buy':
            signal.stop_loss = signal.entry_price * 0.98  # Tighter stop
        else:
            signal.stop_loss = signal.entry_price * 1.02
        
        return signal
    
    def _integrate_ai_signals(
        self,
        signal: StrategySignal,
        ai_signals: Dict[str, Any]
    ) -> StrategySignal:
        """Integrate AI model signals with technical signal"""
        # Get AI consensus
        ai_action = ai_signals.get('action', 'hold')
        ai_confidence = ai_signals.get('confidence', 0.5)
        
        # Adjust confidence based on AI agreement
        if ai_action == signal.action:
            # AI agrees - boost confidence
            signal.confidence = min(0.95, signal.confidence * 1.2)
            signal.reasoning += f" | AI consensus: {ai_confidence:.2%}"
        else:
            # AI disagrees - reduce confidence
            signal.confidence *= 0.8
            signal.reasoning += f" | AI conflict: {ai_action}"
        
        return signal
    
    def record_trade_outcome(
        self,
        regime: str,
        profit_loss: float
    ):
        """Record trade outcome for regime performance tracking"""
        if regime not in self.regime_performance:
            return
        
        if profit_loss > 0:
            self.regime_performance[regime]['wins'] += 1
        else:
            self.regime_performance[regime]['losses'] += 1
        
        self.regime_performance[regime]['total_return'] += profit_loss
    
    def get_regime_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary by regime"""
        summary = {}
        
        for regime, perf in self.regime_performance.items():
            total_trades = perf['wins'] + perf['losses']
            win_rate = perf['wins'] / total_trades if total_trades > 0 else 0
            
            summary[regime] = {
                'total_trades': total_trades,
                'wins': perf['wins'],
                'losses': perf['losses'],
                'win_rate': win_rate,
                'total_return': perf['total_return'],
                'average_return': perf['total_return'] / total_trades if total_trades > 0 else 0
            }
        
        return summary


# Global instance
_regime_strategy = None

def get_regime_strategy() -> RegimeAdaptiveStrategy:
    """Get or create global regime-adaptive strategy instance"""
    global _regime_strategy
    if _regime_strategy is None:
        _regime_strategy = RegimeAdaptiveStrategy()
    return _regime_strategy
