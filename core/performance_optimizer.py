#!/usr/bin/env python3
"""
Performance Optimizer - Improve Win Rate, Profitability, and Decision Speed
Addresses the three key areas needing improvement
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np
from collections import deque
import time

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """
    Optimizes three key areas:
    1. Win Rate (target >50%)
    2. Profitability (target positive returns)
    3. Decision Speed (target <100ms)
    """
    
    def __init__(self):
        # Win Rate Optimization
        self.confidence_threshold = 0.3  # Start conservative
        self.min_confidence_for_trade = 0.4  # Only trade with higher confidence
        self.win_rate_history = deque(maxlen=100)
        self.trade_outcomes = deque(maxlen=1000)
        
        # Profitability Optimization
        self.reward_multiplier = 1.0
        self.risk_reward_ratio = 2.0  # Target 2:1 risk/reward
        self.position_sizing_factor = 0.05  # Start with 5% position size
        
        # Decision Speed Optimization
        self.decision_cache = {}
        self.cache_ttl = 60  # Cache for 60 seconds
        self.parallel_processing = True
        self.last_decision_time = 0.0
        
        # Performance tracking
        self.metrics = {
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'avg_decision_time': 0.0,
            'total_trades': 0,
            'winning_trades': 0
        }
        
        logger.info("✅ Performance Optimizer initialized")
    
    def optimize_win_rate(self, decision: Dict, market_data: Dict) -> Dict:
        """
        Optimize win rate by:
        1. Higher confidence threshold
        2. Better entry conditions
        3. Context-aware filtering
        """
        original_confidence = decision.get('confidence', 0.0)
        action = decision.get('action', 'HOLD')
        
        # Calculate dynamic confidence threshold based on win rate
        if len(self.win_rate_history) > 10:
            avg_win_rate = np.mean(list(self.win_rate_history))
            # If win rate is low, be more conservative
            if avg_win_rate < 0.4:
                self.min_confidence_for_trade = 0.5
            elif avg_win_rate < 0.5:
                self.min_confidence_for_trade = 0.45
            else:
                self.min_confidence_for_trade = 0.4
        
        # Apply confidence threshold
        if action != 'HOLD' and original_confidence < self.min_confidence_for_trade:
            logger.info(f"  ⚠️ Confidence too low ({original_confidence:.3f} < {self.min_confidence_for_trade:.3f}), changing to HOLD")
            decision['action'] = 'HOLD'
            decision['confidence'] = original_confidence
            decision['reason'] = 'confidence_threshold'
        
        # Context-aware filtering
        if action != 'HOLD':
            # Check market conditions
            indicators = market_data.get('indicators', {})
            rsi = indicators.get('rsi', 50)
            volatility = indicators.get('volatility', 0)
            
            # Filter out trades in extreme conditions
            if action == 'BUY' and rsi > 80:
                logger.info(f"  ⚠️ RSI too high ({rsi:.1f}), changing to HOLD")
                decision['action'] = 'HOLD'
                decision['reason'] = 'rsi_too_high'
            elif action == 'SELL' and rsi < 20:
                logger.info(f"  ⚠️ RSI too low ({rsi:.1f}), changing to HOLD")
                decision['action'] = 'HOLD'
                decision['reason'] = 'rsi_too_low'
            
            # Filter out trades in high volatility without high confidence
            if volatility > 0.05 and original_confidence < 0.6:
                logger.info(f"  ⚠️ High volatility ({volatility:.3f}) with low confidence, changing to HOLD")
                decision['action'] = 'HOLD'
                decision['reason'] = 'high_volatility'
        
        # Adjust position size based on confidence
        if decision['action'] != 'HOLD':
            confidence_multiplier = max(0.5, min(1.0, original_confidence))
            decision['position_size'] = decision.get('position_size', 0.1) * confidence_multiplier
        
        return decision
    
    def optimize_profitability(self, decision: Dict, market_data: Dict, portfolio: Dict) -> Dict:
        """
        Optimize profitability by:
        1. Better risk/reward ratio
        2. Dynamic position sizing
        3. Profit-taking logic
        """
        if decision.get('action') == 'HOLD':
            return decision
        
        # Calculate risk/reward ratio
        indicators = market_data.get('indicators', {})
        price = market_data.get('price', 100.0)
        
        # Estimate stop loss and take profit
        volatility = indicators.get('volatility', 0.02)
        stop_loss_pct = volatility * 2  # 2x volatility for stop loss
        take_profit_pct = stop_loss_pct * self.risk_reward_ratio  # Target 2:1
        
        # Adjust position size based on risk
        risk_per_trade = portfolio.get('total_value', 10000) * 0.01  # Risk 1% per trade
        position_size = risk_per_trade / (price * stop_loss_pct)
        max_position_size = portfolio.get('total_value', 10000) * self.position_sizing_factor
        
        decision['position_size'] = min(position_size / portfolio.get('total_value', 10000), max_position_size)
        decision['stop_loss'] = price * (1 - stop_loss_pct)
        decision['take_profit'] = price * (1 + take_profit_pct)
        decision['risk_reward_ratio'] = self.risk_reward_ratio
        
        # Adjust based on recent profitability
        if len(self.trade_outcomes) > 10:
            recent_profits = [o.get('profit', 0) for o in list(self.trade_outcomes)[-10:]]
            avg_recent_profit = np.mean(recent_profits)
            
            if avg_recent_profit < 0:
                # Reduce position size if recent losses
                decision['position_size'] *= 0.7
                logger.info(f"  ⚠️ Recent losses detected, reducing position size")
            elif avg_recent_profit > 0:
                # Slightly increase if profitable
                decision['position_size'] *= 1.1
                decision['position_size'] = min(decision['position_size'], max_position_size)
        
        return decision
    
    def optimize_decision_speed(self, decision_func, *args, **kwargs) -> Dict:
        """
        Optimize decision speed by:
        1. Caching results
        2. Parallel processing
        3. Early exits
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key(*args, **kwargs)
        if cache_key in self.decision_cache:
            cached_result, cache_time = self.decision_cache[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                elapsed = (time.time() - start_time) * 1000
                logger.debug(f"  ⚡ Cache hit! Decision time: {elapsed:.2f}ms")
                return cached_result
        
        # Make decision
        if self.parallel_processing and asyncio.iscoroutinefunction(decision_func):
            # Run async decision
            decision = asyncio.run(decision_func(*args, **kwargs))
        else:
            decision = decision_func(*args, **kwargs)
        
        # Cache result
        self.decision_cache[cache_key] = (decision, time.time())
        
        # Clean old cache entries
        if len(self.decision_cache) > 100:
            oldest_key = min(self.decision_cache.keys(), 
                           key=lambda k: self.decision_cache[k][1])
            del self.decision_cache[oldest_key]
        
        elapsed = (time.time() - start_time) * 1000
        self.last_decision_time = elapsed
        
        # Update average
        if self.metrics['avg_decision_time'] == 0:
            self.metrics['avg_decision_time'] = elapsed
        else:
            self.metrics['avg_decision_time'] = (self.metrics['avg_decision_time'] * 0.9 + elapsed * 0.1)
        
        return decision
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Use market data price and timestamp for cache key
        if args and isinstance(args[0], dict):
            market_data = args[0]
            price = market_data.get('price', 0)
            timestamp = market_data.get('timestamp', '')
            return f"{price:.2f}_{timestamp}"
        return str(hash(str(args) + str(kwargs)))
    
    def update_from_outcome(self, decision: Dict, outcome: Dict):
        """
        Update optimizer based on trade outcome
        """
        profit = outcome.get('profit', 0)
        success = outcome.get('success', False)
        
        # Update win rate
        self.trade_outcomes.append({
            'profit': profit,
            'success': success,
            'decision': decision,
            'timestamp': datetime.now()
        })
        
        if success:
            self.metrics['winning_trades'] += 1
        self.metrics['total_trades'] += 1
        
        # Calculate win rate
        if self.metrics['total_trades'] > 0:
            self.metrics['win_rate'] = self.metrics['winning_trades'] / self.metrics['total_trades']
            self.win_rate_history.append(self.metrics['win_rate'])
        
        # Update average profit
        if profit != 0:
            if self.metrics['avg_profit'] == 0:
                self.metrics['avg_profit'] = profit
            else:
                self.metrics['avg_profit'] = (self.metrics['avg_profit'] * 0.9 + profit * 0.1)
        
        # Adaptive adjustments
        if len(self.win_rate_history) > 20:
            recent_win_rate = np.mean(list(self.win_rate_history)[-20:])
            
            if recent_win_rate < 0.4:
                # Win rate too low - be more conservative
                self.min_confidence_for_trade = min(0.6, self.min_confidence_for_trade + 0.05)
                self.position_sizing_factor = max(0.03, self.position_sizing_factor - 0.01)
                logger.info(f"  📉 Win rate low ({recent_win_rate:.1%}), increasing confidence threshold to {self.min_confidence_for_trade:.2f}")
            elif recent_win_rate > 0.55:
                # Win rate good - can be slightly less conservative
                self.min_confidence_for_trade = max(0.35, self.min_confidence_for_trade - 0.02)
                self.position_sizing_factor = min(0.08, self.position_sizing_factor + 0.01)
                logger.info(f"  📈 Win rate good ({recent_win_rate:.1%}), reducing confidence threshold to {self.min_confidence_for_trade:.2f}")
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            'win_rate': {
                'current': self.metrics['win_rate'],
                'target': 0.5,
                'status': '✅' if self.metrics['win_rate'] >= 0.5 else '⚠️',
                'confidence_threshold': self.min_confidence_for_trade
            },
            'profitability': {
                'avg_profit': self.metrics['avg_profit'],
                'total_trades': self.metrics['total_trades'],
                'winning_trades': self.metrics['winning_trades'],
                'status': '✅' if self.metrics['avg_profit'] > 0 else '⚠️'
            },
            'decision_speed': {
                'avg_time_ms': self.metrics['avg_decision_time'],
                'target_ms': 100.0,
                'status': '✅' if self.metrics['avg_decision_time'] < 100 else '⚠️',
                'cache_size': len(self.decision_cache)
            }
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics = {
            'win_rate': 0.0,
            'avg_profit': 0.0,
            'avg_decision_time': 0.0,
            'total_trades': 0,
            'winning_trades': 0
        }
        self.win_rate_history.clear()
        self.trade_outcomes.clear()
        self.decision_cache.clear()
        logger.info("✅ Metrics reset")


class OptimizedTradingSystem:
    """
    Wrapper around Ultimate Trading System with performance optimization
    """
    
    def __init__(self):
        from core.ultimate_trading_system import UltimateTradingSystem
        self.base_system = UltimateTradingSystem()
        self.optimizer = PerformanceOptimizer()
        logger.info("✅ Optimized Trading System initialized")
    
    def make_optimized_decision(self, market_data: Dict, portfolio: Dict = None, context: Dict = None) -> Dict[str, Any]:
        """
        Make optimized trading decision with all three optimizations
        """
        portfolio = portfolio or {}
        context = context or {}
        
        # 1. Get base decision (with speed optimization)
        decision = self.optimizer.optimize_decision_speed(
            self.base_system.make_ultimate_decision,
            market_data=market_data,
            portfolio=portfolio,
            context=context
        )
        
        # 2. Optimize win rate
        decision = self.optimizer.optimize_win_rate(decision, market_data)
        
        # 3. Optimize profitability
        decision = self.optimizer.optimize_profitability(decision, market_data, portfolio)
        
        # Add optimization metadata
        decision['optimized'] = True
        decision['optimization_metrics'] = self.optimizer.get_optimization_status()
        
        return decision
    
    def learn_from_outcome(self, decision: Dict, outcome: Dict):
        """Learn from outcome with optimization"""
        # Update base system
        self.base_system.learn_from_outcome(decision, outcome)
        
        # Update optimizer
        self.optimizer.update_from_outcome(decision, outcome)
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        base_status = self.base_system.get_system_status()
        optimization_status = self.optimizer.get_optimization_status()
        
        return {
            'base_system': base_status,
            'optimization': optimization_status,
            'metrics': self.optimizer.metrics
        }

