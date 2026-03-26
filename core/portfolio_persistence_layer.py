"""
💾 PROMETHEUS Portfolio Persistence Layer
Comprehensive data persistence system for trading portfolios and session continuity
"""

import sqlite3
import json
import logging
import pickle
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from contextlib import contextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .persistent_trading_engine import persistent_trading_engine
from .user_portfolio_manager import user_portfolio_manager
from .wealth_management_system import wealth_management_system
from .access_control_manager import access_control_manager

logger = logging.getLogger(__name__)

class PersistenceEventType(Enum):
    PORTFOLIO_UPDATE = "portfolio_update"
    TRADE_EXECUTION = "trade_execution"
    POSITION_CHANGE = "position_change"
    BALANCE_CHANGE = "balance_change"
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_STARTUP = "system_startup"

@dataclass
class PersistenceEvent:
    event_id: str
    event_type: PersistenceEventType
    user_id: str
    data: Dict[str, Any]
    timestamp: datetime
    processed: bool = False

class PortfolioPersistenceLayer:
    """
    Advanced persistence layer ensuring all trading data survives system restarts
    """
    
    def __init__(self, db_path: str = "portfolio_persistence.db"):
        self.db_path = db_path
        self.event_queue: List[PersistenceEvent] = []
        self.active_sessions: Dict[str, Dict] = {}
        self.persistence_thread = None
        self.is_running = False
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        self._init_database()
        self._restore_system_state()

    def _init_database(self):
        """Initialize comprehensive persistence database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # System state table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_state (
                    id INTEGER PRIMARY KEY,
                    state_key TEXT UNIQUE NOT NULL,
                    state_value TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Active user sessions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS active_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_data TEXT NOT NULL,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Portfolio state snapshots (for recovery)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_state_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    portfolio_type TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    snapshot_reason TEXT
                )
            """)
            
            # Trading engine state
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trading_engine_state (
                    engine_id TEXT PRIMARY KEY,
                    engine_type TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            
            # Persistence events log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persistence_events (
                    event_id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    user_id TEXT,
                    event_data TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT 0
                )
            """)
            
            # Background task status
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS background_tasks (
                    task_id TEXT PRIMARY KEY,
                    task_type TEXT NOT NULL,
                    user_id TEXT,
                    task_data TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT
                )
            """)
            
            # Data integrity checksums
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_integrity (
                    table_name TEXT PRIMARY KEY,
                    checksum TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    last_verified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Portfolio persistence database initialized")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def start_persistence_engine(self):
        """Start the background persistence engine"""
        if self.is_running:
            logger.warning("Persistence engine already running")
            return
        
        self.is_running = True
        self.persistence_thread = threading.Thread(target=self._persistence_loop, daemon=True)
        self.persistence_thread.start()
        
        # Record system startup
        self.record_event(PersistenceEventType.SYSTEM_STARTUP, "system", {
            'startup_time': datetime.now().isoformat(),
            'active_users': len(self.active_sessions)
        })
        
        logger.info("Portfolio persistence engine started")

    def stop_persistence_engine(self):
        """Stop the persistence engine and save all state"""
        self.is_running = False
        
        # Record system shutdown
        self.record_event(PersistenceEventType.SYSTEM_SHUTDOWN, "system", {
            'shutdown_time': datetime.now().isoformat(),
            'active_users': len(self.active_sessions)
        })
        
        # Process remaining events
        self._process_pending_events()
        
        # Save all active sessions
        self._save_all_sessions()
        
        if self.persistence_thread:
            self.persistence_thread.join(timeout=10)
        
        self.executor.shutdown(wait=True)
        logger.info("Portfolio persistence engine stopped")

    def _persistence_loop(self):
        """Main persistence loop"""
        while self.is_running:
            try:
                # Process pending events
                self._process_pending_events()
                
                # Create portfolio snapshots
                self._create_portfolio_snapshots()
                
                # Update wealth management data
                self._update_wealth_data()
                
                # Clean up old data
                self._cleanup_old_data()
                
                # Verify data integrity
                self._verify_data_integrity()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in persistence loop: {e}")
                time.sleep(60)

    def record_event(self, event_type: PersistenceEventType, user_id: str, data: Dict[str, Any]):
        """Record a persistence event"""
        event = PersistenceEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            user_id=user_id,
            data=data,
            timestamp=datetime.now()
        )
        
        with self.lock:
            self.event_queue.append(event)
        
        # Also save to database immediately for critical events
        if event_type in [PersistenceEventType.TRADE_EXECUTION, PersistenceEventType.SYSTEM_SHUTDOWN]:
            self._save_event_to_db(event)

    def _save_event_to_db(self, event: PersistenceEvent):
        """Save event to database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO persistence_events
                (event_id, event_type, user_id, event_data, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                event.event_id,
                event.event_type.value,
                event.user_id,
                json.dumps(event.data),
                event.timestamp.isoformat()
            ))
            conn.commit()

    def _process_pending_events(self):
        """Process all pending persistence events"""
        with self.lock:
            events_to_process = self.event_queue.copy()
            self.event_queue.clear()
        
        for event in events_to_process:
            try:
                self._process_event(event)
                event.processed = True
            except Exception as e:
                logger.error(f"Failed to process event {event.event_id}: {e}")

    def _process_event(self, event: PersistenceEvent):
        """Process individual persistence event"""
        if event.event_type == PersistenceEventType.PORTFOLIO_UPDATE:
            self._handle_portfolio_update(event)
        elif event.event_type == PersistenceEventType.TRADE_EXECUTION:
            self._handle_trade_execution(event)
        elif event.event_type == PersistenceEventType.USER_LOGIN:
            self._handle_user_login(event)
        elif event.event_type == PersistenceEventType.USER_LOGOUT:
            self._handle_user_logout(event)
        
        # Save event to database
        self._save_event_to_db(event)

    def _handle_portfolio_update(self, event: PersistenceEvent):
        """Handle portfolio update event"""
        user_id = event.user_id
        data = event.data
        
        # Create portfolio snapshot
        self.create_portfolio_snapshot(
            user_id,
            data.get('portfolio_type', 'paper'),
            data.get('total_value', 0),
            data.get('positions', {}),
            "portfolio_update"
        )

    def _handle_trade_execution(self, event: PersistenceEvent):
        """Handle trade execution event"""
        user_id = event.user_id
        data = event.data
        
        # Update portfolio state
        portfolio = persistent_trading_engine.get_user_portfolio(user_id)
        if portfolio:
            # Update wealth management
            wealth_management_system.create_wealth_snapshot(
                user_id,
                data.get('portfolio_type', 'paper'),
                portfolio.current_value,
                portfolio.allocated_capital,
                portfolio.cash_balance,
                portfolio.current_value - portfolio.cash_balance
            )

    def _handle_user_login(self, event: PersistenceEvent):
        """Handle user login event"""
        user_id = event.user_id
        session_data = event.data
        
        self.active_sessions[user_id] = {
            'login_time': event.timestamp,
            'last_activity': event.timestamp,
            'session_data': session_data
        }
        
        # Save session to database
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO active_sessions
                (session_id, user_id, session_data, last_activity)
                VALUES (?, ?, ?, ?)
            """, (user_id, user_id, json.dumps(session_data), event.timestamp.isoformat()))
            conn.commit()

    def _handle_user_logout(self, event: PersistenceEvent):
        """Handle user logout event"""
        user_id = event.user_id
        
        if user_id in self.active_sessions:
            # Save final session state
            self._save_session_state(user_id)
            del self.active_sessions[user_id]
        
        # Mark session as inactive
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE active_sessions SET is_active = 0 WHERE user_id = ?
            """, (user_id,))
            conn.commit()

    def create_portfolio_snapshot(self, user_id: str, portfolio_type: str, 
                                total_value: float, positions: Dict, reason: str):
        """Create a portfolio state snapshot"""
        snapshot_data = {
            'total_value': total_value,
            'positions': positions,
            'timestamp': datetime.now().isoformat(),
            'reason': reason
        }
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO portfolio_state_snapshots
                (user_id, portfolio_type, state_data, snapshot_reason)
                VALUES (?, ?, ?, ?)
            """, (user_id, portfolio_type, json.dumps(snapshot_data), reason))
            conn.commit()

    def restore_user_portfolio(self, user_id: str, portfolio_type: str) -> Optional[Dict]:
        """Restore user portfolio from latest snapshot"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT state_data FROM portfolio_state_snapshots
                WHERE user_id = ? AND portfolio_type = ?
                ORDER BY snapshot_timestamp DESC
                LIMIT 1
            """, (user_id, portfolio_type))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['state_data'])
            return None

    def _create_portfolio_snapshots(self):
        """Create snapshots for all active portfolios"""
        for user_id in self.active_sessions:
            try:
                portfolio = persistent_trading_engine.get_user_portfolio(user_id)
                if portfolio:
                    self.create_portfolio_snapshot(
                        user_id,
                        portfolio.trading_mode.value,
                        portfolio.current_value,
                        portfolio.positions,
                        "scheduled_snapshot"
                    )
            except Exception as e:
                logger.error(f"Failed to create snapshot for user {user_id}: {e}")

    def _update_wealth_data(self):
        """Update wealth management data for all users"""
        for user_id in self.active_sessions:
            try:
                portfolio = persistent_trading_engine.get_user_portfolio(user_id)
                if portfolio:
                    wealth_management_system.create_wealth_snapshot(
                        user_id,
                        portfolio.trading_mode.value,
                        portfolio.current_value,
                        portfolio.allocated_capital,
                        portfolio.cash_balance,
                        portfolio.current_value - portfolio.cash_balance
                    )
            except Exception as e:
                logger.error(f"Failed to update wealth data for user {user_id}: {e}")

    def _save_all_sessions(self):
        """Save all active session states"""
        for user_id in self.active_sessions:
            self._save_session_state(user_id)

    def _save_session_state(self, user_id: str):
        """Save individual session state"""
        if user_id not in self.active_sessions:
            return
        
        session = self.active_sessions[user_id]
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE active_sessions 
                SET session_data = ?, last_activity = ?
                WHERE user_id = ?
            """, (
                json.dumps(session['session_data']),
                datetime.now().isoformat(),
                user_id
            ))
            conn.commit()

    def _restore_system_state(self):
        """Restore system state from database"""
        try:
            # Restore active sessions
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, session_data, last_activity FROM active_sessions
                    WHERE is_active = 1 AND last_activity > datetime('now', '-24 hours')
                """)
                
                for row in cursor.fetchall():
                    user_id = row['user_id']
                    session_data = json.loads(row['session_data'])
                    last_activity = datetime.fromisoformat(row['last_activity'])
                    
                    self.active_sessions[user_id] = {
                        'login_time': last_activity,
                        'last_activity': last_activity,
                        'session_data': session_data
                    }
            
            logger.info(f"Restored {len(self.active_sessions)} active sessions")
            
        except Exception as e:
            logger.error(f"Failed to restore system state: {e}")

    def _cleanup_old_data(self):
        """Clean up old persistence data"""
        try:
            cutoff_date = datetime.now() - timedelta(days=90)
            
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Clean old events
                cursor.execute("""
                    DELETE FROM persistence_events 
                    WHERE timestamp < ? AND processed = 1
                """, (cutoff_date.isoformat(),))
                
                # Clean old snapshots (keep daily snapshots)
                cursor.execute("""
                    DELETE FROM portfolio_state_snapshots 
                    WHERE snapshot_timestamp < ? 
                    AND snapshot_reason != 'daily_snapshot'
                """, (cutoff_date.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")

    def _verify_data_integrity(self):
        """Verify data integrity across all tables"""
        # Implementation for data integrity checks
        pass

    def get_system_health(self) -> Dict:
        """Get system health and persistence status"""
        return {
            'persistence_engine_running': self.is_running,
            'active_sessions': len(self.active_sessions),
            'pending_events': len(self.event_queue),
            'last_health_check': datetime.now().isoformat()
        }

# Global instance
portfolio_persistence_layer = PortfolioPersistenceLayer()
