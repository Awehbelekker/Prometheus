#!/usr/bin/env python3
"""
Launch Prometheus with Revolutionary HRM System
Integrates all high-value enhancements
"""

import logging
import asyncio
from typing import Dict
from core.revolutionary_hrm_system import RevolutionaryHRMSystem
from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
from core.workflow_automation import TradingWorkflowAutomation
from core.hrm_evaluation import HRMEvaluator
from core.alpaca_mcp_integration import AlpacaMCPIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RevolutionaryPrometheusLauncher:
    """
    Launch Prometheus with all revolutionary enhancements
    """
    
    def __init__(self):
        logger.info("="*80)
        logger.info("INITIALIZING REVOLUTIONARY PROMETHEUS SYSTEM")
        logger.info("="*80)
        
        # Initialize revolutionary HRM
        self.hrm_system = RevolutionaryHRMSystem(
            device='cpu',
            use_multi_agent=True,
            use_ensemble=True,
            use_memory=True
        )
        
        # Initialize workflow automation
        self.workflows = TradingWorkflowAutomation()
        
        # Initialize evaluation
        self.evaluator = HRMEvaluator()
        
        # Initialize Alpaca MCP
        self.alpaca_mcp = AlpacaMCPIntegration()
        
        logger.info("✅ Revolutionary Prometheus System initialized")
        logger.info(f"   Multi-Agent: {self.hrm_system.use_multi_agent}")
        logger.info(f"   Ensemble: {self.hrm_system.use_ensemble}")
        logger.info(f"   Memory: {self.hrm_system.use_memory}")
        logger.info(f"   Workflows: {self.workflows.available}")
        logger.info(f"   Evaluation: {self.evaluator.available}")
    
    async def make_trading_decision(self, market_data: Dict) -> Dict:
        """Make trading decision using revolutionary HRM"""
        # Create context
        context = HRMReasoningContext(
            market_data=market_data,
            user_profile={},
            trading_history=[],
            current_portfolio={},
            risk_preferences={},
            reasoning_level=HRMReasoningLevel.HIGH_LEVEL
        )
        
        # Execute market analysis workflow
        if self.workflows.available:
            analysis = self.workflows.execute_workflow('market_analysis', market_data)
            logger.info(f"Workflow analysis: {analysis.get('result')}")
        
        # Get revolutionary decision
        decision = self.hrm_system.make_revolutionary_decision(context)
        
        logger.info(f"Revolutionary Decision: {decision['action']} (confidence: {decision['confidence']:.3f})")
        logger.info(f"   Sources: {decision.get('num_sources', 0)}")
        logger.info(f"   Enhancements: {decision.get('enhancements', {})}")
        
        return decision
    
    def update_with_outcome(self, decision: Dict, outcome: Dict):
        """Update system with trading outcome"""
        # Update HRM memory
        self.hrm_system.update_with_outcome(decision, outcome)
        
        # Evaluate decision
        if self.evaluator.available:
            metrics = self.evaluator.evaluate_decision(decision, {}, outcome)
            logger.info(f"Decision evaluation: accuracy={metrics.get('accuracy', 0):.3f}")
    
    def get_system_status(self) -> Dict:
        """Get complete system status"""
        return {
            'hrm_system': self.hrm_system.get_system_status(),
            'workflows': {'available': self.workflows.available},
            'evaluation': {'available': self.evaluator.available},
            'alpaca_mcp': {'available': self.alpaca_mcp.mcp_available}
        }


async def main():
    """Main launcher"""
    launcher = RevolutionaryPrometheusLauncher()
    
    # Example usage
    market_data = {
        'symbol': 'AAPL',
        'price': 150.0,
        'volume': 1000000,
        'indicators': {
            'rsi': 65.5,
            'macd': 0.8,
            'volatility': 0.02
        }
    }
    
    decision = await launcher.make_trading_decision(market_data)
    print(f"\nFinal Decision: {decision}")
    
    # Get system status
    status = launcher.get_system_status()
    print(f"\nSystem Status: {status}")


if __name__ == "__main__":
    asyncio.run(main())

