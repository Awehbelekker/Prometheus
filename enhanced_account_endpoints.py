#!/usr/bin/env python3
"""
🏦 Enhanced Account API Endpoints
Based on Alpaca API Documentation

New endpoints to add to the server:
1. /api/trading/alpaca/account/detailed - Enhanced account info
2. /api/trading/alpaca/account/trading-status - Trading eligibility check
3. /api/trading/alpaca/account/daily-pnl - Daily profit/loss analysis
4. /api/trading/alpaca/account/restrictions - Account restrictions summary
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any
import logging
from datetime import datetime

# This would be added to unified_production_server.py

def create_enhanced_account_endpoints():
    """
    Enhanced account endpoints following Alpaca documentation patterns
    """
    
    @app.get("/api/trading/alpaca/account/detailed")
    async def get_detailed_account_info(
        use_paper: bool = Query(not ALWAYS_LIVE, description="Use paper trading (true) or live trading (false)"),
        current_user: dict = Depends(get_current_user)
    ):
        """
        🏦 Get detailed Alpaca account information with analysis
        
        Based on Alpaca documentation examples:
        - Check trading restrictions
        - Calculate buying power
        - Analyze account status
        """
        try:
            alpaca_service = get_alpaca_service(use_paper=use_paper)
            
            if not alpaca_service.is_available():
                raise HTTPException(status_code=503, detail="Alpaca trading service not available")
            
            account_info = alpaca_service.get_account_info()
            
            if "error" in account_info:
                raise HTTPException(status_code=400, detail=account_info["error"])
            
            # Enhanced analysis based on Alpaca docs
            current_equity = float(account_info.get('equity', 0))
            last_equity = float(account_info.get('last_equity', 0))
            balance_change = current_equity - last_equity
            percentage_change = ((balance_change / last_equity) * 100) if last_equity > 0 else 0
            
            # Trading eligibility check (from docs)
            trading_blocked = account_info.get('trading_blocked', True)
            account_status = account_info.get('status', 'Unknown')
            buying_power = float(account_info.get('buying_power', 0))
            
            eligible_for_trading = (
                not trading_blocked and 
                account_status == 'ACTIVE' and 
                buying_power > 0
            )
            
            # Portfolio composition
            portfolio_value = float(account_info.get('portfolio_value', 0))
            cash = float(account_info.get('cash', 0))
            invested_amount = portfolio_value - cash
            
            return {
                "success": True,
                "account": account_info,
                "analysis": {
                    "daily_pnl": {
                        "current_equity": current_equity,
                        "last_equity": last_equity,
                        "balance_change": balance_change,
                        "percentage_change": percentage_change,
                        "status": "profit" if balance_change > 0 else "loss" if balance_change < 0 else "flat"
                    },
                    "trading_eligibility": {
                        "eligible": eligible_for_trading,
                        "restrictions": {
                            "trading_blocked": trading_blocked,
                            "account_status": account_status,
                            "has_buying_power": buying_power > 0,
                            "pattern_day_trader": account_info.get('pattern_day_trader', False)
                        }
                    },
                    "portfolio_composition": {
                        "total_value": portfolio_value,
                        "cash": cash,
                        "cash_percentage": (cash / portfolio_value * 100) if portfolio_value > 0 else 0,
                        "invested": invested_amount,
                        "invested_percentage": (invested_amount / portfolio_value * 100) if portfolio_value > 0 else 0
                    },
                    "key_messages": {
                        "trading_status": "Account is currently restricted from trading." if trading_blocked else "Account is free to trade",
                        "buying_power_message": f"${buying_power:,.2f} is available as buying power.",
                        "daily_change_message": f"Today's portfolio balance change: ${balance_change:+,.2f}"
                    }
                },
                "trading_mode": "paper" if use_paper else "live",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "user_id": current_user.get('user_id')
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Detailed account info failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/trading/alpaca/account/trading-status")
    async def get_trading_status(
        use_paper: bool = Query(not ALWAYS_LIVE, description="Use paper trading (true) or live trading (false)"),
        current_user: dict = Depends(get_current_user)
    ):
        """
        🔍 Check trading eligibility and restrictions
        
        Returns comprehensive trading status based on account restrictions
        """
        try:
            alpaca_service = get_alpaca_service(use_paper=use_paper)
            
            if not alpaca_service.is_available():
                raise HTTPException(status_code=503, detail="Alpaca trading service not available")
            
            account_info = alpaca_service.get_account_info()
            
            if "error" in account_info:
                raise HTTPException(status_code=400, detail=account_info["error"])
            
            # Check trading eligibility (from Alpaca docs)
            trading_blocked = account_info.get('trading_blocked', True)
            transfers_blocked = account_info.get('transfers_blocked', False)
            account_blocked = account_info.get('account_blocked', False)
            account_status = account_info.get('status', 'Unknown')
            buying_power = float(account_info.get('buying_power', 0))
            pattern_day_trader = account_info.get('pattern_day_trader', False)
            day_trade_count = account_info.get('day_trade_count', 0)
            
            # Overall eligibility
            eligible = (
                not trading_blocked and 
                not account_blocked and
                account_status == 'ACTIVE' and 
                buying_power > 0
            )
            
            # Compile restrictions
            restrictions = []
            if trading_blocked:
                restrictions.append("Trading is blocked")
            if transfers_blocked:
                restrictions.append("Transfers are blocked")
            if account_blocked:
                restrictions.append("Account is blocked")
            if account_status != 'ACTIVE':
                restrictions.append(f"Account status is {account_status}")
            if buying_power <= 0:
                restrictions.append("No buying power available")
            
            return {
                "success": True,
                "trading_eligible": eligible,
                "account_status": account_status,
                "restrictions": restrictions,
                "details": {
                    "trading_blocked": trading_blocked,
                    "transfers_blocked": transfers_blocked,
                    "account_blocked": account_blocked,
                    "pattern_day_trader": pattern_day_trader,
                    "day_trade_count": day_trade_count,
                    "buying_power": buying_power
                },
                "warnings": [
                    "Pattern Day Trader rules apply" if pattern_day_trader else None,
                    f"Day trade count: {day_trade_count}/3" if day_trade_count > 0 and not pattern_day_trader else None
                ],
                "trading_mode": "paper" if use_paper else "live",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Trading status check failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/trading/alpaca/account/daily-pnl")
    async def get_daily_pnl(
        use_paper: bool = Query(not ALWAYS_LIVE, description="Use paper trading (true) or live trading (false)"),
        current_user: dict = Depends(get_current_user)
    ):
        """
        📈 Get daily profit/loss analysis
        
        Based on Alpaca documentation example for calculating daily P&L
        """
        try:
            alpaca_service = get_alpaca_service(use_paper=use_paper)
            
            if not alpaca_service.is_available():
                raise HTTPException(status_code=503, detail="Alpaca trading service not available")
            
            account_info = alpaca_service.get_account_info()
            
            if "error" in account_info:
                raise HTTPException(status_code=400, detail=account_info["error"])
            
            # Calculate daily P&L (from Alpaca docs)
            current_equity = float(account_info.get('equity', 0))
            last_equity = float(account_info.get('last_equity', 0))
            balance_change = current_equity - last_equity
            
            # Calculate percentage change
            percentage_change = 0
            if last_equity > 0:
                percentage_change = (balance_change / last_equity) * 100
            
            # Determine status
            status = "flat"
            if balance_change > 0:
                status = "profit"
            elif balance_change < 0:
                status = "loss"
            
            # Additional metrics
            portfolio_value = float(account_info.get('portfolio_value', 0))
            unrealized_pl = float(account_info.get('long_market_value', 0)) - float(account_info.get('cost_basis', 0)) if 'cost_basis' in account_info else 0
            
            return {
                "success": True,
                "daily_pnl": {
                    "current_equity": current_equity,
                    "last_equity": last_equity,
                    "balance_change": balance_change,
                    "percentage_change": percentage_change,
                    "status": status,
                    "portfolio_value": portfolio_value
                },
                "message": f"Today's portfolio balance change: ${balance_change:+,.2f}",
                "analysis": {
                    "trend": "📈 Up" if balance_change > 0 else "📉 Down" if balance_change < 0 else "➡️ Flat",
                    "significant": abs(percentage_change) > 1.0,
                    "performance_rating": (
                        "Excellent" if percentage_change > 5 else
                        "Good" if percentage_change > 2 else
                        "Fair" if percentage_change > 0 else
                        "Poor" if percentage_change > -2 else
                        "Very Poor"
                    )
                },
                "trading_mode": "paper" if use_paper else "live",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Daily P&L calculation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "detailed_account": get_detailed_account_info,
        "trading_status": get_trading_status, 
        "daily_pnl": get_daily_pnl
    }

# This code would be integrated into unified_production_server.py
"""
To add these endpoints to the server:

1. Copy the endpoint functions into unified_production_server.py
2. Add them after the existing account endpoint
3. Restart the server to activate the new endpoints
"""
