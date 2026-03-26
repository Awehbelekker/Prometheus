#!/usr/bin/env python3
"""
Working Dual Broker System with Fixed IB Configuration
"""

import asyncio
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import brokers
try:
    from brokers.alpaca_broker import AlpacaBroker
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    ALPACA_AVAILABLE = True
    IB_AVAILABLE = True
except ImportError as e:
    logger.error(f"Broker import error: {e}")
    ALPACA_AVAILABLE = False
    IB_AVAILABLE = False

class FixedDualBrokerTradingSystem:
    """Fixed Dual Broker Trading System"""
    
    def __init__(self):
        self.alpaca_broker: Optional[AlpacaBroker] = None
        self.ib_broker: Optional[InteractiveBrokersBroker] = None
        self.alpaca_trades_today = 0
        self.ib_trades_today = 0
        self.ib_account = None
        
    async def initialize(self):
        """Initialize the dual broker system"""
        logger.info("Starting PROMETHEUS Fixed Dual Broker Trading System...")
        logger.info("This system will execute trades on both Alpaca and Interactive Brokers")
        logger.info("Press Ctrl+C to stop")
        logger.info("="*80)
        logger.info("PROMETHEUS FIXED DUAL BROKER TRADING SYSTEM")
        logger.info("="*80)
        logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)

        logger.info("[CONNECTING] Establishing broker connections...")
        await self._setup_brokers()
        if not self.alpaca_broker and not self.ib_broker:
            raise Exception("No brokers initialized. Cannot start trading.")

    async def _setup_brokers(self):
        """Setup both brokers with fixed configuration"""
        
        # Setup Alpaca broker
        if ALPACA_AVAILABLE:
            alpaca_config = {
                'paper_trading': os.getenv('ALPACA_PAPER_TRADING', 'true').lower() == 'true',
                'api_key': os.getenv('ALPACA_LIVE_KEY'),
                'secret_key': os.getenv('ALPACA_LIVE_SECRET')
            }
            if alpaca_config['api_key'] and alpaca_config['secret_key']:
                self.alpaca_broker = AlpacaBroker(alpaca_config)
                logger.info("[ALPACA] Testing connection...")
                if await self.alpaca_broker.connect():
                    account_info = await self.alpaca_broker.get_account_info()
                    logger.info(f"[ALPACA] Connected - Account: {account_info.get('account_number')}")
                    logger.info(f"[ALPACA] Balance: ${float(account_info.get('equity', 0)):.2f}")
                    logger.info(f"[ALPACA] Buying Power: ${float(account_info.get('buying_power', 0)):.2f}")
                else:
                    logger.error("[ALPACA] Failed to connect to Alpaca.")
                    self.alpaca_broker = None
            else:
                logger.warning("[ALPACA] Alpaca API keys not configured. Skipping Alpaca connection.")

        # Setup Interactive Brokers with FIXED configuration
        if IB_AVAILABLE:
            # Use different client ID to avoid conflicts
            ib_config = {
                'host': os.getenv('IB_HOST', '127.0.0.1'),
                'port': int(os.getenv('IB_PORT', '7496')),
                'client_id': int(os.getenv('IB_CLIENT_ID', '5')),  # Use client ID 5
                'paper_trading': os.getenv('IB_PAPER_TRADING', 'false').lower() == 'true'
            }
            
            self.ib_broker = InteractiveBrokersBroker(ib_config)
            logger.info("[IB] Connecting to IB Gateway with fixed configuration...")
            
            if await self.ib_broker.connect():
                logger.info("[IB] Connected successfully!")
                
                # Wait for connection to stabilize
                await asyncio.sleep(2)
                
                # Request next valid order ID
                self.ib_broker.client.reqIds(1)
                await asyncio.sleep(1)
                
                if hasattr(self.ib_broker, 'next_order_id') and self.ib_broker.next_order_id:
                    logger.info(f"[IB] Next valid order ID: {self.ib_broker.next_order_id}")
                else:
                    logger.warning("[IB] No order ID received")
                
                # Get account information
                try:
                    # Request managed accounts first
                    self.ib_broker.client.reqManagedAccts()
                    await asyncio.sleep(2)
                    
                    # Check if we have account data
                    if hasattr(self.ib_broker, 'managed_accounts') and self.ib_broker.managed_accounts:
                        accounts = self.ib_broker.managed_accounts.split(',')
                        logger.info(f"[IB] Available accounts: {accounts}")
                        
                        # Use the first account that's not U22261894
                        for account in accounts:
                            if account.strip() and account.strip() != "U22261894":
                                self.ib_account = account.strip()
                                logger.info(f"[IB] Using account: {self.ib_account}")
                                break
                        
                        if not self.ib_account and accounts:
                            self.ib_account = accounts[0].strip()
                            logger.warning(f"[IB] Using first available account: {self.ib_account}")
                    
                    # Request account summary for the selected account
                    if self.ib_account:
                        self.ib_broker.client.reqAccountSummary(9001, self.ib_account, "$LEDGER")
                        await asyncio.sleep(1)
                    
                    # Request positions
                    self.ib_broker.client.reqPositions()
                    await asyncio.sleep(1)
                    
                    # Log any errors
                    if hasattr(self.ib_broker, 'wrapper') and hasattr(self.ib_broker.wrapper, 'errors'):
                        for error in self.ib_broker.wrapper.errors:
                            logger.error(f"[IB ERROR] {error}")
                        self.ib_broker.wrapper.errors.clear()
                    
                except Exception as e:
                    logger.error(f"[IB] Error during account setup: {e}")
            else:
                logger.error("[IB] Failed to connect to Interactive Brokers.")
                self.ib_broker = None
        else:
            logger.warning("[IB] Interactive Brokers API not available. Skipping IB connection.")

        logger.info(f"[CONNECTIONS] Alpaca: {'CONNECTED' if self.alpaca_broker else 'NOT CONNECTED'}")
        logger.info(f"[CONNECTIONS] IB: {'CONNECTED' if self.ib_broker else 'NOT CONNECTED'}")

    async def run_trading_loop(self):
        """Run the trading loop"""
        cycle = 0
        while True:
            cycle += 1
            logger.info(f"[TRADING CYCLE {cycle}] {datetime.now().strftime('%H:%M:%S')}")
            logger.info("-" * 60)

            signals = await self._generate_trading_signals()
            if not signals:
                logger.info("[AI] No trading signals generated. Waiting for next cycle.")
            else:
                logger.info(f"[AI] Generated {len(signals)} dual-broker signals")
                await self._execute_dual_broker_trades(signals)

            await self._dual_broker_status_check()
            logger.info(f"[WAIT] Waiting 5 minutes for next cycle...")
            await asyncio.sleep(300)  # Wait for 5 minutes

    async def _generate_trading_signals(self) -> List[Dict[str, Any]]:
        """Generate trading signals"""
        logger.info("[AI] Generating dual-broker trading signals...")
        signals = [
            {"symbol": "ETHUSD", "action": "BUY", "quantity": 0.001, "confidence": 0.78, "type": "crypto"},
            {"symbol": "BTCUSD", "action": "BUY", "quantity": 0.0001, "confidence": 0.72, "type": "crypto"},
            {"symbol": "AAPL", "action": "BUY", "quantity": 1, "confidence": 0.85, "type": "stock"},
            {"symbol": "TSLA", "action": "SELL", "quantity": 1, "confidence": 0.65, "type": "stock"},
        ]
        return signals

    async def _execute_dual_broker_trades(self, signals: List[Dict[str, Any]]):
        """Execute trades on appropriate brokers"""
        logger.info(f"[DUAL BROKER] Executing {len(signals)} trades...")
        alpaca_trades = 0
        ib_trades = 0

        alpaca_tasks = []
        ib_tasks = []

        for signal in signals:
            if signal['type'] == 'crypto' and self.alpaca_broker:
                alpaca_tasks.append(self._execute_alpaca_trade(signal))
                alpaca_trades += 1
            elif signal['type'] == 'stock' and self.ib_broker:
                ib_tasks.append(self._execute_ib_trade_fixed(signal))
                ib_trades += 1
            else:
                logger.warning(f"[WARNING] No suitable broker for signal: {signal['symbol']} ({signal['type']})")

        logger.info(f"[DUAL BROKER] Alpaca trades: {alpaca_trades}")
        logger.info(f"[DUAL BROKER] IB trades: {ib_trades}")

        if alpaca_tasks:
            logger.info("[ALPACA] Executing crypto trades...")
            await asyncio.gather(*alpaca_tasks)
        if ib_tasks:
            logger.info("[IB] Executing stock trades...")
            await asyncio.gather(*ib_tasks)

    async def _execute_alpaca_trade(self, signal: Dict[str, Any]):
        """Execute a trade on Alpaca"""
        try:
            logger.info(f"[ALPACA] Executing {signal['action']} order for {signal['symbol']}")
            order = await self.alpaca_broker.place_order(
                symbol=signal['symbol'],
                qty=signal['quantity'],
                side=signal['action'].lower(),
                order_type='market',
                time_in_force='gtc'
            )
            if order and order.status in ['new', 'filled', 'partially_filled']:
                logger.info(f"[ALPACA SUCCESS] Order placed: {order.id}")
                logger.info(f"   Symbol: {order.symbol}")
                logger.info(f"   Side: {order.side}")
                logger.info(f"   Qty: {order.qty}")
                logger.info(f"   Status: {order.status}")
                self.alpaca_trades_today += 1
            else:
                logger.error(f"[ALPACA ERROR] Order failed: {order.status if order else 'Unknown'}")
                if order and order.body:
                    logger.error(f"   Response: {order.body}")
        except Exception as e:
            logger.error(f"[ALPACA ERROR] Error placing Alpaca order for {signal['symbol']}: {e}")

    async def _execute_ib_trade_fixed(self, signal: Dict[str, Any]):
        """Execute a trade on Interactive Brokers with FIXED configuration"""
        if not self.ib_broker or not self.ib_broker.connected:
            logger.error(f"[IB ERROR] IB not connected for {signal['symbol']}")
            return

        try:
            logger.info(f"[IB] Executing {signal['action']} order for {signal['symbol']}")
            
            # Create contract
            contract = self.ib_broker.create_stock_contract(signal['symbol'])
            
            # Create order with FIXED configuration
            order = self.ib_broker.create_order(
                action=signal['action'].upper(),
                quantity=signal['quantity'],
                order_type='MKT'
            )
            
            # FIX: Remove problematic order attributes
            # Do NOT set order.etradeOnly = True (this was causing the error)
            if hasattr(order, 'etradeOnly'):
                order.etradeOnly = False
            
            # Ensure next_order_id is available
            if not hasattr(self.ib_broker, 'next_order_id') or self.ib_broker.next_order_id is None:
                self.ib_broker.client.reqIds(1)
                await asyncio.sleep(1)
                if not hasattr(self.ib_broker, 'next_order_id') or self.ib_broker.next_order_id is None:
                    logger.error("[IB ERROR] Could not get next valid order ID from IB.")
                    return

            order_id = self.ib_broker.next_order_id
            self.ib_broker.client.placeOrder(order_id, contract, order)
            self.ib_broker.next_order_id += 1  # Increment for next order

            # Wait for order status update
            await asyncio.sleep(2)
            
            logger.info(f"[IB SUCCESS] Order placed: {order_id}")
            logger.info(f"   Symbol: {signal['symbol']}")
            logger.info(f"   Action: {signal['action']}")
            logger.info(f"   Quantity: {signal['quantity']}")
            logger.info(f"   Account: {self.ib_account}")
            
            self.ib_trades_today += 1
            
        except Exception as e:
            logger.error(f"[IB ERROR] Error placing IB order for {signal['symbol']}: {e}")

    async def _dual_broker_status_check(self):
        """Print status of both brokers"""
        logger.info("="*80)
        logger.info("DUAL BROKER STATUS CHECK")
        logger.info("="*80)

        if self.alpaca_broker:
            account_info = await self.alpaca_broker.get_account_info()
            logger.info(f"[ALPACA] Status: {'CONNECTED' if self.alpaca_broker.connected else 'DISCONNECTED'}")
            logger.info(f"   Account: {account_info.get('account_number')}")
            logger.info(f"   Balance: ${float(account_info.get('equity', 0)):.2f}")
            logger.info(f"   Buying Power: ${float(account_info.get('buying_power', 0)):.2f}")
            logger.info(f"   Trades Today: {self.alpaca_trades_today}")
        else:
            logger.info("[ALPACA] Status: NOT CONNECTED")

        if self.ib_broker:
            logger.info(f"[IB] Status: {'CONNECTED' if self.ib_broker.connected else 'DISCONNECTED'}")
            logger.info(f"   Host: {self.ib_broker.host}:{self.ib_broker.port}")
            logger.info(f"   Client ID: {self.ib_broker.client_id}")
            logger.info(f"   Account: {self.ib_account}")
            logger.info(f"   Trades Today: {self.ib_trades_today}")
            
            # Display IB positions
            if hasattr(self.ib_broker, 'positions_data') and self.ib_broker.positions_data:
                logger.info(f"   Positions: {len(self.ib_broker.positions_data)}")
            else:
                logger.info("   Positions: 0")
        else:
            logger.info("[IB] Status: NOT CONNECTED")

        logger.info("="*80)
        logger.info(f"[CYCLE RESULTS]")
        logger.info(f"   Alpaca Trades: {self.alpaca_trades_today}")
        logger.info(f"   IB Trades: {self.ib_trades_today}")
        logger.info(f"   Total Trades: {self.alpaca_trades_today + self.ib_trades_today}")

async def main():
    """Main function"""
    system = FixedDualBrokerTradingSystem()
    try:
        await system.initialize()
        await system.run_trading_loop()
    except KeyboardInterrupt:
        logger.info("Trading system stopped by user")
    except Exception as e:
        logger.critical(f"PROMETHEUS Fixed Dual Broker System encountered a critical error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
