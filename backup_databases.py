#!/usr/bin/env python3
"""
Backup Prometheus Databases
Creates timestamped backups of all critical databases
"""

import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_databases():
    """Backup all critical databases"""
    print("=" * 80)
    print("PROMETHEUS DATABASE BACKUP")
    print("=" * 80)
    print()
    
    # Create backup directory
    backup_dir = Path("backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Databases to backup
    databases = {
        'prometheus_trading.db': 'Main Trading Database',
        'portfolio_persistence.db': 'Portfolio Persistence',
        'enhanced_paper_trading.db': 'Paper Trading Database',
        'learning_database.db': 'Learning Database'
    }
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backed_up = 0
    
    print(f"Backup timestamp: {timestamp}")
    print()
    
    for db_file, description in databases.items():
        db_path = Path(db_file)
        
        if db_path.exists():
            backup_file = backup_dir / f"{db_file.replace('.db', '')}_{timestamp}.db"
            
            try:
                shutil.copy2(db_path, backup_file)
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"[OK] {description}")
                print(f"     Source: {db_file} ({size_mb:.2f} MB)")
                print(f"     Backup: {backup_file.name}")
                backed_up += 1
            except Exception as e:
                print(f"[ERROR] {description}: {str(e)}")
        else:
            print(f"[SKIP] {description}: Not found (optional)")
        
        print()
    
    print("=" * 80)
    print(f"Backup complete: {backed_up} database(s) backed up")
    print(f"Backup location: {backup_dir.absolute()}")
    print("=" * 80)
    
    return backed_up

if __name__ == "__main__":
    backup_databases()

