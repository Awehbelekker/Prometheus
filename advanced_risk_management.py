"""
PROMETHEUS Advanced Risk Management System
===========================================
Implements Kelly Criterion, volatility-based position sizing, and drawdown protection.

Addresses performance issues from 50-year benchmark:
- Drawdown increased from -6.36% to -14.66% → Conservative volatility scaling
- Win rate dropped from 58.9% to 55.4% → Higher confidence thresholds
- Risk management → Kelly Criterion prevents over-leveraging

Author: PROMETHEUS Trading Platform
Version: 1.0.0
Date: 2026-03-09
"""

import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np

logger = logging.getLogger(__name__)


class KellyPositionSizer:
    """
    Kelly Criterion position sizing with fractional Kelly for safety.
    
    Formula: f = (p * (b + 1) - 1) / b
    Where:
        f = fraction of capital to bet
        p = probability of winning
        b = ratio of amount won to amount wagered
    
    Uses fractional Kelly (0.25x) to reduce volatility.
    """
    
    def __init__(
        self,
        fractional_kelly: float = 0.25,  # Conservative: use 1/4 Kelly
        min_win_rate: float = 0.52,      # Minimum 52% win rate to trade
        max_position: float = 0.10,      # Max 10% per position
        min_position: float = 0.01       # Min 1% per position
    ):
        self.fractional_kelly = fractional_kelly
        self.min_win_rate = min_win_rate
        self.max_position = max_position
        self.min_position = min_position
        
        logger.debug(f"🎯 Kelly Position Sizer initialized")
        logger.debug(f"   Fractional Kelly: {fractional_kelly}x (conservative)")
        logger.debug(f"   Min Win Rate: {min_win_rate*100:.1f}%")
        logger.debug(f"   Position Limits: {min_position*100:.1f}% - {max_position*100:.1f}%")
    
    def calculate_position_size(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        confidence: float = 0.5,
        capital: float = 100000.0
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate optimal position size using Kelly Criterion.
        
        Args:
            win_rate: Historical win rate (0.0 to 1.0)
            avg_win: Average winning trade amount
            avg_loss: Average losing trade amount (positive value)
            confidence: AI confidence in this trade (0.0 to 1.0)
            capital: Total capital available
        
        Returns:
            (position_size_dollars, metrics_dict)
        """
        # Validate inputs
        if win_rate < self.min_win_rate:
            logger.debug(f"Win rate {win_rate:.1%} below minimum {self.min_win_rate:.1%} - NO TRADE")
            return 0.0, {"reason": "win_rate_too_low", "kelly_fraction": 0.0}
        
        if avg_loss <= 0:
            avg_loss = 0.01  # Prevent division by zero
        
        # Calculate win/loss ratio (b in Kelly formula)
        win_loss_ratio = avg_win / avg_loss
        
        # Kelly Criterion: f = (p * (b + 1) - 1) / b
        kelly_fraction = (win_rate * (win_loss_ratio + 1) - 1) / win_loss_ratio
        
        # Apply fractional Kelly for safety
        kelly_fraction *= self.fractional_kelly
        
        # Adjust by AI confidence (higher confidence = larger position)
        confidence_adjusted = kelly_fraction * (0.5 + 0.5 * confidence)
        
        # Clamp to position limits
        final_fraction = np.clip(confidence_adjusted, self.min_position, self.max_position)
        
        # Calculate dollar amount
        position_size = capital * final_fraction
        
        metrics = {
            "kelly_fraction": kelly_fraction,
            "confidence_adjusted": confidence_adjusted,
            "final_fraction": final_fraction,
            "position_size": position_size,
            "win_rate": win_rate,
            "win_loss_ratio": win_loss_ratio,
            "confidence": confidence
        }
        
        logger.info(f"💰 Kelly Position: ${position_size:,.2f} ({final_fraction:.1%} of capital)")
        logger.info(f"   Win Rate: {win_rate:.1%} | W/L: {win_loss_ratio:.2f} | Confidence: {confidence:.1%}")
        
        return position_size, metrics


class VolatilityScaler:
    """
    Scale position sizes based on market volatility (VIX).
    High volatility = smaller positions to protect capital.
    """
    
    def __init__(
        self,
        vix_low: float = 15.0,    # VIX below this = normal sizing
        vix_medium: float = 25.0,  # VIX above this = reduce positions
        vix_high: float = 35.0,    # VIX above this = aggressive reduction
        vix_extreme: float = 50.0  # VIX above this = minimal positions
    ):
        self.vix_low = vix_low
        self.vix_medium = vix_medium
        self.vix_high = vix_high
        self.vix_extreme = vix_extreme
        
        logger.debug(f"📊 Volatility Scaler initialized")
        logger.debug(f"   VIX Thresholds: Low={vix_low}, Medium={vix_medium}, High={vix_high}, Extreme={vix_extreme}")
    
    def get_volatility_multiplier(self, vix: float) -> Tuple[float, str]:
        """
        Get position size multiplier based on VIX level.
        
        Args:
            vix: Current VIX value
        
        Returns:
            (multiplier, regime_name)
        """
        if vix < self.vix_low:
            return 1.0, "LOW_VOL"
        elif vix < self.vix_medium:
            # Linear scale from 1.0 to 0.7
            multiplier = 1.0 - 0.3 * (vix - self.vix_low) / (self.vix_medium - self.vix_low)
            return multiplier, "MEDIUM_VOL"
        elif vix < self.vix_high:
            # Linear scale from 0.7 to 0.4
            multiplier = 0.7 - 0.3 * (vix - self.vix_medium) / (self.vix_high - self.vix_medium)
            return multiplier, "HIGH_VOL"
        elif vix < self.vix_extreme:
            # Linear scale from 0.4 to 0.15
            multiplier = 0.4 - 0.25 * (vix - self.vix_high) / (self.vix_extreme - self.vix_high)
            return multiplier, "EXTREME_VOL"
        else:
            return 0.15, "CRISIS"
    
    def scale_position(
        self,
        base_position: float,
        vix: float
    ) -> Tuple[float, Dict[str, any]]:
        """
        Scale a position based on current volatility.
        
        Args:
            base_position: Base position size (dollars)
            vix: Current VIX value
        
        Returns:
            (scaled_position, metrics_dict)
        """
        multiplier, regime = self.get_volatility_multiplier(vix)
        scaled_position = base_position * multiplier
        
        metrics = {
            "base_position": base_position,
            "scaled_position": scaled_position,
            "vix": vix,
            "multiplier": multiplier,
            "regime": regime,
            "reduction_pct": (1 - multiplier) * 100
        }
        
        if multiplier < 1.0:
            logger.info(f"⚠️ Volatility Scaling: {regime} (VIX={vix:.1f})")
            logger.info(f"   Position reduced {metrics['reduction_pct']:.1f}%: ${base_position:,.2f} → ${scaled_position:,.2f}")
        
        return scaled_position, metrics


class DrawdownProtection:
    """
    Reduce position sizes when approaching drawdown limits.
    Protects against cascade losses.
    """
    
    def __init__(
        self,
        max_drawdown: float = 0.15,      # Max 15% drawdown allowed
        warning_level: float = 0.10,     # Start reducing at 10% drawdown
        emergency_level: float = 0.13    # Aggressive reduction at 13%
    ):
        self.max_drawdown = max_drawdown
        self.warning_level = warning_level
        self.emergency_level = emergency_level
        
        logger.debug(f"🛡️ Drawdown Protection initialized")
        logger.debug(f"   Max Drawdown: {max_drawdown*100:.1f}%")
        logger.debug(f"   Warning Level: {warning_level*100:.1f}%")
        logger.debug(f"   Emergency Level: {emergency_level*100:.1f}%")
    
    def get_drawdown_multiplier(
        self,
        current_drawdown: float
    ) -> Tuple[float, str]:
        """
        Get position multiplier based on current drawdown.
        
        Args:
            current_drawdown: Current drawdown as fraction (e.g., 0.12 = 12%)
        
        Returns:
            (multiplier, status)
        """
        if current_drawdown < self.warning_level:
            return 1.0, "NORMAL"
        elif current_drawdown < self.emergency_level:
            # Linear scale from 1.0 to 0.5
            multiplier = 1.0 - 0.5 * (current_drawdown - self.warning_level) / (self.emergency_level - self.warning_level)
            return multiplier, "WARNING"
        elif current_drawdown < self.max_drawdown:
            # Linear scale from 0.5 to 0.2
            multiplier = 0.5 - 0.3 * (current_drawdown - self.emergency_level) / (self.max_drawdown - self.emergency_level)
            return multiplier, "EMERGENCY"
        else:
            return 0.0, "HALT"
    
    def protect_position(
        self,
        base_position: float,
        current_capital: float,
        peak_capital: float
    ) -> Tuple[float, Dict[str, any]]:
        """
        Apply drawdown protection to position size.
        
        Args:
            base_position: Base position size
            current_capital: Current capital
            peak_capital: Peak capital (high watermark)
        
        Returns:
            (protected_position, metrics_dict)
        """
        # Calculate current drawdown
        drawdown = (peak_capital - current_capital) / peak_capital if peak_capital > 0 else 0.0
        
        multiplier, status = self.get_drawdown_multiplier(drawdown)
        protected_position = base_position * multiplier
        
        metrics = {
            "base_position": base_position,
            "protected_position": protected_position,
            "current_drawdown": drawdown,
            "drawdown_pct": drawdown * 100,
            "multiplier": multiplier,
            "status": status
        }
        
        if status != "NORMAL":
            logger.warning(f"🛡️ Drawdown Protection: {status}")
            logger.warning(f"   Current Drawdown: {drawdown*100:.2f}%")
            logger.warning(f"   Position reduced: ${base_position:,.2f} → ${protected_position:,.2f}")
        
        if status == "HALT":
            logger.critical(f"🚨 TRADING HALTED - Drawdown {drawdown*100:.2f}% exceeds limit {self.max_drawdown*100:.1f}%")
        
        return protected_position, metrics


class AdvancedRiskManager:
    """
    Master risk management system combining Kelly Criterion, volatility scaling,
    and drawdown protection.
    """
    
    def __init__(
        self,
        fractional_kelly: float = 0.25,
        min_confidence: float = 0.55,  # Raised from 0.50 to improve win rate
        enable_volatility_scaling: bool = True,
        enable_drawdown_protection: bool = True
    ):
        self.kelly_sizer = KellyPositionSizer(fractional_kelly=fractional_kelly)
        self.volatility_scaler = VolatilityScaler() if enable_volatility_scaling else None
        self.drawdown_protection = DrawdownProtection() if enable_drawdown_protection else None
        
        self.min_confidence = min_confidence
        self.enable_volatility_scaling = enable_volatility_scaling
        self.enable_drawdown_protection = enable_drawdown_protection
        
        # Performance tracking
        self.trade_history = []
        self.peak_capital = 0.0
        
        logger.debug(f"🎯 Advanced Risk Manager initialized")
        logger.debug(f"   Minimum Confidence: {min_confidence*100:.1f}% (raised to improve win rate)")
        logger.debug(f"   Volatility Scaling: {'ENABLED' if enable_volatility_scaling else 'DISABLED'}")
        logger.debug(f"   Drawdown Protection: {'ENABLED' if enable_drawdown_protection else 'DISABLED'}")
    
    def calculate_optimal_position(
        self,
        symbol: str,
        confidence: float,
        capital: float,
        vix: float = 20.0,
        historical_performance: Optional[Dict] = None
    ) -> Tuple[float, Dict[str, any]]:
        """
        Calculate optimal position size with all risk management layers.
        
        Args:
            symbol: Trading symbol
            confidence: AI confidence (0.0 to 1.0)
            capital: Total capital available
            vix: Current VIX value
            historical_performance: Dict with 'win_rate', 'avg_win', 'avg_loss'
        
        Returns:
            (final_position_size, detailed_metrics)
        """
        # Update peak capital for drawdown protection
        if capital > self.peak_capital:
            self.peak_capital = capital
        
        # Step 1: Confidence filter (improved from 50% to 55% threshold)
        if confidence < self.min_confidence:
            logger.debug(f"{symbol}: Confidence {confidence:.1%} below threshold {self.min_confidence:.1%} - NO TRADE")
            return 0.0, {
                "reason": "low_confidence",
                "confidence": confidence,
                "threshold": self.min_confidence,
                "final_position": 0.0
            }
        
        # Step 2: Kelly Criterion base position
        if historical_performance:
            win_rate = historical_performance.get('win_rate', 0.554)  # Use benchmark win rate
            avg_win = historical_performance.get('avg_win', 0.02)
            avg_loss = historical_performance.get('avg_loss', 0.015)
        else:
            # Use benchmark performance as defaults
            win_rate = 0.554  # 55.4% from latest benchmark
            avg_win = 0.02    # 2% avg win
            avg_loss = 0.015  # 1.5% avg loss
        
        kelly_position, kelly_metrics = self.kelly_sizer.calculate_position_size(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            confidence=confidence,
            capital=capital
        )
        
        if kelly_position == 0.0:
            return 0.0, {**kelly_metrics, "final_position": 0.0}
        
        # Step 3: Volatility scaling
        if self.volatility_scaler:
            volatility_position, vol_metrics = self.volatility_scaler.scale_position(
                kelly_position, vix
            )
        else:
            volatility_position = kelly_position
            vol_metrics = {"regime": "SCALING_DISABLED"}
        
        # Step 4: Drawdown protection
        if self.drawdown_protection:
            final_position, dd_metrics = self.drawdown_protection.protect_position(
                volatility_position, capital, self.peak_capital
            )
        else:
            final_position = volatility_position
            dd_metrics = {"status": "PROTECTION_DISABLED"}
        
        # Combine all metrics
        all_metrics = {
            "symbol": symbol,
            "confidence": confidence,
            "capital": capital,
            "vix": vix,
            "kelly": kelly_metrics,
            "volatility": vol_metrics,
            "drawdown": dd_metrics,
            "final_position": final_position,
            "final_fraction": final_position / capital if capital > 0 else 0.0
        }
        
        logger.info(f"✅ {symbol}: Final Position ${final_position:,.2f} ({all_metrics['final_fraction']:.2%} of capital)")
        
        return final_position, all_metrics
    
    def record_trade(
        self,
        symbol: str,
        entry_price: float,
        exit_price: float,
        position_size: float,
        profit_loss: float
    ):
        """Record trade outcome for historical performance tracking."""
        trade = {
            "timestamp": datetime.now(),
            "symbol": symbol,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "position_size": position_size,
            "profit_loss": profit_loss,
            "win": profit_loss > 0
        }
        self.trade_history.append(trade)
        
        # Keep last 100 trades
        if len(self.trade_history) > 100:
            self.trade_history = self.trade_history[-100:]
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Calculate historical performance statistics."""
        if not self.trade_history:
            return {
                "win_rate": 0.554,
                "avg_win": 0.02,
                "avg_loss": 0.015,
                "total_trades": 0
            }
        
        wins = [t for t in self.trade_history if t['win']]
        losses = [t for t in self.trade_history if not t['win']]
        
        win_rate = len(wins) / len(self.trade_history) if self.trade_history else 0.0
        avg_win = np.mean([t['profit_loss'] for t in wins]) if wins else 0.02
        avg_loss = abs(np.mean([t['profit_loss'] for t in losses])) if losses else 0.015
        
        return {
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "total_trades": len(self.trade_history),
            "total_wins": len(wins),
            "total_losses": len(losses)
        }


# Global instance
_risk_manager = None


def get_risk_manager() -> AdvancedRiskManager:
    """Get or create global risk manager instance."""
    global _risk_manager
    if _risk_manager is None:
        _risk_manager = AdvancedRiskManager(
            fractional_kelly=0.25,      # Conservative 1/4 Kelly
            min_confidence=0.55,         # Raised from 0.50 to improve win rate
            enable_volatility_scaling=True,
            enable_drawdown_protection=True
        )
    return _risk_manager


if __name__ == "__main__":
    # Test the risk manager
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("TESTING PROMETHEUS ADVANCED RISK MANAGEMENT")
    print("="*60 + "\n")
    
    rm = get_risk_manager()
    
    # Test scenarios
    test_cases = [
        {"name": "High Confidence, Low VIX", "confidence": 0.85, "vix": 12, "capital": 100000},
        {"name": "Medium Confidence, Medium VIX", "confidence": 0.65, "vix": 22, "capital": 100000},
        {"name": "Low Confidence (rejected)", "confidence": 0.45, "vix": 18, "capital": 100000},
        {"name": "High VIX (crisis)", "confidence": 0.75, "vix": 55, "capital": 100000},
        {"name": "Drawdown scenario", "confidence": 0.70, "vix": 25, "capital": 87000},  # 13% drawdown
    ]
    
    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"Test: {test['name']}")
        print(f"{'='*60}")
        
        position, metrics = rm.calculate_optimal_position(
            symbol="AAPL",
            confidence=test['confidence'],
            capital=test['capital'],
            vix=test['vix']
        )
        
        print(f"\nFinal Position: ${position:,.2f}")
        print(f"Fraction of Capital: {metrics.get('final_fraction', 0)*100:.2f}%")
        print()
