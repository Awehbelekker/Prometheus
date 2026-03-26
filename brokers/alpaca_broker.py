"""
Alpaca Broker Implementation for PROMETHEUS Trading Platform
"""

import asyncio
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import TimeFrame
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import requests

from .universal_broker_interface import (
    BrokerInterface, Order, Position, Account, 
    OrderSide, OrderType, OrderStatus
)

# Import enhanced error handling
from core.error_handling import (
    TradingError, ConnectionError, AuthenticationError, MarketDataError,
    OrderExecutionError, AccountAccessError, RateLimitError, ValidationError,
    ErrorSeverity, ErrorCategory, ErrorContext, error_logger, 
    error_recovery_manager, ExponentialBackoffRetry, create_connection_error,
    create_market_data_error, create_order_execution_error
)

logger = logging.getLogger(__name__)

class AlpacaBroker(BrokerInterface):
    """Alpaca broker implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
        self.secret_key = config.get('secret_key')
        self.paper_trading = config.get('paper_trading', True)
        
        # Set base URL based on trading mode
        if self.paper_trading:
            self.base_url = 'https://paper-api.alpaca.markets'
        else:
            self.base_url = 'https://api.alpaca.markets'
        
        # Enable 24/5 trading (Sunday 8PM - Friday 4AM ET)
        self.enable_24_5 = config.get('enable_24_5_trading', True)
        logger.info(f"[24/5] Alpaca 24/5 trading: {'ENABLED' if self.enable_24_5 else 'DISABLED'}")
        
        self.api = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to Alpaca API with enhanced error handling and retry logic"""
        retry_strategy = ExponentialBackoffRetry(max_attempts=3, base_delay=2.0)
        
        async def _connect_attempt():
            try:
                # Validate credentials
                if not self.api_key or not self.secret_key:
                    raise AuthenticationError(
                        message="Missing Alpaca API credentials",
                        broker="Alpaca"
                    )
                
                # Initialize API client
                self.api = tradeapi.REST(
                    self.api_key,
                    self.secret_key,
                    self.base_url,
                    api_version='v2'
                )
                
                # Test connection with comprehensive validation
                await self._validate_alpaca_connection()
                
                self.connected = True
                logger.info(f"✅ Connected to Alpaca {'Paper' if self.paper_trading else 'Live'}")
                if self.enable_24_5:
                    logger.info(f"🌙 Alpaca 24/5 trading ENABLED (Sun 8PM - Fri 4AM)")
                return True
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    raise AuthenticationError(
                        message="Invalid Alpaca API credentials",
                        broker="Alpaca",
                        original_error=e
                    )
                elif e.response.status_code == 403:
                    raise AuthenticationError(
                        message="Alpaca API access forbidden - check permissions",
                        broker="Alpaca",
                        original_error=e
                    )
                elif e.response.status_code == 429:
                    raise RateLimitError(
                        message="Alpaca API rate limit exceeded",
                        broker="Alpaca",
                        retry_after=int(e.response.headers.get('Retry-After', 60)),
                        original_error=e
                    )
                else:
                    raise ConnectionError(
                        message=f"Alpaca API HTTP error: {e.response.status_code}",
                        broker="Alpaca",
                        original_error=e
                    )
            except requests.exceptions.ConnectionError as e:
                raise ConnectionError(
                    message="Cannot connect to Alpaca API - network issue",
                    broker="Alpaca",
                    original_error=e
                )
            except requests.exceptions.Timeout as e:
                raise ConnectionError(
                    message="Alpaca API connection timeout",
                    broker="Alpaca",
                    original_error=e
                )
            except Exception as e:
                raise ConnectionError(
                    message=f"Unexpected Alpaca connection error: {str(e)}",
                    broker="Alpaca",
                    original_error=e
                )
        
        try:
            return await retry_strategy.execute(_connect_attempt)
        except TradingError as e:
            await error_logger.log_error(e)
            logger.error(f"❌ Alpaca connection failed: {e.message}")
            self.connected = False
            return False
        except Exception as e:
            connection_error = create_connection_error("Alpaca", e)
            await error_logger.log_error(connection_error)
            logger.error(f"❌ Alpaca connection error: {e}")
            self.connected = False
            return False
    
    async def _validate_alpaca_connection(self):
        """Validate Alpaca connection with comprehensive tests"""
        try:
            # Test account access
            account = self.api.get_account()
            
            # Validate account data
            if not account.account_number:
                raise ValidationError(
                    message="Invalid account data received from Alpaca",
                    broker="Alpaca",
                    operation="get_account"
                )
            
            # Test market data access
            try:
                # Test with a common stock
                test_symbol = "AAPL"
                quote = self.api.get_latest_quote(test_symbol)
                if not quote or not hasattr(quote, 'bid_price'):
                    logger.warning("Market data test returned incomplete data")
            except Exception as market_error:
                logger.warning(f"Market data test failed: {market_error}")
                # Don't fail connection for market data issues
            
            # Test order capabilities (if not paper trading)
            if not self.paper_trading:
                try:
                    # Just test if we can list orders (won't place any)
                    orders = self.api.list_orders(status='all', limit=1)
                except Exception as order_error:
                    logger.warning(f"Order capability test failed: {order_error}")
            
            logger.info(f"✅ Alpaca connection validation successful - Account: {account.account_number}")
            
        except Exception as e:
            raise ConnectionError(
                message=f"Alpaca connection validation failed: {str(e)}",
                broker="Alpaca",
                original_error=e
            )
    
    async def disconnect(self):
        """Disconnect from Alpaca"""
        self.api = None
        self.connected = False
        logger.info("[CHECK] Disconnected from Alpaca")
    
    async def get_account(self) -> Account:
        """Get account information"""
        if not self.connected or not self.api:
            raise RuntimeError("Not connected to Alpaca")
        
        account = self.api.get_account()
        return Account(
            account_id=account.account_number,
            buying_power=float(account.buying_power),
            cash=float(account.cash),
            portfolio_value=float(account.portfolio_value),
            equity=float(account.equity),
            day_trade_count=int(account.daytrade_count),
            pattern_day_trader=account.pattern_day_trader
        )
    
    async def get_positions(self) -> List[Position]:
        """Get all positions"""
        if not self.connected or not self.api:
            raise RuntimeError("Not connected to Alpaca")
        
        positions = self.api.list_positions()
        result = []
        
        for pos in positions:
            # Alpaca API uses avg_entry_price, not avg_cost
            avg_price = getattr(pos, 'avg_entry_price', None) or getattr(pos, 'avg_cost', 0)
            result.append(Position(
                symbol=pos.symbol,
                quantity=float(pos.qty),
                avg_price=float(avg_price),
                market_value=float(pos.market_value),
                unrealized_pnl=float(pos.unrealized_pl),
                unrealized_pnl_percent=float(pos.unrealized_plpc),
                side="long" if float(pos.qty) > 0 else "short"
            ))
        
        return result
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        try:
            if not self.connected or not self.api:
                raise RuntimeError("Not connected to Alpaca")

            # Try different symbol formats (BTC/USD -> BTCUSD for Alpaca)
            symbols_to_try = [symbol]
            if '/' in symbol:
                symbols_to_try.append(symbol.replace('/', ''))  # BTC/USD -> BTCUSD
            else:
                # Try adding slash for crypto
                if len(symbol) >= 6 and symbol.endswith('USD'):
                    symbols_to_try.append(f"{symbol[:-3]}/{symbol[-3:]}")  # BTCUSD -> BTC/USD

            pos = None
            for sym in symbols_to_try:
                try:
                    pos = self.api.get_position(sym)
                    if pos:
                        logger.info(f"✅ Found position for {sym}: qty={pos.qty}")
                        break
                except Exception as e:
                    logger.debug(f"Position lookup failed for {sym}: {e}")
                    continue

            # If direct lookup failed, search through all positions
            if not pos:
                logger.info(f"🔍 Direct lookup failed for {symbol}, searching all positions...")
                try:
                    all_positions = self.api.list_positions()
                    # Normalize the search symbol
                    search_symbols = set(symbols_to_try)
                    for p in all_positions:
                        pos_symbol = p.symbol
                        # Check if position symbol matches any of our search symbols
                        if pos_symbol in search_symbols or pos_symbol.replace('/', '') in search_symbols:
                            pos = p
                            logger.info(f"✅ Found position via search: {pos_symbol} qty={pos.qty}")
                            break
                        # Also check reverse (BTCUSD matches BTC/USD)
                        if '/' not in pos_symbol and len(pos_symbol) >= 6:
                            normalized = f"{pos_symbol[:-3]}/{pos_symbol[-3:]}"
                            if normalized in search_symbols:
                                pos = p
                                logger.info(f"✅ Found position via normalized search: {pos_symbol} qty={pos.qty}")
                                break
                except Exception as e:
                    logger.warning(f"Failed to search all positions: {e}")

            if not pos:
                logger.info(f"❌ No position found for {symbol}")
                return None

            # Alpaca API uses avg_entry_price, not avg_cost
            avg_price = getattr(pos, 'avg_entry_price', None) or getattr(pos, 'avg_cost', 0)
            return Position(
                symbol=pos.symbol,
                quantity=float(pos.qty),
                avg_price=float(avg_price),
                market_value=float(pos.market_value),
                unrealized_pnl=float(pos.unrealized_pl),
                unrealized_pnl_percent=float(pos.unrealized_plpc),
                side="long" if float(pos.qty) > 0 else "short"
            )
        except Exception as e:
            logger.error(f"Error getting position for {symbol}: {e}")
            return None
    
    async def submit_order(self, order: Order) -> Order:
        """Submit an order"""
        if not self.connected or not self.api:
            raise RuntimeError("Not connected to Alpaca")

        # Check if this is a 24-hour stock (not crypto)
        is_crypto = '/' in order.symbol
        is_24hr_stock = not is_crypto and self._is_24hr_stock(order.symbol)

        # Check if we're in 24/5 overnight session
        is_overnight_session = self._is_overnight_session() if self.enable_24_5 else False
        
        # For 24-hour stocks or overnight sessions, use extended_hours=True
        extended_hours = is_24hr_stock or is_overnight_session
        
        if is_overnight_session:
            logger.info(f"🌙 Alpaca 24/5: Overnight session active for {order.symbol}")

        # CRITICAL: Alpaca extended hours orders MUST be DAY limit orders
        # Convert market orders to limit orders for extended hours trading
        order_type_to_use = order.order_type.value
        time_in_force_to_use = order.time_in_force
        # Use limit_price field if available (new), fall back to price (legacy)
        limit_price_to_use = getattr(order, 'limit_price', None) or order.price if order.order_type == OrderType.LIMIT else None

        if extended_hours and order.order_type == OrderType.MARKET:
            # For extended hours, convert market order to limit order at current price
            order_type_to_use = 'limit'
            time_in_force_to_use = 'day'  # Extended hours requires DAY TIF
            # Use provided price or get current price with small buffer
            if order.price:
                limit_price_to_use = order.price
            else:
                # Add 0.5% buffer for BUY, subtract 0.5% for SELL to ensure fill
                try:
                    bar = self.api.get_latest_bar(order.symbol)
                    current_price = float(bar.c) if bar else None
                    if current_price:
                        if order.side.value == 'buy':
                            limit_price_to_use = round(current_price * 1.005, 2)  # 0.5% above
                        else:
                            limit_price_to_use = round(current_price * 0.995, 2)  # 0.5% below
                        logger.info(f"📈 Extended hours: Converting market to limit @ ${limit_price_to_use}")
                except Exception as e:
                    logger.warning(f"Could not get price for {order.symbol}: {e}")
                    # Fall back to order price if available
                    limit_price_to_use = order.price

            if not limit_price_to_use:
                raise RuntimeError(f"Cannot place extended hours order for {order.symbol}: no price available")

        # Convert universal order to Alpaca format
        alpaca_order = self.api.submit_order(
            symbol=order.symbol,
            qty=order.quantity,
            side=order.side.value,
            type=order_type_to_use,
            time_in_force=time_in_force_to_use,
            limit_price=limit_price_to_use,
            stop_price=order.stop_price if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT] else None,
            extended_hours=extended_hours  # Enable 24/5 trading for supported stocks
        )

        # Update order with Alpaca response
        order.broker_order_id = alpaca_order.id
        order.status = self._convert_alpaca_status(alpaca_order.status)
        order.created_at = alpaca_order.created_at

        if extended_hours:
            logger.info(f"📈 24-hour stock order submitted: {order.symbol} as {order_type_to_use.upper()} @ ${limit_price_to_use}")

        return order

    def sell(self, symbol: str, quantity: float) -> Dict[str, Any]:
        """
        Synchronous sell method for position monitor auto-exits
        Sells specified quantity of a symbol
        """
        try:
            if not self.connected or not self.api:
                return {'success': False, 'error': 'Not connected to Alpaca'}

            # Check if this is a 24-hour stock (not crypto)
            is_crypto = '/' in symbol or symbol.endswith('USD')
            is_24hr_stock = not is_crypto and self._is_24hr_stock(symbol)

            # For 24-hour stocks or extended hours, use limit order
            extended_hours = is_24hr_stock
            order_type = 'market'
            time_in_force = 'gtc' if is_crypto else 'day'
            limit_price = None

            if extended_hours:
                # Extended hours requires limit order
                order_type = 'limit'
                time_in_force = 'day'
                try:
                    # Try to get bid price first (more reliable for sells)
                    try:
                        quote = self.api.get_latest_quote(symbol)
                        if quote and hasattr(quote, 'bp') and quote.bp:
                            bid_price = float(quote.bp)
                            # Use 1% below bid for quick fill during extended hours
                            limit_price = round(bid_price * 0.99, 2)
                            logger.info(f"📈 Extended hours SELL: {symbol} as limit @ ${limit_price} (1% below bid ${bid_price:.2f})")
                        else:
                            raise ValueError("No bid price available")
                    except Exception as quote_err:
                        # Fallback to bar close price with more aggressive discount
                        logger.warning(f"Could not get quote for {symbol}: {quote_err}, using bar price")
                        bar = self.api.get_latest_bar(symbol)
                        if bar:
                            current_price = float(bar.c)
                            limit_price = round(current_price * 0.98, 2)  # 2% below close for safety
                            logger.info(f"📈 Extended hours SELL: {symbol} as limit @ ${limit_price} (2% below close ${current_price:.2f})")
                        else:
                            raise ValueError("No price data available")
                except Exception as e:
                    logger.warning(f"Could not get price for {symbol}: {e}")
                    return {'success': False, 'error': f'Could not get price for limit order: {e}'}

            # Submit the sell order
            alpaca_order = self.api.submit_order(
                symbol=symbol,
                qty=quantity,
                side='sell',
                type=order_type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                extended_hours=extended_hours
            )

            logger.info(f"✅ SELL order submitted: {symbol} x {quantity} - Order ID: {alpaca_order.id}")

            return {
                'success': True,
                'order_id': alpaca_order.id,
                'symbol': symbol,
                'quantity': quantity,
                'side': 'sell',
                'type': order_type,
                'status': str(alpaca_order.status)
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ SELL order failed for {symbol}: {error_msg}")
            return {'success': False, 'error': error_msg}

    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if not self.connected or not self.api:
                raise RuntimeError("Not connected to Alpaca")
            
            self.api.cancel_order(order_id)
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to cancel order {order_id}: {e}")
            return False
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            if not self.connected or not self.api:
                raise RuntimeError("Not connected to Alpaca")
            
            alpaca_order = self.api.get_order(order_id)
            return self._convert_alpaca_order(alpaca_order)
        except Exception:
            return None
    
    async def place_order(self, symbol: str, qty: float, side: str, 
                         order_type: str = 'market', time_in_force: str = 'gtc',
                         limit_price: float = None, stop_price: float = None) -> Any:
        """
        Alias for submit_order to maintain compatibility with older code
        This method provides a simplified interface that matches common usage patterns
        """
        from .universal_broker_interface import Order, OrderSide, OrderType
        
        # Convert string types to enums
        try:
            order_side = OrderSide(side.lower())
        except ValueError:
            raise ValueError(f"Invalid order side: {side}. Must be 'buy' or 'sell'")
        
        try:
            order_type_enum = OrderType(order_type.lower())
        except ValueError:
            raise ValueError(f"Invalid order type: {order_type}. Must be 'market', 'limit', 'stop', or 'stop_limit'")
        
        # Create Order object
        order = Order(
            symbol=symbol,
            quantity=qty,
            side=order_side,
            order_type=order_type_enum,
            price=limit_price,
            stop_price=stop_price,
            time_in_force=time_in_force
        )
        
        # Use existing submit_order method
        return await self.submit_order(order)
    
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders, optionally filtered by status"""
        if not self.connected or not self.api:
            raise RuntimeError("Not connected to Alpaca")
        
        # Convert status filter to Alpaca format
        alpaca_status = None
        if status:
            status_map = {
                OrderStatus.PENDING: 'pending_new',
                OrderStatus.SUBMITTED: 'new',
                OrderStatus.FILLED: 'filled',
                OrderStatus.PARTIALLY_FILLED: 'partially_filled',
                OrderStatus.CANCELLED: 'canceled',
                OrderStatus.REJECTED: 'rejected'
            }
            alpaca_status = status_map.get(status)
        
        alpaca_orders = self.api.list_orders(status=alpaca_status)
        return [self._convert_alpaca_order(order) for order in alpaca_orders]
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data with enhanced error handling"""
        if not self.connected or not self.api:
            raise ConnectionError(
                message="Not connected to Alpaca",
                broker="Alpaca"
            )

        # Validate and normalize symbol early to fix scope issue
        if not symbol or not symbol.strip():
            raise ValidationError(
                message="Invalid symbol provided",
                broker="Alpaca",
                operation="get_market_data"
            )
        
        symbol = symbol.strip().upper()

        retry_strategy = ExponentialBackoffRetry(max_attempts=3, base_delay=1.0)
        
        async def _get_market_data_attempt():
            try:
                
                # Check if crypto (has /)
                is_crypto = '/' in symbol

                if is_crypto:
                    return await self._get_crypto_market_data(symbol)
                else:
                    return await self._get_stock_market_data(symbol)

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    raise MarketDataError(
                        message=f"Symbol {symbol} not found",
                        broker="Alpaca",
                        symbol=symbol,
                        original_error=e
                    )
                elif e.response.status_code == 429:
                    raise RateLimitError(
                        message="Alpaca market data rate limit exceeded",
                        broker="Alpaca",
                        retry_after=int(e.response.headers.get('Retry-After', 60)),
                        original_error=e
                    )
                else:
                    raise MarketDataError(
                        message=f"Alpaca market data HTTP error: {e.response.status_code}",
                        broker="Alpaca",
                        symbol=symbol,
                        original_error=e
                    )
            except Exception as e:
                raise MarketDataError(
                    message=f"Failed to get market data for {symbol}: {str(e)}",
                    broker="Alpaca",
                    symbol=symbol,
                    original_error=e
                )
        
        try:
            return await retry_strategy.execute(_get_market_data_attempt)
        except TradingError as e:
            await error_logger.log_error(e)
            logger.error(f"❌ Market data failed for {symbol}: {e.message}")
            raise e
        except Exception as e:
            market_error = create_market_data_error("Alpaca", symbol, e)
            await error_logger.log_error(market_error)
            logger.error(f"❌ Market data error for {symbol}: {e}")
            raise market_error
    
    async def _get_crypto_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get crypto market data with fallback"""
        try:
            # Primary: Get latest crypto trade
            trade = self.api.get_crypto_latest_trade(symbol)
            
            if not trade or not hasattr(trade, 'price'):
                raise MarketDataError(
                    message=f"No trade data available for {symbol}",
                    broker="Alpaca",
                    symbol=symbol
                )
            
            return {
                'symbol': symbol,
                'price': float(trade.price),
                'volume': float(trade.size) if hasattr(trade, 'size') else 0,
                'timestamp': trade.timestamp
            }
            
        except Exception as primary_error:
            logger.debug(f"Primary crypto API failed for {symbol}, trying bars: {primary_error}")
            
            # Fallback: Get latest bar
            try:
                bars = self.api.get_crypto_bars(symbol, TimeFrame.Minute, limit=1)
                if not bars or len(bars) == 0:
                    raise MarketDataError(
                        message=f"No bar data available for {symbol}",
                        broker="Alpaca",
                        symbol=symbol
                    )
                
                latest_bar = bars[-1]
                return {
                    'symbol': symbol,
                    'price': float(latest_bar.c),  # close price
                    'volume': float(latest_bar.v),
                    'timestamp': latest_bar.t
                }
                
            except Exception as fallback_error:
                raise MarketDataError(
                    message=f"Both primary and fallback crypto data failed for {symbol}",
                    broker="Alpaca",
                    symbol=symbol,
                    original_error=fallback_error
                )
    
    async def _get_stock_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get stock market data"""
        try:
            # Get trade and quote data
            trade = self.api.get_latest_trade(symbol)
            quote = self.api.get_latest_quote(symbol)
            
            if not trade or not hasattr(trade, 'price'):
                raise MarketDataError(
                    message=f"No trade data available for {symbol}",
                    broker="Alpaca",
                    symbol=symbol
                )
            
            if not quote or not hasattr(quote, 'bid_price'):
                raise MarketDataError(
                    message=f"No quote data available for {symbol}",
                    broker="Alpaca",
                    symbol=symbol
                )
            
            return {
                'symbol': symbol,
                'price': float(trade.price),
                'bid': float(quote.bid_price),
                'ask': float(quote.ask_price),
                'bid_size': int(quote.bid_size),
                'ask_size': int(quote.ask_size),
                'timestamp': trade.timestamp
            }
            
        except Exception as e:
            raise MarketDataError(
                message=f"Failed to get stock market data for {symbol}: {str(e)}",
                broker="Alpaca",
                symbol=symbol,
                original_error=e
            )
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1Min', limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical market data"""
        if not self.connected or not self.api:
            raise RuntimeError("Not connected to Alpaca")

        try:
            # Convert timeframe
            tf_map = {
                '1Min': TimeFrame.Minute,
                '5Min': TimeFrame(5, TimeFrame.Minute),
                '15Min': TimeFrame(15, TimeFrame.Minute),
                '1Hour': TimeFrame.Hour,
                '1Day': TimeFrame.Day
            }

            tf = tf_map.get(timeframe, TimeFrame.Minute)

            # Check if crypto
            is_crypto = '/' in symbol

            if is_crypto:
                # Use crypto bars
                bars = self.api.get_crypto_bars(symbol, tf, limit=limit)
            else:
                # Use stock bars
                bars = self.api.get_bars(symbol, tf, limit=limit)

            # Convert to list
            result = []
            if hasattr(bars, 'df'):
                # DataFrame format
                df = bars.df
                for index, row in df.iterrows():
                    result.append({
                        'timestamp': index,
                        'open': float(row['open']),
                        'high': float(row['high']),
                        'low': float(row['low']),
                        'close': float(row['close']),
                        'volume': int(row['volume'])
                    })
            else:
                # List format
                for bar in bars:
                    result.append({
                        'timestamp': bar.t,
                        'open': float(bar.o),
                        'high': float(bar.h),
                        'low': float(bar.l),
                        'close': float(bar.c),
                        'volume': int(bar.v)
                    })

            return result

        except Exception as e:
            logger.warning(f"Failed to get historical data for {symbol}: {e}")
            return []
    
    def _convert_alpaca_status(self, alpaca_status: str) -> OrderStatus:
        """Convert Alpaca order status to universal status"""
        status_map = {
            'pending_new': OrderStatus.PENDING,
            'new': OrderStatus.SUBMITTED,
            'filled': OrderStatus.FILLED,
            'partially_filled': OrderStatus.PARTIALLY_FILLED,
            'canceled': OrderStatus.CANCELLED,
            'rejected': OrderStatus.REJECTED
        }
        return status_map.get(alpaca_status, OrderStatus.PENDING)
    
    def _convert_alpaca_order(self, alpaca_order) -> Order:
        """Convert Alpaca order to universal order"""
        return Order(
            symbol=alpaca_order.symbol,
            quantity=float(alpaca_order.qty),
            side=OrderSide(alpaca_order.side),
            order_type=OrderType(alpaca_order.order_type),
            price=float(alpaca_order.limit_price) if alpaca_order.limit_price else None,
            stop_price=float(alpaca_order.stop_price) if alpaca_order.stop_price else None,
            time_in_force=alpaca_order.time_in_force,
            broker_order_id=alpaca_order.id,
            status=self._convert_alpaca_status(alpaca_order.status),
            filled_price=float(alpaca_order.filled_avg_price) if alpaca_order.filled_avg_price else None,
            filled_quantity=float(alpaca_order.filled_qty) if alpaca_order.filled_qty else None,
            created_at=alpaca_order.created_at,
            updated_at=alpaca_order.updated_at
        )

    def _is_24hr_stock(self, symbol: str) -> bool:
        """Check if stock supports Alpaca 24-hour trading"""
        # Alpaca 24-hour trading supported stocks (as of 2024)
        # Trading hours: Sunday 8 PM ET - Friday 8 PM ET
        ALPACA_24HR_STOCKS = {
            # Tech Giants
            'AAPL',   # Apple
            'MSFT',   # Microsoft
            'GOOGL',  # Google
            'GOOG',   # Google (Class C)
            'AMZN',   # Amazon
            'META',   # Meta/Facebook
            'NVDA',   # NVIDIA
            'TSLA',   # Tesla
            'NFLX',   # Netflix
            'AMD',    # AMD

            # Major ETFs
            'SPY',    # S&P 500 ETF
            'QQQ',    # Nasdaq 100 ETF
            'IWM',    # Russell 2000 ETF
            'DIA',    # Dow Jones ETF
            'VOO',    # Vanguard S&P 500 ETF

            # Other Popular Stocks
            'COIN',   # Coinbase
            'PLTR',   # Palantir
            'BABA',   # Alibaba
            'NIO',    # NIO
            'RIVN',   # Rivian
            'LCID',   # Lucid
            'F',      # Ford
            'GM',     # General Motors
            'DIS',    # Disney
            'BA',     # Boeing
            'UBER',   # Uber
            'LYFT',   # Lyft
            'SNAP',   # Snap
            'TWTR',   # Twitter (if still trading)
            'SQ',     # Block (Square)
            'PYPL',   # PayPal
            'SHOP',   # Shopify
            'ROKU',   # Roku
            'ZM',     # Zoom
            'DOCU',   # DocuSign
            'CRM',    # Salesforce
            'ORCL',   # Oracle
            'INTC',   # Intel
            'MU',     # Micron
            'QCOM',   # Qualcomm
        }

        return symbol.upper() in ALPACA_24HR_STOCKS

    def _is_overnight_session(self) -> bool:
        """Check if we're currently in Alpaca 24/5 overnight trading session.

        Alpaca 24/5 trading hours: Sunday 8 PM ET - Friday 8 PM ET
        Regular market hours: 9:30 AM - 4:00 PM ET (Mon-Fri)

        Overnight session = outside regular market hours but within 24/5 window
        """
        from datetime import datetime
        import pytz

        try:
            eastern = pytz.timezone('US/Eastern')
            now_et = datetime.now(eastern)

            weekday = now_et.weekday()  # 0=Monday, 6=Sunday
            hour = now_et.hour
            minute = now_et.minute
            time_value = hour * 100 + minute

            # Regular market hours: 9:30 AM - 4:00 PM ET (Mon-Fri)
            MARKET_OPEN = 930
            MARKET_CLOSE = 1600

            # If it's Saturday, no trading
            if weekday == 5:
                return False

            # Sunday: only after 8 PM ET
            if weekday == 6:
                return hour >= 20

            # Friday: until 8 PM ET
            if weekday == 4:
                if hour >= 20:
                    return False  # After Friday 8 PM = no trading
                elif time_value < MARKET_OPEN or time_value >= MARKET_CLOSE:
                    return True  # Friday overnight session

            # Mon-Thu: overnight if outside regular hours
            if time_value < MARKET_OPEN or time_value >= MARKET_CLOSE:
                return True

            return False

        except Exception as e:
            logger.warning(f"Error checking overnight session: {e}")
            return False
