#!/usr/bin/env python3
"""
PROMETHEUS Enhanced Agent Integration
======================================
Integrates new market intelligence agents with existing hierarchical agent coordinator.

Features:
- Seamless integration of new agents into existing system
- Enhanced decision aggregation with performance weighting
- Automatic agent selection based on market conditions
- Performance-based agent optimization
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import existing systems
from core.hierarchical_agent_coordinator import (
    HierarchicalAgentCoordinator,
    TradingDecision,
    AgentType
)

# Import new intelligence agents
from core.market_intelligence_agents import (
    get_gap_detection_agent,
    get_opportunity_scanner_agent,
    get_market_research_agent
)

# Import performance optimizer
from core.agent_performance_optimizer import get_performance_optimizer

logger = logging.getLogger(__name__)


class EnhancedAgentCoordinator:
    """
    Enhanced coordinator that integrates new intelligence agents
    with existing hierarchical agent system
    """
    
    def __init__(self):
        # Use existing hierarchical coordinator
        self.base_coordinator = HierarchicalAgentCoordinator()
        
        # Add new intelligence agents
        self.gap_agent = get_gap_detection_agent()
        self.opportunity_agent = get_opportunity_scanner_agent()
        self.research_agent = get_market_research_agent()
        
        # Performance optimizer
        self.performance_optimizer = get_performance_optimizer()
        
        # Agent registry (combines existing + new agents)
        self.all_agents = {
            'gap_detector': self.gap_agent,
            'opportunity_scanner': self.opportunity_agent,
            'market_researcher': self.research_agent
        }
        
        # Agent weights (performance-based)
        self.agent_weights = {}

        # Count execution agents
        total_execution_agents = sum(len(agents) for agents in self.base_coordinator.execution_swarm.values())

        logger.info("🚀 Enhanced Agent Coordinator initialized")
        logger.info(f"  Base agents: {total_execution_agents}")
        logger.info(f"  Intelligence agents: {len(self.all_agents)}")
    
    async def initialize(self):
        """Initialize all agents and load performance data"""
        logger.info("🔧 Initializing Enhanced Agent Coordinator...")

        # Base coordinator is already initialized in __init__
        # No need to call initialize() as it doesn't exist

        # Load agent weights from performance history
        self.agent_weights = await self.performance_optimizer.optimize_agent_weights()

        logger.info("[CHECK] Enhanced Agent Coordinator ready")
    
    async def get_trading_recommendations(
        self,
        symbols: List[str],
        market_data: Dict[str, Any]
    ) -> List[TradingDecision]:
        """
        Get comprehensive trading recommendations from all agents
        
        Args:
            symbols: List of symbols to analyze
            market_data: Current market data
        
        Returns:
            List of trading decisions from all agents
        """
        logger.info(f"🤖 Getting recommendations for {len(symbols)} symbols...")
        
        all_decisions = []
        
        # 1. Get decisions from existing hierarchical agents
        logger.info("  📊 Consulting existing agents...")
        for symbol in symbols:
            symbol_data = market_data.get(symbol, {})
            symbol_data['symbol'] = symbol
            
            # Get decision from base coordinator
            base_decision = await self.base_coordinator.coordinate_trading_decision(symbol_data)
            if base_decision:
                all_decisions.append(base_decision)
                
                # Record decision for performance tracking
                await self.performance_optimizer.record_decision(base_decision)
        
        # 2. Get intelligence from new agents
        logger.info("  🔍 Consulting intelligence agents...")
        
        # Gap detection
        gaps = await self.gap_agent.scan_for_gaps(symbols)
        logger.info(f"    Found {len(gaps)} gaps")
        
        # Opportunity scanning
        opportunities = await self.opportunity_agent.scan_all_opportunities(symbols)
        logger.info(f"    Found {len(opportunities)} opportunities")
        
        # Market research
        intelligence = await self.research_agent.generate_market_intelligence(symbols)
        logger.info(f"    Market regime: {intelligence.market_regime}")
        
        # 3. Convert intelligence to trading decisions
        for symbol in symbols:
            symbol_data = {'symbol': symbol}
            
            # Get decisions from intelligence agents
            gap_decision = await self.gap_agent.analyze(symbol_data)
            opp_decision = await self.opportunity_agent.analyze(symbol_data)
            research_decision = await self.research_agent.analyze(symbol_data)
            
            # Add to decisions list
            for decision in [gap_decision, opp_decision, research_decision]:
                if decision.action != 'hold':
                    all_decisions.append(decision)
                    await self.performance_optimizer.record_decision(decision)
        
        logger.info(f"[CHECK] Generated {len(all_decisions)} total recommendations")
        
        return all_decisions
    
    async def aggregate_decisions(
        self,
        decisions: List[TradingDecision],
        use_performance_weighting: bool = True
    ) -> Dict[str, TradingDecision]:
        """
        Aggregate decisions from multiple agents with performance weighting
        
        Args:
            decisions: List of trading decisions
            use_performance_weighting: Whether to use performance-based weights
        
        Returns:
            Dictionary of symbol -> aggregated decision
        """
        logger.info(f"🎯 Aggregating {len(decisions)} decisions...")
        
        # Group decisions by symbol
        decisions_by_symbol = {}
        for decision in decisions:
            if decision.symbol not in decisions_by_symbol:
                decisions_by_symbol[decision.symbol] = []
            decisions_by_symbol[decision.symbol].append(decision)
        
        # Aggregate for each symbol
        aggregated = {}
        
        for symbol, symbol_decisions in decisions_by_symbol.items():
            # Get agent weights
            if use_performance_weighting and self.agent_weights:
                weights = [
                    self.agent_weights.get(d.agent_id, 1.0)
                    for d in symbol_decisions
                ]
            else:
                weights = [1.0] * len(symbol_decisions)
            
            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]
            
            # Calculate weighted confidence
            weighted_confidence = sum(
                d.confidence * w
                for d, w in zip(symbol_decisions, weights)
            )
            
            # Determine action by majority vote (weighted)
            action_scores = {'buy': 0, 'sell': 0, 'hold': 0}
            for decision, weight in zip(symbol_decisions, weights):
                action_scores[decision.action] += weight
            
            best_action = max(action_scores, key=action_scores.get)
            
            # Find best decision with that action
            best_decision = max(
                [d for d in symbol_decisions if d.action == best_action],
                key=lambda d: d.confidence
            )
            
            # Create aggregated decision
            aggregated[symbol] = TradingDecision(
                agent_id="enhanced_coordinator",
                agent_type=AgentType.SUPERVISOR,
                symbol=symbol,
                action=best_action,
                quantity=best_decision.quantity,
                price=best_decision.price,
                confidence=weighted_confidence,
                reasoning=f"Aggregated from {len(symbol_decisions)} agents: {best_decision.reasoning}",
                risk_score=best_decision.risk_score,
                expected_return=best_decision.expected_return,
                timeframe=best_decision.timeframe
            )
        
        logger.info(f"[CHECK] Aggregated decisions for {len(aggregated)} symbols")
        
        return aggregated
    
    async def execute_with_intelligence(
        self,
        symbols: List[str],
        market_data: Dict[str, Any]
    ) -> Dict[str, TradingDecision]:
        """
        Complete workflow: get recommendations, aggregate, and return final decisions
        
        Args:
            symbols: List of symbols to trade
            market_data: Current market data
        
        Returns:
            Final trading decisions per symbol
        """
        logger.info("🚀 Executing enhanced trading intelligence workflow...")
        
        # Get all recommendations
        decisions = await self.get_trading_recommendations(symbols, market_data)
        
        # Aggregate with performance weighting
        final_decisions = await self.aggregate_decisions(
            decisions,
            use_performance_weighting=True
        )
        
        logger.info(f"[CHECK] Final decisions ready for {len(final_decisions)} symbols")
        
        return final_decisions
    
    async def update_performance(
        self,
        record_id: str,
        exit_price: float,
        actual_return: float
    ):
        """
        Update agent performance after trade completion
        
        Args:
            record_id: Decision record ID
            exit_price: Exit price
            actual_return: Actual return achieved
        """
        outcome = 'success' if actual_return > 0 else 'failure'
        
        await self.performance_optimizer.update_decision_outcome(
            record_id,
            exit_price,
            actual_return,
            outcome
        )
        
        # Re-optimize agent weights
        self.agent_weights = await self.performance_optimizer.optimize_agent_weights()
        
        logger.info(f"[CHECK] Updated performance for record: {record_id}")
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report for all agents"""
        top_agents = await self.performance_optimizer.get_top_agents(n=10)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_agents': len(self.all_agents) + len(self.base_coordinator.execution_agents),
            'top_performers': top_agents,
            'agent_weights': self.agent_weights
        }
        
        return report


# Global instance
_enhanced_coordinator = None

async def get_enhanced_coordinator() -> EnhancedAgentCoordinator:
    """Get global enhanced coordinator instance"""
    global _enhanced_coordinator
    if _enhanced_coordinator is None:
        _enhanced_coordinator = EnhancedAgentCoordinator()
        await _enhanced_coordinator.initialize()
    return _enhanced_coordinator


# Example usage
async def main():
    """Example usage of Enhanced Agent Integration"""
    
    # Initialize coordinator
    coordinator = await get_enhanced_coordinator()
    
    # Define symbols and market data
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    market_data = {
        'AAPL': {'price': 150.0, 'volume': 1000000},
        'MSFT': {'price': 300.0, 'volume': 800000},
        'GOOGL': {'price': 120.0, 'volume': 900000},
        'TSLA': {'price': 200.0, 'volume': 1500000}
    }
    
    # Get trading decisions
    decisions = await coordinator.execute_with_intelligence(symbols, market_data)
    
    # Print decisions
    print("\n" + "="*80)
    print("ENHANCED TRADING DECISIONS")
    print("="*80)
    for symbol, decision in decisions.items():
        print(f"\n{symbol}:")
        print(f"  Action: {decision.action}")
        print(f"  Confidence: {decision.confidence:.2%}")
        print(f"  Reasoning: {decision.reasoning}")
    print("="*80)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

