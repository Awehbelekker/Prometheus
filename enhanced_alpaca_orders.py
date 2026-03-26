#!/usr/bin/env python3
"""
🚀 ENHANCED ALPACA ORDER ENDPOINTS
Implementation of comprehensive order management from Alpaca docs

Features:
- All order types from Alpaca documentation
- Real-time order tracking
- Position management
- Asset validation
- Advanced order execution
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import json

# Pydantic models for order requests
class MarketOrderRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    qty: Optional[float] = Field(None, description="Quantity of shares")
    notional: Optional[float] = Field(None, description="Dollar amount")
    side: str = Field(..., description="buy or sell")
    time_in_force: str = Field(default="day", description="day, gtc, ioc, fok")
    client_order_id: Optional[str] = Field(None, description="Custom order ID")

class LimitOrderRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    qty: Optional[float] = Field(None, description="Quantity of shares")
    notional: Optional[float] = Field(None, description="Dollar amount")
    side: str = Field(..., description="buy or sell")
    limit_price: float = Field(..., description="Limit price")
    time_in_force: str = Field(default="day", description="day, gtc, ioc, fok")
    client_order_id: Optional[str] = Field(None, description="Custom order ID")

class TakeProfitRequest(BaseModel):
    limit_price: float = Field(..., description="Take profit price")

class StopLossRequest(BaseModel):
    stop_price: float = Field(..., description="Stop loss price")

class BracketOrderRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    qty: float = Field(..., description="Quantity of shares")
    side: str = Field(..., description="buy or sell")
    time_in_force: str = Field(default="day", description="day, gtc, ioc, fok")
    order_class: str = Field(default="bracket", description="bracket, oto")
    take_profit: Optional[TakeProfitRequest] = Field(None, description="Take profit order")
    stop_loss: Optional[StopLossRequest] = Field(None, description="Stop loss order")
    client_order_id: Optional[str] = Field(None, description="Custom order ID")

class TrailingStopOrderRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    qty: float = Field(..., description="Quantity of shares")
    side: str = Field(..., description="buy or sell")
    time_in_force: str = Field(default="gtc", description="day, gtc, ioc, fok")
    trail_percent: Optional[float] = Field(None, description="Trail percentage (0-100)")
    trail_price: Optional[float] = Field(None, description="Trail price in dollars")
    client_order_id: Optional[str] = Field(None, description="Custom order ID")

class OrdersFilterRequest(BaseModel):
    status: Optional[str] = Field(None, description="open, closed, all")
    limit: int = Field(default=50, description="Number of orders to return")
    after: Optional[datetime] = Field(None, description="Orders after this time")
    until: Optional[datetime] = Field(None, description="Orders before this time")
    nested: bool = Field(default=True, description="Include nested orders")

# Enhanced Order Management Router
def create_enhanced_orders_router(alpaca_service, auth_service):
    """Create enhanced orders router with all Alpaca documentation features"""
    router = APIRouter(prefix="/api/trading/alpaca/orders", tags=["Enhanced Orders"])

    @router.post("/market", summary="Place Market Order")
    async def place_market_order(
        order: MarketOrderRequest,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Place a market order (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Buy 0.023 shares of SPY
        - Market execution
        - Day time in force
        """
        try:
            order_data = {
                "symbol": order.symbol,
                "side": order.side,
                "type": "market",
                "time_in_force": order.time_in_force
            }
            
            # Add quantity or notional
            if order.qty is not None:
                order_data["qty"] = str(order.qty)
            elif order.notional is not None:
                order_data["notional"] = str(order.notional)
            else:
                raise HTTPException(status_code=400, detail="Must specify qty or notional")
            
            # Add client order ID if provided
            if order.client_order_id:
                order_data["client_order_id"] = order.client_order_id
            
            # Submit order via Alpaca service
            result = await alpaca_service.submit_order(order_data)
            
            return {
                "success": True,
                "order": result,
                "order_type": "market",
                "message": f"Market order for {order.symbol} submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Order submission failed: {str(e)}")

    @router.post("/limit", summary="Place Limit Order")
    async def place_limit_order(
        order: LimitOrderRequest,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Place a limit order (from Alpaca docs)
        
        Example from Alpaca documentation:
        - BTC/USD limit order
        - $4000 notional value
        - $17000 limit price
        - Fill-or-kill execution
        """
        try:
            order_data = {
                "symbol": order.symbol,
                "side": order.side,
                "type": "limit",
                "limit_price": str(order.limit_price),
                "time_in_force": order.time_in_force
            }
            
            # Add quantity or notional
            if order.qty is not None:
                order_data["qty"] = str(order.qty)
            elif order.notional is not None:
                order_data["notional"] = str(order.notional)
            else:
                raise HTTPException(status_code=400, detail="Must specify qty or notional")
            
            # Add client order ID if provided
            if order.client_order_id:
                order_data["client_order_id"] = order.client_order_id
            
            # Submit order via Alpaca service
            result = await alpaca_service.submit_order(order_data)
            
            return {
                "success": True,
                "order": result,
                "order_type": "limit",
                "limit_price": order.limit_price,
                "message": f"Limit order for {order.symbol} at ${order.limit_price} submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Limit order submission failed: {str(e)}")

    @router.post("/short", summary="Place Short Order")
    async def place_short_order(
        order: MarketOrderRequest,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Place a short order (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Short sell 1 share of SPY
        - Market execution
        - Good-till-canceled
        """
        try:
            if order.side.lower() != "sell":
                raise HTTPException(status_code=400, detail="Short orders must have side='sell'")
            
            order_data = {
                "symbol": order.symbol,
                "qty": str(order.qty) if order.qty else str(order.notional),
                "side": "sell",  # Short selling
                "type": "market",
                "time_in_force": order.time_in_force
            }
            
            # Add client order ID if provided
            if order.client_order_id:
                order_data["client_order_id"] = order.client_order_id
            
            # Submit order via Alpaca service
            result = await alpaca_service.submit_order(order_data)
            
            return {
                "success": True,
                "order": result,
                "order_type": "short",
                "message": f"Short order for {order.symbol} submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Short order submission failed: {str(e)}")

    @router.post("/bracket", summary="Place Bracket Order")
    async def place_bracket_order(
        order: BracketOrderRequest,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Place a bracket order (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Buy 5 shares of SPY
        - Take profit at $400
        - Stop loss at $300
        - Bracket order class
        """
        try:
            order_data = {
                "symbol": order.symbol,
                "qty": str(order.qty),
                "side": order.side,
                "type": "market",
                "time_in_force": order.time_in_force,
                "order_class": order.order_class
            }
            
            # Add take profit
            if order.take_profit:
                order_data["take_profit"] = {
                    "limit_price": str(order.take_profit.limit_price)
                }
            
            # Add stop loss
            if order.stop_loss:
                order_data["stop_loss"] = {
                    "stop_price": str(order.stop_loss.stop_price)
                }
            
            # Add client order ID if provided
            if order.client_order_id:
                order_data["client_order_id"] = order.client_order_id
            
            # Submit order via Alpaca service
            result = await alpaca_service.submit_order(order_data)
            
            return {
                "success": True,
                "order": result,
                "order_type": "bracket",
                "take_profit_price": order.take_profit.limit_price if order.take_profit else None,
                "stop_loss_price": order.stop_loss.stop_price if order.stop_loss else None,
                "message": f"Bracket order for {order.symbol} submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bracket order submission failed: {str(e)}")

    @router.post("/trailing-stop", summary="Place Trailing Stop Order")
    async def place_trailing_stop_order(
        order: TrailingStopOrderRequest,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Place a trailing stop order (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Sell 1 share of SPY
        - Trail by 1% or $1.00
        - Good-till-canceled
        """
        try:
            if not order.trail_percent and not order.trail_price:
                raise HTTPException(status_code=400, detail="Must specify trail_percent or trail_price")
            
            order_data = {
                "symbol": order.symbol,
                "qty": str(order.qty),
                "side": order.side,
                "type": "trailing_stop",
                "time_in_force": order.time_in_force
            }
            
            # Add trailing parameters
            if order.trail_percent:
                order_data["trail_percent"] = str(order.trail_percent)
            elif order.trail_price:
                order_data["trail_price"] = str(order.trail_price)
            
            # Add client order ID if provided
            if order.client_order_id:
                order_data["client_order_id"] = order.client_order_id
            
            # Submit order via Alpaca service
            result = await alpaca_service.submit_order(order_data)
            
            return {
                "success": True,
                "order": result,
                "order_type": "trailing_stop",
                "trail_percent": order.trail_percent,
                "trail_price": order.trail_price,
                "message": f"Trailing stop order for {order.symbol} submitted successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Trailing stop order submission failed: {str(e)}")

    @router.get("/", summary="Retrieve All Orders")
    async def get_all_orders(
        status: Optional[str] = Query(None, description="open, closed, all"),
        limit: int = Query(50, description="Number of orders to return"),
        after: Optional[str] = Query(None, description="Orders after this time (ISO format)"),
        until: Optional[str] = Query(None, description="Orders before this time (ISO format)"),
        nested: bool = Query(True, description="Include nested multi-leg orders"),
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Retrieve orders with filtering (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Get last 100 closed orders
        - Include nested multi-leg orders
        - Filter by status and time range
        """
        try:
            # Build query parameters
            params = {}
            if status:
                params["status"] = status
            if limit:
                params["limit"] = limit
            if after:
                params["after"] = after
            if until:
                params["until"] = until
            if nested:
                params["nested"] = str(nested).lower()
            
            # Get orders via Alpaca service
            orders = await alpaca_service.get_orders(params)
            
            return {
                "success": True,
                "orders": orders,
                "count": len(orders) if orders else 0,
                "filters": {
                    "status": status,
                    "limit": limit,
                    "nested": nested
                },
                "message": f"Retrieved {len(orders) if orders else 0} orders",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve orders: {str(e)}")

    @router.get("/by-client-id/{client_order_id}", summary="Get Order by Client ID")
    async def get_order_by_client_id(
        client_order_id: str,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Get order by client ID (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Retrieve order using custom client_order_id
        - Useful for tracking specific strategies
        """
        try:
            order = await alpaca_service.get_order_by_client_id(client_order_id)
            
            return {
                "success": True,
                "order": order,
                "client_order_id": client_order_id,
                "message": f"Order retrieved by client ID: {client_order_id}",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Order not found: {str(e)}")

    @router.get("/{order_id}", summary="Get Specific Order")
    async def get_order(
        order_id: str,
        current_user = Depends(auth_service.get_current_user)
    ):
        """Get specific order by ID"""
        try:
            order = await alpaca_service.get_order(order_id)
            
            return {
                "success": True,
                "order": order,
                "order_id": order_id,
                "message": f"Order {order_id} retrieved successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Order not found: {str(e)}")

    @router.delete("/{order_id}", summary="Cancel Order")
    async def cancel_order(
        order_id: str,
        current_user = Depends(auth_service.get_current_user)
    ):
        """Cancel an open order"""
        try:
            result = await alpaca_service.cancel_order(order_id)
            
            return {
                "success": True,
                "result": result,
                "order_id": order_id,
                "message": f"Order {order_id} cancelled successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

    @router.post("/cancel-all", summary="Cancel All Orders")
    async def cancel_all_orders(
        current_user = Depends(auth_service.get_current_user)
    ):
        """Cancel all open orders"""
        try:
            result = await alpaca_service.cancel_all_orders()
            
            return {
                "success": True,
                "result": result,
                "message": "All orders cancelled successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to cancel all orders: {str(e)}")

    return router

# Enhanced Positions Router
def create_enhanced_positions_router(alpaca_service, auth_service):
    """Create enhanced positions router with Alpaca documentation features"""
    router = APIRouter(prefix="/api/trading/alpaca/positions", tags=["Enhanced Positions"])

    @router.get("/", summary="Get All Positions")
    async def get_all_positions(
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Get all open positions (from Alpaca docs)
        
        Example from Alpaca documentation:
        - List all positions
        - Show quantity and market value
        - Real-time price updates
        """
        try:
            positions = await alpaca_service.get_positions()
            
            # Add summary statistics
            total_positions = len(positions) if positions else 0
            total_market_value = sum(
                float(pos.get('market_value', 0)) for pos in (positions or [])
            )
            total_unrealized_pl = sum(
                float(pos.get('unrealized_pl', 0)) for pos in (positions or [])
            )
            
            return {
                "success": True,
                "positions": positions,
                "summary": {
                    "total_positions": total_positions,
                    "total_market_value": total_market_value,
                    "total_unrealized_pl": total_unrealized_pl
                },
                "message": f"Retrieved {total_positions} positions",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve positions: {str(e)}")

    @router.get("/{symbol}", summary="Get Position for Symbol")
    async def get_position(
        symbol: str,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Get position for specific symbol (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Get AAPL position
        - Show detailed position info
        """
        try:
            position = await alpaca_service.get_position(symbol)
            
            return {
                "success": True,
                "position": position,
                "symbol": symbol,
                "message": f"Position for {symbol} retrieved successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Position not found: {str(e)}")

    @router.delete("/{symbol}", summary="Close Position")
    async def close_position(
        symbol: str,
        qty: Optional[str] = Query(None, description="Quantity to close (optional)"),
        percentage: Optional[str] = Query(None, description="Percentage to close (optional)"),
        current_user = Depends(auth_service.get_current_user)
    ):
        """Close position for specific symbol"""
        try:
            result = await alpaca_service.close_position(symbol, qty, percentage)
            
            return {
                "success": True,
                "result": result,
                "symbol": symbol,
                "message": f"Position for {symbol} closed successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to close position: {str(e)}")

    @router.delete("/", summary="Close All Positions")
    async def close_all_positions(
        cancel_orders: bool = Query(True, description="Cancel open orders"),
        current_user = Depends(auth_service.get_current_user)
    ):
        """Close all open positions"""
        try:
            result = await alpaca_service.close_all_positions(cancel_orders)
            
            return {
                "success": True,
                "result": result,
                "cancel_orders": cancel_orders,
                "message": "All positions closed successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to close all positions: {str(e)}")

    return router

# Enhanced Assets Router
def create_enhanced_assets_router(alpaca_service, auth_service):
    """Create enhanced assets router with Alpaca documentation features"""
    router = APIRouter(prefix="/api/trading/alpaca/assets", tags=["Enhanced Assets"])

    @router.get("/", summary="Get All Assets")
    async def get_all_assets(
        asset_class: Optional[str] = Query(None, description="us_equity, crypto"),
        status: Optional[str] = Query("active", description="active, inactive"),
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Get list of assets (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Search for US equities
        - Filter by asset class
        - Check tradability
        """
        try:
            params = {}
            if asset_class:
                params["asset_class"] = asset_class
            if status:
                params["status"] = status
            
            assets = await alpaca_service.get_assets(params)
            
            return {
                "success": True,
                "assets": assets[:100] if assets else [],  # Limit to first 100
                "count": len(assets) if assets else 0,
                "filters": {
                    "asset_class": asset_class,
                    "status": status
                },
                "message": f"Retrieved {len(assets) if assets else 0} assets",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve assets: {str(e)}")

    @router.get("/{symbol}", summary="Get Asset Information")
    async def get_asset(
        symbol: str,
        current_user = Depends(auth_service.get_current_user)
    ):
        """
        Get asset information (from Alpaca docs)
        
        Example from Alpaca documentation:
        - Check if AAPL is tradable
        - Get asset details
        - Validate before trading
        """
        try:
            asset = await alpaca_service.get_asset(symbol)
            
            # Add trading recommendation
            trading_recommendation = "[CHECK] Tradable" if asset.get('tradable') else "[ERROR] Not tradable"
            shortable_status = "[CHECK] Shortable" if asset.get('shortable') else "[ERROR] Not shortable"
            
            return {
                "success": True,
                "asset": asset,
                "symbol": symbol,
                "trading_info": {
                    "tradable": asset.get('tradable', False),
                    "shortable": asset.get('shortable', False),
                    "easy_to_borrow": asset.get('easy_to_borrow', False),
                    "recommendation": trading_recommendation,
                    "shortable_status": shortable_status
                },
                "message": f"Asset information for {symbol} retrieved successfully",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Asset not found: {str(e)}")

    return router
