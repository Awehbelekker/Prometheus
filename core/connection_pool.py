"""
PROMETHEUS Trading Platform - Connection Pooling
High-performance database connection management
"""

import sqlite3
import threading
import queue
import os
from contextlib import contextmanager
from typing import Dict, Any
import time

class DatabaseConnectionPool:
    """Thread-safe database connection pool."""
    
    def __init__(self, database_path: str, max_connections: int = 20, timeout: int = 30):
        self.database_path = database_path
        self.max_connections = max_connections
        self.timeout = timeout
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        
        # Pre-populate pool with connections
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize connection pool with connections."""
        for _ in range(min(5, self.max_connections)):  # Start with 5 connections
            conn = self._create_connection()
            if conn:
                self.pool.put(conn)
                self.active_connections += 1
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection with optimizations."""
        try:
            conn = sqlite3.connect(
                self.database_path,
                check_same_thread=False,
                timeout=self.timeout
            )
            
            # Apply performance optimizations
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            
            return conn
            
        except Exception as e:
            print(f"[ERROR] Failed to create database connection: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with context manager."""
        conn = None
        try:
            # Try to get connection from pool
            try:
                conn = self.pool.get(timeout=5)
            except queue.Empty:
                # Create new connection if pool is empty and under limit
                with self.lock:
                    if self.active_connections < self.max_connections:
                        conn = self._create_connection()
                        if conn:
                            self.active_connections += 1
                    else:
                        # Wait for connection to become available
                        conn = self.pool.get(timeout=self.timeout)
            
            if not conn:
                raise Exception("Unable to get database connection")
            
            yield conn
            
        finally:
            # Return connection to pool
            if conn:
                try:
                    # Rollback any uncommitted transactions
                    conn.rollback()
                    self.pool.put(conn, timeout=1)
                except queue.Full:
                    # Pool is full, close connection
                    conn.close()
                    with self.lock:
                        self.active_connections -= 1
                except Exception as e:
                    print(f"[ERROR] Error returning connection to pool: {e}")
                    conn.close()
                    with self.lock:
                        self.active_connections -= 1
    
    def close_all(self):
        """Close all connections in pool."""
        while not self.pool.empty():
            try:
                conn = self.pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
            except Exception as e:
                print(f"[ERROR] Error closing connection: {e}")
        
        self.active_connections = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics."""
        return {
            "active_connections": self.active_connections,
            "max_connections": self.max_connections,
            "available_connections": self.pool.qsize(),
            "database_path": self.database_path
        }

class DatabaseManager:
    """Centralized database manager with connection pooling."""
    
    def __init__(self):
        self.pools: Dict[str, DatabaseConnectionPool] = {}
        self.databases = {
            "trading": "prometheus_trading.db",
            "users": "prometheus_users.db",
            "portfolio": "prometheus_portfolio.db",
            "trades": "prometheus_trades.db",
            "market_data": "prometheus_market_data.db",
            "ai_learning": "prometheus_ai_learning.db",
            "audit": "prometheus_audit.db"
        }
        
        # Initialize connection pools
        self._initialize_pools()
    
    def _initialize_pools(self):
        """Initialize connection pools for all databases."""
        for db_name, db_path in self.databases.items():
            if os.path.exists(db_path):
                self.pools[db_name] = DatabaseConnectionPool(db_path)
                print(f"[CHECK] Connection pool initialized for {db_name}")
    
    @contextmanager
    def get_connection(self, database: str):
        """Get connection for specific database."""
        if database not in self.pools:
            raise ValueError(f"Database {database} not found in pools")
        
        with self.pools[database].get_connection() as conn:
            yield conn
    
    def execute_query(self, database: str, query: str, params: tuple = None) -> Any:
        """Execute query with connection pooling."""
        with self.get_connection(database) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
                conn.commit()
                return cursor.rowcount
            else:
                return cursor.fetchall()
    
    def execute_many(self, database: str, query: str, params_list: list) -> int:
        """Execute many queries with connection pooling."""
        with self.get_connection(database) as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all connection pools."""
        stats = {}
        for db_name, pool in self.pools.items():
            stats[db_name] = pool.get_stats()
        return stats
    
    def close_all_pools(self):
        """Close all connection pools."""
        for pool in self.pools.values():
            pool.close_all()

# Global database manager instance
db_manager = DatabaseManager()

def get_db_connection(database: str):
    """Get database connection from pool."""
    return db_manager.get_connection(database)

def execute_db_query(database: str, query: str, params: tuple = None):
    """Execute database query with connection pooling."""
    return db_manager.execute_query(database, query, params)
