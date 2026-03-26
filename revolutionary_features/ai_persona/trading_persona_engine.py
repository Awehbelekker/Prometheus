"""
🎯 HYPER-PERSONALIZED AI TRADING PERSONAS
Create AI personalities that match each trader's psychology and trading style
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TradingPersonalityType(Enum):
    AGGRESSIVE_WOLF = "aggressive_wolf"
    CONSERVATIVE_TURTLE = "conservative_turtle"  
    ANALYTICAL_OWL = "analytical_owl"
    INTUITIVE_DOLPHIN = "intuitive_dolphin"
    BALANCED_EAGLE = "balanced_eagle"
    RISK_LOVING_SHARK = "risk_loving_shark"
    CAUTIOUS_RABBIT = "cautious_rabbit"

@dataclass
class TradingPersona:
    """AI Trading Persona with unique characteristics"""
    persona_id: str
    user_id: int
    personality_type: TradingPersonalityType
    name: str
    risk_tolerance: float  # 0.0 to 1.0
    aggression_level: float  # 0.0 to 1.0
    patience_factor: float  # 0.0 to 1.0
    analytical_depth: float  # 0.0 to 1.0
    emotional_sensitivity: float  # 0.0 to 1.0
    
    # Learning characteristics
    learning_speed: float = 0.5
    adaptation_rate: float = 0.3
    memory_retention: float = 0.8
    
    # Trading preferences
    preferred_timeframes: List[str] = None
    preferred_assets: List[str] = None
    max_positions: int = 10
    position_sizing_method: str = "kelly_criterion"
    
    # Performance tracking
    total_trades: int = 0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    
    # AI consciousness attributes
    confidence_level: float = 0.5
    decision_certainty: float = 0.5
    stress_level: float = 0.0
    
    created_at: datetime = None
    last_updated: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()
        if self.preferred_timeframes is None:
            self.preferred_timeframes = ["1h", "4h", "1d"]
        if self.preferred_assets is None:
            self.preferred_assets = ["BTC", "ETH", "AAPL", "TSLA"]

class TradingPersonaEngine:
    """Advanced AI system that creates and manages trading personas"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.personas: Dict[str, TradingPersona] = {}
        self.personality_templates = self._initialize_personality_templates()
        
    def _initialize_personality_templates(self) -> Dict[TradingPersonalityType, Dict[str, Any]]:
        """Initialize personality templates with unique characteristics"""
        return {
            TradingPersonalityType.AGGRESSIVE_WOLF: {
                "name": "Alpha Wolf",
                "risk_tolerance": 0.9,
                "aggression_level": 0.95,
                "patience_factor": 0.2,
                "analytical_depth": 0.6,
                "emotional_sensitivity": 0.3,
                "description": "High-risk, high-reward hunter. Strikes fast and decisively.",
                "trading_style": "Scalping and momentum trading",
                "motto": "Fortune favors the bold",
                "max_positions": 15,
                "preferred_timeframes": ["1m", "5m", "15m"],
                "position_sizing_method": "fixed_fraction_aggressive"
            },
            TradingPersonalityType.CONSERVATIVE_TURTLE: {
                "name": "Wise Turtle",
                "risk_tolerance": 0.2,
                "aggression_level": 0.1,
                "patience_factor": 0.95,
                "analytical_depth": 0.9,
                "emotional_sensitivity": 0.8,
                "description": "Slow and steady wins the race. Long-term wealth building.",
                "trading_style": "Buy and hold with value investing",
                "motto": "Patience is the key to success",
                "max_positions": 5,
                "preferred_timeframes": ["1d", "1w", "1M"],
                "position_sizing_method": "kelly_criterion_conservative"
            },
            TradingPersonalityType.ANALYTICAL_OWL: {
                "name": "Professor Owl", 
                "risk_tolerance": 0.5,
                "aggression_level": 0.3,
                "patience_factor": 0.8,
                "analytical_depth": 0.98,
                "emotional_sensitivity": 0.2,
                "description": "Data-driven decisions with deep market analysis.",
                "trading_style": "Quantitative and algorithmic trading",
                "motto": "In data we trust",
                "max_positions": 8,
                "preferred_timeframes": ["4h", "1d"],
                "position_sizing_method": "volatility_adjusted"
            },
            TradingPersonalityType.INTUITIVE_DOLPHIN: {
                "name": "Mystic Dolphin",
                "risk_tolerance": 0.6,
                "aggression_level": 0.5,
                "patience_factor": 0.6,
                "analytical_depth": 0.4,
                "emotional_sensitivity": 0.9,
                "description": "Uses intuition and market sentiment for trading decisions.",
                "trading_style": "Sentiment-based and contrarian trading",
                "motto": "Feel the market's pulse",
                "max_positions": 10,
                "preferred_timeframes": ["1h", "4h"],
                "position_sizing_method": "sentiment_adjusted"
            },
            TradingPersonalityType.BALANCED_EAGLE: {
                "name": "Golden Eagle",
                "risk_tolerance": 0.6,
                "aggression_level": 0.6,
                "patience_factor": 0.6,
                "analytical_depth": 0.7,
                "emotional_sensitivity": 0.5,
                "description": "Perfect balance of all trading characteristics.",
                "trading_style": "Multi-strategy adaptive trading",
                "motto": "Balance creates harmony",
                "max_positions": 12,
                "preferred_timeframes": ["15m", "1h", "4h", "1d"],
                "position_sizing_method": "adaptive_sizing"
            },
            TradingPersonalityType.RISK_LOVING_SHARK: {
                "name": "Apex Shark",
                "risk_tolerance": 0.95,
                "aggression_level": 0.9,
                "patience_factor": 0.3,
                "analytical_depth": 0.5,
                "emotional_sensitivity": 0.1,
                "description": "Thrives on high-risk, high-reward opportunities.",
                "trading_style": "Leveraged trading and options strategies",
                "motto": "No risk, no reward",
                "max_positions": 20,
                "preferred_timeframes": ["1m", "5m", "15m", "1h"],
                "position_sizing_method": "maximum_risk"
            },
            TradingPersonalityType.CAUTIOUS_RABBIT: {
                "name": "Careful Rabbit",
                "risk_tolerance": 0.15,
                "aggression_level": 0.05,
                "patience_factor": 0.9,
                "analytical_depth": 0.8,
                "emotional_sensitivity": 0.95,
                "description": "Extremely cautious with capital preservation focus.",
                "trading_style": "Conservative swing trading",
                "motto": "Protect capital at all costs",
                "max_positions": 3,
                "preferred_timeframes": ["1d", "1w"],
                "position_sizing_method": "minimum_risk"
            }
        }
    
    async def create_persona_for_user(self, user_id: int, personality_type: TradingPersonalityType,
                                    custom_params: Optional[Dict[str, Any]] = None) -> TradingPersona:
        """Create a personalized AI trading persona for a user"""
        try:
            template = self.personality_templates[personality_type]
            persona_id = f"persona_{user_id}_{personality_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create base persona from template
            persona = TradingPersona(
                persona_id=persona_id,
                user_id=user_id,
                personality_type=personality_type,
                name=template["name"],
                risk_tolerance=template["risk_tolerance"],
                aggression_level=template["aggression_level"],
                patience_factor=template["patience_factor"],
                analytical_depth=template["analytical_depth"],
                emotional_sensitivity=template["emotional_sensitivity"],
                max_positions=template["max_positions"],
                preferred_timeframes=template["preferred_timeframes"],
                position_sizing_method=template["position_sizing_method"]
            )
            
            # Apply custom parameters if provided
            if custom_params:
                for key, value in custom_params.items():
                    if hasattr(persona, key):
                        setattr(persona, key, value)
            
            # Store the persona
            self.personas[persona_id] = persona
            
            logger.info(f"Created AI trading persona '{template['name']}' for user {user_id}")
            return persona
            
        except Exception as e:
            logger.error(f"Error creating trading persona: {e}")
            raise
    
    async def analyze_user_trading_behavior(self, user_id: int, trading_history: List[Dict[str, Any]]) -> TradingPersonalityType:
        """Analyze user's trading history to recommend the best persona"""
        try:
            if not trading_history:
                return TradingPersonalityType.BALANCED_EAGLE  # Default
            
            # Analyze trading patterns
            total_trades = len(trading_history)
            profitable_trades = len([t for t in trading_history if t.get('pnl', 0) > 0])
            win_rate = profitable_trades / total_trades if total_trades > 0 else 0
            
            # Calculate risk metrics
            avg_position_size = sum([abs(t.get('quantity', 0)) for t in trading_history]) / total_trades
            max_position_size = max([abs(t.get('quantity', 0)) for t in trading_history])
            risk_ratio = avg_position_size / max_position_size if max_position_size > 0 else 0
            
            # Analyze timeframes
            timeframes = [t.get('timeframe', '1h') for t in trading_history]
            short_term_trades = len([tf for tf in timeframes if tf in ['1m', '5m', '15m']])
            long_term_trades = len([tf for tf in timeframes if tf in ['1d', '1w', '1M']])
            
            # Determine personality based on patterns
            if risk_ratio > 0.8 and short_term_trades > total_trades * 0.7:
                if win_rate > 0.6:
                    return TradingPersonalityType.AGGRESSIVE_WOLF
                else:
                    return TradingPersonalityType.RISK_LOVING_SHARK
            elif risk_ratio < 0.3 and long_term_trades > total_trades * 0.6:
                if win_rate > 0.7:
                    return TradingPersonalityType.CONSERVATIVE_TURTLE
                else:
                    return TradingPersonalityType.CAUTIOUS_RABBIT
            elif win_rate > 0.75:
                return TradingPersonalityType.ANALYTICAL_OWL
            elif short_term_trades > 0 and long_term_trades > 0:
                return TradingPersonalityType.INTUITIVE_DOLPHIN
            else:
                return TradingPersonalityType.BALANCED_EAGLE
                
        except Exception as e:
            logger.error(f"Error analyzing trading behavior: {e}")
            return TradingPersonalityType.BALANCED_EAGLE
    
    async def evolve_persona(self, persona_id: str, trade_result: Dict[str, Any]) -> None:
        """Evolve the persona based on trading results"""
        try:
            if persona_id not in self.personas:
                return
            
            persona = self.personas[persona_id]
            
            # Update trading statistics
            persona.total_trades += 1
            is_profitable = trade_result.get('pnl', 0) > 0
            
            # Update win rate
            current_wins = persona.win_rate * (persona.total_trades - 1)
            if is_profitable:
                current_wins += 1
            persona.win_rate = current_wins / persona.total_trades
            
            # Adapt personality traits based on performance
            if is_profitable:
                # Successful trade - increase confidence
                persona.confidence_level = min(1.0, persona.confidence_level + 0.01)
                persona.decision_certainty = min(1.0, persona.decision_certainty + 0.005)
                persona.stress_level = max(0.0, persona.stress_level - 0.02)
                
                # Slightly increase aggression if conservative persona is winning
                if persona.personality_type in [TradingPersonalityType.CONSERVATIVE_TURTLE, TradingPersonalityType.CAUTIOUS_RABBIT]:
                    persona.aggression_level = min(0.8, persona.aggression_level + 0.01)
            else:
                # Losing trade - adjust traits
                persona.confidence_level = max(0.1, persona.confidence_level - 0.02)
                persona.stress_level = min(1.0, persona.stress_level + 0.03)
                
                # Become more analytical after losses
                persona.analytical_depth = min(1.0, persona.analytical_depth + 0.01)
                
                # Reduce aggression for aggressive personas
                if persona.personality_type in [TradingPersonalityType.AGGRESSIVE_WOLF, TradingPersonalityType.RISK_LOVING_SHARK]:
                    persona.aggression_level = max(0.1, persona.aggression_level - 0.02)
            
            # Update last modified time
            persona.last_updated = datetime.utcnow()
            
            logger.info(f"Evolved persona {persona.name} - Confidence: {persona.confidence_level:.2f}, Win Rate: {persona.win_rate:.2f}")
            
        except Exception as e:
            logger.error(f"Error evolving persona: {e}")
    
    async def get_persona_trading_decision(self, persona_id: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get trading decision from the AI persona"""
        try:
            if persona_id not in self.personas:
                raise ValueError(f"Persona {persona_id} not found")
            
            persona = self.personas[persona_id]
            
            # Generate decision based on persona characteristics
            decision = {
                "action": await self._determine_action(persona, market_data),
                "confidence": persona.confidence_level,
                "position_size": await self._calculate_position_size(persona, market_data),
                "stop_loss": await self._calculate_stop_loss(persona, market_data),
                "take_profit": await self._calculate_take_profit(persona, market_data),
                "reasoning": await self._generate_reasoning(persona, market_data),
                "personality_influence": await self._get_personality_influence(persona),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return decision
            
        except Exception as e:
            logger.error(f"Error getting persona trading decision: {e}")
            raise
    
    async def _determine_action(self, persona: TradingPersona, market_data: Dict[str, Any]) -> str:
        """Determine trading action based on persona characteristics"""
        # Simplified decision logic - in production, this would be much more sophisticated
        market_trend = market_data.get('trend', 'neutral')
        volatility = market_data.get('volatility', 0.5)
        
        if persona.aggression_level > 0.7 and market_trend == 'bullish':
            return 'strong_buy'
        elif persona.aggression_level > 0.7 and market_trend == 'bearish':
            return 'strong_sell'
        elif persona.patience_factor > 0.8 and volatility > 0.7:
            return 'hold'  # Patient personas wait out volatility
        elif persona.analytical_depth > 0.8:
            return 'analyze_further'
        else:
            return 'moderate_buy' if market_trend == 'bullish' else 'moderate_sell'
    
    async def _calculate_position_size(self, persona: TradingPersona, market_data: Dict[str, Any]) -> float:
        """Calculate position size based on persona risk tolerance"""
        base_size = 0.1  # 10% of portfolio
        risk_multiplier = persona.risk_tolerance
        confidence_multiplier = persona.confidence_level
        
        return base_size * risk_multiplier * confidence_multiplier
    
    async def _calculate_stop_loss(self, persona: TradingPersona, market_data: Dict[str, Any]) -> float:
        """Calculate stop loss based on persona characteristics"""
        base_stop = 0.02  # 2%
        if persona.risk_tolerance > 0.8:
            return base_stop * 2  # Aggressive personas use wider stops
        elif persona.risk_tolerance < 0.3:
            return base_stop * 0.5  # Conservative personas use tight stops
        else:
            return base_stop
    
    async def _calculate_take_profit(self, persona: TradingPersona, market_data: Dict[str, Any]) -> float:
        """Calculate take profit based on persona characteristics"""
        base_target = 0.04  # 4%
        if persona.patience_factor > 0.8:
            return base_target * 3  # Patient personas wait for bigger moves
        elif persona.aggression_level > 0.8:
            return base_target * 0.8  # Aggressive personas take quick profits
        else:
            return base_target
    
    async def _generate_reasoning(self, persona: TradingPersona, market_data: Dict[str, Any]) -> str:
        """Generate human-like reasoning for the decision"""
        template = self.personality_templates[persona.personality_type]
        
        reasonings = [
            f"As {template['name']}, my {template['trading_style']} approach suggests this move.",
            f"Following my motto '{template['motto']}', I believe this is the right decision.",
            f"My analytical depth of {persona.analytical_depth:.1f} and risk tolerance of {persona.risk_tolerance:.1f} support this choice.",
            f"Based on my {persona.total_trades} previous trades with {persona.win_rate:.1%} win rate, this aligns with my strategy."
        ]
        
        return reasonings[persona.total_trades % len(reasonings)]
    
    async def _get_personality_influence(self, persona: TradingPersona) -> Dict[str, float]:
        """Get the influence of different personality traits on the decision"""
        return {
            "risk_tolerance": persona.risk_tolerance,
            "aggression_level": persona.aggression_level,
            "patience_factor": persona.patience_factor,
            "analytical_depth": persona.analytical_depth,
            "emotional_sensitivity": persona.emotional_sensitivity,
            "confidence_level": persona.confidence_level,
            "stress_level": persona.stress_level
        }
    
    async def get_all_personas_for_user(self, user_id: int) -> List[TradingPersona]:
        """Get all trading personas for a user"""
        return [persona for persona in self.personas.values() if persona.user_id == user_id]
    
    async def delete_persona(self, persona_id: str) -> bool:
        """Delete a trading persona"""
        if persona_id in self.personas:
            del self.personas[persona_id]
            logger.info(f"Deleted trading persona {persona_id}")
            return True
        return False
    
    async def get_persona_performance_report(self, persona_id: str) -> Dict[str, Any]:
        """Generate comprehensive performance report for a persona"""
        if persona_id not in self.personas:
            raise ValueError(f"Persona {persona_id} not found")
        
        persona = self.personas[persona_id]
        template = self.personality_templates[persona.personality_type]
        
        return {
            "persona_info": {
                "name": persona.name,
                "type": persona.personality_type.value,
                "description": template["description"],
                "motto": template["motto"],
                "trading_style": template["trading_style"]
            },
            "performance_metrics": {
                "total_trades": persona.total_trades,
                "win_rate": persona.win_rate,
                "profit_factor": persona.profit_factor,
                "sharpe_ratio": persona.sharpe_ratio,
                "max_drawdown": persona.max_drawdown
            },
            "personality_traits": {
                "risk_tolerance": persona.risk_tolerance,
                "aggression_level": persona.aggression_level,
                "patience_factor": persona.patience_factor,
                "analytical_depth": persona.analytical_depth,
                "emotional_sensitivity": persona.emotional_sensitivity
            },
            "current_state": {
                "confidence_level": persona.confidence_level,
                "decision_certainty": persona.decision_certainty,
                "stress_level": persona.stress_level
            },
            "evolution_tracking": {
                "created_at": persona.created_at.isoformat(),
                "last_updated": persona.last_updated.isoformat(),
                "learning_progress": min(1.0, persona.total_trades / 100)  # Learning progress out of 100 trades
            }
        }

# Global instance
persona_engine = None

def get_persona_engine(config: Dict[str, Any] = None) -> TradingPersonaEngine:
    """Get or create the global persona engine instance"""
    global persona_engine
    if persona_engine is None:
        persona_engine = TradingPersonaEngine(config or {})
    return persona_engine

# Example usage and testing functions
async def test_persona_system():
    """Test the AI trading persona system"""
    engine = get_persona_engine()
    
    # Create different personas
    wolf_persona = await engine.create_persona_for_user(1, TradingPersonalityType.AGGRESSIVE_WOLF)
    turtle_persona = await engine.create_persona_for_user(1, TradingPersonalityType.CONSERVATIVE_TURTLE)
    owl_persona = await engine.create_persona_for_user(1, TradingPersonalityType.ANALYTICAL_OWL)
    
    # Test market data
    market_data = {
        "trend": "bullish",
        "volatility": 0.6,
        "price": 45000,
        "volume": 1000000
    }
    
    # Get decisions from different personas
    wolf_decision = await engine.get_persona_trading_decision(wolf_persona.persona_id, market_data)
    turtle_decision = await engine.get_persona_trading_decision(turtle_persona.persona_id, market_data)
    owl_decision = await engine.get_persona_trading_decision(owl_persona.persona_id, market_data)
    
    print("=== AI TRADING PERSONA DECISIONS ===")
    print(f"Wolf Decision: {wolf_decision}")
    print(f"Turtle Decision: {turtle_decision}")
    print(f"Owl Decision: {owl_decision}")
    
    # Simulate trade results and evolution
    for i in range(10):
        trade_result = {"pnl": random.uniform(-100, 200)}  # Random P&L
        await engine.evolve_persona(wolf_persona.persona_id, trade_result)
    
    # Get performance report
    wolf_report = await engine.get_persona_performance_report(wolf_persona.persona_id)
    print(f"\nWolf Persona Report: {json.dumps(wolf_report, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test_persona_system())
