"""
Universal Broker Interface for PROMETHEUS Trading Platform
Supports multiple brokers: Alpaca, Interactive Brokers, etc.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class OrderStatus(Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass
class Order:
    """Universal order representation"""
    symbol: str
    quantity: float
    side: OrderSide
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    limit_price: Optional[float] = None
    time_in_force: str = "day"
    order_id: Optional[str] = None
    broker_order_id: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_price: Optional[float] = None
    filled_quantity: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class Position:
    """Universal position representation"""
    symbol: str
    quantity: float
    avg_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    side: str  # "long" or "short"

@dataclass
class Account:
    """Universal account representation"""
    account_id: str
    buying_power: float
    cash: float
    portfolio_value: float
    equity: float
    day_trade_count: int
    pattern_day_trader: bool

class BrokerInterface(ABC):
    """Abstract base class for all broker implementations"""
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the broker"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the broker"""
        pass
    
    @abstractmethod
    async def get_account(self) -> Account:
        """Get account information"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Position]:
        """Get all positions"""
        pass
    
    @abstractmethod
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        pass
    
    @abstractmethod
    async def submit_order(self, order: Order) -> Order:
        """Submit an order"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        pass
    
    @abstractmethod
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        pass
    
    @abstractmethod
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders, optionally filtered by status"""
        pass
    
    @abstractmethod
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data"""
        pass
    
    @abstractmethod
    async def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical market data"""
        pass

class BrokerManager:
    """Manages multiple broker connections"""
    
    def __init__(self):
        self.brokers: Dict[str, BrokerInterface] = {}
        self.primary_broker: Optional[str] = None
        
    def register_broker(self, name: str, broker: BrokerInterface, is_primary: bool = False):
        """Register a broker"""
        self.brokers[name] = broker
        if is_primary or not self.primary_broker:
            self.primary_broker = name
        logger.info(f"[CHECK] Registered broker: {name} {'(Primary)' if is_primary else ''}")
    
    def get_broker(self, name: Optional[str] = None) -> Optional[BrokerInterface]:
        """Get broker by name, or primary if none specified"""
        if name:
            return self.brokers.get(name)
        elif self.primary_broker:
            return self.brokers.get(self.primary_broker)
        return None
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all registered brokers"""
        results = {}
        for name, broker in self.brokers.items():
            try:
                results[name] = await broker.connect()
                logger.info(f"[CHECK] Connected to {name}")
            except Exception as e:
                results[name] = False
                logger.error(f"[ERROR] Failed to connect to {name}: {e}")
        return results
    
    async def disconnect_all(self):
        """Disconnect from all brokers"""
        for name, broker in self.brokers.items():
            try:
                await broker.disconnect()
                logger.info(f"[CHECK] Disconnected from {name}")
            except Exception as e:
                logger.error(f"[ERROR] Error disconnecting from {name}: {e}")
    
    async def submit_order(self, order: Order, broker_name: Optional[str] = None) -> Order:
        """Submit order to specified broker or primary"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise ValueError(f"Broker not found: {broker_name or 'primary'}")
        return await broker.submit_order(order)
    
    async def get_account(self, broker_name: Optional[str] = None) -> Account:
        """Get account from specified broker or primary"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise ValueError(f"Broker not found: {broker_name or 'primary'}")
        return await broker.get_account()
    
    async def get_positions(self, broker_name: Optional[str] = None) -> List[Position]:
        """Get positions from specified broker or primary"""
        broker = self.get_broker(broker_name)
        if not broker:
            raise ValueError(f"Broker not found: {broker_name or 'primary'}")
        return await broker.get_positions()
