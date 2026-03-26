#!/usr/bin/env python3
"""
Enhanced Account API Endpoints for Alpaca Trading
Comprehensive account management based on official Alpaca documentation
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from enum import Enum

# Import our enhanced account manager
from enhanced_account_management import EnhancedAccountManager, AccountStatus, CryptoStatus


# Pydantic models for API responses
class AccountStatusEnum(str, Enum):
    """Account status enumeration for API"""
    ONBOARDING = "ONBOARDING"
    SUBMISSION_FAILED = "SUBMISSION_FAILED"
    SUBMITTED = "SUBMITTED"
    ACCOUNT_UPDATED = "ACCOUNT_UPDATED"
    APPROVAL_PENDING = "APPROVAL_PENDING"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"


class CryptoStatusEnum(str, Enum):
    """Crypto status enumeration for API"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    PENDING = "PENDING"
    DISABLED = "DISABLED"


class AccountBasicInfo(BaseModel):
    """Basic account information response"""
    account_id: str
    account_number: str
    status: AccountStatusEnum
    crypto_status: CryptoStatusEnum
    classification: str
    created_at: str


class FinancialSummary(BaseModel):
    """Financial summary response"""
    equity: float = Field(..., description="Total account equity")
    cash: float = Field(..., description="Available cash")
    buying_power: float = Field(..., description="Current buying power")
    buying_power_explanation: str = Field(..., description="Explanation of buying power calculation")
    portfolio_value: float = Field(..., description="Total portfolio value")
    long_market_value: float = Field(..., description="Long positions market value")
    short_market_value: float = Field(..., description="Short positions market value")


class MarginDetails(BaseModel):
    """Margin account details"""
    multiplier: int = Field(..., description="Buying power multiplier")
    initial_margin: float = Field(..., description="Initial margin requirement")
    maintenance_margin: float = Field(..., description="Maintenance margin requirement")
    daytrading_buying_power: float = Field(..., description="Day trading buying power")
    regt_buying_power: float = Field(..., description="Regulation T buying power")
    non_marginable_buying_power: float = Field(..., description="Non-marginable buying power")


class TradingStatus(BaseModel):
    """Trading status and restrictions"""
    trading_allowed: bool
    pattern_day_trader: bool
    daytrade_count: int
    shorting_enabled: bool
    restrictions: list[str]


class TransfersAndFees(BaseModel):
    """Transfers and fees information"""
    pending_transfer_in: float
    pending_transfer_out: float
    accrued_fees: float


class AccountFlags(BaseModel):
    """Account flags and restrictions"""
    account_blocked: bool
    trading_blocked: bool
    transfers_blocked: bool
    trade_suspended_by_user: bool


class ComprehensiveAccountResponse(BaseModel):
    """Comprehensive account analysis response"""
    basic_info: AccountBasicInfo
    financial_summary: FinancialSummary
    margin_details: MarginDetails
    trading_status: TradingStatus
    transfers_and_fees: TransfersAndFees
    flags: AccountFlags


class AccountValidationResponse(BaseModel):
    """Account validation response"""
    valid: bool
    account_status: str
    restrictions: list[str]
    cash_available: float
    buying_power: float
    can_day_trade: bool
    can_short: bool
    recommendations: list[str]


class FullAccountObject(BaseModel):
    """Complete Alpaca account object"""
    # Basic Information
    id: str
    account_number: str
    status: str
    crypto_status: str
    currency: str = "USD"
    created_at: str
    
    # Financial Information
    cash: str
    portfolio_value: str
    equity: str
    last_equity: str
    buying_power: str
    non_marginable_buying_power: str
    daytrading_buying_power: str
    regt_buying_power: str
    
    # Market Values
    long_market_value: str
    short_market_value: str
    
    # Margin Information
    multiplier: str
    initial_margin: str
    maintenance_margin: str
    last_maintenance_margin: str
    sma: str
    
    # Fees and Transfers
    accrued_fees: str
    pending_transfer_in: str
    pending_transfer_out: str
    
    # Trading Flags
    pattern_day_trader: bool
    daytrade_count: int
    trade_suspended_by_user: bool
    trading_blocked: bool
    transfers_blocked: bool
    account_blocked: bool
    shorting_enabled: bool


# Initialize router
router = APIRouter(prefix="/api/account", tags=["Enhanced Account Management"])

# Global account manager instance
account_manager = None


def get_account_manager() -> EnhancedAccountManager:
    """Dependency to get account manager instance"""
    global account_manager
    if account_manager is None:
        account_manager = EnhancedAccountManager()
    return account_manager


@router.get("/info", response_model=ComprehensiveAccountResponse)
async def get_comprehensive_account_info(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """
    Get comprehensive account information with detailed analysis
    
    Returns complete account information including:
    - Basic account details
    - Financial summary
    - Margin information
    - Trading status and restrictions
    - Transfer and fee information
    """
    try:
        analysis = manager.get_account_analysis()
        
        return ComprehensiveAccountResponse(
            basic_info=AccountBasicInfo(**analysis["basic_info"]),
            financial_summary=FinancialSummary(**analysis["financial_summary"]),
            margin_details=MarginDetails(**analysis["margin_details"]),
            trading_status=TradingStatus(**analysis["trading_status"]),
            transfers_and_fees=TransfersAndFees(**analysis["transfers_and_fees"]),
            flags=AccountFlags(**analysis["flags"])
        )
        
    except Exception as e:
        logging.error(f"Failed to get account info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve account information: {str(e)}")


@router.get("/basic", response_model=AccountBasicInfo)
async def get_basic_account_info(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """Get basic account information"""
    try:
        analysis = manager.get_account_analysis()
        return AccountBasicInfo(**analysis["basic_info"])
        
    except Exception as e:
        logging.error(f"Failed to get basic account info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve basic account information: {str(e)}")


@router.get("/financial", response_model=FinancialSummary)
async def get_financial_summary(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """Get account financial summary"""
    try:
        analysis = manager.get_account_analysis()
        return FinancialSummary(**analysis["financial_summary"])
        
    except Exception as e:
        logging.error(f"Failed to get financial summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve financial summary: {str(e)}")


@router.get("/margin", response_model=MarginDetails)
async def get_margin_details(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """Get margin account details and buying power information"""
    try:
        analysis = manager.get_account_analysis()
        return MarginDetails(**analysis["margin_details"])
        
    except Exception as e:
        logging.error(f"Failed to get margin details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve margin details: {str(e)}")


@router.get("/trading-status", response_model=TradingStatus)
async def get_trading_status(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """Get trading status and restrictions"""
    try:
        analysis = manager.get_account_analysis()
        return TradingStatus(**analysis["trading_status"])
        
    except Exception as e:
        logging.error(f"Failed to get trading status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trading status: {str(e)}")


@router.get("/validate", response_model=AccountValidationResponse)
async def validate_account_for_trading(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """
    Validate account readiness for trading operations
    
    Checks account status, restrictions, and provides recommendations
    for optimal trading configuration.
    """
    try:
        validation = manager.validate_account_for_trading()
        return AccountValidationResponse(**validation)
        
    except Exception as e:
        logging.error(f"Failed to validate account: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate account: {str(e)}")


@router.get("/full", response_model=FullAccountObject)
async def get_full_account_object(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """
    Get complete Alpaca account object
    
    Returns the full account object exactly as defined in Alpaca documentation
    with all properties and values.
    """
    try:
        account_info = manager.get_comprehensive_account_info()
        return FullAccountObject(**account_info.to_dict())
        
    except Exception as e:
        logging.error(f"Failed to get full account object: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve full account object: {str(e)}")


@router.get("/status-definitions")
async def get_status_definitions():
    """
    Get definitions of account and crypto status values
    
    Returns explanations of all possible status values as defined
    in the Alpaca documentation.
    """
    return {
        "account_statuses": {
            "ONBOARDING": "The account is onboarding.",
            "SUBMISSION_FAILED": "The account application submission failed for some reason.",
            "SUBMITTED": "The account application has been submitted for review.",
            "ACCOUNT_UPDATED": "The account information is being updated.",
            "APPROVAL_PENDING": "The final account approval is pending.",
            "ACTIVE": "The account is active for trading.",
            "REJECTED": "The account application has been rejected."
        },
        "crypto_statuses": {
            "ACTIVE": "Crypto trading is enabled and active.",
            "INACTIVE": "Crypto trading is not enabled.",
            "PENDING": "Crypto enablement is pending approval.",
            "DISABLED": "Crypto trading has been disabled."
        },
        "multiplier_explanations": {
            "1": "Standard limited margin account with 1x BP (buying_power = cash)",
            "2": "Reg T margin account with 2x intraday and overnight BP (default for non-PDT accounts with $2,000+ equity)",
            "4": "PDT account with 4x intraday BP and 2x reg T overnight BP"
        }
    }


@router.get("/buying-power-calculator")
async def calculate_buying_power_details(manager: EnhancedAccountManager = Depends(get_account_manager)):
    """
    Get detailed buying power calculation breakdown
    
    Explains how buying power is calculated based on account type,
    equity, and margin requirements.
    """
    try:
        account_info = manager.get_comprehensive_account_info()
        analysis = manager.get_account_analysis()
        
        multiplier = int(account_info.multiplier)
        equity = float(account_info.equity)
        cash = float(account_info.cash)
        initial_margin = float(account_info.initial_margin)
        maintenance_margin = float(account_info.maintenance_margin)
        last_equity = float(account_info.last_equity)
        last_maintenance_margin = float(account_info.last_maintenance_margin)
        
        calculation_details = {
            "account_type": account_info.get_account_classification(),
            "multiplier": multiplier,
            "current_values": {
                "equity": equity,
                "cash": cash,
                "initial_margin": initial_margin,
                "maintenance_margin": maintenance_margin,
                "last_equity": last_equity,
                "last_maintenance_margin": last_maintenance_margin
            },
            "buying_power_types": {
                "current_buying_power": float(account_info.buying_power),
                "daytrading_buying_power": float(account_info.daytrading_buying_power),
                "regt_buying_power": float(account_info.regt_buying_power),
                "non_marginable_buying_power": float(account_info.non_marginable_buying_power)
            },
            "calculation_explanation": analysis["financial_summary"]["buying_power_explanation"]
        }
        
        # Add specific calculations based on multiplier
        if multiplier == 4:
            pdt_calculation = (last_equity - last_maintenance_margin) * 4
            calculation_details["pdt_calculation"] = {
                "formula": "(last_equity - last_maintenance_margin) * 4",
                "last_equity": last_equity,
                "last_maintenance_margin": last_maintenance_margin,
                "calculated_daytrading_bp": pdt_calculation
            }
        elif multiplier == 2:
            reg_t_calculation = max(equity - initial_margin, 0) * 2
            calculation_details["reg_t_calculation"] = {
                "formula": "max(equity - initial_margin, 0) * 2",
                "equity": equity,
                "initial_margin": initial_margin,
                "calculated_buying_power": reg_t_calculation
            }
        else:
            calculation_details["limited_margin_calculation"] = {
                "formula": "buying_power = cash",
                "cash": cash
            }
        
        return calculation_details
        
    except Exception as e:
        logging.error(f"Failed to calculate buying power details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate buying power details: {str(e)}")


# Additional utility endpoints
@router.get("/health")
async def account_health_check():
    """Health check for account management endpoints"""
    try:
        manager = get_account_manager()
        account_info = manager.get_comprehensive_account_info()
        
        return {
            "status": "healthy",
            "account_connected": True,
            "account_number": account_info.account_number,
            "account_status": account_info.status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logging.error(f"Account health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Account service unavailable: {str(e)}")


# Export router for integration with main server
__all__ = ["router"]
