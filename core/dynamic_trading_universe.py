"""
DYNAMIC TRADING UNIVERSE
========================
Manages what PROMETHEUS should trade based on real-time profitability.

No more hardcoded watchlists - the system autonomously:
- Adds high-potential assets
- Removes low-performing assets
- Reallocates capital to best opportunities
- Adapts to market conditions

Features:
- Real-time universe updates
- Performance-based selection
- Automatic portfolio rebalancing
- Multi-asset class support
"""

import asyncio
import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from core.autonomous_market_scanner import TradingOpportunity, AssetClass

logger = logging.getLogger(__name__)

@dataclass
class AssetPerformance:
    """Track performance of an asset in the universe"""
    symbol: str
    asset_class: AssetClass
    added_at: datetime
    last_updated: datetime
    total_return: float = 0.0
    win_rate: float = 0.0
    trades_count: int = 0
    avg_holding_time: float = 0.0  # minutes
    profitability_score: float = 0.0
    current_allocation: float = 0.0  # % of portfolio

class DynamicTradingUniverse:
    """
    Manages the active trading universe dynamically based on profitability
    """
    
    def __init__(self, max_active_symbols: int = 15):
        self.max_active_symbols = max_active_symbols
        
        # Universe sets
        self.active_symbols: Set[str] = set()  # Currently trading
        self.watchlist: Set[str] = set()        # Monitoring for entry
        self.blacklist: Set[str] = set()        # Temporarily avoiding
        
        # Performance tracking
        self.performance: Dict[str, AssetPerformance] = {}
        
        # Configuration
        self.min_profitability_score = 0.6
        self.max_blacklist_duration = timedelta(hours=1)
        self.rebalance_interval = timedelta(minutes=5)
        self.last_rebalance = datetime.now()
        
        logger.info("🌍 Dynamic Trading Universe initialized")
        logger.info(f"   Max active symbols: {max_active_symbols}")
    
    async def update_universe(self, opportunities: List[TradingOpportunity]) -> Dict[str, Any]:
        """
        Update the trading universe based on new opportunities
        
        Args:
            opportunities: List of discovered opportunities
        
        Returns:
            Update summary
        """
        logger.info("🔄 Updating trading universe...")
        
        added = []
        removed = []
        maintained = []
        
        # 1. Remove underperforming assets
        for symbol in list(self.active_symbols):
            if not self._should_keep_trading(symbol):
                self.active_symbols.remove(symbol)
                self.blacklist.add(symbol)
                removed.append(symbol)
                logger.info(f"   ❌ Removed {symbol} (underperforming)")
        
        # 2. Add new high-potential assets
        for opp in opportunities:
            if opp.symbol in self.blacklist:
                # Check if blacklist expired
                if not self._is_blacklisted(opp.symbol):
                    self.blacklist.remove(opp.symbol)
                else:
                    continue
            
            if opp.symbol not in self.active_symbols:
                if len(self.active_symbols) < self.max_active_symbols:
                    if opp.confidence >= 0.7 and opp.expected_return >= 0.01:
                        self.active_symbols.add(opp.symbol)
                        self.watchlist.discard(opp.symbol)
                        added.append(opp.symbol)
                        
                        # Initialize performance tracking
                        self.performance[opp.symbol] = AssetPerformance(
                            symbol=opp.symbol,
                            asset_class=opp.asset_class,
                            added_at=datetime.now(),
                            last_updated=datetime.now()
                        )
                        logger.info(f"   ✅ Added {opp.symbol} ({opp.asset_class.value}): "
                                  f"{opp.expected_return:.1%} return, {opp.confidence:.0%} conf")
                else:
                    # Add to watchlist if active is full
                    self.watchlist.add(opp.symbol)
            else:
                maintained.append(opp.symbol)
        
        # 3. Update watchlist
        self.watchlist = {opp.symbol for opp in opportunities[self.max_active_symbols:]}
        
        summary = {
            'active_symbols': len(self.active_symbols),
            'watchlist_size': len(self.watchlist),
            'blacklist_size': len(self.blacklist),
            'added': added,
            'removed': removed,
            'maintained': len(maintained)
        }
        
        logger.info(f"✅ Universe updated: {len(added)} added, {len(removed)} removed")
        logger.info(f"   Active: {len(self.active_symbols)}, Watchlist: {len(self.watchlist)}")
        
        return summary
    
    def _should_keep_trading(self, symbol: str) -> bool:
        """Determine if we should continue trading a symbol"""
        if symbol not in self.performance:
            return True  # Keep if no data yet
        
        perf = self.performance[symbol]
        
        # Keep if recently added (give it a chance)
        if datetime.now() - perf.added_at < timedelta(minutes=15):
            return True
        
        # Remove if consistently unprofitable
        if perf.trades_count >= 3 and perf.win_rate < 0.4:
            return False
        
        if perf.total_return < -0.02:  # -2% loss
            return False
        
        return True
    
    def _is_blacklisted(self, symbol: str) -> bool:
        """Check if symbol is still blacklisted"""
        if symbol not in self.blacklist:
            return False
        
        if symbol not in self.performance:
            return True
        
        perf = self.performance[symbol]
        time_since_removal = datetime.now() - perf.last_updated
        
        return time_since_removal < self.max_blacklist_duration
    
    def update_performance(self, symbol: str, trade_return: float, 
                          holding_time_minutes: float, won: bool):
        """Update performance metrics for a symbol"""
        if symbol not in self.performance:
            return
        
        perf = self.performance[symbol]
        perf.trades_count += 1
        perf.total_return += trade_return
        
        # Update win rate
        old_wins = perf.win_rate * (perf.trades_count - 1)
        new_wins = old_wins + (1 if won else 0)
        perf.win_rate = new_wins / perf.trades_count
        
        # Update average holding time
        perf.avg_holding_time = (
            (perf.avg_holding_time * (perf.trades_count - 1) + holding_time_minutes) 
            / perf.trades_count
        )
        
        # Calculate profitability score
        perf.profitability_score = self._calculate_profitability_score(perf)
        perf.last_updated = datetime.now()
        
        logger.debug(f"Updated {symbol}: {perf.trades_count} trades, "
                    f"{perf.win_rate:.0%} win rate, {perf.total_return:.2%} return")
    
    def _calculate_profitability_score(self, perf: AssetPerformance) -> float:
        """Calculate overall profitability score"""
        if perf.trades_count == 0:
            return 0.5
        
        # Weighted score
        return_score = min(1.0, max(0.0, (perf.total_return + 0.05) / 0.1))
        win_rate_score = perf.win_rate
        activity_score = min(1.0, perf.trades_count / 10)
        
        score = (
            return_score * 0.5 +
            win_rate_score * 0.3 +
            activity_score * 0.2
        )
        
        return score
    
    def get_active_symbols(self) -> List[str]:
        """Get list of currently active symbols"""
        return list(self.active_symbols)
    
    def get_top_performers(self, limit: int = 5) -> List[AssetPerformance]:
        """Get top performing assets"""
        performers = [p for p in self.performance.values() if p.trades_count > 0]
        performers.sort(key=lambda x: x.profitability_score, reverse=True)
        return performers[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get universe statistics"""
        return {
            'active_symbols': len(self.active_symbols),
            'watchlist_size': len(self.watchlist),
            'blacklist_size': len(self.blacklist),
            'total_tracked': len(self.performance),
            'avg_profitability': np.mean([p.profitability_score for p in self.performance.values()]) if self.performance else 0,
            'total_trades': sum(p.trades_count for p in self.performance.values()),
            'overall_win_rate': np.mean([p.win_rate for p in self.performance.values() if p.trades_count > 0]) if self.performance else 0
        }

# Global instance
dynamic_universe = DynamicTradingUniverse()

