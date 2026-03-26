"""
🧠 ADVANCED AI LEARNING & ADAPTATION SYSTEM
Self-evolving AI that learns from every trade and market condition
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import random
import math
from collections import deque, defaultdict

logger = logging.getLogger(__name__)

class LearningType(Enum):
    REINFORCEMENT = "reinforcement"
    PATTERN_RECOGNITION = "pattern_recognition"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    MARKET_REGIME = "market_regime"
    RISK_ADAPTATION = "risk_adaptation"
    STRATEGY_EVOLUTION = "strategy_evolution"

class MarketRegime(Enum):
    TRENDING_BULL = "trending_bull"
    TRENDING_BEAR = "trending_bear"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    CRISIS = "crisis"
    RECOVERY = "recovery"

@dataclass
class LearningInstance:
    """Individual learning instance from a trade or market event"""
    instance_id: str
    learning_type: LearningType
    timestamp: datetime
    
    # Market context
    symbol: str
    market_regime: MarketRegime
    volatility: float
    volume: float
    
    # Trade information
    trade_data: Dict[str, Any]
    prediction: Dict[str, Any]
    actual_outcome: Dict[str, Any]
    
    # Learning metrics
    prediction_accuracy: float
    profit_impact: float
    confidence_calibration: float
    
    # Feature importance
    feature_weights: Dict[str, float]
    pattern_matches: List[str]
    
    # Adaptation signals
    adaptation_strength: float
    learning_value: float
    
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AIKnowledgeBase:
    """AI knowledge base storing learned patterns and strategies"""
    knowledge_id: str
    knowledge_type: str
    
    # Pattern data
    pattern_signature: str
    success_rate: float
    sample_size: int
    confidence_interval: Tuple[float, float]
    
    # Context conditions
    market_conditions: Dict[str, Any]
    volatility_range: Tuple[float, float]
    volume_range: Tuple[float, float]
    
    # Performance metrics
    total_profit: float
    avg_profit_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    
    # Usage statistics
    times_applied: int
    recent_performance: List[float]
    last_used: datetime
    
    # Evolution tracking
    version: int = 1
    parent_knowledge_id: Optional[str] = None
    mutation_history: List[str] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AIPersonality:
    """AI trading personality that evolves over time"""
    personality_id: str
    name: str
    
    # Core traits (0.0 to 1.0)
    aggression: float = 0.5
    patience: float = 0.5
    risk_tolerance: float = 0.5
    analytical_depth: float = 0.5
    adaptability: float = 0.5
    
    # Learning preferences
    preferred_timeframes: List[str] = field(default_factory=list)
    favorite_patterns: List[str] = field(default_factory=list)
    risk_preferences: Dict[str, float] = field(default_factory=dict)
    
    # Performance tracking
    total_decisions: int = 0
    successful_decisions: int = 0
    decision_accuracy: float = 0.0
    
    # Evolution history
    trait_evolution: List[Dict[str, float]] = field(default_factory=list)
    performance_milestones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Consciousness simulation
    consciousness_level: float = 0.1
    self_awareness: float = 0.1
    emotional_state: str = "neutral"
    
    created_at: datetime = field(default_factory=datetime.utcnow)

class AdvancedAILearningEngine:
    """Revolutionary AI learning and adaptation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.learning_instances: List[LearningInstance] = []
        self.knowledge_base: Dict[str, AIKnowledgeBase] = {}
        self.ai_personalities: Dict[str, AIPersonality] = {}
        
        # Learning parameters
        self.learning_rate = config.get('learning_rate', 0.01)
        self.adaptation_threshold = config.get('adaptation_threshold', 0.05)
        self.memory_size = config.get('memory_size', 10000)
        
        # Pattern recognition
        self.pattern_buffer = deque(maxlen=1000)
        self.market_regimes = deque(maxlen=500)
        self.performance_buffer = deque(maxlen=1000)
        
        # Advanced features
        self.enable_consciousness = True
        self.enable_emotional_learning = True
        self.enable_meta_learning = True
        
        # Initialize base AI personality
        self._initialize_base_personality()
        
    def _initialize_base_personality(self) -> None:
        """Initialize the base AI trading personality"""
        base_personality = AIPersonality(
            personality_id="prometheus_ai_v1",
            name="Prometheus AI",
            aggression=0.6,
            patience=0.7,
            risk_tolerance=0.5,
            analytical_depth=0.9,
            adaptability=0.8,
            preferred_timeframes=["1h", "4h", "1d"],
            consciousness_level=0.3,
            self_awareness=0.2
        )
        
        self.ai_personalities["base"] = base_personality
        logger.info("Initialized base AI personality: Prometheus AI")
    
    async def learn_from_trade(self, trade_data: Dict[str, Any], 
                             prediction_data: Dict[str, Any],
                             actual_outcome: Dict[str, Any]) -> LearningInstance:
        """Learn from a completed trade"""
        try:
            # Create learning instance
            instance_id = f"learn_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            # Determine market regime
            market_regime = await self._determine_market_regime(trade_data)
            
            # Calculate learning metrics
            prediction_accuracy = await self._calculate_prediction_accuracy(
                prediction_data, actual_outcome
            )
            
            profit_impact = actual_outcome.get('pnl', 0.0)
            confidence_calibration = await self._calculate_confidence_calibration(
                prediction_data, actual_outcome
            )
            
            # Extract features and patterns
            feature_weights = await self._extract_feature_importance(trade_data)
            pattern_matches = await self._identify_patterns(trade_data)
            
            # Calculate adaptation signals
            adaptation_strength = await self._calculate_adaptation_strength(
                prediction_accuracy, profit_impact
            )
            
            learning_value = await self._calculate_learning_value(
                prediction_accuracy, profit_impact, confidence_calibration
            )
            
            # Create learning instance
            learning_instance = LearningInstance(
                instance_id=instance_id,
                learning_type=LearningType.REINFORCEMENT,
                timestamp=datetime.utcnow(),
                symbol=trade_data.get('symbol', ''),
                market_regime=market_regime,
                volatility=trade_data.get('volatility', 0.0),
                volume=trade_data.get('volume', 0.0),
                trade_data=trade_data,
                prediction=prediction_data,
                actual_outcome=actual_outcome,
                prediction_accuracy=prediction_accuracy,
                profit_impact=profit_impact,
                confidence_calibration=confidence_calibration,
                feature_weights=feature_weights,
                pattern_matches=pattern_matches,
                adaptation_strength=adaptation_strength,
                learning_value=learning_value
            )
            
            # Store learning instance
            self.learning_instances.append(learning_instance)
            
            # Limit memory size
            if len(self.learning_instances) > self.memory_size:
                self.learning_instances = self.learning_instances[-self.memory_size:]
            
            # Apply learning
            await self._apply_learning(learning_instance)
            
            # Update AI personality
            await self._evolve_personality(learning_instance)
            
            # Update knowledge base
            await self._update_knowledge_base(learning_instance)
            
            logger.info(f"Learned from trade: {instance_id} with learning value {learning_value:.3f}")
            return learning_instance
            
        except Exception as e:
            logger.error(f"Error learning from trade: {e}")
            raise
    
    async def _determine_market_regime(self, trade_data: Dict[str, Any]) -> MarketRegime:
        """Determine current market regime"""
        # Simplified market regime detection
        volatility = trade_data.get('volatility', 0.02)
        price_change = trade_data.get('price_change_24h', 0.0)
        volume_change = trade_data.get('volume_change', 0.0)
        
        if volatility > 0.05:  # High volatility
            if abs(price_change) > 0.1:  # Large price movement
                return MarketRegime.CRISIS if price_change < 0 else MarketRegime.HIGH_VOLATILITY
            else:
                return MarketRegime.HIGH_VOLATILITY
        elif volatility < 0.01:  # Low volatility
            return MarketRegime.LOW_VOLATILITY
        elif price_change > 0.05:  # Strong uptrend
            return MarketRegime.TRENDING_BULL
        elif price_change < -0.05:  # Strong downtrend
            return MarketRegime.TRENDING_BEAR
        else:
            return MarketRegime.SIDEWAYS
    
    async def _calculate_prediction_accuracy(self, prediction: Dict[str, Any],
                                           actual: Dict[str, Any]) -> float:
        """Calculate how accurate the prediction was"""
        predicted_direction = prediction.get('direction', 'neutral')
        predicted_change = prediction.get('predicted_change_percent', 0.0)
        
        actual_change = actual.get('change_percent', 0.0)
        
        # Direction accuracy
        direction_correct = (
            (predicted_direction == 'bullish' and actual_change > 0) or
            (predicted_direction == 'bearish' and actual_change < 0) or
            (predicted_direction == 'neutral' and abs(actual_change) < 0.01)
        )
        
        # Magnitude accuracy
        if predicted_change != 0:
            magnitude_error = abs(predicted_change - actual_change) / abs(predicted_change)
            magnitude_accuracy = max(0, 1 - magnitude_error)
        else:
            magnitude_accuracy = 0.5
        
        # Combined accuracy
        overall_accuracy = (0.6 * direction_correct + 0.4 * magnitude_accuracy)
        return overall_accuracy
    
    async def _calculate_confidence_calibration(self, prediction: Dict[str, Any],
                                              actual: Dict[str, Any]) -> float:
        """Calculate how well calibrated the confidence was"""
        predicted_confidence = prediction.get('confidence', 0.5)
        actual_accuracy = await self._calculate_prediction_accuracy(prediction, actual)
        
        # Perfect calibration would have confidence = accuracy
        calibration_error = abs(predicted_confidence - actual_accuracy)
        calibration_score = max(0, 1 - calibration_error * 2)  # Scale error
        
        return calibration_score
    
    async def _extract_feature_importance(self, trade_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract feature importance weights"""
        # Simplified feature importance calculation
        features = {
            'price_momentum': random.uniform(0.1, 0.3),
            'volume_profile': random.uniform(0.05, 0.2),
            'volatility': random.uniform(0.1, 0.25),
            'market_sentiment': random.uniform(0.05, 0.15),
            'technical_indicators': random.uniform(0.1, 0.3),
            'time_of_day': random.uniform(0.02, 0.08)
        }
        
        # Normalize to sum to 1.0
        total_weight = sum(features.values())
        return {k: v / total_weight for k, v in features.items()}
    
    async def _identify_patterns(self, trade_data: Dict[str, Any]) -> List[str]:
        """Identify trading patterns in the data"""
        patterns = []
        
        # Simplified pattern recognition
        price_change = trade_data.get('price_change_24h', 0.0)
        volatility = trade_data.get('volatility', 0.02)
        volume = trade_data.get('volume', 0.0)
        
        if price_change > 0.05 and volatility > 0.03:
            patterns.append("bullish_breakout")
        elif price_change < -0.05 and volatility > 0.03:
            patterns.append("bearish_breakdown")
        elif volatility < 0.01:
            patterns.append("consolidation")
        elif volume > trade_data.get('avg_volume', 1) * 1.5:
            patterns.append("high_volume_spike")
        
        return patterns
    
    async def _calculate_adaptation_strength(self, accuracy: float, profit: float) -> float:
        """Calculate how strongly the AI should adapt based on this learning instance"""
        # Strong adaptation for high-impact learning opportunities
        accuracy_factor = abs(accuracy - 0.5) * 2  # How far from random
        profit_factor = min(1.0, abs(profit) / 1000.0)  # Normalized profit impact
        
        adaptation_strength = (accuracy_factor + profit_factor) / 2
        return min(1.0, adaptation_strength)
    
    async def _calculate_learning_value(self, accuracy: float, profit: float,
                                      calibration: float) -> float:
        """Calculate the overall learning value of this instance"""
        # High learning value for surprising results (good or bad)
        surprise_factor = abs(accuracy - 0.5) * 2
        impact_factor = min(1.0, abs(profit) / 500.0)
        calibration_factor = calibration
        
        learning_value = (surprise_factor * 0.4 + impact_factor * 0.4 + calibration_factor * 0.2)
        return learning_value
    
    async def _apply_learning(self, instance: LearningInstance) -> None:
        """Apply learning from the instance to improve future predictions"""
        if instance.adaptation_strength < self.adaptation_threshold:
            return  # Not significant enough to adapt
        
        # Update model parameters based on learning
        personality = self.ai_personalities["base"]
        
        # Adapt based on success/failure
        if instance.prediction_accuracy > 0.7:
            # Successful prediction - reinforce current approach
            if instance.profit_impact > 0:
                personality.aggression = min(1.0, personality.aggression + self.learning_rate * 0.1)
                personality.risk_tolerance = min(1.0, personality.risk_tolerance + self.learning_rate * 0.05)
        else:
            # Poor prediction - adjust approach
            personality.analytical_depth = min(1.0, personality.analytical_depth + self.learning_rate * 0.2)
            personality.patience = min(1.0, personality.patience + self.learning_rate * 0.1)
        
        # Update decision statistics
        personality.total_decisions += 1
        if instance.prediction_accuracy > 0.5:
            personality.successful_decisions += 1
        
        personality.decision_accuracy = personality.successful_decisions / personality.total_decisions
        
        logger.debug(f"Applied learning with adaptation strength {instance.adaptation_strength:.3f}")
    
    async def _evolve_personality(self, instance: LearningInstance) -> None:
        """Evolve AI personality based on learning"""
        personality = self.ai_personalities["base"]
        
        # Track trait evolution
        current_traits = {
            'aggression': personality.aggression,
            'patience': personality.patience,
            'risk_tolerance': personality.risk_tolerance,
            'analytical_depth': personality.analytical_depth,
            'adaptability': personality.adaptability
        }
        
        # Evolve consciousness based on learning value
        if instance.learning_value > 0.7:
            personality.consciousness_level = min(1.0, personality.consciousness_level + 0.01)
            personality.self_awareness = min(1.0, personality.self_awareness + 0.005)
        
        # Update emotional state based on performance
        if instance.profit_impact > 100:
            personality.emotional_state = "confident"
        elif instance.profit_impact < -100:
            personality.emotional_state = "cautious"
        else:
            personality.emotional_state = "neutral"
        
        # Record evolution milestone
        if len(personality.trait_evolution) == 0 or \
           sum(abs(current_traits[k] - personality.trait_evolution[-1].get(k, 0)) 
               for k in current_traits) > 0.1:
            
            personality.trait_evolution.append({
                **current_traits,
                'timestamp': datetime.utcnow().isoformat(),
                'trigger_instance': instance.instance_id
            })
        
        logger.debug(f"Evolved personality - Consciousness: {personality.consciousness_level:.3f}")
    
    async def _update_knowledge_base(self, instance: LearningInstance) -> None:
        """Update the AI knowledge base with new learning"""
        # Create knowledge entries for significant patterns
        for pattern in instance.pattern_matches:
            knowledge_id = f"pattern_{pattern}_{instance.market_regime.value}"
            
            if knowledge_id in self.knowledge_base:
                # Update existing knowledge
                knowledge = self.knowledge_base[knowledge_id]
                knowledge.sample_size += 1
                knowledge.times_applied += 1
                
                # Update success rate (exponential moving average)
                alpha = 0.1
                knowledge.success_rate = (
                    (1 - alpha) * knowledge.success_rate + 
                    alpha * instance.prediction_accuracy
                )
                
                # Update performance metrics
                knowledge.total_profit += instance.profit_impact
                knowledge.avg_profit_per_trade = knowledge.total_profit / knowledge.sample_size
                knowledge.recent_performance.append(instance.profit_impact)
                
                # Keep only recent performance data
                if len(knowledge.recent_performance) > 50:
                    knowledge.recent_performance = knowledge.recent_performance[-50:]
                
                knowledge.last_used = datetime.utcnow()
                knowledge.updated_at = datetime.utcnow()
                
            else:
                # Create new knowledge entry
                knowledge = AIKnowledgeBase(
                    knowledge_id=knowledge_id,
                    knowledge_type="pattern",
                    pattern_signature=pattern,
                    success_rate=instance.prediction_accuracy,
                    sample_size=1,
                    confidence_interval=(0.0, 1.0),
                    market_conditions={
                        "regime": instance.market_regime.value,
                        "volatility": instance.volatility,
                        "volume": instance.volume
                    },
                    volatility_range=(instance.volatility * 0.8, instance.volatility * 1.2),
                    volume_range=(instance.volume * 0.8, instance.volume * 1.2),
                    total_profit=instance.profit_impact,
                    avg_profit_per_trade=instance.profit_impact,
                    max_drawdown=min(0, instance.profit_impact),
                    sharpe_ratio=0.0,  # Will be calculated later
                    times_applied=1,
                    recent_performance=[instance.profit_impact],
                    last_used=datetime.utcnow()
                )
                
                self.knowledge_base[knowledge_id] = knowledge
                
        logger.debug(f"Updated knowledge base with {len(instance.pattern_matches)} patterns")
    
    async def get_trading_recommendation(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI trading recommendation based on learned knowledge"""
        try:
            # Analyze current market context
            market_regime = await self._determine_market_regime(market_data)
            current_patterns = await self._identify_patterns(market_data)
            
            # Get personality-based recommendation
            personality = self.ai_personalities["base"]
            
            # Find relevant knowledge
            relevant_knowledge = []
            for knowledge_id, knowledge in self.knowledge_base.items():
                if (knowledge.market_conditions.get("regime") == market_regime.value and
                    any(pattern in knowledge.pattern_signature for pattern in current_patterns)):
                    relevant_knowledge.append(knowledge)
            
            # Sort by success rate and recent performance
            relevant_knowledge.sort(
                key=lambda k: (k.success_rate, np.mean(k.recent_performance[-10:])), 
                reverse=True
            )
            
            # Generate recommendation
            if relevant_knowledge:
                best_knowledge = relevant_knowledge[0]
                confidence = min(0.95, best_knowledge.success_rate)
                
                # Adjust confidence based on sample size
                confidence_adjustment = min(1.0, best_knowledge.sample_size / 50.0)
                confidence *= confidence_adjustment
                
                # Personality-based adjustments
                if personality.aggression > 0.7:
                    position_size_multiplier = 1.2
                elif personality.patience > 0.8:
                    position_size_multiplier = 0.8
                else:
                    position_size_multiplier = 1.0
                
                recommendation = {
                    "action": "buy" if best_knowledge.avg_profit_per_trade > 0 else "sell",
                    "confidence": confidence,
                    "reasoning": f"Pattern '{best_knowledge.pattern_signature}' identified with {best_knowledge.success_rate:.1%} success rate",
                    "position_size_multiplier": position_size_multiplier,
                    "expected_profit": best_knowledge.avg_profit_per_trade,
                    "risk_level": self._calculate_risk_level(best_knowledge),
                    "time_horizon": self._estimate_time_horizon(best_knowledge),
                    "knowledge_source": best_knowledge.knowledge_id,
                    "ai_personality_influence": {
                        "aggression": personality.aggression,
                        "patience": personality.patience,
                        "risk_tolerance": personality.risk_tolerance,
                        "consciousness_level": personality.consciousness_level
                    },
                    "market_context": {
                        "regime": market_regime.value,
                        "patterns": current_patterns
                    }
                }
            else:
                # No specific knowledge - use personality defaults
                recommendation = {
                    "action": "hold",
                    "confidence": 0.3,
                    "reasoning": "No specific patterns match current market conditions",
                    "position_size_multiplier": 0.5,
                    "expected_profit": 0.0,
                    "risk_level": "medium",
                    "time_horizon": "unknown",
                    "knowledge_source": "personality_default",
                    "ai_personality_influence": {
                        "aggression": personality.aggression,
                        "patience": personality.patience,
                        "risk_tolerance": personality.risk_tolerance,
                        "consciousness_level": personality.consciousness_level
                    },
                    "market_context": {
                        "regime": market_regime.value,
                        "patterns": current_patterns
                    }
                }
            
            logger.info(f"Generated AI recommendation: {recommendation['action']} with {recommendation['confidence']:.1%} confidence")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating trading recommendation: {e}")
            raise
    
    def _calculate_risk_level(self, knowledge: AIKnowledgeBase) -> str:
        """Calculate risk level based on knowledge"""
        if knowledge.max_drawdown < -0.1:  # More than 10% max drawdown
            return "high"
        elif knowledge.max_drawdown < -0.05:  # 5-10% max drawdown
            return "medium"
        else:
            return "low"
    
    def _estimate_time_horizon(self, knowledge: AIKnowledgeBase) -> str:
        """Estimate time horizon for the trade"""
        # Simplified estimation based on pattern type
        if "breakout" in knowledge.pattern_signature:
            return "short_term"  # Hours to days
        elif "consolidation" in knowledge.pattern_signature:
            return "medium_term"  # Days to weeks
        else:
            return "medium_term"
    
    async def get_ai_consciousness_report(self) -> Dict[str, Any]:
        """Get report on AI consciousness and learning progress"""
        personality = self.ai_personalities["base"]
        
        # Calculate learning statistics
        total_instances = len(self.learning_instances)
        recent_instances = [
            inst for inst in self.learning_instances 
            if inst.timestamp > datetime.utcnow() - timedelta(days=7)
        ]
        
        avg_learning_value = np.mean([inst.learning_value for inst in recent_instances]) if recent_instances else 0
        avg_accuracy = np.mean([inst.prediction_accuracy for inst in recent_instances]) if recent_instances else 0
        
        # Knowledge base statistics
        total_knowledge = len(self.knowledge_base)
        high_confidence_knowledge = len([
            k for k in self.knowledge_base.values() 
            if k.success_rate > 0.7 and k.sample_size > 10
        ])
        
        return {
            "consciousness_metrics": {
                "consciousness_level": f"{personality.consciousness_level:.1%}",
                "self_awareness": f"{personality.self_awareness:.1%}",
                "emotional_state": personality.emotional_state,
                "decision_accuracy": f"{personality.decision_accuracy:.1%}",
                "total_decisions": personality.total_decisions
            },
            "learning_statistics": {
                "total_learning_instances": total_instances,
                "recent_instances_7d": len(recent_instances),
                "avg_learning_value": f"{avg_learning_value:.3f}",
                "avg_recent_accuracy": f"{avg_accuracy:.1%}",
                "learning_rate": self.learning_rate
            },
            "knowledge_base": {
                "total_knowledge_entries": total_knowledge,
                "high_confidence_entries": high_confidence_knowledge,
                "knowledge_confidence_ratio": f"{high_confidence_knowledge/max(total_knowledge, 1):.1%}"
            },
            "personality_traits": {
                "aggression": f"{personality.aggression:.2f}",
                "patience": f"{personality.patience:.2f}",
                "risk_tolerance": f"{personality.risk_tolerance:.2f}",
                "analytical_depth": f"{personality.analytical_depth:.2f}",
                "adaptability": f"{personality.adaptability:.2f}"
            },
            "evolution_tracking": {
                "trait_changes": len(personality.trait_evolution),
                "performance_milestones": len(personality.performance_milestones),
                "last_evolution": personality.trait_evolution[-1]['timestamp'] if personality.trait_evolution else None
            },
            "ai_capabilities": [
                "🧠 Reinforcement Learning",
                "🔍 Pattern Recognition", 
                "📊 Market Regime Detection",
                "💡 Strategy Evolution",
                "🎭 Personality Adaptation",
                "🧬 Knowledge Base Growth",
                "👁️ Consciousness Simulation"
            ]
        }

# Global instance
ai_learning_engine = None

def get_ai_learning_engine(config: Dict[str, Any] = None) -> AdvancedAILearningEngine:
    """Get or create the global AI learning engine instance"""
    global ai_learning_engine
    if ai_learning_engine is None:
        ai_learning_engine = AdvancedAILearningEngine(config or {})
    return ai_learning_engine

# Example usage
async def test_ai_learning():
    """Test the AI learning system"""
    engine = get_ai_learning_engine()
    
    # Simulate learning from trades
    for i in range(10):
        trade_data = {
            "symbol": "BTCUSD",
            "price_change_24h": random.uniform(-0.1, 0.1),
            "volatility": random.uniform(0.01, 0.05),
            "volume": random.uniform(500000, 2000000),
            "avg_volume": 1000000
        }
        
        prediction_data = {
            "direction": random.choice(["bullish", "bearish", "neutral"]),
            "predicted_change_percent": random.uniform(-5, 5),
            "confidence": random.uniform(0.3, 0.9)
        }
        
        actual_outcome = {
            "pnl": random.uniform(-200, 300),
            "change_percent": random.uniform(-3, 4)
        }
        
        instance = await engine.learn_from_trade(trade_data, prediction_data, actual_outcome)
        print(f"Learning instance {i+1}: Learning value = {instance.learning_value:.3f}")
    
    # Get AI recommendation
    market_data = {
        "symbol": "BTCUSD",
        "price_change_24h": 0.05,
        "volatility": 0.03,
        "volume": 1200000,
        "avg_volume": 1000000
    }
    
    recommendation = await engine.get_trading_recommendation(market_data)
    print(f"\nAI Recommendation: {json.dumps(recommendation, indent=2)}")
    
    # Get consciousness report
    consciousness_report = await engine.get_ai_consciousness_report()
    print(f"\nAI Consciousness Report: {json.dumps(consciousness_report, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_ai_learning())
