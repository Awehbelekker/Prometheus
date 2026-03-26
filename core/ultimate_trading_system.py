#!/usr/bin/env python3
"""
Ultimate Trading System - #1 in the World
Combines Universal Reasoning Engine + RL + Predictive Forecasting
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from core.universal_reasoning_engine import UniversalReasoningEngine
from core.reinforcement_learning_trading import ReinforcementLearningTrading
from core.predictive_regime_forecasting import PredictiveRegimeForecaster

logger = logging.getLogger(__name__)


class UltimateTradingSystem:
    """
    Ultimate Trading System - #1 in the World
    Combines:
    1. Universal Reasoning Engine (all reasoning sources)
    2. Reinforcement Learning (profit optimization)
    3. Predictive Regime Forecasting (proactive trading)
    """
    
    def __init__(self):
        logger.info("="*80)
        logger.info("INITIALIZING ULTIMATE TRADING SYSTEM - #1 IN THE WORLD")
        logger.info("="*80)
        
        # Initialize all three systems
        self.universal_reasoning = UniversalReasoningEngine()
        self.reinforcement_learning = ReinforcementLearningTrading()
        self.regime_forecaster = PredictiveRegimeForecaster()
        
        # Integration weights
        self.weights = {
            'universal_reasoning': 0.50,  # Primary: combines all reasoning
            'reinforcement_learning': 0.30,  # Profit optimization
            'regime_forecasting': 0.20  # Proactive adaptation
        }
        
        logger.info("✅ Ultimate Trading System initialized")
        logger.info(f"   Universal Reasoning: {self.universal_reasoning.get_system_status()['total_sources']} sources")
        logger.info(f"   Reinforcement Learning: Ready")
        logger.info(f"   Regime Forecasting: Ready")
    
    def make_ultimate_decision(self, market_data: Dict, portfolio: Dict = None, 
                               context: Dict = None) -> Dict[str, Any]:
        """
        Make ultimate trading decision using all three systems
        
        Args:
            market_data: Current market data
            portfolio: Current portfolio state
            context: Additional context
            
        Returns:
            Ultimate trading decision
        """
        portfolio = portfolio or {}
        context = context or {}
        
        logger.info("🧠 Making Ultimate Decision using all systems...")
        
        decisions = {}
        
        # 1. Universal Reasoning Engine (50%)
        try:
            universal_context = {
                'market_data': market_data,
                'user_profile': context.get('user_profile', {}),
                'trading_history': context.get('trading_history', []),
                'portfolio': portfolio,
                'risk_preferences': context.get('risk_preferences', {})
            }
            universal_decision = self.universal_reasoning.make_ultimate_decision(universal_context)
            decisions['universal_reasoning'] = {
                'decision': universal_decision,
                'weight': self.weights['universal_reasoning'],
                'confidence': universal_decision.get('confidence', 0.5)
            }
            logger.info(f"  ✅ Universal Reasoning: {universal_decision.get('action', 'UNKNOWN')} "
                      f"(confidence: {universal_decision.get('confidence', 0):.3f}, "
                      f"sources: {universal_decision.get('num_sources', 0)})")
        except Exception as e:
            logger.warning(f"  ⚠️ Universal Reasoning failed: {e}")
        
        # 2. Reinforcement Learning (30%)
        try:
            rl_decision = self.reinforcement_learning.make_rl_decision(market_data, portfolio, context)
            decisions['reinforcement_learning'] = {
                'decision': rl_decision,
                'weight': self.weights['reinforcement_learning'],
                'confidence': rl_decision.get('confidence', 0.5)
            }
            logger.info(f"  ✅ Reinforcement Learning: {rl_decision.get('action', 'UNKNOWN')} "
                      f"(confidence: {rl_decision.get('confidence', 0):.3f})")
        except Exception as e:
            logger.warning(f"  ⚠️ Reinforcement Learning failed: {e}")
        
        # 3. Predictive Regime Forecasting (20%)
        try:
            indicators = market_data.get('indicators', {})
            regime_prediction = self.regime_forecaster.predict_future_regime(market_data, indicators)
            
            # Convert regime prediction to trading decision
            # If regime change predicted, adjust strategy
            if regime_prediction['regime_change_predicted']:
                # Proactive adjustment based on predicted regime
                if regime_prediction['predicted_regime'] == 'pattern_recognition':
                    regime_action = 'BUY'  # Favor buying in pattern regimes
                elif regime_prediction['predicted_regime'] == 'optimization':
                    regime_action = 'HOLD'  # Wait for optimization
                elif regime_prediction['predicted_regime'] == 'volatile':
                    regime_action = 'SELL'  # Reduce exposure in volatile
                else:
                    regime_action = 'HOLD'
            else:
                regime_action = 'HOLD'  # No change needed
            
            regime_decision = {
                'action': regime_action,
                'confidence': regime_prediction['confidence'],
                'regime_prediction': regime_prediction,
                'proactive': regime_prediction['regime_change_predicted']
            }
            
            decisions['regime_forecasting'] = {
                'decision': regime_decision,
                'weight': self.weights['regime_forecasting'],
                'confidence': regime_decision.get('confidence', 0.5)
            }
            
            logger.info(f"  ✅ Regime Forecasting: {regime_decision.get('action', 'UNKNOWN')} "
                      f"(predicted regime: {regime_prediction['predicted_regime']}, "
                      f"change predicted: {regime_prediction['regime_change_predicted']})")
        except Exception as e:
            logger.warning(f"  ⚠️ Regime Forecasting failed: {e}")
        
        # Synthesize ultimate decision
        ultimate_decision = self._synthesize_ultimate_decision(decisions, market_data, portfolio)
        
        logger.info("="*80)
        logger.info(f"🎯 ULTIMATE DECISION: {ultimate_decision['action']} "
                   f"(confidence: {ultimate_decision['confidence']:.3f})")
        logger.info(f"   Sources: {ultimate_decision['num_sources']}/3 systems")
        logger.info(f"   Universal Reasoning: {decisions.get('universal_reasoning', {}).get('decision', {}).get('num_sources', 0)} sources")
        logger.info("="*80)
        
        return ultimate_decision
    
    def _synthesize_ultimate_decision(self, decisions: Dict, market_data: Dict, portfolio: Dict) -> Dict[str, Any]:
        """Synthesize ultimate decision from all systems"""
        if not decisions:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'All systems failed',
                'ultimate': True
            }
        
        # Weighted voting
        action_scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        system_details = {}
        
        for system_name, system_data in decisions.items():
            decision = system_data['decision']
            weight = system_data['weight']
            confidence = system_data['confidence']
            
            action = decision.get('action', 'HOLD')
            if action in action_scores:
                action_scores[action] += confidence * weight
            
            total_weight += weight
            system_details[system_name] = {
                'action': action,
                'confidence': confidence,
                'weight': weight
            }
        
        # Select best action
        best_action = max(action_scores, key=action_scores.get)
        final_confidence = action_scores[best_action] / max(total_weight, 0.001)
        
        # Calculate position size
        position_size = min(final_confidence * 0.1, 0.1)  # Max 10%
        
        return {
            'action': best_action,
            'confidence': min(final_confidence, 1.0),
            'position_size': position_size,
            'system_decisions': system_details,
            'num_sources': len(decisions),
            'ultimate': True,
            'timestamp': datetime.now().isoformat()
        }
    
    def learn_from_outcome(self, decision: Dict, outcome: Dict):
        """
        Learn from trading outcome
        
        Args:
            decision: Decision that was made
            outcome: Trading outcome (profit, loss, etc.)
        """
        # Update reinforcement learning
        if 'system_decisions' in decision:
            rl_decision = decision['system_decisions'].get('reinforcement_learning', {})
            if rl_decision:
                try:
                    # Get state from decision
                    state = decision.get('state', None)
                    if state is None:
                        # Reconstruct state
                        market_data = decision.get('market_data', {})
                        portfolio = decision.get('portfolio', {})
                        state = self.reinforcement_learning.encode_state(market_data, portfolio, {})
                    
                    action = rl_decision.get('action', 'HOLD')
                    next_state = state  # Simplified
                    
                    self.reinforcement_learning.learn_from_outcome(
                        state, action, outcome, next_state, done=False
                    )
                    logger.info("✅ Updated reinforcement learning from outcome")
                except Exception as e:
                    logger.warning(f"RL learning update failed: {e}")
        
        # Update regime forecaster history
        try:
            market_data = decision.get('market_data', {})
            indicators = market_data.get('indicators', {})
            self.regime_forecaster.update_history(market_data, indicators)
        except Exception as e:
            logger.warning(f"Regime forecaster update failed: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all systems"""
        return {
            'universal_reasoning': self.universal_reasoning.get_system_status(),
            'reinforcement_learning': self.reinforcement_learning.get_training_stats(),
            'regime_forecasting': {
                'history_size': len(self.regime_forecaster.history_buffer),
                'regime_history_size': len(self.regime_forecaster.regime_history)
            },
            'weights': self.weights
        }
    
    def save_all_models(self, base_path: str = "models"):
        """Save all models"""
        from pathlib import Path
        Path(base_path).mkdir(parents=True, exist_ok=True)
        
        # Save RL model
        self.reinforcement_learning.save_model(f"{base_path}/rl_trading_agent.pt")
        
        # Save regime forecaster
        self.regime_forecaster.save_model(f"{base_path}/regime_forecaster.pt")
        
        logger.info(f"✅ All models saved to {base_path}")
    
    def load_all_models(self, base_path: str = "models"):
        """Load all models"""
        # Load RL model
        self.reinforcement_learning.load_model(f"{base_path}/rl_trading_agent.pt")
        
        # Load regime forecaster
        self.regime_forecaster.load_model(f"{base_path}/regime_forecaster.pt")
        
        logger.info(f"✅ All models loaded from {base_path}")

