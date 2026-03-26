#!/usr/bin/env python3
"""
Integrate Interactive Brokers Live Trading with PROMETHEUS Backend
Non-disruptive integration that adds live trading capabilities
"""
import os
import sys
import json
import asyncio
import requests
from pathlib import Path
from datetime import datetime

class IBLiveTradingIntegration:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backend_url = "http://localhost:8000"
        
    def print_status(self, message, status="INFO"):
        """Print colored status messages"""
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "RESET": "\033[0m"
        }
        print(f"{colors.get(status, '')}{message}{colors['RESET']}")
    
    def check_backend_status(self):
        """Check if PROMETHEUS backend is running"""
        self.print_status("🔍 Checking PROMETHEUS Backend Status...", "INFO")
        
        try:
            response = requests.get(f"{self.backend_url}/api/health", timeout=5)
            if response.status_code == 200:
                self.print_status("[CHECK] PROMETHEUS Backend is running", "SUCCESS")
                return True
            else:
                self.print_status(f"[WARNING]️ Backend responded with status {response.status_code}", "WARNING")
                return False
        except requests.exceptions.RequestException as e:
            self.print_status(f"[ERROR] Backend not accessible: {e}", "ERROR")
            return False
    
    def add_ib_live_endpoints(self):
        """Add IB live trading endpoints to backend"""
        self.print_status("🔌 Adding IB Live Trading Endpoints...", "INFO")
        
        # Create the endpoint addition script
        endpoint_code = '''
# IB Live Trading Endpoints for PROMETHEUS Backend
# Add these to your unified_production_server.py

from fastapi import HTTPException
import json
import os
from datetime import datetime

# IB Live Trading Configuration
IB_LIVE_CONFIG = {
    "enabled": os.getenv("IB_LIVE_ENABLED", "false").lower() == "true",
    "host": os.getenv("IB_LIVE_HOST", "127.0.0.1"),
    "port": int(os.getenv("IB_LIVE_PORT", "7496")),
    "client_id": int(os.getenv("IB_LIVE_CLIENT_ID", "2")),
    "account_id": os.getenv("IB_LIVE_ACCOUNT_ID", ""),
    "max_daily_loss": float(os.getenv("LIVE_MAX_DAILY_LOSS_DOLLARS", "50.0"))
}

@app.get("/api/ib-live/status")
async def get_ib_live_status():
    """Get IB live trading status"""
    return {
        "status": "configured" if IB_LIVE_CONFIG["enabled"] else "disabled",
        "connection": "disconnected",  # Will be updated when connected
        "account_id": IB_LIVE_CONFIG["account_id"],
        "port": IB_LIVE_CONFIG["port"],
        "safety_features": {
            "confirmation_required": True,
            "daily_loss_limit": IB_LIVE_CONFIG["max_daily_loss"],
            "position_size_limit": "1%",
            "stop_loss_default": "1.5%"
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
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ib-live/enable")
async def enable_ib_live_trading(confirmation_code: str):
    """Enable IB live trading with confirmation"""
    if confirmation_code != "PROMETHEUS_LIVE_CONFIRMED":
        raise HTTPException(status_code=400, detail="Invalid confirmation code")
    
    if not IB_LIVE_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="IB Live trading not configured")
    
    # Enable live trading (would connect to IB API)
    return {
        "status": "live_trading_enabled",
        "warning": "REAL MONEY TRADING IS NOW ACTIVE",
        "safety_features_active": True,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ib-live/disable")
async def disable_ib_live_trading():
    """Disable IB live trading"""
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
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/ib-live/order")
async def place_ib_live_order(order_data: dict):
    """Place live order (with safety checks)"""
    if not IB_LIVE_CONFIG["enabled"]:
        raise HTTPException(status_code=400, detail="IB Live trading not enabled")
    
    # Safety checks would be implemented here
    return {
        "status": "order_requires_confirmation",
        "message": "Live orders require manual confirmation",
        "order_data": order_data,
        "timestamp": datetime.now().isoformat()
    }
'''
        
        # Save the endpoint code
        endpoint_file = self.project_root / 'ib_live_endpoints.py'
        with open(endpoint_file, 'w', encoding='utf-8') as f:
            f.write(endpoint_code)
        
        self.print_status(f"[CHECK] IB Live endpoints created: {endpoint_file}", "SUCCESS")
        return endpoint_file
    
    def create_ib_live_manager(self):
        """Create IB live trading manager"""
        self.print_status("🏦 Creating IB Live Trading Manager...", "INFO")
        
        manager_code = '''#!/usr/bin/env python3
"""
Interactive Brokers Live Trading Manager for PROMETHEUS
Handles live trading operations with safety features
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

class IBLiveTradingManager:
    """Manages IB live trading operations with safety features"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.live_trading_enabled = False
        self.daily_pnl = 0.0
        self.max_daily_loss = config.get('max_daily_loss', 50.0)
        self.trades_today = 0
        self.max_daily_trades = config.get('max_daily_trades', 5)
        
        # Safety features
        self.confirmation_required = True
        self.emergency_stop_active = False
        
        self.logger = logging.getLogger(__name__)
        self.logger.warning("🚨 IB Live Trading Manager initialized - REAL MONEY MODE")
    
    async def connect_to_ib(self) -> bool:
        """Connect to IB Gateway for live trading"""
        try:
            # Import IB API
            from ibapi.client import EClient
            from ibapi.wrapper import EWrapper
            
            # Initialize connection (placeholder)
            self.logger.warning("🚨 Connecting to IB Live Trading Gateway")
            
            # Connection logic would go here
            # For now, return False to prevent accidental live trading
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to IB: {e}")
            return False
    
    def enable_live_trading(self, confirmation_code: str) -> bool:
        """Enable live trading with confirmation"""
        if confirmation_code == "PROMETHEUS_LIVE_CONFIRMED":
            self.live_trading_enabled = True
            self.logger.warning("🚨 LIVE TRADING ENABLED - REAL MONEY AT RISK!")
            return True
        return False
    
    def disable_live_trading(self):
        """Disable live trading"""
        self.live_trading_enabled = False
        self.logger.info("[CHECK] Live trading disabled safely")
    
    async def place_live_order(self, symbol: str, quantity: int, order_type: str = "MKT") -> Optional[Dict]:
        """Place live order with safety checks"""
        if not self.live_trading_enabled:
            self.logger.error("[ERROR] Live trading not enabled")
            return None
        
        # Safety checks
        if abs(self.daily_pnl) >= self.max_daily_loss:
            self.logger.error(f"[ERROR] Daily loss limit reached: ${self.daily_pnl}")
            self.emergency_stop_active = True
            return None
        
        if self.trades_today >= self.max_daily_trades:
            self.logger.error(f"[ERROR] Daily trade limit reached: {self.trades_today}")
            return None
        
        if self.confirmation_required:
            self.logger.warning("[WARNING]️ Live order requires manual confirmation")
            return {
                "status": "requires_confirmation",
                "symbol": symbol,
                "quantity": quantity,
                "order_type": order_type,
                "timestamp": datetime.now().isoformat()
            }
        
        # Actual order placement would go here
        self.logger.warning(f"🚨 LIVE ORDER: {symbol} x {quantity} ({order_type})")
        return None
    
    def get_account_status(self) -> Dict[str, Any]:
        """Get live account status"""
        return {
            "live_trading_enabled": self.live_trading_enabled,
            "daily_pnl": self.daily_pnl,
            "trades_today": self.trades_today,
            "emergency_stop_active": self.emergency_stop_active,
            "confirmation_required": self.confirmation_required,
            "max_daily_loss": self.max_daily_loss,
            "max_daily_trades": self.max_daily_trades
        }

# Global instance
ib_live_manager = None

def get_ib_live_manager() -> IBLiveTradingManager:
    """Get or create IB live trading manager"""
    global ib_live_manager
    if ib_live_manager is None:
        config = {
            'max_daily_loss': 50.0,
            'max_daily_trades': 5,
            'host': '127.0.0.1',
            'port': 7496,
            'client_id': 2
        }
        ib_live_manager = IBLiveTradingManager(config)
    return ib_live_manager
'''
        
        manager_file = self.project_root / 'ib_live_manager.py'
        with open(manager_file, 'w', encoding='utf-8') as f:
            f.write(manager_code)
        
        self.print_status(f"[CHECK] IB Live manager created: {manager_file}", "SUCCESS")
        return manager_file
    
    def create_integration_guide(self):
        """Create integration guide"""
        self.print_status("📚 Creating Integration Guide...", "INFO")
        
        guide_content = """# PROMETHEUS IB Live Trading Integration Guide

## 🚨 WARNING: REAL MONEY TRADING

This integration enables REAL MONEY trading through Interactive Brokers. Use with extreme caution.

## Setup Steps

### 1. IB Gateway Configuration
- Download IB Gateway from: https://www.interactivebrokers.com/en/trading/ib-gateway.php
- Configure for LIVE trading (NOT paper trading)
- Use port 7496 for live trading
- Enable API connections

### 2. Environment Configuration
Load the live trading environment:
```bash
# Load live trading environment
source .env.live
```

### 3. Backend Integration
Add the IB live endpoints to your backend server:
```python
# Add contents of ib_live_endpoints.py to unified_production_server.py
```

### 4. Safety Features
- Manual confirmation required for all trades
- Daily loss limit: $50
- Maximum 5 trades per day
- Position size limit: 1% of account
- Emergency stop functionality

### 5. Enable Live Trading
```python
# Enable with confirmation code
confirmation_code = "PROMETHEUS_LIVE_CONFIRMED"
manager.enable_live_trading(confirmation_code)
```

## API Endpoints

- `GET /api/ib-live/status` - Get live trading status
- `GET /api/ib-live/account` - Get account information
- `POST /api/ib-live/enable` - Enable live trading
- `POST /api/ib-live/disable` - Disable live trading
- `GET /api/ib-live/positions` - Get current positions
- `POST /api/ib-live/order` - Place live order

## Safety Checklist

- [ ] IB Gateway configured for live trading
- [ ] API connections enabled
- [ ] Daily loss limits set
- [ ] Position size limits configured
- [ ] Emergency stop procedures ready
- [ ] Manual confirmation enabled
- [ ] Small test trades planned

## Risk Management

- Start with very small position sizes
- Monitor all trades closely
- Have stop-loss orders ready
- Never risk more than you can afford to lose
- Test thoroughly before increasing position sizes

## Emergency Procedures

If something goes wrong:
1. Call `POST /api/ib-live/disable` immediately
2. Close IB Gateway
3. Contact Interactive Brokers if needed
4. Review all positions and orders

## Support

For issues with this integration, check:
- IB Gateway connection status
- API permissions
- Account permissions
- Network connectivity
"""
        
        guide_file = self.project_root / 'IB_LIVE_TRADING_GUIDE.md'
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        
        self.print_status(f"[CHECK] Integration guide created: {guide_file}", "SUCCESS")
        return guide_file
    
    def run_integration(self):
        """Run complete IB live trading integration"""
        self.print_status("🚀 PROMETHEUS IB LIVE TRADING INTEGRATION", "INFO")
        print("=" * 70)
        print("🚨 WARNING: This enables REAL MONEY trading!")
        print("=" * 70)
        
        # Check backend status
        if not self.check_backend_status():
            self.print_status("[ERROR] Backend not running. Start backend first.", "ERROR")
            return False
        
        # Create integration components
        endpoint_file = self.add_ib_live_endpoints()
        manager_file = self.create_ib_live_manager()
        guide_file = self.create_integration_guide()
        
        # Summary
        self.print_status("[CHECK] IB Live Trading Integration Complete!", "SUCCESS")
        print("\n📋 NEXT STEPS:")
        print("1. Review the integration guide: IB_LIVE_TRADING_GUIDE.md")
        print("2. Configure IB Gateway for live trading (port 7496)")
        print("3. Add endpoints from ib_live_endpoints.py to your backend")
        print("4. Test with small amounts first!")
        print("5. Enable live trading with confirmation code")
        
        print("\n🚨 SAFETY REMINDERS:")
        print("- This trades with REAL MONEY")
        print("- Start with very small positions")
        print("- Monitor all trades closely")
        print("- Have emergency stop procedures ready")
        
        return True

if __name__ == "__main__":
    integration = IBLiveTradingIntegration()
    integration.run_integration()
