"""
Options Trading Strategies for PROMETHEUS
Implements Iron Condor, Iron Butterfly, and other advanced options strategies
"""

import asyncio
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class IronCondorStrategy:
    """Iron Condor options strategy configuration"""
    underlying: str
    lower_put_strike: float
    higher_put_strike: float
    lower_call_strike: float
    higher_call_strike: float
    expiration: str
    quantity: int
    max_profit: float
    max_loss: float
    breakeven_low: float
    breakeven_high: float
    credit_received: float

@dataclass
class IronButterflyStrategy:
    """Iron Butterfly options strategy configuration"""
    underlying: str
    lower_strike: float
    center_strike: float
    upper_strike: float
    expiration: str
    quantity: int
    max_profit: float
    max_loss: float
    breakeven_low: float
    breakeven_high: float
    credit_received: float

class OptionsStrategyExecutor:
    """Execute advanced options strategies"""
    
    def __init__(self, broker, options_provider=None):
        """
        Initialize options strategy executor
        
        Args:
            broker: Broker interface (IB or Alpaca)
            options_provider: Options data provider (optional)
        """
        self.broker = broker
        self.options_provider = options_provider
        self.active_strategies = {}
        logger.info("[OPTIONS] Options Strategy Executor initialized")
    
    async def create_iron_condor(
        self, 
        underlying: str, 
        current_price: float,
        expiration: str,
        wing_width: float = 5.0,
        body_width: float = 10.0
    ) -> IronCondorStrategy:
        """
        Create iron condor spread configuration
        
        Iron Condor Structure:
        - Buy PUT at lower strike (protection)
        - Sell PUT at higher strike (income)
        - Sell CALL at lower strike (income)
        - Buy CALL at higher strike (protection)
        
        Example for stock at $150:
        - Buy PUT at $140 (lower wing)
        - Sell PUT at $145 (higher put)
        - Sell CALL at $155 (lower call)
        - Buy CALL at $160 (upper wing)
        
        Args:
            underlying: Stock symbol
            current_price: Current stock price
            expiration: Expiration date (YYYY-MM-DD)
            wing_width: Distance between bought and sold strikes (default: $5)
            body_width: Distance from current price to sold strikes (default: $10)
        
        Returns:
            IronCondorStrategy configuration
        """
        logger.info(f"[IRON CONDOR] Creating strategy for {underlying} at ${current_price}")
        
        # Calculate strikes
        lower_put = current_price - body_width - wing_width
        higher_put = current_price - body_width
        lower_call = current_price + body_width
        higher_call = current_price + body_width + wing_width
        
        logger.info(f"[IRON CONDOR] Strikes: PUT {lower_put}/{higher_put}, CALL {lower_call}/{higher_call}")
        
        # Estimate credit and risk (simplified - real implementation would use options pricing)
        # Typical iron condor collects 20-40% of wing width as credit
        estimated_credit = wing_width * 100 * 0.30  # 30% of wing width per contract
        max_loss = (wing_width * 100) - estimated_credit
        max_profit = estimated_credit
        
        # Calculate breakevens
        breakeven_low = higher_put - (estimated_credit / 100)
        breakeven_high = lower_call + (estimated_credit / 100)
        
        strategy = IronCondorStrategy(
            underlying=underlying,
            lower_put_strike=lower_put,
            higher_put_strike=higher_put,
            lower_call_strike=lower_call,
            higher_call_strike=higher_call,
            expiration=expiration,
            quantity=1,
            max_profit=max_profit,
            max_loss=max_loss,
            breakeven_low=breakeven_low,
            breakeven_high=breakeven_high,
            credit_received=estimated_credit
        )
        
        logger.info(f"[IRON CONDOR] Max Profit: ${max_profit:.2f}, Max Loss: ${max_loss:.2f}")
        logger.info(f"[IRON CONDOR] Breakevens: ${breakeven_low:.2f} - ${breakeven_high:.2f}")
        
        return strategy
    
    async def execute_iron_condor(self, strategy: IronCondorStrategy) -> Dict:
        """
        Execute all 4 legs of iron condor
        
        Note: This is a placeholder. Real implementation requires:
        1. Options trading enabled on broker
        2. Options contract symbols
        3. Multi-leg order support
        
        Args:
            strategy: IronCondorStrategy configuration
        
        Returns:
            Dict with execution results
        """
        logger.info(f"[IRON CONDOR] Executing strategy for {strategy.underlying}")
        
        results = {
            'success': False,
            'strategy': 'iron_condor',
            'underlying': strategy.underlying,
            'legs': [],
            'message': 'Options trading not yet fully integrated'
        }
        
        # Placeholder for actual execution
        # Real implementation would:
        # 1. Get options chain
        # 2. Find exact contracts
        # 3. Submit multi-leg order
        # 4. Monitor fills
        
        logger.warning("[IRON CONDOR] Options execution requires IB options integration")
        logger.info("[IRON CONDOR] Strategy configured and ready for manual execution")
        
        # Store strategy for monitoring
        strategy_id = f"IC_{strategy.underlying}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_strategies[strategy_id] = strategy
        
        results['strategy_id'] = strategy_id
        results['message'] = f"Strategy created: {strategy_id}. Manual execution required."
        
        return results
    
    async def create_iron_butterfly(
        self,
        underlying: str,
        current_price: float,
        expiration: str,
        wing_width: float = 5.0
    ) -> IronButterflyStrategy:
        """
        Create iron butterfly spread configuration
        
        Iron Butterfly Structure:
        - Buy PUT at lower strike (protection)
        - Sell PUT at ATM strike (income)
        - Sell CALL at ATM strike (income)
        - Buy CALL at upper strike (protection)
        
        Similar to iron condor but with ATM center strikes
        
        Args:
            underlying: Stock symbol
            current_price: Current stock price
            expiration: Expiration date (YYYY-MM-DD)
            wing_width: Distance from ATM to wings (default: $5)
        
        Returns:
            IronButterflyStrategy configuration
        """
        logger.info(f"[IRON BUTTERFLY] Creating strategy for {underlying} at ${current_price}")
        
        # Round to nearest strike (typically $5 or $10 increments)
        center_strike = round(current_price / 5) * 5
        lower_strike = center_strike - wing_width
        upper_strike = center_strike + wing_width
        
        logger.info(f"[IRON BUTTERFLY] Strikes: {lower_strike}/{center_strike}/{upper_strike}")
        
        # Estimate credit and risk
        estimated_credit = wing_width * 100 * 0.40  # Butterflies collect more credit
        max_loss = (wing_width * 100) - estimated_credit
        max_profit = estimated_credit
        
        # Calculate breakevens
        breakeven_low = center_strike - (estimated_credit / 100)
        breakeven_high = center_strike + (estimated_credit / 100)
        
        strategy = IronButterflyStrategy(
            underlying=underlying,
            lower_strike=lower_strike,
            center_strike=center_strike,
            upper_strike=upper_strike,
            expiration=expiration,
            quantity=1,
            max_profit=max_profit,
            max_loss=max_loss,
            breakeven_low=breakeven_low,
            breakeven_high=breakeven_high,
            credit_received=estimated_credit
        )
        
        logger.info(f"[IRON BUTTERFLY] Max Profit: ${max_profit:.2f}, Max Loss: ${max_loss:.2f}")
        logger.info(f"[IRON BUTTERFLY] Breakevens: ${breakeven_low:.2f} - ${breakeven_high:.2f}")
        
        return strategy
    
    async def execute_iron_butterfly(self, strategy: IronButterflyStrategy) -> Dict:
        """
        Execute all 4 legs of iron butterfly
        
        Note: Placeholder for actual execution
        
        Args:
            strategy: IronButterflyStrategy configuration
        
        Returns:
            Dict with execution results
        """
        logger.info(f"[IRON BUTTERFLY] Executing strategy for {strategy.underlying}")
        
        results = {
            'success': False,
            'strategy': 'iron_butterfly',
            'underlying': strategy.underlying,
            'legs': [],
            'message': 'Options trading not yet fully integrated'
        }
        
        # Store strategy for monitoring
        strategy_id = f"IB_{strategy.underlying}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_strategies[strategy_id] = strategy
        
        results['strategy_id'] = strategy_id
        results['message'] = f"Strategy created: {strategy_id}. Manual execution required."
        
        logger.warning("[IRON BUTTERFLY] Options execution requires IB options integration")
        logger.info("[IRON BUTTERFLY] Strategy configured and ready for manual execution")
        
        return results
    
    def get_active_strategies(self) -> Dict:
        """Get all active options strategies"""
        return self.active_strategies
    
    def get_strategy_pnl(self, strategy_id: str, current_price: float) -> Dict:
        """
        Calculate current P&L for a strategy
        
        Args:
            strategy_id: Strategy identifier
            current_price: Current underlying price
        
        Returns:
            Dict with P&L information
        """
        if strategy_id not in self.active_strategies:
            return {'error': 'Strategy not found'}
        
        strategy = self.active_strategies[strategy_id]
        
        # Simplified P&L calculation
        if isinstance(strategy, IronCondorStrategy):
            # Check if price is within profit zone
            if strategy.breakeven_low < current_price < strategy.breakeven_high:
                # In profit zone - max profit at center
                pnl = strategy.max_profit
            elif current_price <= strategy.lower_put_strike or current_price >= strategy.higher_call_strike:
                # Outside wings - max loss
                pnl = -strategy.max_loss
            else:
                # Partial profit/loss
                if current_price < strategy.breakeven_low:
                    pnl = -(abs(current_price - strategy.breakeven_low) * 100)
                else:
                    pnl = -(abs(current_price - strategy.breakeven_high) * 100)
        
        elif isinstance(strategy, IronButterflyStrategy):
            # Similar calculation for butterfly
            if strategy.breakeven_low < current_price < strategy.breakeven_high:
                pnl = strategy.max_profit
            elif current_price <= strategy.lower_strike or current_price >= strategy.upper_strike:
                pnl = -strategy.max_loss
            else:
                if current_price < strategy.breakeven_low:
                    pnl = -(abs(current_price - strategy.breakeven_low) * 100)
                else:
                    pnl = -(abs(current_price - strategy.breakeven_high) * 100)
        else:
            pnl = 0
        
        return {
            'strategy_id': strategy_id,
            'current_price': current_price,
            'pnl': pnl,
            'max_profit': strategy.max_profit,
            'max_loss': strategy.max_loss
        }


# Example usage and testing
async def test_options_strategies():
    """Test options strategies"""
    logger.info("[TEST] Testing options strategies")
    
    # Create executor (without real broker for testing)
    executor = OptionsStrategyExecutor(broker=None)
    
    # Test Iron Condor
    ic_strategy = await executor.create_iron_condor(
        underlying='SPY',
        current_price=450.0,
        expiration='2026-02-20',
        wing_width=5.0,
        body_width=10.0
    )
    
    logger.info(f"[TEST] Iron Condor created: {ic_strategy}")
    
    # Test Iron Butterfly
    ib_strategy = await executor.create_iron_butterfly(
        underlying='AAPL',
        current_price=175.0,
        expiration='2026-02-20',
        wing_width=5.0
    )
    
    logger.info(f"[TEST] Iron Butterfly created: {ib_strategy}")
    
    logger.info("[TEST] Options strategies test complete")


if __name__ == "__main__":
    # Run test
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_options_strategies())
