
import sqlite3
import threading
from typing import List, Dict, Any, Optional
import asyncio
import time
from contextlib import contextmanager

# Enhanced DatabaseManager with connection pooling
class DatabaseConnectionPool:
    """Connection pool for improved database performance"""
    
    def __init__(self, db_path: str, max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._pool: List[sqlite3.Connection] = []
        self._lock = threading.Lock()
        
    def get_connection(self) -> sqlite3.Connection:
        """Get connection from pool or create new one"""
        with self._lock:
            if self._pool:
                return self._pool.pop()
            else:
                conn = sqlite3.connect(self.db_path)
                conn.row_factory = sqlite3.Row
                return conn
                
    def return_connection(self, conn: sqlite3.Connection):
        """Return connection to pool"""
        with self._lock:
            if len(self._pool) < self.max_connections:
                self._pool.append(conn)
            else:
                conn.close()
