"""
PROMETHEUS Trading Platform - Database Helper
Optimized database operations
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, List, Tuple

class DatabaseHelper:
    """Optimized database helper."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.local = threading.local()
    
    def get_connection(self):
        """Get thread-local database connection."""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            # Apply optimizations
            conn = self.local.connection
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
        
        return self.local.connection
    
    @contextmanager
    def transaction(self):
        """Database transaction context manager."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def execute_query(self, query: str, params: Tuple = None) -> List[Any]:
        """Execute query and return results."""
        with self.transaction() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                return cursor.fetchall()
            else:
                return cursor.rowcount
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """Execute many queries."""
        with self.transaction() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            return cursor.rowcount

# Database instances
trading_db = DatabaseHelper("prometheus_trading.db")
