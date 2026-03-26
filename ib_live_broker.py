"""
Interactive Brokers Live Trading Broker for PROMETHEUS
WARNING: This trades with REAL MONEY!
"""
import asyncio
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order as IBOrder
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False

logger = logging.getLogger(__name__)

class IBLiveTradingBroker:
    """Interactive Brokers Live Trading Implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        if not IB_AVAILABLE:
            raise ImportError("IB API required for live trading")
        
        self.config = config
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('live_port', 7496)  # Live trading port
        self.client_id = config.get('client_id', 2)
        self.account_id = config.get('account_id')
        
        # Live trading safety checks
        self.live_trading_enabled = False
        self.confirmation_required = True
        self.max_daily_loss = config.get('max_daily_loss_dollars', 50.0)
        self.daily_pnl = 0.0
        
        # Initialize IB components
        self.wrapper = IBLiveWrapper(self)
        self.client = EClient(self.wrapper)
        self.connected = False
        
        logger.warning("🚨 LIVE TRADING BROKER INITIALIZED - REAL MONEY AT RISK!")
    
    async def connect(self) -> bool:
        """Connect to IB Gateway for live trading"""
        logger.warning(f"🚨 Connecting to IB LIVE trading on port {self.port}")
        
        try:
            self.client.connect(self.host, self.port, self.client_id)
            
            # Start API thread
            api_thread = threading.Thread(target=self.client.run, daemon=True)
            api_thread.start()
            
            # Wait for connection
            timeout = 15
            start_time = time.time()
            while not self.client.isConnected() and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.client.isConnected():
                self.connected = True
                logger.warning("🚨 CONNECTED TO LIVE TRADING - REAL MONEY MODE ACTIVE!")
                return True
            else:
                logger.error("[ERROR] Failed to connect to IB live trading")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Live trading connection error: {e}")
            return False
    
    def enable_live_trading(self, confirmation_code: str):
        """Enable live trading with confirmation"""
        if confirmation_code == "PROMETHEUS_LIVE_CONFIRMED":
            self.live_trading_enabled = True
            logger.warning("🚨 LIVE TRADING ENABLED - REAL MONEY TRADES ACTIVE!")
            return True
        else:
            logger.error("[ERROR] Invalid confirmation code for live trading")
            return False
    
    async def place_live_order(self, symbol: str, quantity: int, order_type: str = "MKT"):
        """Place live order with safety checks"""
        if not self.live_trading_enabled:
            logger.error("[ERROR] Live trading not enabled")
            return None
        
        if abs(self.daily_pnl) >= self.max_daily_loss:
            logger.error(f"[ERROR] Daily loss limit reached: ${self.daily_pnl}")
            return None
        
        logger.warning(f"🚨 PLACING LIVE ORDER: {symbol} x {quantity} ({order_type})")
        
        # Additional safety confirmation for live orders
        if self.confirmation_required:
            logger.warning("[WARNING]️ Live order requires manual confirmation")
            return None
        
        # Implement actual order placement here
        return await self._execute_live_order(symbol, quantity, order_type)

class IBLiveWrapper(EWrapper):
    """IB API Wrapper for live trading"""
    
    def __init__(self, broker):
        self.broker = broker
    
    def error(self, reqId, errorCode, errorString, advancedOrderRejectJson=""):
        logger.error(f"IB Live Error {errorCode}: {errorString}")
    
    def nextValidId(self, orderId):
        self.broker.next_order_id = orderId
        logger.info(f"Next valid order ID: {orderId}")
