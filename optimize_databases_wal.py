#!/usr/bin/env python3
"""
Optimize Databases with WAL Mode
Enables Write-Ahead Logging for better performance and concurrency
"""

import sqlite3
from pathlib import Path

def optimize_database(db_path):
    """Enable WAL mode and optimize database"""
    if not Path(db_path).exists():
        print(f"[SKIP] {db_path}: Not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current journal mode
        cursor.execute("PRAGMA journal_mode")
        current_mode = cursor.fetchone()[0]
        
        if current_mode.lower() == 'wal':
            print(f"[OK] {db_path}: Already in WAL mode")
            conn.close()
            return True
        
        # Enable WAL mode
        cursor.execute("PRAGMA journal_mode=WAL")
        new_mode = cursor.fetchone()[0]
        
        # Optimize other settings
        cursor.execute("PRAGMA synchronous=NORMAL")  # Faster than FULL, still safe
        cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
        
        conn.commit()
        conn.close()
        
        print(f"[OK] {db_path}: Optimized")
        print(f"     Journal Mode: {current_mode} -> {new_mode}")
        print(f"     Cache Size: 64MB")
        print(f"     Synchronous: NORMAL")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] {db_path}: {str(e)}")
        return False

def main():
    print("=" * 80)
    print("DATABASE OPTIMIZATION - WAL MODE")
    print("=" * 80)
    print()
    
    databases = [
        'prometheus_trading.db',
        'portfolio_persistence.db',
        'enhanced_paper_trading.db',
        'learning_database.db'
    ]
    
    optimized = 0
    for db in databases:
        if optimize_database(db):
            optimized += 1
        print()
    
    print("=" * 80)
    print(f"Optimization complete: {optimized} database(s) optimized")
    print("=" * 80)
    print()
    print("Benefits of WAL mode:")
    print("  - Better concurrent read performance")
    print("  - Faster writes")
    print("  - Better reliability")
    print("  - No locking issues with multiple readers")

if __name__ == "__main__":
    main()

