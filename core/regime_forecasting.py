"""
Market Regime Detection and Forecasting System
Predicts regime changes BEFORE they happen for proactive trading
Identifies: Bull, Bear, Volatile, Sideways regimes
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class MarketRegime:
    """Market regime classification"""
    current_regime: str  # 'bull', 'bear', 'volatile', 'sideways'
    confidence: float
    duration_days: int
    characteristics: Dict[str, float]
    timestamp: datetime

@dataclass
class RegimeForecast:
    """Forecast of upcoming regime change"""
    predicted_regime: str
    current_regime: str
    probability: float
    expected_transition_days: int
    confidence: float
    signals: List[str]
    timestamp: datetime

class MarketRegimeForecaster:
    """
    Predicts market regime changes using multiple indicators
    Enables proactive positioning before regime shifts
    """
    
    def __init__(self):
        # Regime characteristics
        self.regime_definitions = {
            'bull': {
                'returns_mean': 0.001,  # Positive daily returns
                'volatility_max': 0.015,  # Low volatility
                'trend_strength_min': 0.6,  # Strong uptrend
                'momentum_min': 0.5
            },
            'bear': {
                'returns_mean': -0.001,  # Negative daily returns
                'volatility_max': 0.025,  # Higher volatility
                'trend_strength_min': 0.6,  # Strong downtrend
                'momentum_max': -0.5
            },
            'volatile': {
                'volatility_min': 0.025,  # High volatility
                'returns_std_min': 0.020,  # High variance
                'trend_strength_max': 0.4  # Weak trends
            },
            'sideways': {
                'volatility_max': 0.015,  # Low volatility
                'returns_mean_max': 0.0005,  # Minimal returns
                'trend_strength_max': 0.3  # No clear trend
            }
        }
        
        # Regime transition probabilities (from historical data)
        self.transition_matrix = {
            'bull': {'bull': 0.70, 'sideways': 0.20, 'volatile': 0.07, 'bear': 0.03},
            'bear': {'bear': 0.65, 'sideways': 0.20, 'volatile': 0.10, 'bull': 0.05},
            'volatile': {'volatile': 0.50, 'sideways': 0.25, 'bull': 0.15, 'bear': 0.10},
            'sideways': {'sideways': 0.60, 'bull': 0.20, 'volatile': 0.15, 'bear': 0.05}
        }
        
        # Early warning indicators
        self.warning_indicators = {
            'volatility_spike': 0.03,  # 3% volatility threshold
            'volume_surge': 2.0,  # 2x normal volume
            'momentum_reversal': 0.02,  # 2% momentum shift
            'correlation_breakdown': 0.3  # Asset correlation drop
        }
        
        self.current_regime = None
        self.regime_history = []
        
        logger.info("✅ Market Regime Forecaster initialized")
    
    async def detect_current_regime(
        self,
        market_data: pd.DataFrame,
        window_days: int = 30
    ) -> MarketRegime:
        """
        Detect current market regime from recent data
        
        Args:
            market_data: DataFrame with OHLCV data
            window_days: Lookback window for regime detection
            
        Returns:
            Current market regime classification
        """
        try:
            if len(market_data) < window_days:
                logger.warning(f"Insufficient data ({len(market_data)} < {window_days} days)")
                return self._get_default_regime()
            
            # Calculate regime characteristics
            recent_data = market_data.tail(window_days)
            characteristics = self._calculate_regime_characteristics(recent_data)
            
            # Classify regime
            regime_scores = self._score_regimes(characteristics)
            best_regime = max(regime_scores, key=regime_scores.get)
            confidence = regime_scores[best_regime]
            
            # Create regime object
            regime = MarketRegime(
                current_regime=best_regime,
                confidence=confidence,
                duration_days=self._estimate_regime_duration(recent_data),
                characteristics=characteristics,
                timestamp=datetime.utcnow()
            )
            
            self.current_regime = regime
            self.regime_history.append(regime)
            
            # Keep last 100 regimes
            if len(self.regime_history) > 100:
                self.regime_history = self.regime_history[-100:]
            
            logger.info(f"📊 Current regime: {best_regime.upper()} "
                       f"(confidence: {confidence:.2%}, duration: {regime.duration_days} days)")
            
            return regime
            
        except Exception as e:
            logger.error(f"Error detecting regime: {e}")
            return self._get_default_regime()
    
    async def forecast_regime_change(
        self,
        market_data: pd.DataFrame,
        forecast_days: int = 7
    ) -> RegimeForecast:
        """
        Forecast upcoming regime changes
        
        Args:
            market_data: DataFrame with OHLCV data
            forecast_days: Days ahead to forecast
            
        Returns:
            Regime change forecast with probability
        """
        try:
            # Detect current regime if not already detected
            if self.current_regime is None:
                await self.detect_current_regime(market_data)
            
            current_regime_name = self.current_regime.current_regime
            
            # Analyze early warning signals
            warning_signals = self._detect_warning_signals(market_data)
            
            # Calculate transition probabilities
            transition_probs = self.transition_matrix.get(
                current_regime_name,
                {'bull': 0.25, 'bear': 0.25, 'volatile': 0.25, 'sideways': 0.25}
            )
            
            # Adjust probabilities based on warning signals
            adjusted_probs = self._adjust_probabilities(
                transition_probs,
                warning_signals,
                market_data
            )
            
            # Determine most likely future regime
            predicted_regime = max(adjusted_probs, key=adjusted_probs.get)
            probability = adjusted_probs[predicted_regime]
            
            # Estimate timing of transition
            expected_days = self._estimate_transition_timing(
                warning_signals,
                self.current_regime.duration_days
            )
            
            # Calculate confidence
            confidence = self._calculate_forecast_confidence(
                warning_signals,
                probability,
                self.current_regime.confidence
            )
            
            forecast = RegimeForecast(
                predicted_regime=predicted_regime,
                current_regime=current_regime_name,
                probability=probability,
                expected_transition_days=expected_days,
                confidence=confidence,
                signals=warning_signals,
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"🔮 Regime forecast: {current_regime_name.upper()} → "
                       f"{predicted_regime.upper()} in ~{expected_days} days "
                       f"(probability: {probability:.2%}, confidence: {confidence:.2%})")
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting regime: {e}")
            return self._get_default_forecast()
    
    def _calculate_regime_characteristics(
        self,
        data: pd.DataFrame
    ) -> Dict[str, float]:
        """Calculate characteristics for regime classification"""
        # Calculate returns
        returns = data['close'].pct_change().dropna()
        
        # Volatility (standard deviation of returns)
        volatility = returns.std()
        
        # Mean return
        mean_return = returns.mean()
        
        # Trend strength (using linear regression slope)
        x = np.arange(len(data))
        y = data['close'].values
        trend_slope = np.polyfit(x, y, 1)[0] / y.mean()  # Normalized slope
        trend_strength = abs(trend_slope)
        
        # Momentum (rate of change)
        momentum = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]
        
        # Volume analysis
        volume_mean = data['volume'].mean() if 'volume' in data.columns else 0
        volume_std = data['volume'].std() if 'volume' in data.columns else 0
        
        return {
            'returns_mean': float(mean_return),
            'returns_std': float(returns.std()),
            'volatility': float(volatility),
            'trend_strength': float(trend_strength),
            'trend_slope': float(trend_slope),
            'momentum': float(momentum),
            'volume_mean': float(volume_mean),
            'volume_std': float(volume_std)
        }
    
    def _score_regimes(
        self,
        characteristics: Dict[str, float]
    ) -> Dict[str, float]:
        """Score each regime based on current characteristics"""
        scores = {}
        
        for regime_name, definition in self.regime_definitions.items():
            score = 0.0
            matches = 0
            total_conditions = len(definition)
            
            for condition, threshold in definition.items():
                char_key = condition.replace('_min', '').replace('_max', '')
                char_value = characteristics.get(char_key, 0)
                
                if '_min' in condition:
                    if char_value >= threshold:
                        score += 1.0
                        matches += 1
                elif '_max' in condition:
                    if char_value <= threshold:
                        score += 1.0
                        matches += 1
                else:
                    # Exact match (with tolerance)
                    if abs(char_value - threshold) < 0.001:
                        score += 1.0
                        matches += 1
            
            # Normalize score
            scores[regime_name] = score / total_conditions if total_conditions > 0 else 0.0
        
        return scores
    
    def _estimate_regime_duration(self, data: pd.DataFrame) -> int:
        """Estimate how long current regime has lasted"""
        # Simplified: count consecutive similar days
        returns = data['close'].pct_change().dropna()
        
        # Count consecutive positive/negative days
        sign = np.sign(returns.iloc[-1])
        duration = 1
        
        for i in range(len(returns) - 2, -1, -1):
            if np.sign(returns.iloc[i]) == sign:
                duration += 1
            else:
                break
        
        return duration
    
    def _detect_warning_signals(
        self,
        data: pd.DataFrame
    ) -> List[str]:
        """Detect early warning signals of regime change"""
        signals = []
        
        if len(data) < 10:
            return signals
        
        recent = data.tail(10)
        older = data.tail(30).head(20) if len(data) >= 30 else data
        
        # Volatility spike
        recent_vol = recent['close'].pct_change().std()
        older_vol = older['close'].pct_change().std()
        if recent_vol > older_vol * 1.5 and recent_vol > self.warning_indicators['volatility_spike']:
            signals.append('volatility_spike')
        
        # Volume surge
        if 'volume' in data.columns:
            recent_volume = recent['volume'].mean()
            older_volume = older['volume'].mean()
            if recent_volume > older_volume * self.warning_indicators['volume_surge']:
                signals.append('volume_surge')
        
        # Momentum reversal
        recent_momentum = (recent['close'].iloc[-1] - recent['close'].iloc[0]) / recent['close'].iloc[0]
        older_momentum = (older['close'].iloc[-1] - older['close'].iloc[0]) / older['close'].iloc[0]
        if np.sign(recent_momentum) != np.sign(older_momentum) and abs(recent_momentum) > 0.01:
            signals.append('momentum_reversal')
        
        # Price action extremes
        if recent['high'].max() > data.tail(100)['high'].quantile(0.95):
            signals.append('price_extreme_high')
        if recent['low'].min() < data.tail(100)['low'].quantile(0.05):
            signals.append('price_extreme_low')
        
        return signals
    
    def _adjust_probabilities(
        self,
        base_probs: Dict[str, float],
        signals: List[str],
        data: pd.DataFrame
    ) -> Dict[str, float]:
        """Adjust transition probabilities based on warning signals"""
        adjusted = base_probs.copy()
        
        # Increase volatility regime probability on warning signals
        if len(signals) >= 2:
            adjusted['volatile'] = min(1.0, adjusted['volatile'] * 1.5)
        
        # Increase bear regime probability on certain signals
        if 'price_extreme_high' in signals or 'momentum_reversal' in signals:
            adjusted['bear'] = min(1.0, adjusted['bear'] * 1.3)
        
        # Increase bull regime probability on recovery signals
        if 'price_extreme_low' in signals:
            adjusted['bull'] = min(1.0, adjusted['bull'] * 1.3)
        
        # Normalize to sum to 1.0
        total = sum(adjusted.values())
        if total > 0:
            adjusted = {k: v / total for k, v in adjusted.items()}
        
        return adjusted
    
    def _estimate_transition_timing(
        self,
        signals: List[str],
        current_duration: int
    ) -> int:
        """Estimate days until regime transition"""
        # Base estimate: regimes last 10-30 days on average
        base_duration = 20
        
        # Adjust based on signals
        if len(signals) >= 3:
            # Multiple strong signals = imminent change
            return max(1, 7 - len(signals))
        elif len(signals) >= 1:
            # Some signals = change within 2 weeks
            return 10
        else:
            # No signals = use typical regime duration
            remaining = base_duration - current_duration
            return max(7, remaining)
    
    def _calculate_forecast_confidence(
        self,
        signals: List[str],
        probability: float,
        regime_confidence: float
    ) -> float:
        """Calculate confidence in regime forecast"""
        # Base confidence from probability
        confidence = probability
        
        # Boost confidence with multiple signals
        signal_boost = min(0.20, len(signals) * 0.05)
        confidence += signal_boost
        
        # Reduce confidence if current regime is uncertain
        if regime_confidence < 0.70:
            confidence *= regime_confidence
        
        return min(0.95, confidence)
    
    def _get_default_regime(self) -> MarketRegime:
        """Get default regime when detection fails"""
        return MarketRegime(
            current_regime='sideways',
            confidence=0.50,
            duration_days=0,
            characteristics={},
            timestamp=datetime.utcnow()
        )
    
    def _get_default_forecast(self) -> RegimeForecast:
        """Get default forecast when forecasting fails"""
        return RegimeForecast(
            predicted_regime='sideways',
            current_regime='unknown',
            probability=0.25,
            expected_transition_days=14,
            confidence=0.30,
            signals=[],
            timestamp=datetime.utcnow()
        )
    
    def get_trading_recommendations(
        self,
        regime: MarketRegime,
        forecast: RegimeForecast
    ) -> Dict[str, Any]:
        """Get trading recommendations based on regime analysis"""
        current = regime.current_regime
        predicted = forecast.predicted_regime
        
        recommendations = {
            'current_regime': current,
            'predicted_regime': predicted,
            'position_sizing': 'normal',
            'strategy_type': 'neutral',
            'risk_adjustment': 1.0,
            'recommended_actions': []
        }
        
        # Adjust strategy based on current regime
        if current == 'bull':
            recommendations['strategy_type'] = 'momentum_long'
            recommendations['position_sizing'] = 'aggressive'
            recommendations['recommended_actions'].append('Focus on strong uptrends')
        elif current == 'bear':
            recommendations['strategy_type'] = 'short_bias'
            recommendations['position_sizing'] = 'defensive'
            recommendations['recommended_actions'].append('Consider short positions')
        elif current == 'volatile':
            recommendations['strategy_type'] = 'range_trading'
            recommendations['position_sizing'] = 'reduced'
            recommendations['risk_adjustment'] = 0.5
            recommendations['recommended_actions'].append('Reduce position sizes')
        elif current == 'sideways':
            recommendations['strategy_type'] = 'mean_reversion'
            recommendations['position_sizing'] = 'normal'
            recommendations['recommended_actions'].append('Buy dips, sell rallies')
        
        # Adjust for predicted regime change
        if predicted != current and forecast.confidence > 0.70:
            recommendations['recommended_actions'].append(
                f'Prepare for transition to {predicted} regime'
            )
            if forecast.expected_transition_days <= 7:
                recommendations['position_sizing'] = 'reduced'
                recommendations['recommended_actions'].append('Reduce exposure ahead of regime change')
        
        return recommendations


# Global instance
_regime_forecaster = None

def get_regime_forecaster() -> MarketRegimeForecaster:
    """Get or create global regime forecaster instance"""
    global _regime_forecaster
    if _regime_forecaster is None:
        _regime_forecaster = MarketRegimeForecaster()
    return _regime_forecaster
