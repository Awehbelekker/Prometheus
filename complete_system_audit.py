#!/usr/bin/env python3
"""
Complete Prometheus System Audit and Fix
Comprehensive check of all components and automatic fixes
"""

import os
import sys
import psutil
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class SystemAuditor:
    def __init__(self):
        self.issues = []
        self.fixes_applied = []
        self.status = {}
        
    def print_header(self, text):
        print()
        print("=" * 80)
        print(text)
        print("=" * 80)
        print()
    
    def add_issue(self, component, issue, severity="MEDIUM", fix=None):
        self.issues.append({
            'component': component,
            'issue': issue,
            'severity': severity,
            'fix': fix
        })
    
    def apply_fix(self, component, fix_description):
        self.fixes_applied.append({
            'component': component,
            'fix': fix_description,
            'timestamp': datetime.now()
        })
        print(f"[FIX] {component}: {fix_description}")
    
    def check_prometheus_process(self):
        """Check if Prometheus trading system is running"""
        self.print_header("1. PROMETHEUS TRADING SYSTEM")
        
        prometheus_running = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline_parts = proc.info.get('cmdline') or []
                cmdline = ' '.join(str(c) for c in cmdline_parts) if cmdline_parts else ''
                if 'launch_ultimate_prometheus' in cmdline.lower():
                    prometheus_running = True
                    runtime = (datetime.now().timestamp() - proc.create_time()) / 60
                    print(f"[OK] Prometheus Trading System: RUNNING")
                    print(f"   PID: {proc.info['pid']}")
                    print(f"   Runtime: {int(runtime)} minutes")
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not prometheus_running:
            print("[ERROR] Prometheus Trading System: NOT RUNNING")
            self.add_issue("Prometheus", "Trading system not running", "CRITICAL", 
                          "Start with: python full_system_restart.py")
            return False
        
        self.status['prometheus'] = True
        return True
    
    def check_alpaca_broker(self):
        """Check Alpaca broker connection"""
        self.print_header("2. ALPACA BROKER")
        
        try:
            import alpaca_trade_api as tradeapi
            
            api_key = (os.getenv('ALPACA_API_KEY') or 
                      os.getenv('ALPACA_LIVE_KEY') or
                      os.getenv('APCA_API_KEY_ID'))
            secret_key = (os.getenv('ALPACA_SECRET_KEY') or 
                         os.getenv('ALPACA_LIVE_SECRET') or
                         os.getenv('APCA_API_SECRET_KEY'))
            base_url = os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
            
            if not api_key or not secret_key:
                print("[ERROR] Alpaca credentials not found")
                self.add_issue("Alpaca", "API credentials missing", "CRITICAL",
                              "Add ALPACA_API_KEY and ALPACA_SECRET_KEY to .env")
                return False
            
            api = tradeapi.REST(api_key, secret_key, base_url, api_version='v2')
            account = api.get_account()
            positions = api.list_positions()
            
            print(f"[OK] Alpaca: CONNECTED")
            print(f"   Account: {account.account_number}")
            print(f"   Status: {account.status}")
            print(f"   Portfolio Value: ${float(account.portfolio_value):,.2f}")
            print(f"   Open Positions: {len(positions)}")
            
            self.status['alpaca'] = True
            return True
            
        except ImportError:
            print("[ERROR] alpaca_trade_api not installed")
            self.add_issue("Alpaca", "Package not installed", "HIGH",
                          "Install: pip install alpaca-trade-api")
            return False
        except Exception as e:
            print(f"[ERROR] Alpaca connection failed: {e}")
            self.add_issue("Alpaca", f"Connection failed: {str(e)[:50]}", "HIGH")
            return False
    
    def check_ib_gateway(self):
        """Check Interactive Brokers Gateway"""
        self.print_header("3. INTERACTIVE BROKERS GATEWAY")
        
        ib_port = int(os.getenv('IB_PORT', '7497'))
        ib_host = os.getenv('IB_HOST', '127.0.0.1')
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ib_host, ib_port))
            sock.close()
            
            if result == 0:
                mode = "LIVE" if ib_port == 7497 else "PAPER"
                print(f"[OK] IB Gateway: RUNNING")
                print(f"   Port: {ib_port} ({mode} trading)")
                print(f"   Host: {ib_host}")
                self.status['ib'] = True
                return True
            else:
                print(f"[ERROR] IB Gateway: NOT RUNNING")
                print(f"   Port {ib_port} is closed")
                self.add_issue("IB Gateway", f"Port {ib_port} not accessible", "HIGH",
                              "Start IB Gateway and enable API connections")
                return False
        except Exception as e:
            print(f"[ERROR] Could not check IB Gateway: {e}")
            self.add_issue("IB Gateway", f"Check failed: {str(e)[:50]}", "MEDIUM")
            return False
    
    def check_ai_systems(self):
        """Check AI systems status"""
        self.print_header("4. AI SYSTEMS")
        
        # Check CPT-OSS
        try:
            from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
            gpt_oss = GPTOSSTradingAdapter()
            if gpt_oss:
                model_size = getattr(gpt_oss, 'model_size', '20b')
                print(f"[OK] CPT-OSS: AVAILABLE (Model: {model_size})")
                self.status['cpt_oss'] = True
            else:
                print("[WARNING] CPT-OSS: Not initialized")
                self.status['cpt_oss'] = False
        except Exception as e:
            print(f"[WARNING] CPT-OSS: {str(e)[:50]}")
            self.status['cpt_oss'] = False
        
        # Check Universal Reasoning Engine
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            print("[OK] Universal Reasoning Engine: Available")
            self.status['reasoning'] = True
        except Exception as e:
            print(f"[WARNING] Universal Reasoning Engine: {str(e)[:50]}")
            self.status['reasoning'] = False
        
        # Check Market Oracle
        try:
            from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
            print("[OK] Market Oracle Engine: Available")
            self.status['oracle'] = True
        except Exception as e:
            print(f"[WARNING] Market Oracle: {str(e)[:50]}")
            self.status['oracle'] = False
        
        return True
    
    def check_backend_server(self):
        """Check backend API server"""
        self.print_header("5. BACKEND API SERVER")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', 8000))
            sock.close()
            
            if result == 0:
                print("[OK] Backend Server: RUNNING")
                print("   URL: http://localhost:8000")
                print("   Docs: http://localhost:8000/docs")
                self.status['backend'] = True
                return True
            else:
                print("[INFO] Backend Server: Not running (optional)")
                print("   To start: python start_backend_windows.py")
                self.status['backend'] = False
                return False
        except Exception as e:
            print(f"[INFO] Backend Server: Could not check ({str(e)[:30]})")
            self.status['backend'] = False
            return False
    
    def check_databases(self):
        """Check trading databases"""
        self.print_header("6. DATABASES")
        
        db_files = {
            'prometheus_trading.db': 'Main Trading Database',
            'portfolio_persistence.db': 'Portfolio Persistence',
            'enhanced_paper_trading.db': 'Paper Trading Database',
            'learning_database.db': 'Learning Database'
        }
        
        found = 0
        for db_file, description in db_files.items():
            db_path = Path(db_file)
            if db_path.exists():
                size_mb = db_path.stat().st_size / (1024 * 1024)
                print(f"[OK] {description}: {size_mb:.2f} MB")
                found += 1
            else:
                print(f"[INFO] {description}: Not found (will be created on first use)")
        
        print(f"\nActive Databases: {found}/{len(db_files)}")
        self.status['databases'] = found
        return True
    
    def check_metrics_server(self):
        """Check metrics server"""
        self.print_header("7. METRICS SERVER")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', 9090))
            sock.close()
            
            if result == 0:
                print("[OK] Metrics Server: RUNNING (port 9090)")
                self.status['metrics'] = True
                return True
            else:
                print("[INFO] Metrics Server: Not active")
                self.status['metrics'] = False
                return False
        except:
            print("[INFO] Metrics Server: Could not check")
            self.status['metrics'] = False
            return False
    
    def check_configuration(self):
        """Check key configuration"""
        self.print_header("8. CONFIGURATION")
        
        # Alpaca
        alpaca_key = (os.getenv('ALPACA_API_KEY') or 
                     os.getenv('ALPACA_LIVE_KEY') or
                     os.getenv('APCA_API_KEY_ID'))
        print(f"Alpaca API Key: {'[OK] SET' if alpaca_key else '[ERROR] NOT SET'}")
        
        # IB
        ib_port = os.getenv('IB_PORT', '7497')
        ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
        print(f"IB Port: {ib_port} ({'LIVE' if ib_port == '7497' else 'PAPER'})")
        print(f"IB Account: {ib_account}")
        
        # CUDA
        try:
            import torch
            cuda_available = torch.cuda.is_available()
            print(f"CUDA: {'[OK] AVAILABLE' if cuda_available else '[INFO] CPU mode (works fine)'}")
        except:
            print("CUDA: [INFO] PyTorch not available")
        
        return True
    
    def check_system_resources(self):
        """Check system resources"""
        self.print_header("9. SYSTEM RESOURCES")
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            print(f"CPU Usage: {cpu_percent:.1f}%")
            if cpu_percent > 90:
                print("   [WARNING] High CPU usage")
            
            print(f"Memory: {memory.percent:.1f}% used ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)")
            if memory.percent > 90:
                print("   [WARNING] High memory usage")
            
            print(f"Disk: {disk.percent:.1f}% used ({disk.used / (1024**3):.1f} GB / {disk.total / (1024**3):.1f} GB)")
            if disk.percent > 90:
                print("   [WARNING] Low disk space")
            
            return True
        except Exception as e:
            print(f"[ERROR] Could not check resources: {e}")
            return False
    
    def apply_fixes(self):
        """Apply automatic fixes"""
        self.print_header("APPLYING FIXES")
        
        if not self.issues:
            print("[OK] No issues found - all systems operational!")
            return
        
        for issue in self.issues:
            if issue['severity'] == 'CRITICAL' and issue['fix']:
                print(f"\n[FIXING] {issue['component']}: {issue['issue']}")
                print(f"   Solution: {issue['fix']}")
                
                # Auto-fix Prometheus not running
                if issue['component'] == 'Prometheus' and 'not running' in issue['issue'].lower():
                    print("   Attempting to start Prometheus...")
                    try:
                        subprocess.Popen(
                            ["python", "full_system_restart.py"],
                            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                        )
                        self.apply_fix("Prometheus", "Started trading system")
                    except Exception as e:
                        print(f"   [ERROR] Could not auto-start: {e}")
                
                # Auto-fix backend server
                elif issue['component'] == 'Backend Server' and 'not running' in issue['issue'].lower():
                    print("   Attempting to start backend server...")
                    try:
                        subprocess.Popen(
                            ["python", "start_backend_windows.py"],
                            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
                        )
                        self.apply_fix("Backend Server", "Started backend server")
                    except Exception as e:
                        print(f"   [ERROR] Could not auto-start: {e}")
    
    def generate_report(self):
        """Generate final report"""
        self.print_header("SYSTEM AUDIT REPORT")
        
        print("COMPONENT STATUS:")
        print()
        
        components = {
            'Prometheus Trading System': self.status.get('prometheus', False),
            'Alpaca Broker': self.status.get('alpaca', False),
            'IB Gateway': self.status.get('ib', False),
            'CPT-OSS AI': self.status.get('cpt_oss', False),
            'Reasoning Engine': self.status.get('reasoning', False),
            'Market Oracle': self.status.get('oracle', False),
            'Backend Server': self.status.get('backend', False),
            'Metrics Server': self.status.get('metrics', False),
            'Databases': self.status.get('databases', 0) > 0
        }
        
        critical_components = ['prometheus', 'alpaca', 'ib', 'cpt_oss', 'reasoning', 'oracle']
        critical_status = all(self.status.get(c, False) for c in critical_components)
        
        for component, status in components.items():
            icon = "[OK]" if status else "[WARNING]"
            print(f"  {icon} {component}: {'OPERATIONAL' if status else 'NEEDS ATTENTION'}")
        
        print()
        print("ISSUES FOUND:", len(self.issues))
        if self.issues:
            print()
            for issue in self.issues:
                severity_icon = {
                    'CRITICAL': '[CRITICAL]',
                    'HIGH': '[HIGH]',
                    'MEDIUM': '[MEDIUM]',
                    'LOW': '[LOW]'
                }
                icon = severity_icon.get(issue['severity'], '[INFO]')
                print(f"  {icon} {issue['component']}: {issue['issue']}")
                if issue['fix']:
                    print(f"      Fix: {issue['fix']}")
        
        print()
        print("FIXES APPLIED:", len(self.fixes_applied))
        if self.fixes_applied:
            for fix in self.fixes_applied:
                print(f"  [FIX] {fix['component']}: {fix['fix']}")
        
        print()
        print("=" * 80)
        if critical_status:
            print("OVERALL STATUS: [OK] SYSTEM OPERATIONAL - READY FOR TRADING")
        else:
            print("OVERALL STATUS: [WARNING] SOME ISSUES DETECTED - REVIEW ABOVE")
        print("=" * 80)
    
    def run_audit(self):
        """Run complete system audit"""
        print("=" * 80)
        print("PROMETHEUS COMPLETE SYSTEM AUDIT")
        print("=" * 80)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Run all checks
        self.check_prometheus_process()
        self.check_alpaca_broker()
        self.check_ib_gateway()
        self.check_ai_systems()
        self.check_backend_server()
        self.check_databases()
        self.check_metrics_server()
        self.check_configuration()
        self.check_system_resources()
        
        # Apply fixes
        self.apply_fixes()
        
        # Generate report
        self.generate_report()

def main():
    auditor = SystemAuditor()
    try:
        auditor.run_audit()
    except KeyboardInterrupt:
        print("\n\nAudit cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Audit failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

