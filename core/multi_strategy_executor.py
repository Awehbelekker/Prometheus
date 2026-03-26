"""
MULTI-STRATEGY EXECUTOR
=======================
Executes multiple trading strategies on the same opportunity to maximize profits.

Instead of one-trade-per-opportunity, this system:
- Identifies optimal strategy combinations
- Allocates capital across strategies
- Manages multiple positions simultaneously
- Aggregates results for maximum return

Example: BTC breakout detected
- Strategy 1: Momentum (60% capital, 3% target, hold 1-4 hours)
- Strategy 2: Scalp (30% capital, 0.8% target, hold 5-15 minutes)
- Strategy 3: Swing (10% capital, 8% target, hold 1-3 days)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.autonomous_market_scanner import TradingOpportunity, OpportunityType

# Import broker executor (uses existing broker infrastructure)
try:
    from core.autonomous_broker_executor import AutonomousBrokerExecutor
    BROKER_EXECUTOR_AVAILABLE = True
except ImportError:
    BROKER_EXECUTOR_AVAILABLE = False
    AutonomousBrokerExecutor = None

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    MOMENTUM = "momentum"
    SCALP = "scalp"
    SWING = "swing"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    ARBITRAGE = "arbitrage"

@dataclass
class StrategyConfig:
    """Configuration for a specific strategy"""
    strategy_type: StrategyType
    capital_allocation: float  # % of available capital
    profit_target: float  # % return target
    stop_loss: float  # % stop loss
    max_holding_time: int  # minutes
    min_confidence: float  # minimum confidence to execute

@dataclass
class StrategyExecution:
    """Result of executing a single strategy"""
    strategy_type: StrategyType
    symbol: str
    entry_price: float
    target_price: float
    stop_price: float
    capital_allocated: float
    quantity: float
    expected_return: float
    confidence: float
    executed_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, active, closed
    actual_return: float = 0.0

@dataclass
class MultiStrategyResult:
    """Aggregated result from multiple strategies"""
    symbol: str
    opportunity: TradingOpportunity
    strategies_executed: List[StrategyExecution]
    total_capital_allocated: float
    expected_total_return: float
    weighted_confidence: float
    execution_summary: str

class MultiStrategyExecutor:
    """
    Executes multiple strategies on the same opportunity
    """
    
    def __init__(self, enable_broker_execution=True):  # ENABLED by default
        # Strategy templates
        
        # Broker executor (optional - for real trading)
        self.broker_executor = None
        self.enable_broker_execution = enable_broker_execution
        
        if enable_broker_execution and BROKER_EXECUTOR_AVAILABLE:
            logger.info("✅ Broker execution ENABLED - autonomous real trading")
        else:
            logger.info("ℹ️  Broker execution DISABLED - simulation only")
        self.strategy_templates = {
            StrategyType.MOMENTUM: StrategyConfig(
                strategy_type=StrategyType.MOMENTUM,
                capital_allocation=0.50,  # 50% of capital
                profit_target=0.025,  # 2.5%
                stop_loss=0.015,  # 1.5%
                max_holding_time=180,  # 3 hours
                min_confidence=0.70
            ),
            StrategyType.SCALP: StrategyConfig(
                strategy_type=StrategyType.SCALP,
                capital_allocation=0.30,  # 30% of capital
                profit_target=0.008,  # 0.8%
                stop_loss=0.005,  # 0.5%
                max_holding_time=15,  # 15 minutes
                min_confidence=0.65
            ),
            StrategyType.SWING: StrategyConfig(
                strategy_type=StrategyType.SWING,
                capital_allocation=0.20,  # 20% of capital
                profit_target=0.05,  # 5%
                stop_loss=0.025,  # 2.5%
                max_holding_time=1440,  # 1 day
                min_confidence=0.75
            )
        }
        
        logger.info("🎯 Multi-Strategy Executor initialized")
    
    async def maximize_opportunity(self, 
                                   opportunity: TradingOpportunity,
                                   available_capital: float) -> MultiStrategyResult:
        """
        Maximize profits from an opportunity using multiple strategies
        
        Args:
            opportunity: The trading opportunity
            available_capital: Capital available for trading
        
        Returns:
            Multi-strategy execution result
        """
        logger.info(f"🎯 Maximizing opportunity: {opportunity.symbol}")
        logger.info(f"   Opportunity: {opportunity.opportunity_type.value}, "
                   f"{opportunity.expected_return:.1%} return")
        
        # Select optimal strategies for this opportunity
        selected_strategies = self._select_strategies(opportunity)
        
        if not selected_strategies:
            logger.warning(f"   No suitable strategies for {opportunity.symbol}")
            return MultiStrategyResult(
                symbol=opportunity.symbol,
                opportunity=opportunity,
                strategies_executed=[],
                total_capital_allocated=0,
                expected_total_return=0,
                weighted_confidence=0,
                execution_summary="No suitable strategies"
            )
        
        # Optimize capital allocation
        allocations = self._optimize_allocation(
            selected_strategies,
            available_capital,
            opportunity
        )
        
        # Execute all strategies
        executions = []
        total_allocated = 0
        
        for strategy, capital in zip(selected_strategies, allocations):
            execution = await self._execute_strategy(
                strategy,
                opportunity,
                capital
            )
            executions.append(execution)
            total_allocated += capital
            
            logger.info(f"   ✅ {strategy.strategy_type.value}: "
                       f"${capital:.2f} allocated, "
                       f"{strategy.profit_target:.1%} target")
        
        # Calculate aggregate metrics
        expected_total_return = sum(
            e.expected_return * e.capital_allocated for e in executions
        ) / total_allocated if total_allocated > 0 else 0
        
        weighted_confidence = sum(
            e.confidence * e.capital_allocated for e in executions
        ) / total_allocated if total_allocated > 0 else 0
        
        summary = (
            f"{len(executions)} strategies on {opportunity.symbol}: "
            f"${total_allocated:.2f} capital, "
            f"{expected_total_return:.1%} expected return"
        )
        
        logger.info(f"✅ Multi-strategy execution complete")
        logger.info(f"   {summary}")
        
        return MultiStrategyResult(
            symbol=opportunity.symbol,
            opportunity=opportunity,
            strategies_executed=executions,
            total_capital_allocated=total_allocated,
            expected_total_return=expected_total_return,
            weighted_confidence=weighted_confidence,
            execution_summary=summary
        )
    
    def _select_strategies(self, opportunity: TradingOpportunity) -> List[StrategyConfig]:
        """Select optimal strategies for the opportunity"""
        selected = []
        
        # Base strategy selection on opportunity type and characteristics
        if opportunity.opportunity_type in [OpportunityType.MOMENTUM, OpportunityType.BREAKOUT]:
            # High momentum - use momentum + scalp
            if opportunity.confidence >= self.strategy_templates[StrategyType.MOMENTUM].min_confidence:
                selected.append(self.strategy_templates[StrategyType.MOMENTUM])
            if opportunity.volume_score > 0.7:
                selected.append(self.strategy_templates[StrategyType.SCALP])
        
        elif opportunity.opportunity_type == OpportunityType.REVERSAL:
            # Reversal - use swing + scalp
            if opportunity.confidence >= self.strategy_templates[StrategyType.SWING].min_confidence:
                selected.append(self.strategy_templates[StrategyType.SWING])
            selected.append(self.strategy_templates[StrategyType.SCALP])
        
        else:
            # Default: momentum strategy
            if opportunity.confidence >= 0.65:
                selected.append(self.strategy_templates[StrategyType.MOMENTUM])
        
        # Add swing for high-confidence opportunities
        if opportunity.confidence >= 0.80 and opportunity.expected_return >= 0.03:
            if StrategyType.SWING not in [s.strategy_type for s in selected]:
                selected.append(self.strategy_templates[StrategyType.SWING])
        
        return selected
    
    def _optimize_allocation(self,
                            strategies: List[StrategyConfig],
                            available_capital: float,
                            opportunity: TradingOpportunity) -> List[float]:
        """Optimize capital allocation across strategies"""
        if not strategies:
            return []
        
        # Start with template allocations
        base_allocations = [s.capital_allocation for s in strategies]
        total_base = sum(base_allocations)
        
        # Normalize to sum to 1.0
        normalized = [a / total_base for a in base_allocations]
        
        # Apply available capital
        allocations = [a * available_capital for a in normalized]
        
        # Ensure minimum position size
        min_position = 5.0
        allocations = [max(a, min_position) for a in allocations]
        
        # Adjust if total exceeds available
        total = sum(allocations)
        if total > available_capital:
            scale = available_capital / total
            allocations = [a * scale for a in allocations]
        
        return allocations
    
    async def _execute_strategy(self,
                                strategy: StrategyConfig,
                                opportunity: TradingOpportunity,
                                capital: float) -> StrategyExecution:
        """Execute a single strategy"""
        entry_price = opportunity.entry_price
        target_price = entry_price * (1 + strategy.profit_target)
        stop_price = entry_price * (1 - strategy.stop_loss)
        
        # Calculate quantity
        quantity = capital / entry_price
        
        expected_return = strategy.profit_target
        confidence = min(opportunity.confidence, 0.95)
        
        # Create execution record
        execution = StrategyExecution(
            strategy_type=strategy.strategy_type,
            symbol=opportunity.symbol,
            entry_price=entry_price,
            target_price=target_price,
            stop_price=stop_price,
            capital_allocated=capital,
            quantity=quantity,
            expected_return=expected_return,
            confidence=confidence,
            status="pending"
        )
        
        # Execute with broker if enabled
        if self.enable_broker_execution and self.broker_executor:
            try:
                result = await self.broker_executor.execute_strategy(
                    symbol=opportunity.symbol,
                    strategy_type=strategy.strategy_type.value,
                    capital_allocated=capital,
                    entry_price=entry_price,
                    target_price=target_price,
                    stop_price=stop_price
                )
                
                if result.success:
                    execution.status = "filled"
                    logger.info(f"   [EXECUTED] {result.broker_name} order: {result.order_id}")
                else:
                    execution.status = "rejected"
                    logger.warning(f"   [REJECTED] {result.error_message}")
                    
            except Exception as e:
                logger.error(f"   [ERROR] Broker execution failed: {e}")
                execution.status = "error"
        else:
            # Simulation mode
            execution.status = "simulated"
        
        return execution
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get executor statistics"""
        return {
            'available_strategies': len(self.strategy_templates),
            'strategies': [s.value for s in self.strategy_templates.keys()]
        }

# Global instance
multi_strategy_executor = MultiStrategyExecutor()

