"""
CONTINUOUS LEARNING FOR TRADING PERFORMANCE
==========================================

Advanced machine learning system that continuously improves trading
performance by learning from past trades, market conditions, and outcomes.

Features:
- Real-time performance feedback loops
- Adaptive model updating based on trading results
- Market regime detection and adaptation
- Strategy performance optimization
- Risk-adjusted learning algorithms
- Multi-timeframe learning integration
- Ensemble model improvement
- Performance degradation detection
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from enum import Enum
import uuid
import json
import pickle
import math
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class LearningMode(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    ADAPTIVE = "adaptive"

class PerformanceMetric(Enum):
    PROFIT_LOSS = "profit_loss"
    WIN_RATE = "win_rate"
    SHARPE_RATIO = "sharpe_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    RISK_ADJUSTED_RETURN = "risk_adjusted_return"

class MarketRegime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    LOW_VOLATILITY = "low_volatility"

@dataclass
class TradingOutcome:
    """Trading outcome data structure"""
    trade_id: str
    timestamp: datetime
    symbol: str
    action: str  # buy/sell
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    profit_loss: float
    duration: timedelta
    market_conditions: Dict[str, Any]
    model_confidence: float
    model_version: str
    features_used: Dict[str, Any]
    risk_metrics: Dict[str, Any]

@dataclass
class LearningUpdate:
    """Learning update result"""
    update_id: str
    timestamp: datetime
    model_version: str
    performance_improvement: float
    learning_rate_adjustment: float
    features_importance_changes: Dict[str, float]
    market_regime_adaptations: Dict[str, Any]
    confidence_calibration: float
    update_summary: str

@dataclass
class PerformanceAnalysis:
    """Performance analysis result"""
    analysis_id: str
    timestamp: datetime
    period_analyzed: timedelta
    total_trades: int
    win_rate: float
    profit_loss: float
    sharpe_ratio: float
    max_drawdown: float
    risk_adjusted_return: float
    market_regime_performance: Dict[str, Dict[str, float]]
    model_performance_by_confidence: Dict[str, Dict[str, float]]
    feature_effectiveness: Dict[str, float]
    recommendations: List[str]

class ContinuousLearningEngine:
    """
    CONTINUOUS LEARNING FOR TRADING PERFORMANCE
    Advanced ML system for continuous trading improvement
    """
    
    def __init__(self, learning_mode: LearningMode = LearningMode.BALANCED):
        self.learning_mode = learning_mode
        
        # Learning parameters
        self.learning_rates = {
            LearningMode.CONSERVATIVE: 0.001,
            LearningMode.BALANCED: 0.01,
            LearningMode.AGGRESSIVE: 0.05,
            LearningMode.ADAPTIVE: 0.01  # Will be adjusted dynamically
        }
        
        # Performance tracking
        self.trading_outcomes = deque(maxlen=10000)  # Keep last 10k trades
        self.performance_history = deque(maxlen=1000)  # Keep last 1k performance snapshots
        self.model_versions = {}
        self.feature_importance_history = defaultdict(list)
        
        # Market regime tracking
        self.market_regime_detector = MarketRegimeDetector()
        self.regime_performance = defaultdict(lambda: defaultdict(list))
        
        # Learning state
        self.current_learning_rate = self.learning_rates[learning_mode]
        self.learning_momentum = 0.9
        self.performance_baseline = 0.0
        self.consecutive_improvements = 0
        self.consecutive_degradations = 0
        
        # Model ensemble
        self.ensemble_models = {}
        self.model_weights = {}
        self.model_performance_scores = defaultdict(float)
        
        # Feature learning
        self.feature_effectiveness = defaultdict(float)
        self.feature_usage_count = defaultdict(int)
        self.feature_correlation_matrix = {}
        
        logger.info("🧠 Continuous Learning Engine initialized")
        logger.info(f"📊 Learning mode: {learning_mode.value}")
        logger.info(f"[LIGHTNING] Initial learning rate: {self.current_learning_rate}")
    
    async def record_trading_outcome(self, outcome: TradingOutcome) -> None:
        """Record a trading outcome for learning"""
        
        logger.info(f"📝 Recording trading outcome: {outcome.trade_id}")
        
        # Add to outcomes history
        self.trading_outcomes.append(outcome)
        
        # Update feature effectiveness
        await self._update_feature_effectiveness(outcome)
        
        # Update market regime performance
        await self._update_regime_performance(outcome)
        
        # Update model performance tracking
        await self._update_model_performance(outcome)
        
        # Trigger learning update if conditions are met
        if await self._should_trigger_learning_update():
            learning_update = await self.perform_learning_update()
            logger.info(f"🎯 Learning update triggered: {learning_update.update_id}")
    
    async def perform_learning_update(self) -> LearningUpdate:
        """Perform a comprehensive learning update"""
        
        logger.info("🧠 Performing continuous learning update...")
        
        update_id = f"learning_update_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()
        
        # Analyze recent performance
        performance_analysis = await self._analyze_recent_performance()
        
        # Adjust learning rate based on performance
        learning_rate_adjustment = await self._adjust_learning_rate(performance_analysis)
        
        # Update feature importance
        feature_importance_changes = await self._update_feature_importance()
        
        # Adapt to market regimes
        market_regime_adaptations = await self._adapt_to_market_regimes()
        
        # Calibrate model confidence
        confidence_calibration = await self._calibrate_model_confidence()
        
        # Update ensemble weights
        await self._update_ensemble_weights()
        
        # Calculate performance improvement
        performance_improvement = await self._calculate_performance_improvement()
        
        # Generate update summary
        update_summary = await self._generate_update_summary(
            performance_improvement, learning_rate_adjustment, feature_importance_changes
        )
        
        # Create learning update result
        learning_update = LearningUpdate(
            update_id=update_id,
            timestamp=start_time,
            model_version=f"v{len(self.model_versions) + 1}",
            performance_improvement=performance_improvement,
            learning_rate_adjustment=learning_rate_adjustment,
            features_importance_changes=feature_importance_changes,
            market_regime_adaptations=market_regime_adaptations,
            confidence_calibration=confidence_calibration,
            update_summary=update_summary
        )
        
        # Store model version
        self.model_versions[learning_update.model_version] = {
            'timestamp': start_time,
            'learning_update': learning_update,
            'performance_baseline': self.performance_baseline
        }
        
        logger.info(f"[CHECK] Learning update completed: {performance_improvement:.2%} improvement")
        
        return learning_update
    
    async def _update_feature_effectiveness(self, outcome: TradingOutcome) -> None:
        """Update feature effectiveness based on trading outcome"""
        
        # Calculate outcome score (normalized profit/loss)
        outcome_score = self._normalize_outcome_score(outcome.profit_loss, outcome.risk_metrics)
        
        # Update feature effectiveness
        for feature_name, feature_value in outcome.features_used.items():
            # Weight by model confidence
            weighted_score = outcome_score * outcome.model_confidence
            
            # Update running average
            current_effectiveness = self.feature_effectiveness[feature_name]
            usage_count = self.feature_usage_count[feature_name]
            
            # Exponential moving average
            alpha = 0.1  # Learning rate for feature effectiveness
            new_effectiveness = (1 - alpha) * current_effectiveness + alpha * weighted_score
            
            self.feature_effectiveness[feature_name] = new_effectiveness
            self.feature_usage_count[feature_name] = usage_count + 1
            
            # Track feature importance history
            self.feature_importance_history[feature_name].append(new_effectiveness)
    
    async def _update_regime_performance(self, outcome: TradingOutcome) -> None:
        """Update performance tracking by market regime"""
        
        # Detect current market regime
        current_regime = await self.market_regime_detector.detect_regime(outcome.market_conditions)
        
        # Update regime-specific performance
        regime_key = current_regime.value
        self.regime_performance[regime_key]['profit_loss'].append(outcome.profit_loss)
        self.regime_performance[regime_key]['win_rate'].append(1.0 if outcome.profit_loss > 0 else 0.0)
        self.regime_performance[regime_key]['confidence'].append(outcome.model_confidence)
    
    async def _update_model_performance(self, outcome: TradingOutcome) -> None:
        """Update model-specific performance tracking"""
        
        model_version = outcome.model_version
        outcome_score = self._normalize_outcome_score(outcome.profit_loss, outcome.risk_metrics)
        
        # Update model performance score
        current_score = self.model_performance_scores[model_version]
        alpha = 0.05  # Learning rate for model performance
        new_score = (1 - alpha) * current_score + alpha * outcome_score
        
        self.model_performance_scores[model_version] = new_score
    
    def _normalize_outcome_score(self, profit_loss: float, risk_metrics: Dict[str, Any]) -> float:
        """Normalize trading outcome to a score between -1 and 1"""
        
        # Risk-adjusted return calculation
        risk_factor = risk_metrics.get('risk_factor', 1.0)
        max_risk = risk_metrics.get('max_risk', 1000.0)  # Maximum expected risk
        
        # Normalize profit/loss by risk
        risk_adjusted_return = profit_loss / (risk_factor * max_risk)
        
        # Apply sigmoid to bound between -1 and 1
        normalized_score = 2 / (1 + math.exp(-risk_adjusted_return)) - 1
        
        return normalized_score
    
    async def _should_trigger_learning_update(self) -> bool:
        """Determine if a learning update should be triggered"""

        # Minimum number of trades before learning - REDUCED for faster learning
        if len(self.trading_outcomes) < 20:  # Was 50, now 20 for faster adaptation
            return False

        # Time-based trigger (more frequent updates for faster learning)
        time_triggers = {
            LearningMode.CONSERVATIVE: timedelta(hours=12),  # Was 1 day
            LearningMode.BALANCED: timedelta(hours=3),       # Was 6 hours
            LearningMode.AGGRESSIVE: timedelta(minutes=30),  # Was 1 hour
            LearningMode.ADAPTIVE: timedelta(hours=1)        # Was 3 hours
        }
        
        last_update_time = datetime.now() - timedelta(hours=24)  # Default to 24 hours ago
        if self.model_versions:
            last_version = max(self.model_versions.values(), key=lambda x: x['timestamp'])
            last_update_time = last_version['timestamp']
        
        time_since_update = datetime.now() - last_update_time
        
        if time_since_update >= time_triggers[self.learning_mode]:
            return True
        
        # Performance-based trigger
        recent_outcomes = list(self.trading_outcomes)[-20:]  # Last 20 trades
        if len(recent_outcomes) >= 20:
            recent_performance = sum(outcome.profit_loss for outcome in recent_outcomes)
            
            # Trigger if performance is significantly different from baseline
            performance_change = abs(recent_performance - self.performance_baseline)
            threshold = 0.1 * abs(self.performance_baseline) if self.performance_baseline != 0 else 100.0
            
            if performance_change > threshold:
                return True
        
        return False
    
    async def _analyze_recent_performance(self) -> PerformanceAnalysis:
        """Analyze recent trading performance"""
        
        analysis_id = f"perf_analysis_{uuid.uuid4().hex[:8]}"
        analysis_period = timedelta(days=7)  # Analyze last 7 days
        cutoff_time = datetime.now() - analysis_period
        
        # Filter recent outcomes
        recent_outcomes = [
            outcome for outcome in self.trading_outcomes 
            if outcome.timestamp >= cutoff_time
        ]
        
        if not recent_outcomes:
            # Return empty analysis if no recent data
            return PerformanceAnalysis(
                analysis_id=analysis_id,
                timestamp=datetime.now(),
                period_analyzed=analysis_period,
                total_trades=0,
                win_rate=0.0,
                profit_loss=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                risk_adjusted_return=0.0,
                market_regime_performance={},
                model_performance_by_confidence={},
                feature_effectiveness={},
                recommendations=[]
            )
        
        # Calculate performance metrics
        total_trades = len(recent_outcomes)
        winning_trades = sum(1 for outcome in recent_outcomes if outcome.profit_loss > 0)
        win_rate = winning_trades / total_trades
        
        total_profit_loss = sum(outcome.profit_loss for outcome in recent_outcomes)
        
        # Calculate Sharpe ratio (simplified)
        returns = [outcome.profit_loss for outcome in recent_outcomes]
        avg_return = np.mean(returns)
        std_return = np.std(returns) if len(returns) > 1 else 1.0
        sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
        
        # Calculate max drawdown
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdowns = running_max - cumulative_returns
        max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0.0
        
        # Risk-adjusted return
        total_risk = sum(outcome.risk_metrics.get('risk_factor', 1.0) for outcome in recent_outcomes)
        risk_adjusted_return = total_profit_loss / total_risk if total_risk > 0 else 0.0
        
        # Analyze performance by market regime
        regime_performance = await self._analyze_regime_performance(recent_outcomes)
        
        # Analyze performance by model confidence
        confidence_performance = await self._analyze_confidence_performance(recent_outcomes)
        
        # Calculate current feature effectiveness
        current_feature_effectiveness = dict(self.feature_effectiveness)
        
        # Generate recommendations
        recommendations = await self._generate_performance_recommendations(
            win_rate, sharpe_ratio, max_drawdown, regime_performance
        )
        
        return PerformanceAnalysis(
            analysis_id=analysis_id,
            timestamp=datetime.now(),
            period_analyzed=analysis_period,
            total_trades=total_trades,
            win_rate=win_rate,
            profit_loss=total_profit_loss,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            risk_adjusted_return=risk_adjusted_return,
            market_regime_performance=regime_performance,
            model_performance_by_confidence=confidence_performance,
            feature_effectiveness=current_feature_effectiveness,
            recommendations=recommendations
        )

    async def _analyze_regime_performance(self, outcomes: List[TradingOutcome]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by market regime"""

        regime_stats = defaultdict(lambda: {'trades': 0, 'profit_loss': 0.0, 'wins': 0})

        for outcome in outcomes:
            regime = await self.market_regime_detector.detect_regime(outcome.market_conditions)
            regime_key = regime.value

            regime_stats[regime_key]['trades'] += 1
            regime_stats[regime_key]['profit_loss'] += outcome.profit_loss
            if outcome.profit_loss > 0:
                regime_stats[regime_key]['wins'] += 1

        # Calculate performance metrics for each regime
        regime_performance = {}
        for regime, stats in regime_stats.items():
            if stats['trades'] > 0:
                regime_performance[regime] = {
                    'win_rate': stats['wins'] / stats['trades'],
                    'avg_profit_loss': stats['profit_loss'] / stats['trades'],
                    'total_trades': stats['trades']
                }

        return regime_performance

    async def _analyze_confidence_performance(self, outcomes: List[TradingOutcome]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by model confidence levels"""

        confidence_buckets = {
            'low': (0.0, 0.6),
            'medium': (0.6, 0.8),
            'high': (0.8, 1.0)
        }

        bucket_stats = defaultdict(lambda: {'trades': 0, 'profit_loss': 0.0, 'wins': 0})

        for outcome in outcomes:
            confidence = outcome.model_confidence

            for bucket_name, (min_conf, max_conf) in confidence_buckets.items():
                if min_conf <= confidence < max_conf:
                    bucket_stats[bucket_name]['trades'] += 1
                    bucket_stats[bucket_name]['profit_loss'] += outcome.profit_loss
                    if outcome.profit_loss > 0:
                        bucket_stats[bucket_name]['wins'] += 1
                    break

        # Calculate performance metrics for each confidence bucket
        confidence_performance = {}
        for bucket, stats in bucket_stats.items():
            if stats['trades'] > 0:
                confidence_performance[bucket] = {
                    'win_rate': stats['wins'] / stats['trades'],
                    'avg_profit_loss': stats['profit_loss'] / stats['trades'],
                    'total_trades': stats['trades']
                }

        return confidence_performance

    async def _generate_performance_recommendations(self,
                                                  win_rate: float,
                                                  sharpe_ratio: float,
                                                  max_drawdown: float,
                                                  regime_performance: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate performance improvement recommendations"""

        recommendations = []

        # Win rate recommendations
        if win_rate < 0.4:
            recommendations.append("Consider tightening entry criteria - win rate below 40%")
        elif win_rate > 0.8:
            recommendations.append("Excellent win rate - consider increasing position sizes")

        # Sharpe ratio recommendations
        if sharpe_ratio < 0.5:
            recommendations.append("Low risk-adjusted returns - review risk management")
        elif sharpe_ratio > 2.0:
            recommendations.append("Excellent Sharpe ratio - strategy performing well")

        # Drawdown recommendations
        if max_drawdown > 1000:  # Assuming dollar amounts
            recommendations.append("High maximum drawdown - implement stricter stop losses")

        # Regime-specific recommendations
        best_regime = None
        worst_regime = None
        best_performance = float('-inf')
        worst_performance = float('inf')

        for regime, performance in regime_performance.items():
            avg_pl = performance['avg_profit_loss']
            if avg_pl > best_performance:
                best_performance = avg_pl
                best_regime = regime
            if avg_pl < worst_performance:
                worst_performance = avg_pl
                worst_regime = regime

        if best_regime and worst_regime:
            recommendations.append(f"Best performance in {best_regime} market - consider increasing exposure")
            recommendations.append(f"Poor performance in {worst_regime} market - reduce exposure or adjust strategy")

        return recommendations

    async def _adjust_learning_rate(self, performance_analysis: PerformanceAnalysis) -> float:
        """Adjust learning rate based on performance"""

        # Calculate performance trend
        if performance_analysis.profit_loss > self.performance_baseline:
            self.consecutive_improvements += 1
            self.consecutive_degradations = 0
        else:
            self.consecutive_degradations += 1
            self.consecutive_improvements = 0

        # Adjust learning rate based on performance trend
        if self.learning_mode == LearningMode.ADAPTIVE:
            if self.consecutive_improvements >= 3:
                # Increase learning rate when consistently improving
                self.current_learning_rate = min(0.1, self.current_learning_rate * 1.1)
            elif self.consecutive_degradations >= 3:
                # Decrease learning rate when consistently degrading
                self.current_learning_rate = max(0.0001, self.current_learning_rate * 0.9)

        # Update performance baseline
        alpha = 0.1
        self.performance_baseline = (1 - alpha) * self.performance_baseline + alpha * performance_analysis.profit_loss

        return self.current_learning_rate

    async def _update_feature_importance(self) -> Dict[str, float]:
        """Update feature importance based on recent performance"""

        importance_changes = {}

        for feature_name, effectiveness in self.feature_effectiveness.items():
            # Calculate change in importance
            history = self.feature_importance_history[feature_name]
            if len(history) >= 2:
                recent_avg = np.mean(history[-10:]) if len(history) >= 10 else np.mean(history)
                older_avg = np.mean(history[:-10]) if len(history) >= 20 else np.mean(history[:-1])

                importance_change = recent_avg - older_avg
                importance_changes[feature_name] = importance_change

        return importance_changes

    async def _adapt_to_market_regimes(self) -> Dict[str, Any]:
        """Adapt learning parameters to different market regimes"""

        regime_adaptations = {}

        # Analyze performance by regime
        for regime, performance_data in self.regime_performance.items():
            if performance_data['profit_loss']:
                avg_performance = np.mean(performance_data['profit_loss'])
                win_rate = np.mean(performance_data['win_rate'])

                # Determine adaptation strategy
                if avg_performance > 0 and win_rate > 0.6:
                    adaptation = "increase_exposure"
                elif avg_performance < 0 or win_rate < 0.4:
                    adaptation = "decrease_exposure"
                else:
                    adaptation = "maintain_current"

                regime_adaptations[regime] = {
                    'adaptation_strategy': adaptation,
                    'performance_score': avg_performance,
                    'confidence_adjustment': win_rate - 0.5  # Adjust confidence based on win rate
                }

        return regime_adaptations

    async def _calibrate_model_confidence(self) -> float:
        """Calibrate model confidence based on actual performance"""

        if len(self.trading_outcomes) < 10:
            return 1.0  # No calibration needed with insufficient data

        # Analyze confidence vs actual performance
        confidence_buckets = defaultdict(list)

        for outcome in list(self.trading_outcomes)[-100:]:  # Last 100 trades
            confidence_bucket = int(outcome.model_confidence * 10) / 10  # Round to nearest 0.1
            actual_performance = 1.0 if outcome.profit_loss > 0 else 0.0
            confidence_buckets[confidence_bucket].append(actual_performance)

        # Calculate calibration factor
        total_calibration_error = 0.0
        total_buckets = 0

        for confidence_level, actual_outcomes in confidence_buckets.items():
            if len(actual_outcomes) >= 5:  # Need minimum samples
                actual_success_rate = np.mean(actual_outcomes)
                calibration_error = abs(confidence_level - actual_success_rate)
                total_calibration_error += calibration_error
                total_buckets += 1

        if total_buckets > 0:
            avg_calibration_error = total_calibration_error / total_buckets
            calibration_factor = 1.0 - avg_calibration_error
        else:
            calibration_factor = 1.0

        return calibration_factor

    async def _update_ensemble_weights(self) -> None:
        """Update ensemble model weights based on performance"""

        if not self.model_performance_scores:
            return

        # Calculate softmax weights based on performance scores
        scores = np.array(list(self.model_performance_scores.values()))
        exp_scores = np.exp(scores - np.max(scores))  # Numerical stability
        softmax_weights = exp_scores / np.sum(exp_scores)

        # Update model weights
        for i, model_version in enumerate(self.model_performance_scores.keys()):
            self.model_weights[model_version] = softmax_weights[i]

    async def _calculate_performance_improvement(self) -> float:
        """Calculate overall performance improvement"""

        if len(self.performance_history) < 2:
            return 0.0

        # Compare recent performance to historical average
        recent_performance = np.mean([outcome.profit_loss for outcome in list(self.trading_outcomes)[-50:]])
        historical_performance = np.mean([outcome.profit_loss for outcome in list(self.trading_outcomes)[:-50]])

        if historical_performance != 0:
            improvement = (recent_performance - historical_performance) / abs(historical_performance)
        else:
            improvement = 0.0

        return improvement

    async def _generate_update_summary(self,
                                     performance_improvement: float,
                                     learning_rate_adjustment: float,
                                     feature_importance_changes: Dict[str, float]) -> str:
        """Generate a summary of the learning update"""

        summary = f"Learning Update Summary:\n"
        summary += f"Performance Improvement: {performance_improvement:.2%}\n"
        summary += f"Learning Rate: {learning_rate_adjustment:.4f}\n"

        if feature_importance_changes:
            summary += f"Top Feature Changes:\n"
            sorted_changes = sorted(feature_importance_changes.items(), key=lambda x: abs(x[1]), reverse=True)
            for feature, change in sorted_changes[:5]:
                direction = "↑" if change > 0 else "↓"
                summary += f"  {feature}: {direction} {abs(change):.3f}\n"

        summary += f"Total Trades Analyzed: {len(self.trading_outcomes)}\n"
        summary += f"Model Versions: {len(self.model_versions)}\n"

        return summary

    async def get_learning_report(self) -> Dict[str, Any]:
        """Generate comprehensive learning performance report"""

        # Calculate overall statistics
        total_trades = len(self.trading_outcomes)
        if total_trades == 0:
            return {'error': 'No trading data available'}

        recent_outcomes = list(self.trading_outcomes)[-100:]  # Last 100 trades
        overall_profit_loss = sum(outcome.profit_loss for outcome in self.trading_outcomes)
        recent_profit_loss = sum(outcome.profit_loss for outcome in recent_outcomes)

        win_rate = sum(1 for outcome in recent_outcomes if outcome.profit_loss > 0) / len(recent_outcomes)

        # Feature effectiveness summary
        top_features = sorted(self.feature_effectiveness.items(), key=lambda x: x[1], reverse=True)[:10]

        # Model performance summary
        model_performance_summary = dict(self.model_performance_scores)

        # Learning statistics
        learning_stats = {
            'current_learning_rate': self.current_learning_rate,
            'consecutive_improvements': self.consecutive_improvements,
            'consecutive_degradations': self.consecutive_degradations,
            'performance_baseline': self.performance_baseline,
            'total_model_versions': len(self.model_versions)
        }

        return {
            'learning_performance': {
                'total_trades_processed': total_trades,
                'overall_profit_loss': overall_profit_loss,
                'recent_profit_loss': recent_profit_loss,
                'recent_win_rate': win_rate,
                'performance_improvement_trend': recent_profit_loss - (overall_profit_loss - recent_profit_loss)
            },
            'feature_learning': {
                'top_effective_features': top_features,
                'total_features_tracked': len(self.feature_effectiveness),
                'feature_usage_distribution': dict(self.feature_usage_count)
            },
            'model_ensemble': {
                'model_performance_scores': model_performance_summary,
                'model_weights': dict(self.model_weights),
                'active_models': len(self.ensemble_models)
            },
            'learning_statistics': learning_stats,
            'market_regime_performance': {
                regime: {
                    'avg_profit_loss': np.mean(data['profit_loss']) if data['profit_loss'] else 0.0,
                    'avg_win_rate': np.mean(data['win_rate']) if data['win_rate'] else 0.0,
                    'trade_count': len(data['profit_loss'])
                }
                for regime, data in self.regime_performance.items()
            },
            'report_timestamp': datetime.now().isoformat(),
            'report_type': 'continuous_learning_performance'
        }


class MarketRegimeDetector:
    """Market regime detection for adaptive learning"""

    def __init__(self):
        self.regime_indicators = {
            'volatility_threshold': 0.02,
            'trend_threshold': 0.05,
            'volume_threshold': 1.5
        }

    async def detect_regime(self, market_conditions: Dict[str, Any]) -> MarketRegime:
        """Detect current market regime"""

        # Extract market indicators
        volatility = market_conditions.get('volatility', 0.01)
        trend_strength = market_conditions.get('trend_strength', 0.0)
        volume_ratio = market_conditions.get('volume_ratio', 1.0)
        price_change = market_conditions.get('price_change', 0.0)

        # Determine regime based on indicators
        if volatility > self.regime_indicators['volatility_threshold'] * 2:
            return MarketRegime.VOLATILE
        elif volatility < self.regime_indicators['volatility_threshold'] * 0.5:
            return MarketRegime.LOW_VOLATILITY
        elif trend_strength > self.regime_indicators['trend_threshold']:
            if price_change > 0:
                return MarketRegime.BULL
            else:
                return MarketRegime.BEAR
        else:
            return MarketRegime.SIDEWAYS


# Example usage and testing
async def test_continuous_learning_engine():
    """Test the continuous learning engine"""

    # Initialize learning engine
    learning_engine = ContinuousLearningEngine(LearningMode.BALANCED)

    # Simulate trading outcomes
    for i in range(100):
        outcome = TradingOutcome(
            trade_id=f"trade_{i:03d}",
            timestamp=datetime.now() - timedelta(hours=i),
            symbol="BTCUSD",
            action="buy" if i % 2 == 0 else "sell",
            entry_price=45000.0 + np.random.normal(0, 1000),
            exit_price=45000.0 + np.random.normal(100, 1000),
            quantity=1.0,
            profit_loss=np.random.normal(50, 200),  # Random profit/loss
            duration=timedelta(minutes=np.random.randint(5, 120)),
            market_conditions={
                'volatility': np.random.uniform(0.005, 0.05),
                'trend_strength': np.random.uniform(-0.1, 0.1),
                'volume_ratio': np.random.uniform(0.5, 2.0),
                'price_change': np.random.uniform(-0.02, 0.02)
            },
            model_confidence=np.random.uniform(0.5, 0.95),
            model_version="v1.0",
            features_used={
                'rsi': np.random.uniform(20, 80),
                'macd': np.random.uniform(-1, 1),
                'volume_sma': np.random.uniform(0.8, 1.2),
                'price_momentum': np.random.uniform(-0.05, 0.05)
            },
            risk_metrics={
                'risk_factor': np.random.uniform(0.5, 2.0),
                'max_risk': 1000.0
            }
        )

        await learning_engine.record_trading_outcome(outcome)

    # Perform learning update
    learning_update = await learning_engine.perform_learning_update()

    print(f"\n🧠 Continuous Learning Results:")
    print(f"📊 Performance Improvement: {learning_update.performance_improvement:.2%}")
    print(f"[LIGHTNING] Learning Rate: {learning_update.learning_rate_adjustment:.4f}")
    print(f"🎯 Confidence Calibration: {learning_update.confidence_calibration:.3f}")
    print(f"📈 Model Version: {learning_update.model_version}")

    print(f"\n🔍 Feature Importance Changes:")
    for feature, change in learning_update.features_importance_changes.items():
        direction = "↑" if change > 0 else "↓"
        print(f"   {feature}: {direction} {abs(change):.3f}")

    # Generate learning report
    learning_report = await learning_engine.get_learning_report()
    print(f"\n📈 Learning Report:")
    print(f"   Total Trades: {learning_report['learning_performance']['total_trades_processed']}")
    print(f"   Recent Win Rate: {learning_report['learning_performance']['recent_win_rate']:.1%}")
    print(f"   Top Features: {[f[0] for f in learning_report['feature_learning']['top_effective_features'][:3]]}")
    print(f"   Active Models: {learning_report['model_ensemble']['active_models']}")


if __name__ == "__main__":
    asyncio.run(test_continuous_learning_engine())
