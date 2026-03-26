"""
Cross-Asset Arbitrage Strategy
Exploits price discrepancies across different assets, exchanges, and markets
Targets: crypto pairs, stock-futures spreads, ETF-basket spreads
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ArbitrageOpportunity:
    """Detected arbitrage opportunity"""
    type: str  # 'pair', 'triangular', 'cross_exchange', 'etf_basket'
    assets: List[str]
    expected_profit_pct: float
    confidence: float
    entry_prices: Dict[str, float]
    exit_prices: Dict[str, float]
    actions: List[Dict[str, Any]]  # Buy/sell actions
    risk_score: float
    timestamp: datetime
    reasoning: str

class CrossAssetArbitrageStrategy:
    """
    Multi-asset arbitrage strategy
    Identifies and exploits pricing inefficiencies
    """
    
    def __init__(self):
        # Minimum profit thresholds (after fees)
        self.min_profit_thresholds = {
            'pair': 0.005,       # 0.5% for pair trading
            'triangular': 0.003,  # 0.3% for triangular arb
            'cross_exchange': 0.008,  # 0.8% for cross-exchange
            'etf_basket': 0.004   # 0.4% for ETF arbitrage
        }
        
        # Trading fees (conservative estimates)
        self.fees = {
            'crypto': 0.001,  # 0.1% per trade
            'stock': 0.0005,  # 0.05% per trade
            'etf': 0.0005
        }
        
        # Correlation tracking for pair trading
        self.correlation_history = {}
        
        # Opportunity tracking
        self.opportunities_found = 0
        self.opportunities_executed = 0
        self.total_profit = 0.0
        
        logger.info("✅ Cross-Asset Arbitrage Strategy initialized")
    
    async def scan_for_opportunities(
        self,
        market_data: Dict[str, pd.DataFrame],
        portfolio_positions: Dict[str, float]
    ) -> List[ArbitrageOpportunity]:
        """
        Scan all available assets for arbitrage opportunities
        
        Args:
            market_data: Dict of symbol -> OHLCV DataFrame
            portfolio_positions: Current portfolio positions
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        
        try:
            # 1. Pair trading opportunities
            pair_opps = await self._scan_pair_trading(market_data)
            opportunities.extend(pair_opps)
            
            # 2. Triangular arbitrage (crypto)
            triangular_opps = await self._scan_triangular_arbitrage(market_data)
            opportunities.extend(triangular_opps)
            
            # 3. Cross-exchange opportunities
            # (requires multi-exchange data - placeholder)
            
            # 4. ETF vs basket arbitrage
            # (requires ETF holdings data - placeholder)
            
            # Sort by expected profit
            opportunities.sort(key=lambda x: x.expected_profit_pct, reverse=True)
            
            if opportunities:
                logger.info(f"🔍 Found {len(opportunities)} arbitrage opportunities")
                for i, opp in enumerate(opportunities[:3]):  # Log top 3
                    logger.info(f"   #{i+1}: {opp.type} - {opp.assets} - "
                               f"Expected profit: {opp.expected_profit_pct:.3%}")
            
            self.opportunities_found += len(opportunities)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Error scanning for opportunities: {e}")
            return []
    
    async def _scan_pair_trading(
        self,
        market_data: Dict[str, pd.DataFrame]
    ) -> List[ArbitrageOpportunity]:
        """
        Scan for statistical arbitrage between correlated pairs
        Looks for temporary deviations from historical correlation
        """
        opportunities = []
        symbols = list(market_data.keys())
        
        # Need at least 2 assets
        if len(symbols) < 2:
            return opportunities
        
        # Check all pairs
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                symbol1, symbol2 = symbols[i], symbols[j]
                data1, data2 = market_data[symbol1], market_data[symbol2]
                
                # Need sufficient data
                if len(data1) < 30 or len(data2) < 30:
                    continue
                
                # Calculate correlation
                returns1 = data1['close'].pct_change().dropna()
                returns2 = data2['close'].pct_change().dropna()
                
                # Align indices
                common_idx = returns1.index.intersection(returns2.index)
                if len(common_idx) < 20:
                    continue
                
                returns1_aligned = returns1.loc[common_idx]
                returns2_aligned = returns2.loc[common_idx]
                
                correlation = returns1_aligned.corr(returns2_aligned)
                
                # Only trade highly correlated pairs (>0.7)
                if abs(correlation) < 0.70:
                    continue
                
                # Calculate z-score of spread
                price1 = data1['close'].iloc[-1]
                price2 = data2['close'].iloc[-1]
                
                # Normalize prices to same scale
                normalized1 = data1['close'] / data1['close'].iloc[0]
                normalized2 = data2['close'] / data2['close'].iloc[0]
                
                # Calculate spread
                spread = normalized1 - normalized2
                spread_mean = spread.mean()
                spread_std = spread.std()
                
                if spread_std == 0:
                    continue
                
                current_spread = spread.iloc[-1]
                z_score = (current_spread - spread_mean) / spread_std
                
                # Trade when z-score exceeds threshold
                if abs(z_score) > 2.0:  # 2 standard deviations
                    # Determine trade direction
                    if z_score > 2.0:
                        # Spread too wide: sell symbol1, buy symbol2
                        action1 = 'sell'
                        action2 = 'buy'
                        expected_profit = (abs(z_score) - 2.0) / 100  # Rough estimate
                    else:
                        # Spread too narrow: buy symbol1, sell symbol2
                        action1 = 'buy'
                        action2 = 'sell'
                        expected_profit = (abs(z_score) - 2.0) / 100
                    
                    # Subtract fees
                    total_fees = 2 * self.fees['stock']  # Two trades
                    net_profit = expected_profit - total_fees
                    
                    if net_profit > self.min_profit_thresholds['pair']:
                        opportunity = ArbitrageOpportunity(
                            type='pair',
                            assets=[symbol1, symbol2],
                            expected_profit_pct=net_profit,
                            confidence=min(0.95, abs(correlation) * 1.1),
                            entry_prices={symbol1: price1, symbol2: price2},
                            exit_prices={
                                symbol1: price1 * (1 + 0.01 if action1 == 'sell' else 1 - 0.01),
                                symbol2: price2 * (1 + 0.01 if action2 == 'sell' else 1 - 0.01)
                            },
                            actions=[
                                {'symbol': symbol1, 'action': action1, 'quantity': 1.0},
                                {'symbol': symbol2, 'action': action2, 'quantity': 1.0}
                            ],
                            risk_score=1.0 / abs(z_score),  # Lower risk with higher z-score
                            timestamp=datetime.utcnow(),
                            reasoning=f"Pair trading: z-score={z_score:.2f}, correlation={correlation:.2f}"
                        )
                        
                        opportunities.append(opportunity)
        
        return opportunities
    
    async def _scan_triangular_arbitrage(
        self,
        market_data: Dict[str, pd.DataFrame]
    ) -> List[ArbitrageOpportunity]:
        """
        Scan for triangular arbitrage in crypto markets
        Example: BTC/USD -> ETH/BTC -> USD/ETH should equal 1
        """
        opportunities = []
        
        # Define common triangular paths
        # Format: [(base, quote), (base, quote), (base, quote)]
        triangular_paths = [
            # Crypto triangles (if data available)
            [('BTC', 'USD'), ('ETH', 'BTC'), ('USD', 'ETH')],
            [('BTC', 'USD'), ('LTC', 'BTC'), ('USD', 'LTC')],
            # More paths can be added based on available pairs
        ]
        
        for path in triangular_paths:
            try:
                # Build symbol strings
                symbols = [f"{base}/{quote}" for base, quote in path]
                
                # Check if all symbols exist in market data
                if not all(sym in market_data or sym.replace('/', '') in market_data for sym in symbols):
                    continue
                
                # Get latest prices
                prices = []
                actual_symbols = []
                for sym in symbols:
                    # Try both formats
                    if sym in market_data:
                        prices.append(market_data[sym]['close'].iloc[-1])
                        actual_symbols.append(sym)
                    elif sym.replace('/', '') in market_data:
                        sym_no_slash = sym.replace('/', '')
                        prices.append(market_data[sym_no_slash]['close'].iloc[-1])
                        actual_symbols.append(sym_no_slash)
                    else:
                        break
                
                if len(prices) != 3:
                    continue
                
                # Calculate triangular rate
                # Starting with 1 unit, after 3 trades we should get back 1
                triangular_rate = prices[0] * prices[1] * prices[2]
                
                # Calculate deviation from 1.0
                profit_pct = abs(1.0 - triangular_rate)
                
                # Subtract fees (3 trades)
                total_fees = 3 * self.fees['crypto']
                net_profit = profit_pct - total_fees
                
                if net_profit > self.min_profit_thresholds['triangular']:
                    # Determine trade direction
                    if triangular_rate < 1.0:
                        # Forward path profitable
                        direction = 'forward'
                    else:
                        # Reverse path profitable
                        direction = 'reverse'
                    
                    opportunity = ArbitrageOpportunity(
                        type='triangular',
                        assets=actual_symbols,
                        expected_profit_pct=net_profit,
                        confidence=0.80,  # Lower confidence due to execution risk
                        entry_prices={sym: price for sym, price in zip(actual_symbols, prices)},
                        exit_prices={sym: price for sym, price in zip(actual_symbols, prices)},
                        actions=[
                            {'symbol': actual_symbols[0], 'action': 'buy' if direction == 'forward' else 'sell', 'quantity': 1.0},
                            {'symbol': actual_symbols[1], 'action': 'buy' if direction == 'forward' else 'sell', 'quantity': 1.0},
                            {'symbol': actual_symbols[2], 'action': 'buy' if direction == 'forward' else 'sell', 'quantity': 1.0}
                        ],
                        risk_score=0.70,  # Higher risk due to execution timing
                        timestamp=datetime.utcnow(),
                        reasoning=f"Triangular arbitrage: rate={triangular_rate:.6f}, direction={direction}"
                    )
                    
                    opportunities.append(opportunity)
                    
            except Exception as e:
                logger.debug(f"Error checking triangular path {path}: {e}")
                continue
        
        return opportunities
    
    def validate_opportunity(
        self,
        opportunity: ArbitrageOpportunity,
        current_prices: Dict[str, float],
        max_slippage_pct: float = 0.001  # 0.1%
    ) -> bool:
        """
        Validate opportunity still exists with current prices
        Accounts for price movement since detection
        """
        try:
            # Check price slippage for each asset
            for asset in opportunity.assets:
                if asset not in current_prices:
                    logger.warning(f"Price not available for {asset}")
                    return False
                
                expected_price = opportunity.entry_prices[asset]
                current_price = current_prices[asset]
                
                slippage = abs(current_price - expected_price) / expected_price
                
                if slippage > max_slippage_pct:
                    logger.debug(f"Excessive slippage for {asset}: {slippage:.4%}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating opportunity: {e}")
            return False
    
    def calculate_position_sizes(
        self,
        opportunity: ArbitrageOpportunity,
        available_capital: float,
        max_position_pct: float = 0.20  # Max 20% of capital per opportunity
    ) -> Dict[str, float]:
        """
        Calculate optimal position sizes for arbitrage
        Ensures balanced exposure across legs
        """
        max_investment = available_capital * max_position_pct
        
        # For pair trading: split equally
        if opportunity.type == 'pair':
            per_asset = max_investment / 2
            return {
                asset: per_asset / opportunity.entry_prices[asset]
                for asset in opportunity.assets
            }
        
        # For triangular: split three ways
        elif opportunity.type == 'triangular':
            per_asset = max_investment / 3
            return {
                asset: per_asset / opportunity.entry_prices[asset]
                for asset in opportunity.assets
            }
        
        # Default: equal split
        else:
            per_asset = max_investment / len(opportunity.assets)
            return {
                asset: per_asset / opportunity.entry_prices[asset]
                for asset in opportunity.assets
            }
    
    def record_execution(
        self,
        opportunity: ArbitrageOpportunity,
        actual_profit: float
    ):
        """Record executed arbitrage trade"""
        self.opportunities_executed += 1
        self.total_profit += actual_profit
        
        logger.info(f"✅ Executed {opportunity.type} arbitrage: "
                   f"Expected: {opportunity.expected_profit_pct:.3%}, "
                   f"Actual: {actual_profit:.3%}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get arbitrage strategy performance summary"""
        win_rate = (
            self.opportunities_executed / self.opportunities_found
            if self.opportunities_found > 0 else 0
        )
        
        avg_profit = (
            self.total_profit / self.opportunities_executed
            if self.opportunities_executed > 0 else 0
        )
        
        return {
            'opportunities_found': self.opportunities_found,
            'opportunities_executed': self.opportunities_executed,
            'execution_rate': win_rate,
            'total_profit': self.total_profit,
            'average_profit': avg_profit
        }


# Global instance
_arbitrage_strategy = None

def get_arbitrage_strategy() -> CrossAssetArbitrageStrategy:
    """Get or create global arbitrage strategy instance"""
    global _arbitrage_strategy
    if _arbitrage_strategy is None:
        _arbitrage_strategy = CrossAssetArbitrageStrategy()
    return _arbitrage_strategy
