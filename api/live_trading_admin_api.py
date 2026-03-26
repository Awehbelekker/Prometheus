#!/usr/bin/env python3
"""
💰 PROMETHEUS LIVE TRADING ADMIN API
Admin controls for activating live trading with real money

UPDATED: Now uses real database (prometheus_trading.db) instead of mock data
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import asyncio
import sqlite3
import os

logger = logging.getLogger(__name__)

# Create router
live_trading_admin_router = APIRouter(prefix="/api/admin", tags=["Live Trading Admin"])

# Database path - use prometheus_trading.db which has the proper schema
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prometheus_trading.db")

# Pydantic models
class ActivateLiveTradingRequest(BaseModel):
    userId: str
    investmentAmount: float

class DeactivateLiveTradingRequest(BaseModel):
    userId: str

class LiveTradingStats(BaseModel):
    users: List[Dict[str, Any]]
    poolStats: Dict[str, Any]


def get_db_connection():
    """Get database connection with row factory for dict-like access"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_users_from_db() -> Dict[str, Dict[str, Any]]:
    """Fetch all users from the real database"""
    users_dict = {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Join users with capital_accounts and user_performance for complete data
        cursor.execute("""
            SELECT
                u.id, u.email, u.name, u.role, u.status, u.created_at,
                COALESCE(ca.starting_capital, 0) as investmentAmount,
                COALESCE(ca.current_equity, 0) as currentValue,
                COALESCE(ca.current_equity - ca.starting_capital, 0) as pnl,
                CASE WHEN ca.starting_capital > 0
                     THEN ((ca.current_equity - ca.starting_capital) / ca.starting_capital * 100)
                     ELSE 0 END as pnlPercentage,
                ca.status as trading_status
            FROM users u
            LEFT JOIN capital_accounts ca ON u.id = ca.user_id
        """)

        rows = cursor.fetchall()
        for row in rows:
            user_id = row['id']
            # Determine tier based on investment amount
            investment = float(row['investmentAmount'] or 0)
            if investment >= 100000:
                tier = "platinum"
            elif investment >= 50000:
                tier = "gold"
            elif investment >= 10000:
                tier = "silver"
            else:
                tier = "bronze"

            # Determine trading status
            trading_status = row['trading_status'] or row['status'] or 'paper_trading'
            if trading_status == 'active':
                trading_status = 'live_trading_active'
            elif trading_status not in ['live_trading_active', 'paper_trading']:
                trading_status = 'paper_trading'

            users_dict[user_id] = {
                "id": user_id,
                "name": row['name'] or f"User {user_id[:8]}",
                "email": row['email'] or "",
                "investmentAmount": investment,
                "currentValue": float(row['currentValue'] or 0),
                "pnl": float(row['pnl'] or 0),
                "pnlPercentage": float(row['pnlPercentage'] or 0),
                "status": trading_status,
                "tier": tier,
                "joinDate": row['created_at'] or datetime.now().isoformat(),
                "lastActivity": datetime.now().isoformat()
            }

        conn.close()

        # If no users in database, return empty dict (no mock data)
        if not users_dict:
            logger.info("No users found in database - returning empty user list")

        return users_dict

    except Exception as e:
        logger.error(f"Error fetching users from database: {e}")
        return {}


def update_user_status_in_db(user_id: str, status: str, investment_amount: float = None) -> bool:
    """Update user trading status in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Update capital_accounts status
        if investment_amount is not None:
            cursor.execute("""
                INSERT INTO capital_accounts (id, user_id, starting_capital, cash, current_equity, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    starting_capital = excluded.starting_capital,
                    cash = excluded.cash,
                    current_equity = excluded.current_equity,
                    status = excluded.status,
                    updated_at = excluded.updated_at
            """, (
                f"ca_{user_id}",
                user_id,
                investment_amount,
                investment_amount,
                investment_amount,
                'active' if status == 'live_trading_active' else 'paper',
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        else:
            cursor.execute("""
                UPDATE capital_accounts
                SET status = ?, updated_at = ?
                WHERE user_id = ?
            """, (
                'active' if status == 'live_trading_active' else 'paper',
                datetime.now().isoformat(),
                user_id
            ))

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"Error updating user status in database: {e}")
        return False

async def get_alpaca_account_info():
    """Get real Alpaca account information - NO MOCK FALLBACK"""
    try:
        # Import Alpaca trading service
        from ..core.alpaca_trading_service import AlpacaTradingService

        alpaca_service = AlpacaTradingService()
        account_info = alpaca_service.get_account_info()  # Sync method

        if "error" in account_info:
            raise Exception(account_info["error"])

        return {
            "account_value": float(account_info.get("portfolio_value", 0)),
            "buying_power": float(account_info.get("buying_power", 0)),
            "cash": float(account_info.get("cash", 0)),
            "positions_value": float(account_info.get("long_market_value", 0)),
            "connected": True
        }
    except Exception as e:
        logger.error(f"Failed to get Alpaca account info: {e}")
        # Return error state instead of mock data
        return {
            "account_value": 0,
            "buying_power": 0,
            "cash": 0,
            "positions_value": 0,
            "connected": False,
            "error": str(e)
        }


async def calculate_pool_stats():
    """Calculate live trading pool statistics from real database"""
    # Get users from real database
    users_db = get_users_from_db()

    total_capital = 0
    total_current_value = 0
    live_users = 0
    paper_users = 0

    for user in users_db.values():
        total_capital += user["investmentAmount"]
        total_current_value += user["currentValue"]

        if user["status"] == "live_trading_active":
            live_users += 1
        elif user["status"] == "paper_trading":
            paper_users += 1

    total_pnl = total_current_value - total_capital
    total_pnl_percentage = (total_pnl / total_capital * 100) if total_capital > 0 else 0

    # Get Alpaca account info
    alpaca_info = await get_alpaca_account_info()

    return {
        "totalCapital": total_capital,
        "totalAllocated": total_current_value,
        "availableCash": alpaca_info["cash"],
        "totalPnL": total_pnl,
        "totalPnLPercentage": total_pnl_percentage,
        "activeUsers": len(users_db),
        "liveUsers": live_users,
        "paperUsers": paper_users,
        "alpacaAccountValue": alpaca_info["account_value"],
        "alpacaBuyingPower": alpaca_info["buying_power"],
        "alpacaConnected": alpaca_info.get("connected", False)
    }


@live_trading_admin_router.get("/live-trading-stats")
async def get_live_trading_stats():
    """
    Get comprehensive live trading statistics for admin dashboard

    Returns user list, pool statistics, and Alpaca account information
    Uses REAL database data - no mock data
    """
    try:
        # Calculate pool statistics
        pool_stats = await calculate_pool_stats()

        # Get user list from real database
        users_db = get_users_from_db()
        users = list(users_db.values())

        return {
            "success": True,
            "users": users,
            "poolStats": pool_stats,
            "timestamp": datetime.now().isoformat(),
            "data_source": "real_database"
        }

    except Exception as e:
        logger.error(f"Failed to get live trading stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@live_trading_admin_router.post("/activate-live-trading")
async def activate_live_trading(request: ActivateLiveTradingRequest):
    """
    Activate live trading for a specific user

    This moves the user from paper trading to live trading with real money
    Uses REAL database - no mock data
    """
    try:
        user_id = request.userId
        investment_amount = request.investmentAmount

        # Get users from real database
        users_db = get_users_from_db()

        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")

        user = users_db[user_id]

        if user["status"] == "live_trading_active":
            raise HTTPException(status_code=400, detail="User already has live trading active")

        # Update user status in real database
        success = update_user_status_in_db(user_id, "live_trading_active", investment_amount)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user status in database")

        # Initialize AI trading for this user
        await initialize_ai_trading_for_user(user_id, investment_amount)

        # Log the activation
        logger.info(f"[CHECK] Live trading activated for user {user_id} with ${investment_amount:,.2f}")

        # Fetch updated user data
        updated_users = get_users_from_db()
        updated_user = updated_users.get(user_id, user)

        return {
            "success": True,
            "message": f"Live trading activated for {user['name']} with ${investment_amount:,.2f}",
            "user": updated_user,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate live trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@live_trading_admin_router.post("/deactivate-live-trading")
async def deactivate_live_trading(request: DeactivateLiveTradingRequest):
    """
    Deactivate live trading for a specific user

    This moves the user back to paper trading mode
    Uses REAL database - no mock data
    """
    try:
        user_id = request.userId

        # Get users from real database
        users_db = get_users_from_db()

        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")

        user = users_db[user_id]

        if user["status"] != "live_trading_active":
            raise HTTPException(status_code=400, detail="User does not have live trading active")

        # Update user status in real database
        success = update_user_status_in_db(user_id, "paper_trading")
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update user status in database")

        # Stop AI trading for this user
        await stop_ai_trading_for_user(user_id)

        # Log the deactivation
        logger.info(f"⏹️ Live trading deactivated for user {user_id}")

        # Fetch updated user data
        updated_users = get_users_from_db()
        updated_user = updated_users.get(user_id, user)

        return {
            "success": True,
            "message": f"Live trading deactivated for {user['name']}",
            "user": updated_user,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to deactivate live trading: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def initialize_ai_trading_for_user(user_id: str, investment_amount: float):
    """Initialize AI trading systems for a user's live allocation"""
    try:
        # Start AI trading engines for this user's allocation
        from ..core.ai_coordinator import get_ai_coordinator
        
        ai_coordinator = await get_ai_coordinator()
        
        # Configure AI trading for this user
        await ai_coordinator.configure_user_trading(
            user_id=user_id,
            allocation_amount=investment_amount,
            risk_tolerance="moderate",  # Could be user-specific
            trading_strategies=["revolutionary_engines", "ai_consciousness", "quantum_trading"]
        )
        
        logger.info(f"🤖 AI trading initialized for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI trading for user {user_id}: {e}")

async def stop_ai_trading_for_user(user_id: str):
    """Stop AI trading systems for a user"""
    try:
        from ..core.ai_coordinator import get_ai_coordinator
        
        ai_coordinator = await get_ai_coordinator()
        
        # Stop AI trading for this user
        await ai_coordinator.stop_user_trading(user_id)
        
        logger.info(f"⏹️ AI trading stopped for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to stop AI trading for user {user_id}: {e}")

@live_trading_admin_router.get("/alpaca-integration-status")
async def get_alpaca_integration_status():
    """
    Get Alpaca integration status and account information
    """
    try:
        alpaca_info = await get_alpaca_account_info()
        
        return {
            "success": True,
            "alpaca_status": "connected",
            "account_info": alpaca_info,
            "integration_health": "healthy",
            "last_sync": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get Alpaca status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@live_trading_admin_router.post("/emergency-stop-all")
async def emergency_stop_all_trading():
    """
    Emergency stop all live trading activities
    Uses REAL database - no mock data
    """
    try:
        stopped_users = []

        # Get users from real database
        users_db = get_users_from_db()

        for user_id, user in users_db.items():
            if user["status"] == "live_trading_active":
                # Stop AI trading
                await stop_ai_trading_for_user(user_id)

                # Update status in real database
                update_user_status_in_db(user_id, "paper_trading")
                stopped_users.append(user["name"])

        logger.warning(f"🚨 Emergency stop executed - stopped trading for {len(stopped_users)} users")

        return {
            "success": True,
            "message": f"Emergency stop executed - stopped trading for {len(stopped_users)} users",
            "stopped_users": stopped_users,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Emergency stop failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_user_performance_from_db(user_id: str) -> Dict[str, Any]:
    """Fetch user performance data from the real database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get daily PnL from user_performance table
        cursor.execute("""
            SELECT period_date, start_equity, end_equity, rtn_pct, max_drawdown, realized_pnl
            FROM user_performance
            WHERE user_id = ?
            ORDER BY period_date DESC
            LIMIT 30
        """, (user_id,))

        performance_rows = cursor.fetchall()

        # Get trades summary from trade_ledger
        cursor.execute("""
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl_realized > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl_realized < 0 THEN 1 ELSE 0 END) as losing_trades,
                AVG(CASE WHEN pnl_realized > 0 THEN pnl_realized ELSE NULL END) as avg_win,
                AVG(CASE WHEN pnl_realized < 0 THEN pnl_realized ELSE NULL END) as avg_loss
            FROM trade_ledger
            WHERE user_id = ?
        """, (user_id,))

        trades_row = cursor.fetchone()

        conn.close()

        # Build daily PnL list
        daily_pnl = []
        for row in performance_rows:
            pnl = float(row['end_equity'] or 0) - float(row['start_equity'] or 0)
            pnl_pct = float(row['rtn_pct'] or 0)
            daily_pnl.append({
                "date": row['period_date'],
                "pnl": pnl,
                "pnl_percentage": pnl_pct
            })

        # Build trades summary
        total_trades = int(trades_row['total_trades'] or 0)
        winning_trades = int(trades_row['winning_trades'] or 0)
        losing_trades = int(trades_row['losing_trades'] or 0)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        trades_summary = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 1),
            "avg_win": round(float(trades_row['avg_win'] or 0), 2),
            "avg_loss": round(float(trades_row['avg_loss'] or 0), 2)
        }

        return {
            "daily_pnl": daily_pnl,
            "trades_summary": trades_summary
        }

    except Exception as e:
        logger.error(f"Error fetching user performance from database: {e}")
        return {
            "daily_pnl": [],
            "trades_summary": {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0
            }
        }


@live_trading_admin_router.get("/user-performance/{user_id}")
async def get_user_performance(user_id: str):
    """
    Get detailed performance data for a specific user
    Uses REAL database - no mock data
    """
    try:
        # Get users from real database
        users_db = get_users_from_db()

        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")

        user = users_db[user_id]

        # Get performance data from real database
        perf_data = get_user_performance_from_db(user_id)

        performance_data = {
            "user_info": user,
            "daily_pnl": perf_data["daily_pnl"],
            "trades_summary": perf_data["trades_summary"],
            "ai_insights": [
                "Performance data sourced from real database",
                f"User tier: {user['tier']}",
                f"Current PnL: ${user['pnl']:,.2f} ({user['pnlPercentage']:.2f}%)"
            ],
            "data_source": "real_database"
        }

        return {
            "success": True,
            "performance": performance_data,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
