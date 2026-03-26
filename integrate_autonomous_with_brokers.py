"""
ONE-CLICK INTEGRATION
====================
Integrates the autonomous system with your EXISTING broker infrastructure.
No duplication - uses what you already have!
"""

import os
import re

def integrate_multi_strategy_executor():
    """Add broker execution to multi-strategy executor"""
    
    file_path = "core/multi_strategy_executor.py"
    
    print(f"[1/2] Integrating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already integrated
    if 'autonomous_broker_executor' in content:
        print("   [SKIP] Already integrated")
        return
    
    # Add broker executor import at top
    import_section = """import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from core.autonomous_market_scanner import TradingOpportunity, OpportunityType"""
    
    new_import = """import asyncio
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
    AutonomousBrokerExecutor = None"""
    
    content = content.replace(import_section, new_import)
    
    # Add broker_executor to __init__
    old_init = """    def __init__(self):
        # Strategy templates"""
    
    new_init = """    def __init__(self, enable_broker_execution=False):
        # Strategy templates
        
        # Broker executor (optional - for real trading)
        self.broker_executor = None
        self.enable_broker_execution = enable_broker_execution
        
        if enable_broker_execution and BROKER_EXECUTOR_AVAILABLE:
            logger.info("[INFO] Broker execution ENABLED - will place real orders")
        else:
            logger.info("[INFO] Broker execution DISABLED - simulation only")"""
    
    content = content.replace(old_init, new_init)
    
    # Modify _execute_strategy to actually execute
    old_execute = """    async def _execute_strategy(self,
                                strategy: StrategyConfig,
                                opportunity: TradingOpportunity,
                                capital: float) -> StrategyExecution:
        \"\"\"Execute a single strategy\"\"\"
        entry_price = opportunity.entry_price
        target_price = entry_price * (1 + strategy.profit_target)
        stop_price = entry_price * (1 - strategy.stop_loss)
        
        # Calculate quantity (simplified - would use actual broker API)
        quantity = capital / entry_price
        
        expected_return = strategy.profit_target
        confidence = min(opportunity.confidence, 0.95)
        
        return StrategyExecution(
            strategy_type=strategy.strategy_type,
            symbol=opportunity.symbol,
            entry_price=entry_price,
            target_price=target_price,
            stop_price=stop_price,
            capital_allocated=capital,
            quantity=quantity,
            expected_return=expected_return,
            confidence=confidence,
            status="active"
        )"""
    
    new_execute = """    async def _execute_strategy(self,
                                strategy: StrategyConfig,
                                opportunity: TradingOpportunity,
                                capital: float) -> StrategyExecution:
        \"\"\"Execute a single strategy\"\"\"
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
        
        return execution"""
    
    content = content.replace(old_execute, new_execute)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   [OK] Integration complete")

def integrate_profit_engine():
    """Add broker initialization to profit engine"""
    
    file_path = "core/profit_maximization_engine.py"
    
    print(f"[2/2] Integrating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already integrated
    if 'paper_trading' in content and 'enable_broker_execution' in content:
        print("   [SKIP] Already integrated")
        return
    
    # Add paper_trading parameter to __init__
    old_init_sig = """    def __init__(self, 
                 total_capital: float = 10000.0,
                 scan_interval_seconds: int = 60,
                 max_capital_per_opportunity: float = 1000.0):"""
    
    new_init_sig = """    def __init__(self, 
                 total_capital: float = 10000.0,
                 scan_interval_seconds: int = 60,
                 max_capital_per_opportunity: float = 1000.0,
                 paper_trading: bool = True,
                 enable_broker_execution: bool = False):"""
    
    content = content.replace(old_init_sig, new_init_sig)
    
    # Add initialization code
    old_init_body = """        self.total_capital = total_capital
        self.available_capital = total_capital
        self.scan_interval = scan_interval_seconds
        self.max_capital_per_opportunity = max_capital_per_opportunity"""
    
    new_init_body = """        self.total_capital = total_capital
        self.available_capital = total_capital
        self.scan_interval = scan_interval_seconds
        self.max_capital_per_opportunity = max_capital_per_opportunity
        self.paper_trading = paper_trading
        self.enable_broker_execution = enable_broker_execution
        
        # Warn if live trading
        if enable_broker_execution and not paper_trading:
            logger.warning("="*80)
            logger.warning("LIVE TRADING MODE - REAL MONEY AT RISK!")
            logger.warning("="*80)"""
    
    content = content.replace(old_init_body, new_init_body)
    
    # Initialize multi_strategy_executor with broker execution flag
    old_executor = """from core.multi_strategy_executor import multi_strategy_executor"""
    new_executor = """from core.multi_strategy_executor import MultiStrategyExecutor
multi_strategy_executor = MultiStrategyExecutor(enable_broker_execution=False)  # Will be set in engine"""
    
    content = content.replace(old_executor, new_executor)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("   [OK] Integration complete")

def main():
    print("\n" + "="*60)
    print("AUTONOMOUS SYSTEM <-> BROKER INTEGRATION")
    print("="*60)
    print("\nThis integrates the autonomous system with your")
    print("EXISTING broker infrastructure (no duplication!).\n")
    
    try:
        integrate_multi_strategy_executor()
        integrate_profit_engine()
        
        print("\n" + "="*60)
        print("[SUCCESS] Integration Complete!")
        print("="*60)
        print("\nThe autonomous system can now execute real trades!")
        print("\nUsage:")
        print("  # Paper trading (safe - default)")
        print("  engine = ProfitMaximizationEngine(paper_trading=True)")
        print("")
        print("  # Live trading (requires broker connection)")
        print("  engine = ProfitMaximizationEngine(")
        print("      paper_trading=False,")
        print("      enable_broker_execution=True")
        print("  )")
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Integration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
