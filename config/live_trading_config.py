#!/usr/bin/env python3
"""
💰 PROMETHEUS LIVE TRADING CONFIGURATION
Complete setup for real money trading with safety controls
"""

import os
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TradingMode(Enum):
    """Trading mode options"""
    PAPER = "paper"
    LIVE_CONSERVATIVE = "live_conservative"
    LIVE_MODERATE = "live_moderate"
    LIVE_AGGRESSIVE = "live_aggressive"

class RiskLevel(Enum):
    """Risk level settings"""
    MINIMAL = "minimal"
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

@dataclass
class LiveTradingConfig:
    """
    Comprehensive live trading configuration
    Includes safety controls and risk management
    """
    
    # =============================================================================
    # TRADING MODE CONFIGURATION
    # =============================================================================
    trading_mode: TradingMode = TradingMode.LIVE
    risk_level: RiskLevel = RiskLevel.CONSERVATIVE
    
    # Alpaca Configuration
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    alpaca_base_url: str = "https://paper-api.alpaca.markets"  # Default to paper
    
    # Trading Controls
    enable_live_order_execution: bool = True
    live_trading_enabled: bool = True
    paper_trading_only: bool = False
    
    # =============================================================================
    # RISK MANAGEMENT SETTINGS
    # =============================================================================
    
    # Position Sizing
    max_position_size_percent: float = 1.0  # 1% of portfolio per position
    max_daily_trades: int = 10
    max_portfolio_risk_percent: float = 0.5  # 0.5% max portfolio risk
    
    # Stop Loss Settings
    default_stop_loss_percent: float = 2.0  # 2% stop loss
    emergency_stop_loss_percent: float = 5.0  # 5% emergency stop
    max_drawdown_percent: float = 10.0  # 10% max drawdown
    
    # Daily Limits
    max_daily_loss_dollars: float = 500.0  # $500 max daily loss
    max_daily_trades_per_symbol: int = 3
    
    # Portfolio Limits
    max_total_exposure_percent: float = 50.0  # 50% max exposure
    max_single_stock_percent: float = 5.0  # 5% max per stock
    
    # =============================================================================
    # SAFETY CONTROLS
    # =============================================================================
    
    # Circuit Breakers
    enable_circuit_breakers: bool = True
    circuit_breaker_loss_percent: float = 3.0  # Halt at 3% daily loss
    circuit_breaker_cooldown_minutes: int = 30
    
    # Market Hours
    trade_only_market_hours: bool = True
    avoid_first_15_minutes: bool = True  # Avoid market open volatility
    avoid_last_15_minutes: bool = True   # Avoid market close volatility
    
    # Volatility Controls
    max_symbol_volatility: float = 5.0  # Skip symbols with >5% daily volatility
    min_volume_threshold: int = 1000000  # Minimum daily volume
    
    # =============================================================================
    # MONITORING & ALERTS
    # =============================================================================
    
    # Real-time Monitoring
    enable_real_time_monitoring: bool = True
    monitoring_interval_seconds: int = 30
    
    # Alert Thresholds
    alert_on_loss_percent: float = 1.0  # Alert at 1% loss
    alert_on_unusual_volume: bool = True
    alert_on_system_errors: bool = True
    
    # Notification Settings
    email_alerts_enabled: bool = False
    slack_alerts_enabled: bool = False
    sms_alerts_enabled: bool = False
    
    # =============================================================================
    # TRADING STRATEGIES
    # =============================================================================
    
    # Enabled Engines
    enable_crypto_engine: bool = False  # Disabled for initial testing
    enable_options_engine: bool = False  # Disabled for initial testing
    enable_advanced_engine: bool = True
    enable_market_maker: bool = False  # Disabled for initial testing
    
    # Strategy Settings
    strategy_allocation: Dict[str, float] = field(default_factory=lambda: {
        "advanced_engine": 100.0,  # 100% allocation to advanced engine initially
        "crypto_engine": 0.0,
        "options_engine": 0.0,
        "market_maker": 0.0
    })
    
    # =============================================================================
    # SYMBOLS AND MARKETS
    # =============================================================================
    
    # Allowed Symbols (Conservative list for initial testing)
    allowed_symbols: List[str] = field(default_factory=lambda: [
        "SPY", "QQQ", "IWM",  # ETFs
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",  # Large cap stocks
        "NVDA", "META", "NFLX"  # Tech stocks
    ])
    
    # Forbidden Symbols (High risk)
    forbidden_symbols: List[str] = field(default_factory=lambda: [
        "SQQQ", "TQQQ", "UVXY", "VXX",  # Leveraged/volatility ETFs
        "SPXS", "SPXL", "TZA", "TNA"    # Leveraged ETFs
    ])
    
    # Market Sectors
    max_sector_exposure_percent: float = 20.0  # 20% max per sector
    
    # =============================================================================
    # TESTING AND VALIDATION
    # =============================================================================
    
    # Testing Mode
    testing_mode: bool = True
    test_duration_days: int = 30
    test_capital_dollars: float = 2000.0  # $2,000 for testing
    
    # Validation Settings
    require_manual_approval: bool = True  # Require manual approval for trades
    dry_run_mode: bool = True  # Log trades without executing
    
    # Performance Tracking
    track_performance_metrics: bool = True
    benchmark_symbol: str = "SPY"
    
    # =============================================================================
    # COMPLIANCE AND LOGGING
    # =============================================================================
    
    # Regulatory Compliance
    enable_trade_surveillance: bool = True
    enable_audit_logging: bool = True
    log_all_decisions: bool = True
    
    # Data Retention
    trade_data_retention_days: int = 2555  # 7 years
    log_retention_days: int = 365
    
    # Reporting
    generate_daily_reports: bool = True
    generate_weekly_reports: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
        self._apply_risk_level_settings()
        self._set_trading_mode_defaults()
    
    def _validate_config(self):
        """Validate configuration settings"""
        # Validate percentages
        if not 0 < self.max_position_size_percent <= 10:
            raise ValueError("max_position_size_percent must be between 0 and 10")
        
        if not 0 < self.max_portfolio_risk_percent <= 5:
            raise ValueError("max_portfolio_risk_percent must be between 0 and 5")
        
        # Validate stop losses
        if self.default_stop_loss_percent >= self.emergency_stop_loss_percent:
            raise ValueError("default_stop_loss_percent must be less than emergency_stop_loss_percent")
        
        # Validate API keys for live trading
        if self.live_trading_enabled and not (self.alpaca_api_key and self.alpaca_secret_key):
            raise ValueError("API keys required for live trading")
    
    def _apply_risk_level_settings(self):
        """Apply risk level specific settings"""
        if self.risk_level == RiskLevel.MINIMAL:
            self.max_position_size_percent = 0.5
            self.max_daily_trades = 5
            self.max_portfolio_risk_percent = 0.25
            self.default_stop_loss_percent = 1.5
            self.max_daily_loss_dollars = 200.0
            
        elif self.risk_level == RiskLevel.CONSERVATIVE:
            self.max_position_size_percent = 1.0
            self.max_daily_trades = 10
            self.max_portfolio_risk_percent = 0.5
            self.default_stop_loss_percent = 2.0
            self.max_daily_loss_dollars = 500.0
            
        elif self.risk_level == RiskLevel.MODERATE:
            self.max_position_size_percent = 2.0
            self.max_daily_trades = 20
            self.max_portfolio_risk_percent = 1.0
            self.default_stop_loss_percent = 2.5
            self.max_daily_loss_dollars = 1000.0
            
        elif self.risk_level == RiskLevel.AGGRESSIVE:
            self.max_position_size_percent = 5.0
            self.max_daily_trades = 50
            self.max_portfolio_risk_percent = 2.0
            self.default_stop_loss_percent = 3.0
            self.max_daily_loss_dollars = 2000.0
    
    def _set_trading_mode_defaults(self):
        """Set defaults based on trading mode"""
        if self.trading_mode == TradingMode.PAPER:
            self.alpaca_base_url = "https://paper-api.alpaca.markets"
            self.enable_live_order_execution = False
            self.live_trading_enabled = False
            self.paper_trading_only = True
            
        elif self.trading_mode == TradingMode.LIVE_CONSERVATIVE:
            self.alpaca_base_url = "https://api.alpaca.markets"
            self.enable_live_order_execution = True
            self.live_trading_enabled = True
            self.paper_trading_only = False
            self.risk_level = RiskLevel.CONSERVATIVE
            
        elif self.trading_mode == TradingMode.LIVE_MODERATE:
            self.alpaca_base_url = "https://api.alpaca.markets"
            self.enable_live_order_execution = True
            self.live_trading_enabled = True
            self.paper_trading_only = False
            self.risk_level = RiskLevel.MODERATE
            
        elif self.trading_mode == TradingMode.LIVE_AGGRESSIVE:
            self.alpaca_base_url = "https://api.alpaca.markets"
            self.enable_live_order_execution = True
            self.live_trading_enabled = True
            self.paper_trading_only = False
            self.risk_level = RiskLevel.AGGRESSIVE
    
    def to_env_vars(self) -> Dict[str, str]:
        """Convert configuration to environment variables"""
        return {
            # Trading Mode
            "TRADING_MODE": self.trading_mode.value,
            "RISK_LEVEL": self.risk_level.value,
            
            # Alpaca Configuration
            "ALPACA_API_KEY": self.alpaca_api_key,
            "ALPACA_SECRET_KEY": self.alpaca_secret_key,
            "ALPACA_BASE_URL": self.alpaca_base_url,
            
            # Trading Controls
            "ENABLE_LIVE_ORDER_EXECUTION": str(self.enable_live_order_execution).lower(),
            "LIVE_TRADING_ENABLED": str(self.live_trading_enabled).lower(),
            "PAPER_TRADING_ONLY": str(self.paper_trading_only).lower(),
            
            # Risk Management
            "MAX_POSITION_SIZE_PERCENT": str(self.max_position_size_percent),
            "MAX_DAILY_TRADES": str(self.max_daily_trades),
            "MAX_PORTFOLIO_RISK_PERCENT": str(self.max_portfolio_risk_percent),
            "DEFAULT_STOP_LOSS_PERCENT": str(self.default_stop_loss_percent),
            "EMERGENCY_STOP_LOSS_PERCENT": str(self.emergency_stop_loss_percent),
            "MAX_DRAWDOWN_PERCENT": str(self.max_drawdown_percent),
            
            # Safety Controls
            "ENABLE_CIRCUIT_BREAKERS": str(self.enable_circuit_breakers).lower(),
            "CIRCUIT_BREAKER_LOSS_PERCENT": str(self.circuit_breaker_loss_percent),
            "TRADE_ONLY_MARKET_HOURS": str(self.trade_only_market_hours).lower(),
            
            # Monitoring
            "ENABLE_REAL_TIME_MONITORING": str(self.enable_real_time_monitoring).lower(),
            "MONITORING_INTERVAL_SECONDS": str(self.monitoring_interval_seconds),
            
            # Strategies
            "ENABLE_CRYPTO_ENGINE": str(self.enable_crypto_engine).lower(),
            "ENABLE_OPTIONS_ENGINE": str(self.enable_options_engine).lower(),
            "ENABLE_ADVANCED_ENGINE": str(self.enable_advanced_engine).lower(),
            "ENABLE_MARKET_MAKER": str(self.enable_market_maker).lower(),
            
            # Testing
            "TESTING_MODE": str(self.testing_mode).lower(),
            "TEST_CAPITAL_DOLLARS": str(self.test_capital_dollars),
            "DRY_RUN_MODE": str(self.dry_run_mode).lower(),
            
            # Compliance
            "ENABLE_TRADE_SURVEILLANCE": str(self.enable_trade_surveillance).lower(),
            "ENABLE_AUDIT_LOGGING": str(self.enable_audit_logging).lower(),
        }
    
    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        config_dict = {
            "trading_mode": self.trading_mode.value,
            "risk_level": self.risk_level.value,
            "alpaca_base_url": self.alpaca_base_url,
            "enable_live_order_execution": self.enable_live_order_execution,
            "live_trading_enabled": self.live_trading_enabled,
            "max_position_size_percent": self.max_position_size_percent,
            "max_daily_trades": self.max_daily_trades,
            "max_portfolio_risk_percent": self.max_portfolio_risk_percent,
            "default_stop_loss_percent": self.default_stop_loss_percent,
            "allowed_symbols": self.allowed_symbols,
            "forbidden_symbols": self.forbidden_symbols,
            "testing_mode": self.testing_mode,
            "test_capital_dollars": self.test_capital_dollars
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Live trading configuration saved to: {filepath}")
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'LiveTradingConfig':
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        
        # Convert string enums back to enum objects
        if 'trading_mode' in config_dict:
            config_dict['trading_mode'] = TradingMode(config_dict['trading_mode'])
        if 'risk_level' in config_dict:
            config_dict['risk_level'] = RiskLevel(config_dict['risk_level'])
        
        return cls(**config_dict)

# =============================================================================
# PREDEFINED CONFIGURATIONS
# =============================================================================

def get_paper_trading_config() -> LiveTradingConfig:
    """Get safe paper trading configuration"""
    return LiveTradingConfig(
        trading_mode=TradingMode.PAPER,
        risk_level=RiskLevel.CONSERVATIVE
    )

def get_live_conservative_config() -> LiveTradingConfig:
    """Get conservative live trading configuration"""
    return LiveTradingConfig(
        trading_mode=TradingMode.LIVE_CONSERVATIVE,
        risk_level=RiskLevel.CONSERVATIVE,
        test_capital_dollars=2000.0,
        max_daily_loss_dollars=200.0
    )

def get_live_moderate_config() -> LiveTradingConfig:
    """Get moderate live trading configuration"""
    return LiveTradingConfig(
        trading_mode=TradingMode.LIVE_MODERATE,
        risk_level=RiskLevel.MODERATE,
        test_capital_dollars=5000.0,
        max_daily_loss_dollars=500.0
    )

def get_testing_config() -> LiveTradingConfig:
    """Get configuration for initial live testing"""
    return LiveTradingConfig(
        trading_mode=TradingMode.LIVE_CONSERVATIVE,
        risk_level=RiskLevel.MINIMAL,
        testing_mode=True,
        dry_run_mode=True,
        require_manual_approval=True,
        test_capital_dollars=1000.0,
        max_daily_loss_dollars=100.0,
        max_position_size_percent=0.5,
        max_daily_trades=5
    )
