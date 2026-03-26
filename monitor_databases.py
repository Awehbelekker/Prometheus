#!/usr/bin/env python3
"""
Monitor Database Growth and Disk Space
Weekly monitoring script for Prometheus databases
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json

def format_size(size_bytes):
    """Format size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_database_info(db_path):
    """Get detailed information about a database"""
    if not Path(db_path).exists():
        return None
    
    info = {
        'path': db_path,
        'size': Path(db_path).stat().st_size,
        'modified': datetime.fromtimestamp(Path(db_path).stat().st_mtime),
        'tables': [],
        'row_counts': {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        info['tables'] = tables
        
        # Get row counts for each table
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                info['row_counts'][table] = count
            except:
                pass
        
        conn.close()
    except Exception as e:
        info['error'] = str(e)
    
    return info

def check_disk_space():
    """Check disk space usage"""
    import shutil
    
    total, used, free = shutil.disk_usage('/')
    
    return {
        'total': total,
        'used': used,
        'free': free,
        'percent_used': (used / total) * 100
    }

def load_history():
    """Load monitoring history"""
    history_file = Path("database_monitoring_history.json")
    if history_file.exists():
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history):
    """Save monitoring history"""
    history_file = Path("database_monitoring_history.json")
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2, default=str)

def compare_with_history(current_data, history):
    """Compare current data with history"""
    changes = {}
    
    for db_name, current_info in current_data.items():
        if db_name in history:
            old_info = history[db_name]
            
            size_change = current_info['size'] - old_info['size']
            size_change_pct = (size_change / old_info['size'] * 100) if old_info['size'] > 0 else 0
            
            changes[db_name] = {
                'size_change': size_change,
                'size_change_pct': size_change_pct,
                'days_since_last_check': (datetime.now() - datetime.fromisoformat(old_info['timestamp'])).days
            }
        else:
            changes[db_name] = {
                'size_change': 0,
                'size_change_pct': 0,
                'days_since_last_check': 0
            }
    
    return changes

def main():
    print("=" * 80)
    print("PROMETHEUS DATABASE MONITORING")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Databases to monitor
    databases = {
        'prometheus_trading.db': 'Main Trading Database',
        'portfolio_persistence.db': 'Portfolio Persistence',
        'enhanced_paper_trading.db': 'Paper Trading Database',
        'learning_database.db': 'Learning Database'
    }
    
    # Get current database info
    print("DATABASE STATUS:")
    print()
    
    current_data = {}
    total_size = 0
    
    for db_file, description in databases.items():
        info = get_database_info(db_file)
        
        if info:
            current_data[db_file] = {
                'description': description,
                'size': info['size'],
                'tables': len(info['tables']),
                'timestamp': datetime.now().isoformat()
            }
            total_size += info['size']
            
            print(f"[OK] {description}")
            print(f"     Size: {format_size(info['size'])}")
            print(f"     Tables: {len(info['tables'])}")
            if info.get('row_counts'):
                total_rows = sum(info['row_counts'].values())
                print(f"     Total Rows: {total_rows:,}")
            print()
        else:
            print(f"[INFO] {description}: Not found (optional)")
            print()
    
    print(f"Total Database Size: {format_size(total_size)}")
    print()
    
    # Load and compare with history
    history = load_history()
    if history:
        print("=" * 80)
        print("GROWTH ANALYSIS:")
        print()
        
        changes = compare_with_history(current_data, history)
        
        for db_file, change_info in changes.items():
            if db_file in current_data:
                desc = current_data[db_file]['description']
                size_change = change_info['size_change']
                size_change_pct = change_info['size_change_pct']
                days = change_info['days_since_last_check']
                
                if days > 0:
                    if size_change > 0:
                        print(f"{desc}:")
                        print(f"  Growth: +{format_size(size_change)} ({size_change_pct:+.2f}%)")
                        print(f"  Days since last check: {days}")
                        print()
                    elif size_change < 0:
                        print(f"{desc}:")
                        print(f"  Change: {format_size(size_change)} ({size_change_pct:+.2f}%)")
                        print(f"  Days since last check: {days}")
                        print()
    
    # Check disk space
    print("=" * 80)
    print("DISK SPACE:")
    print()
    
    disk = check_disk_space()
    print(f"Total: {format_size(disk['total'])}")
    print(f"Used: {format_size(disk['used'])} ({disk['percent_used']:.1f}%)")
    print(f"Free: {format_size(disk['free'])}")
    print()
    
    # Warnings
    warnings = []
    
    if disk['percent_used'] > 90:
        warnings.append(f"CRITICAL: Disk space at {disk['percent_used']:.1f}% - Free up space immediately!")
    elif disk['percent_used'] > 85:
        warnings.append(f"WARNING: Disk space at {disk['percent_used']:.1f}% - Consider freeing up space")
    
    if total_size > 100 * 1024 * 1024:  # > 100 MB
        warnings.append(f"INFO: Databases total {format_size(total_size)} - Consider archiving old data")
    
    if warnings:
        print("=" * 80)
        print("WARNINGS:")
        print()
        for warning in warnings:
            print(f"  {warning}")
        print()
    
    # Save current data to history
    save_history(current_data)
    
    # Recommendations
    print("=" * 80)
    print("RECOMMENDATIONS:")
    print()
    
    if disk['percent_used'] > 85:
        print("  1. [HIGH] Free up disk space")
        print("     - Delete unnecessary files")
        print("     - Archive old backups")
        print("     - Clean temporary files")
        print()
    
    if total_size > 50 * 1024 * 1024:  # > 50 MB
        print("  2. [MEDIUM] Consider archiving old trading data")
        print("     - Move old trades to archive")
        print("     - Keep only recent data in main database")
        print()
    
    print("  3. [RECOMMENDED] Run this script weekly")
    print("     - Monitor database growth")
    print("     - Track disk space usage")
    print("     - Review warnings")
    print()
    
    print("=" * 80)
    print("Monitoring complete. Data saved to database_monitoring_history.json")
    print("=" * 80)

if __name__ == "__main__":
    main()

