#!/usr/bin/env python3
"""
HRM Trading Decoder
Decodes HRM outputs to trading decisions (BUY/SELL/HOLD, position sizes)
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HRMTradingDecoder:
    """
    Decodes HRM model outputs to trading decisions
    Maps logits to actions and calculates position sizes
    """
    
    def __init__(self):
        # Trading action vocabulary (must match encoder)
        self.action_vocab = {
            0: 'HOLD',
            1: 'BUY',
            2: 'SELL',
            3: 'CLOSE',
            4: 'SCALE_IN',
            5: 'SCALE_OUT'
        }
        
        # Action priorities (for multi-action scenarios)
        self.action_priority = {
            'BUY': 1,
            'SELL': 2,
            'CLOSE': 3,
            'SCALE_IN': 4,
            'SCALE_OUT': 5,
            'HOLD': 6
        }
    
    def decode_logits(self, logits: torch.Tensor, 
                     top_k: int = 1) -> Dict[str, Any]:
        """
        Decode logits to action predictions
        
        Args:
            logits: HRM output logits [batch_size, seq_len, vocab_size] or [vocab_size]
            top_k: Number of top predictions to return
        
        Returns:
            Dictionary with predictions
        """
        # Handle different input shapes
        if logits.dim() == 3:
            # Take last token prediction
            logits = logits[:, -1, :]
        elif logits.dim() == 2:
            # Already [batch_size, vocab_size]
            pass
        elif logits.dim() == 1:
            # Single prediction
            logits = logits.unsqueeze(0)
        
        # Get batch size
        batch_size = logits.shape[0]
        
        # Apply softmax
        probs = torch.softmax(logits, dim=-1)
        
        # Get top-k predictions
        top_probs, top_indices = torch.topk(probs, k=min(top_k, probs.shape[-1]), dim=-1)
        
        predictions = []
        for i in range(batch_size):
            batch_predictions = []
            for j in range(top_k):
                action_id = top_indices[i, j].item()
                prob = top_probs[i, j].item()
                action = self.action_vocab.get(action_id, 'HOLD')
                
                batch_predictions.append({
                    'action': action,
                    'action_id': action_id,
                    'probability': prob,
                    'confidence': prob
                })
            
            predictions.append(batch_predictions)
        
        # Return single prediction if batch_size == 1
        if batch_size == 1:
            return {
                'predictions': predictions[0],
                'primary_action': predictions[0][0]['action'],
                'primary_confidence': predictions[0][0]['confidence']
            }
        else:
            return {
                'predictions': predictions,
                'primary_action': [p[0]['action'] for p in predictions],
                'primary_confidence': [p[0]['confidence'] for p in predictions]
            }
    
    def calculate_position_size(self, confidence: float,
                               action: str,
                               risk_preferences: Dict[str, float],
                               current_portfolio: Dict[str, Any]) -> float:
        """
        Calculate position size based on confidence and risk preferences
        
        Args:
            confidence: Confidence score (0-1)
            action: Trading action
            risk_preferences: Risk preference dictionary
            current_portfolio: Current portfolio state
        
        Returns:
            Position size (0.0 to 1.0)
        """
        # Base position size from risk preferences
        max_position = risk_preferences.get('max_position_size', 0.1)
        
        # Adjust based on confidence
        confidence_factor = confidence
        
        # Adjust based on action type
        action_factors = {
            'BUY': 1.0,
            'SELL': 1.0,
            'SCALE_IN': 0.5,
            'SCALE_OUT': 0.5,
            'CLOSE': 1.0,
            'HOLD': 0.0
        }
        action_factor = action_factors.get(action, 0.0)
        
        # Calculate position size
        position_size = max_position * confidence_factor * action_factor
        
        # Apply risk limits
        max_drawdown = risk_preferences.get('max_drawdown', 0.2)
        if 'current_drawdown' in current_portfolio:
            current_dd = current_portfolio['current_drawdown']
            if current_dd > max_drawdown * 0.8:  # Near limit
                position_size *= 0.5  # Reduce position size
        
        # Ensure reasonable bounds
        return max(0.0, min(max_position, position_size))
    
    def determine_stop_loss(self, action: str,
                           confidence: float,
                           entry_price: float,
                           risk_preferences: Dict[str, float]) -> Optional[float]:
        """
        Determine stop loss price
        
        Args:
            action: Trading action
            confidence: Confidence score
            entry_price: Entry price
            risk_preferences: Risk preferences
        
        Returns:
            Stop loss price or None
        """
        if action not in ['BUY', 'SELL']:
            return None
        
        # Base stop loss percentage
        stop_loss_pct = risk_preferences.get('stop_loss_percent', 0.02)  # 2%
        
        # Adjust based on confidence (higher confidence = tighter stop)
        confidence_factor = 0.5 + (1 - confidence) * 0.5  # 0.5 to 1.0
        stop_loss_pct *= confidence_factor
        
        if action == 'BUY':
            stop_loss = entry_price * (1 - stop_loss_pct)
        else:  # SELL
            stop_loss = entry_price * (1 + stop_loss_pct)
        
        return stop_loss
    
    def determine_take_profit(self, action: str,
                            confidence: float,
                            entry_price: float,
                            risk_preferences: Dict[str, float]) -> Optional[float]:
        """
        Determine take profit price
        
        Args:
            action: Trading action
            confidence: Confidence score
            entry_price: Entry price
            risk_preferences: Risk preferences
        
        Returns:
            Take profit price or None
        """
        if action not in ['BUY', 'SELL']:
            return None
        
        # Base take profit percentage
        take_profit_pct = risk_preferences.get('take_profit_percent', 0.04)  # 4%
        
        # Adjust based on confidence (higher confidence = higher target)
        confidence_factor = 0.8 + confidence * 0.4  # 0.8 to 1.2
        take_profit_pct *= confidence_factor
        
        if action == 'BUY':
            take_profit = entry_price * (1 + take_profit_pct)
        else:  # SELL
            take_profit = entry_price * (1 - take_profit_pct)
        
        return take_profit
    
    def decode_to_trading_decision(self, hrm_output: Dict[str, Any],
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decode HRM output to complete trading decision
        
        Args:
            hrm_output: HRM model output
            context: Trading context (risk_preferences, current_portfolio, etc.)
        
        Returns:
            Complete trading decision dictionary
        """
        # Extract logits
        logits = hrm_output.get('logits')
        if logits is None:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'error': 'No logits in HRM output'
            }
        
        # Convert to tensor if needed
        if isinstance(logits, list):
            logits = torch.tensor(logits)
        
        # Decode predictions
        decoded = self.decode_logits(logits, top_k=3)
        
        primary_action = decoded['primary_action']
        primary_confidence = decoded['primary_confidence']
        
        # Get context
        risk_preferences = context.get('risk_preferences', {})
        current_portfolio = context.get('current_portfolio', {})
        market_data = context.get('market_data', {})
        
        # Calculate position size
        position_size = self.calculate_position_size(
            primary_confidence,
            primary_action,
            risk_preferences,
            current_portfolio
        )
        
        # Determine stop loss and take profit
        entry_price = market_data.get('price')
        stop_loss = None
        take_profit = None
        
        if entry_price and primary_action in ['BUY', 'SELL']:
            stop_loss = self.determine_stop_loss(
                primary_action,
                primary_confidence,
                float(entry_price),
                risk_preferences
            )
            take_profit = self.determine_take_profit(
                primary_action,
                primary_confidence,
                float(entry_price),
                risk_preferences
            )
        
        # Build decision
        decision = {
            'action': primary_action,
            'confidence': primary_confidence,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'alternative_actions': decoded.get('predictions', [])[1:] if len(decoded.get('predictions', [])) > 1 else [],
            'hrm_metadata': {
                'q_halt': hrm_output.get('q_halt', 0.0),
                'q_continue': hrm_output.get('q_continue', 0.0),
                'halt_steps': hrm_output.get('halt_steps', 0)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return decision

