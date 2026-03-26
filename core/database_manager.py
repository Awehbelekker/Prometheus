#!/usr/bin/env python3
"""
Database Manager for PROMETHEUS Trading Platform
Simple database management for the trading system
"""

import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import threading

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple database manager for PROMETHEUS Trading Platform"""
    
    def __init__(self, db_path: str = "prometheus_trading.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_database()
        logger.info(f"[CHECK] Database manager initialized: {db_path}")
    
    def _init_database(self):
        """Initialize database with required tables"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            ''')
            
            # Trading data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trading_data (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    symbol TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # System logs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    component TEXT,
                    timestamp TEXT NOT NULL,
                    data TEXT
                )
            ''')
            
            # Platform stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS platform_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    data TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
                results = [dict(row) for row in cursor.fetchall()]
                return results
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                return []
            finally:
                conn.close()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a SELECT query and return the first result"""
        results = self.execute_query(query, params)
        return results[0] if results else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return all results (alias for execute_query)"""
        return self.execute_query(query, params)

    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """Execute an INSERT/UPDATE/DELETE query"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute(query, params)
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Update execution failed: {e}")
                return False
            finally:
                conn.close()
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        results = self.execute_query(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        )
        return results[0] if results else None
    
    def create_user(self, user_id: str, email: str, name: str, role: str = 'user') -> bool:
        """Create a new user"""
        now = datetime.now().isoformat()
        return self.execute_update(
            "INSERT INTO users (id, email, name, role, status, created_at, updated_at) VALUES (?, ?, ?, ?, 'active', ?, ?)",
            (user_id, email, name, role, now, now)
        )
    
    def log_trading_data(self, user_id: str, symbol: str, action: str, 
                        quantity: float, price: float, data: Dict[str, Any] = None) -> bool:
        """Log trading data"""
        trade_id = f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data) if data else None
        
        return self.execute_update(
            "INSERT INTO trading_data (id, user_id, symbol, action, quantity, price, timestamp, data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (trade_id, user_id, symbol, action, quantity, price, timestamp, data_json)
        )
    
    def log_system_event(self, level: str, message: str, component: str = None, data: Dict[str, Any] = None) -> bool:
        """Log system event"""
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data) if data else None
        
        return self.execute_update(
            "INSERT INTO system_logs (level, message, component, timestamp, data) VALUES (?, ?, ?, ?, ?)",
            (level, message, component, timestamp, data_json)
        )
    
    def update_platform_stat(self, metric_name: str, metric_value: float, data: Dict[str, Any] = None) -> bool:
        """Update platform statistic"""
        timestamp = datetime.now().isoformat()
        data_json = json.dumps(data) if data else None
        
        return self.execute_update(
            "INSERT INTO platform_stats (metric_name, metric_value, timestamp, data) VALUES (?, ?, ?, ?)",
            (metric_name, metric_value, timestamp, data_json)
        )
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get current platform statistics"""
        stats = {}
        
        # Get user count
        user_count = self.execute_query("SELECT COUNT(*) as count FROM users WHERE status = 'active'")
        stats['total_users'] = user_count[0]['count'] if user_count else 0
        
        # Get trading activity
        trade_count = self.execute_query("SELECT COUNT(*) as count FROM trading_data WHERE date(timestamp) = date('now')")
        stats['daily_trades'] = trade_count[0]['count'] if trade_count else 0
        
        # Get latest platform metrics
        latest_metrics = self.execute_query(
            "SELECT metric_name, metric_value FROM platform_stats WHERE timestamp >= date('now') ORDER BY timestamp DESC"
        )
        
        for metric in latest_metrics:
            stats[metric['metric_name']] = metric['metric_value']
        
        return stats
    
    def cleanup_old_data(self, days: int = 30) -> bool:
        """Clean up old data (older than specified days)"""
        cutoff_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
        
        try:
            # Clean old logs
            self.execute_update("DELETE FROM system_logs WHERE timestamp < ?", (cutoff_date,))
            
            # Clean old stats (keep daily summaries)
            self.execute_update("DELETE FROM platform_stats WHERE timestamp < ?", (cutoff_date,))
            
            logger.info(f"[CHECK] Cleaned up data older than {days} days")
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return False
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a direct database connection (use with caution)"""
        return sqlite3.connect(self.db_path)
    
    def close(self):
        """Close database manager (cleanup if needed)"""
        logger.info("Database manager closed")

# Global instance
_db_manager = None

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
