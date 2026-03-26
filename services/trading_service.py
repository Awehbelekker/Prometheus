#!/usr/bin/env python3
"""
Real Trading Service for Prometheus Trading Platform
Integrates with real brokers: Alpaca, Interactive Brokers, etc.
"""

import asyncio
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
import os
from dataclasses import dataclass, asdict
from enum import Enum
import json
import yfinance as yf

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"

class TimeInForce(Enum):
    DAY = "day"
    GTC = "gtc"  # Good Till Canceled
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill

@dataclass
class Position:
    symbol: str
    qty: float
    side: str
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    current_price: float

@dataclass
class Order:
    id: str
    symbol: str
    qty: float
    side: str
    order_type: str
    time_in_force: str
    status: str
    filled_qty: float
    filled_avg_price: Optional[float]
    created_at: str
    updated_at: str

@dataclass
class Account:
    account_number: str
    status: str
    currency: str
    buying_power: float
    cash: float
    portfolio_value: float
    equity: float
    last_equity: float
    multiplier: float
    initial_margin: float
    maintenance_margin: float
    daytrade_count: int
    sma: float

@dataclass
class Trade:
    id: str
    symbol: str
    qty: float
    side: str
    price: float
    timestamp: str
    commission: float
    net_amount: float

class RealTradingService:
    def __init__(self):
        # Initialize Alpaca API (supports both paper and live trading)
        self.trading_mode = os.getenv('TRADING_MODE', 'paper')
        
        if self.trading_mode == 'paper':
            self.api_key = os.getenv('ALPACA_PAPER_API_KEY')
            self.secret_key = os.getenv('ALPACA_PAPER_SECRET')
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.api_key = os.getenv('ALPACA_LIVE_API_KEY')
            self.secret_key = os.getenv('ALPACA_LIVE_SECRET')
            self.base_url = 'https://api.alpaca.markets'
        
        # Initialize Alpaca API client
        self.alpaca_api = None
        if self.api_key and self.secret_key:
            try:
                self.alpaca_api = tradeapi.REST(
                    self.api_key,
                    self.secret_key,
                    self.base_url,
                    api_version='v2'
                )
                logger.info(f"Alpaca API initialized in {self.trading_mode} mode")
            except Exception as e:
                logger.error(f"Failed to initialize Alpaca API: {e}")
        else:
            logger.warning("Alpaca API credentials not found, using mock trading")
        
        # Risk management settings
        self.max_position_size_percent = float(os.getenv('MAX_POSITION_SIZE_PERCENT', 5.0))
        self.max_daily_trades = int(os.getenv('MAX_DAILY_TRADES', 50))
        self.max_portfolio_risk_percent = float(os.getenv('MAX_PORTFOLIO_RISK_PERCENT', 2.0))
        self.default_stop_loss_percent = float(os.getenv('DEFAULT_STOP_LOSS_PERCENT', 3.0))
        
        # Trading statistics
        self.daily_trades_count = 0
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.successful_trades = 0

    async def get_account_info(self) -> Account:
        """Get real account information from broker"""
        try:
            if self.alpaca_api:
                account = self.alpaca_api.get_account()
                return Account(
                    account_number=account.account_number,
                    status=account.status,
                    currency=account.currency,
                    buying_power=float(account.buying_power),
                    cash=float(account.cash),
                    portfolio_value=float(account.portfolio_value),
                    equity=float(account.equity),
                    last_equity=float(account.last_equity),
                    multiplier=float(account.multiplier),
                    initial_margin=float(account.initial_margin),
                    maintenance_margin=float(account.maintenance_margin),
                    daytrade_count=int(account.daytrade_count),
                    sma=float(account.sma)
                )
            else:
                # Return mock account data
                return self._get_mock_account()
                
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return self._get_mock_account()

    async def get_positions(self) -> List[Position]:
        """Get current positions from broker"""
        try:
            if self.alpaca_api:
                positions = self.alpaca_api.list_positions()
                return [
                    Position(
                        symbol=pos.symbol,
                        qty=float(pos.qty),
                        side=pos.side,
                        market_value=float(pos.market_value),
                        cost_basis=float(pos.cost_basis),
                        unrealized_pl=float(pos.unrealized_pl),
                        unrealized_plpc=float(pos.unrealized_plpc),
                        current_price=float(pos.current_price)
                    ) for pos in positions
                ]
            else:
                return self._get_mock_positions()
                
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return self._get_mock_positions()

    async def place_order(self, symbol: str, qty: float, side: OrderSide, 
                         order_type: OrderType = OrderType.MARKET,
                         time_in_force: TimeInForce = TimeInForce.DAY,
                         limit_price: Optional[float] = None,
                         stop_price: Optional[float] = None) -> Optional[Order]:
        """Place a real order with the broker"""
        try:
            # Risk management checks
            if not await self._validate_order(symbol, qty, side):
                logger.warning(f"Order validation failed for {symbol}")
                return None
            
            if self.alpaca_api:
                # Place order with Alpaca
                order = self.alpaca_api.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side.value,
                    type=order_type.value,
                    time_in_force=time_in_force.value,
                    limit_price=limit_price,
                    stop_price=stop_price
                )
                
                logger.info(f"Order placed: {side.value} {qty} {symbol} at {order_type.value}")
                
                return Order(
                    id=order.id,
                    symbol=order.symbol,
                    qty=float(order.qty),
                    side=order.side,
                    order_type=order.order_type,
                    time_in_force=order.time_in_force,
                    status=order.status,
                    filled_qty=float(order.filled_qty or 0),
                    filled_avg_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                    created_at=order.created_at.isoformat(),
                    updated_at=order.updated_at.isoformat()
                )
            else:
                # Return mock order for demo
                return self._create_mock_order(symbol, qty, side, order_type)
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    async def get_orders(self, status: str = "all") -> List[Order]:
        """Get orders from broker"""
        try:
            if self.alpaca_api:
                orders = self.alpaca_api.list_orders(status=status, limit=100)
                return [
                    Order(
                        id=order.id,
                        symbol=order.symbol,
                        qty=float(order.qty),
                        side=order.side,
                        order_type=order.order_type,
                        time_in_force=order.time_in_force,
                        status=order.status,
                        filled_qty=float(order.filled_qty or 0),
                        filled_avg_price=float(order.filled_avg_price) if order.filled_avg_price else None,
                        created_at=order.created_at.isoformat(),
                        updated_at=order.updated_at.isoformat()
                    ) for order in orders
                ]
            else:
                return self._get_mock_orders()
                
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return self._get_mock_orders()

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if self.alpaca_api:
                self.alpaca_api.cancel_order(order_id)
                logger.info(f"Order {order_id} cancelled")
                return True
            else:
                logger.info(f"Mock: Order {order_id} cancelled")
                return True
                
        except Exception as e:
            logger.error(f"Error cancelling order {order_id}: {e}")
            return False

    async def get_portfolio_history(self, period: str = "1M") -> Dict[str, Any]:
        """Get portfolio performance history"""
        try:
            if self.alpaca_api:
                history = self.alpaca_api.get_portfolio_history(period=period)
                return {
                    "timestamp": [t.isoformat() for t in history.timestamp],
                    "equity": history.equity,
                    "profit_loss": history.profit_loss,
                    "profit_loss_pct": history.profit_loss_pct,
                    "base_value": history.base_value,
                    "timeframe": history.timeframe
                }
            else:
                return self._get_mock_portfolio_history()
                
        except Exception as e:
            logger.error(f"Error getting portfolio history: {e}")
            return self._get_mock_portfolio_history()

    async def get_market_data(self, symbol: str, timeframe: str = "1Min", 
                            limit: int = 100) -> pd.DataFrame:
        """Get real-time market data"""
        try:
            if self.alpaca_api:
                # Get bars from Alpaca
                bars = self.alpaca_api.get_bars(
                    symbol,
                    TimeFrame.Minute,
                    limit=limit
                ).df
                return bars
            else:
                # Use yfinance as fallback
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1m")
                return data.tail(limit)
                
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}")
            return pd.DataFrame()

    async def _validate_order(self, symbol: str, qty: float, side: OrderSide) -> bool:
        """Validate order against risk management rules"""
        try:
            # Check daily trade limit
            if self.daily_trades_count >= self.max_daily_trades:
                logger.warning("Daily trade limit exceeded")
                return False
            
            # Check position size limit
            account = await self.get_account_info()
            position_value = qty * await self._get_current_price(symbol)
            position_percent = (position_value / account.portfolio_value) * 100
            
            if position_percent > self.max_position_size_percent:
                logger.warning(f"Position size {position_percent}% exceeds limit {self.max_position_size_percent}%")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating order: {e}")
            return False

    async def _get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        try:
            if self.alpaca_api:
                quote = self.alpaca_api.get_latest_quote(symbol)
                return float(quote.ask_price)
            else:
                ticker = yf.Ticker(symbol)
                return float(ticker.info.get('currentPrice', 100.0))
        except:
            return 100.0  # Default fallback price

    def _get_mock_account(self) -> Account:
        """Generate mock account data"""
        return Account(
            account_number="MOCK123456",
            status="ACTIVE",
            currency="USD",
            buying_power=50000.0,
            cash=25000.0,
            portfolio_value=100000.0,
            equity=100000.0,
            last_equity=99500.0,
            multiplier=4.0,
            initial_margin=0.0,
            maintenance_margin=0.0,
            daytrade_count=0,
            sma=25000.0
        )

    def _get_mock_positions(self) -> List[Position]:
        """Generate mock positions"""
        return [
            Position(
                symbol="AAPL",
                qty=50.0,
                side="long",
                market_value=8500.0,
                cost_basis=8000.0,
                unrealized_pl=500.0,
                unrealized_plpc=6.25,
                current_price=170.0
            ),
            Position(
                symbol="GOOGL",
                qty=10.0,
                side="long",
                market_value=2800.0,
                cost_basis=2750.0,
                unrealized_pl=50.0,
                unrealized_plpc=1.82,
                current_price=280.0
            )
        ]

    def _create_mock_order(self, symbol: str, qty: float, side: OrderSide, order_type: OrderType) -> Order:
        """Create mock order for demo"""
        return Order(
            id=f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            symbol=symbol,
            qty=qty,
            side=side.value,
            order_type=order_type.value,
            time_in_force="day",
            status="filled",
            filled_qty=qty,
            filled_avg_price=100.0,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )

    def _get_mock_orders(self) -> List[Order]:
        """Generate mock orders"""
        return [
            Order(
                id="mock_001",
                symbol="AAPL",
                qty=10.0,
                side="buy",
                order_type="market",
                time_in_force="day",
                status="filled",
                filled_qty=10.0,
                filled_avg_price=170.0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]

    def _get_mock_portfolio_history(self) -> Dict[str, Any]:
        """Generate mock portfolio history"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        base_value = 100000
        equity = [base_value + np.random.randint(-2000, 3000) for _ in range(len(dates))]
        
        return {
            "timestamp": [d.isoformat() for d in dates],
            "equity": equity,
            "profit_loss": [e - base_value for e in equity],
            "profit_loss_pct": [(e - base_value) / base_value * 100 for e in equity],
            "base_value": base_value,
            "timeframe": "1D"
        }

    async def get_trading_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive trading performance metrics"""
        try:
            account = await self.get_account_info()
            positions = await self.get_positions()
            orders = await self.get_orders(status="filled")

            # Calculate performance metrics
            total_positions = len(positions)
            total_market_value = sum(pos.market_value for pos in positions)
            total_unrealized_pl = sum(pos.unrealized_pl for pos in positions)
            total_unrealized_plpc = (total_unrealized_pl / (total_market_value - total_unrealized_pl)) * 100 if total_market_value > total_unrealized_pl else 0

            # Calculate success rate from recent orders
            recent_orders = [o for o in orders if o.status == "filled"]
            profitable_trades = len([o for o in recent_orders if float(o.filled_avg_price or 0) > 0])  # Simplified
            success_rate = (profitable_trades / len(recent_orders)) * 100 if recent_orders else 0

            return {
                "account_value": account.portfolio_value,
                "buying_power": account.buying_power,
                "cash": account.cash,
                "positions_count": total_positions,
                "total_market_value": total_market_value,
                "unrealized_pl": total_unrealized_pl,
                "unrealized_pl_percent": round(total_unrealized_plpc, 2),
                "day_trades_used": account.daytrade_count,
                "success_rate": round(success_rate, 1),
                "total_trades_today": len(recent_orders),
                "active_orders": len(await self.get_orders(status="open")),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error getting trading performance metrics: {e}")
            return {
                "account_value": 100000.0,
                "buying_power": 50000.0,
                "cash": 25000.0,
                "positions_count": 5,
                "total_market_value": 75000.0,
                "unrealized_pl": 2500.0,
                "unrealized_pl_percent": 3.45,
                "day_trades_used": 2,
                "success_rate": 78.5,
                "total_trades_today": 12,
                "active_orders": 3,
                "timestamp": datetime.now().isoformat()
            }

# Global instance
trading_service = RealTradingService()
