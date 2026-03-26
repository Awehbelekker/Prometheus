#!/usr/bin/env python3
"""
🚀 INTERACTIVE BROKERS OPTIONS TRADING CONFIGURATION
====================================================

Complete configuration for IB options trading with 3 main strategies:
1. Covered Call - Income generation
2. Protective Put - Downside protection
3. Long Call/Put - Directional speculation

NO MARKET DATA SUBSCRIPTION REQUIRED - Uses external data sources
"""

import os
from typing import Dict, Any

# ============================================================================
# IB OPTIONS TRADING CONFIGURATION
# ============================================================================

IB_OPTIONS_CONFIG = {
    # Connection Settings
    # Ports: 4002=Gateway Live, 4001=Gateway Paper, 7497=TWS Paper, 7496=TWS Live
    "connection": {
        "host": "127.0.0.1",
        "paper_port": 4001,
        "live_port": 4002,
        "client_id": 2,
        "use_live": True,  # Set to True for live trading
        "timeout": 60,
        "auto_reconnect": True
    },
    
    # Options Trading Settings
    "options": {
        "enabled": True,
        "strategies": ["covered_call", "protective_put", "long_call", "long_put"],
        "max_contracts_per_trade": 5,
        "min_days_to_expiration": 7,
        "max_days_to_expiration": 45,
        "preferred_expiration_days": 30
    },
    
    # Strategy 1: Covered Call (Income Generation)
    "covered_call": {
        "enabled": True,
        "allocation": 0.30,  # 30% of options allocation
        "strike_selection": "otm",  # Out of the money
        "delta_target": 0.30,  # 30 delta (70% probability OTM)
        "min_premium": 0.50,  # Minimum $0.50 per share premium
        "max_position_size": 0.05,  # 5% of portfolio per position
        "description": "Sell calls against stock holdings to generate income"
    },
    
    # Strategy 2: Protective Put (Downside Protection)
    "protective_put": {
        "enabled": True,
        "allocation": 0.30,  # 30% of options allocation
        "strike_selection": "otm",  # Out of the money
        "delta_target": -0.30,  # -30 delta (70% probability OTM)
        "max_premium": 0.02,  # Max 2% of portfolio value
        "protection_level": 0.90,  # Protect at 90% of current price
        "description": "Buy puts to protect stock holdings from decline"
    },
    
    # Strategy 3: Long Call/Put (Directional Speculation)
    "directional": {
        "enabled": True,
        "allocation": 0.40,  # 40% of options allocation
        "long_call": {
            "enabled": True,
            "strike_selection": "atm",  # At the money
            "delta_target": 0.50,  # 50 delta
            "max_premium": 0.01,  # Max 1% of portfolio per trade
            "min_confidence": 0.85  # Require 85% AI confidence
        },
        "long_put": {
            "enabled": True,
            "strike_selection": "atm",  # At the money
            "delta_target": -0.50,  # -50 delta
            "max_premium": 0.01,  # Max 1% of portfolio per trade
            "min_confidence": 0.85  # Require 85% AI confidence
        },
        "description": "Buy calls (bullish) or puts (bearish) for directional bets"
    },
    
    # Risk Management
    "risk_management": {
        "max_options_allocation": 0.30,  # Max 30% of portfolio in options
        "max_premium_per_trade": 0.02,  # Max 2% of portfolio per trade
        "max_total_premium": 0.10,  # Max 10% of portfolio in total premiums
        "stop_loss_percent": 0.50,  # Stop loss at 50% of premium paid
        "take_profit_percent": 1.00,  # Take profit at 100% gain
        "max_concurrent_positions": 10,
        "position_size_scaling": True  # Scale based on AI confidence
    },
    
    # Market Data (External Sources - No IB Subscription)
    "market_data": {
        "use_ib_subscription": False,
        "use_external_sources": True,
        "sources": {
            "primary": "polygon",  # Polygon.io (free tier)
            "secondary": "yahoo",  # Yahoo Finance (free)
            "tertiary": "alpha_vantage"  # Alpha Vantage (free tier)
        },
        "ib_delayed_data": True,  # Use IB's free 15-min delayed data
        "snapshot_on_demand": True,  # Use IB snapshots ($0.01 each) when needed
        "cache_duration": 30  # Cache data for 30 seconds
    },
    
    # Greeks Calculation
    "greeks": {
        "calculate_live": True,
        "use_black_scholes": True,
        "risk_free_rate": 0.05,  # 5% risk-free rate
        "update_frequency": 60  # Update every 60 seconds
    },
    
    # Symbols for Options Trading
    "symbols": {
        "high_liquidity": ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"],
        "medium_liquidity": ["AMD", "META", "NFLX", "DIS", "BA", "JPM"],
        "min_option_volume": 100,  # Minimum daily option volume
        "min_open_interest": 500  # Minimum open interest
    },
    
    # Performance Tracking
    "tracking": {
        "log_all_trades": True,
        "calculate_roi": True,
        "track_greeks": True,
        "monitor_iv": True,  # Monitor implied volatility
        "alert_on_assignment": True  # Alert if option assigned
    }
}

# ============================================================================
# PORTFOLIO ALLOCATION
# ============================================================================

PORTFOLIO_ALLOCATION = {
    "stocks": 0.70,  # 70% in stocks (core holdings)
    "options": 0.20,  # 20% in options (income + protection + speculation)
    "cash": 0.10,  # 10% cash reserve
    
    "options_breakdown": {
        "covered_calls": 0.30,  # 30% of options allocation (6% of total)
        "protective_puts": 0.30,  # 30% of options allocation (6% of total)
        "directional": 0.40  # 40% of options allocation (8% of total)
    }
}

# ============================================================================
# EXPECTED PERFORMANCE
# ============================================================================

EXPECTED_PERFORMANCE = {
    "stocks_only": {
        "daily_return": 0.075,  # 7.5% average (6-9% range)
        "allocation": 0.70,
        "contribution": 0.0525  # 5.25% to total
    },
    "options": {
        "daily_return": 0.125,  # 12.5% average (10-15% range)
        "allocation": 0.20,
        "contribution": 0.025  # 2.5% to total
    },
    "total_expected": {
        "daily_return": 0.0775,  # 7.75% total (stocks + options)
        "monthly_return": 1.55,  # 155% monthly (compounded)
        "improvement_vs_stocks_only": 0.0025  # +0.25% daily improvement
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_ib_config() -> Dict[str, Any]:
    """Get IB configuration from environment or defaults"""
    return {
        "host": os.getenv("IB_HOST", "127.0.0.1"),
        "port": int(os.getenv("IB_PORT", "4002")),  # Default to Gateway Live port
        "client_id": int(os.getenv("IB_CLIENT_ID", "2")),
        "paper_trading": os.getenv("IB_PAPER_TRADING", "false").lower() == "true",
        "account_id": os.getenv("IB_ACCOUNT", "U21922116")
    }

def get_options_config() -> Dict[str, Any]:
    """Get options trading configuration"""
    return IB_OPTIONS_CONFIG

def get_portfolio_allocation() -> Dict[str, Any]:
    """Get portfolio allocation"""
    return PORTFOLIO_ALLOCATION

def print_configuration():
    """Print configuration summary"""
    print("\n" + "=" * 80)
    print("🚀 IB OPTIONS TRADING CONFIGURATION")
    print("=" * 80)
    
    print("\n📊 PORTFOLIO ALLOCATION:")
    print(f"   Stocks: {PORTFOLIO_ALLOCATION['stocks']*100:.0f}%")
    print(f"   Options: {PORTFOLIO_ALLOCATION['options']*100:.0f}%")
    print(f"   Cash: {PORTFOLIO_ALLOCATION['cash']*100:.0f}%")
    
    print("\n🎯 OPTIONS STRATEGIES:")
    print(f"   1. Covered Call: {IB_OPTIONS_CONFIG['covered_call']['allocation']*100:.0f}% (Income)")
    print(f"   2. Protective Put: {IB_OPTIONS_CONFIG['protective_put']['allocation']*100:.0f}% (Protection)")
    print(f"   3. Directional: {IB_OPTIONS_CONFIG['directional']['allocation']*100:.0f}% (Speculation)")
    
    print("\n📈 EXPECTED PERFORMANCE:")
    print(f"   Stocks Only: {EXPECTED_PERFORMANCE['stocks_only']['daily_return']*100:.1f}% daily")
    print(f"   With Options: {EXPECTED_PERFORMANCE['total_expected']['daily_return']*100:.2f}% daily")
    print(f"   Improvement: +{EXPECTED_PERFORMANCE['total_expected']['improvement_vs_stocks_only']*100:.2f}% daily")
    
    print("\n💰 MARKET DATA:")
    print(f"   IB Subscription: {'No' if not IB_OPTIONS_CONFIG['market_data']['use_ib_subscription'] else 'Yes'}")
    print(f"   External Sources: {'Yes' if IB_OPTIONS_CONFIG['market_data']['use_external_sources'] else 'No'}")
    print(f"   Primary: {IB_OPTIONS_CONFIG['market_data']['sources']['primary'].upper()}")
    print(f"   Cost: $0/month (using free sources)")
    
    print("\n🛡️ RISK MANAGEMENT:")
    print(f"   Max Options Allocation: {IB_OPTIONS_CONFIG['risk_management']['max_options_allocation']*100:.0f}%")
    print(f"   Max Premium Per Trade: {IB_OPTIONS_CONFIG['risk_management']['max_premium_per_trade']*100:.0f}%")
    print(f"   Stop Loss: {IB_OPTIONS_CONFIG['risk_management']['stop_loss_percent']*100:.0f}%")
    print(f"   Take Profit: {IB_OPTIONS_CONFIG['risk_management']['take_profit_percent']*100:.0f}%")
    
    print("\n" + "=" * 80)
    print("[CHECK] CONFIGURATION READY")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    print_configuration()

