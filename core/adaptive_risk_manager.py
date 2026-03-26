#!/usr/bin/env python3
"""
PROMETHEUS Adaptive Risk Manager
================================
Central risk management that ALL trading scripts use.
Provides adaptive confidence thresholds based on performance.

Connects existing learning infrastructure to live trading.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

# Persistence file for learning across sessions
RISK_STATE_FILE = Path(__file__).parent.parent / "data" / "adaptive_risk_state.json"


@dataclass
class TradeRecord:
    """Record of a completed trade for learning"""
    trade_id: str
    timestamp: str
    symbol: str
    asset_type: str  # crypto, stock, option
    action: str  # buy, sell
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    profit_loss: float
    confidence_used: float
    market_volatility: float
    won: bool


@dataclass 
class AssetPerformance:
    """Performance metrics for a specific asset"""
    symbol: str
    total_trades: int = 0
    wins: int = 0
    losses: int = 0
    total_profit: float = 0.0
    avg_confidence_on_win: float = 0.6
    avg_confidence_on_loss: float = 0.6
    current_streak: int = 0  # positive = wins, negative = losses
    optimal_confidence: float = 0.60  # Learned optimal threshold


class AdaptiveRiskManager:
    """
    Central adaptive risk manager for all PROMETHEUS trading.
    
    Features:
    - Dynamic confidence thresholds per asset
    - Learns from wins/losses
    - Volatility-aware adjustments
    - Drawdown protection
    - Persists learning across sessions
    """
    
    def __init__(self):
        # Base thresholds
        self.base_confidence = 0.55  # Start relatively low
        self.min_confidence = 0.40   # Never go below this
        self.max_confidence = 0.85   # Never require above this
        
        # Asset-specific performance
        self.asset_performance: Dict[str, AssetPerformance] = {}
        
        # Session tracking
        self.session_trades: List[TradeRecord] = []
        self.session_start = datetime.now()
        self.session_profit = 0.0
        self.session_max_drawdown = 0.0
        self.session_peak = 0.0
        
        # Global state
        self.total_trades_all_time = 0
        self.overall_win_rate = 0.5
        self.is_in_drawdown = False
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        
        # Volatility tracking
        self.market_volatility: Dict[str, float] = {}  # per asset
        
        # Load persisted state
        self._load_state()
        
        logger.info("🎯 Adaptive Risk Manager initialized")
        logger.info(f"   Base confidence: {self.base_confidence:.0%}")
        logger.info(f"   Range: {self.min_confidence:.0%} - {self.max_confidence:.0%}")
        logger.info(f"   Loaded {len(self.asset_performance)} asset histories")
    
    def _load_state(self):
        """Load persisted learning state"""
        try:
            RISK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            if RISK_STATE_FILE.exists():
                with open(RISK_STATE_FILE, 'r') as f:
                    data = json.load(f)
                
                self.total_trades_all_time = data.get('total_trades', 0)
                self.overall_win_rate = data.get('overall_win_rate', 0.5)
                
                # Load asset performance
                for symbol, perf_data in data.get('asset_performance', {}).items():
                    self.asset_performance[symbol] = AssetPerformance(
                        symbol=symbol,
                        total_trades=perf_data.get('total_trades', 0),
                        wins=perf_data.get('wins', 0),
                        losses=perf_data.get('losses', 0),
                        total_profit=perf_data.get('total_profit', 0.0),
                        avg_confidence_on_win=perf_data.get('avg_confidence_on_win', 0.6),
                        avg_confidence_on_loss=perf_data.get('avg_confidence_on_loss', 0.6),
                        current_streak=perf_data.get('current_streak', 0),
                        optimal_confidence=perf_data.get('optimal_confidence', 0.60)
                    )
                
                logger.info(f"   Loaded state: {self.total_trades_all_time} historical trades")
        except Exception as e:
            logger.warning(f"Could not load risk state: {e}")
    
    def _save_state(self):
        """Persist learning state"""
        try:
            RISK_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'total_trades': self.total_trades_all_time,
                'overall_win_rate': self.overall_win_rate,
                'last_updated': datetime.now().isoformat(),
                'asset_performance': {
                    symbol: asdict(perf) 
                    for symbol, perf in self.asset_performance.items()
                }
            }
            
            with open(RISK_STATE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Could not save risk state: {e}")
    
    def get_confidence_threshold(self, symbol: str, asset_type: str = 'crypto', 
                                  volatility: float = 1.0) -> float:
        """
        Get the adaptive confidence threshold for a specific asset.
        
        This is the MAIN method trading scripts should call.
        
        Args:
            symbol: Asset symbol (e.g., 'BTC/USD', 'AAPL')
            asset_type: 'crypto', 'stock', 'option'
            volatility: Current market volatility (1.0 = normal)
        
        Returns:
            Confidence threshold (0.0 - 1.0) - trade if signal >= this
        """
        # Start with base threshold
        threshold = self.base_confidence
        
        # Asset-specific adjustment
        if symbol in self.asset_performance:
            perf = self.asset_performance[symbol]
            
            if perf.total_trades >= 5:
                # Use learned optimal confidence
                threshold = perf.optimal_confidence
                
                # Adjust for recent streak
                if perf.current_streak >= 3:
                    # Winning streak - can be slightly more aggressive
                    threshold -= 0.05
                elif perf.current_streak <= -3:
                    # Losing streak - be more conservative
                    threshold += 0.10
        
        # Volatility adjustment
        if volatility > 1.5:
            # High volatility - require more confidence
            threshold += 0.10
        elif volatility < 0.5:
            # Low volatility - can be more aggressive
            threshold -= 0.05
        
        # Drawdown protection
        if self.is_in_drawdown:
            threshold += 0.15  # Much more conservative
        
        # Consecutive loss protection
        if self.consecutive_losses >= 3:
            threshold += 0.05 * (self.consecutive_losses - 2)
        
        # Asset type adjustments
        if asset_type == 'crypto':
            threshold -= 0.03  # Crypto is 24/7, can be slightly more active
        elif asset_type == 'option':
            threshold += 0.05  # Options need more confidence
        
        # Clamp to valid range
        threshold = max(self.min_confidence, min(self.max_confidence, threshold))
        
        return round(threshold, 2)
    
    def get_position_size_multiplier(self, symbol: str, confidence: float) -> float:
        """
        Get position size multiplier based on confidence and history.
        
        Returns multiplier (0.5 - 1.5) to apply to base position size.
        """
        multiplier = 1.0
        
        # Higher confidence = larger position
        if confidence >= 0.80:
            multiplier = 1.3
        elif confidence >= 0.70:
            multiplier = 1.1
        elif confidence < 0.55:
            multiplier = 0.7
        
        # Asset-specific adjustment
        if symbol in self.asset_performance:
            perf = self.asset_performance[symbol]
            win_rate = perf.wins / max(1, perf.total_trades)
            
            if win_rate >= 0.65 and perf.total_trades >= 10:
                multiplier *= 1.2  # Proven winner
            elif win_rate < 0.40 and perf.total_trades >= 5:
                multiplier *= 0.6  # Reduce on losers
        
        # Drawdown protection
        if self.is_in_drawdown:
            multiplier *= 0.5
        
        return max(0.3, min(1.5, multiplier))
    
    def record_trade(self, symbol: str, asset_type: str, action: str,
                     entry_price: float, exit_price: float, quantity: float,
                     confidence_used: float, volatility: float = 1.0) -> None:
        """
        Record a completed trade for learning.
        
        Call this after EVERY trade closes (win or loss).
        """
        profit_loss = (exit_price - entry_price) * quantity
        if action == 'sell':
            profit_loss = -profit_loss
        
        won = profit_loss > 0
        
        trade = TradeRecord(
            trade_id=f"{symbol}_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            symbol=symbol,
            asset_type=asset_type,
            action=action,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            profit_loss=profit_loss,
            confidence_used=confidence_used,
            market_volatility=volatility,
            won=won
        )
        
        self.session_trades.append(trade)
        self._update_performance(trade)
        self._save_state()
        
        logger.info(f"📊 Trade recorded: {symbol} {'WIN' if won else 'LOSS'} ${profit_loss:+.2f}")
    
    def _update_performance(self, trade: TradeRecord):
        """Update performance metrics from a trade"""
        symbol = trade.symbol
        
        # Initialize if new asset
        if symbol not in self.asset_performance:
            self.asset_performance[symbol] = AssetPerformance(symbol=symbol)
        
        perf = self.asset_performance[symbol]
        
        # Update counts
        perf.total_trades += 1
        perf.total_profit += trade.profit_loss
        
        if trade.won:
            perf.wins += 1
            perf.current_streak = max(1, perf.current_streak + 1)
            
            # Update average winning confidence
            alpha = 0.2
            perf.avg_confidence_on_win = (
                (1 - alpha) * perf.avg_confidence_on_win + 
                alpha * trade.confidence_used
            )
        else:
            perf.losses += 1
            perf.current_streak = min(-1, perf.current_streak - 1)
            
            # Update average losing confidence
            alpha = 0.2
            perf.avg_confidence_on_loss = (
                (1 - alpha) * perf.avg_confidence_on_loss + 
                alpha * trade.confidence_used
            )
        
        # Learn optimal confidence
        # Optimal is between avg winning confidence and avg losing confidence
        if perf.total_trades >= 5:
            # Weight towards the winning confidence
            win_rate = perf.wins / perf.total_trades
            if win_rate >= 0.5:
                # More wins - can use confidence closer to avg winning
                perf.optimal_confidence = (
                    0.7 * perf.avg_confidence_on_win + 
                    0.3 * perf.avg_confidence_on_loss
                )
            else:
                # More losses - need higher confidence
                perf.optimal_confidence = (
                    0.4 * perf.avg_confidence_on_win + 
                    0.6 * perf.avg_confidence_on_loss + 0.05
                )
        
        # Clamp optimal confidence
        perf.optimal_confidence = max(0.45, min(0.80, perf.optimal_confidence))
        
        # Update global stats
        self.total_trades_all_time += 1
        self.session_profit += trade.profit_loss
        
        # Track session peak for drawdown
        if self.session_profit > self.session_peak:
            self.session_peak = self.session_profit
        
        # Calculate drawdown
        if self.session_peak > 0:
            drawdown = (self.session_peak - self.session_profit) / self.session_peak
            self.session_max_drawdown = max(self.session_max_drawdown, drawdown)
            self.is_in_drawdown = drawdown > 0.10  # 10% drawdown triggers protection
        
        # Update consecutive tracking
        if trade.won:
            self.consecutive_losses = 0
            self.consecutive_wins += 1
        else:
            self.consecutive_wins = 0
            self.consecutive_losses += 1
        
        # Update overall win rate
        total_wins = sum(p.wins for p in self.asset_performance.values())
        total_trades = sum(p.total_trades for p in self.asset_performance.values())
        if total_trades > 0:
            self.overall_win_rate = total_wins / total_trades
    
    def should_pause_trading(self) -> tuple[bool, str]:
        """
        Check if trading should be paused for protection.
        
        Returns:
            (should_pause, reason)
        """
        # Too many consecutive losses
        if self.consecutive_losses >= 5:
            return True, f"5 consecutive losses - take a break"
        
        # Severe drawdown
        if self.session_max_drawdown > 0.20:
            return True, f"20% drawdown reached - protect capital"
        
        # Poor session performance
        if len(self.session_trades) >= 10:
            session_win_rate = sum(1 for t in self.session_trades if t.won) / len(self.session_trades)
            if session_win_rate < 0.30:
                return True, f"Session win rate {session_win_rate:.0%} too low"
        
        return False, ""
    
    def get_status(self) -> Dict[str, Any]:
        """Get current risk manager status"""
        return {
            'session_trades': len(self.session_trades),
            'session_profit': self.session_profit,
            'session_drawdown': self.session_max_drawdown,
            'consecutive_wins': self.consecutive_wins,
            'consecutive_losses': self.consecutive_losses,
            'is_in_drawdown': self.is_in_drawdown,
            'overall_win_rate': self.overall_win_rate,
            'total_trades_all_time': self.total_trades_all_time,
            'assets_tracked': len(self.asset_performance),
            'should_pause': self.should_pause_trading()
        }
    
    def get_asset_summary(self, symbol: str) -> Dict[str, Any]:
        """Get performance summary for an asset"""
        if symbol not in self.asset_performance:
            return {'symbol': symbol, 'trades': 0, 'message': 'No history'}
        
        perf = self.asset_performance[symbol]
        win_rate = perf.wins / max(1, perf.total_trades)
        
        return {
            'symbol': symbol,
            'total_trades': perf.total_trades,
            'wins': perf.wins,
            'losses': perf.losses,
            'win_rate': win_rate,
            'total_profit': perf.total_profit,
            'current_streak': perf.current_streak,
            'optimal_confidence': perf.optimal_confidence,
            'current_threshold': self.get_confidence_threshold(symbol)
        }


# Global singleton instance
_risk_manager: Optional[AdaptiveRiskManager] = None

def get_risk_manager() -> AdaptiveRiskManager:
    """Get the global risk manager instance"""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = AdaptiveRiskManager()
    return _risk_manager


# Convenience functions for trading scripts
def get_confidence_threshold(symbol: str, asset_type: str = 'crypto', 
                             volatility: float = 1.0) -> float:
    """Get adaptive confidence threshold for a symbol"""
    return get_risk_manager().get_confidence_threshold(symbol, asset_type, volatility)


def record_trade(symbol: str, asset_type: str, action: str,
                 entry_price: float, exit_price: float, quantity: float,
                 confidence_used: float, volatility: float = 1.0) -> None:
    """Record a completed trade"""
    get_risk_manager().record_trade(
        symbol, asset_type, action, entry_price, exit_price,
        quantity, confidence_used, volatility
    )


def should_pause_trading() -> tuple[bool, str]:
    """Check if trading should pause"""
    return get_risk_manager().should_pause_trading()


if __name__ == "__main__":
    # Test the adaptive risk manager
    logging.basicConfig(level=logging.INFO)
    
    rm = AdaptiveRiskManager()
    
    print("\n=== Adaptive Risk Manager Test ===\n")
    
    # Test confidence thresholds
    symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'TSLA']
    for sym in symbols:
        threshold = rm.get_confidence_threshold(sym)
        print(f"{sym}: threshold = {threshold:.0%}")
    
    # Simulate some trades
    print("\nSimulating trades...")
    rm.record_trade('BTC/USD', 'crypto', 'buy', 95000, 96000, 0.01, 0.65)  # Win
    rm.record_trade('BTC/USD', 'crypto', 'buy', 96000, 95500, 0.01, 0.70)  # Loss
    rm.record_trade('ETH/USD', 'crypto', 'buy', 3300, 3400, 0.1, 0.60)     # Win
    rm.record_trade('ETH/USD', 'crypto', 'buy', 3400, 3450, 0.1, 0.55)     # Win
    
    # Check updated thresholds
    print("\nUpdated thresholds after learning:")
    for sym in ['BTC/USD', 'ETH/USD']:
        threshold = rm.get_confidence_threshold(sym)
        summary = rm.get_asset_summary(sym)
        print(f"{sym}: threshold = {threshold:.0%}, win_rate = {summary['win_rate']:.0%}")
    
    print("\n" + "=" * 40)
    print("Status:", rm.get_status())
