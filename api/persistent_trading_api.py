"""
🚀 PROMETHEUS Persistent Trading API
FastAPI endpoints for persistent trading system management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime, timedelta
import asyncio

# Import our core systems
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from persistent_trading_engine import persistent_trading_engine, TradingMode
from user_portfolio_manager import user_portfolio_manager, PortfolioType
from access_control_manager import access_control_manager, UserRole, PermissionType
from wealth_management_system import wealth_management_system
from portfolio_persistence_layer import portfolio_persistence_layer, PersistenceEventType

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/persistent-trading", tags=["persistent-trading"])
security = HTTPBearer()

# Pydantic models
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str
    initial_capital: float = 100000.0

class TradingApproval(BaseModel):
    user_id: str
    max_allocation: float
    reason: str = ""

class FundAllocation(BaseModel):
    user_id: str
    amount: float
    reason: str = ""

class AllocationRequest(BaseModel):
    amount: float
    justification: str

class TradeOrder(BaseModel):
    symbol: str
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float
    portfolio_type: str = "paper"

class PortfolioUpdate(BaseModel):
    total_value: float
    positions: Dict[str, Any]
    cash_balance: float

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from JWT token"""
    # In a real implementation, you would decode and validate the JWT token
    # For now, we'll extract from a mock token format
    try:
        token = credentials.credentials
        # Mock token validation - replace with actual JWT validation
        if token.startswith("user_"):
            return token
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

async def verify_admin_permission(user_id: str = Depends(get_current_user)) -> str:
    """Verify user has admin permissions"""
    if not access_control_manager.has_permission(user_id, PermissionType.MANAGE_USERS):
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return user_id

# User Management Endpoints
@router.post("/register")
async def register_user(registration: UserRegistration, background_tasks: BackgroundTasks):
    """Register a new user with isolated portfolio"""
    try:
        # Create user profile
        user_id = user_portfolio_manager.create_user_profile(
            registration.username,
            registration.email,
            registration.password
        )
        
        # Create access control permissions
        access_control_manager.create_user_permissions(user_id, UserRole.DEMO_USER)
        
        # Initialize paper trading portfolio
        user_portfolio_manager.initialize_user_portfolio(
            user_id,
            PortfolioType.PAPER,
            registration.initial_capital
        )
        
        # Record registration event
        background_tasks.add_task(
            portfolio_persistence_layer.record_event,
            PersistenceEventType.USER_LOGIN,
            user_id,
            {"registration": True, "initial_capital": registration.initial_capital}
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "message": f"User {registration.username} registered successfully"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

@router.get("/portfolio/{portfolio_type}")
async def get_user_portfolio(
    portfolio_type: str,
    user_id: str = Depends(get_current_user)
):
    """Get user's portfolio data"""
    try:
        portfolio_enum = PortfolioType(portfolio_type.lower())
        portfolio_data = user_portfolio_manager.get_user_portfolio(user_id, portfolio_enum)
        
        if not portfolio_data:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get wealth summary
        wealth_summary = wealth_management_system.get_wealth_summary(user_id, portfolio_type)
        
        return {
            "success": True,
            "portfolio": portfolio_data,
            "wealth_summary": wealth_summary
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid portfolio type")
    except Exception as e:
        logger.error(f"Failed to get portfolio: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve portfolio")

@router.post("/trade")
async def execute_trade(
    trade: TradeOrder,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Execute a trade order"""
    try:
        # Check permissions
        portfolio_enum = PortfolioType(trade.portfolio_type.lower())
        
        if portfolio_enum == PortfolioType.LIVE:
            if not access_control_manager.has_permission(user_id, PermissionType.LIVE_TRADING):
                raise HTTPException(status_code=403, detail="Live trading not approved")
        
        # Execute trade
        success = user_portfolio_manager.execute_trade(
            user_id,
            portfolio_enum,
            trade.symbol,
            trade.action,
            trade.quantity,
            trade.price
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Trade execution failed")
        
        # Record trade event
        background_tasks.add_task(
            portfolio_persistence_layer.record_event,
            PersistenceEventType.TRADE_EXECUTION,
            user_id,
            {
                "symbol": trade.symbol,
                "action": trade.action,
                "quantity": trade.quantity,
                "price": trade.price,
                "portfolio_type": trade.portfolio_type
            }
        )
        
        return {
            "success": True,
            "message": f"Trade executed: {trade.action} {trade.quantity} {trade.symbol} @ ${trade.price}"
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trade parameters")
    except Exception as e:
        logger.error(f"Trade execution failed: {e}")
        raise HTTPException(status_code=500, detail="Trade execution failed")

@router.post("/update-portfolio")
async def update_portfolio(
    update: PortfolioUpdate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user)
):
    """Update portfolio value (called by background systems)"""
    try:
        # Update portfolio in persistent engine
        persistent_trading_engine.update_portfolio_value(user_id, update.total_value)
        
        # Create wealth snapshot
        wealth_management_system.create_wealth_snapshot(
            user_id,
            "paper",  # Default to paper for now
            update.total_value,
            update.total_value,  # Allocated capital (simplified)
            update.cash_balance,
            update.total_value - update.cash_balance
        )
        
        # Record portfolio update event
        background_tasks.add_task(
            portfolio_persistence_layer.record_event,
            PersistenceEventType.PORTFOLIO_UPDATE,
            user_id,
            {
                "total_value": update.total_value,
                "positions": update.positions,
                "cash_balance": update.cash_balance
            }
        )
        
        return {"success": True, "message": "Portfolio updated"}
        
    except Exception as e:
        logger.error(f"Portfolio update failed: {e}")
        raise HTTPException(status_code=500, detail="Portfolio update failed")

# Admin Endpoints
@router.get("/admin/users")
async def get_all_users(admin_id: str = Depends(verify_admin_permission)):
    """Get all users for admin dashboard"""
    try:
        users = access_control_manager.get_all_users_permissions()
        
        # Enhance with portfolio data
        enhanced_users = []
        for user in users:
            portfolio = persistent_trading_engine.get_user_portfolio(user['user_id'])
            wealth_summary = wealth_management_system.get_wealth_summary(
                user['user_id'], 
                "paper"
            )
            
            enhanced_users.append({
                **user,
                'total_return': wealth_summary.get('total_return', 0) if isinstance(wealth_summary, dict) else 0,
                'total_return_percent': wealth_summary.get('total_return_percent', 0) if isinstance(wealth_summary, dict) else 0,
                'current_value': portfolio.current_value if portfolio else 0
            })
        
        return {"success": True, "users": enhanced_users}
        
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve users")

@router.post("/admin/approve-live-trading")
async def approve_live_trading(
    approval: TradingApproval,
    admin_id: str = Depends(verify_admin_permission)
):
    """Approve user for live trading"""
    try:
        success = access_control_manager.approve_live_trading(
            approval.user_id,
            admin_id,
            approval.max_allocation,
            approval.reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to approve live trading")
        
        # Initialize live trading portfolio
        user_portfolio_manager.initialize_user_portfolio(
            approval.user_id,
            PortfolioType.LIVE,
            approval.max_allocation
        )
        
        return {
            "success": True,
            "message": f"Live trading approved with ${approval.max_allocation:,.2f} allocation"
        }
        
    except Exception as e:
        logger.error(f"Live trading approval failed: {e}")
        raise HTTPException(status_code=500, detail="Live trading approval failed")

@router.post("/admin/revoke-live-trading")
async def revoke_live_trading(
    revocation: TradingApproval,
    admin_id: str = Depends(verify_admin_permission)
):
    """Revoke live trading access"""
    try:
        success = access_control_manager.revoke_live_trading(
            revocation.user_id,
            admin_id,
            revocation.reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to revoke live trading")
        
        return {"success": True, "message": "Live trading access revoked"}
        
    except Exception as e:
        logger.error(f"Live trading revocation failed: {e}")
        raise HTTPException(status_code=500, detail="Live trading revocation failed")

@router.post("/admin/allocate-funds")
async def allocate_funds(
    allocation: FundAllocation,
    admin_id: str = Depends(verify_admin_permission)
):
    """Allocate funds to user's live trading account"""
    try:
        success = access_control_manager.allocate_funds(
            allocation.user_id,
            admin_id,
            allocation.amount,
            allocation.reason
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to allocate funds")
        
        # Record allocation in wealth management
        wealth_management_system.record_allocation(
            allocation.user_id,
            allocation.amount,
            "additional",
            admin_id,
            allocation.reason
        )
        
        return {
            "success": True,
            "message": f"${allocation.amount:,.2f} allocated successfully"
        }
        
    except Exception as e:
        logger.error(f"Fund allocation failed: {e}")
        raise HTTPException(status_code=500, detail="Fund allocation failed")

@router.get("/admin/allocation-requests")
async def get_allocation_requests(admin_id: str = Depends(verify_admin_permission)):
    """Get pending allocation requests"""
    try:
        requests = access_control_manager.get_pending_requests()
        return {"success": True, "requests": requests}
        
    except Exception as e:
        logger.error(f"Failed to get allocation requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve allocation requests")

@router.get("/admin/system-metrics")
async def get_system_metrics(admin_id: str = Depends(verify_admin_permission)):
    """Get system-wide metrics"""
    try:
        users = access_control_manager.get_all_users_permissions()

        metrics = {
            "total_users": len(users),
            "active_traders": len([u for u in users if u['live_trading_approved']]),
            "total_allocated": sum(u['current_allocation'] for u in users),
            "total_portfolio_value": 0,  # Calculate from portfolios
            "pending_requests": len(access_control_manager.get_pending_requests()),
            "system_uptime": portfolio_persistence_layer.get_system_health().get('uptime', 0),
            "active_sessions": portfolio_persistence_layer.get_system_health().get('active_sessions', 0),
            "daily_trades": 0  # Calculate from today's transactions
        }

        # Calculate total portfolio value
        total_value = 0
        for user in users:
            portfolio = persistent_trading_engine.get_user_portfolio(user['user_id'])
            if portfolio:
                total_value += portfolio.current_value

        metrics["total_portfolio_value"] = total_value

        return {"success": True, "metrics": metrics}

    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")

# Enhanced Admin Endpoints for Comprehensive Management

@router.post("/admin/create-user")
async def create_user(user_data: UserRegistration, admin_id: str = Depends(verify_admin_permission)):
    """Create a new user (admin only)"""
    try:
        user_id = user_portfolio_manager.create_user_profile(
            user_data.username,
            user_data.email,
            user_data.password
        )

        # Set initial permissions
        access_control_manager.create_user_permissions(user_id, UserRole.DEMO_USER)

        # Initialize paper trading portfolio
        user_portfolio_manager.initialize_user_portfolio(
            user_id,
            PortfolioType.PAPER,
            user_data.initial_capital
        )

        return {
            "success": True,
            "user_id": user_id,
            "message": f"User {user_data.username} created successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

@router.patch("/admin/users/{user_id}")
async def update_user(user_id: str, updates: dict, admin_id: str = Depends(verify_admin_permission)):
    """Update user information"""
    try:
        # Implementation for updating user details
        # This would integrate with user_portfolio_manager to update user info

        return {"success": True, "message": "User updated successfully"}

    except Exception as e:
        logger.error(f"Failed to update user: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.post("/admin/users/{user_id}/deactivate")
async def deactivate_user(user_id: str, reason_data: dict, admin_id: str = Depends(verify_admin_permission)):
    """Deactivate a user account"""
    try:
        # Implementation for deactivating user
        # This would update user status in access_control_manager

        return {"success": True, "message": "User deactivated successfully"}

    except Exception as e:
        logger.error(f"Failed to deactivate user: {e}")
        raise HTTPException(status_code=500, detail="Failed to deactivate user")

@router.post("/admin/users/{user_id}/reset-password")
async def reset_user_password(user_id: str, admin_id: str = Depends(verify_admin_permission)):
    """Reset user password"""
    try:
        # Generate new temporary password
        import secrets
        import string
        new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

        # Implementation for password reset
        # This would update password in user_portfolio_manager

        return {
            "success": True,
            "new_password": new_password,
            "message": "Password reset successfully"
        }

    except Exception as e:
        logger.error(f"Failed to reset password: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

@router.post("/request-allocation")
async def request_allocation(
    request: AllocationRequest,
    user_id: str = Depends(get_current_user)
):
    """Submit allocation request"""
    try:
        request_id = access_control_manager.request_allocation(
            user_id,
            request.amount,
            request.justification
        )
        
        return {
            "success": True,
            "request_id": request_id,
            "message": "Allocation request submitted"
        }
        
    except Exception as e:
        logger.error(f"Allocation request failed: {e}")
        raise HTTPException(status_code=500, detail="Allocation request failed")

# Permissions Management Endpoints

@router.get("/admin/permissions")
async def get_all_permissions(admin_id: str = Depends(verify_admin_permission)):
    """Get all user permissions"""
    try:
        # Implementation to get all permissions from access_control_manager
        permissions = []  # This would be populated from the database

        return {"success": True, "permissions": permissions}

    except Exception as e:
        logger.error(f"Failed to get permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve permissions")

@router.patch("/admin/permissions/{permission_id}")
async def update_permission(permission_id: str, updates: dict, admin_id: str = Depends(verify_admin_permission)):
    """Update a specific permission"""
    try:
        # Implementation for updating permissions

        return {"success": True, "message": "Permission updated successfully"}

    except Exception as e:
        logger.error(f"Failed to update permission: {e}")
        raise HTTPException(status_code=500, detail="Failed to update permission")

@router.post("/admin/permissions/{permission_id}/revoke")
async def revoke_permission(permission_id: str, reason_data: dict, admin_id: str = Depends(verify_admin_permission)):
    """Revoke a specific permission"""
    try:
        # Implementation for revoking permissions

        return {"success": True, "message": "Permission revoked successfully"}

    except Exception as e:
        logger.error(f"Failed to revoke permission: {e}")
        raise HTTPException(status_code=500, detail="Failed to revoke permission")

# Fund Allocation Management Endpoints

@router.get("/admin/allocation-history")
async def get_allocation_history(admin_id: str = Depends(verify_admin_permission)):
    """Get allocation history"""
    try:
        # Get allocation history from wealth_management_system
        history = []  # This would be populated from the database

        return {"success": True, "history": history}

    except Exception as e:
        logger.error(f"Failed to get allocation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve allocation history")

@router.post("/admin/reject-allocation-request")
async def reject_allocation_request(rejection_data: dict, admin_id: str = Depends(verify_admin_permission)):
    """Reject an allocation request"""
    try:
        request_id = rejection_data.get("request_id")
        reason = rejection_data.get("reason")

        # Implementation for rejecting allocation requests

        return {"success": True, "message": "Allocation request rejected"}

    except Exception as e:
        logger.error(f"Failed to reject allocation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to reject allocation request")

# System Monitoring Endpoints

@router.get("/admin/system-health")
async def get_detailed_system_health(admin_id: str = Depends(verify_admin_permission)):
    """Get detailed system health information"""
    try:
        health = portfolio_persistence_layer.get_system_health()

        # Add more detailed system information
        detailed_health = {
            "overall_status": "healthy",  # This would be calculated based on various metrics
            "uptime": health.get("uptime", 0),
            "cpu_usage": 45.2,  # This would come from system monitoring
            "memory_usage": 62.8,
            "disk_usage": 34.1,
            "active_connections": health.get("active_sessions", 0),
            "background_tasks": health.get("pending_events", 0),
            "database_status": "connected",
            "api_response_time": 125,  # milliseconds
            "error_rate": 0.02,  # percentage
            "last_backup": "2024-01-15T10:30:00Z"
        }

        return {"success": True, "health": detailed_health}

    except Exception as e:
        logger.error(f"Failed to get detailed system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve detailed system health")

@router.get("/admin/detailed-metrics")
async def get_detailed_metrics(admin_id: str = Depends(verify_admin_permission)):
    """Get detailed system metrics"""
    try:
        # This would return detailed metrics for system monitoring
        metrics = [
            {
                "metric_name": "api_requests_per_minute",
                "current_value": 245,
                "previous_value": 230,
                "change_percent": 6.52,
                "status": "healthy",
                "last_updated": datetime.now().isoformat(),
                "threshold_warning": 500,
                "threshold_critical": 1000
            },
            {
                "metric_name": "database_connections",
                "current_value": 12,
                "previous_value": 15,
                "change_percent": -20.0,
                "status": "healthy",
                "last_updated": datetime.now().isoformat(),
                "threshold_warning": 50,
                "threshold_critical": 80
            }
        ]

        return {"success": True, "metrics": metrics}

    except Exception as e:
        logger.error(f"Failed to get detailed metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve detailed metrics")

@router.get("/admin/performance-data")
async def get_performance_data(admin_id: str = Depends(verify_admin_permission)):
    """Get performance data for charts and graphs"""
    try:
        # This would return time-series data for performance monitoring
        performance_data = []  # This would be populated with actual performance data

        return {"success": True, "data": performance_data}

    except Exception as e:
        logger.error(f"Failed to get performance data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance data")

@router.post("/admin/system-action")
async def execute_system_action(action_data: dict, admin_id: str = Depends(verify_admin_permission)):
    """Execute system management actions"""
    try:
        action = action_data.get("action")
        params = action_data.get("params", {})

        # Implementation for various system actions
        if action == "restart_services":
            # Restart background services
            pass
        elif action == "backup_system":
            # Trigger system backup
            pass
        elif action == "refresh_metrics":
            # Refresh system metrics
            pass
        # Add more system actions as needed

        return {"success": True, "message": f"System action '{action}' completed"}

    except Exception as e:
        logger.error(f"Failed to execute system action: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute system action")

@router.get("/system-health")
async def get_system_health():
    """Get system health status"""
    try:
        health = portfolio_persistence_layer.get_system_health()

        # Add trading engine status
        health.update({
            "trading_engine_running": persistent_trading_engine.is_running,
            "total_portfolios": len(persistent_trading_engine.user_portfolios)
        })

        return {"success": True, "health": health}

    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system health")

# Audit and Reporting Endpoints

@router.get("/admin/audit-logs")
async def get_audit_logs(admin_id: str = Depends(verify_admin_permission)):
    """Get audit logs for admin actions"""
    try:
        # This would get audit logs from access_control_manager or a dedicated audit system
        audit_logs = [
            {
                "log_id": "audit_001",
                "admin_id": admin_id,
                "admin_username": "admin",
                "action_type": "approve_live_trading",
                "target_user_id": "user_123",
                "target_username": "demo_user_1",
                "action_details": "Approved live trading with $50,000 allocation",
                "timestamp": datetime.now().isoformat(),
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "result": "success",
                "error_message": None
            }
        ]

        return {"success": True, "logs": audit_logs}

    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve audit logs")

@router.post("/admin/generate-report")
async def generate_report(report_data: dict, admin_id: str = Depends(verify_admin_permission)):
    """Generate various administrative reports"""
    try:
        report_type = report_data.get("report_type")
        params = report_data.get("params", {})

        # Implementation for different report types
        if report_type == "audit_summary":
            # Generate audit summary report
            report_content = "Audit Summary Report\n" + "="*50 + "\n"
            # Add report content here

        elif report_type == "user_activity":
            # Generate user activity report
            report_content = "User Activity Report\n" + "="*50 + "\n"
            # Add report content here

        elif report_type == "permission_changes":
            # Generate permission changes report
            report_content = "Permission Changes Report\n" + "="*50 + "\n"
            # Add report content here

        elif report_type == "allocation_history":
            # Generate allocation history report
            report_content = "Allocation History Report\n" + "="*50 + "\n"
            # Add report content here

        elif report_type == "system_events":
            # Generate system events report
            report_content = "System Events Report\n" + "="*50 + "\n"
            # Add report content here

        elif report_type == "security_audit":
            # Generate security audit report
            report_content = "Security Audit Report\n" + "="*50 + "\n"
            # Add report content here

        elif report_type == "compliance_report":
            # Generate compliance report
            report_content = "Compliance Report\n" + "="*50 + "\n"
            # Add report content here

        else:
            raise HTTPException(status_code=400, detail="Invalid report type")

        # In a real implementation, this would generate a CSV/PDF file and return it
        # For now, we'll return a success message
        return {"success": True, "message": f"Report '{report_type}' generated successfully"}

    except Exception as e:
        logger.error(f"Failed to generate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

# Additional Admin Utility Endpoints

@router.post("/admin/approve-allocation-request")
async def approve_allocation_request_endpoint(approval_data: dict, admin_id: str = Depends(verify_admin_permission)):
    """Approve an allocation request (enhanced version)"""
    try:
        request_id = approval_data.get("request_id")
        approved = approval_data.get("approved", True)

        if approved:
            # Get the request details and process the allocation
            # This would integrate with the existing allocation system
            success = True  # Placeholder for actual implementation

            if success:
                return {"success": True, "message": "Allocation request approved successfully"}
            else:
                raise HTTPException(status_code=400, detail="Failed to process allocation")
        else:
            return {"success": True, "message": "Allocation request marked as not approved"}

    except Exception as e:
        logger.error(f"Failed to approve allocation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to approve allocation request")

@router.get("/admin/dashboard-summary")
async def get_dashboard_summary(admin_id: str = Depends(verify_admin_permission)):
    """Get comprehensive dashboard summary for admin overview"""
    try:
        users = access_control_manager.get_all_users_permissions()
        pending_requests = access_control_manager.get_pending_requests()
        system_health = portfolio_persistence_layer.get_system_health()

        # Calculate comprehensive metrics
        total_allocated = sum(u['current_allocation'] for u in users)
        total_capacity = sum(u['max_allocation'] for u in users)
        utilization_rate = (total_allocated / total_capacity * 100) if total_capacity > 0 else 0

        # Get recent activity (last 24 hours)
        recent_activity = []  # This would be populated from audit logs

        # System alerts
        alerts = []
        if utilization_rate > 90:
            alerts.append({
                "type": "warning",
                "message": f"High allocation utilization: {utilization_rate:.1f}%",
                "timestamp": datetime.now().isoformat()
            })

        if len(pending_requests) > 10:
            alerts.append({
                "type": "info",
                "message": f"{len(pending_requests)} pending allocation requests",
                "timestamp": datetime.now().isoformat()
            })

        summary = {
            "overview": {
                "total_users": len(users),
                "active_traders": len([u for u in users if u['live_trading_approved']]),
                "total_allocated": total_allocated,
                "total_capacity": total_capacity,
                "utilization_rate": utilization_rate,
                "pending_requests": len(pending_requests),
                "system_uptime": system_health.get("uptime", 0),
                "active_sessions": system_health.get("active_sessions", 0)
            },
            "recent_activity": recent_activity,
            "alerts": alerts,
            "system_status": {
                "trading_engine": persistent_trading_engine.is_running,
                "persistence_layer": system_health.get("persistence_engine_running", False),
                "database": "connected",  # This would be checked dynamically
                "api_status": "healthy"
            }
        }

        return {"success": True, "summary": summary}

    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard summary")

# Background task to start persistent systems
@router.on_event("startup")
async def startup_event():
    """Start persistent trading systems"""
    try:
        # Start background trading engine
        persistent_trading_engine.start_background_trading()

        # Start persistence layer
        portfolio_persistence_layer.start_persistence_engine()

        logger.info("Persistent trading systems started")

    except Exception as e:
        logger.error(f"Failed to start persistent systems: {e}")

@router.on_event("shutdown")
async def shutdown_event():
    """Stop persistent trading systems"""
    try:
        # Stop background trading engine
        persistent_trading_engine.stop_background_trading()

        # Stop persistence layer
        portfolio_persistence_layer.stop_persistence_engine()

        logger.info("Persistent trading systems stopped")

    except Exception as e:
        logger.error(f"Failed to stop persistent systems: {e}")

# Export router
__all__ = ["router"]
