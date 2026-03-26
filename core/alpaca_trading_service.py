#!/usr/bin/env python3
"""
Alpaca Trading Integration
PROMETHEUS Trading Platform - Real Trading with Alpaca Markets
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import requests
import json
from decimal import Decimal

# Alpaca Trading API
try:
    import alpaca_trade_api as tradeapi
    from alpaca_trade_api.rest import TimeFrame, TimeFrameUnit
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    print("WARNING: Alpaca Trade API not installed. Run: pip install alpaca-trade-api")

# Import our request tracker
try:
    from .alpaca_request_tracker import get_request_tracker
    REQUEST_TRACKING_AVAILABLE = True
except ImportError:
    REQUEST_TRACKING_AVAILABLE = False
    print("WARNING: Request tracking not available")

class AlpacaTradingService:
    """
    Alpaca Markets Integration
    Handles both Paper Trading and Live Trading
    """

    def __init__(self, use_paper_trading: bool = True):
        self.use_paper_trading = use_paper_trading
        self.logger = logging.getLogger(__name__)

        # Initialize request tracker
        if REQUEST_TRACKING_AVAILABLE:
            self.request_tracker = get_request_tracker()
            self.logger.info("Request tracking enabled")
        else:
            self.request_tracker = None
            self.logger.warning("Request tracking disabled")

        if not ALPACA_AVAILABLE:
            self.logger.error("Alpaca Trade API not available")
            self.api = None
            return

        # Your API Keys
        if use_paper_trading:
            # Paper Trading Configuration
            # Prefer explicit paper vars, fall back to generic APCA_* if present
            self.api_key = (
                os.getenv("ALPACA_PAPER_KEY")
                or os.getenv("APCA_API_KEY_ID")
                or os.getenv("ALPACA_API_KEY", "")
            )
            self.api_secret = (
                os.getenv("ALPACA_PAPER_SECRET")
                or os.getenv("APCA_API_SECRET_KEY")
                or os.getenv("ALPACA_SECRET_KEY", "")
            )
            self.base_url = os.getenv(
                "ALPACA_PAPER_BASE_URL",
                os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
            )
            self.logger.info("🧪 Using Alpaca Paper Trading")
        else:
            # Live Trading Configuration
            self.api_key = (
                os.getenv("ALPACA_LIVE_KEY")
                or os.getenv("APCA_API_KEY_ID")
                or os.getenv("ALPACA_API_KEY", "")
            )
            self.api_secret = (
                os.getenv("ALPACA_LIVE_SECRET")
                or os.getenv("APCA_API_SECRET_KEY")
                or os.getenv("ALPACA_SECRET_KEY", "")
            )
            self.base_url = os.getenv(
                "ALPACA_LIVE_BASE_URL",
                os.getenv("ALPACA_BASE_URL", "https://api.alpaca.markets")
            )
            self.logger.info("Using Alpaca Live Trading")

        try:
            if not self.api_key or not self.api_secret:
                raise RuntimeError("Missing Alpaca API credentials")
            self.api = tradeapi.REST(
                self.api_key,
                self.api_secret,
                self.base_url,
                api_version='v2'
            )

            # Best-effort test connection (non-fatal).
            try:
                account = self.api.get_account()
                self.logger.info(f"Connected to Alpaca - Account Status: {account.status}")
            except Exception as te:
                # Keep instance but mark unavailable until first call succeeds
                self.logger.warning(f"Alpaca connection check skipped/failed: {te}")

        except Exception as e:
            self.logger.error(f"Failed to connect to Alpaca ({'paper' if self.use_paper_trading else 'live'}): {e}")
            self.api = None

    def is_available(self) -> bool:
        """Check if Alpaca service is available"""
        return ALPACA_AVAILABLE and self.api is not None

    def _make_tracked_api_call(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make a tracked API call to Alpaca

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/v2/account')
            **kwargs: Additional arguments for the request

        Returns:
            requests.Response with X-Request-ID tracked
        """
        if not self.request_tracker:
            # Fallback to regular requests if tracking unavailable
            url = f"{self.base_url}{endpoint}"
            headers = {
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.api_secret
            }

            if method.upper() == "GET":
                return requests.get(url, headers=headers, **kwargs)
            elif method.upper() == "POST":
                return requests.post(url, headers=headers, **kwargs)
            elif method.upper() == "DELETE":
                return requests.delete(url, headers=headers, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

        # Use tracked request
        url = f"{self.base_url}{endpoint}"
        headers = {
            "APCA-API-KEY-ID": self.api_key,
            "APCA-API-SECRET-KEY": self.api_secret
        }

        return self.request_tracker.make_tracked_request(
            method=method,
            url=url,
            headers=headers,
            **kwargs
        )

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        if not self.is_available():
            return {"error": "Alpaca not available"}

        try:
            account = self.api.get_account()
            return {
                "account_id": account.id,
                "status": account.status,
                "buying_power": float(account.buying_power),
                "cash": float(account.cash),
                "portfolio_value": float(account.portfolio_value),
                "equity": float(account.equity),
                "long_market_value": float(account.long_market_value),
                "short_market_value": float(account.short_market_value),
                "day_trade_count": getattr(account, 'day_trade_count', 0),
                "sma": float(account.sma) if account.sma else 0,
                "pattern_day_trader": account.pattern_day_trader,
                "trading_blocked": account.trading_blocked,
                "transfers_blocked": account.transfers_blocked,
                "account_blocked": account.account_blocked,
                "created_at": account.created_at.isoformat() if account.created_at else None,
                "currency": account.currency,
                "last_equity": float(account.last_equity) if account.last_equity else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting account info: {e}")
            return {"error": str(e)}

    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions"""
        if not self.is_available():
            return []

        try:
            positions = self.api.list_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "side": pos.side,
                    "market_value": float(pos.market_value),
                    "cost_basis": float(pos.cost_basis),
                    "unrealized_pl": float(pos.unrealized_pl),
                    "unrealized_plpc": float(pos.unrealized_plpc),
                    "current_price": float(pos.current_price),
                    "lastday_price": float(pos.lastday_price),
                    "change_today": float(pos.change_today),
                    "avg_entry_price": float(pos.avg_entry_price)
                }
                for pos in positions
            ]
        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []

    def get_orders(self, status: str = "all", limit: int = 100) -> List[Dict[str, Any]]:
        """Get orders with optional status filter"""
        if not self.is_available():
            return []

        try:
            orders = self.api.list_orders(status=status, limit=limit)
            return [
                {
                    "id": order.id,
                    "symbol": order.symbol,
                    "qty": float(order.qty),
                    "side": order.side,
                    "order_type": order.order_type,
                    "time_in_force": order.time_in_force,
                    "status": order.status,
                    "created_at": order.created_at.isoformat() if order.created_at else None,
                    "filled_at": order.filled_at.isoformat() if order.filled_at else None,
                    "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                    "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0,
                    "limit_price": float(order.limit_price) if order.limit_price else None,
                    "stop_price": float(order.stop_price) if order.stop_price else None,
                    "trail_price": float(order.trail_price) if order.trail_price else None,
                    "trail_percent": float(order.trail_percent) if order.trail_percent else None
                }
                for order in orders
            ]
        except Exception as e:
            self.logger.error(f"Error getting orders: {e}")
            return []

    def place_order(
        self,
        symbol: str,
        qty: Union[int, float],
        side: str,  # 'buy' or 'sell'
        order_type: str = 'market',  # 'market', 'limit', 'stop', 'stop_limit'
        time_in_force: str = 'day',  # 'day', 'gtc', 'ioc', 'fok'
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None,
        trail_price: Optional[float] = None,
        trail_percent: Optional[float] = None
    ) -> Dict[str, Any]:
        """Place a trading order"""
        if not self.is_available():
            return {"error": "Alpaca not available"}

        try:
            order_params = {
                'symbol': symbol.upper(),
                'qty': qty,
                'side': side.lower(),
                'type': order_type.lower(),
                'time_in_force': time_in_force.lower()
            }

            # Add conditional parameters
            if limit_price is not None:
                order_params['limit_price'] = limit_price
            if stop_price is not None:
                order_params['stop_price'] = stop_price
            if trail_price is not None:
                order_params['trail_price'] = trail_price
            if trail_percent is not None:
                order_params['trail_percent'] = trail_percent

            order = self.api.submit_order(**order_params)

            return {
                "success": True,
                "order_id": order.id,
                "symbol": order.symbol,
                "qty": float(order.qty),
                "side": order.side,
                "order_type": order.order_type,
                "status": order.status,
                "created_at": order.created_at.isoformat() if order.created_at else None,
                "message": f"Order placed successfully for {qty} shares of {symbol}"
            }

        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to place order for {symbol}"
            }

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an existing order"""
        if not self.is_available():
            return {"error": "Alpaca not available"}

        try:
            self.api.cancel_order(order_id)
            return {
                "success": True,
                "message": f"Order {order_id} cancelled successfully"
            }
        except Exception as e:
            self.logger.error(f"Error cancelling order: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to cancel order {order_id}"
            }

    # ===== Options Trading (Phase 3) =====
    @staticmethod
    def normalize_option_symbol(symbol: str) -> str:
        """Normalize common option symbol formats to OCC (e.g., AAPL250117C00200000).
        Accepts already-OCC strings and pass-through.
        Also accepts human format like: 'AAPL 2025-01-17 C 200' or 'AAPL 2025-01-17 P 412.5'.
        """
        s = symbol.strip().upper()
        # If looks like OCC (has YYMMDD and C/P and long strike), return as-is
        import re
        if re.fullmatch(r"[A-Z]{1,6}[0-9]{6}[CP][0-9]{8}", s):
            return s
        # Try human-friendly split
        parts = s.replace("/", "-").split()
        if len(parts) == 4:
            underlying, date_str, cp, strike_str = parts
            # Parse date to YYMMDD
            from datetime import datetime
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                # Try MM/DD/YYYY
                try:
                    dt = datetime.strptime(date_str, "%m-%d-%Y")
                except Exception:
                    raise ValueError(f"Unrecognized option date format: {date_str}")
            yymmdd = dt.strftime("%y%m%d")
            side = 'C' if cp.startswith('C') else 'P'
            # Strike to 8-digit with 3 decimals (x1000) padded
            try:
                strike_val = float(strike_str)
            except ValueError:
                # Remove possible $ prefix
                strike_val = float(strike_str.replace("$", ""))
            strike_int = int(round(strike_val * 1000))
            strike_field = f"{strike_int:08d}"
            occ = f"{underlying}{yymmdd}{side}{strike_field}"
            if not re.fullmatch(r"[A-Z]{1,6}[0-9]{6}[CP][0-9]{8}", occ):
                raise ValueError(f"Failed to build OCC symbol from inputs: {symbol}")
            return occ
        raise ValueError(f"Unsupported option symbol format: {symbol}")

    def place_options_order(
        self,
        symbol: str,
        qty: Union[int, float],
        side: str,  # 'buy' or 'sell'
        order_type: str = 'market',  # 'market' or 'limit'
        time_in_force: str = 'day',
        limit_price: Optional[float] = None,
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Place an OPTIONS order via Alpaca REST v2.
        Uses tracked request path even if alpaca_trade_api doesn't expose options.
        """
        if not self.is_available():
            return {"error": "Alpaca not available"}
        try:
            occ_symbol = self.normalize_option_symbol(symbol)
            payload: Dict[str, Any] = {
                "symbol": occ_symbol,
                "qty": qty,
                "side": side.lower(),
                "type": order_type.lower(),
                "time_in_force": time_in_force.lower(),
            }
            if client_order_id:
                payload["client_order_id"] = client_order_id
            if order_type.lower() == 'limit' and limit_price is not None:
                payload["limit_price"] = limit_price
            # POST /v2/options/orders
            resp = self._make_tracked_api_call("POST", "/v2/options/orders", json=payload)
            rid = resp.headers.get("X-Request-ID")
            if resp.status_code >= 400:
                try:
                    err = resp.json()
                except Exception:
                    err = {"message": resp.text}
                return {"success": False, "error": err, "request_id": rid}
            data = resp.json()
            return {
                "success": True,
                "request_id": rid,
                "order": data,
            }
        except Exception as e:
            self.logger.error(f"Error placing options order: {e}")
            return {"success": False, "error": str(e)}

    def get_options_orders(self, status: str = "all", limit: int = 50) -> List[Dict[str, Any]]:
        """List options orders."""
        if not self.is_available():
            return []
        try:
            params = {"status": status, "limit": limit}
            resp = self._make_tracked_api_call("GET", "/v2/options/orders", params=params)
            if resp.status_code >= 400:
                return []
            return resp.json() or []
        except Exception as e:
            self.logger.error(f"Error listing options orders: {e}")
            return []

    def cancel_options_order(self, order_id: str) -> Dict[str, Any]:
        """Cancel an options order."""
        if not self.is_available():
            return {"error": "Alpaca not available"}
        try:
            resp = self._make_tracked_api_call("DELETE", f"/v2/options/orders/{order_id}")
            rid = resp.headers.get("X-Request-ID")
            if resp.status_code in (200, 204):
                return {"success": True, "request_id": rid}
            try:
                err = resp.json()
            except Exception:
                err = {"message": resp.text}
            return {"success": False, "error": err, "request_id": rid}
        except Exception as e:
            self.logger.error(f"Error cancelling options order: {e}")
            return {"success": False, "error": str(e)}

    def get_market_data(self, symbols: List[str], timeframe: str = "1Min", limit: int = 1000) -> Dict[str, Any]:
        """Get historical market data"""
        if not self.is_available():
            return {"error": "Alpaca not available"}

        try:
            # Convert timeframe string to Alpaca TimeFrame
            timeframe_map = {
                "1Min": TimeFrame.Minute,
                "5Min": TimeFrame(5, TimeFrameUnit.Minute),
                "15Min": TimeFrame(15, TimeFrameUnit.Minute),
                "1Hour": TimeFrame.Hour,
                "1Day": TimeFrame.Day
            }

            tf = timeframe_map.get(timeframe, TimeFrame.Minute)

            bars = self.api.get_bars(
                symbols,
                tf,
                limit=limit,
                adjustment='raw'
            ).df

            # Convert to dictionary format
            result = {}
            for symbol in symbols:
                if symbol in bars.index.get_level_values('symbol'):
                    symbol_data = bars[bars.index.get_level_values('symbol') == symbol]
                    result[symbol] = {
                        "bars": [
                            {
                                "timestamp": timestamp.isoformat(),
                                "open": float(row['open']),
                                "high": float(row['high']),
                                "low": float(row['low']),
                                "close": float(row['close']),
                                "volume": int(row['volume'])
                            }
                            for timestamp, row in symbol_data.iterrows()
                        ]
                    }

            return result

        except Exception as e:
            self.logger.error(f"Error getting market data: {e}")
            return {"error": str(e)}

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current price for a symbol"""
        if not self.is_available():
            return None

        try:
            latest_trade = self.api.get_latest_trade(symbol)
            return float(latest_trade.price) if latest_trade else None
        except Exception as e:
            self.logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    def get_portfolio_performance(self, period: str = "1D") -> Dict[str, Any]:
        """Get portfolio performance metrics"""
        if not self.is_available():
            return {"error": "Alpaca not available"}

        try:
            account = self.api.get_account()
            positions = self.get_positions()

            # Calculate basic metrics
            total_value = float(account.portfolio_value)
            total_pl = sum(pos['unrealized_pl'] for pos in positions)
            total_pl_percent = (total_pl / total_value * 100) if total_value > 0 else 0

            return {
                "total_value": total_value,
                "total_pl": total_pl,
                "total_pl_percent": total_pl_percent,
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "positions_count": len(positions),
                "day_trade_count": account.day_trade_count,
                "performance_period": period
            }

        except Exception as e:
            self.logger.error(f"Error getting portfolio performance: {e}")
            return {"error": str(e)}

    def get_portfolio_history(self, period: str = "1D", timeframe: str = "1Min", extended_hours: bool = True) -> Dict[str, Any]:
        """Get portfolio history over time"""
        if not self.is_available():
            return {"error": "Alpaca not available"}

        try:
            # Get portfolio history from Alpaca
            # Request intraday by default; allow extended hours to populate more points
            try:
                history = self.api.get_portfolio_history(period=period, timeframe=timeframe, extended_hours=extended_hours)
            except TypeError:
                # Older SDKs may not support extended_hours kwarg
                history = self.api.get_portfolio_history(period=period, timeframe=timeframe)

            if not history or not history.timestamp:
                return {
                    "timestamps": [],
                    "equity": [],
                    "profit_loss": [],
                    "profit_loss_pct": [],
                    "base_value": 0
                }

            # Convert to our format - handle both datetime and unix timestamp formats
            timestamps = []
            for ts in history.timestamp:
                if hasattr(ts, 'isoformat'):
                    # It's a datetime object
                    timestamps.append(ts.isoformat())
                else:
                    # It's likely a unix timestamp (int/float)
                    from datetime import datetime
                    timestamps.append(datetime.fromtimestamp(ts).isoformat())

            equity = [float(val) for val in history.equity if val is not None] if history.equity else []
            profit_loss = [float(val) for val in history.profit_loss if val is not None] if history.profit_loss else []
            profit_loss_pct = [float(val) for val in history.profit_loss_pct if val is not None] if history.profit_loss_pct else []

            return {
                "timestamps": timestamps,
                "equity": equity,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "base_value": float(history.base_value) if history.base_value else 0,
                "timeframe": timeframe,
                "period": period
            }

        except Exception as e:
            self.logger.error(f"Error getting portfolio history: {e}")
            return {"error": str(e)}


    # Request Tracking Methods
    def get_recent_request_ids(self, limit: int = 10) -> List[str]:
        """Get recent X-Request-IDs for support tickets"""
        if not self.request_tracker:
            return []

        recent_requests = self.request_tracker.get_recent_requests(limit)
        return [req['request_id'] for req in recent_requests if req['request_id'] != 'unknown']

    def get_request_details(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific Request ID"""
        if not self.request_tracker:
            return None

        return self.request_tracker.get_request_by_id(request_id)

    def get_failed_requests(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get failed API requests from the last N hours"""
        if not self.request_tracker:
            return []

        return self.request_tracker.get_failed_requests(hours)

    def generate_support_report(self) -> Dict[str, Any]:
        """Generate a comprehensive support report with Request IDs"""
        if not self.request_tracker:
            return {
                "error": "Request tracking not available",
                "recent_request_ids": [],
                "support_message": "Request tracking is disabled. Enable it to get X-Request-IDs for support."
            }

        report = self.request_tracker.generate_support_report()

        # Add account context
        try:
            account = self.get_account_info()
            report['account_context'] = {
                "account_id": account.get('account_id'),
                "status": account.get('status'),
                "trading_mode": "paper" if self.use_paper_trading else "live",
                "timestamp": datetime.now().isoformat()
            }
        except:
            report['account_context'] = {
                "trading_mode": "paper" if self.use_paper_trading else "live",
                "timestamp": datetime.now().isoformat()
            }

        # Format support message
        recent_ids = report.get('recent_request_ids', [])
        support_message = f"""
ALPACA SUPPORT REQUEST

Account Type: {'Paper Trading' if self.use_paper_trading else 'Live Trading'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

Recent Request IDs (last 10 calls):
{chr(10).join(f"  - {rid}" for rid in recent_ids[-10:]) if recent_ids else "  No Request IDs available"}

Latest Request ID: {recent_ids[0] if recent_ids else "None"}

Failed Requests (24h): {len(report.get('failed_requests', []))}

Please provide this information when contacting Alpaca support.
"""

        report['support_message'] = support_message
        return report


# Lazy global instances to avoid initializing both modes at import time
alpaca_paper: Optional[AlpacaTradingService] = None
alpaca_live: Optional[AlpacaTradingService] = None

def get_alpaca_service(use_paper: bool = True) -> AlpacaTradingService:
    """Get Alpaca service instance lazily without touching the other mode."""
    global alpaca_paper, alpaca_live
    if use_paper:
        if alpaca_paper is None:
            alpaca_paper = AlpacaTradingService(use_paper_trading=True)
        return alpaca_paper
    else:
        if alpaca_live is None:
            alpaca_live = AlpacaTradingService(use_paper_trading=False)
        return alpaca_live

if __name__ == "__main__":
    # Test the integration
    print("Testing Alpaca Trading Integration...")

    # Test paper trading
    print("\nPaper Trading Test:")
    paper_service = get_alpaca_service(use_paper=True)
    if paper_service.is_available():
        account_info = paper_service.get_account_info()
        print(f"Account Status: {account_info.get('status', 'Unknown')}")
        print(f"Buying Power: ${account_info.get('buying_power', 0):,.2f}")
        print(f"Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")

        positions = paper_service.get_positions()
        print(f"Current Positions: {len(positions)}")

        orders = paper_service.get_orders(limit=5)
        print(f"Recent Orders: {len(orders)}")
    else:
        print("Paper trading service not available")

    # Test live trading (if configured)
    print("\nLive Trading Test:")
    live_service = get_alpaca_service(use_paper=False)
    if live_service.is_available():
        account_info = live_service.get_account_info()
        print(f"Account Status: {account_info.get('status', 'Unknown')}")
        print(f"Buying Power: ${account_info.get('buying_power', 0):,.2f}")
        print(f"Portfolio Value: ${account_info.get('portfolio_value', 0):,.2f}")
    else:
        print("Live trading service not available (API secret needed)")

    print("\nAlpaca integration test complete!")
