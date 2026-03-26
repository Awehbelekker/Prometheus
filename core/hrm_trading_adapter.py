#!/usr/bin/env python3
"""
HRM Trading Adapter
Adapter layer between Prometheus trading system and full HRM architecture
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime

# Lazy imports to avoid circular dependencies
try:
    from core.hrm_full_architecture import FullHRMArchitecture, HRMTradingConfig
except ImportError:
    FullHRMArchitecture = None
    HRMTradingConfig = None

try:
    from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
except ImportError:
    HRMReasoningContext = None
    HRMReasoningLevel = None

logger = logging.getLogger(__name__)


class HRMTradingAdapter:
    """
    Adapter between Prometheus trading system and full HRM architecture
    Handles conversion between trading data and HRM format
    """
    
    def __init__(self, hrm_architecture: FullHRMArchitecture):
        self.hrm = hrm_architecture
        self.device = hrm_architecture.device
        
        # Trading action vocabulary
        self.action_vocab = {
            0: 'HOLD',
            1: 'BUY',
            2: 'SELL',
            3: 'CLOSE',
            4: 'SCALE_IN',
            5: 'SCALE_OUT'
        }
        self.vocab_to_id = {v: k for k, v in self.action_vocab.items()}
        
        # Market regime mapping
        self.regime_map = {
            'bull': 0,
            'bear': 1,
            'sideways': 2,
            'volatile': 3
        }
    
    def encode_market_data(self, context: HRMReasoningContext) -> Tuple[torch.Tensor, int]:
        """
        Encode market data from context into HRM input tokens
        
        Args:
            context: HRM reasoning context with market data
        
        Returns:
            (tokens, market_regime_id) tuple
        """
        market_data = context.market_data
        
        # Extract features
        features = []
        
        # Price data
        if 'price' in market_data:
            price = float(market_data['price'])
            # Normalize and quantize price
            price_token = int(min(999, max(0, int(price * 10) % 1000)))
            features.append(price_token)
        
        # Volume data
        if 'volume' in market_data:
            volume = float(market_data['volume'])
            # Normalize and quantize volume
            volume_token = int(min(999, max(0, int(np.log10(max(1, volume))) * 50) % 1000))
            features.append(volume_token)
        
        # Technical indicators
        if 'indicators' in market_data:
            indicators = market_data['indicators']
            
            # RSI (0-100 -> 0-999)
            if 'rsi' in indicators:
                rsi = float(indicators['rsi'])
                rsi_token = int(min(999, max(0, int(rsi * 10))))
                features.append(rsi_token)
            
            # MACD (normalize to 0-999)
            if 'macd' in indicators:
                macd = float(indicators['macd'])
                macd_token = int(min(999, max(0, int((macd + 10) * 50) % 1000)))
                features.append(macd_token)
            
            # Bollinger Bands
            if 'bollinger_upper' in indicators and 'bollinger_lower' in indicators:
                upper = float(indicators['bollinger_upper'])
                lower = float(indicators['bollinger_lower'])
                price = float(market_data.get('price', 100))
                bb_width = ((upper - lower) / price) * 1000
                bb_token = int(min(999, max(0, int(bb_width))))
                features.append(bb_token)
        
        # Price history if available
        if 'price_history' in market_data:
            price_history = market_data['price_history']
            if isinstance(price_history, list) and len(price_history) > 0:
                # Take last N prices
                recent_prices = price_history[-20:] if len(price_history) >= 20 else price_history
                for price in recent_prices:
                    price_token = int(min(999, max(0, int(float(price) * 10) % 1000)))
                    features.append(price_token)
        
        # Pad or truncate to seq_len
        seq_len = self.hrm.config.seq_len
        if len(features) < seq_len:
            # Pad with zeros
            features.extend([0] * (seq_len - len(features)))
        else:
            # Truncate
            features = features[:seq_len]
        
        # Convert to tensor
        tokens = torch.tensor(features, dtype=torch.int32)
        
        # Determine market regime
        market_regime_id = self._detect_market_regime(market_data)
        
        return tokens, market_regime_id
    
    def _detect_market_regime(self, market_data: Dict[str, Any]) -> int:
        """
        Detect market regime from market data
        
        Returns:
            Market regime ID (0-3)
        """
        indicators = market_data.get('indicators', {})
        
        # Simple regime detection based on indicators
        if 'rsi' in indicators and 'macd' in indicators:
            rsi = float(indicators['rsi'])
            macd = float(indicators['macd'])
            
            # Volatile: High RSI variance or extreme values
            if rsi > 80 or rsi < 20:
                return self.regime_map['volatile']
            
            # Bull: Positive MACD and RSI > 50
            if macd > 0 and rsi > 50:
                return self.regime_map['bull']
            
            # Bear: Negative MACD and RSI < 50
            if macd < 0 and rsi < 50:
                return self.regime_map['bear']
        
        # Default to sideways
        return self.regime_map['sideways']
    
    def decode_hrm_output(self, hrm_output: Dict[str, Any], 
                         context: HRMReasoningContext) -> Dict[str, Any]:
        """
        Decode HRM output to trading decision
        
        Args:
            hrm_output: Output from HRM
            context: Original reasoning context
        
        Returns:
            Trading decision dictionary
        """
        action_id = hrm_output['action']
        confidence = hrm_output['confidence']
        
        # Map action ID to trading action
        action = self.action_vocab.get(action_id, 'HOLD')
        
        # Extract additional information
        logits = hrm_output.get('logits', [])
        
        # Calculate position size based on confidence
        position_size = self._calculate_position_size(confidence, context)
        
        # Determine risk level
        risk_level = self._assess_risk(confidence, hrm_output, context)
        
        return {
            'action': action,
            'confidence': confidence,
            'position_size': position_size,
            'risk_level': risk_level,
            'hrm_metadata': {
                'q_halt': hrm_output.get('q_halt', 0.0),
                'q_continue': hrm_output.get('q_continue', 0.0),
                'halt_steps': hrm_output.get('halt_steps', 0),
                'action_id': action_id
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_position_size(self, confidence: float, 
                                context: HRMReasoningContext) -> float:
        """
        Calculate position size based on confidence and risk preferences
        
        Args:
            confidence: HRM confidence score
            context: Reasoning context
        
        Returns:
            Position size (0.0 to 1.0)
        """
        # Base position size from risk preferences
        max_position = context.risk_preferences.get('max_position_size', 0.1)
        
        # Adjust based on confidence
        confidence_factor = confidence * 0.5 + 0.5  # 0.5 to 1.0
        
        # Calculate final position size
        position_size = max_position * confidence_factor
        
        # Ensure reasonable bounds
        return max(0.01, min(0.2, position_size))
    
    def _assess_risk(self, confidence: float, 
                    hrm_output: Dict[str, Any],
                    context: HRMReasoningContext) -> str:
        """
        Assess risk level of the decision
        
        Returns:
            Risk level string ('low', 'medium', 'high')
        """
        # Base risk from confidence
        if confidence > 0.8:
            base_risk = 'low'
        elif confidence > 0.6:
            base_risk = 'medium'
        else:
            base_risk = 'high'
        
        # Adjust based on halt steps (more steps = more computation = potentially more uncertainty)
        halt_steps = hrm_output.get('halt_steps', 0)
        if halt_steps > 6:
            # High computation might indicate uncertainty
            if base_risk == 'low':
                base_risk = 'medium'
            elif base_risk == 'medium':
                base_risk = 'high'
        
        return base_risk
    
    def make_trading_decision(self, context: HRMReasoningContext,
                            carry: Optional[Any] = None) -> Dict[str, Any]:
        """
        Make trading decision using full HRM
        
        Args:
            context: HRM reasoning context
            carry: Optional carry state from previous decision
        
        Returns:
            Trading decision dictionary
        """
        try:
            # Encode market data
            tokens, regime_id = self.encode_market_data(context)
            
            # Make HRM decision
            hrm_output = self.hrm.make_decision(
                market_data_tokens=tokens,
                market_regime_id=regime_id,
                carry=carry
            )
            
            # Decode to trading decision
            decision = self.decode_hrm_output(hrm_output, context)
            
            # Add carry for next iteration
            decision['carry'] = hrm_output.get('carry')
            
            logger.info(f"✅ HRM decision: {decision['action']} (confidence: {decision['confidence']:.3f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Error making HRM trading decision: {e}")
            # Fallback decision
            return {
                'action': 'HOLD',
                'confidence': 0.1,
                'position_size': 0.0,
                'risk_level': 'high',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

