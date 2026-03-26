#!/usr/bin/env python3
"""
Backtest-Optimized Performance Optimizer
Less conservative settings for backtesting scenarios
"""

import logging
import numpy as np
from typing import Dict, Any
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

# Import base optimizer
from core.performance_optimizer import PerformanceOptimizer


class BacktestOptimizer(PerformanceOptimizer):
    """
    Backtest-optimized version with less conservative settings
    """
    
    def __init__(self):
        # Call parent init
        super().__init__()
        
        # Override with backtest-friendly settings
        self.min_confidence_for_trade = 0.25  # Lower threshold for backtesting (was 0.4)
        self.confidence_threshold = 0.2  # Lower base threshold (was 0.3)
        self.position_sizing_factor = 0.08  # Slightly higher position sizing (was 0.05)
        
        # Less aggressive filtering for backtesting
        self.rsi_upper_limit = 85  # More lenient (was implicit 80)
        self.rsi_lower_limit = 15  # More lenient (was implicit 20)
        self.volatility_threshold = 0.08  # Higher threshold (was 0.05)
        self.volatility_confidence_requirement = 0.5  # Lower requirement (was 0.6)
        
        logger.info("✅ Backtest Optimizer initialized (less conservative settings)")
    
    def optimize_win_rate(self, decision: Dict, market_data: Dict) -> Dict:
        """
        Optimize win rate with backtest-friendly settings
        """
        original_confidence = decision.get('confidence', 0.0)
        action = decision.get('action', 'HOLD')
        
        # For backtesting, use fixed lower threshold (don't adapt based on win rate initially)
        # Only adapt if we have significant history
        if len(self.win_rate_history) > 50:  # Need more history before adapting
            avg_win_rate = np.mean(list(self.win_rate_history)[-50:])
            if avg_win_rate < 0.35:
                self.min_confidence_for_trade = 0.35
            elif avg_win_rate < 0.45:
                self.min_confidence_for_trade = 0.30
            else:
                self.min_confidence_for_trade = 0.25
        else:
            # Use fixed lower threshold for backtesting
            self.min_confidence_for_trade = 0.25
        
        # Apply confidence threshold (more lenient)
        if action != 'HOLD' and original_confidence < self.min_confidence_for_trade:
            # For backtesting, log but don't filter as aggressively
            if original_confidence < 0.15:  # Only filter very low confidence
                decision['action'] = 'HOLD'
                decision['reason'] = 'confidence_threshold'
            # Otherwise, allow the trade with lower confidence
        
        # Context-aware filtering (less aggressive)
        if action != 'HOLD':
            indicators = market_data.get('indicators', {})
            rsi = indicators.get('rsi', 50)
            volatility = indicators.get('volatility', 0)
            
            # More lenient RSI filtering
            if action == 'BUY' and rsi > self.rsi_upper_limit:
                decision['action'] = 'HOLD'
                decision['reason'] = 'rsi_too_high'
            elif action == 'SELL' and rsi < self.rsi_lower_limit:
                decision['action'] = 'HOLD'
                decision['reason'] = 'rsi_too_low'
            
            # More lenient volatility filtering
            if volatility > self.volatility_threshold and original_confidence < self.volatility_confidence_requirement:
                decision['action'] = 'HOLD'
                decision['reason'] = 'high_volatility'
        
        # Adjust position size based on confidence
        if decision['action'] != 'HOLD':
            confidence_multiplier = max(0.4, min(1.0, original_confidence))  # Lower minimum (was 0.5)
            decision['position_size'] = decision.get('position_size', 0.1) * confidence_multiplier
        
        return decision



