#!/usr/bin/env python3
"""
🔧 QUICK API FIX - Missing Endpoints Server
Runs on port 8001 to provide missing API endpoints for frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uvicorn
import uuid

# Create FastAPI app
app = FastAPI(
    title="PROMETHEUS API Fix",
    description="Missing endpoints for frontend integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data
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
        "total_pnl": 1250.75,
        "pnlPercentage": 12.51
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
        "total_pnl": 8750.25,
        "pnlPercentage": 17.50
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

@app.get("/")
async def root():
    return {
        "message": "PROMETHEUS API Fix Server",
        "status": "operational",
        "endpoints": [
            "/api/admin/dashboard",
            "/api/admin/users", 
            "/api/admin/invite-user",
            "/api/user/sessions",
            "/api/ai-trading/health"
        ]
    }

@app.get("/api/admin/dashboard")
async def get_admin_dashboard():
    """Get admin dashboard metrics"""
    return {
        "success": True,
        "total_users": len(MOCK_USERS),
        "active_traders": len([u for u in MOCK_USERS if u["status"] == "active"]),
        "total_allocated_funds": sum(u["allocated_funds"] for u in MOCK_USERS),
        "total_portfolio_value": sum(u["paper_balance"] + u["allocated_funds"] for u in MOCK_USERS),
        "daily_pnl": 2156.25,
        "system_uptime": 99.8,
        "pending_approvals": 3,
        "active_sessions": len([s for s in MOCK_SESSIONS if s["status"] == "active"]),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/admin/users")
async def get_admin_users():
    """Get all users for admin management"""
    return {
        "success": True,
        "users": MOCK_USERS,
        "total_count": len(MOCK_USERS),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/admin/invite-user")
async def invite_user(invite_data: dict):
    """Invite a new user"""
    email = invite_data.get("email", "")
    new_user_id = f"user_{str(uuid.uuid4())[:8]}"
    
    return {
        "success": True,
        "message": f"Invitation sent to {email}",
        "user_id": new_user_id,
        "invitation_code": f"INV_{str(uuid.uuid4())[:12].upper()}",
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }

@app.get("/api/user/sessions")
async def get_user_sessions():
    """Get user trading sessions"""
    return {
        "success": True,
        "sessions": MOCK_SESSIONS,
        "total_count": len(MOCK_SESSIONS),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ai-trading/health")
async def get_ai_trading_health():
    """Get AI trading system health"""
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

if __name__ == "__main__":
    print("🔧 Starting PROMETHEUS API Fix Server on port 8001...")
    print("🌐 This server provides missing endpoints for frontend integration")
    print("📊 Frontend should use http://localhost:8001 for missing APIs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
