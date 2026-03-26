"""
👤 PROMETHEUS User Portfolio Manager
Isolated portfolio management system with user-specific data separation
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import uuid
from contextlib import contextmanager

from .persistent_trading_engine import TradingMode, UserPortfolio, persistent_trading_engine

logger = logging.getLogger(__name__)

class PortfolioType(Enum):
    PAPER = "paper"
    LIVE = "live"
    DEMO = "demo"

@dataclass
class Position:
    symbol: str
    quantity: int
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    last_updated: datetime

@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    symbol: str
    action: str  # 'buy', 'sell'
    quantity: int
    price: float
    total_value: float
    fees: float
    timestamp: datetime
    portfolio_type: PortfolioType

@dataclass
class UserTradingProfile:
    user_id: str
    username: str
    email: str
    live_trading_approved: bool
    max_allocation: float
    current_allocation: float
    risk_tolerance: str  # 'conservative', 'moderate', 'aggressive'
    trading_experience: str  # 'beginner', 'intermediate', 'advanced'
    created_at: datetime
    last_login: Optional[datetime] = None

class UserPortfolioManager:
    """
    Manages isolated user portfolios with strict data separation
    """
    
    def __init__(self, db_path: str = "user_portfolios.db"):
        self.db_path = db_path
        self.user_sessions: Dict[str, Dict] = {}
        self._init_database()

    def _init_database(self):
        """Initialize user portfolio database with proper isolation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User trading profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_trading_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    live_trading_approved BOOLEAN DEFAULT 0,
                    max_allocation REAL DEFAULT 0,
                    current_allocation REAL DEFAULT 0,
                    risk_tolerance TEXT DEFAULT 'moderate',
                    trading_experience TEXT DEFAULT 'beginner',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # User positions (isolated per user and portfolio type)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    avg_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    market_value REAL NOT NULL,
                    unrealized_pnl REAL NOT NULL,
                    unrealized_pnl_percent REAL NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, portfolio_type, symbol),
                    FOREIGN KEY (user_id) REFERENCES user_trading_profiles (user_id)
                )
            """)
            
            # User transactions (complete trading history per user)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_transactions (
                    transaction_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    total_value REAL NOT NULL,
                    fees REAL DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_trading_profiles (user_id)
                )
            """)
            
            # Portfolio snapshots (daily portfolio values)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    total_value REAL NOT NULL,
                    cash_balance REAL NOT NULL,
                    positions_value REAL NOT NULL,
                    daily_pnl REAL NOT NULL,
                    total_return REAL NOT NULL,
                    total_return_percent REAL NOT NULL,
                    snapshot_date DATE NOT NULL,
                    UNIQUE(user_id, portfolio_type, snapshot_date),
                    FOREIGN KEY (user_id) REFERENCES user_trading_profiles (user_id)
                )
            """)
            
            # User sessions for tracking active users
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES user_trading_profiles (user_id)
                )
            """)
            
            conn.commit()
            logger.info("User portfolio database initialized")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def create_user_profile(self, username: str, email: str, password: str) -> str:
        """Create a new user trading profile"""
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO user_trading_profiles 
                    (user_id, username, email, password_hash, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, email, password_hash, datetime.now().isoformat()))
                
                conn.commit()
                
                # Create initial paper trading portfolio
                self.initialize_user_portfolio(user_id, PortfolioType.PAPER, 100000.0)
                
                logger.info(f"Created user profile: {username} ({user_id})")
                return user_id
                
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to create user profile: {e}")
                raise ValueError("Username or email already exists")

    def initialize_user_portfolio(self, user_id: str, portfolio_type: PortfolioType, 
                                initial_capital: float) -> bool:
        """Initialize a new portfolio for a user"""
        try:
            # Create portfolio in persistent trading engine
            trading_mode = TradingMode.LIVE if portfolio_type == PortfolioType.LIVE else TradingMode.PAPER
            persistent_trading_engine.create_user_portfolio(user_id, initial_capital, trading_mode)
            
            # Create initial portfolio snapshot
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO portfolio_snapshots
                    (user_id, portfolio_type, total_value, cash_balance, positions_value,
                     daily_pnl, total_return, total_return_percent, snapshot_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id, portfolio_type.value, initial_capital, initial_capital, 0.0,
                    0.0, 0.0, 0.0, datetime.now().date().isoformat()
                ))
                conn.commit()
            
            logger.info(f"Initialized {portfolio_type.value} portfolio for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize portfolio: {e}")
            return False

    def get_user_portfolio(self, user_id: str, portfolio_type: PortfolioType) -> Optional[Dict]:
        """Get user's portfolio data with complete isolation"""
        try:
            # Get portfolio from persistent engine
            portfolio = persistent_trading_engine.get_user_portfolio(user_id)
            if not portfolio:
                return None
            
            # Get positions
            positions = self.get_user_positions(user_id, portfolio_type)
            
            # Get recent transactions
            transactions = self.get_user_transactions(user_id, portfolio_type, limit=10)
            
            # Get portfolio performance
            performance = self.get_portfolio_performance(user_id, portfolio_type)
            
            return {
                'user_id': user_id,
                'portfolio_type': portfolio_type.value,
                'allocated_capital': portfolio.allocated_capital,
                'current_value': portfolio.current_value,
                'cash_balance': portfolio.cash_balance,
                'total_return': portfolio.total_return,
                'total_return_percent': portfolio.total_return_percent,
                'positions': positions,
                'recent_transactions': transactions,
                'performance': performance,
                'last_updated': portfolio.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get portfolio for user {user_id}: {e}")
            return None

    def get_user_positions(self, user_id: str, portfolio_type: PortfolioType) -> List[Dict]:
        """Get user's current positions"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_positions 
                WHERE user_id = ? AND portfolio_type = ?
                ORDER BY market_value DESC
            """, (user_id, portfolio_type.value))
            
            positions = []
            for row in cursor.fetchall():
                positions.append({
                    'symbol': row['symbol'],
                    'quantity': row['quantity'],
                    'avg_price': row['avg_price'],
                    'current_price': row['current_price'],
                    'market_value': row['market_value'],
                    'unrealized_pnl': row['unrealized_pnl'],
                    'unrealized_pnl_percent': row['unrealized_pnl_percent'],
                    'last_updated': row['last_updated']
                })
            
            return positions

    def get_user_transactions(self, user_id: str, portfolio_type: PortfolioType, 
                            limit: int = 50) -> List[Dict]:
        """Get user's transaction history"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM user_transactions 
                WHERE user_id = ? AND portfolio_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, portfolio_type.value, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'transaction_id': row['transaction_id'],
                    'symbol': row['symbol'],
                    'action': row['action'],
                    'quantity': row['quantity'],
                    'price': row['price'],
                    'total_value': row['total_value'],
                    'fees': row['fees'],
                    'timestamp': row['timestamp'],
                    'notes': row['notes']
                })
            
            return transactions

    def get_portfolio_performance(self, user_id: str, portfolio_type: PortfolioType, 
                                days: int = 30) -> Dict:
        """Get portfolio performance metrics"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get performance data for the last N days
            cursor.execute("""
                SELECT * FROM portfolio_snapshots 
                WHERE user_id = ? AND portfolio_type = ?
                AND snapshot_date >= date('now', '-{} days')
                ORDER BY snapshot_date ASC
            """.format(days), (user_id, portfolio_type.value))
            
            snapshots = cursor.fetchall()
            
            if not snapshots:
                return {'error': 'No performance data available'}
            
            # Calculate performance metrics
            first_value = snapshots[0]['total_value']
            last_value = snapshots[-1]['total_value']
            
            total_return = last_value - first_value
            total_return_percent = (total_return / first_value) * 100 if first_value > 0 else 0
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(snapshots)):
                prev_value = snapshots[i-1]['total_value']
                curr_value = snapshots[i]['total_value']
                daily_return = (curr_value - prev_value) / prev_value if prev_value > 0 else 0
                daily_returns.append(daily_return)
            
            # Calculate volatility (standard deviation of daily returns)
            if len(daily_returns) > 1:
                mean_return = sum(daily_returns) / len(daily_returns)
                variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
                volatility = variance ** 0.5
            else:
                volatility = 0
            
            return {
                'period_days': days,
                'starting_value': first_value,
                'ending_value': last_value,
                'total_return': total_return,
                'total_return_percent': total_return_percent,
                'volatility': volatility * 100,  # Convert to percentage
                'daily_snapshots': [
                    {
                        'date': snap['snapshot_date'],
                        'value': snap['total_value'],
                        'daily_pnl': snap['daily_pnl']
                    } for snap in snapshots
                ]
            }

    def execute_trade(self, user_id: str, portfolio_type: PortfolioType, 
                     symbol: str, action: str, quantity: int, price: float) -> bool:
        """Execute a trade for a user with proper isolation"""
        try:
            transaction_id = str(uuid.uuid4())
            total_value = quantity * price
            fees = total_value * 0.001  # 0.1% fee
            
            # Record transaction
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_transactions
                    (transaction_id, user_id, portfolio_type, symbol, action, 
                     quantity, price, total_value, fees, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transaction_id, user_id, portfolio_type.value, symbol, action,
                    quantity, price, total_value, fees, datetime.now().isoformat()
                ))
                
                # Update or create position
                if action.lower() == 'buy':
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_positions
                        (user_id, portfolio_type, symbol, quantity, avg_price, 
                         current_price, market_value, unrealized_pnl, unrealized_pnl_percent)
                        VALUES (?, ?, ?, 
                                COALESCE((SELECT quantity FROM user_positions 
                                         WHERE user_id = ? AND portfolio_type = ? AND symbol = ?), 0) + ?,
                                ?, ?, ?, 0, 0)
                    """, (user_id, portfolio_type.value, symbol, user_id, portfolio_type.value, symbol, quantity, price, price, total_value))
                
                conn.commit()
            
            logger.info(f"Executed {action} trade for user {user_id}: {quantity} {symbol} @ ${price}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return False

# Global instance
user_portfolio_manager = UserPortfolioManager()
