"""
PROMETHEUS Universal Reasoning Engine v2.0
Enhanced multi-model ensemble with weighted synthesis
Combines HRM, GPT-OSS, DeepSeek, Quantum, and Memory systems
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ReasoningResult:
    """Result from a single reasoning source"""
    source: str
    recommendation: str
    confidence: float
    reasoning: str
    risk_score: float
    position_size: float
    timestamp: datetime
    metadata: Dict[str, Any]

class UniversalReasoningEngineV2:
    """
    Enhanced Universal Reasoning Engine
    Synthesizes decisions from multiple AI systems with intelligent weighting
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Enhanced weighting system - adaptive based on performance
        self.weights = {
            'hrm': 0.30,           # Hierarchical reasoning
            'gpt_oss': 0.25,       # Language understanding
            'deepseek': 0.20,      # Logical reasoning
            'quantum': 0.15,       # Portfolio optimization
            'memory': 0.10         # Historical insights
        }
        
        # Performance tracking for adaptive weighting
        self.performance_history = {
            'hrm': [],
            'gpt_oss': [],
            'deepseek': [],
            'quantum': [],
            'memory': []
        }
        
        # Consensus thresholds
        self.strong_consensus_threshold = 0.80
        self.weak_consensus_threshold = 0.60
        
        logger.info("✅ Universal Reasoning Engine v2.0 initialized")
    
    async def synthesize_decision(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize trading decision from all reasoning sources
        
        Returns:
            Comprehensive trading recommendation with confidence metrics
        """
        try:
            # Gather reasoning from all sources in parallel
            reasoning_results = await self._gather_all_reasoning(
                symbol, market_data, technical_indicators
            )
            
            # Calculate weighted consensus
            consensus = self._calculate_weighted_consensus(reasoning_results)
            
            # Determine final action
            final_decision = self._determine_final_action(
                consensus, reasoning_results
            )
            
            # Generate comprehensive recommendation
            recommendation = {
                'symbol': symbol,
                'action': final_decision['action'],
                'confidence': final_decision['confidence'],
                'position_size': final_decision['position_size'],
                'entry_price': market_data.get('price', 0),
                'stop_loss': final_decision['stop_loss'],
                'take_profit': final_decision['take_profit'],
                'risk_score': final_decision['risk_score'],
                'consensus_strength': consensus['strength'],
                'reasoning_breakdown': self._format_reasoning_breakdown(reasoning_results),
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': {
                    'sources_used': len(reasoning_results),
                    'weights_applied': self.weights.copy(),
                    'consensus_metrics': consensus
                }
            }
            
            logger.info(f"🎯 Synthesized decision for {symbol}: {final_decision['action']} "
                       f"(confidence: {final_decision['confidence']:.2%}, "
                       f"consensus: {consensus['strength']})")
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error synthesizing decision: {e}")
            return self._get_safe_fallback_decision(symbol, market_data)
    
    async def _gather_all_reasoning(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> List[ReasoningResult]:
        """Gather reasoning from all sources in parallel"""
        tasks = []
        
        # HRM Reasoning
        if self._is_source_enabled('hrm'):
            tasks.append(self._get_hrm_reasoning(symbol, market_data, technical_indicators))
        
        # GPT-OSS Reasoning
        if self._is_source_enabled('gpt_oss'):
            tasks.append(self._get_gpt_oss_reasoning(symbol, market_data, technical_indicators))
        
        # DeepSeek Reasoning
        if self._is_source_enabled('deepseek'):
            tasks.append(self._get_deepseek_reasoning(symbol, market_data, technical_indicators))
        
        # Quantum Optimization
        if self._is_source_enabled('quantum'):
            tasks.append(self._get_quantum_reasoning(symbol, market_data, technical_indicators))
        
        # Memory-based Insights
        if self._is_source_enabled('memory'):
            tasks.append(self._get_memory_reasoning(symbol, market_data, technical_indicators))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Reasoning source failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _get_hrm_reasoning(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> ReasoningResult:
        """Get reasoning from Hierarchical Reasoning Model"""
        try:
            from core.hrm_official_integration import get_hrm_decision
            
            decision = await get_hrm_decision(symbol, market_data, technical_indicators)
            
            return ReasoningResult(
                source='hrm',
                recommendation=decision['action'],
                confidence=decision['confidence'],
                reasoning=decision['reasoning'],
                risk_score=decision['risk_score'],
                position_size=decision['position_size'],
                timestamp=datetime.utcnow(),
                metadata=decision.get('metadata', {})
            )
        except Exception as e:
            logger.warning(f"HRM reasoning failed: {e}")
            return self._get_fallback_reasoning('hrm', symbol, market_data)
    
    async def _get_gpt_oss_reasoning(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> ReasoningResult:
        """Get reasoning from GPT-OSS models"""
        try:
            from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
            
            adapter = GPTOSSTradingAdapter()
            decision = await adapter.analyze_market(symbol, market_data, technical_indicators)
            
            return ReasoningResult(
                source='gpt_oss',
                recommendation=decision.get('action', 'HOLD'),
                confidence=decision.get('confidence', 0.5),
                reasoning=decision.get('reasoning', 'GPT-OSS analysis'),
                risk_score=decision.get('risk_score', 0.5),
                position_size=decision.get('position_size', 0.05),
                timestamp=datetime.utcnow(),
                metadata=decision.get('metadata', {})
            )
        except Exception as e:
            logger.warning(f"GPT-OSS reasoning failed: {e}")
            return self._get_fallback_reasoning('gpt_oss', symbol, market_data)
    
    async def _get_deepseek_reasoning(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> ReasoningResult:
        """Get reasoning from DeepSeek-R1"""
        try:
            from core.deepseek_adapter import DeepSeekAdapter
            
            adapter = DeepSeekAdapter()
            decision = await adapter.analyze(symbol, market_data, technical_indicators)
            
            return ReasoningResult(
                source='deepseek',
                recommendation=decision.get('action', 'HOLD'),
                confidence=decision.get('confidence', 0.5),
                reasoning=decision.get('reasoning', 'DeepSeek analysis'),
                risk_score=decision.get('risk_score', 0.5),
                position_size=decision.get('position_size', 0.05),
                timestamp=datetime.utcnow(),
                metadata=decision.get('metadata', {})
            )
        except Exception as e:
            logger.warning(f"DeepSeek reasoning failed: {e}")
            return self._get_fallback_reasoning('deepseek', symbol, market_data)
    
    async def _get_quantum_reasoning(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> ReasoningResult:
        """Get reasoning from Quantum Trading Engine"""
        try:
            # Quantum optimization focuses on portfolio allocation
            price = market_data.get('price', 0)
            volatility = technical_indicators.get('volatility', 0.02)
            
            # Quantum-inspired position sizing
            quantum_position_size = min(0.10, 0.03 / max(volatility, 0.01))
            
            # Risk-adjusted recommendation
            rsi = technical_indicators.get('rsi', 50)
            macd = technical_indicators.get('macd', 0)
            
            if rsi < 30 and macd > 0:
                action = 'BUY'
                confidence = 0.75
            elif rsi > 70 and macd < 0:
                action = 'SELL'
                confidence = 0.75
            else:
                action = 'HOLD'
                confidence = 0.60
            
            return ReasoningResult(
                source='quantum',
                recommendation=action,
                confidence=confidence,
                reasoning=f"Quantum optimization: RSI={rsi:.1f}, MACD={macd:.3f}, Vol={volatility:.3f}",
                risk_score=volatility * 25,  # Scale to 0-1
                position_size=quantum_position_size,
                timestamp=datetime.utcnow(),
                metadata={'method': 'quantum_inspired_optimization'}
            )
        except Exception as e:
            logger.warning(f"Quantum reasoning failed: {e}")
            return self._get_fallback_reasoning('quantum', symbol, market_data)
    
    async def _get_memory_reasoning(
        self,
        symbol: str,
        market_data: Dict[str, Any],
        technical_indicators: Dict[str, Any]
    ) -> ReasoningResult:
        """Get reasoning from historical memory/patterns"""
        try:
            # Memory-based pattern recognition
            price_change = market_data.get('change_24h', 0)
            momentum = technical_indicators.get('momentum', 0)
            
            # Mean reversion strategy
            if abs(price_change) > 0.05:
                # Large moves often reverse
                action = 'BUY' if price_change < -0.03 else 'SELL' if price_change > 0.03 else 'HOLD'
                confidence = min(0.80, abs(price_change) * 12)
                reasoning = f"Historical pattern: Large move ({price_change:.2%}) indicates reversal opportunity"
            elif abs(momentum) > 0.02:
                # Strong momentum continuation
                action = 'BUY' if momentum > 0 else 'SELL'
                confidence = min(0.70, abs(momentum) * 25)
                reasoning = f"Momentum pattern: Strong {momentum:.2%} suggests continuation"
            else:
                action = 'HOLD'
                confidence = 0.50
                reasoning = "No significant historical pattern match"
            
            return ReasoningResult(
                source='memory',
                recommendation=action,
                confidence=confidence,
                reasoning=reasoning,
                risk_score=max(abs(price_change), abs(momentum)) * 10,
                position_size=0.05,
                timestamp=datetime.utcnow(),
                metadata={'pattern_type': 'mean_reversion_momentum'}
            )
        except Exception as e:
            logger.warning(f"Memory reasoning failed: {e}")
            return self._get_fallback_reasoning('memory', symbol, market_data)
    
    def _calculate_weighted_consensus(
        self,
        results: List[ReasoningResult]
    ) -> Dict[str, Any]:
        """Calculate weighted consensus from all reasoning sources"""
        if not results:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'strength': 'none'
            }
        
        # Vote counts with weights
        action_votes = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_confidence = 0.0
        total_weight = 0.0
        
        for result in results:
            weight = self.weights.get(result.source, 0.10)
            weighted_confidence = result.confidence * weight
            
            action_votes[result.recommendation] += weighted_confidence
            total_confidence += weighted_confidence
            total_weight += weight
        
        # Normalize
        if total_weight > 0:
            for action in action_votes:
                action_votes[action] /= total_weight
        
        # Determine winning action
        winning_action = max(action_votes, key=action_votes.get)
        winning_confidence = action_votes[winning_action]
        
        # Determine consensus strength
        if winning_confidence >= self.strong_consensus_threshold:
            strength = 'strong'
        elif winning_confidence >= self.weak_consensus_threshold:
            strength = 'moderate'
        else:
            strength = 'weak'
        
        return {
            'action': winning_action,
            'confidence': winning_confidence,
            'strength': strength,
            'vote_breakdown': action_votes
        }
    
    def _determine_final_action(
        self,
        consensus: Dict[str, Any],
        results: List[ReasoningResult]
    ) -> Dict[str, Any]:
        """Determine final trading action based on consensus"""
        action = consensus['action']
        confidence = consensus['confidence']
        
        # Calculate average risk score
        avg_risk_score = np.mean([r.risk_score for r in results]) if results else 0.5
        
        # Calculate position size based on confidence and risk
        base_position_size = 0.05  # 5% default
        position_size = base_position_size * confidence * (1 - min(avg_risk_score, 0.8))
        position_size = min(0.10, max(0.01, position_size))  # Limit 1-10%
        
        # Calculate stop loss and take profit
        stop_loss_pct = 0.02 + avg_risk_score * 0.03  # 2-5%
        take_profit_pct = stop_loss_pct * 2.5  # 2.5:1 risk-reward
        
        # Don't trade on weak consensus
        if consensus['strength'] == 'weak' and action != 'HOLD':
            action = 'HOLD'
            confidence = 0.40
            position_size = 0.0
        
        return {
            'action': action,
            'confidence': confidence,
            'position_size': position_size,
            'stop_loss': stop_loss_pct,
            'take_profit': take_profit_pct,
            'risk_score': avg_risk_score
        }
    
    def _format_reasoning_breakdown(
        self,
        results: List[ReasoningResult]
    ) -> List[Dict[str, Any]]:
        """Format reasoning from all sources for output"""
        breakdown = []
        for result in results:
            breakdown.append({
                'source': result.source,
                'recommendation': result.recommendation,
                'confidence': result.confidence,
                'reasoning': result.reasoning[:200],  # Limit length
                'weight': self.weights.get(result.source, 0.10)
            })
        return breakdown
    
    def _is_source_enabled(self, source: str) -> bool:
        """Check if reasoning source is enabled"""
        return self.config.get(f'enable_{source}', True)
    
    def _get_fallback_reasoning(
        self,
        source: str,
        symbol: str,
        market_data: Dict[str, Any]
    ) -> ReasoningResult:
        """Get safe fallback reasoning when source fails"""
        return ReasoningResult(
            source=source,
            recommendation='HOLD',
            confidence=0.30,
            reasoning=f"{source} unavailable, using safe fallback",
            risk_score=0.80,  # High risk when source fails
            position_size=0.01,
            timestamp=datetime.utcnow(),
            metadata={'fallback': True}
        )
    
    def _get_safe_fallback_decision(
        self,
        symbol: str,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get safe fallback decision when all reasoning fails"""
        return {
            'symbol': symbol,
            'action': 'HOLD',
            'confidence': 0.20,
            'position_size': 0.0,
            'entry_price': market_data.get('price', 0),
            'stop_loss': 0.02,
            'take_profit': 0.05,
            'risk_score': 0.90,
            'consensus_strength': 'none',
            'reasoning_breakdown': [],
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': {'error': 'All reasoning sources failed', 'fallback': True}
        }
    
    def update_weights_from_performance(self, performance_data: Dict[str, float]):
        """Adaptively update weights based on performance"""
        for source, performance in performance_data.items():
            if source in self.weights:
                self.performance_history[source].append(performance)
                
                # Keep last 100 performances
                if len(self.performance_history[source]) > 100:
                    self.performance_history[source] = self.performance_history[source][-100:]
                
                # Calculate moving average performance
                avg_performance = np.mean(self.performance_history[source])
                
                # Adjust weight (±20% based on performance)
                adjustment = (avg_performance - 0.5) * 0.4  # -0.2 to +0.2
                self.weights[source] = max(0.05, min(0.40, self.weights[source] + adjustment))
        
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            for source in self.weights:
                self.weights[source] /= total
        
        logger.info(f"📊 Updated weights: {self.weights}")


# Global instance
_reasoning_engine = None

def get_universal_reasoning_engine(config: Dict[str, Any] = None):
    """Get or create global reasoning engine instance"""
    global _reasoning_engine
    if _reasoning_engine is None:
        _reasoning_engine = UniversalReasoningEngineV2(config)
    return _reasoning_engine
