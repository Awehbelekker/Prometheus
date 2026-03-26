#!/usr/bin/env python3
"""
Database Optimization Recommendations
Analyzes database status and provides recommendations
"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime

def check_database_status():
    """Check all databases and their status"""
    print("=" * 80)
    print("DATABASE STATUS ANALYSIS")
    print("=" * 80)
    print()
    
    databases = {
        'prometheus_trading.db': {
            'name': 'Main Trading Database',
            'critical': True,
            'purpose': 'Stores all live trading data, orders, positions'
        },
        'portfolio_persistence.db': {
            'name': 'Portfolio Persistence',
            'critical': True,
            'purpose': 'Tracks portfolio state and session persistence'
        },
        'enhanced_paper_trading.db': {
            'name': 'Paper Trading Database',
            'critical': False,
            'purpose': 'Simulated trading for testing strategies'
        },
        'learning_database.db': {
            'name': 'Learning Database',
            'critical': False,
            'purpose': 'Stores AI learning data and model improvements'
        }
    }
    
    print("DATABASE INVENTORY:")
    print()
    
    active_count = 0
    for db_file, info in databases.items():
        db_path = Path(db_file)
        exists = db_path.exists()
        
        if exists:
            size_mb = db_path.stat().st_size / (1024 * 1024)
            active_count += 1
            status = "[OK]"
            
            # Check database health
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                table_count = len(tables)
                conn.close()
                
                print(f"  {status} {info['name']}")
                print(f"      Size: {size_mb:.2f} MB")
                print(f"      Tables: {table_count}")
                print(f"      Purpose: {info['purpose']}")
                print(f"      Critical: {'Yes' if info['critical'] else 'No (optional)'}")
            except Exception as e:
                print(f"  {status} {info['name']}")
                print(f"      Size: {size_mb:.2f} MB")
                print(f"      Status: [WARNING] Could not analyze: {str(e)[:50]}")
        else:
            status = "[MISSING]"
            print(f"  {status} {info['name']}")
            print(f"      Status: Not created yet")
            print(f"      Purpose: {info['purpose']}")
            print(f"      Critical: {'Yes' if info['critical'] else 'No (optional)'}")
            if not info['critical']:
                print(f"      Note: Will be created automatically on first use")
        
        print()
    
    print(f"Active Databases: {active_count}/{len(databases)}")
    print()
    
    return active_count, len(databases), databases

def analyze_database_health():
    """Analyze health of existing databases"""
    print("=" * 80)
    print("DATABASE HEALTH ANALYSIS")
    print("=" * 80)
    print()
    
    issues = []
    recommendations = []
    
    # Check main trading database
    if Path('prometheus_trading.db').exists():
        try:
            conn = sqlite3.connect('prometheus_trading.db')
            cursor = conn.cursor()
            
            # Check for tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            if not tables:
                issues.append("Main trading database has no tables")
                recommendations.append("Database may need initialization")
            
            # Check database size
            db_size = Path('prometheus_trading.db').stat().st_size
            if db_size < 1024:  # Less than 1KB
                issues.append("Main trading database is very small")
                recommendations.append("Database may be empty or not initialized")
            
            # Check for recent activity
            try:
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                conn.close()
            except:
                pass
            
            conn.close()
        except Exception as e:
            issues.append(f"Could not analyze main trading database: {str(e)[:50]}")
    
    # Check portfolio persistence
    if Path('portfolio_persistence.db').exists():
        try:
            conn = sqlite3.connect('portfolio_persistence.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            conn.close()
            
            if not tables:
                issues.append("Portfolio persistence database has no tables")
        except Exception as e:
            issues.append(f"Could not analyze portfolio database: {str(e)[:50]}")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  [WARNING] {issue}")
        print()
    
    if recommendations:
        print("RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  - {rec}")
        print()
    
    if not issues:
        print("[OK] All active databases appear healthy")
        print()
    
    return issues, recommendations

def provide_recommendations(active_count, total_count, databases):
    """Provide optimization recommendations"""
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    
    missing_critical = False
    missing_optional = False
    
    for db_file, info in databases.items():
        if not Path(db_file).exists():
            if info['critical']:
                missing_critical = True
            else:
                missing_optional = True
    
    # Critical databases status
    print("1. CRITICAL DATABASES:")
    if not missing_critical:
        print("   [OK] All critical databases are present and operational")
        print("   - Main Trading Database: Active")
        print("   - Portfolio Persistence: Active")
    else:
        print("   [ERROR] Missing critical databases!")
        print("   Action required: System may not function properly")
    print()
    
    # Optional databases
    print("2. OPTIONAL DATABASES:")
    if missing_optional:
        print("   [INFO] Optional databases not yet created:")
        for db_file, info in databases.items():
            if not Path(db_file).exists() and not info['critical']:
                print(f"   - {info['name']}: Will be created on first use")
        print()
        print("   RECOMMENDATION:")
        print("   - Paper Trading Database: Create if you want to test strategies")
        print("   - Learning Database: Create if you want AI learning features")
        print()
        print("   These are OPTIONAL and not required for live trading.")
        print("   The system works perfectly without them.")
    else:
        print("   [OK] All optional databases are present")
    print()
    
    # Performance recommendations
    print("3. PERFORMANCE OPTIMIZATIONS:")
    print()
    
    # Check database sizes
    total_size = 0
    for db_file in databases.keys():
        if Path(db_file).exists():
            total_size += Path(db_file).stat().st_size
    
    total_size_mb = total_size / (1024 * 1024)
    
    print(f"   Total Database Size: {total_size_mb:.2f} MB")
    print()
    
    if total_size_mb < 1:
        print("   [INFO] Databases are small - this is normal for a new system")
        print("   - Data will accumulate as you trade")
        print("   - No action needed")
    elif total_size_mb > 100:
        print("   [INFO] Databases are growing - consider:")
        print("   - Regular backups (recommended)")
        print("   - Archive old data if needed")
        print("   - Monitor disk space")
    else:
        print("   [OK] Database sizes are healthy")
    
    print()
    
    # Backup recommendations
    print("4. BACKUP RECOMMENDATIONS:")
    print()
    print("   [RECOMMENDED] Regular backups:")
    print("   - Backup critical databases daily")
    print("   - Store backups in separate location")
    print("   - Test restore procedures")
    print()
    print("   Backup command:")
    print("   - Copy .db files to backup location")
    print("   - Or use: python backup_databases.py (if available)")
    print()
    
    # Maintenance recommendations
    print("5. MAINTENANCE RECOMMENDATIONS:")
    print()
    print("   [RECOMMENDED] Regular maintenance:")
    print("   - Run VACUUM periodically to optimize databases")
    print("   - Check database integrity")
    print("   - Monitor database growth")
    print()
    print("   SQLite maintenance commands:")
    print("   - VACUUM; (optimize database)")
    print("   - PRAGMA integrity_check; (check for corruption)")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    if active_count == total_count:
        print("[OK] All databases are present and operational")
    elif active_count >= 2:  # At least critical databases
        print(f"[OK] Critical databases operational ({active_count}/{total_count} total)")
        print("   Optional databases can be created when needed")
    else:
        print(f"[WARNING] Only {active_count}/{total_count} databases present")
        print("   Some critical databases may be missing")
    
    print()
    print("RECOMMENDATION PRIORITY:")
    print("   1. [DONE] Critical databases are operational")
    print("   2. [OPTIONAL] Create paper trading DB if testing strategies")
    print("   3. [OPTIONAL] Create learning DB if using AI learning features")
    print("   4. [RECOMMENDED] Set up regular backups")
    print("   5. [RECOMMENDED] Schedule periodic maintenance")
    print()
    print("=" * 80)

def main():
    active_count, total_count, databases = check_database_status()
    issues, recommendations = analyze_database_health()
    provide_recommendations(active_count, total_count, databases)

if __name__ == "__main__":
    main()

