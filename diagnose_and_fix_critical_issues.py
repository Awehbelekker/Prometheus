#!/usr/bin/env python3
"""
Comprehensive Diagnostic and Fix Script for Prometheus Critical Issues
Addresses: Backend servers, broker connections, disk space, database errors
"""

import os
import sys
import psutil
import socket
import requests
import sqlite3
import subprocess
import time
import shutil
from datetime import datetime
from pathlib import Path
import json

sys.stdout.reconfigure(encoding='utf-8')

class PrometheusDiagnostic:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        )
        return logging.getLogger(__name__)
    
    def check_backend_process(self):
        """Check if backend process is running but not responding"""
        self.logger.info("="*80)
        self.logger.info("DIAGNOSING BACKEND SERVER ISSUE")
        self.logger.info("="*80)
        
        backend_process = None
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'memory_info']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'unified_production_server' in cmdline or ('uvicorn' in cmdline and '8000' in cmdline):
                    backend_process = proc
                    self.logger.info(f"Found backend process: PID {proc.info['pid']}")
                    self.logger.info(f"  Status: {proc.info['status']}")
                    self.logger.info(f"  Memory: {proc.info['memory_info'].rss / (1024*1024):.1f} MB")
                    self.logger.info(f"  Command: {cmdline[:100]}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if backend_process:
            # Check if port is actually listening
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('127.0.0.1', 8000))
                sock.close()
                
                if result == 0:
                    # Port is open, check if it responds
                    try:
                        response = requests.get('http://127.0.0.1:8000/health', timeout=3)
                        if response.status_code == 200:
                            self.logger.info("✅ Backend is responding correctly")
                            return True
                        else:
                            self.logger.warning(f"⚠️ Backend responded with status {response.status_code}")
                            self.issues.append("Backend responding with non-200 status")
                    except requests.exceptions.RequestException as e:
                        self.logger.error(f"❌ Backend port open but not responding: {e}")
                        self.issues.append(f"Backend process stuck: {e}")
                        return False
                else:
                    self.logger.warning("⚠️ Backend process exists but port 8000 is not listening")
                    self.issues.append("Backend process exists but port not listening")
                    return False
            except Exception as e:
                self.logger.error(f"❌ Error checking backend: {e}")
                self.issues.append(f"Error checking backend: {e}")
                return False
        else:
            self.logger.warning("❌ No backend process found")
            self.issues.append("Backend process not running")
            return False
    
    def fix_backend_server(self):
        """Restart backend server"""
        self.logger.info("\n" + "="*80)
        self.logger.info("FIXING BACKEND SERVER")
        self.logger.info("="*80)
        
        # Kill existing backend processes
        killed = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                if 'unified_production_server' in cmdline or ('uvicorn' in cmdline and '8000' in cmdline):
                    self.logger.info(f"Killing stuck backend process: PID {proc.info['pid']}")
                    proc.kill()
                    proc.wait(timeout=5)
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                pass
        
        if killed:
            self.logger.info("Waiting 3 seconds for cleanup...")
            time.sleep(3)
        
        # Check if port is free
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            if result == 0:
                self.logger.error("❌ Port 8000 still in use after killing process")
                self.issues.append("Port 8000 still occupied")
                return False
        except:
            pass
        
        # Start backend server
        self.logger.info("Starting backend server...")
        try:
            if os.name == 'nt':  # Windows
                # Start in background using PowerShell
                script_path = os.path.join('scripts', 'windows', 'start_backend.ps1')
                if os.path.exists(script_path):
                    subprocess.Popen(['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
                                   cwd=os.getcwd(), creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    # Fallback: direct Python start
                    subprocess.Popen([sys.executable, '-m', 'uvicorn', 'unified_production_server:app',
                                     '--host', '0.0.0.0', '--port', '8000'],
                                    cwd=os.getcwd(), creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # Unix
                subprocess.Popen([sys.executable, '-m', 'uvicorn', 'unified_production_server:app',
                                 '--host', '0.0.0.0', '--port', '8000'],
                                cwd=os.getcwd())
            
            self.logger.info("Waiting 10 seconds for backend to initialize...")
            time.sleep(10)
            
            # Verify it's working
            for attempt in range(5):
                try:
                    response = requests.get('http://127.0.0.1:8000/health', timeout=3)
                    if response.status_code == 200:
                        self.logger.info("✅ Backend server started successfully")
                        self.fixes_applied.append("Backend server restarted")
                        return True
                except:
                    if attempt < 4:
                        self.logger.info(f"Waiting for backend... (attempt {attempt + 1}/5)")
                        time.sleep(3)
            
            self.logger.warning("⚠️ Backend started but not responding yet")
            self.issues.append("Backend started but health check failing")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error starting backend: {e}")
            self.issues.append(f"Failed to start backend: {e}")
            return False
    
    def check_alpaca_credentials(self):
        """Check and guide Alpaca credentials setup"""
        self.logger.info("\n" + "="*80)
        self.logger.info("CHECKING ALPACA CREDENTIALS")
        self.logger.info("="*80)
        
        api_key = os.getenv('ALPACA_API_KEY') or os.getenv('APCA_API_KEY_ID')
        secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('APCA_API_SECRET_KEY')
        
        if not api_key or not secret_key:
            self.logger.warning("❌ Alpaca credentials not configured")
            self.logger.info("\nTo configure Alpaca credentials, set these environment variables:")
            self.logger.info("  ALPACA_API_KEY=<your_api_key>")
            self.logger.info("  ALPACA_SECRET_KEY=<your_secret_key>")
            self.logger.info("\nOr add them to your .env file:")
            self.logger.info("  ALPACA_API_KEY=<your_api_key>")
            self.logger.info("  ALPACA_SECRET_KEY=<your_secret_key>")
            self.issues.append("Alpaca credentials not configured")
            return False
        else:
            self.logger.info("✅ Alpaca credentials found in environment")
            return True
    
    def check_ib_connection(self):
        """Check Interactive Brokers connection and database"""
        self.logger.info("\n" + "="*80)
        self.logger.info("CHECKING INTERACTIVE BROKERS")
        self.logger.info("="*80)
        
        # Check if IB Gateway is running
        ib_running = False
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                name = proc.info.get('name', '').lower()
                if 'tws' in name or 'ibgateway' in name:
                    ib_running = True
                    self.logger.info(f"✅ IB Gateway/TWS running: PID {proc.info['pid']}")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not ib_running:
            self.logger.warning("❌ IB Gateway/TWS not running")
            self.issues.append("IB Gateway not running")
            return False
        
        # Check port
        ib_port = int(os.getenv('IB_GATEWAY_PORT', '7497'))
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', ib_port))
            sock.close()
            if result == 0:
                self.logger.info(f"✅ IB Port {ib_port} is open")
            else:
                self.logger.warning(f"❌ IB Port {ib_port} is closed")
                self.issues.append(f"IB Port {ib_port} closed")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error checking IB port: {e}")
            self.issues.append(f"Error checking IB port: {e}")
            return False
        
        # Check database schema
        self.logger.info("Checking IB database schema...")
        db_path = os.path.join('databases', 'prometheus_trading.db')
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(trades)")
                columns = [row[1] for row in cursor.fetchall()]
                if 'broker' not in columns:
                    self.logger.warning("❌ 'broker' column missing from trades table")
                    self.logger.info("Attempting to fix database schema...")
                    try:
                        cursor.execute("ALTER TABLE trades ADD COLUMN broker TEXT")
                        conn.commit()
                        self.logger.info("✅ Added 'broker' column to trades table")
                        self.fixes_applied.append("Added 'broker' column to trades table")
                    except sqlite3.OperationalError as e:
                        if 'duplicate column' in str(e).lower():
                            self.logger.info("✅ Column already exists (schema is correct)")
                        else:
                            self.logger.error(f"❌ Error fixing schema: {e}")
                            self.issues.append(f"Database schema error: {e}")
                else:
                    self.logger.info("✅ Database schema is correct")
                conn.close()
            except Exception as e:
                self.logger.error(f"❌ Error checking database: {e}")
                self.issues.append(f"Database error: {e}")
        
        return True
    
    def check_disk_space(self):
        """Check and suggest fixes for disk space"""
        self.logger.info("\n" + "="*80)
        self.logger.info("CHECKING DISK SPACE")
        self.logger.info("="*80)
        
        disk = shutil.disk_usage('.')
        total_gb = disk.total / (1024**3)
        used_gb = disk.used / (1024**3)
        free_gb = disk.free / (1024**3)
        usage_pct = (disk.used / disk.total) * 100
        
        self.logger.info(f"Total: {total_gb:.1f} GB")
        self.logger.info(f"Used: {used_gb:.1f} GB ({usage_pct:.1f}%)")
        self.logger.info(f"Free: {free_gb:.1f} GB")
        
        if usage_pct > 90:
            self.logger.warning(f"⚠️ Disk usage is {usage_pct:.1f}% - CRITICAL")
            self.issues.append(f"High disk usage: {usage_pct:.1f}%")
            
            # Find large files
            self.logger.info("\nFinding large files and directories...")
            large_items = []
            for root, dirs, files in os.walk('.'):
                # Skip certain directories
                if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']):
                    continue
                
                for name in files + dirs:
                    path = os.path.join(root, name)
                    try:
                        if os.path.isfile(path):
                            size = os.path.getsize(path)
                            if size > 100 * 1024 * 1024:  # > 100 MB
                                large_items.append((path, size, 'file'))
                        elif os.path.isdir(path):
                            total_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                           for dirpath, dirnames, filenames in os.walk(path)
                                           for filename in filenames)
                            if total_size > 100 * 1024 * 1024:  # > 100 MB
                                large_items.append((path, total_size, 'dir'))
                    except (OSError, PermissionError):
                        pass
                
                # Limit search depth
                if root.count(os.sep) > 3:
                    dirs[:] = []
            
            # Sort by size
            large_items.sort(key=lambda x: x[1], reverse=True)
            
            self.logger.info("\nTop 10 largest items:")
            for path, size, item_type in large_items[:10]:
                size_mb = size / (1024 * 1024)
                self.logger.info(f"  {item_type.upper()}: {path} ({size_mb:.1f} MB)")
            
            # Check logs directory
            log_dirs = ['logs', 'log', '.logs']
            for log_dir in log_dirs:
                if os.path.exists(log_dir):
                    log_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                                 for dirpath, dirnames, filenames in os.walk(log_dir)
                                 for filename in filenames)
                    if log_size > 0:
                        log_size_mb = log_size / (1024 * 1024)
                        self.logger.info(f"\n⚠️ Log directory '{log_dir}' size: {log_size_mb:.1f} MB")
                        self.logger.info(f"   Consider cleaning old logs")
        else:
            self.logger.info(f"✅ Disk usage is acceptable ({usage_pct:.1f}%)")
        
        return usage_pct < 90
    
    def generate_report(self):
        """Generate diagnostic report"""
        self.logger.info("\n" + "="*80)
        self.logger.info("DIAGNOSTIC REPORT")
        self.logger.info("="*80)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'issues_found': len(self.issues),
            'fixes_applied': len(self.fixes_applied),
            'issues': self.issues,
            'fixes': self.fixes_applied
        }
        
        self.logger.info(f"Issues Found: {len(self.issues)}")
        self.logger.info(f"Fixes Applied: {len(self.fixes_applied)}")
        
        if self.issues:
            self.logger.info("\nRemaining Issues:")
            for issue in self.issues:
                self.logger.info(f"  - {issue}")
        
        if self.fixes_applied:
            self.logger.info("\nFixes Applied:")
            for fix in self.fixes_applied:
                self.logger.info(f"  ✅ {fix}")
        
        # Save report
        report_file = 'DIAGNOSTIC_REPORT.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        self.logger.info(f"\n✅ Report saved to: {report_file}")
        
        return report

def main():
    diagnostic = PrometheusDiagnostic()
    
    # Run diagnostics
    backend_ok = diagnostic.check_backend_process()
    
    if not backend_ok:
        diagnostic.fix_backend_server()
    
    diagnostic.check_alpaca_credentials()
    diagnostic.check_ib_connection()
    diagnostic.check_disk_space()
    
    # Generate report
    report = diagnostic.generate_report()
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    if report['issues_found'] == 0:
        print("✅ All systems operational!")
    else:
        print(f"⚠️ {report['issues_found']} issue(s) found")
        print("Review the report above for details")

if __name__ == "__main__":
    main()

