"""
🚀 PROMETHEUS Persistent Trading Engine
Background trading system that continues running when users are offline
"""

import asyncio
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingMode(Enum):
    PAPER = "paper"
    LIVE = "live"

class TradingStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"

@dataclass
class UserPortfolio:
    user_id: str
    trading_mode: TradingMode
    allocated_capital: float
    current_value: float
    cash_balance: float
    positions: Dict[str, Any]
    total_return: float
    total_return_percent: float
    last_updated: datetime
    is_active: bool = True

@dataclass
class TradingOrder:
    order_id: str
    user_id: str
    symbol: str
    order_type: str  # 'buy', 'sell'
    quantity: int
    price: float
    status: str  # 'pending', 'executed', 'cancelled'
    created_at: datetime
    executed_at: Optional[datetime] = None
    trading_mode: TradingMode = TradingMode.PAPER

class PersistentTradingEngine:
    """
    Background trading engine that persists across user sessions
    """
    
    def __init__(self, db_path: str = "persistent_trading.db"):
        self.db_path = db_path
        self.is_running = False
        self.user_portfolios: Dict[str, UserPortfolio] = {}
        self.pending_orders: List[TradingOrder] = []
        self.trading_thread = None
        self.lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        self._load_portfolios()
        
    def _init_database(self):
        """Initialize the persistent trading database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User portfolios table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_portfolios (
                    user_id TEXT PRIMARY KEY,
                    trading_mode TEXT NOT NULL,
                    allocated_capital REAL NOT NULL DEFAULT 0,
                    current_value REAL NOT NULL DEFAULT 0,
                    cash_balance REAL NOT NULL DEFAULT 0,
                    positions TEXT NOT NULL DEFAULT '{}',
                    total_return REAL NOT NULL DEFAULT 0,
                    total_return_percent REAL NOT NULL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    live_trading_approved BOOLEAN DEFAULT 0
                )
            """)
            
            # Trading orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_orders (
                    order_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    order_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    trading_mode TEXT NOT NULL DEFAULT 'paper',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_portfolios (user_id)
                )
            """)
            
            # Trading history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL NOT NULL,
                    trading_mode TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    portfolio_value_after REAL,
                    FOREIGN KEY (user_id) REFERENCES user_portfolios (user_id)
                )
            """)
            
            # User permissions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_permissions (
                    user_id TEXT PRIMARY KEY,
                    live_trading_approved BOOLEAN DEFAULT 0,
                    max_allocation REAL DEFAULT 0,
                    approved_by TEXT,
                    approved_at TIMESTAMP,
                    notes TEXT
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _load_portfolios(self):
        """Load all user portfolios from database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_portfolios WHERE is_active = 1")
            
            for row in cursor.fetchall():
                portfolio = UserPortfolio(
                    user_id=row['user_id'],
                    trading_mode=TradingMode(row['trading_mode']),
                    allocated_capital=row['allocated_capital'],
                    current_value=row['current_value'],
                    cash_balance=row['cash_balance'],
                    positions=json.loads(row['positions']),
                    total_return=row['total_return'],
                    total_return_percent=row['total_return_percent'],
                    last_updated=datetime.fromisoformat(row['last_updated']),
                    is_active=bool(row['is_active'])
                )
                self.user_portfolios[row['user_id']] = portfolio
                
        logger.info(f"Loaded {len(self.user_portfolios)} user portfolios")

    def create_user_portfolio(self, user_id: str, initial_capital: float = 100000, 
                            trading_mode: TradingMode = TradingMode.PAPER) -> UserPortfolio:
        """Create a new user portfolio"""
        with self.lock:
            if user_id in self.user_portfolios:
                return self.user_portfolios[user_id]
            
            portfolio = UserPortfolio(
                user_id=user_id,
                trading_mode=trading_mode,
                allocated_capital=initial_capital,
                current_value=initial_capital,
                cash_balance=initial_capital,
                positions={},
                total_return=0.0,
                total_return_percent=0.0,
                last_updated=datetime.now(),
                is_active=True
            )
            
            # Save to database
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_portfolios 
                    (user_id, trading_mode, allocated_capital, current_value, cash_balance, 
                     positions, total_return, total_return_percent, last_updated, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    portfolio.user_id,
                    portfolio.trading_mode.value,
                    portfolio.allocated_capital,
                    portfolio.current_value,
                    portfolio.cash_balance,
                    json.dumps(portfolio.positions),
                    portfolio.total_return,
                    portfolio.total_return_percent,
                    portfolio.last_updated.isoformat(),
                    portfolio.is_active
                ))
                conn.commit()
            
            self.user_portfolios[user_id] = portfolio
            logger.info(f"Created portfolio for user {user_id} with ${initial_capital:,.2f}")
            return portfolio

    def get_user_portfolio(self, user_id: str) -> Optional[UserPortfolio]:
        """Get user portfolio by ID"""
        return self.user_portfolios.get(user_id)

    def update_portfolio_value(self, user_id: str, new_value: float):
        """Update portfolio value and calculate returns"""
        with self.lock:
            if user_id not in self.user_portfolios:
                return
            
            portfolio = self.user_portfolios[user_id]
            old_value = portfolio.current_value
            portfolio.current_value = new_value
            portfolio.total_return = new_value - portfolio.allocated_capital
            portfolio.total_return_percent = (portfolio.total_return / portfolio.allocated_capital) * 100
            portfolio.last_updated = datetime.now()
            
            # Save to database
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_portfolios 
                    SET current_value = ?, total_return = ?, total_return_percent = ?, last_updated = ?
                    WHERE user_id = ?
                """, (
                    portfolio.current_value,
                    portfolio.total_return,
                    portfolio.total_return_percent,
                    portfolio.last_updated.isoformat(),
                    user_id
                ))
                conn.commit()
            
            logger.info(f"Updated portfolio for {user_id}: ${old_value:,.2f} -> ${new_value:,.2f}")

    def start_background_trading(self):
        """Start the background trading engine"""
        if self.is_running:
            logger.warning("Trading engine is already running")
            return
        
        self.is_running = True
        self.trading_thread = threading.Thread(target=self._trading_loop, daemon=True)
        self.trading_thread.start()
        logger.info("Background trading engine started")

    def stop_background_trading(self):
        """Stop the background trading engine"""
        self.is_running = False
        if self.trading_thread:
            self.trading_thread.join(timeout=5)
        logger.info("Background trading engine stopped")

    def _trading_loop(self):
        """Main trading loop that runs in background"""
        while self.is_running:
            try:
                # Process pending orders
                self._process_pending_orders()
                
                # Update portfolio values based on market data
                self._update_portfolio_values()
                
                # Execute automated trading strategies
                self._execute_trading_strategies()
                
                # Sleep for 30 seconds before next iteration
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}")
                time.sleep(60)  # Wait longer on error

    def _process_pending_orders(self):
        """Process all pending trading orders"""
        # Implementation for order processing
        pass

    def _update_portfolio_values(self):
        """Update portfolio values based on current market prices"""
        # Implementation for portfolio value updates
        pass

    def _execute_trading_strategies(self):
        """Execute automated trading strategies for active portfolios"""
        # Implementation for strategy execution
        pass

# Global instance
persistent_trading_engine = PersistentTradingEngine()
