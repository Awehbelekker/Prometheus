#!/usr/bin/env python3
"""
HRM-Enhanced AI Personas for Prometheus Trading App

This module enhances the existing AI personas with HRM (Hierarchical Reasoning Model)
capabilities, providing each persona with sophisticated reasoning abilities for
different trading strategies and risk profiles.
"""

import torch
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from enum import Enum
from dataclasses import dataclass

from .hrm_integration import HRMTradingEngine, HRMReasoningContext, HRMReasoningLevel

logger = logging.getLogger(__name__)

class HRMPersonaType(Enum):
    """CogniFlow™-enhanced persona types"""
    CONSERVATIVE_HRM = "conservative_hrm"
    AGGRESSIVE_HRM = "aggressive_hrm"
    BALANCED_HRM = "balanced_hrm"
    QUANTUM_HRM = "quantum_hrm"
    ARBITRAGE_HRM = "arbitrage_hrm"
    MOMENTUM_HRM = "momentum_hrm"
    MEAN_REVERSION_HRM = "mean_reversion_hrm"

@dataclass
class HRMPersonaProfile:
    """Profile for CogniFlow™-enhanced trading persona"""
    persona_type: HRMPersonaType
    risk_tolerance: float  # 0.0 (ultra-conservative) to 1.0 (ultra-aggressive)
    reasoning_style: str
    preferred_assets: List[str]
    max_position_size: float
    stop_loss_percentage: float
    take_profit_percentage: float
    trading_frequency: str  # "low", "medium", "high"
    hrm_weights: Dict[str, float]  # Weights for different HRM reasoning levels

class HRMEnhancedPersona:
    """
    HRM-enhanced trading persona with hierarchical reasoning capabilities
    """
    
    def __init__(self, profile: HRMPersonaProfile, hrm_engine: HRMTradingEngine):
        self.profile = profile
        self.hrm_engine = hrm_engine
        self.trading_history = []
        self.performance_metrics = {}
        self.logger = logging.getLogger(f"HRM_Persona_{profile.persona_type.value}")
        
        self.logger.info(f"🤖 HRM-Enhanced Persona '{profile.persona_type.value}' initialized")
    
    def analyze_market_with_hrm(self, market_data: Dict[str, Any], 
                               user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market using HRM hierarchical reasoning
        """
        try:
            # Create HRM reasoning context
            context = HRMReasoningContext(
                market_data=market_data,
                user_profile=user_context.get('profile', {}),
                trading_history=user_context.get('trading_history', []),
                current_portfolio=user_context.get('portfolio', {}),
                risk_preferences=user_context.get('risk_preferences', {}),
                reasoning_level=self._get_reasoning_level_for_persona()
            )
            
            # Get HRM decision
            hrm_decision = self.hrm_engine.make_hierarchical_decision(context)
            
            # Apply persona-specific modifications
            enhanced_decision = self._apply_persona_logic(hrm_decision, context)
            
            # Track decision
            self.trading_history.append({
                'timestamp': datetime.now(),
                'decision': enhanced_decision,
                'market_data': market_data,
                'persona_type': self.profile.persona_type.value
            })
            
            return enhanced_decision
            
        except Exception as e:
            self.logger.error(f"Error in HRM market analysis: {e}")
            return self._fallback_analysis(market_data)
    
    def _get_reasoning_level_for_persona(self) -> HRMReasoningLevel:
        """
        Get appropriate reasoning level based on persona type
        """
        reasoning_map = {
            HRMPersonaType.CONSERVATIVE_HRM: HRMReasoningLevel.HIGH_LEVEL,
            HRMPersonaType.AGGRESSIVE_HRM: HRMReasoningLevel.LOW_LEVEL,
            HRMPersonaType.BALANCED_HRM: HRMReasoningLevel.ARC_LEVEL,
            HRMPersonaType.QUANTUM_HRM: HRMReasoningLevel.SUDOKU_LEVEL,
            HRMPersonaType.ARBITRAGE_HRM: HRMReasoningLevel.MAZE_LEVEL,
            HRMPersonaType.MOMENTUM_HRM: HRMReasoningLevel.LOW_LEVEL,
            HRMPersonaType.MEAN_REVERSION_HRM: HRMReasoningLevel.HIGH_LEVEL
        }
        
        return reasoning_map.get(self.profile.persona_type, HRMReasoningLevel.ARC_LEVEL)
    
    def _apply_persona_logic(self, hrm_decision: Dict[str, Any], 
                            context: HRMReasoningContext) -> Dict[str, Any]:
        """
        Apply persona-specific logic to HRM decision
        """
        # Get base decision
        decision = hrm_decision.copy()
        
        # Apply persona-specific modifications
        if self.profile.persona_type == HRMPersonaType.CONSERVATIVE_HRM:
            decision = self._apply_conservative_logic(decision)
        elif self.profile.persona_type == HRMPersonaType.AGGRESSIVE_HRM:
            decision = self._apply_aggressive_logic(decision)
        elif self.profile.persona_type == HRMPersonaType.BALANCED_HRM:
            decision = self._apply_balanced_logic(decision)
        elif self.profile.persona_type == HRMPersonaType.QUANTUM_HRM:
            decision = self._apply_quantum_logic(decision)
        elif self.profile.persona_type == HRMPersonaType.ARBITRAGE_HRM:
            decision = self._apply_arbitrage_logic(decision)
        elif self.profile.persona_type == HRMPersonaType.MOMENTUM_HRM:
            decision = self._apply_momentum_logic(decision)
        elif self.profile.persona_type == HRMPersonaType.MEAN_REVERSION_HRM:
            decision = self._apply_mean_reversion_logic(decision)
        
        # Add persona-specific metadata
        decision['persona_type'] = self.profile.persona_type.value
        decision['persona_confidence'] = self._calculate_persona_confidence(decision)
        decision['risk_adjusted_action'] = self._adjust_action_for_risk(decision)
        
        return decision
    
    def _apply_conservative_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply conservative trading logic
        """
        # Reduce position size for conservative approach
        decision['position_size'] *= 0.5
        
        # Increase confidence threshold
        if decision['confidence'] < 0.7:
            decision['action'] = 'HOLD'
        
        # Add conservative stop-loss
        decision['stop_loss'] = self.profile.stop_loss_percentage * 0.8
        
        return decision
    
    def _apply_aggressive_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply aggressive trading logic
        """
        # Increase position size for aggressive approach
        decision['position_size'] = min(decision['position_size'] * 1.5, 1.0)
        
        # Lower confidence threshold
        if decision['confidence'] > 0.4:
            decision['action'] = decision['action']  # Keep original action
        
        # Add aggressive take-profit
        decision['take_profit'] = self.profile.take_profit_percentage * 1.2
        
        return decision
    
    def _apply_balanced_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply balanced trading logic
        """
        # Moderate position sizing
        decision['position_size'] *= 1.0  # Keep original
        
        # Balanced confidence threshold
        if decision['confidence'] < 0.6:
            decision['action'] = 'HOLD'
        
        # Standard risk management
        decision['stop_loss'] = self.profile.stop_loss_percentage
        decision['take_profit'] = self.profile.take_profit_percentage
        
        return decision
    
    def _apply_quantum_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply quantum-inspired trading logic
        """
        # Quantum superposition of actions
        if decision['confidence'] > 0.8:
            # High confidence - strong action
            decision['position_size'] *= 1.2
        elif decision['confidence'] > 0.6:
            # Medium confidence - moderate action
            decision['position_size'] *= 1.0
        else:
            # Low confidence - quantum uncertainty
            decision['action'] = 'HOLD'
        
        # Quantum entanglement with market patterns
        if 'patterns' in decision.get('reasoning_levels', {}):
            pattern_score = np.mean(decision['reasoning_levels']['patterns'])
            decision['quantum_factor'] = pattern_score
        
        return decision
    
    def _apply_arbitrage_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply arbitrage trading logic
        """
        # Look for price discrepancies
        if 'market_data' in decision:
            # Arbitrage opportunities
            decision['arbitrage_opportunity'] = self._detect_arbitrage(decision['market_data'])
        
        # Quick execution for arbitrage
        decision['execution_speed'] = 'immediate'
        decision['position_size'] *= 0.8  # Smaller positions for arbitrage
        
        return decision
    
    def _apply_momentum_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply momentum trading logic
        """
        # Momentum-based position sizing
        if decision['action'] == 'BUY':
            decision['position_size'] *= 1.3
        elif decision['action'] == 'SELL':
            decision['position_size'] *= 1.3
        
        # Momentum indicators
        decision['momentum_score'] = self._calculate_momentum_score(decision)
        
        return decision
    
    def _apply_mean_reversion_logic(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply mean reversion trading logic
        """
        # Mean reversion position sizing
        if decision['action'] == 'BUY':
            decision['position_size'] *= 0.8  # Smaller positions for mean reversion
        elif decision['action'] == 'SELL':
            decision['position_size'] *= 0.8
        
        # Mean reversion indicators
        decision['mean_reversion_score'] = self._calculate_mean_reversion_score(decision)
        
        return decision
    
    def _calculate_persona_confidence(self, decision: Dict[str, Any]) -> float:
        """
        Calculate persona-specific confidence
        """
        base_confidence = decision.get('confidence', 0.5)
        
        # Adjust confidence based on persona type
        if self.profile.persona_type == HRMPersonaType.CONSERVATIVE_HRM:
            return min(base_confidence * 0.9, 1.0)  # More conservative
        elif self.profile.persona_type == HRMPersonaType.AGGRESSIVE_HRM:
            return min(base_confidence * 1.1, 1.0)  # More aggressive
        else:
            return base_confidence
    
    def _adjust_action_for_risk(self, decision: Dict[str, Any]) -> str:
        """
        Adjust trading action based on risk profile
        """
        action = decision.get('action', 'HOLD')
        risk_level = decision.get('risk_level', 0.5)
        
        # Conservative risk adjustment
        if self.profile.risk_tolerance < 0.3:
            if action == 'BUY' and risk_level > 0.6:
                return 'HOLD'
            elif action == 'SELL' and risk_level > 0.6:
                return 'HOLD'
        
        # Aggressive risk adjustment
        elif self.profile.risk_tolerance > 0.7:
            if action == 'HOLD' and risk_level < 0.4:
                return 'BUY'  # More aggressive
        
        return action
    
    def _detect_arbitrage(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect arbitrage opportunities
        """
        # Simplified arbitrage detection
        return {
            'opportunity_detected': False,
            'price_discrepancy': 0.0,
            'recommended_action': 'HOLD'
        }
    
    def _calculate_momentum_score(self, decision: Dict[str, Any]) -> float:
        """
        Calculate momentum score
        """
        # Simplified momentum calculation
        return decision.get('confidence', 0.5)
    
    def _calculate_mean_reversion_score(self, decision: Dict[str, Any]) -> float:
        """
        Calculate mean reversion score
        """
        # Simplified mean reversion calculation
        return 1.0 - decision.get('confidence', 0.5)
    
    def _fallback_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback analysis when HRM fails
        """
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'position_size': 0.0,
            'risk_level': 0.5,
            'persona_type': self.profile.persona_type.value,
            'persona_confidence': 0.5,
            'risk_adjusted_action': 'HOLD',
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get persona performance metrics
        """
        if not self.trading_history:
            return {'total_decisions': 0, 'success_rate': 0.0}
        
        total_decisions = len(self.trading_history)
        successful_decisions = sum(1 for d in self.trading_history 
                                 if d['decision'].get('action') != 'HOLD')
        
        return {
            'total_decisions': total_decisions,
            'successful_decisions': successful_decisions,
            'success_rate': successful_decisions / total_decisions if total_decisions > 0 else 0.0,
            'persona_type': self.profile.persona_type.value,
            'last_decision_time': self.trading_history[-1]['timestamp'] if self.trading_history else None
        }

class HRMPersonaManager:
    """
    Manager for HRM-enhanced trading personas
    """
    
    def __init__(self, hrm_engine: HRMTradingEngine):
        self.hrm_engine = hrm_engine
        self.personas = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize all HRM personas
        self._initialize_personas()
        
        self.logger.info("🤖 HRM Persona Manager initialized with all personas")
    
    def _initialize_personas(self):
        """
        Initialize all HRM-enhanced personas
        """
        persona_profiles = [
            HRMPersonaProfile(
                persona_type=HRMPersonaType.CONSERVATIVE_HRM,
                risk_tolerance=0.2,
                reasoning_style="High-level abstract planning",
                preferred_assets=["Bonds", "Blue-chip stocks", "Gold"],
                max_position_size=0.1,
                stop_loss_percentage=0.02,
                take_profit_percentage=0.05,
                trading_frequency="low",
                hrm_weights={'high_level': 0.8, 'low_level': 0.1, 'arc_level': 0.1}
            ),
            HRMPersonaProfile(
                persona_type=HRMPersonaType.AGGRESSIVE_HRM,
                risk_tolerance=0.8,
                reasoning_style="Low-level detailed execution",
                preferred_assets=["Growth stocks", "Crypto", "Options"],
                max_position_size=0.3,
                stop_loss_percentage=0.05,
                take_profit_percentage=0.15,
                trading_frequency="high",
                hrm_weights={'high_level': 0.2, 'low_level': 0.7, 'arc_level': 0.1}
            ),
            HRMPersonaProfile(
                persona_type=HRMPersonaType.BALANCED_HRM,
                risk_tolerance=0.5,
                reasoning_style="ARC-level general reasoning",
                preferred_assets=["ETFs", "Dividend stocks", "Real estate"],
                max_position_size=0.2,
                stop_loss_percentage=0.03,
                take_profit_percentage=0.08,
                trading_frequency="medium",
                hrm_weights={'high_level': 0.3, 'low_level': 0.3, 'arc_level': 0.4}
            ),
            HRMPersonaProfile(
                persona_type=HRMPersonaType.QUANTUM_HRM,
                risk_tolerance=0.6,
                reasoning_style="Sudoku-level pattern recognition",
                preferred_assets=["Quantum computing stocks", "AI stocks", "Futures"],
                max_position_size=0.25,
                stop_loss_percentage=0.04,
                take_profit_percentage=0.12,
                trading_frequency="medium",
                hrm_weights={'high_level': 0.2, 'low_level': 0.3, 'arc_level': 0.3, 'sudoku_level': 0.2}
            ),
            HRMPersonaProfile(
                persona_type=HRMPersonaType.ARBITRAGE_HRM,
                risk_tolerance=0.4,
                reasoning_style="Maze-level path finding",
                preferred_assets=["Pairs trading", "Statistical arbitrage", "Market making"],
                max_position_size=0.15,
                stop_loss_percentage=0.02,
                take_profit_percentage=0.03,
                trading_frequency="very_high",
                hrm_weights={'high_level': 0.1, 'low_level': 0.4, 'arc_level': 0.2, 'maze_level': 0.3}
            ),
            HRMPersonaProfile(
                persona_type=HRMPersonaType.MOMENTUM_HRM,
                risk_tolerance=0.7,
                reasoning_style="Low-level momentum analysis",
                preferred_assets=["Trending stocks", "Sector ETFs", "Commodities"],
                max_position_size=0.25,
                stop_loss_percentage=0.04,
                take_profit_percentage=0.10,
                trading_frequency="high",
                hrm_weights={'high_level': 0.1, 'low_level': 0.8, 'arc_level': 0.1}
            ),
            HRMPersonaProfile(
                persona_type=HRMPersonaType.MEAN_REVERSION_HRM,
                risk_tolerance=0.3,
                reasoning_style="High-level mean reversion",
                preferred_assets=["Oversold stocks", "Value stocks", "Bonds"],
                max_position_size=0.2,
                stop_loss_percentage=0.03,
                take_profit_percentage=0.06,
                trading_frequency="medium",
                hrm_weights={'high_level': 0.7, 'low_level': 0.2, 'arc_level': 0.1}
            )
        ]
        
        # Create personas
        for profile in persona_profiles:
            persona = HRMEnhancedPersona(profile, self.hrm_engine)
            self.personas[profile.persona_type] = persona
    
    def get_persona(self, persona_type: HRMPersonaType) -> HRMEnhancedPersona:
        """
        Get specific HRM persona
        """
        return self.personas.get(persona_type)
    
    def get_all_personas(self) -> Dict[HRMPersonaType, HRMEnhancedPersona]:
        """
        Get all HRM personas
        """
        return self.personas
    
    def analyze_with_persona(self, persona_type: HRMPersonaType, 
                           market_data: Dict[str, Any], 
                           user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market with specific HRM persona
        """
        persona = self.get_persona(persona_type)
        if persona:
            return persona.analyze_market_with_hrm(market_data, user_context)
        else:
            self.logger.error(f"Persona {persona_type.value} not found")
            return self._fallback_analysis(market_data)
    
    def get_persona_performance(self) -> Dict[str, Any]:
        """
        Get performance metrics for all personas
        """
        performance = {}
        for persona_type, persona in self.personas.items():
            performance[persona_type.value] = persona.get_performance_metrics()
        return performance
    
    def _fallback_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback analysis when persona not found
        """
        return {
            'action': 'HOLD',
            'confidence': 0.5,
            'position_size': 0.0,
            'risk_level': 0.5,
            'persona_type': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'fallback': True
        }

# Initialize HRM Persona Manager - will be initialized in API
# hrm_persona_manager = HRMPersonaManager(hrm_trading_engine) 