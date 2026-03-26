# Trading Endpoints for Prometheus Trading Platform
# Alpaca Trading Integration Endpoints

import os
import logging
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Depends
from core.alpaca_trading_service import AlpacaTradingService

logger = logging.getLogger(__name__)

# Global Alpaca service instances
_alpaca_paper = None
_alpaca_live = None

def get_alpaca_service(use_paper: bool = True):
    """Get Alpaca trading service instance"""
    global _alpaca_paper, _alpaca_live

    if use_paper:
        if _alpaca_paper is None:
            _alpaca_paper = AlpacaTradingService(use_paper=True)
        return _alpaca_paper
    else:
        if _alpaca_live is None:
            _alpaca_live = AlpacaTradingService(use_paper=False)
        return _alpaca_live

# Environment variables for ALWAYS_LIVE mode
ALWAYS_LIVE = os.getenv('ALWAYS_LIVE', '0').lower() in ('1', 'true', 'yes')
ENABLE_LIVE_ORDER_EXECUTION = os.getenv('ENABLE_LIVE_ORDER_EXECUTION', '0').lower() in ('1', 'true', 'yes')

# Alpaca Trading Endpoints

@app.get("/api/trading/alpaca/account")
async def get_alpaca_account(current_user: dict = Depends(require_authenticated_user)):
    """Get Alpaca account information"""
    try:
        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        account_info = await alpaca_service.get_account_info()
        return {
            "success": True,
            "account": account_info,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE
        }

    except Exception as e:
        logger.error(f"Alpaca account error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get account: {str(e)}")

@app.get("/api/trading/alpaca/positions")
async def get_alpaca_positions(current_user: dict = Depends(require_authenticated_user)):
    """Get Alpaca positions"""
    try:
        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        positions = await alpaca_service.get_positions()
        return {
            "success": True,
            "positions": positions,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE
        }

    except Exception as e:
        logger.error(f"Alpaca positions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get positions: {str(e)}")

@app.get("/api/trading/alpaca/orders")
async def get_alpaca_orders(status: str = "all", current_user: dict = Depends(require_authenticated_user)):
    """Get Alpaca orders"""
    try:
        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        orders = await alpaca_service.get_orders(status=status)
        return {
            "success": True,
            "orders": orders,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE
        }

    except Exception as e:
        logger.error(f"Alpaca orders error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get orders: {str(e)}")

@app.post("/api/trading/alpaca/order")
async def place_alpaca_order(order_data: Dict[str, Any], current_user: dict = Depends(require_authenticated_user)):
    """Place Alpaca order"""
    try:
        # Safety guard: Block live order execution unless explicitly enabled
        if not ENABLE_LIVE_ORDER_EXECUTION and not ALWAYS_LIVE:
            raise HTTPException(
                status_code=403,
                detail="Live order execution is disabled. Set ENABLE_LIVE_ORDER_EXECUTION=1 to enable."
            )

        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        # Extract order parameters
        symbol = order_data.get("symbol")
        qty = order_data.get("qty")
        side = order_data.get("side")
        order_type = order_data.get("type", "market")
        time_in_force = order_data.get("time_in_force", "day")
        limit_price = order_data.get("limit_price")
        stop_price = order_data.get("stop_price")

        if not all([symbol, qty, side]):
            raise HTTPException(status_code=400, detail="Missing required order parameters")

        order = await alpaca_service.place_order(
            symbol=symbol,
            qty=qty,
            side=side,
            order_type=order_type,
            time_in_force=time_in_force,
            limit_price=limit_price,
            stop_price=stop_price
        )

        return {
            "success": True,
            "order": order,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE,
            "live_execution_enabled": ENABLE_LIVE_ORDER_EXECUTION
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alpaca order placement error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to place order: {str(e)}")

@app.delete("/api/trading/alpaca/order/{order_id}")
async def cancel_alpaca_order(order_id: str, current_user: dict = Depends(require_authenticated_user)):
    """Cancel Alpaca order"""
    try:
        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        success = await alpaca_service.cancel_order(order_id)
        return {
            "success": success,
            "order_id": order_id,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE
        }

    except Exception as e:
        logger.error(f"Alpaca order cancellation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel order: {str(e)}")

@app.get("/api/trading/alpaca/portfolio/history")
async def get_alpaca_portfolio_history(period: str = "1M", current_user: dict = Depends(require_authenticated_user)):
    """Get Alpaca portfolio history"""
    try:
        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        history = await alpaca_service.get_portfolio_history(period=period)
        return {
            "success": True,
            "history": history,
            "period": period,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE
        }

    except Exception as e:
        logger.error(f"Alpaca portfolio history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get portfolio history: {str(e)}")

@app.get("/api/trading/alpaca/market-data/{symbol}")
async def get_alpaca_market_data(symbol: str, timeframe: str = "1Min", limit: int = 100, current_user: dict = Depends(require_authenticated_user)):
    """Get Alpaca market data"""
    try:
        # Use ALWAYS_LIVE logic
        use_paper = not ALWAYS_LIVE
        alpaca_service = get_alpaca_service(use_paper=use_paper)

        if not alpaca_service.is_available():
            raise HTTPException(status_code=503, detail="Alpaca service not available")

        market_data = await alpaca_service.get_market_data(
            symbol=symbol.upper(),
            timeframe=timeframe,
            limit=min(limit, 1000)  # Limit to prevent excessive data
        )

        return {
            "success": True,
            "symbol": symbol.upper(),
            "data": market_data.to_dict('records') if hasattr(market_data, 'to_dict') else market_data,
            "timeframe": timeframe,
            "limit": limit,
            "mode": "paper" if use_paper else "live",
            "always_live": ALWAYS_LIVE
        }

    except Exception as e:
        logger.error(f"Alpaca market data error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get market data: {str(e)}")

@app.get("/api/trading/alpaca/status")
async def get_alpaca_status(current_user: dict = Depends(require_authenticated_user)):
    """Get Alpaca service status"""
    try:
        paper_service = get_alpaca_service(use_paper=True)
        live_service = get_alpaca_service(use_paper=False)

        paper_available = paper_service.is_available()
        live_available = live_service.is_available()

        return {
            "success": True,
            "paper_trading": {
                "available": paper_available,
                "configured": bool(os.getenv('ALPACA_PAPER_API_KEY'))
            },
            "live_trading": {
                "available": live_available,
                "configured": bool(os.getenv('ALPACA_LIVE_API_KEY'))
            },
            "always_live": ALWAYS_LIVE,
            "live_execution_enabled": ENABLE_LIVE_ORDER_EXECUTION,
            "effective_mode": "live" if ALWAYS_LIVE else "paper"
        }

    except Exception as e:
        logger.error(f"Alpaca status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# Legacy endpoint aliases for backward compatibility
@app.get("/api/alpaca/account")
async def get_alpaca_account_legacy(current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for Alpaca account"""
    return await get_alpaca_account(current_user)

@app.get("/api/alpaca/positions")
async def get_alpaca_positions_legacy(current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for Alpaca positions"""
    return await get_alpaca_positions(current_user)

@app.get("/api/alpaca/orders")
async def get_alpaca_orders_legacy(status: str = "all", current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for Alpaca orders"""
    return await get_alpaca_orders(status, current_user)

@app.post("/api/alpaca/order")
async def place_alpaca_order_legacy(order_data: Dict[str, Any], current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for placing Alpaca orders"""
    return await place_alpaca_order(order_data, current_user)

@app.get("/api/alpaca/portfolio/history")
async def get_alpaca_portfolio_history_legacy(period: str = "1M", current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for Alpaca portfolio history"""
    return await get_alpaca_portfolio_history(period, current_user)

@app.get("/api/alpaca/market-data/{symbol}")
async def get_alpaca_market_data_legacy(symbol: str, timeframe: str = "1Min", limit: int = 100, current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for Alpaca market data"""
    return await get_alpaca_market_data(symbol, timeframe, limit, current_user)

@app.get("/api/alpaca/status")
async def get_alpaca_status_legacy(current_user: dict = Depends(require_authenticated_user)):
    """Legacy endpoint for Alpaca status"""
    return await get_alpaca_status(current_user)

print("[CHECK] Trading endpoints loaded successfully")
