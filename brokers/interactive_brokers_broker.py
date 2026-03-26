"""
Interactive Brokers Broker Implementation for PROMETHEUS Trading Platform
Requires TWS API installation and IB Gateway/TWS running
"""

import asyncio
import threading
import time
import json
import socket
import random
from decimal import Decimal
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

try:
    from ibapi.client import EClient
    from ibapi.wrapper import EWrapper
    from ibapi.contract import Contract
    from ibapi.order import Order as IBOrder
    from ibapi.common import TickerId, OrderId
    IB_AVAILABLE = True
except ImportError:
    IB_AVAILABLE = False
    EClient = object
    EWrapper = object
    class Contract:
        pass

    class IBOrder:
        pass

    TickerId = int
    OrderId = int

from .universal_broker_interface import (
    BrokerInterface, Order, Position, Account, 
    OrderSide, OrderType, OrderStatus
)

# Import enhanced error handling
from core.error_handling import (
    TradingError, ConnectionError, AuthenticationError, MarketDataError,
    OrderExecutionError, AccountAccessError, ErrorSeverity, ErrorCategory,
    ErrorContext, error_logger, error_recovery_manager, create_connection_error
)

logger = logging.getLogger(__name__)

if IB_AVAILABLE:
    class IBWrapper(EWrapper):
        """Interactive Brokers API Wrapper"""
        
        def __init__(self, broker):
            self.broker = broker
            
        def error(self, reqId: int, errorCode: int, errorString: str):
            """Handle errors with enhanced error code mapping"""
            # ── Informational codes (DEBUG) ────────────────────────────
            info_codes = {
                2104: "Market data farm connection is OK",
                2106: "A]Market data farm connection is broken",
                2108: "Market data farm connection is inactive",
                2158: "Sec-def data farm connection is OK",
                2119: "Market data farm is connecting",
            }
            # ── Connectivity restored (INFO) ──────────────────────────
            restored_codes = {1101, 1102, 2110}
            # ── Benign / expected warnings (WARNING once, not ERROR) ──
            benign_codes = {
                300: "Order-related notification",
                399: "Order message",
                2100: "API client has been unsubscribed from account data",
                2103: "Market data farm connection is broken",
                2105: "HMDS data farm connection is broken",
                2157: "Sec-def data farm connection is broken",
                10089: "Market data requires additional subscription",
                10090: "Part of requested market data is not subscribed",
                10167: "Requested market data is not subscribed",
                10197: "No market data during competing live session",
            }
            # ── Connection-loss codes that trigger reconnect ──────────
            reconnect_codes = {502, 504, 1100, 2159}

            if errorCode == 326:
                # Client ID already in use — pick a new random ID
                old_id = self.broker.client_id
                self.broker.client_id = random.randint(100, 999)
                logger.warning(f"IB Error 326: Client ID {old_id} in use — switching to {self.broker.client_id}")
                if hasattr(self.broker, 'connected'):
                    self.broker.connected = False
            elif errorCode in reconnect_codes:
                logger.warning(f"IB Error {errorCode}: {errorString}")
                if hasattr(self.broker, 'connected'):
                    self.broker.connected = False
            elif errorCode in restored_codes:
                logger.info(f"IB Info {errorCode}: {errorString}")
            elif errorCode in info_codes:
                logger.debug(f"IB Info {errorCode}: {errorString}")
            elif errorCode in benign_codes:
                logger.debug(f"IB Notice {errorCode}: {errorString}")
            else:
                # Genuine unexpected error
                logger.warning(f"IB Error {errorCode}: {errorString}")
            
        def nextValidId(self, orderId: int):
            """Receive next valid order ID"""
            self.broker.next_order_id = orderId
            
        def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
            """Receive account summary - ONLY use primary account"""
            # Get the primary account ID from config
            primary_account = self.broker.config.get('account_id', 'U21922116')
            
            # Only store data from the primary account (ignore other linked accounts)
            if account == primary_account or primary_account in account:
                if not hasattr(self.broker, 'account_data'):
                    self.broker.account_data = {}
                self.broker.account_data[tag] = value
                logger.debug(f"📊 IB accountSummary: {tag} = {value} ({currency})")
            else:
                # Skip data from other accounts
                pass

        def accountSummaryEnd(self, reqId: int):
            """Account summary complete"""
            logger.info(f"[CHECK] IB accountSummaryEnd for reqId {reqId}")

        def updateAccountValue(self, key: str, val: str, currency: str, accountName: str):
            """Receive account value updates (BETTER METHOD)"""
            if not hasattr(self.broker, 'account_values'):
                self.broker.account_values = {}
            self.broker.account_values[key] = val
            logger.debug(f"💰 IB updateAccountValue: {key} = {val} ({currency}) for {accountName}")

        def accountDownloadEnd(self, accountName: str):
            """Account download complete"""
            logger.info(f"[CHECK] IB accountDownloadEnd for {accountName}")

        def position(self, account: str, contract: Contract, position: float, avgCost: float):
            """Receive position data"""
            if not hasattr(self.broker, 'positions_data'):
                self.broker.positions_data = {}
            self.broker.positions_data[contract.symbol] = {
                'symbol': contract.symbol,
                'quantity': position,
                'avg_price': avgCost,
                'contract': contract
            }
            
        def orderStatus(self, orderId: int, status: str, filled: float, remaining: float, 
                       avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, 
                       clientId: int, whyHeld: str, mktCapPrice: float):
            """Receive order status updates"""
            if not hasattr(self.broker, 'order_status'):
                self.broker.order_status = {}
            self.broker.order_status[orderId] = {
                'status': status,
                'filled': filled,
                'remaining': remaining,
                'avg_fill_price': avgFillPrice
            }
            
        def tickPrice(self, reqId: int, tickType: int, price: float, attrib):
            """Receive market data ticks"""
            if not hasattr(self.broker, 'market_data'):
                self.broker.market_data = {}
            if reqId not in self.broker.market_data:
                self.broker.market_data[reqId] = {}
                
            # Map tick types to readable names
            tick_map = {
                1: 'bid',
                2: 'ask',
                4: 'last',
                6: 'high',
                7: 'low',
                9: 'close'
            }
            
            if tickType in tick_map:
                self.broker.market_data[reqId][tick_map[tickType]] = price

        def openOrder(self, orderId: int, contract: Contract, order: IBOrder, orderState):
            """Track all open orders"""
            if not hasattr(self.broker, 'open_orders'):
                self.broker.open_orders = {}
            
            self.broker.open_orders[orderId] = {
                'contract': contract,
                'order': order,
                'order_state': orderState,
                'timestamp': time.time()
            }
            logger.info(f"📋 IB Open Order: {orderId} - {contract.symbol} {order.action} {order.totalQuantity}")

        def execDetails(self, reqId: int, contract: Contract, execution):
            """Track execution details for fill analysis"""
            if not hasattr(self.broker, 'executions'):
                self.broker.executions = []
            
            execution_data = {
                'req_id': reqId,
                'contract': contract,
                'execution': execution,
                'timestamp': time.time()
            }
            self.broker.executions.append(execution_data)
            
            # Track execution for performance monitoring
            if hasattr(self.broker, 'execution_tracker') and self.broker.execution_tracker:
                # Find the order ID from the execution
                order_id = str(execution.orderId) if hasattr(execution, 'orderId') else str(reqId)
                self.broker.execution_tracker.record_order_fill(
                    order_id=order_id,
                    fill_price=Decimal(str(execution.price)),
                    fill_time=time.time()
                )
            
            logger.info(f"✅ IB Execution: {contract.symbol} {execution.shares} @ {execution.price}")

        def updatePortfolio(self, contract: Contract, position: float, marketPrice: float, 
                          marketValue: float, avgCost: float, unrealizedPNL: float, 
                          realizedPNL: float, accountName: str):
            """Real-time portfolio updates with P&L"""
            if not hasattr(self.broker, 'portfolio_updates'):
                self.broker.portfolio_updates = {}
            
            self.broker.portfolio_updates[contract.symbol] = {
                'position': position,
                'market_price': marketPrice,
                'market_value': marketValue,
                'avg_cost': avgCost,
                'unrealized_pnl': unrealizedPNL,
                'realized_pnl': realizedPNL,
                'account': accountName,
                'timestamp': time.time()
            }
            logger.debug(f"💰 IB Portfolio Update: {contract.symbol} - Pos: {position}, P&L: ${unrealizedPNL:.2f}")

class InteractiveBrokersBroker(BrokerInterface):
    """Interactive Brokers broker implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        if not IB_AVAILABLE:
            raise ImportError("Interactive Brokers API not available. Install with: pip install ibapi")
            
        self.config = config
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 4002)  # 4002=Gateway Live, 4001=Gateway Paper, 7497=TWS Paper, 7496=TWS Live
        # Use base client ID starting at 10 to avoid conflicts with TWS/other apps (which often use 0-5)
        # Will auto-increment if conflicts occur
        import random
        default_client_id = config.get('client_id', random.randint(10, 99))
        self.client_id = default_client_id
        self.base_client_id = self.client_id
        self.paper_trading = config.get('paper_trading', False)  # Default to live trading
        
        # Initialize IB API components
        self.wrapper = IBWrapper(self)
        self.client = EClient(self.wrapper)
        
        self.connected = False
        self.next_order_id = None
        self.req_id_counter = 1000
        
        # Enhanced connection management with improved resilience
        self.connection_retry_count = 0
        self.max_retry_attempts = 10  # Increased from 5
        self.retry_delay_base = 2.0  # Increased base delay in seconds
        self.last_connection_attempt = None
        self.connection_health_check_interval = 30  # Reduced from 60 for faster detection
        self.last_health_check = None
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3  # Reset after this many failures
        self._heartbeat_task = None
        self._auto_reconnect_enabled = True
        
        # Data storage
        self.account_data = {}
        self.account_values = {}  # For updateAccountValue callback
        self.positions_data = {}
        self.order_status = {}
        self.market_data = {}
        
        # Enhanced tracking (initialized by callbacks)
        self.open_orders = {}
        self.executions = []
        self.portfolio_updates = {}
        
        # Performance tracking integration
        try:
            from monitoring.ib_execution_tracker import ib_execution_tracker
            self.execution_tracker = ib_execution_tracker
            logger.info("✅ IB Execution Tracker integrated")
        except ImportError:
            logger.warning("⚠️ IB Execution Tracker not available")
            self.execution_tracker = None

        # Load overnight trading configuration
        self.overnight_config = self._load_overnight_config()
        self.overnight_trades_count = 0  # Track trades per overnight session
        self.current_session = None  # Track current trading session
        self.last_session_check = None  # Last time we checked session

        # Session performance tracking
        self.session_stats = {
            "overnight": {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0},
            "pre_market": {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0},
            "regular": {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0},
            "after_hours": {"trades": 0, "wins": 0, "losses": 0, "pnl": 0.0}
        }
        
    async def connect(self) -> bool:
        """Connect to Interactive Brokers with comprehensive validation"""
        try:
            # Pre-connection validation
            await self._validate_connection_prerequisites()

            # Test port connectivity
            if not await self._test_port_connectivity():
                raise ConnectionError(
                    message=f"Cannot connect to {self.host}:{self.port} - port not accessible",
                    broker="IB"
                )

            # Connect to IB Gateway/TWS with timeout protection
            logger.info(f"Connecting to IB at {self.host}:{self.port} (client_id: {self.client_id})")

            # Use a thread with timeout to prevent blocking
            connect_result = [False]
            connect_error = [None]

            def do_connect():
                try:
                    # Try connecting with auto-increment on client ID conflict
                    max_client_id_attempts = 5
                    for attempt in range(max_client_id_attempts):
                        try:
                            self.client.connect(self.host, self.port, self.client_id)
                            connect_result[0] = True
                            break
                        except Exception as conn_err:
                            if "already in use" in str(conn_err).lower() and attempt < max_client_id_attempts - 1:
                                self.client_id += 1
                                logger.warning(f"[IB] Client ID conflict, trying ID {self.client_id}")
                                time.sleep(0.3)
                                continue
                            else:
                                raise conn_err
                except Exception as e:
                    connect_error[0] = e

            connect_thread = threading.Thread(target=do_connect, daemon=True)
            connect_thread.start()
            connect_thread.join(timeout=5)  # 5 second timeout for initial connect call

            if connect_thread.is_alive():
                # Connect() returned but thread still alive - this is OK, the API needs to run
                logger.info("IB connect() initiated - starting message loop...")

            if connect_error[0]:
                logger.warning(f"IB connect() call had error: {connect_error[0]}")
                raise ConnectionError(
                    message=f"IB Gateway connection error: {connect_error[0]}",
                    broker="IB"
                )

            if connect_error[0]:
                raise ConnectionError(
                    message=f"IB connect failed: {connect_error[0]}",
                    broker="IB"
                )

            # Start the client in a separate thread
            api_thread = threading.Thread(target=self.client.run, daemon=True)
            api_thread.start()

            # Wait for connection with timeout
            if not await self._wait_for_connection():
                raise ConnectionError(
                    message="Connection timeout - TWS/Gateway may not be running or API not enabled",
                    broker="IB"
                )

            # Validate connection
            await self._validate_connection()

            self.connected = True
            self.connection_retry_count = 0  # Reset retry count on successful connection

            logger.info(f"Connected to Interactive Brokers {'Paper' if self.paper_trading else 'Live'}")
            return True

        except ConnectionError as e:
            await error_logger.log_error(e)
            logger.error(f"IB Connection failed: {e.message}")
            return False
        except Exception as e:
            connection_error = create_connection_error("IB", e)
            await error_logger.log_error(connection_error)
            logger.error(f"IB Connection error: {e}")
            return False
    
    async def _validate_connection_prerequisites(self):
        """Validate prerequisites before connecting"""
        if not IB_AVAILABLE:
            raise ConnectionError(
                message="IB API not available. Install with: pip install ibapi",
                broker="IB"
            )
        
        if not self.host or not self.port:
            raise ConnectionError(
                message="Invalid host or port configuration",
                broker="IB"
            )
        
        # Check if TWS/Gateway is likely running by testing common ports
        common_ports = [7497, 7496, 4001, 4002]  # TWS paper, TWS live, Gateway paper, Gateway live
        if self.port not in common_ports:
            logger.warning(f"Using non-standard port {self.port}. Common ports are: {common_ports}")
    
    async def _test_port_connectivity(self) -> bool:
        """Test if port is accessible"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.host, self.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Port connectivity test failed: {e}")
            return False
    
    async def _wait_for_connection(self, timeout: int = 30) -> bool:
        """Wait for IB connection to establish"""
        start_time = time.time()
        check_count = 0
        while not self.client.isConnected() and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.2)
            check_count += 1
            if check_count % 25 == 0:  # Log every 5 seconds
                logger.info(f"⏳ Waiting for IB connection... ({int(time.time() - start_time)}s)")

        if self.client.isConnected():
            logger.info("✅ IB client connected - waiting for order ID...")
            # Wait for next valid order ID (longer timeout)
            start_time = time.time()
            while self.next_order_id is None and (time.time() - start_time) < 10:
                await asyncio.sleep(0.2)

            if self.next_order_id is not None:
                logger.info(f"✅ IB ready - next order ID: {self.next_order_id}")
                return True
            else:
                logger.warning("⚠️ Connected but no order ID received")
                return True  # Still return true, connection is established

        logger.warning(f"⚠️ IB connection not established after {timeout}s")
        return False
    
    async def _validate_connection(self):
        """Validate that connection is working properly"""
        try:
            # Test account access
            account_id = self.config.get('account_id', '')
            if account_id:
                self.client.reqAccountUpdates(True, account_id)
                await asyncio.sleep(2)
                self.client.reqAccountUpdates(False, account_id)
            
            # Test market data access
            contract = Contract()
            contract.symbol = "AAPL"
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            
            req_id = self.req_id_counter
            self.req_id_counter += 1
            self.client.reqMktData(req_id, contract, "", False, False, [])
            await asyncio.sleep(2)
            self.client.cancelMktData(req_id)
            
            logger.info("✅ IB connection validation successful")
            
        except Exception as e:
            raise ConnectionError(
                message=f"Connection validation failed: {str(e)}",
                broker="IB",
                original_error=e
            )
    
    async def disconnect(self):
        """Disconnect from Interactive Brokers"""
        if self.client.isConnected():
            self.client.disconnect()
        self.connected = False
        logger.info("[CHECK] Disconnected from Interactive Brokers")

    async def check_connection(self) -> bool:
        """Check if connection is still alive and reconnect if needed with exponential backoff"""
        try:
            current_time = time.time()
            
            # Check if we need a health check
            if (self.last_health_check is None or 
                current_time - self.last_health_check > self.connection_health_check_interval):
                self.last_health_check = current_time
                logger.debug("🔍 Performing IB connection health check")
            
            if not self.client.isConnected():
                logger.warning("[WARNING]️ IB connection lost - attempting reconnection...")
                self.connected = False

                # Check if we should attempt reconnection
                if self.connection_retry_count >= self.max_retry_attempts:
                    logger.error(f"[ERROR] Max reconnection attempts ({self.max_retry_attempts}) reached. Manual intervention required.")
                    return False

                # Calculate exponential backoff delay
                delay = self.retry_delay_base * (2 ** self.connection_retry_count)
                logger.info(f"⏳ Waiting {delay:.1f}s before reconnection attempt {self.connection_retry_count + 1}/{self.max_retry_attempts}")
                
                await asyncio.sleep(delay)
                self.connection_retry_count += 1
                self.last_connection_attempt = current_time

                # Attempt to reconnect
                success = await self.connect()
                if success:
                    logger.info("[CHECK] IB reconnection successful")
                    self.connection_retry_count = 0  # Reset on successful connection
                    
                    # Track successful reconnection
                    if self.execution_tracker:
                        self.execution_tracker.record_connection_event(
                            connected=True,
                            retry_count=self.connection_retry_count
                        )
                    
                    return True
                else:
                    logger.error(f"[ERROR] IB reconnection failed (attempt {self.connection_retry_count})")
                    
                    # Track failed reconnection
                    if self.execution_tracker:
                        self.execution_tracker.record_connection_event(
                            connected=False,
                            retry_count=self.connection_retry_count,
                            error_code=502,  # Connection lost
                            error_message="Reconnection failed"
                        )
                    
                    return False

            # Connection is alive, reset retry count and failures
            if self.connection_retry_count > 0:
                logger.info("[CHECK] IB connection restored - resetting retry count")
                self.connection_retry_count = 0
            self.consecutive_failures = 0
                
            return True
        except Exception as e:
            logger.error(f"[ERROR] Error checking IB connection: {e}")
            self.consecutive_failures += 1
            return False
    
    async def start_heartbeat_monitor(self):
        """Start background heartbeat monitor for connection stability"""
        if self._heartbeat_task is not None:
            return  # Already running
        
        async def heartbeat_loop():
            """Background heartbeat loop"""
            while self._auto_reconnect_enabled:
                try:
                    await asyncio.sleep(self.connection_health_check_interval)
                    if self.connected:
                        is_alive = await self.check_connection()
                        if not is_alive and self._auto_reconnect_enabled:
                            logger.warning("[HEARTBEAT] Connection lost, auto-reconnect will handle it")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"[HEARTBEAT] Error in heartbeat loop: {e}")
        
        self._heartbeat_task = asyncio.create_task(heartbeat_loop())
        logger.info("[HEARTBEAT] IB connection heartbeat monitor started")
    
    async def stop_heartbeat_monitor(self):
        """Stop background heartbeat monitor"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None
            logger.info("[HEARTBEAT] IB connection heartbeat monitor stopped")
    
    async def get_account(self) -> Account:
        """Get account information with multiple fallback methods"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")

        logger.info("🔍 Requesting IB account data using multiple methods...")

        # Initialize data structures
        if not hasattr(self, 'account_data'):
            self.account_data = {}
        if not hasattr(self, 'account_values'):
            self.account_values = {}

        # METHOD 1: Request account updates (BEST - real-time updates)
        account_id = self.config.get('account_id', '')
        if account_id:
            logger.info(f"📡 METHOD 1: Requesting account updates for {account_id}")
            self.client.reqAccountUpdates(True, account_id)
            await asyncio.sleep(3)  # Wait for updates
            self.client.reqAccountUpdates(False, account_id)  # Stop updates

        # METHOD 2: Request account summary (fallback)
        logger.info("📡 METHOD 2: Requesting account summary")
        self.client.reqAccountSummary(9001, "All", "TotalCashValue,NetLiquidation,BuyingPower,AvailableFunds")
        await asyncio.sleep(2)
        self.client.cancelAccountSummary(9001)

        # Extract values with multiple fallback options
        logger.info(f"📊 account_data: {self.account_data}")
        logger.info(f"💰 account_values: {self.account_values}")

        # Try to get values from account_values first (more reliable)
        buying_power = 0
        cash = 0
        portfolio_value = 0

        # Get buying power
        if 'BuyingPower' in self.account_values:
            buying_power = float(self.account_values['BuyingPower'])
        elif 'AvailableFunds' in self.account_values:
            buying_power = float(self.account_values['AvailableFunds'])
        elif 'BuyingPower' in self.account_data:
            buying_power = float(self.account_data['BuyingPower'])

        # Get cash
        if 'TotalCashValue' in self.account_values:
            cash = float(self.account_values['TotalCashValue'])
        elif 'CashBalance' in self.account_values:
            cash = float(self.account_values['CashBalance'])
        elif 'TotalCashValue' in self.account_data:
            cash = float(self.account_data['TotalCashValue'])

        # Get portfolio value (net liquidation)
        if 'NetLiquidation' in self.account_values:
            portfolio_value = float(self.account_values['NetLiquidation'])
        elif 'NetLiquidation' in self.account_data:
            portfolio_value = float(self.account_data['NetLiquidation'])

        # METHOD 3: Calculate from positions if still zero
        if portfolio_value == 0:
            logger.info("📡 METHOD 3: Calculating from positions")
            positions = await self.get_positions()
            positions_value = sum(abs(p.market_value) for p in positions)
            portfolio_value = cash + positions_value
            logger.info(f"💰 Calculated portfolio: ${cash:.2f} cash + ${positions_value:.2f} positions = ${portfolio_value:.2f}")

        # If still zero, use a minimum value to prevent division by zero
        if portfolio_value == 0 and cash == 0:
            logger.warning("[WARNING]️ All methods returned $0! Using minimum $1 to prevent errors")
            portfolio_value = 1
            cash = 1
            buying_power = 1

        logger.info(f"[CHECK] Final IB Account Values:")
        logger.info(f"   💵 Cash: ${cash:.2f}")
        logger.info(f"   💰 Portfolio Value: ${portfolio_value:.2f}")
        logger.info(f"   🔥 Buying Power: ${buying_power:.2f}")

        return Account(
            account_id=self.config.get('account_id', 'IB_ACCOUNT'),
            buying_power=buying_power,
            cash=cash,
            portfolio_value=portfolio_value,
            equity=portfolio_value,
            day_trade_count=0,  # IB doesn't provide this directly
            pattern_day_trader=False
        )
    
    async def get_positions(self) -> List[Position]:
        """Get all positions"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")
        
        # Request positions
        self.client.reqPositions()
        
        # Wait for data
        await asyncio.sleep(2)
        
        positions = []
        for symbol, pos_data in self.positions_data.items():
            if pos_data['quantity'] != 0:  # Only include non-zero positions
                positions.append(Position(
                    symbol=symbol,
                    quantity=pos_data['quantity'],
                    avg_price=pos_data['avg_price'],
                    market_value=pos_data['quantity'] * pos_data['avg_price'],  # Approximate
                    unrealized_pnl=0,  # Would need current price to calculate
                    unrealized_pnl_percent=0,
                    side="long" if pos_data['quantity'] > 0 else "short"
                ))
        
        return positions
    
    async def get_position(self, symbol: str) -> Optional[Position]:
        """Get position for specific symbol"""
        positions = await self.get_positions()
        for pos in positions:
            if pos.symbol == symbol:
                return pos
        return None
    
    async def submit_order(self, order: Order) -> Order:
        """Submit an order with 24/5 extended hours support, overnight validation, and risk management"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")

        if self.next_order_id is None:
            raise RuntimeError("No valid order ID available")

        # Pre-trade risk validation
        try:
            # Get account balance for risk validation
            account = await self.get_account()
            account_balance = Decimal(str(account.equity or 0))
            
            # Get current positions for risk calculation
            positions = await self.get_positions()
            positions_dict = {pos.symbol: pos for pos in positions}
            
            # Import and use existing RiskManager
            from core.trading_engine import RiskManager
            risk_config = {
                'max_position_size': 15000,  # 15% of typical account
                'max_daily_loss': 1500,      # 10% of typical account
                'max_portfolio_risk': 0.03,  # 3%
                'max_single_position_risk': 0.15  # 15%
            }
            risk_manager = RiskManager(risk_config)
            
            # Validate order against risk parameters
            is_valid, message = await risk_manager.validate_order(order, account_balance, positions_dict)
            if not is_valid:
                logger.error(f"🚨 Risk validation failed: {message}")
                raise RuntimeError(f"Risk validation failed: {message}")
            
            logger.info(f"✅ Risk validation passed: {message}")
            
        except Exception as e:
            logger.error(f"Risk validation error: {e}")
            raise RuntimeError(f"Risk validation error: {str(e)}")

        # Get current session
        current_session = self._get_current_trading_session()

        # Overnight session validation
        if current_session == "overnight":
            if not self.overnight_config.get('enabled', True):
                raise RuntimeError("Overnight trading is disabled")

            if not self._is_overnight_approved_symbol(order.symbol):
                raise RuntimeError(f"Symbol {order.symbol} not approved for overnight trading")

            if not self._check_overnight_limits():
                raise RuntimeError("Overnight trade limit reached for this session")

            # Increment overnight counter
            self.overnight_trades_count += 1
            logger.info(f"🌙 Overnight trade {self.overnight_trades_count}/{self.overnight_config.get('risk_parameters', {}).get('max_trades_per_session', 3)}")

        # Create IB contract based on symbol type
        contract = self._create_contract(order.symbol)

        # Create IB order
        ib_order = IBOrder()
        ib_order.action = "BUY" if order.side == OrderSide.BUY else "SELL"
        ib_order.totalQuantity = order.quantity
        ib_order.orderType = order.order_type.value.upper()

        # Compatibility: newer IB venues reject legacy-only flags if populated.
        if hasattr(ib_order, 'eTradeOnly'):
            ib_order.eTradeOnly = False
        if hasattr(ib_order, 'firmQuoteOnly'):
            ib_order.firmQuoteOnly = False

        # CRITICAL: Enable extended hours trading (24/5 support)
        ib_order.outsideRth = True  # Allow trading outside regular hours

        # Set Time-in-Force based on current session
        ib_order.tif = "DAY"  # Day orders work for all sessions

        # Log session-specific information
        if current_session == "overnight":
            logger.info(f"🌙 Overnight order: {order.symbol} qty={order.quantity}")
        elif current_session == "pre_market":
            logger.info(f"🌅 Pre-market order: {order.symbol} qty={order.quantity}")
        elif current_session == "after_hours":
            logger.info(f"🌆 After-hours order: {order.symbol} qty={order.quantity}")
        else:
            logger.info(f"📈 Regular hours order: {order.symbol} qty={order.quantity}")

        if order.order_type == OrderType.LIMIT:
            ib_order.lmtPrice = order.price
        elif order.order_type == OrderType.STOP:
            ib_order.auxPrice = order.stop_price
        elif order.order_type == OrderType.STOP_LIMIT:
            ib_order.lmtPrice = order.price
            ib_order.auxPrice = order.stop_price

        # Submit order
        order_id = self.next_order_id
        self.client.placeOrder(order_id, contract, ib_order)
        self.next_order_id += 1

        # Track order submission for performance monitoring
        if self.execution_tracker:
            self.execution_tracker.record_order_submission(
                order_id=str(order_id),
                symbol=order.symbol,
                side=order.side.value,
                quantity=order.quantity,
                order_type=order.order_type.value,
                expected_price=order.price
            )

        # Update order
        order.broker_order_id = str(order_id)
        order.status = OrderStatus.SUBMITTED
        order.created_at = datetime.now()

        return order

    async def submit_bracket_order(self, symbol: str, quantity: int, side: str, 
                                 take_profit_price: float, stop_loss_price: float,
                                 time_in_force: str = "DAY") -> Dict[str, Any]:
        """Submit a bracket order (entry + take profit + stop loss) using IB's native bracket order support"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")

        if self.next_order_id is None:
            raise RuntimeError("No valid order ID available")

        try:
            # Create contract (auto-detects forex vs stock)
            contract = self._create_contract(symbol)

            # Parent order (entry)
            parent_order = IBOrder()
            parent_order.action = side.upper()
            parent_order.orderType = "MKT"  # Market order for entry
            parent_order.totalQuantity = quantity
            parent_order.transmit = False  # Don't transmit until all orders are ready
            parent_order.tif = time_in_force

            # Take profit order (child)
            take_profit_order = IBOrder()
            take_profit_order.action = "SELL" if side.upper() == "BUY" else "BUY"
            take_profit_order.orderType = "LMT"
            take_profit_order.totalQuantity = quantity
            take_profit_order.lmtPrice = take_profit_price
            take_profit_order.parentId = self.next_order_id  # Link to parent
            take_profit_order.transmit = False

            # Stop loss order (child)
            stop_loss_order = IBOrder()
            stop_loss_order.action = "SELL" if side.upper() == "BUY" else "BUY"
            stop_loss_order.orderType = "STP"
            stop_loss_order.totalQuantity = quantity
            stop_loss_order.auxPrice = stop_loss_price
            stop_loss_order.parentId = self.next_order_id  # Link to parent
            stop_loss_order.transmit = True  # Transmit when this is placed

            # Place parent order
            parent_id = self.next_order_id
            self.client.placeOrder(parent_id, contract, parent_order)
            self.next_order_id += 1

            # Place take profit order
            take_profit_id = self.next_order_id
            self.client.placeOrder(take_profit_id, contract, take_profit_order)
            self.next_order_id += 1

            # Place stop loss order (this will transmit all orders)
            stop_loss_id = self.next_order_id
            self.client.placeOrder(stop_loss_id, contract, stop_loss_order)
            self.next_order_id += 1

            logger.info(f"🎯 IB Bracket Order placed:")
            logger.info(f"   Parent: {parent_id} - {symbol} {side} {quantity} @ MKT")
            logger.info(f"   Take Profit: {take_profit_id} - {symbol} @ ${take_profit_price}")
            logger.info(f"   Stop Loss: {stop_loss_id} - {symbol} @ ${stop_loss_price}")

            return {
                "success": True,
                "parent_order_id": parent_id,
                "take_profit_order_id": take_profit_id,
                "stop_loss_order_id": stop_loss_id,
                "symbol": symbol,
                "quantity": quantity,
                "side": side,
                "take_profit_price": take_profit_price,
                "stop_loss_price": stop_loss_price,
                "message": f"Bracket order for {symbol} submitted successfully"
            }

        except Exception as e:
            logger.error(f"Bracket order submission failed: {e}")
            raise RuntimeError(f"Bracket order submission failed: {str(e)}")

    async def submit_trailing_stop(self, symbol: str, quantity: int, side: str,
                                 trail_percent: Optional[float] = None,
                                 trail_amount: Optional[float] = None,
                                 time_in_force: str = "GTC") -> Dict[str, Any]:
        """Submit a trailing stop order using IB's native trailing stop support"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")

        if self.next_order_id is None:
            raise RuntimeError("No valid order ID available")

        if not trail_percent and not trail_amount:
            raise ValueError("Either trail_percent or trail_amount must be specified")

        try:
            # Create contract (auto-detects forex vs stock)
            contract = self._create_contract(symbol)

            # Create trailing stop order
            trailing_order = IBOrder()
            trailing_order.action = side.upper()
            trailing_order.orderType = "TRAIL"
            trailing_order.totalQuantity = quantity
            trailing_order.tif = time_in_force

            if trail_percent:
                trailing_order.trailingPercent = trail_percent
                logger.info(f"📈 IB Trailing Stop: {symbol} {side} {quantity} - {trail_percent}% trail")
            else:
                trailing_order.auxPrice = trail_amount
                logger.info(f"📈 IB Trailing Stop: {symbol} {side} {quantity} - ${trail_amount} trail")

            # Place order
            order_id = self.next_order_id
            self.client.placeOrder(order_id, contract, trailing_order)
            self.next_order_id += 1

            logger.info(f"✅ IB Trailing Stop Order placed: {order_id}")

            return {
                "success": True,
                "order_id": order_id,
                "symbol": symbol,
                "quantity": quantity,
                "side": side,
                "trail_percent": trail_percent,
                "trail_amount": trail_amount,
                "message": f"Trailing stop order for {symbol} submitted successfully"
            }

        except Exception as e:
            logger.error(f"Trailing stop order submission failed: {e}")
            raise RuntimeError(f"Trailing stop order submission failed: {str(e)}")
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            if not self.connected:
                raise RuntimeError("Not connected to Interactive Brokers")
            
            self.client.cancelOrder(int(order_id))
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to cancel IB order {order_id}: {e}")
            return False
    
    async def get_order(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        # IB doesn't provide a direct way to get a single order
        # Would need to implement order tracking
        return None
    
    async def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
        """Get orders, optionally filtered by status"""
        # Request all open orders
        self.client.reqAllOpenOrders()
        await asyncio.sleep(1)
        
        # Convert IB orders to universal format
        orders = []
        # Implementation would depend on tracking orders in wrapper
        return orders
    
    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")
        
        # Create contract (auto-detects forex vs stock)
        contract = self._create_contract(symbol)

        # Request market data
        req_id = self.req_id_counter
        self.req_id_counter += 1
        
        self.client.reqMktData(req_id, contract, "", False, False, [])
        
        # Wait for data
        await asyncio.sleep(2)
        
        data = self.market_data.get(req_id, {})
        
        return {
            'symbol': symbol,
            'price': data.get('last', 0),
            'bid': data.get('bid', 0),
            'ask': data.get('ask', 0),
            'high': data.get('high', 0),
            'low': data.get('low', 0),
            'close': data.get('close', 0),
            'timestamp': datetime.now()
        }
    
    async def get_historical_data(self, symbol: str, timeframe: str = '1Min', limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical market data"""
        if not self.connected:
            raise RuntimeError("Not connected to Interactive Brokers")

        # Create contract (auto-detects forex vs stock)
        contract = self._create_contract(symbol)

        # Convert timeframe to IB format (with space)
        timeframe_map = {
            '1Min': '1 min',
            '5Min': '5 mins',
            '15Min': '15 mins',
            '30Min': '30 mins',
            '1Hour': '1 hour',
            '1Day': '1 day'
        }
        bar_size = timeframe_map.get(timeframe, '1 min')

        # Request historical data
        req_id = self.req_id_counter
        self.req_id_counter += 1

        duration = "1 D"  # 1 day of data

        # Forex uses MIDPOINT, stocks use TRADES
        what_to_show = "MIDPOINT" if contract.secType == "CASH" else "TRADES"
        self.client.reqHistoricalData(
            req_id, contract, "", duration, bar_size, what_to_show, 1, 1, False, []
        )

        # Wait for data (would need proper implementation in wrapper)
        await asyncio.sleep(3)

        # Return empty list for now - would need proper historical data handling
        return []

    def _get_current_trading_session(self) -> str:
        """
        Determine current IB trading session for 24/5 trading
        Returns: 'overnight', 'pre_market', 'regular', 'after_hours', or 'closed'
        """
        try:
            import pytz
            from datetime import datetime

            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
            hour = now_et.hour
            minute = now_et.minute
            weekday = now_et.weekday()  # 0=Monday, 6=Sunday

            # Saturday - no trading
            if weekday == 5:
                return "closed"

            # Sunday evening - overnight session starts at 8:00 PM
            if weekday == 6:
                if hour >= 20:
                    return "overnight"
                else:
                    return "closed"

            # Overnight: 8:00 PM - 3:50 AM (spans midnight)
            if hour >= 20 or hour < 4 or (hour == 3 and minute <= 50):
                return "overnight"

            # Pre-market: 4:00 AM - 9:30 AM
            if hour == 4 or (4 < hour < 9) or (hour == 9 and minute < 30):
                return "pre_market"

            # Regular hours: 9:30 AM - 4:00 PM
            if (hour == 9 and minute >= 30) or (9 < hour < 16):
                return "regular"

            # After-hours: 4:00 PM - 8:00 PM
            if hour >= 16 and hour < 20:
                return "after_hours"

            return "closed"

        except Exception as e:
            logger.error(f"[ERROR] Session detection error: {e}")
            return "regular"  # Default to regular hours on error

    def _is_ib_trading_available(self) -> bool:
        """Check if IB trading is currently available (24/5 support)"""
        session = self._get_current_trading_session()
        return session in ["overnight", "pre_market", "regular", "after_hours"]

    def _load_overnight_config(self) -> Dict[str, Any]:
        """Load overnight trading configuration"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "overnight_trading_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    logger.info("[CHECK] Overnight trading config loaded")
                    return config.get('overnight_trading', {})
            else:
                logger.warning("[WARNING]️ Overnight config not found, using defaults")
                return self._get_default_overnight_config()
        except Exception as e:
            logger.error(f"[ERROR] Failed to load overnight config: {e}")
            return self._get_default_overnight_config()

    def _get_default_overnight_config(self) -> Dict[str, Any]:
        """Get default overnight trading configuration"""
        return {
            "enabled": True,
            "risk_parameters": {
                "max_position_size_pct": 7.5,
                "stop_loss_pct": 7.0,
                "take_profit_pct": 10.0,
                "max_trades_per_session": 3
            },
            "approved_symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "SPY", "QQQ", "DIA"]
        }

    def _is_overnight_approved_symbol(self, symbol: str) -> bool:
        """Check if symbol is approved for overnight trading"""
        approved = self.overnight_config.get('approved_symbols', [])
        return symbol in approved

    def _check_overnight_limits(self) -> bool:
        """Check if overnight trading limits are reached"""
        max_trades = self.overnight_config.get('risk_parameters', {}).get('max_trades_per_session', 3)
        return self.overnight_trades_count < max_trades

    def _reset_overnight_counter(self):
        """Reset overnight trade counter (call at session start)"""
        self.overnight_trades_count = 0

    def _create_contract(self, symbol: str) -> Contract:
        """Create IB contract based on symbol type (stock or forex)"""
        contract = Contract()
        
        # Check if it's a forex pair (6 characters, no numbers)
        if len(symbol) == 6 and symbol.isalpha() and symbol.upper() in self._get_forex_pairs():
            # Forex contract
            contract.symbol = symbol[:3]  # Base currency (e.g., EUR from EURUSD)
            contract.secType = "CASH"
            contract.exchange = "IDEALPRO"
            contract.currency = symbol[3:]  # Quote currency (e.g., USD from EURUSD)
            logger.info(f"🌍 Forex contract: {symbol} ({contract.symbol}/{contract.currency})")
        else:
            # Stock contract
            contract.symbol = symbol
            contract.secType = "STK"
            contract.exchange = "SMART"
            contract.currency = "USD"
            logger.info(f"📈 Stock contract: {symbol}")
        
        return contract

    def _get_forex_pairs(self) -> List[str]:
        """Get list of approved forex pairs"""
        try:
            config_path = Path(__file__).parent.parent / "config" / "forex_trading_config.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('forex_trading', {}).get('approved_pairs', [])
        except Exception as e:
            logger.error(f"[ERROR] Failed to load forex config: {e}")
        
        # Default forex pairs (majors + crosses — matches launcher watchlist)
        return [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD",
            "EURGBP", "EURJPY", "GBPJPY", "EURCHF", "GBPCHF",
            "AUDJPY", "CADJPY", "EURAUD", "EURCAD", "GBPAUD",
            "GBPCAD", "AUDCAD", "AUDCHF", "CADCHF", "NZDJPY",
        ]

    def check_session_transition(self) -> bool:
        """
        Check if trading session has changed and handle transition
        Returns True if session changed, False otherwise
        """
        try:
            new_session = self._get_current_trading_session()

            # First time check
            if self.current_session is None:
                self.current_session = new_session
                logger.info(f"🎯 Initial session: {new_session.upper()}")
                return False

            # Session changed
            if new_session != self.current_session:
                old_session = self.current_session
                self.current_session = new_session

                logger.info(f"🔄 SESSION TRANSITION: {old_session.upper()} → {new_session.upper()}")

                # Handle session-specific transitions
                if new_session == "overnight":
                    self._reset_overnight_counter()
                    logger.info("🌙 Overnight session started - limits reset")

                elif new_session == "pre_market":
                    logger.info("🌅 Pre-market session started")

                elif new_session == "regular":
                    logger.info("📈 Regular market hours started")

                elif new_session == "after_hours":
                    logger.info("🌆 After-hours session started")

                elif new_session == "closed":
                    logger.info("⏸️ Market closed - no trading")
                    self._log_session_stats(old_session)

                return True

            return False

        except Exception as e:
            logger.error(f"[ERROR] Session transition check failed: {e}")
            return False

    def _log_session_stats(self, session: str):
        """Log statistics for completed session"""
        if session in self.session_stats:
            stats = self.session_stats[session]
            if stats['trades'] > 0:
                win_rate = (stats['wins'] / stats['trades']) * 100
                logger.info(f"📊 {session.upper()} Session Stats:")
                logger.info(f"   Trades: {stats['trades']}")
                logger.info(f"   Wins: {stats['wins']} | Losses: {stats['losses']}")
                logger.info(f"   Win Rate: {win_rate:.1f}%")
                logger.info(f"   P&L: ${stats['pnl']:.2f}")

    def update_session_stats(self, session: str, win: bool, pnl: float):
        """Update statistics for a trading session"""
        if session in self.session_stats:
            self.session_stats[session]['trades'] += 1
            if win:
                self.session_stats[session]['wins'] += 1
            else:
                self.session_stats[session]['losses'] += 1
            self.session_stats[session]['pnl'] += pnl

    def get_session_performance(self) -> Dict[str, Any]:
        """Get performance metrics for all sessions"""
        performance = {}
        for session, stats in self.session_stats.items():
            if stats['trades'] > 0:
                win_rate = (stats['wins'] / stats['trades']) * 100
                avg_pnl = stats['pnl'] / stats['trades']
                performance[session] = {
                    "trades": stats['trades'],
                    "win_rate": win_rate,
                    "total_pnl": stats['pnl'],
                    "avg_pnl": avg_pnl
                }
            else:
                performance[session] = {
                    "trades": 0,
                    "win_rate": 0.0,
                    "total_pnl": 0.0,
                    "avg_pnl": 0.0
                }
        return performance

if not IB_AVAILABLE:
    # Fallback class when IB API is not available
    class InteractiveBrokersBroker(BrokerInterface):
        def __init__(self, config: Dict[str, Any]):
            raise ImportError("Interactive Brokers API not available. Install with: pip install ibapi")
        
        async def connect(self) -> bool:
            return False
        
        async def disconnect(self):
            pass
        
        async def get_account(self) -> Account:
            raise NotImplementedError
        
        async def get_positions(self) -> List[Position]:
            raise NotImplementedError
        
        async def get_position(self, symbol: str) -> Optional[Position]:
            raise NotImplementedError
        
        async def submit_order(self, order: Order) -> Order:
            raise NotImplementedError
        
        async def cancel_order(self, order_id: str) -> bool:
            raise NotImplementedError
        
        async def get_order(self, order_id: str) -> Optional[Order]:
            raise NotImplementedError
        
        async def get_orders(self, status: Optional[OrderStatus] = None) -> List[Order]:
            raise NotImplementedError
        
        async def get_market_data(self, symbol: str) -> Dict[str, Any]:
            raise NotImplementedError
        
        async def get_historical_data(self, symbol: str, timeframe: str = '1 min', limit: int = 100) -> List[Dict[str, Any]]:
            raise NotImplementedError
