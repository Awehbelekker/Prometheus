"""
💰 ADMIN FUND ALLOCATION API
Admin-only endpoints for fund allocation and live trading activation
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json
import sqlite3

try:
    from core.dual_tier_permission_system import dual_tier_system, UserTier, TradingPermission
except ImportError:
    from ..core.dual_tier_permission_system import dual_tier_system, UserTier, TradingPermission
try:
    from core.gamification_engine import gamification_engine
except ImportError:
    from ..core.gamification_engine import gamification_engine

logger = logging.getLogger(__name__)

# Create router
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# Request models
class FundAllocationRequest(BaseModel):
    user_id: str
    amount: float
    reason: str = ""

class LiveTradingActivationRequest(BaseModel):
    user_id: str
    reason: str = ""

class UserPermissionUpdateRequest(BaseModel):
    user_id: str
    tier: str
    permissions: List[str]
    max_allocation: Optional[float] = None

# Response models
class AdminDashboardResponse(BaseModel):
    total_users: int
    paper_only_users: int
    live_approved_users: int
    total_allocated_funds: float
    active_sessions: int
    recent_allocations: List[Dict[str, Any]]

class UserSummaryResponse(BaseModel):
    user_id: str
    tier: str
    paper_trading_enabled: bool
    live_trading_enabled: bool
    allocated_funds: float
    total_trades: int
    total_profit_loss: float
    achievements_count: int
    current_level: int

# Dependency to verify admin access
async def verify_admin_access(request: Request) -> str:
    """Verify that the requesting user is an admin"""
    # In a real implementation, this would check JWT tokens, sessions, etc.
    # For now, we'll use a simple header-based approach
    admin_id = request.headers.get("X-Admin-ID")
    
    if not admin_id:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    
    if not dual_tier_system.is_admin(admin_id):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return admin_id

@admin_router.get("/dashboard", response_model=AdminDashboardResponse)
async def get_admin_dashboard(admin_id: str = Depends(verify_admin_access)):
    """Get admin dashboard overview"""
    try:
        # Get user statistics
        with sqlite3.connect(dual_tier_system.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Count users by tier
            cursor = conn.execute("""
                SELECT tier, COUNT(*) as count 
                FROM user_permissions 
                GROUP BY tier
            """)
            tier_counts = {row['tier']: row['count'] for row in cursor.fetchall()}
            
            # Get total allocated funds
            cursor = conn.execute("""
                SELECT SUM(allocated_funds) as total 
                FROM user_permissions 
                WHERE allocated_funds > 0
            """)
            total_allocated = cursor.fetchone()['total'] or 0.0
            
            # Get recent allocations
            cursor = conn.execute("""
                SELECT fa.*, up.tier 
                FROM fund_allocations fa
                JOIN user_permissions up ON fa.user_id = up.user_id
                ORDER BY fa.allocated_at DESC 
                LIMIT 10
            """)
            recent_allocations = [
                {
                    "allocation_id": row['allocation_id'],
                    "user_id": row['user_id'],
                    "amount": row['amount'],
                    "allocation_type": row['allocation_type'],
                    "reason": row['reason'],
                    "allocated_at": row['allocated_at'],
                    "user_tier": row['tier']
                }
                for row in cursor.fetchall()
            ]
        
        return AdminDashboardResponse(
            total_users=sum(tier_counts.values()),
            paper_only_users=tier_counts.get(UserTier.PAPER_ONLY.value, 0),
            live_approved_users=tier_counts.get(UserTier.LIVE_APPROVED.value, 0),
            total_allocated_funds=total_allocated,
            active_sessions=0,  # TODO: Get from enhanced paper trading system
            recent_allocations=recent_allocations
        )
        
    except Exception as e:
        logger.error(f"Failed to get admin dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to load dashboard")

@admin_router.get("/users", response_model=List[UserSummaryResponse])
async def get_all_users(admin_id: str = Depends(verify_admin_access)):
    """Get all users summary for admin"""
    try:
        users = []
        
        with sqlite3.connect(dual_tier_system.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT up.*, 
                       COALESCE(prog.total_trades, 0) as total_trades,
                       COALESCE(prog.total_profit_loss, 0.0) as total_profit_loss,
                       COALESCE(prog.total_achievements, 0) as achievements_count,
                       COALESCE(prog.level, 1) as current_level
                FROM user_permissions up
                LEFT JOIN user_progress prog ON up.user_id = prog.user_id
                ORDER BY up.created_at DESC
            """)
            
            for row in cursor.fetchall():
                users.append(UserSummaryResponse(
                    user_id=row['user_id'],
                    tier=row['tier'],
                    paper_trading_enabled=bool(row['paper_trading_enabled']),
                    live_trading_enabled=bool(row['live_trading_enabled']),
                    allocated_funds=float(row['allocated_funds']),
                    total_trades=row['total_trades'],
                    total_profit_loss=float(row['total_profit_loss']),
                    achievements_count=row['achievements_count'],
                    current_level=row['current_level']
                ))
        
        return users
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(status_code=500, detail="Failed to load users")

@admin_router.post("/allocate-funds")
async def allocate_funds(
    request: FundAllocationRequest,
    admin_id: str = Depends(verify_admin_access)
):
    """Allocate funds to a user"""
    try:
        if request.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        success = dual_tier_system.allocate_funds(
            user_id=request.user_id,
            admin_id=admin_id,
            amount=request.amount,
            reason=request.reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to allocate funds")
        
        return {
            "success": True,
            "message": f"${request.amount:,.2f} allocated to user {request.user_id}",
            "allocation_details": {
                "user_id": request.user_id,
                "amount": request.amount,
                "admin_id": admin_id,
                "reason": request.reason,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to allocate funds: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@admin_router.post("/activate-live-trading")
async def activate_live_trading(
    request: LiveTradingActivationRequest,
    admin_id: str = Depends(verify_admin_access)
):
    """Activate live trading for a user"""
    try:
        success = dual_tier_system.activate_live_trading(
            user_id=request.user_id,
            admin_id=admin_id
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to activate live trading")
        
        return {
            "success": True,
            "message": f"Live trading activated for user {request.user_id}",
            "activation_details": {
                "user_id": request.user_id,
                "admin_id": admin_id,
                "reason": request.reason,
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate live trading: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@admin_router.get("/user/{user_id}/details")
async def get_user_details(
    user_id: str,
    admin_id: str = Depends(verify_admin_access)
):
    """Get detailed user information"""
    try:
        # Get user permissions
        user_perms = dual_tier_system.get_user_permissions(user_id)
        if not user_perms:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user progress
        user_progress = gamification_engine.get_user_progress(user_id)
        
        # Get user allocations
        allocations = dual_tier_system.get_user_allocations(user_id)
        
        # Get user achievements
        user_achievements = []
        try:
            with sqlite3.connect(gamification_engine.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT ua.*, a.name, a.description, a.icon, a.points
                    FROM user_achievements ua
                    JOIN achievements a ON ua.achievement_id = a.achievement_id
                    WHERE ua.user_id = ?
                    ORDER BY ua.earned_at DESC
                """, (user_id,))
                
                user_achievements = [
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
        
        return {
            "user_permissions": {
                "user_id": user_perms.user_id,
                "tier": user_perms.tier.value,
                "paper_trading_enabled": user_perms.paper_trading_enabled,
                "live_trading_enabled": user_perms.live_trading_enabled,
                "allocated_funds": user_perms.allocated_funds,
                "max_allocation": user_perms.max_allocation,
                "permissions": [p.value for p in user_perms.permissions],
                "created_at": user_perms.created_at.isoformat() if user_perms.created_at else None
            },
            "user_progress": {
                "level": user_progress.level if user_progress else 1,
                "experience_points": user_progress.experience_points if user_progress else 0,
                "total_achievements": user_progress.total_achievements if user_progress else 0,
                "trading_sessions": user_progress.trading_sessions if user_progress else 0,
                "total_trades": user_progress.total_trades if user_progress else 0,
                "total_profit_loss": user_progress.total_profit_loss if user_progress else 0.0,
                "skill_ratings": user_progress.skill_ratings if user_progress else {}
            },
            "fund_allocations": [
                {
                    "allocation_id": alloc.allocation_id,
                    "amount": alloc.amount,
                    "allocation_type": alloc.allocation_type,
                    "reason": alloc.reason,
                    "allocated_at": alloc.allocated_at.isoformat(),
                    "status": alloc.status
                }
                for alloc in allocations
            ],
            "achievements": user_achievements
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@admin_router.get("/audit-log")
async def get_audit_log(
    limit: int = 100,
    admin_id: str = Depends(verify_admin_access)
):
    """Get permission audit log"""
    try:
        with sqlite3.connect(dual_tier_system.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM permission_audit_log 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            audit_entries = [
                {
                    "log_id": row['log_id'],
                    "user_id": row['user_id'],
                    "admin_id": row['admin_id'],
                    "action": row['action'],
                    "details": json.loads(row['details']) if row['details'] else {},
                    "timestamp": row['timestamp']
                }
                for row in cursor.fetchall()
            ]
        
        return {"audit_log": audit_entries}
        
    except Exception as e:
        logger.error(f"Failed to get audit log: {e}")
        raise HTTPException(status_code=500, detail="Failed to load audit log")
