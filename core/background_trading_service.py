#!/usr/bin/env python3
"""
Persistent Background Trading Service
Runs continuously in the background, managing user trades and AI learning
even when users are offline. Maintains state across sessions.
"""

import asyncio
import logging
import json
import time
import signal
import sys
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from decimal import Decimal
import sqlite3
from pathlib import Path
import yfinance as yf
import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('background_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ActiveTrade:
    """Represents an active trade being managed by the background service"""
    trade_id: str
    user_id: str
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    strategy: str
    ai_confidence: float
    created_at: datetime
    last_updated: datetime
    status: str  # 'active', 'completed', 'stopped'
    pnl: float
    metadata: Dict[str, Any]

@dataclass
class UserSession:
    """Tracks user session state"""
    user_id: str
    session_id: str
    last_login: datetime
    last_activity: datetime
    is_online: bool
    active_trades: List[str]  # List of trade IDs
    ai_learning_state: Dict[str, Any]
    preferences: Dict[str, Any]

class BackgroundTradingService:
    """
    Persistent background service that manages all trading operations
    independently of user sessions
    """
    
    def __init__(self, db_path: str = "trading_persistence.db"):
        self.db_path = db_path
        self.active_trades: Dict[str, ActiveTrade] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        self.market_data_cache: Dict[str, Dict] = {}
        self.ai_learning_engine = None
        self.is_running = False
        self.background_tasks: Set[asyncio.Task] = set()
        
        # Initialize database
        self._init_database()
        
        # Load persistent state
        self._load_persistent_state()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _init_database(self):
        """Initialize SQLite database for persistence"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables for persistent storage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS active_trades (
                    trade_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    stop_loss REAL,
                    take_profit REAL,
                    strategy TEXT NOT NULL,
                    ai_confidence REAL NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    status TEXT NOT NULL,
                    pnl REAL NOT NULL,
                    metadata TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    user_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    last_login TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    is_online INTEGER NOT NULL,
                    active_trades TEXT NOT NULL,
                    ai_learning_state TEXT NOT NULL,
                    preferences TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    symbol TEXT PRIMARY KEY,
                    price REAL NOT NULL,
                    volume REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_learning_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    learning_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _load_persistent_state(self):
        """Load persistent state from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load active trades
            cursor.execute("SELECT * FROM active_trades WHERE status = 'active'")
            for row in cursor.fetchall():
                trade = ActiveTrade(
                    trade_id=row[0],
                    user_id=row[1],
                    symbol=row[2],
                    side=row[3],
                    quantity=row[4],
                    entry_price=row[5],
                    current_price=row[6],
                    stop_loss=row[7],
                    take_profit=row[8],
                    strategy=row[9],
                    ai_confidence=row[10],
                    created_at=datetime.fromisoformat(row[11]),
                    last_updated=datetime.fromisoformat(row[12]),
                    status=row[13],
                    pnl=row[14],
                    metadata=json.loads(row[15])
                )
                self.active_trades[trade.trade_id] = trade
            
            # Load user sessions
            cursor.execute("SELECT * FROM user_sessions")
            for row in cursor.fetchall():
                session = UserSession(
                    user_id=row[0],
                    session_id=row[1],
                    last_login=datetime.fromisoformat(row[2]),
                    last_activity=datetime.fromisoformat(row[3]),
                    is_online=bool(row[4]),
                    active_trades=json.loads(row[5]),
                    ai_learning_state=json.loads(row[6]),
                    preferences=json.loads(row[7])
                )
                self.user_sessions[session.user_id] = session
            
            conn.close()
            logger.info(f"Loaded {len(self.active_trades)} active trades and {len(self.user_sessions)} user sessions")
            
        except Exception as e:
            logger.error(f"Failed to load persistent state: {e}")
    
    def _save_trade_state(self, trade: ActiveTrade):
        """Save trade state to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO active_trades VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                trade.trade_id, trade.user_id, trade.symbol, trade.side,
                trade.quantity, trade.entry_price, trade.current_price,
                trade.stop_loss, trade.take_profit, trade.strategy,
                trade.ai_confidence, trade.created_at.isoformat(),
                trade.last_updated.isoformat(), trade.status, trade.pnl,
                json.dumps(trade.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save trade state: {e}")
    
    def _save_user_session(self, session: UserSession):
        """Save user session to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.user_id, session.session_id,
                session.last_login.isoformat(), session.last_activity.isoformat(),
                int(session.is_online), json.dumps(session.active_trades),
                json.dumps(session.ai_learning_state), json.dumps(session.preferences)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to save user session: {e}")
    
    async def start_service(self):
        """Start the background trading service"""
        if self.is_running:
            logger.warning("Service is already running")
            return

        self.is_running = True
        logger.info("🚀 Starting PROMETHEUS Background Trading Service...")

        # Initialize autonomous self-improvement system
        try:
            from autonomous_self_improvement_system import AutonomousSelfImprovementSystem
            self.autonomous_ai = AutonomousSelfImprovementSystem()
            logger.info("🤖 Autonomous AI system initialized")
        except ImportError:
            logger.warning("Autonomous AI system not available - continuing without it")
            self.autonomous_ai = None

        # Start background tasks
        tasks = [
            self._market_data_updater(),
            self._trade_monitor(),
            self._ai_learning_processor(),
            self._session_manager(),
            self._performance_tracker()
        ]

        # Add autonomous AI tasks if available
        if self.autonomous_ai:
            autonomous_tasks = [
                self._autonomous_monitoring_loop(),
                self._breakthrough_discovery_loop(),
                self._ai_learning_enhancement_loop()
            ]
            tasks.extend(autonomous_tasks)
            logger.info("🔬 Autonomous AI tasks added to background service")

        for task_coro in tasks:
            task = asyncio.create_task(task_coro)
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)

        logger.info("[CHECK] Background Trading Service started successfully")
        logger.info(f"📊 Active background tasks: {len(self.background_tasks)}")
        logger.info(f"Managing {len(self.active_trades)} active trades for {len(self.user_sessions)} users")
    
    async def stop_service(self):
        """Stop the background trading service gracefully"""
        logger.info("Stopping Background Trading Service...")
        self.is_running = False
        
        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Save final state
        self._save_all_state()
        
        logger.info("Background Trading Service stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(self.stop_service())
    
    def _save_all_state(self):
        """Save all current state to database"""
        for trade in self.active_trades.values():
            self._save_trade_state(trade)
        
        for session in self.user_sessions.values():
            self._save_user_session(session)
        
        logger.info("All state saved to database")
    
    async def add_user_trade(self, user_id: str, trade_data: Dict[str, Any]) -> str:
        """Add a new trade for a user"""
        trade_id = f"trade_{user_id}_{int(time.time())}"
        
        trade = ActiveTrade(
            trade_id=trade_id,
            user_id=user_id,
            symbol=trade_data['symbol'],
            side=trade_data['side'],
            quantity=trade_data['quantity'],
            entry_price=trade_data['entry_price'],
            current_price=trade_data['entry_price'],
            stop_loss=trade_data.get('stop_loss'),
            take_profit=trade_data.get('take_profit'),
            strategy=trade_data.get('strategy', 'manual'),
            ai_confidence=trade_data.get('ai_confidence', 0.5),
            created_at=datetime.now(),
            last_updated=datetime.now(),
            status='active',
            pnl=0.0,
            metadata=trade_data.get('metadata', {})
        )
        
        self.active_trades[trade_id] = trade
        self._save_trade_state(trade)
        
        # Update user session
        if user_id in self.user_sessions:
            self.user_sessions[user_id].active_trades.append(trade_id)
            self._save_user_session(self.user_sessions[user_id])
        
        logger.info(f"Added new trade {trade_id} for user {user_id}")
        return trade_id
    
    async def user_login(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Handle user login and return their current state"""
        now = datetime.now()
        
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]
            session.session_id = session_id
            session.last_login = now
            session.last_activity = now
            session.is_online = True
        else:
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                last_login=now,
                last_activity=now,
                is_online=True,
                active_trades=[],
                ai_learning_state={},
                preferences={}
            )
            self.user_sessions[user_id] = session
        
        self._save_user_session(session)
        
        # Get user's active trades
        user_trades = [
            asdict(trade) for trade in self.active_trades.values()
            if trade.user_id == user_id and trade.status == 'active'
        ]
        
        logger.info(f"User {user_id} logged in with {len(user_trades)} active trades")
        
        return {
            'user_id': user_id,
            'session_id': session_id,
            'active_trades': user_trades,
            'last_activity': session.last_activity.isoformat(),
            'ai_learning_state': session.ai_learning_state
        }
    
    async def user_logout(self, user_id: str):
        """Handle user logout"""
        if user_id in self.user_sessions:
            session = self.user_sessions[user_id]
            session.is_online = False
            session.last_activity = datetime.now()
            self._save_user_session(session)
            
            logger.info(f"User {user_id} logged out, trades continue in background")
    
    def get_user_trade_progress(self, user_id: str) -> Dict[str, Any]:
        """Get current progress of user's trades"""
        user_trades = [
            trade for trade in self.active_trades.values()
            if trade.user_id == user_id and trade.status == 'active'
        ]

        total_pnl = sum(trade.pnl for trade in user_trades)

        return {
            'user_id': user_id,
            'active_trades_count': len(user_trades),
            'total_pnl': total_pnl,
            'trades': [asdict(trade) for trade in user_trades],
            'last_updated': datetime.now().isoformat()
        }

    async def _market_data_updater(self):
        """Background task to continuously update market data"""
        logger.info("Starting market data updater...")

        while self.is_running:
            try:
                # Get unique symbols from active trades
                symbols = set(trade.symbol for trade in self.active_trades.values())

                if symbols:
                    # Update market data for all active symbols
                    for symbol in symbols:
                        await self._update_symbol_price(symbol)

                # Sleep for 30 seconds between updates
                await asyncio.sleep(30)

            except Exception as e:
                logger.error(f"Market data updater error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _update_symbol_price(self, symbol: str):
        """Update price for a specific symbol"""
        try:
            # Use yfinance to get real-time data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if not data.empty:
                current_price = float(data['Close'].iloc[-1])

                # Update all trades for this symbol
                for trade in self.active_trades.values():
                    if trade.symbol == symbol and trade.status == 'active':
                        old_price = trade.current_price
                        trade.current_price = current_price
                        trade.last_updated = datetime.now()

                        # Calculate P&L
                        if trade.side == 'buy':
                            trade.pnl = (current_price - trade.entry_price) * trade.quantity
                        else:  # sell
                            trade.pnl = (trade.entry_price - current_price) * trade.quantity

                        # Check stop loss and take profit
                        await self._check_trade_conditions(trade)

                        # Save updated state
                        self._save_trade_state(trade)

                        if abs(current_price - old_price) > 0.01:  # Log significant price changes
                            logger.debug(f"Updated {symbol}: ${old_price:.2f} -> ${current_price:.2f}, Trade {trade.trade_id} P&L: ${trade.pnl:.2f}")

                # Cache market data
                self.market_data_cache[symbol] = {
                    'price': current_price,
                    'timestamp': datetime.now(),
                    'volume': float(data['Volume'].iloc[-1]) if 'Volume' in data else 0
                }

        except Exception as e:
            logger.error(f"Failed to update price for {symbol}: {e}")

    async def _check_trade_conditions(self, trade: ActiveTrade):
        """Check if trade should be closed based on stop loss or take profit"""
        if trade.status != 'active':
            return

        should_close = False
        close_reason = ""

        if trade.side == 'buy':
            # Check stop loss
            if trade.stop_loss and trade.current_price <= trade.stop_loss:
                should_close = True
                close_reason = f"Stop loss triggered at ${trade.current_price:.2f}"

            # Check take profit
            elif trade.take_profit and trade.current_price >= trade.take_profit:
                should_close = True
                close_reason = f"Take profit triggered at ${trade.current_price:.2f}"

        else:  # sell
            # Check stop loss
            if trade.stop_loss and trade.current_price >= trade.stop_loss:
                should_close = True
                close_reason = f"Stop loss triggered at ${trade.current_price:.2f}"

            # Check take profit
            elif trade.take_profit and trade.current_price <= trade.take_profit:
                should_close = True
                close_reason = f"Take profit triggered at ${trade.current_price:.2f}"

        if should_close:
            trade.status = 'completed'
            trade.metadata['close_reason'] = close_reason
            trade.metadata['close_time'] = datetime.now().isoformat()

            logger.info(f"Trade {trade.trade_id} closed: {close_reason}, P&L: ${trade.pnl:.2f}")

            # Record learning data
            await self._record_trade_completion(trade)

    async def _trade_monitor(self):
        """Background task to monitor all active trades"""
        logger.info("Starting trade monitor...")

        while self.is_running:
            try:
                active_count = len([t for t in self.active_trades.values() if t.status == 'active'])
                total_pnl = sum(t.pnl for t in self.active_trades.values() if t.status == 'active')

                logger.info(f"Monitoring {active_count} active trades, Total P&L: ${total_pnl:.2f}")

                # Check for stale trades (older than 24 hours with no updates)
                now = datetime.now()
                for trade in list(self.active_trades.values()):
                    if trade.status == 'active' and (now - trade.last_updated).total_seconds() > 86400:
                        logger.warning(f"Stale trade detected: {trade.trade_id}, last updated: {trade.last_updated}")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Trade monitor error: {e}")
                await asyncio.sleep(300)

    async def _ai_learning_processor(self):
        """Background task for AI learning and pattern recognition"""
        logger.info("Starting AI learning processor...")

        while self.is_running:
            try:
                # Process completed trades for learning
                completed_trades = [t for t in self.active_trades.values() if t.status == 'completed']

                if completed_trades:
                    await self._process_learning_data(completed_trades)

                await asyncio.sleep(600)  # Process every 10 minutes

            except Exception as e:
                logger.error(f"AI learning processor error: {e}")
                await asyncio.sleep(600)

    async def _session_manager(self):
        """Background task to manage user sessions"""
        logger.info("Starting session manager...")

        while self.is_running:
            try:
                now = datetime.now()

                # Mark users as offline if no activity for 30 minutes
                for session in self.user_sessions.values():
                    if session.is_online and (now - session.last_activity).total_seconds() > 1800:
                        session.is_online = False
                        self._save_user_session(session)
                        logger.info(f"User {session.user_id} marked as offline due to inactivity")

                await asyncio.sleep(300)  # Check every 5 minutes

            except Exception as e:
                logger.error(f"Session manager error: {e}")
                await asyncio.sleep(300)

    async def _performance_tracker(self):
        """Background task to track system performance"""
        logger.info("Starting performance tracker...")

        while self.is_running:
            try:
                # Log system statistics
                active_trades = len([t for t in self.active_trades.values() if t.status == 'active'])
                online_users = len([s for s in self.user_sessions.values() if s.is_online])
                total_users = len(self.user_sessions)

                logger.info(f"System Status - Active Trades: {active_trades}, Online Users: {online_users}/{total_users}")

                await asyncio.sleep(900)  # Log every 15 minutes

            except Exception as e:
                logger.error(f"Performance tracker error: {e}")
                await asyncio.sleep(900)

    async def _record_trade_completion(self, trade: ActiveTrade):
        """Record completed trade for AI learning"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            learning_data = {
                'trade_id': trade.trade_id,
                'symbol': trade.symbol,
                'strategy': trade.strategy,
                'entry_price': trade.entry_price,
                'exit_price': trade.current_price,
                'pnl': trade.pnl,
                'duration': (trade.last_updated - trade.created_at).total_seconds(),
                'ai_confidence': trade.ai_confidence,
                'market_conditions': self.market_data_cache.get(trade.symbol, {})
            }

            cursor.execute('''
                INSERT INTO ai_learning_data (user_id, learning_type, data, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (
                trade.user_id,
                'trade_completion',
                json.dumps(learning_data),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Failed to record trade completion: {e}")

    async def _process_learning_data(self, completed_trades: List[ActiveTrade]):
        """Process completed trades for AI learning"""
        try:
            # Group trades by user
            user_trades = {}
            for trade in completed_trades:
                if trade.user_id not in user_trades:
                    user_trades[trade.user_id] = []
                user_trades[trade.user_id].append(trade)

            # Analyze patterns for each user
            for user_id, trades in user_trades.items():
                if user_id in self.user_sessions:
                    session = self.user_sessions[user_id]

                    # Calculate success rate
                    profitable_trades = len([t for t in trades if t.pnl > 0])
                    success_rate = profitable_trades / len(trades) if trades else 0

                    # Update AI learning state
                    session.ai_learning_state.update({
                        'success_rate': success_rate,
                        'total_trades': len(trades),
                        'avg_pnl': sum(t.pnl for t in trades) / len(trades),
                        'last_learning_update': datetime.now().isoformat()
                    })

                    self._save_user_session(session)

            logger.info(f"Processed learning data for {len(user_trades)} users")

        except Exception as e:
            logger.error(f"Failed to process learning data: {e}")

    async def _autonomous_monitoring_loop(self):
        """Autonomous AI monitoring loop"""
        if not hasattr(self, 'autonomous_ai') or not self.autonomous_ai:
            return

        logger.info("🤖 Starting autonomous monitoring loop...")

        while self.is_running:
            try:
                # Run autonomous monitoring
                await self.autonomous_ai.monitor_performance_continuously()

            except Exception as e:
                logger.error(f"Error in autonomous monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _breakthrough_discovery_loop(self):
        """Breakthrough discovery loop"""
        if not hasattr(self, 'autonomous_ai') or not self.autonomous_ai:
            return

        logger.info("🔬 Starting breakthrough discovery loop...")

        while self.is_running:
            try:
                # Run breakthrough discovery
                await self.autonomous_ai.breakthrough_discovery_loop()

            except Exception as e:
                logger.error(f"Error in breakthrough discovery: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes before retry

    async def _ai_learning_enhancement_loop(self):
        """AI learning enhancement loop"""
        if not hasattr(self, 'autonomous_ai') or not self.autonomous_ai:
            return

        logger.info("🧠 Starting AI learning enhancement loop...")

        while self.is_running:
            try:
                # Run AI learning enhancement
                await self.autonomous_ai.ai_learning_enhancement_loop()

            except Exception as e:
                logger.error(f"Error in AI learning enhancement: {e}")
                await asyncio.sleep(900)  # Wait 15 minutes before retry

# Global service instance
background_service = None

def get_background_service() -> BackgroundTradingService:
    """Get the global background service instance"""
    global background_service
    if background_service is None:
        background_service = BackgroundTradingService()
    return background_service
