"""
OPTIMIZED TRADING PARAMETERS - Updated 2025-10-21 23:10:00
Focus: Better profit taking, more short opportunities, optimized for limited capital
"""

# ============================================================================
# OPTIMIZED RISK MANAGEMENT PARAMETERS
# ============================================================================

RISK_PARAMETERS = {
    # Daily Loss Limit - Conservative for limited capital
    'daily_loss_limit': 10,
    
    # Position Size - Optimized for $0.98 buying power
    'position_size_pct': 0.015,  # 1.5% (reduced for limited capital)
    
    # Maximum Concurrent Positions - Focused approach
    'max_positions': 6,
    
    # Stop Loss - Slightly wider for better execution
    'stop_loss_pct': 0.03,  # 3% (slightly wider)
    
    # Take Profit - Increased for better profit capture
    'take_profit_pct': 0.08,  # 8% (increased from 5%)
    
    # Trailing Stop - More room for growth
    'trailing_stop_pct': 0.025,  # 2.5% (increased from 1.5%)
    
    # Maximum Drawdown - Tighter control
    'max_drawdown_pct': 0.1,  # 10% (tighter control)
    
    # Minimum Confidence - Higher quality trades
    'min_confidence': 0.75,  # 75% (increased from 72%)
}

# ============================================================================
# SHORT SELLING OPTIMIZATION
# ============================================================================

SHORT_SELLING_CONFIG = {
    'enabled': True,
    'target_short_ratio': 0.5,  # 50% of trades should be shorts
    'short_take_profit_pct': 0.06,  # 6% for shorts
    'short_stop_loss_pct': 0.04,    # 4% wider stops for shorts
    'short_trailing_stop_pct': 0.03, # 3% trailing for shorts
}

# ============================================================================
# PROFIT TAKING OPTIMIZATION
# ============================================================================

PROFIT_TAKING_CONFIG = {
    'partial_profit_taking': True,
    'first_profit_target': 0.04,  # Take 50% at 4%
    'second_profit_target': 0.08, # Take rest at 8%
    'dynamic_take_profit': True,  # Adjust based on volatility
    'volatility_multiplier': 1.5, # Increase targets in high volatility
}

# ============================================================================
# POSITION MANAGEMENT
# ============================================================================

POSITION_MANAGEMENT = {
    'monitoring_interval': 60,    # Check positions every 60 seconds
    'max_hold_hours': 24,         # Maximum 24 hours hold
    'time_based_exit': True,      # Exit after max hold time
    'volatility_sizing': True,    # Adjust size based on volatility
}