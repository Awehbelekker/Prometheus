"""
📊 USER PAPER TRADING API
User-facing endpoints for paper trading sessions and gamification
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json
import sqlite3

try:
    from core.dual_tier_permission_system import dual_tier_system, TradingPermission
except ImportError:
    from ..core.dual_tier_permission_system import dual_tier_system, TradingPermission
try:
    from core.enhanced_paper_trading_system import enhanced_paper_trading, SessionType, SessionStatus
except ImportError:
    from ..core.enhanced_paper_trading_system import enhanced_paper_trading, SessionType, SessionStatus
try:
    from core.gamification_engine import gamification_engine
except ImportError:
    from ..core.gamification_engine import gamification_engine

logger = logging.getLogger(__name__)

# Create router
user_router = APIRouter(prefix="/api/user", tags=["user"])

# Request models
class CreateSessionRequest(BaseModel):
    session_type: str  # '24_hour', '48_hour', '168_hour', 'custom'
    starting_capital: float
    custom_hours: Optional[int] = None

class PlaceTradeRequest(BaseModel):
    session_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    trade_type: str = 'market'  # 'market', 'limit', 'stop'
    limit_price: Optional[float] = None

# Response models
class SessionResponse(BaseModel):
    session_id: str
    session_type: str
    starting_capital: float
    current_value: float
    duration_hours: int
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    trades_count: int
    profit_loss: float
    return_percentage: float
    time_remaining_hours: Optional[float]

class UserDashboardResponse(BaseModel):
    user_id: str
    tier: str
    paper_trading_enabled: bool
    live_trading_enabled: bool
    current_level: int
    experience_points: int
    total_achievements: int
    active_sessions: List[SessionResponse]
    recent_achievements: List[Dict[str, Any]]
    leaderboard_rank: Optional[int]

# Dependency to get current user
async def get_current_user(request: Request) -> str:
    """Get current user ID from request"""
    # In a real implementation, this would decode JWT tokens, check sessions, etc.
    user_id = request.headers.get("X-User-ID")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Verify user exists
    user_perms = dual_tier_system.get_user_permissions(user_id)
    if not user_perms:
        # Create paper-only user if doesn't exist
        dual_tier_system.create_paper_only_user(user_id)
    
    return user_id

@user_router.get("/sessions")
async def get_user_sessions(user_id: str = Depends(get_current_user)):
    """Get all paper trading sessions for the current user"""
    try:
        sessions = []

        # Get all sessions for the user
        with sqlite3.connect(enhanced_paper_trading.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM paper_sessions
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))

            for row in cursor.fetchall():
                session_data = {
                    "session_id": row['session_id'],
                    "user_id": row['user_id'],
                    "session_type": row['session_type'],
                    "starting_capital": row['starting_capital'],
                    "current_value": row['current_value'],
                    "duration_hours": row['duration_hours'],
                    "status": row['status'],
                    "start_time": row['start_time'],
                    "end_time": row['end_time'],
                    "trades_count": row['trades_count'],
                    "profit_loss": row['profit_loss'],
                    "return_percentage": row['return_percentage'],
                    "max_drawdown": row['max_drawdown'],
                    "win_rate": row['win_rate'],
                    "total_volume": row.get('total_volume', 0)
                }

                # Calculate time remaining if active
                if row['status'] == 'active' and row['end_time']:
                    end_time = datetime.fromisoformat(row['end_time'])
                    time_remaining = (end_time - datetime.now()).total_seconds() / 3600
                    session_data['time_remaining_hours'] = max(0, time_remaining)

                sessions.append(session_data)

        return {
            "success": True,
            "sessions": sessions,
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s['status'] == 'active']),
            "completed_sessions": len([s for s in sessions if s['status'] == 'completed'])
        }

    except Exception as e:
        logger.error(f"Failed to get user sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.get("/dashboard", response_model=UserDashboardResponse)
async def get_user_dashboard(user_id: str = Depends(get_current_user)):
    """Get user dashboard with sessions, achievements, and progress"""
    try:
        # Get user permissions
        user_perms = dual_tier_system.get_user_permissions(user_id)
        if not user_perms:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user progress
        user_progress = gamification_engine.get_user_progress(user_id)
        
        # Get active sessions
        active_sessions = []
        try:
            with sqlite3.connect(enhanced_paper_trading.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM paper_sessions 
                    WHERE user_id = ? AND status IN ('not_started', 'active', 'paused')
                    ORDER BY created_at DESC
                """, (user_id,))
                
                for row in cursor.fetchall():
                    session_data = SessionResponse(
                        session_id=row['session_id'],
                        session_type=row['session_type'],
                        starting_capital=row['starting_capital'],
                        current_value=row['current_value'],
                        duration_hours=row['duration_hours'],
                        status=row['status'],
                        start_time=row['start_time'],
                        end_time=row['end_time'],
                        trades_count=row['trades_count'],
                        profit_loss=row['profit_loss'],
                        return_percentage=row['return_percentage'],
                        time_remaining_hours=None
                    )
                    
                    # Calculate time remaining if active
                    if row['status'] == 'active' and row['end_time']:
                        end_time = datetime.fromisoformat(row['end_time'])
                        time_remaining = (end_time - datetime.now()).total_seconds() / 3600
                        session_data.time_remaining_hours = max(0, time_remaining)
                    
                    active_sessions.append(session_data)
        except:
            pass  # Sessions are optional
        
        # Get recent achievements
        recent_achievements = []
        try:
            with sqlite3.connect(gamification_engine.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT ua.*, a.name, a.description, a.icon, a.points
                    FROM user_achievements ua
                    JOIN achievements a ON ua.achievement_id = a.achievement_id
                    WHERE ua.user_id = ?
                    ORDER BY ua.earned_at DESC
                    LIMIT 5
                """, (user_id,))
                
                recent_achievements = [
                    {
                        "achievement_id": row['achievement_id'],
                        "name": row['name'],
                        "description": row['description'],
                        "icon": row['icon'],
                        "points": row['points'],
                        "earned_at": row['earned_at']
                    }
                    for row in cursor.fetchall()
                ]
        except:
            pass  # Achievements are optional
        
        return UserDashboardResponse(
            user_id=user_id,
            tier=user_perms.tier.value,
            paper_trading_enabled=user_perms.paper_trading_enabled,
            live_trading_enabled=user_perms.live_trading_enabled,
            current_level=user_progress.level if user_progress else 1,
            experience_points=user_progress.experience_points if user_progress else 0,
            total_achievements=user_progress.total_achievements if user_progress else 0,
            active_sessions=active_sessions,
            recent_achievements=recent_achievements,
            leaderboard_rank=None  # TODO: Calculate from leaderboard
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.post("/create-session")
async def create_paper_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_current_user)
):
    """Create a new paper trading session"""
    try:
        # Validate session type
        try:
            session_type = SessionType(request.session_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid session type")
        
        # Validate starting capital
        if request.starting_capital <= 0:
            raise HTTPException(status_code=400, detail="Starting capital must be positive")
        
        if request.starting_capital > 1000000:  # $1M limit for paper trading
            raise HTTPException(status_code=400, detail="Starting capital too high")
        
        # Create session
        session_id = await enhanced_paper_trading.create_paper_session(
            user_id=user_id,
            session_type=session_type,
            starting_capital=request.starting_capital,
            custom_hours=request.custom_hours
        )
        
        if not session_id:
            raise HTTPException(status_code=400, detail="Failed to create session")
        
        return {
            "success": True,
            "session_id": session_id,
            "message": f"Paper trading session created successfully",
            "session_details": {
                "session_type": request.session_type,
                "starting_capital": request.starting_capital,
                "duration_hours": request.custom_hours if session_type == SessionType.CUSTOM else {
                    SessionType.QUICK_24H: 24,
                    SessionType.EXTENDED_48H: 48,
                    SessionType.FULL_WEEK: 168
                }.get(session_type, 24)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.post("/start-session/{session_id}")
async def start_paper_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Start a paper trading session"""
    try:
        # Verify session belongs to user
        session = await enhanced_paper_trading.get_session(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        success = await enhanced_paper_trading.start_session(session_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start session")
        
        return {
            "success": True,
            "message": "Session started successfully",
            "session_id": session_id,
            "start_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.get("/session/{session_id}")
async def get_session_details(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """Get detailed session information"""
    try:
        session = await enhanced_paper_trading.get_session(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get session trades
        trades = []
        try:
            with sqlite3.connect(enhanced_paper_trading.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM paper_trades 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC
                """, (session_id,))
                
                trades = [
                    {
                        "trade_id": row['trade_id'],
                        "symbol": row['symbol'],
                        "side": row['side'],
                        "quantity": row['quantity'],
                        "price": row['price'],
                        "timestamp": row['timestamp'],
                        "trade_type": row['trade_type'],
                        "profit_loss": row['profit_loss']
                    }
                    for row in cursor.fetchall()
                ]
        except:
            pass
        
        # Calculate time remaining
        time_remaining_hours = None
        if session.status == SessionStatus.ACTIVE and session.end_time:
            time_remaining = (session.end_time - datetime.now()).total_seconds() / 3600
            time_remaining_hours = max(0, time_remaining)
        
        return {
            "session": {
                "session_id": session.session_id,
                "session_type": session.session_type.value,
                "starting_capital": session.starting_capital,
                "current_value": session.current_value,
                "duration_hours": session.duration_hours,
                "status": session.status.value,
                "start_time": session.start_time.isoformat() if session.start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "trades_count": session.trades_count,
                "profit_loss": session.profit_loss,
                "return_percentage": session.return_percentage,
                "max_drawdown": session.max_drawdown,
                "win_rate": session.win_rate,
                "time_remaining_hours": time_remaining_hours,
                "positions": session.positions
            },
            "trades": trades
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.get("/market-data")
async def get_market_data(user_id: str = Depends(get_current_user)):
    """Get current market data for supported symbols"""
    try:
        market_data = []
        
        for symbol, data in enhanced_paper_trading.market_data_cache.items():
            market_data.append({
                "symbol": data.symbol,
                "price": data.price,
                "bid": data.bid,
                "ask": data.ask,
                "volume": data.volume,
                "change": data.change,
                "change_percent": data.change_percent,
                "timestamp": data.timestamp.isoformat()
            })
        
        return {
            "market_data": market_data,
            "supported_symbols": enhanced_paper_trading.supported_symbols,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get market data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@user_router.get("/achievements")
async def get_user_achievements(user_id: str = Depends(get_current_user)):
    """Get user's achievements and progress"""
    try:
        # Get user progress
        user_progress = gamification_engine.get_user_progress(user_id)
        
        # Get all achievements
        all_achievements = []
        user_achievement_ids = set()
        
        try:
            with sqlite3.connect(gamification_engine.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Get user's earned achievements
                cursor = conn.execute("""
                    SELECT achievement_id FROM user_achievements WHERE user_id = ?
                """, (user_id,))
                user_achievement_ids = {row['achievement_id'] for row in cursor.fetchall()}
                
                # Get all available achievements
                cursor = conn.execute("SELECT * FROM achievements ORDER BY points ASC")
                for row in cursor.fetchall():
                    all_achievements.append({
                        "achievement_id": row['achievement_id'],
                        "name": row['name'],
                        "description": row['description'],
                        "achievement_type": row['achievement_type'],
                        "rarity": row['rarity'],
                        "icon": row['icon'],
                        "points": row['points'],
                        "earned": row['achievement_id'] in user_achievement_ids
                    })
        except:
            pass
        
        return {
            "user_progress": {
                "level": user_progress.level if user_progress else 1,
                "experience_points": user_progress.experience_points if user_progress else 0,
                "total_achievements": user_progress.total_achievements if user_progress else 0,
                "skill_ratings": user_progress.skill_ratings if user_progress else {}
            },
            "achievements": all_achievements
        }
        
    except Exception as e:
        logger.error(f"Failed to get achievements: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
