#!/usr/bin/env python3
"""
Enhanced Account Management for Alpaca Trading
Based on comprehensive Alpaca account documentation

This module provides full account object implementation matching the official
Alpaca API documentation with all account properties and status enums.
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
from decimal import Decimal

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import alpaca_trade_api as tradeapi
    from alpaca_trade_api.rest import APIError
except ImportError:
    print("[ERROR] alpaca-trade-api not installed")
    sys.exit(1)


class AccountStatus(Enum):
    """Account status enumeration from Alpaca documentation"""
    ONBOARDING = "ONBOARDING"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    SUBMITTED = "SUBMITTED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"


class CryptoStatus(Enum):
    """Crypto enablement status enumeration"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    DISABLED = "DISABLED"


@dataclass
class AccountInfo:
    """
    Complete Alpaca Account Object
    Based on official Alpaca API documentation
    """
    # Basic Account Information
    id: str
    account_number: str
    status: str
    crypto_status: str
    currency: str = "USD"
    created_at: str = ""
    
    # Financial Information
    cash: str = "0"
    portfolio_value: str = "0"  # Deprecated but included for compatibility
    equity: str = "0"
    last_equity: str = "0"
    buying_power: str = "0"
    non_marginable_buying_power: str = "0"
    daytrading_buying_power: str = "0"
    regt_buying_power: str = "0"
    
    # Market Values
    long_market_value: str = "0"
    short_market_value: str = "0"
    
    # Margin Information
    multiplier: str = "1"
    initial_margin: str = "0"
    maintenance_margin: str = "0"
    last_maintenance_margin: str = "0"
    sma: str = "0"
    
    # Fees and Transfers
    accrued_fees: str = "0"
    pending_transfer_in: str = "0"
    pending_transfer_out: str = "0"
    
    # Trading Flags and Restrictions
    pattern_day_trader: bool = False
    daytrade_count: int = 0
    trade_suspended_by_user: bool = False
    trading_blocked: bool = False
    transfers_blocked: bool = False
    account_blocked: bool = False
    shorting_enabled: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return asdict(self)
    
    def get_buying_power_explanation(self) -> str:
        """Explain buying power calculation based on multiplier"""
        multiplier_int = int(self.multiplier)
        
        if multiplier_int == 4:
            return (
                "PDT account with 4x intraday BP and 2x reg T overnight BP. "
                "Daytrade buying power = (last_equity - last_maintenance_margin) * 4"
            )
        elif multiplier_int == 2:
            return (
                "Reg T margin account with 2x intraday and overnight BP. "
                "Buying power = max(equity - initial_margin, 0) * 2"
            )
        else:
            return (
                "Standard limited margin account with 1x BP. "
                "Buying power = cash"
            )
    
    def get_account_classification(self) -> str:
        """Get account classification based on multiplier"""
        multiplier_int = int(self.multiplier)
        
        if multiplier_int == 4:
            return "Pattern Day Trader (PDT)"
        elif multiplier_int == 2:
            return "Reg T Margin Account"
        else:
            return "Limited Margin Account"
    
    def is_trading_allowed(self) -> bool:
        """Check if trading is allowed on this account"""
        return (
            not self.account_blocked and
            not self.trading_blocked and
            not self.trade_suspended_by_user and
            self.status == AccountStatus.ACTIVE.value
        )
    
    def get_restrictions(self) -> List[str]:
        """Get list of current account restrictions"""
        restrictions = []
        
        if self.account_blocked:
            restrictions.append("Account activity prohibited")
        if self.trading_blocked:
            restrictions.append("Trading blocked")
        if self.transfers_blocked:
            restrictions.append("Transfers blocked")
        if self.trade_suspended_by_user:
            restrictions.append("Trading suspended by user")
        if self.pattern_day_trader:
            restrictions.append("Pattern Day Trader restrictions apply")
        if not self.shorting_enabled:
            restrictions.append("Short selling not enabled")
        
        return restrictions


class EnhancedAccountManager:
    """Enhanced Account Manager with full Alpaca API compatibility"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api = None
        self._setup_alpaca_connection()
    
    def _setup_alpaca_connection(self):
        """Setup Alpaca API connection"""
        try:
            # Get API credentials from environment
            paper_key = os.getenv('ALPACA_PAPER_KEY')
            paper_secret = os.getenv('ALPACA_PAPER_SECRET')
            
            if not paper_key or not paper_secret:
                raise ValueError("Alpaca API credentials not found in environment")
            
            # Initialize Alpaca API (paper trading)
            self.api = tradeapi.REST(
                paper_key,
                paper_secret,
                base_url='https://paper-api.alpaca.markets',
                api_version='v2'
            )
            
            # Test connection
            account = self.api.get_account()
            self.logger.info(f"[CHECK] Connected to Alpaca - Account: {account.account_number}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to connect to Alpaca: {e}")
            raise
    
    def get_comprehensive_account_info(self) -> AccountInfo:
        """Get comprehensive account information matching Alpaca documentation"""
        try:
            account = self.api.get_account()
            
            # Create comprehensive account info object
            account_info = AccountInfo(
                # Basic Information
                id=account.id,
                account_number=account.account_number,
                status=account.status,
                crypto_status=getattr(account, 'crypto_status', 'INACTIVE'),
                currency=getattr(account, 'currency', 'USD'),
                created_at=getattr(account, 'created_at', ''),
                
                # Financial Information
                cash=str(account.cash),
                portfolio_value=str(account.portfolio_value),
                equity=str(account.equity),
                last_equity=str(getattr(account, 'last_equity', account.equity)),
                buying_power=str(account.buying_power),
                non_marginable_buying_power=str(getattr(account, 'non_marginable_buying_power', '0')),
                daytrading_buying_power=str(getattr(account, 'daytrading_buying_power', account.buying_power)),
                regt_buying_power=str(getattr(account, 'regt_buying_power', account.buying_power)),
                
                # Market Values
                long_market_value=str(account.long_market_value),
                short_market_value=str(account.short_market_value),
                
                # Margin Information
                multiplier=str(getattr(account, 'multiplier', '1')),
                initial_margin=str(getattr(account, 'initial_margin', '0')),
                maintenance_margin=str(getattr(account, 'maintenance_margin', '0')),
                last_maintenance_margin=str(getattr(account, 'last_maintenance_margin', '0')),
                sma=str(account.sma) if account.sma else "0",
                
                # Fees and Transfers
                accrued_fees=str(getattr(account, 'accrued_fees', '0')),
                pending_transfer_in=str(getattr(account, 'pending_transfer_in', '0')),
                pending_transfer_out=str(getattr(account, 'pending_transfer_out', '0')),
                
                # Trading Flags
                pattern_day_trader=getattr(account, 'pattern_day_trader', False),
                daytrade_count=getattr(account, 'daytrade_count', 0),
                trade_suspended_by_user=getattr(account, 'trade_suspended_by_user', False),
                trading_blocked=getattr(account, 'trading_blocked', False),
                transfers_blocked=getattr(account, 'transfers_blocked', False),
                account_blocked=getattr(account, 'account_blocked', False),
                shorting_enabled=getattr(account, 'shorting_enabled', False)
            )
            
            self.logger.info(f"[CHECK] Retrieved comprehensive account info for {account_info.account_number}")
            return account_info
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to get account info: {e}")
            raise
    
    def get_account_analysis(self) -> Dict[str, Any]:
        """Get detailed account analysis with explanations"""
        try:
            account_info = self.get_comprehensive_account_info()
            
            analysis = {
                "basic_info": {
                    "account_id": account_info.id,
                    "account_number": account_info.account_number,
                    "status": account_info.status,
                    "crypto_status": account_info.crypto_status,
                    "classification": account_info.get_account_classification(),
                    "created_at": account_info.created_at
                },
                "financial_summary": {
                    "equity": float(account_info.equity),
                    "cash": float(account_info.cash),
                    "buying_power": float(account_info.buying_power),
                    "buying_power_explanation": account_info.get_buying_power_explanation(),
                    "portfolio_value": float(account_info.portfolio_value),
                    "long_market_value": float(account_info.long_market_value),
                    "short_market_value": float(account_info.short_market_value)
                },
                "margin_details": {
                    "multiplier": int(account_info.multiplier),
                    "initial_margin": float(account_info.initial_margin),
                    "maintenance_margin": float(account_info.maintenance_margin),
                    "daytrading_buying_power": float(account_info.daytrading_buying_power),
                    "regt_buying_power": float(account_info.regt_buying_power),
                    "non_marginable_buying_power": float(account_info.non_marginable_buying_power)
                },
                "trading_status": {
                    "trading_allowed": account_info.is_trading_allowed(),
                    "pattern_day_trader": account_info.pattern_day_trader,
                    "daytrade_count": account_info.daytrade_count,
                    "shorting_enabled": account_info.shorting_enabled,
                    "restrictions": account_info.get_restrictions()
                },
                "transfers_and_fees": {
                    "pending_transfer_in": float(account_info.pending_transfer_in),
                    "pending_transfer_out": float(account_info.pending_transfer_out),
                    "accrued_fees": float(account_info.accrued_fees)
                },
                "flags": {
                    "account_blocked": account_info.account_blocked,
                    "trading_blocked": account_info.trading_blocked,
                    "transfers_blocked": account_info.transfers_blocked,
                    "trade_suspended_by_user": account_info.trade_suspended_by_user
                }
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to generate account analysis: {e}")
            raise
    
    def validate_account_for_trading(self) -> Dict[str, Any]:
        """Validate account readiness for trading operations"""
        try:
            account_info = self.get_comprehensive_account_info()
            
            validation_result = {
                "valid": account_info.is_trading_allowed(),
                "account_status": account_info.status,
                "restrictions": account_info.get_restrictions(),
                "cash_available": float(account_info.cash),
                "buying_power": float(account_info.buying_power),
                "can_day_trade": account_info.pattern_day_trader,
                "can_short": account_info.shorting_enabled,
                "recommendations": []
            }
            
            # Add recommendations based on account state
            if not validation_result["valid"]:
                if account_info.account_blocked:
                    validation_result["recommendations"].append("Contact Alpaca support - account blocked")
                if account_info.trading_blocked:
                    validation_result["recommendations"].append("Resolve trading restrictions")
                if account_info.trade_suspended_by_user:
                    validation_result["recommendations"].append("Enable trading in account settings")
            
            if float(account_info.cash) < 100:
                validation_result["recommendations"].append("Consider funding account for trading")
            
            if account_info.pattern_day_trader and account_info.daytrade_count >= 3:
                validation_result["recommendations"].append("Approaching day trade limit")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"[ERROR] Account validation failed: {e}")
            raise


def demo_enhanced_account_management():
    """Demonstrate enhanced account management capabilities"""
    print("🏦 ENHANCED ALPACA ACCOUNT MANAGEMENT DEMO")
    print("=" * 60)
    
    try:
        # Initialize account manager
        manager = EnhancedAccountManager()
        
        print("\n📊 COMPREHENSIVE ACCOUNT INFORMATION:")
        print("-" * 40)
        
        # Get comprehensive account info
        account_info = manager.get_comprehensive_account_info()
        
        # Display basic info
        print(f"Account ID: {account_info.id}")
        print(f"Account Number: {account_info.account_number}")
        print(f"Status: {account_info.status}")
        print(f"Classification: {account_info.get_account_classification()}")
        print(f"Crypto Status: {account_info.crypto_status}")
        
        print(f"\n💰 FINANCIAL OVERVIEW:")
        print(f"Equity: ${float(account_info.equity):,.2f}")
        print(f"Cash: ${float(account_info.cash):,.2f}")
        print(f"Buying Power: ${float(account_info.buying_power):,.2f}")
        print(f"Portfolio Value: ${float(account_info.portfolio_value):,.2f}")
        
        print(f"\n📈 MARKET POSITIONS:")
        print(f"Long Market Value: ${float(account_info.long_market_value):,.2f}")
        print(f"Short Market Value: ${float(account_info.short_market_value):,.2f}")
        
        print(f"\n⚖️ MARGIN INFORMATION:")
        print(f"Multiplier: {account_info.multiplier}x")
        print(f"Initial Margin: ${float(account_info.initial_margin):,.2f}")
        print(f"Maintenance Margin: ${float(account_info.maintenance_margin):,.2f}")
        print(f"Daytrading Buying Power: ${float(account_info.daytrading_buying_power):,.2f}")
        
        print(f"\n🚦 TRADING STATUS:")
        print(f"Trading Allowed: {'[CHECK]' if account_info.is_trading_allowed() else '[ERROR]'}")
        print(f"Pattern Day Trader: {'[CHECK]' if account_info.pattern_day_trader else '[ERROR]'}")
        print(f"Day Trade Count: {account_info.daytrade_count}/3")
        print(f"Shorting Enabled: {'[CHECK]' if account_info.shorting_enabled else '[ERROR]'}")
        
        # Show restrictions if any
        restrictions = account_info.get_restrictions()
        if restrictions:
            print(f"\n[WARNING]️ ACCOUNT RESTRICTIONS:")
            for restriction in restrictions:
                print(f"  • {restriction}")
        
        print(f"\n🔍 DETAILED ANALYSIS:")
        print("-" * 40)
        
        # Get detailed analysis
        analysis = manager.get_account_analysis()
        print(f"Buying Power Explanation:")
        print(f"  {analysis['financial_summary']['buying_power_explanation']}")
        
        print(f"\n[CHECK] TRADING VALIDATION:")
        print("-" * 40)
        
        # Validate account for trading
        validation = manager.validate_account_for_trading()
        print(f"Account Valid for Trading: {'[CHECK]' if validation['valid'] else '[ERROR]'}")
        print(f"Cash Available: ${validation['cash_available']:,.2f}")
        print(f"Buying Power: ${validation['buying_power']:,.2f}")
        
        if validation['recommendations']:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in validation['recommendations']:
                print(f"  • {rec}")
        
        print(f"\n📄 FULL ACCOUNT OBJECT (JSON):")
        print("-" * 40)
        print(json.dumps(account_info.to_dict(), indent=2, default=str))
        
        print(f"\n[CHECK] Enhanced account management demo completed successfully!")
        
    except Exception as e:
        print(f"[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    demo_enhanced_account_management()
