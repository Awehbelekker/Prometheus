#!/usr/bin/env python3
"""
Multi-Checkpoint Ensemble System
Combines ARC, Sudoku, and Maze checkpoints for superior reasoning
"""

import torch
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from core.hrm_integration import FullHRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
from core.hrm_checkpoint_manager import HRMCheckpointManager

logger = logging.getLogger(__name__)


class MultiCheckpointEnsemble:
    """
    Ensemble system combining multiple HRM checkpoints
    Uses ARC (general reasoning), Sudoku (pattern recognition), Maze (optimization)
    """
    
    def __init__(self, device='cpu'):
        self.device = device
        self.checkpoint_manager = HRMCheckpointManager()
        
        # Initialize engines for each checkpoint
        self.engines = {}
        self._initialize_engines()
        
        # Market regime detection
        self.regime_weights = {
            'general': {'arc': 0.5, 'sudoku': 0.3, 'maze': 0.2},
            'pattern_recognition': {'arc': 0.2, 'sudoku': 0.6, 'maze': 0.2},
            'optimization': {'arc': 0.2, 'sudoku': 0.2, 'maze': 0.6},
            'volatile': {'arc': 0.4, 'sudoku': 0.4, 'maze': 0.2}
        }
    
    def _initialize_engines(self):
        """Initialize HRM engines for each checkpoint"""
        checkpoints = ['arc_agi_2', 'sudoku_extreme', 'maze_30x30']
        
        for checkpoint_name in checkpoints:
            try:
                # Create engine (will use checkpoint if available)
                engine = FullHRMTradingEngine(
                    device=self.device,
                    use_full_hrm=True
                )
                
                # Try to load specific checkpoint
                checkpoint_path = self.checkpoint_manager.get_checkpoint_path(checkpoint_name)
                if checkpoint_path and Path(checkpoint_path).exists():
                    # Load checkpoint into engine
                    if hasattr(engine, 'full_hrm') and engine.full_hrm:
                        try:
                            engine.full_hrm.load_checkpoint(checkpoint_path)
                            logger.info(f"✅ Loaded {checkpoint_name} checkpoint")
                        except Exception as e:
                            logger.warning(f"Could not load {checkpoint_name}: {e}")
                
                self.engines[checkpoint_name] = engine
                
            except Exception as e:
                logger.error(f"Failed to initialize engine for {checkpoint_name}: {e}")
                self.engines[checkpoint_name] = None
    
    def make_ensemble_decision(self, context: HRMReasoningContext) -> Dict[str, Any]:
        """
        Make decision using ensemble of checkpoints
        """
        # Detect market regime
        regime = self._detect_market_regime(context.market_data)
        weights = self.regime_weights.get(regime, self.regime_weights['general'])
        
        # Get decisions from each checkpoint
        decisions = {}
        for checkpoint_name, engine in self.engines.items():
            if engine is None:
                continue
                
            try:
                decision = engine.make_hierarchical_decision(context)
                decisions[checkpoint_name] = decision
            except Exception as e:
                logger.warning(f"{checkpoint_name} engine failed: {e}")
                decisions[checkpoint_name] = None
        
        # Synthesize ensemble decision
        return self._synthesize_ensemble(decisions, weights, regime)
    
    def _detect_market_regime(self, market_data: Dict[str, Any]) -> str:
        """Detect current market regime"""
        if 'indicators' not in market_data:
            return 'general'
        
        indicators = market_data['indicators']
        rsi = indicators.get('rsi', 50)
        macd = indicators.get('macd', 0)
        volatility = indicators.get('volatility', 0)
        
        # Pattern recognition regime (high RSI deviation, clear trends)
        if abs(rsi - 50) > 25 or abs(macd) > 1.5:
            return 'pattern_recognition'
        
        # Optimization regime (moderate trends, need path finding)
        if 0.5 < abs(macd) < 1.5:
            return 'optimization'
        
        # Volatile regime (high volatility)
        if volatility > 0.03:
            return 'volatile'
        
        return 'general'
    
    def _synthesize_ensemble(self, decisions: Dict[str, Dict], weights: Dict[str, float], regime: str) -> Dict[str, Any]:
        """Synthesize decisions from multiple checkpoints"""
        valid_decisions = {k: v for k, v in decisions.items() if v is not None}
        
        if not valid_decisions:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'All checkpoints failed',
                'ensemble': True
            }
        
        # Weighted voting for actions
        action_scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        checkpoint_details = {}
        
        for checkpoint_name, decision in valid_decisions.items():
            action = decision.get('action', 'HOLD')
            confidence = decision.get('confidence', 0.0)
            weight = weights.get(checkpoint_name.replace('_', ''), 0.33)
            
            # Normalize checkpoint name for weight lookup
            weight_key = checkpoint_name.split('_')[0]  # 'arc', 'sudoku', 'maze'
            weight = weights.get(weight_key, 0.33)
            
            if action in action_scores:
                action_scores[action] += confidence * weight
            
            total_weight += weight
            
            checkpoint_details[checkpoint_name] = {
                'action': action,
                'confidence': confidence,
                'weight': weight
            }
        
        # Select best action
        best_action = max(action_scores, key=action_scores.get)
        final_confidence = action_scores[best_action] / max(total_weight, 0.001)
        
        # Calculate position size based on ensemble confidence
        position_size = self._calculate_ensemble_position_size(final_confidence, checkpoint_details)
        
        return {
            'action': best_action,
            'confidence': min(final_confidence, 1.0),
            'position_size': position_size,
            'regime': regime,
            'weights': weights,
            'checkpoint_decisions': checkpoint_details,
            'ensemble': True,
            'num_checkpoints': len(valid_decisions)
        }
    
    def _calculate_ensemble_position_size(self, confidence: float, checkpoint_details: Dict) -> float:
        """Calculate position size based on ensemble confidence and agreement"""
        # Base position size from confidence
        base_size = min(confidence * 0.1, 0.1)  # Max 10% of portfolio
        
        # Boost if checkpoints agree
        actions = [d['action'] for d in checkpoint_details.values()]
        if len(set(actions)) == 1:  # All agree
            base_size *= 1.5
        
        return min(base_size, 0.1)  # Cap at 10%
    
    def get_ensemble_metrics(self) -> Dict[str, Any]:
        """Get metrics about ensemble performance"""
        return {
            'active_checkpoints': len([e for e in self.engines.values() if e is not None]),
            'total_checkpoints': len(self.engines),
            'regime_weights': self.regime_weights
        }

