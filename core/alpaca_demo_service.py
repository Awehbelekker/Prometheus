#!/usr/bin/env python3
"""
🚀 Demo Alpaca Trading Integration
PROMETHEUS Trading Platform - Demo Mode with Simulated Trading
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
from decimal import Decimal
import random

class AlpacaTradingServiceDemo:
    """
    🎯 Alpaca Markets Integration (Demo Mode)
    Provides realistic demo trading functionality
    """
    
    def __init__(self, use_paper_trading: bool = True):
        self.use_paper_trading = use_paper_trading
        self.logger = logging.getLogger(__name__)
        
        # Demo account data
        self.demo_account = {
            "id": "demo-account-12345",
            "status": "ACTIVE",
            "buying_power": 100000.00,
            "cash": 100000.00,
            "portfolio_value": 100000.00,
            "equity": 100000.00,
            "last_equity": 100000.00,
            "multiplier": 1,
            "currency": "USD"
        }
        
        # Demo positions
        self.demo_positions = [
            {
                "symbol": "AAPL",
                "qty": 10,
                "market_value": 1500.00,
                "avg_entry_price": 150.00,
                "unrealized_pl": 50.00,
                "side": "long"
            },
            {
                "symbol": "TSLA", 
                "qty": 5,
                "market_value": 1000.00,
                "avg_entry_price": 200.00,
                "unrealized_pl": -25.00,
                "side": "long"
            }
        ]
        
        # Demo orders
        self.demo_orders = []
        
        self.logger.info("🎭 Using Alpaca Demo Mode - All trading is simulated")
        
    def is_available(self) -> bool:
        """Check if Alpaca service is available"""
        return True
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        self.logger.info("📊 Fetching demo account info")
        return {
            "account_id": self.demo_account["id"],
            "status": self.demo_account["status"],
            "buying_power": self.demo_account["buying_power"],
            "cash": self.demo_account["cash"],
            "portfolio_value": self.demo_account["portfolio_value"],
            "equity": self.demo_account["equity"],
            "last_equity": self.demo_account["last_equity"],
            "multiplier": self.demo_account["multiplier"],
            "currency": self.demo_account["currency"],
            "demo_mode": True
        }
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        self.logger.info("📈 Fetching demo positions")
        return [
            {
                "symbol": pos["symbol"],
                "qty": pos["qty"],
                "market_value": pos["market_value"],
                "avg_entry_price": pos["avg_entry_price"],
                "unrealized_pl": pos["unrealized_pl"],
                "unrealized_plpc": pos["unrealized_pl"] / (pos["avg_entry_price"] * pos["qty"]),
                "side": pos["side"],
                "demo_mode": True
            }
            for pos in self.demo_positions
        ]
    
    def place_order(self, 
                   symbol: str,
                   qty: int,
                   side: str,
                   order_type: str = "market",
                   time_in_force: str = "day",
                   limit_price: Optional[float] = None,
                   stop_price: Optional[float] = None) -> Dict[str, Any]:
        """Place a demo order"""
        
        order_id = f"demo-order-{len(self.demo_orders) + 1}"
        
        # Simulate realistic price
        if limit_price:
            filled_price = limit_price
        else:
            # Simulate market price with some randomness
            base_prices = {"AAPL": 150, "TSLA": 200, "GOOGL": 100, "MSFT": 300}
            base_price = base_prices.get(symbol, 100)
            filled_price = base_price + random.uniform(-5, 5)
        
        order = {
            "id": order_id,
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "order_type": order_type,
            "time_in_force": time_in_force,
            "limit_price": limit_price,
            "stop_price": stop_price,
            "status": "filled",
            "filled_qty": qty,
            "filled_avg_price": filled_price,
            "filled_at": datetime.now().isoformat(),
            "submitted_at": datetime.now().isoformat(),
            "demo_mode": True
        }
        
        self.demo_orders.append(order)
        
        # Update demo account based on order
        total_cost = filled_price * qty
        if side == "buy":
            self.demo_account["cash"] -= total_cost
            # Add to positions or update existing position
            existing_pos = next((p for p in self.demo_positions if p["symbol"] == symbol), None)
            if existing_pos:
                # Update existing position
                total_qty = existing_pos["qty"] + qty
                total_value = (existing_pos["avg_entry_price"] * existing_pos["qty"]) + total_cost
                existing_pos["avg_entry_price"] = total_value / total_qty
                existing_pos["qty"] = total_qty
                existing_pos["market_value"] = total_qty * filled_price
            else:
                # New position
                self.demo_positions.append({
                    "symbol": symbol,
                    "qty": qty,
                    "market_value": total_cost,
                    "avg_entry_price": filled_price,
                    "unrealized_pl": 0.00,
                    "side": "long"
                })
        
        self.logger.info(f"🎯 Demo order placed: {side.upper()} {qty} {symbol} @ ${filled_price:.2f}")
        
        return order
    
    def get_orders(self, status: str = "all") -> List[Dict[str, Any]]:
        """Get order history"""
        self.logger.info("📋 Fetching demo orders")
        if status == "all":
            return self.demo_orders
        else:
            return [order for order in self.demo_orders if order["status"] == status]
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        order = next((o for o in self.demo_orders if o["id"] == order_id), None)
        if order and order["status"] in ["new", "pending_new", "accepted"]:
            order["status"] = "canceled"
            self.logger.info(f"🚫 Demo order canceled: {order_id}")
            return {"success": True, "message": "Order canceled", "demo_mode": True}
        else:
            return {"success": False, "message": "Order not found or cannot be canceled", "demo_mode": True}
    
    def get_portfolio_history(self, period: str = "1D") -> Dict[str, Any]:
        """Get portfolio performance history"""
        self.logger.info("📊 Fetching demo portfolio history")
        
        # Generate demo portfolio history
        timestamps = []
        equity_values = []
        
        start_time = datetime.now() - timedelta(days=30)
        for i in range(30):
            timestamp = start_time + timedelta(days=i)
            timestamps.append(timestamp.isoformat())
            
            # Simulate portfolio growth with some volatility
            base_value = 100000
            growth = i * 100  # $100 growth per day on average
            volatility = random.uniform(-500, 500)  # Random daily volatility
            equity_values.append(base_value + growth + volatility)
        
        return {
            "timeframe": period,
            "timestamp": timestamps,
            "equity": equity_values,
            "profit_loss": [eq - 100000 for eq in equity_values],
            "profit_loss_pct": [(eq - 100000) / 100000 for eq in equity_values],
            "base_value": 100000,
            "demo_mode": True
        }
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get market data for a symbol"""
        self.logger.info(f"📈 Fetching demo market data for {symbol}")
        
        # Simulate market data
        base_prices = {"AAPL": 150, "TSLA": 200, "GOOGL": 100, "MSFT": 300}
        base_price = base_prices.get(symbol, 100)
        
        current_price = base_price + random.uniform(-10, 10)
        prev_close = current_price + random.uniform(-5, 5)
        
        return {
            "symbol": symbol,
            "price": current_price,
            "prev_close": prev_close,
            "change": current_price - prev_close,
            "change_percent": ((current_price - prev_close) / prev_close) * 100,
            "volume": random.randint(1000000, 10000000),
            "timestamp": datetime.now().isoformat(),
            "demo_mode": True
        }

# Create an alias for backward compatibility
AlpacaTradingService = AlpacaTradingServiceDemo
