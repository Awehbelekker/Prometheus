"""
PROFIT MAXIMIZATION ENGINE
==========================
The orchestrator that makes PROMETHEUS truly autonomous and profit-focused.

This is the master brain that:
- Continuously scans ALL markets
- Discovers best opportunities autonomously
- Executes multiple strategies per opportunity
- Manages dynamic trading universe
- Maximizes capital efficiency
- Adapts to market conditions in real-time

NO human intervention required - pure autonomous profit optimization.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

from core.autonomous_market_scanner import autonomous_scanner, TradingOpportunity
from core.dynamic_trading_universe import dynamic_universe
from core.multi_strategy_executor import MultiStrategyExecutor
# NOTE: Do not create a global singleton here - engine will create its own instance
# multi_strategy_executor = MultiStrategyExecutor(enable_broker_execution=False)

logger = logging.getLogger(__name__)

@dataclass
class ProfitMaximizationMetrics:
    """Metrics for profit maximization performance"""
    scan_cycles: int = 0
    opportunities_discovered: int = 0
    opportunities_executed: int = 0
    total_capital_deployed: float = 0.0
    expected_total_return: float = 0.0
    active_positions: int = 0
    universe_size: int = 0
    runtime_minutes: float = 0.0
    avg_opportunity_score: float = 0.0

class ProfitMaximizationEngine:
    """
    Master orchestrator for autonomous profit maximization
    """
    
    def __init__(self, 
                 total_capital: float = 10000.0,
                 scan_interval_seconds: int = 60,
                 max_capital_per_opportunity: float = 1000.0,
                 paper_trading: bool = True,
                 enable_broker_execution: bool = True):  # ENABLED by default - autonomous operation
        self.total_capital = total_capital
        self.available_capital = total_capital
        self.scan_interval = scan_interval_seconds
        self.max_capital_per_opportunity = max_capital_per_opportunity
        self.paper_trading = paper_trading
        self.enable_broker_execution = enable_broker_execution
        
        # Warn if live trading
        if enable_broker_execution and not paper_trading:
            logger.warning("="*80)
            logger.warning("LIVE TRADING MODE - REAL MONEY AT RISK!")
            logger.warning("="*80)
        
        # State
        self.active = False
        self.start_time = None
        self.metrics = ProfitMaximizationMetrics()
        self.active_executions: List[MultiStrategyResult] = []
        
        # Initialize strategy executor with broker execution setting
        self.strategy_executor = MultiStrategyExecutor(enable_broker_execution=enable_broker_execution)
        
        # Configuration
        self.max_opportunities_per_cycle = 5
        self.min_opportunity_confidence = 0.70
        self.min_opportunity_return = 0.008  # 0.8%
        
        logger.info("🚀 Profit Maximization Engine initialized")
        logger.info(f"   Total Capital: ${total_capital:,.2f}")
        logger.info(f"   Scan Interval: {scan_interval_seconds}s")
        logger.info(f"   Max per Opportunity: ${max_capital_per_opportunity:,.2f}")
    
    async def start_autonomous_trading(self, duration_hours: Optional[float] = None):
        """
        Start the autonomous trading engine
        
        Args:
            duration_hours: How long to run (None = run indefinitely)
        """
        self.active = True
        self.start_time = datetime.now()
        
        logger.info("=" * 80)
        logger.info("🚀 STARTING AUTONOMOUS PROFIT MAXIMIZATION ENGINE")
        logger.info("=" * 80)
        logger.info(f"Mode: FULLY AUTONOMOUS - No human intervention")
        logger.info(f"Capital: ${self.total_capital:,.2f}")
        logger.info(f"Duration: {'CONTINUOUS' if not duration_hours else f'{duration_hours} hours'}")
        logger.info(f"Scan Interval: {self.scan_interval}s")
        logger.info("=" * 80)
        
        end_time = None
        if duration_hours:
            end_time = datetime.now() + timedelta(hours=duration_hours)
        
        cycle = 0
        
        try:
            while self.active:
                cycle += 1
                logger.info(f"\n{'='*80}")
                logger.info(f"🔄 CYCLE {cycle} - {datetime.now().strftime('%H:%M:%S')}")
                logger.info(f"{'='*80}")
                
                # Run one complete cycle
                await self._run_trading_cycle()
                
                # Update metrics
                self.metrics.scan_cycles = cycle
                self.metrics.runtime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
                
                # Print progress
                self._print_progress()
                
                # Check if we should stop
                if end_time and datetime.now() >= end_time:
                    logger.info(f"\n⏰ Duration limit reached ({duration_hours} hours)")
                    break
                
                # Wait before next cycle
                logger.info(f"\n💤 Waiting {self.scan_interval}s until next cycle...")
                await asyncio.sleep(self.scan_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️ Autonomous trading stopped by user")
        except Exception as e:
            logger.error(f"\n❌ Error in autonomous trading: {e}", exc_info=True)
        finally:
            self.active = False
            self._print_final_summary()
    
    async def _run_trading_cycle(self):
        """Run one complete trading cycle"""
        try:
            # 1. Scan all markets for opportunities
            logger.info("📊 Step 1: Scanning ALL markets for opportunities...")
            opportunities = await autonomous_scanner.discover_best_opportunities(
                limit=20
            )
            
            self.metrics.opportunities_discovered += len(opportunities)
            
            if not opportunities:
                logger.warning("   ⚠️ No opportunities found this cycle")
                return
            
            # 2. Update trading universe
            logger.info("\n🌍 Step 2: Updating dynamic trading universe...")
            universe_update = await dynamic_universe.update_universe(opportunities)
            self.metrics.universe_size = universe_update['active_symbols']
            
            # 3. Select top opportunities to execute
            logger.info("\n🎯 Step 3: Selecting top opportunities for execution...")
            executable_opportunities = self._filter_opportunities(opportunities)
            
            if not executable_opportunities:
                logger.info("   No opportunities meet execution criteria this cycle")
                return
            
            # 4. Execute multi-strategy approach on each opportunity
            logger.info(f"\n💰 Step 4: Executing multi-strategy approach on {len(executable_opportunities)} opportunities...")
            
            for i, opportunity in enumerate(executable_opportunities, 1):
                if self.available_capital < 50:
                    logger.warning(f"   ⚠️ Insufficient capital (${self.available_capital:.2f})")
                    break
                
                # Determine capital for this opportunity
                capital = min(
                    self.max_capital_per_opportunity,
                    self.available_capital * 0.3,  # Max 30% per opportunity
                    self.available_capital
                )
                
                if capital < 10:
                    continue
                
                logger.info(f"\n   Opportunity {i}/{len(executable_opportunities)}: {opportunity.symbol}")
                
                # Execute multiple strategies
                result = await self.strategy_executor.maximize_opportunity(
                    opportunity,
                    capital
                )
                
                if result.strategies_executed:
                    self.active_executions.append(result)
                    self.available_capital -= result.total_capital_allocated
                    self.metrics.opportunities_executed += 1
                    self.metrics.total_capital_deployed += result.total_capital_allocated
                    self.metrics.expected_total_return += result.expected_total_return
                    
                    logger.info(f"   ✅ Deployed ${result.total_capital_allocated:.2f} "
                              f"across {len(result.strategies_executed)} strategies")
            
            # 5. Manage existing positions (in production, would check and close)
            logger.info(f"\n📈 Step 5: Managing {len(self.active_executions)} active positions...")
            # Placeholder for position management
            
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}", exc_info=True)
    
    def _filter_opportunities(self, opportunities: List[TradingOpportunity]) -> List[TradingOpportunity]:
        """Filter opportunities based on execution criteria"""
        filtered = []
        
        for opp in opportunities:
            if opp.confidence >= self.min_opportunity_confidence and \
               opp.expected_return >= self.min_opportunity_return and \
               opp.risk_reward_ratio >= 1.0:
                filtered.append(opp)
        
        # Limit to max per cycle
        return filtered[:self.max_opportunities_per_cycle]
    
    def _print_progress(self):
        """Print current progress"""
        capital_deployed_pct = (self.metrics.total_capital_deployed / self.total_capital) * 100
        
        logger.info(f"\n{'='*80}")
        logger.info("📊 CURRENT STATUS")
        logger.info(f"{'='*80}")
        logger.info(f"Runtime: {self.metrics.runtime_minutes:.1f} minutes")
        logger.info(f"Cycles: {self.metrics.scan_cycles}")
        logger.info(f"Opportunities Discovered: {self.metrics.opportunities_discovered}")
        logger.info(f"Opportunities Executed: {self.metrics.opportunities_executed}")
        logger.info(f"Active Positions: {len(self.active_executions)}")
        logger.info(f"Capital Deployed: ${self.metrics.total_capital_deployed:,.2f} ({capital_deployed_pct:.1f}%)")
        logger.info(f"Available Capital: ${self.available_capital:,.2f}")
        logger.info(f"Expected Total Return: {self.metrics.expected_total_return:.2%}")
        logger.info(f"Universe Size: {self.metrics.universe_size} active symbols")
        logger.info(f"{'='*80}")
    
    def _print_final_summary(self):
        """Print final trading summary"""
        logger.info(f"\n{'='*80}")
        logger.info("🏁 AUTONOMOUS TRADING SESSION COMPLETE")
        logger.info(f"{'='*80}")
        logger.info(f"Total Runtime: {self.metrics.runtime_minutes:.1f} minutes")
        logger.info(f"Total Cycles: {self.metrics.scan_cycles}")
        logger.info(f"Opportunities Discovered: {self.metrics.opportunities_discovered}")
        logger.info(f"Opportunities Executed: {self.metrics.opportunities_executed}")
        logger.info(f"Execution Rate: {(self.metrics.opportunities_executed / max(self.metrics.opportunities_discovered, 1)) * 100:.1f}%")
        logger.info(f"\n💰 CAPITAL MANAGEMENT:")
        logger.info(f"Starting Capital: ${self.total_capital:,.2f}")
        logger.info(f"Capital Deployed: ${self.metrics.total_capital_deployed:,.2f}")
        logger.info(f"Capital Efficiency: {(self.metrics.total_capital_deployed / self.total_capital) * 100:.1f}%")
        logger.info(f"\n📈 EXPECTED PERFORMANCE:")
        logger.info(f"Expected Total Return: {self.metrics.expected_total_return:.2%}")
        logger.info(f"Average per Opportunity: {(self.metrics.expected_total_return / max(self.metrics.opportunities_executed, 1)) * 100:.2f}%")
        logger.info(f"\n🌍 UNIVERSE:")
        logger.info(f"Final Universe Size: {self.metrics.universe_size}")
        logger.info(f"Active Positions: {len(self.active_executions)}")
        logger.info(f"{'='*80}")
    
    def stop(self):
        """Stop the autonomous trading engine"""
        logger.info("\n🛑 Stopping autonomous trading...")
        self.active = False
    
    def get_metrics(self) -> ProfitMaximizationMetrics:
        """Get current metrics"""
        return self.metrics
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            'active': self.active,
            'runtime_minutes': self.metrics.runtime_minutes,
            'total_capital': self.total_capital,
            'available_capital': self.available_capital,
            'capital_deployed': self.metrics.total_capital_deployed,
            'opportunities_discovered': self.metrics.opportunities_discovered,
            'opportunities_executed': self.metrics.opportunities_executed,
            'active_positions': len(self.active_executions),
            'universe_size': self.metrics.universe_size,
            'expected_return': self.metrics.expected_total_return
        }

# Global instance
profit_engine = ProfitMaximizationEngine()

# Convenience function
async def start_autonomous_trading(duration_hours: Optional[float] = None,
                                   capital: float = 10000.0):
    """Start autonomous trading"""
    engine = ProfitMaximizationEngine(total_capital=capital)
    await engine.start_autonomous_trading(duration_hours=duration_hours)

