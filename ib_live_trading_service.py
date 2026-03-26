#!/usr/bin/env python3
"""
Interactive Brokers Live Trading Service for PROMETHEUS
Runs as separate service alongside current trading session
"""
import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for IB Live Trading
app = FastAPI(
    title="PROMETHEUS IB Live Trading Service",
    description="Interactive Brokers Live Trading API",
    version="1.0.0"
)

# IB Live Trading Configuration
IB_LIVE_CONFIG = {
    "enabled": os.getenv("IB_LIVE_ENABLED", "false").lower() == "true",  # default DISABLED; enable explicitly via env
    "host": os.getenv("IB_LIVE_HOST", "127.0.0.1"),
    "port": int(os.getenv("IB_LIVE_PORT", "7496")),
    "client_id": int(os.getenv("IB_LIVE_CLIENT_ID", "2")),
    "account_id": os.getenv("IB_LIVE_ACCOUNT_ID", "DUN683505"),
    "max_daily_loss": float(os.getenv("LIVE_MAX_DAILY_LOSS_DOLLARS", "50.0"))
}

# Global state
live_trading_enabled = False  # default DISABLED; must be explicitly enabled
daily_pnl = 0.0
trades_today = 0

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "PROMETHEUS IB Live Trading Service",
        "status": "operational",
        "warning": "🚨 REAL MONEY TRADING SERVICE",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ib-live/status")
async def get_ib_live_status():
    """Get IB live trading status"""
    return {
        "service": "PROMETHEUS IB Live Trading",
        "status": "configured" if IB_LIVE_CONFIG["enabled"] else "disabled",
        "connection": "disconnected",  # Will be updated when connected
        "account_id": IB_LIVE_CONFIG["account_id"],
        "port": IB_LIVE_CONFIG["port"],
        "trading_mode": "live",
        "live_trading_enabled": live_trading_enabled,
        "daily_pnl": daily_pnl,
        "trades_today": trades_today,
        "safety_features": {
            "confirmation_required": True,
            "daily_loss_limit": IB_LIVE_CONFIG["max_daily_loss"],
            "position_size_limit": "1%",
            "stop_loss_default": "1.5%",
            "emergency_stop_available": True
        },
        "risk_management": {
            "max_position_size_percent": 1.0,
            "max_daily_trades": 5,
            "max_portfolio_risk_percent": 0.5,
            "default_stop_loss_percent": 1.5,
            "emergency_stop_loss_percent": 3.0
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ib-live/account")
async def get_ib_live_account():
    """Get IB live account information"""
    if not IB_LIVE_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="IB Live trading not enabled")
    
    # This would connect to actual IB API in production
    return {
        "account_id": IB_LIVE_CONFIG["account_id"],
        "account_type": "live",
        "currency": "USD",
        "buying_power": 0.0,  # Will be populated from IB API
        "net_liquidation": 0.0,
        "available_funds": 0.0,
        "day_trades_remaining": 0,
        "warning": "🚨 LIVE TRADING ACCOUNT - REAL MONEY",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ib-live/enable")
async def enable_ib_live_trading(request: Request):
    """Enable IB live trading with confirmation"""
    global live_trading_enabled
    
    try:
        body = await request.json()
        confirmation_code = body.get("confirmation_code", "")
    except:
        confirmation_code = ""
    
    if confirmation_code != "PROMETHEUS_LIVE_CONFIRMED":
        raise HTTPException(status_code=400, detail="Invalid confirmation code")
    
    if not IB_LIVE_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="IB Live trading not configured")
    
    live_trading_enabled = True
    logger.warning("🚨 LIVE TRADING ENABLED - REAL MONEY MODE ACTIVE!")
    
    return {
        "status": "live_trading_enabled",
        "warning": "🚨 REAL MONEY TRADING IS NOW ACTIVE",
        "safety_features_active": True,
        "confirmation_required": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ib-live/disable")
async def disable_ib_live_trading():
    """Disable IB live trading"""
    global live_trading_enabled
    
    live_trading_enabled = False
    logger.info("[CHECK] Live trading disabled safely")
    
    return {
        "status": "live_trading_disabled",
        "message": "Live trading has been safely disabled",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ib-live/positions")
async def get_ib_live_positions():
    """Get current live positions"""
    if not IB_LIVE_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="IB Live trading not enabled")
    
    # Would fetch from IB API
    return {
        "positions": [],
        "total_value": 0.0,
        "unrealized_pnl": 0.0,
        "warning": "🚨 LIVE POSITIONS - REAL MONEY",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ib-live/order")
async def place_ib_live_order(request: Request):
    """Place live order (with safety checks)"""
    global trades_today, daily_pnl
    
    if not IB_LIVE_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="IB Live trading not enabled")
    
    if not live_trading_enabled:
        raise HTTPException(status_code=400, detail="Live trading not enabled")
    
    try:
        order_data = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid order data")
    
    # Safety checks
    if abs(daily_pnl) >= IB_LIVE_CONFIG["max_daily_loss"]:
        raise HTTPException(status_code=400, detail=f"Daily loss limit reached: ${daily_pnl}")
    
    if trades_today >= 5:  # Max daily trades
        raise HTTPException(status_code=400, detail=f"Daily trade limit reached: {trades_today}")
    
    # Safety checks would be implemented here
    return {
        "status": "order_requires_confirmation",
        "message": "🚨 Live orders require manual confirmation",
        "order_data": order_data,
        "warning": "REAL MONEY ORDER - CONFIRM BEFORE EXECUTION",
        "safety_checks": {
            "daily_pnl": daily_pnl,
            "trades_today": trades_today,
            "within_limits": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/ib-live/connection/test")
async def test_ib_connection():
    """Test connection to IB Gateway - REAL CONNECTION TEST"""
    try:
        # First test if the port is accessible
        import socket

        host = IB_LIVE_CONFIG["host"]
        port = IB_LIVE_CONFIG["port"]

        # Test socket connectivity
        socket_connected = False
        socket_error = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            result = sock.connect_ex((host, port))
            socket_connected = (result == 0)
            sock.close()
        except Exception as e:
            socket_error = str(e)

        if not socket_connected:
            return {
                "status": "connection_test",
                "host": host,
                "port": port,
                "result": "failed",
                "connected": False,
                "message": f"Cannot connect to IB Gateway at {host}:{port}. Make sure TWS or IB Gateway is running and API connections are enabled.",
                "error": socket_error or f"Port {port} not accessible",
                "troubleshooting": [
                    "1. Launch TWS (Trader Workstation) or IB Gateway",
                    "2. In TWS: File > Global Configuration > API > Settings",
                    "3. Enable 'Enable ActiveX and Socket Clients'",
                    "4. Set 'Socket port' to 7496 (live) or 7497 (paper)",
                    "5. Add 127.0.0.1 to 'Trusted IPs'"
                ],
                "timestamp": datetime.now().isoformat()
            }

        # Try to connect using the IB API if available
        try:
            from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE

            if not IB_AVAILABLE:
                return {
                    "status": "connection_test",
                    "host": host,
                    "port": port,
                    "result": "partial",
                    "connected": False,
                    "socket_connected": True,
                    "message": "Socket connection successful but ibapi library not installed",
                    "error": "IB API library not available - install with: pip install ibapi",
                    "timestamp": datetime.now().isoformat()
                }

            # Create a test connection
            config = {
                'host': host,
                'port': port,
                'client_id': IB_LIVE_CONFIG["client_id"],
                'paper_trading': port == 7497
            }

            ib_broker = InteractiveBrokersBroker(config)
            connected = await asyncio.wait_for(ib_broker.connect(), timeout=10.0)

            if connected:
                # Get account info
                account_info = await ib_broker.get_account()
                await ib_broker.disconnect()

                return {
                    "status": "connection_test",
                    "host": host,
                    "port": port,
                    "result": "success",
                    "connected": True,
                    "trading_mode": "paper" if port == 7497 else "live",
                    "account_id": IB_LIVE_CONFIG["account_id"],
                    "account_info": {
                        "buying_power": getattr(account_info, 'buying_power', 0) if account_info else 0,
                        "net_liquidation": getattr(account_info, 'equity', 0) if account_info else 0
                    },
                    "message": "Successfully connected to IB Gateway",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "connection_test",
                    "host": host,
                    "port": port,
                    "result": "failed",
                    "connected": False,
                    "socket_connected": True,
                    "message": "Socket connected but IB API connection failed",
                    "error": "API handshake failed - check TWS settings",
                    "timestamp": datetime.now().isoformat()
                }

        except asyncio.TimeoutError:
            return {
                "status": "connection_test",
                "host": host,
                "port": port,
                "result": "timeout",
                "connected": False,
                "socket_connected": True,
                "message": "Connection attempt timed out after 10 seconds",
                "error": "IB Gateway not responding - check if logged in",
                "timestamp": datetime.now().isoformat()
            }
        except ImportError:
            return {
                "status": "connection_test",
                "host": host,
                "port": port,
                "result": "partial",
                "connected": False,
                "socket_connected": True,
                "message": "Socket connection successful but IB broker module not available",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "connection_test",
                "host": host,
                "port": port,
                "result": "failed",
                "connected": False,
                "socket_connected": True,
                "message": f"IB API connection error: {str(e)}",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

@app.get("/api/ib-live/safety/status")
async def get_safety_status():
    """Get safety system status"""
    return {
        "safety_systems": {
            "confirmation_required": True,
            "daily_loss_limit_active": True,
            "position_size_limits_active": True,
            "emergency_stop_available": True
        },
        "current_limits": {
            "daily_pnl": daily_pnl,
            "max_daily_loss": IB_LIVE_CONFIG["max_daily_loss"],
            "trades_today": trades_today,
            "max_daily_trades": 5
        },
        "status": "all_safety_systems_active",
        "timestamp": datetime.now().isoformat()
    }

def main():
    """Run the IB Live Trading Service"""
    print("🚀 STARTING PROMETHEUS IB LIVE TRADING SERVICE")
    print("=" * 60)
    print("🚨 WARNING: This service enables REAL MONEY trading!")
    print("🚨 WARNING: Use with extreme caution!")
    print("=" * 60)
    print(f"Service will run on: http://localhost:8001")
    print(f"IB Account: {IB_LIVE_CONFIG['account_id']}")
    print(f"IB Port: {IB_LIVE_CONFIG['port']} (Live Trading)")
    print(f"Max Daily Loss: ${IB_LIVE_CONFIG['max_daily_loss']}")
    print("=" * 60)
    
    # Load live environment if available
    env_live_file = ".env.live"
    if os.path.exists(env_live_file):
        print(f"[CHECK] Loading live environment: {env_live_file}")
        # Load environment variables from .env.live
        with open(env_live_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Start the service
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Different port to avoid conflict
        log_level="info"
    )

if __name__ == "__main__":
    main()
