#!/usr/bin/env python3
"""
Live Trading Engine for Prometheus Trading Platform
Handles real money transactions and live market operations
"""

import asyncio
import logging
import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import alpaca_trade_api as tradeapi
import yfinance as yf
import threading
import time
from decimal import Decimal, ROUND_HALF_UP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LiveTrade:
    trade_id: str
    user_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    price: float
    order_type: str  # 'market', 'limit', 'stop'
    status: str  # 'pending', 'filled', 'cancelled', 'rejected'
    timestamp: str
    filled_at: Optional[str]
    profit_loss: Optional[float]
    is_live: bool  # True for real money, False for paper
    broker_order_id: Optional[str]

@dataclass
class UserTradingAccount:
    user_id: str
    account_type: str  # 'paper', 'live'
    balance: float
    buying_power: float
    portfolio_value: float
    day_trade_count: int
    is_live_enabled: bool
    risk_limit: float
    daily_loss_limit: float
    position_size_limit: float

@dataclass
class LivePosition:
    user_id: str
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    realized_pnl: float
    is_live: bool

class LiveTradingEngine:
    def __init__(self):
        self.db_path = "live_trading.db"
        self.is_running = False
        self.trading_thread = None
        
        # Initialize Alpaca API
        self.alpaca_api_key = os.getenv('ALPACA_API_KEY', 'DEMO_KEY')
        self.alpaca_secret = os.getenv('ALPACA_SECRET_KEY', 'DEMO_SECRET')
        self.alpaca_base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        # Initialize Alpaca client
        try:
            self.alpaca = tradeapi.REST(
                self.alpaca_api_key,
                self.alpaca_secret,
                self.alpaca_base_url,
                api_version='v2'
            )
            logger.info("Alpaca API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca API: {e}")
            self.alpaca = None
        
        # Initialize database
        self._init_database()
        
        # Trading parameters
        self.max_position_size = 0.02  # 2% of portfolio per position
        self.daily_loss_limit = 0.05   # 5% daily loss limit
        self.risk_per_trade = 0.01     # 1% risk per trade
        
        logger.info("Live Trading Engine initialized")

    def _init_database(self):
        """Initialize database for live trading"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Live trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS live_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id TEXT UNIQUE,
                    user_id TEXT,
                    symbol TEXT,
                    side TEXT,
                    quantity REAL,
                    price REAL,
                    order_type TEXT,
                    status TEXT,
                    timestamp TEXT,
                    filled_at TEXT,
                    profit_loss REAL,
                    is_live BOOLEAN,
                    broker_order_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User trading accounts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE,
                    account_type TEXT,
                    balance REAL,
                    buying_power REAL,
                    portfolio_value REAL,
                    day_trade_count INTEGER DEFAULT 0,
                    is_live_enabled BOOLEAN DEFAULT 0,
                    risk_limit REAL DEFAULT 1000.0,
                    daily_loss_limit REAL DEFAULT 500.0,
                    position_size_limit REAL DEFAULT 0.02,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Live positions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS live_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    symbol TEXT,
                    quantity REAL,
                    avg_price REAL,
                    current_price REAL,
                    market_value REAL,
                    unrealized_pnl REAL,
                    realized_pnl REAL,
                    is_live BOOLEAN,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, symbol, is_live)
                )
            ''')
            
            # Performance tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    date TEXT,
                    portfolio_value REAL,
                    daily_pnl REAL,
                    total_trades INTEGER,
                    winning_trades INTEGER,
                    is_live BOOLEAN,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing live trading database: {e}")

    async def enable_live_trading(self, user_id: str, initial_balance: float = 1000.0) -> bool:
        """Enable live trading for a user with initial balance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user account exists
            cursor.execute('SELECT * FROM user_accounts WHERE user_id = ?', (user_id,))
            account = cursor.fetchone()
            
            if account:
                # Update existing account
                cursor.execute('''
                    UPDATE user_accounts 
                    SET is_live_enabled = 1, balance = ?, buying_power = ?, 
                        portfolio_value = ?, updated_at = ?
                    WHERE user_id = ?
                ''', (initial_balance, initial_balance, initial_balance, 
                      datetime.now().isoformat(), user_id))
            else:
                # Create new account
                cursor.execute('''
                    INSERT INTO user_accounts 
                    (user_id, account_type, balance, buying_power, portfolio_value, 
                     is_live_enabled, risk_limit, daily_loss_limit, position_size_limit)
                    VALUES (?, 'live', ?, ?, ?, 1, 1000.0, 500.0, 0.02)
                ''', (user_id, initial_balance, initial_balance, initial_balance))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Live trading enabled for user {user_id} with ${initial_balance}")
            return True
            
        except Exception as e:
            logger.error(f"Error enabling live trading for user {user_id}: {e}")
            return False

    async def execute_live_trade(self, user_id: str, symbol: str, side: str, 
                                quantity: float, order_type: str = 'market') -> Optional[LiveTrade]:
        """Execute a live trade with real money"""
        try:
            # Check if user has live trading enabled
            if not await self._is_live_enabled(user_id):
                logger.warning(f"Live trading not enabled for user {user_id}")
                return None
            
            # Validate trade parameters
            if not await self._validate_trade(user_id, symbol, side, quantity):
                logger.warning(f"Trade validation failed for user {user_id}")
                return None
            
            # Get current market price
            current_price = await self._get_current_price(symbol)
            if not current_price:
                logger.error(f"Could not get current price for {symbol}")
                return None
            
            # Create trade record
            trade_id = f"live_{user_id}_{symbol}_{int(time.time())}"
            trade = LiveTrade(
                trade_id=trade_id,
                user_id=user_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=current_price,
                order_type=order_type,
                status='pending',
                timestamp=datetime.now().isoformat(),
                filled_at=None,
                profit_loss=None,
                is_live=True,
                broker_order_id=None
            )
            
            # Execute trade via Alpaca (if available) or simulate
            if self.alpaca:
                try:
                    # Submit order to Alpaca
                    order = self.alpaca.submit_order(
                        symbol=symbol,
                        qty=quantity,
                        side=side,
                        type=order_type,
                        time_in_force='day'
                    )
                    
                    trade.broker_order_id = order.id
                    trade.status = 'submitted'
                    
                    logger.info(f"Live order submitted to Alpaca: {order.id}")
                    
                except Exception as e:
                    logger.error(f"Error submitting order to Alpaca: {e}")
                    # Do NOT simulate fills for live trading; mark as rejected
                    trade.status = 'rejected'
                    trade.filled_at = None
            else:
                # No Alpaca client available in live path – do not simulate fills
                trade.status = 'rejected'
                trade.filled_at = None
            
            # Store trade in database
            await self._store_trade(trade)
            
            # Update user account and positions
            await self._update_account_after_trade(trade)
            
            logger.info(f"Live trade executed: {trade_id}")
            return trade
            
        except Exception as e:
            logger.error(f"Error executing live trade: {e}")
            return None

    async def _is_live_enabled(self, user_id: str) -> bool:
        """Check if live trading is enabled for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT is_live_enabled FROM user_accounts WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            
            return result and result[0] == 1
            
        except Exception as e:
            logger.error(f"Error checking live trading status: {e}")
            return False

    async def _validate_trade(self, user_id: str, symbol: str, side: str, quantity: float) -> bool:
        """Validate trade parameters and risk limits"""
        try:
            # Get user account
            account = await self._get_user_account(user_id)
            if not account:
                return False
            
            # Get current price
            current_price = await self._get_current_price(symbol)
            if not current_price:
                return False
            
            # Calculate trade value
            trade_value = quantity * current_price
            
            # Check buying power
            if side == 'buy' and trade_value > account['buying_power']:
                logger.warning(f"Insufficient buying power for user {user_id}")
                return False
            
            # Check position size limit
            max_position_value = account['portfolio_value'] * account['position_size_limit']
            if trade_value > max_position_value:
                logger.warning(f"Trade exceeds position size limit for user {user_id}")
                return False
            
            # Check daily loss limit
            daily_pnl = await self._get_daily_pnl(user_id)
            if daily_pnl < -account['daily_loss_limit']:
                logger.warning(f"Daily loss limit exceeded for user {user_id}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating trade: {e}")
            return False

    async def _get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for symbol"""
        try:
            # Try Alpaca first
            if self.alpaca:
                try:
                    quote = self.alpaca.get_latest_quote(symbol)
                    return float(quote.ask_price)
                except:
                    pass
            
            # Fall back to Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None

    async def _store_trade(self, trade: LiveTrade):
        """Store trade in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO live_trades 
                (trade_id, user_id, symbol, side, quantity, price, order_type, 
                 status, timestamp, filled_at, profit_loss, is_live, broker_order_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id, trade.user_id, trade.symbol, trade.side,
                trade.quantity, trade.price, trade.order_type, trade.status,
                trade.timestamp, trade.filled_at, trade.profit_loss,
                trade.is_live, trade.broker_order_id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing trade: {e}")

    async def _update_account_after_trade(self, trade: LiveTrade):
        """Update user account and positions after trade execution"""
        try:
            if trade.status != 'filled':
                return
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get current account
            cursor.execute('SELECT * FROM user_accounts WHERE user_id = ?', (trade.user_id,))
            account_row = cursor.fetchone()
            if not account_row:
                return
            
            # Calculate trade value
            trade_value = trade.quantity * trade.price
            
            # Update account balance
            if trade.side == 'buy':
                new_balance = account_row[3] - trade_value  # balance column
                new_buying_power = account_row[4] - trade_value  # buying_power column
            else:  # sell
                new_balance = account_row[3] + trade_value
                new_buying_power = account_row[4] + trade_value
            
            cursor.execute('''
                UPDATE user_accounts 
                SET balance = ?, buying_power = ?, updated_at = ?
                WHERE user_id = ?
            ''', (new_balance, new_buying_power, datetime.now().isoformat(), trade.user_id))
            
            # Update or create position
            cursor.execute('''
                SELECT * FROM live_positions 
                WHERE user_id = ? AND symbol = ? AND is_live = ?
            ''', (trade.user_id, trade.symbol, trade.is_live))
            
            position = cursor.fetchone()
            
            if position:
                # Update existing position
                current_qty = position[3]  # quantity column
                current_avg = position[4]  # avg_price column
                
                if trade.side == 'buy':
                    new_qty = current_qty + trade.quantity
                    new_avg = ((current_qty * current_avg) + (trade.quantity * trade.price)) / new_qty
                else:  # sell
                    new_qty = current_qty - trade.quantity
                    new_avg = current_avg if new_qty > 0 else 0
                
                cursor.execute('''
                    UPDATE live_positions 
                    SET quantity = ?, avg_price = ?, updated_at = ?
                    WHERE user_id = ? AND symbol = ? AND is_live = ?
                ''', (new_qty, new_avg, datetime.now().isoformat(), 
                      trade.user_id, trade.symbol, trade.is_live))
            else:
                # Create new position
                if trade.side == 'buy':
                    cursor.execute('''
                        INSERT INTO live_positions 
                        (user_id, symbol, quantity, avg_price, current_price, 
                         market_value, unrealized_pnl, realized_pnl, is_live)
                        VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)
                    ''', (trade.user_id, trade.symbol, trade.quantity, trade.price,
                          trade.price, trade.quantity * trade.price, trade.is_live))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating account after trade: {e}")

    async def get_user_performance(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user performance metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get account info
            cursor.execute('SELECT * FROM user_accounts WHERE user_id = ?', (user_id,))
            account = cursor.fetchone()
            
            # Get all trades
            cursor.execute('''
                SELECT * FROM live_trades 
                WHERE user_id = ? AND status = 'filled'
                ORDER BY filled_at DESC
            ''', (user_id,))
            trades = cursor.fetchall()
            
            # Get current positions
            cursor.execute('''
                SELECT * FROM live_positions 
                WHERE user_id = ? AND quantity > 0
            ''', (user_id,))
            positions = cursor.fetchall()
            
            # Calculate performance metrics
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t[10] and t[10] > 0])  # profit_loss column
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            total_pnl = sum([t[10] for t in trades if t[10]]) if trades else 0
            
            # Get daily performance
            cursor.execute('''
                SELECT date, daily_pnl FROM performance_history 
                WHERE user_id = ? AND is_live = 1
                ORDER BY date DESC LIMIT 30
            ''', (user_id,))
            daily_performance = cursor.fetchall()
            
            conn.close()
            
            return {
                "user_id": user_id,
                "account_balance": account[3] if account else 0,
                "portfolio_value": account[5] if account else 0,
                "total_pnl": total_pnl,
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "win_rate": round(win_rate, 2),
                "is_live_enabled": account[7] if account else False,
                "positions": len(positions),
                "daily_performance": daily_performance
            }
            
        except Exception as e:
            logger.error(f"Error getting user performance: {e}")
            return {}

    async def start_live_trading_engine(self):
        """Start the live trading engine background process"""
        if self.is_running:
            return
        
        self.is_running = True
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        
        logger.info("Live Trading Engine started")

    def _trading_loop(self):
        """Background trading loop for continuous operations"""
        while self.is_running:
            try:
                # Update positions with current market prices
                asyncio.run(self._update_all_positions())
                
                # Update daily performance
                asyncio.run(self._update_daily_performance())
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(60)

    async def _update_all_positions(self):
        """Update all positions with current market prices"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT DISTINCT symbol FROM live_positions WHERE quantity > 0')
            symbols = [row[0] for row in cursor.fetchall()]
            
            for symbol in symbols:
                current_price = await self._get_current_price(symbol)
                if current_price:
                    cursor.execute('''
                        UPDATE live_positions 
                        SET current_price = ?, 
                            market_value = quantity * ?,
                            unrealized_pnl = (? - avg_price) * quantity,
                            updated_at = ?
                        WHERE symbol = ? AND quantity > 0
                    ''', (current_price, current_price, current_price, 
                          datetime.now().isoformat(), symbol))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating positions: {e}")

    async def _update_daily_performance(self):
        """Update daily performance for all users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Get all users with live trading
            cursor.execute('SELECT user_id FROM user_accounts WHERE is_live_enabled = 1')
            users = [row[0] for row in cursor.fetchall()]
            
            for user_id in users:
                # Calculate daily P&L
                cursor.execute('''
                    SELECT SUM(profit_loss) FROM live_trades 
                    WHERE user_id = ? AND DATE(filled_at) = ? AND status = 'filled'
                ''', (user_id, today))
                
                daily_pnl = cursor.fetchone()[0] or 0
                
                # Get portfolio value
                cursor.execute('SELECT portfolio_value FROM user_accounts WHERE user_id = ?', (user_id,))
                portfolio_value = cursor.fetchone()[0] or 0
                
                # Count trades
                cursor.execute('''
                    SELECT COUNT(*) FROM live_trades 
                    WHERE user_id = ? AND DATE(filled_at) = ? AND status = 'filled'
                ''', (user_id, today))
                
                daily_trades = cursor.fetchone()[0] or 0
                
                # Insert or update daily performance
                cursor.execute('''
                    INSERT OR REPLACE INTO performance_history 
                    (user_id, date, portfolio_value, daily_pnl, total_trades, is_live)
                    VALUES (?, ?, ?, ?, ?, 1)
                ''', (user_id, today, portfolio_value, daily_pnl, daily_trades))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating daily performance: {e}")

    async def _get_user_account(self, user_id: str) -> Optional[Dict]:
        """Get user account information"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM user_accounts WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'user_id': row[1],
                    'account_type': row[2],
                    'balance': row[3],
                    'buying_power': row[4],
                    'portfolio_value': row[5],
                    'is_live_enabled': row[7],
                    'risk_limit': row[8],
                    'daily_loss_limit': row[9],
                    'position_size_limit': row[10]
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting user account: {e}")
            return None

    async def _get_daily_pnl(self, user_id: str) -> float:
        """Get today's P&L for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT SUM(profit_loss) FROM live_trades 
                WHERE user_id = ? AND DATE(filled_at) = ? AND status = 'filled'
            ''', (user_id, today))
            
            result = cursor.fetchone()[0]
            conn.close()
            
            return result or 0.0
            
        except Exception as e:
            logger.error(f"Error getting daily P&L: {e}")
            return 0.0

# Global instance
live_trading_engine = LiveTradingEngine()
