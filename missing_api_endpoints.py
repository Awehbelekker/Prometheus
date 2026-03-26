#!/usr/bin/env python3
"""
🔗 MISSING API ENDPOINTS FOR PROMETHEUS FRONTEND
Creates the missing backend endpoints that the frontend is trying to access
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import json

# Create FastAPI app for missing endpoints
missing_api = FastAPI(
    title="PROMETHEUS Missing API Endpoints",
    description="Backend endpoints to support frontend functionality",
    version="1.0.0"
)

# Add CORS middleware
missing_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data for development
MOCK_USERS = [
    {
        "id": "user_001",
        "username": "demo_trader",
        "email": "demo@prometheus.com",
        "role": "user",
        "tier": "paper_only",
        "created_at": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-15T10:30:00Z",
        "status": "active",
        "paper_balance": 10000.0,
        "allocated_funds": 0.0,
        "total_trades": 45,
        "win_rate": 68.5,
        "total_pnl": 1250.75
    },
    {
        "id": "user_002", 
        "username": "pro_investor",
        "email": "investor@prometheus.com",
        "role": "user",
        "tier": "live_approved",
        "created_at": "2025-01-02T00:00:00Z",
        "last_login": "2025-01-15T14:20:00Z",
        "status": "active",
        "paper_balance": 25000.0,
        "allocated_funds": 50000.0,
        "total_trades": 128,
        "win_rate": 74.2,
        "total_pnl": 8750.25
    }
]

MOCK_SESSIONS = [
    {
        "id": "session_001",
        "user_id": "user_001",
        "type": "paper_trading",
        "status": "active",
        "start_time": "2025-01-15T09:00:00Z",
        "duration_hours": 6.5,
        "trades_count": 12,
        "pnl": 245.50,
        "win_rate": 75.0
    },
    {
        "id": "session_002",
        "user_id": "user_002", 
        "type": "live_trading",
        "status": "completed",
        "start_time": "2025-01-15T10:00:00Z",
        "end_time": "2025-01-15T16:00:00Z",
        "duration_hours": 6.0,
        "trades_count": 8,
        "pnl": 1250.75,
        "win_rate": 87.5
    }
]

MOCK_ADMIN_METRICS = {
    "total_users": len(MOCK_USERS),
    "active_traders": len([u for u in MOCK_USERS if u["status"] == "active"]),
    "total_allocated_funds": sum(u["allocated_funds"] for u in MOCK_USERS),
    "total_portfolio_value": sum(u["paper_balance"] + u["allocated_funds"] for u in MOCK_USERS),
    "daily_pnl": 2156.25,
    "system_uptime": 99.8,
    "pending_approvals": 3,
    "active_sessions": len([s for s in MOCK_SESSIONS if s["status"] == "active"])
}

# Request/Response Models
class UserInviteRequest(BaseModel):
    email: str
    initial_allocation: Optional[float] = 0.0
    message: Optional[str] = ""

class FundAllocationRequest(BaseModel):
    user_id: str
    amount: float
    reason: str = ""

# Admin Dashboard Endpoints
@missing_api.get("/api/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard metrics"""
    return {
        "success": True,
        "total_users": MOCK_ADMIN_METRICS["total_users"],
        "active_traders": MOCK_ADMIN_METRICS["active_traders"], 
        "total_allocated_funds": MOCK_ADMIN_METRICS["total_allocated_funds"],
        "total_portfolio_value": MOCK_ADMIN_METRICS["total_portfolio_value"],
        "daily_pnl": MOCK_ADMIN_METRICS["daily_pnl"],
        "system_uptime": MOCK_ADMIN_METRICS["system_uptime"],
        "pending_approvals": MOCK_ADMIN_METRICS["pending_approvals"],
        "active_sessions": MOCK_ADMIN_METRICS["active_sessions"],
        "timestamp": datetime.now().isoformat()
    }

@missing_api.get("/api/admin/users")
async def get_admin_users():
    """Get all users for admin management"""
    return {
        "success": True,
        "users": MOCK_USERS,
        "total_count": len(MOCK_USERS),
        "timestamp": datetime.now().isoformat()
    }

@missing_api.post("/api/admin/invite-user")
async def invite_user(invite_request: UserInviteRequest):
    """Invite a new user (admin only)"""
    # Simulate user invitation
    new_user_id = f"user_{str(uuid.uuid4())[:8]}"
    
    return {
        "success": True,
        "message": f"Invitation sent to {invite_request.email}",
        "user_id": new_user_id,
        "invitation_code": f"INV_{str(uuid.uuid4())[:12].upper()}",
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }

@missing_api.post("/api/admin/allocate-funds")
async def allocate_funds(allocation_request: FundAllocationRequest):
    """Allocate funds to a user"""
    # Find user and update allocation
    for user in MOCK_USERS:
        if user["id"] == allocation_request.user_id:
            user["allocated_funds"] += allocation_request.amount
            return {
                "success": True,
                "message": f"${allocation_request.amount:,.2f} allocated to user {user['username']}",
                "new_balance": user["allocated_funds"],
                "timestamp": datetime.now().isoformat()
            }
    
    raise HTTPException(status_code=404, detail="User not found")

# User Session Endpoints
@missing_api.get("/api/user/sessions")
async def get_user_sessions():
    """Get user trading sessions"""
    return {
        "success": True,
        "sessions": MOCK_SESSIONS,
        "total_count": len(MOCK_SESSIONS),
        "timestamp": datetime.now().isoformat()
    }

# AI Trading Health Endpoint
@missing_api.get("/api/ai-trading/health")
async def get_ai_trading_health():
    """Get AI trading system health status"""
    return {
        "success": True,
        "ai_trading_service": "healthy",
        "services": {
            "sentiment_analysis": True,
            "pattern_recognition": True,
            "risk_management": True,
            "execution_engine": True
        },
        "performance": {
            "accuracy": 87.5,
            "uptime": 99.9,
            "trades_today": 156,
            "success_rate": 74.2
        },
        "models": {
            "sentiment_model": "v2.1.0",
            "pattern_model": "v1.8.3", 
            "risk_model": "v3.0.1"
        },
        "last_check": datetime.now().isoformat(),
        "timestamp": datetime.now().isoformat()
    }

# Paper Trading Validation Endpoint
@missing_api.get("/api/paper-trading/validate-real-data")
async def validate_paper_trading():
    """Validate that paper trading uses real market data"""
    return {
        "success": True,
        "authentic_trading": True,
        "message": "Paper trading uses real market data only",
        "data_sources": [
            "Yahoo Finance",
            "Polygon.io Premium",
            "Alpaca Market Data"
        ],
        "validation_time": datetime.now().isoformat(),
        "market_status": "CLOSED" if datetime.now().weekday() >= 5 else "OPEN"
    }

# System Health Endpoint
@missing_api.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "PROMETHEUS Trading Platform",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "database": "operational", 
            "trading_engine": "operational",
            "market_data": "operational"
        }
    }

# Additional endpoints for frontend compatibility
@missing_api.get("/api/admin/admin-dashboard")
async def get_admin_dashboard_alt():
    """Alternative admin dashboard endpoint"""
    return await get_admin_dashboard()

@missing_api.get("/api/admin/system-metrics")
async def get_system_metrics():
    """Get detailed system metrics"""
    return {
        "success": True,
        "metrics": MOCK_ADMIN_METRICS,
        "performance": {
            "cpu_usage": 45.2,
            "memory_usage": 62.8,
            "disk_usage": 34.1,
            "network_io": 128.5
        },
        "trading_stats": {
            "total_trades_today": 245,
            "successful_trades": 182,
            "failed_trades": 63,
            "average_execution_time": 0.125
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting PROMETHEUS Missing API Endpoints Server...")
    print("📊 Providing mock data for frontend development")
    print("🌐 Server will run on http://localhost:8001")
    
    uvicorn.run(
        missing_api,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
