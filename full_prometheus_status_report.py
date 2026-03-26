#!/usr/bin/env python3
"""
FULL PROMETHEUS STATUS REPORT
Comprehensive status check for all systems, trading brokers, and learning
"""

import sys
import os
import psutil
import requests
import sqlite3
import socket
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

sys.stdout.reconfigure(encoding='utf-8')

class FullPrometheusStatusReport:
    def __init__(self):
        self.report = []
        self.status_summary = {
            'prometheus_systems': {},
            'trading_brokers': {},
            'learning_systems': {},
            'databases': {},
            'servers': {}
        }
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to report"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.report.append(f"[{timestamp}] {level}: {message}")
        print(f"[{timestamp}] {message}")
    
    def check_python_processes(self):
        """Check all Python processes related to Prometheus"""
        self.log("="*80)
        self.log("1. PYTHON PROCESSES")
        self.log("="*80)
        
        prometheus_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if any(keyword in cmdline.lower() for keyword in ['prometheus', 'trading', 'uvicorn', 'unified_production_server', 'launch_ultimate', 'backtest', 'benchmark']):
                        uptime = datetime.now() - datetime.fromtimestamp(proc.info['create_time'])
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                        prometheus_processes.append({
                            'pid': proc.info['pid'],
                            'cmd': cmdline[:100],
                            'uptime': str(uptime).split('.')[0],
                            'memory_mb': memory_mb
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if prometheus_processes:
            self.log(f"Found {len(prometheus_processes)} Prometheus-related process(es):")
            for proc in prometheus_processes:
                self.log(f"  PID {proc['pid']}: {proc['uptime']} uptime, {proc['memory_mb']:.1f} MB")
                self.log(f"    Command: {proc['cmd'][:80]}...")
            self.status_summary['prometheus_systems']['processes'] = len(prometheus_processes)
        else:
            self.log("No Prometheus-related Python processes found", "WARNING")
            self.status_summary['prometheus_systems']['processes'] = 0
    
    def check_servers(self):
        """Check all backend servers"""
        self.log("\n" + "="*80)
        self.log("2. BACKEND SERVERS")
        self.log("="*80)
        
        servers = {
            "Main Backend": ("http://localhost:8000/health", 8000),
            "GPT-OSS 20B": ("http://localhost:5000/health", 5000),
            "GPT-OSS 120B": ("http://localhost:5001/health", 5001),
            "Revolutionary": ("http://localhost:8002/health", 8002),
            "Metrics": ("http://localhost:8001/health", 8001)
        }
        
        for name, (url, port) in servers.items():
            # Check port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            port_open = sock.connect_ex(('127.0.0.1', port)) == 0
            sock.close()
            
            if port_open:
                try:
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                        self.log(f"✅ {name} (Port {port}): UP")
                        if 'uptime_seconds' in data:
                            uptime_hours = data['uptime_seconds'] / 3600
                            self.log(f"   Uptime: {uptime_hours:.2f} hours")
                        self.status_summary['servers'][name] = 'UP'
                    else:
                        self.log(f"⚠️ {name} (Port {port}): RESPONDING (Status: {response.status_code})")
                        self.status_summary['servers'][name] = 'PARTIAL'
                except Exception as e:
                    self.log(f"⚠️ {name} (Port {port}): PORT OPEN but endpoint error: {e}")
                    self.status_summary['servers'][name] = 'PARTIAL'
            else:
                self.log(f"❌ {name} (Port {port}): DOWN")
                self.status_summary['servers'][name] = 'DOWN'
    
    def check_alpaca_trading(self):
        """Check Alpaca broker connection and trading activity"""
        self.log("\n" + "="*80)
        self.log("3. ALPACA TRADING STATUS")
        self.log("="*80)
        
        # Check credentials
        alpaca_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_PAPER_KEY') or os.getenv('APCA_API_KEY_ID')
        alpaca_secret = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_PAPER_SECRET') or os.getenv('APCA_API_SECRET_KEY')
        
        if not alpaca_key or not alpaca_secret:
            self.log("❌ Alpaca: CREDENTIALS NOT CONFIGURED", "WARNING")
            self.status_summary['trading_brokers']['alpaca'] = {'connected': False, 'error': 'No credentials'}
            return
        
        self.log(f"✅ Alpaca: Credentials configured")
        
        # Try to connect via API
        try:
            import alpaca_trade_api as tradeapi
            
            paper_trading = os.getenv('ALPACA_PAPER_TRADING', 'true').lower() == 'true'
            base_url = 'https://paper-api.alpaca.markets' if paper_trading else 'https://api.alpaca.markets'
            
            api = tradeapi.REST(alpaca_key, alpaca_secret, base_url, api_version='v2')
            account = api.get_account()
            
            self.log(f"✅ Alpaca: CONNECTED ({'PAPER' if paper_trading else 'LIVE'})")
            self.log(f"   Account: {account.account_number}")
            self.log(f"   Status: {account.status}")
            self.log(f"   Equity: ${float(account.equity):,.2f}")
            self.log(f"   Cash: ${float(account.cash):,.2f}")
            self.log(f"   Buying Power: ${float(account.buying_power):,.2f}")
            
            # Check recent positions
            positions = api.list_positions()
            self.log(f"   Open Positions: {len(positions)}")
            if positions:
                for pos in positions[:5]:  # Show first 5
                    self.log(f"     - {pos.symbol}: {pos.qty} @ ${float(pos.avg_entry_price):.2f}")
            
            # Check recent orders
            orders = api.list_orders(status='all', limit=10)
            recent_orders = [o for o in orders if o.created_at and (datetime.now() - datetime.fromisoformat(o.created_at.replace('Z', '+00:00')).replace(tzinfo=None)).total_seconds() < 86400]
            self.log(f"   Orders (last 24h): {len(recent_orders)}")
            
            self.status_summary['trading_brokers']['alpaca'] = {
                'connected': True,
                'account_number': account.account_number,
                'equity': float(account.equity),
                'positions': len(positions),
                'recent_orders': len(recent_orders)
            }
            
        except ImportError:
            self.log("⚠️ Alpaca: API library not installed (alpaca-trade-api)", "WARNING")
            self.status_summary['trading_brokers']['alpaca'] = {'connected': False, 'error': 'Library not installed'}
        except Exception as e:
            self.log(f"❌ Alpaca: Connection failed - {e}", "ERROR")
            self.status_summary['trading_brokers']['alpaca'] = {'connected': False, 'error': str(e)}
        
        # Check database for Alpaca trades
        self.check_alpaca_database()
    
    def check_alpaca_database(self):
        """Check database for Alpaca trading activity"""
        trading_db = "databases/prometheus_trading.db"
        if os.path.exists(trading_db):
            try:
                conn = sqlite3.connect(trading_db)
                cursor = conn.cursor()
                
                # Check if trades table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
                if cursor.fetchone():
                    # Recent trades
                    cursor.execute("""
                        SELECT COUNT(*) FROM trades 
                        WHERE timestamp > datetime('now', '-1 hour')
                        AND broker = 'alpaca'
                    """)
                    recent = cursor.fetchone()[0]
                    
                    # Today's trades
                    cursor.execute("""
                        SELECT COUNT(*) FROM trades 
                        WHERE date(timestamp) = date('now')
                        AND broker = 'alpaca'
                    """)
                    today = cursor.fetchone()[0]
                    
                    # Last trade
                    cursor.execute("""
                        SELECT timestamp, symbol, action, quantity 
                        FROM trades 
                        WHERE broker = 'alpaca'
                        ORDER BY timestamp DESC LIMIT 1
                    """)
                    last_trade = cursor.fetchone()
                    
                    self.log(f"   Database Activity:")
                    self.log(f"     Recent (1h): {recent} trades")
                    self.log(f"     Today: {today} trades")
                    if last_trade:
                        self.log(f"     Last Trade: {last_trade[0]} - {last_trade[2]} {last_trade[3]} {last_trade[1]}")
                
                conn.close()
            except Exception as e:
                self.log(f"   Database check error: {e}", "WARNING")
    
    def check_ib_trading(self):
        """Check Interactive Brokers connection and trading activity"""
        self.log("\n" + "="*80)
        self.log("4. INTERACTIVE BROKERS TRADING STATUS")
        self.log("="*80)
        
        # Check if IB Gateway/TWS is running
        ib_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info.get('name', '').lower()
                if 'tws' in name or 'ibgateway' in name or 'ib gateway' in name:
                    ib_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if not ib_processes:
            self.log("❌ IB Gateway/TWS: NOT RUNNING", "WARNING")
            self.log("   IB Gateway must be running for trading")
            self.log("   Expected: IB Gateway on port 7496 (LIVE) or 7497 (PAPER)")
            self.status_summary['trading_brokers']['ib'] = {'connected': False, 'error': 'Gateway not running'}
            return
        
        self.log(f"✅ IB Gateway/TWS: RUNNING ({len(ib_processes)} process(es))")
        for proc in ib_processes:
            self.log(f"   PID {proc.info['pid']}: {proc.info['name']}")
        
        # Check port
        ib_port = int(os.getenv('IB_GATEWAY_PORT', '7497'))
        ib_host = os.getenv('IB_GATEWAY_HOST', '127.0.0.1')
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        port_open = sock.connect_ex((ib_host, ib_port)) == 0
        sock.close()
        
        if port_open:
            self.log(f"✅ IB Port {ib_port}: OPEN")
            
            # Try to connect via ib_insync
            try:
                from ib_insync import IB
                import asyncio
                
                ib = IB()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    connected = loop.run_until_complete(asyncio.wait_for(
                        ib.connectAsync(ib_host, ib_port, clientId=int(os.getenv('IB_CLIENT_ID', '1'))),
                        timeout=3.0
                    ))
                    
                    if connected:
                        account_values = ib.accountValues()
                        positions = ib.positions()
                        
                        self.log(f"✅ IB: CONNECTED")
                        self.log(f"   Host: {ib_host}:{ib_port}")
                        self.log(f"   Client ID: {os.getenv('IB_CLIENT_ID', '1')}")
                        self.log(f"   Positions: {len(positions)}")
                        
                        if account_values:
                            for av in account_values[:5]:  # Show first 5
                                if av.tag in ['NetLiquidation', 'TotalCashValue', 'BuyingPower']:
                                    self.log(f"   {av.tag}: {av.value}")
                        
                        self.status_summary['trading_brokers']['ib'] = {
                            'connected': True,
                            'positions': len(positions),
                            'host': ib_host,
                            'port': ib_port
                        }
                        
                        ib.disconnect()
                    else:
                        self.log("⚠️ IB: Port open but connection failed", "WARNING")
                        self.status_summary['trading_brokers']['ib'] = {'connected': False, 'error': 'Connection failed'}
                except asyncio.TimeoutError:
                    self.log("⚠️ IB: Connection timeout (Gateway may be busy)", "WARNING")
                    self.status_summary['trading_brokers']['ib'] = {'connected': False, 'error': 'Timeout'}
                finally:
                    loop.close()
                    
            except ImportError:
                self.log("⚠️ IB: ib_insync library not installed", "WARNING")
                self.status_summary['trading_brokers']['ib'] = {'connected': False, 'error': 'Library not installed'}
            except Exception as e:
                self.log(f"⚠️ IB: Connection check error - {e}", "WARNING")
                self.status_summary['trading_brokers']['ib'] = {'connected': False, 'error': str(e)}
        else:
            self.log(f"❌ IB Port {ib_port}: CLOSED", "WARNING")
            self.status_summary['trading_brokers']['ib'] = {'connected': False, 'error': 'Port closed'}
        
        # Check database for IB trades
        self.check_ib_database()
    
    def check_ib_database(self):
        """Check database for IB trading activity"""
        trading_db = "databases/prometheus_trading.db"
        if os.path.exists(trading_db):
            try:
                conn = sqlite3.connect(trading_db)
                cursor = conn.cursor()
                
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'")
                if cursor.fetchone():
                    cursor.execute("""
                        SELECT COUNT(*) FROM trades 
                        WHERE timestamp > datetime('now', '-1 hour')
                        AND broker = 'interactive_brokers'
                    """)
                    recent = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT COUNT(*) FROM trades 
                        WHERE date(timestamp) = date('now')
                        AND broker = 'interactive_brokers'
                    """)
                    today = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        SELECT timestamp, symbol, action, quantity 
                        FROM trades 
                        WHERE broker = 'interactive_brokers'
                        ORDER BY timestamp DESC LIMIT 1
                    """)
                    last_trade = cursor.fetchone()
                    
                    self.log(f"   Database Activity:")
                    self.log(f"     Recent (1h): {recent} trades")
                    self.log(f"     Today: {today} trades")
                    if last_trade:
                        self.log(f"     Last Trade: {last_trade[0]} - {last_trade[2]} {last_trade[3]} {last_trade[1]}")
                
                conn.close()
            except Exception as e:
                self.log(f"   Database check error: {e}", "WARNING")
    
    def check_learning_systems(self):
        """Check learning system status"""
        self.log("\n" + "="*80)
        self.log("5. LEARNING SYSTEMS STATUS")
        self.log("="*80)
        
        # Check learning database
        learning_db = "databases/prometheus_learning.db"
        if os.path.exists(learning_db):
            try:
                conn = sqlite3.connect(learning_db)
                cursor = conn.cursor()
                
                # Check for learning tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                self.log(f"✅ Learning Database: EXISTS ({len(tables)} tables)")
                
                # Check recent learning activity
                if 'learning_events' in tables:
                    cursor.execute("""
                        SELECT COUNT(*) FROM learning_events 
                        WHERE timestamp > datetime('now', '-24 hours')
                    """)
                    recent_events = cursor.fetchone()[0]
                    self.log(f"   Learning Events (24h): {recent_events}")
                
                if 'pattern_learning' in tables:
                    cursor.execute("SELECT COUNT(*) FROM pattern_learning")
                    patterns = cursor.fetchone()[0]
                    self.log(f"   Learned Patterns: {patterns}")
                
                if 'trade_history' in tables:
                    cursor.execute("""
                        SELECT COUNT(*) FROM trade_history 
                        WHERE timestamp > datetime('now', '-24 hours')
                    """)
                    recent_trades = cursor.fetchone()[0]
                    self.log(f"   Trade History Entries (24h): {recent_trades}")
                
                conn.close()
                self.status_summary['learning_systems']['database'] = 'active'
            except Exception as e:
                self.log(f"⚠️ Learning Database: Error - {e}", "WARNING")
                self.status_summary['learning_systems']['database'] = 'error'
        else:
            self.log("⚠️ Learning Database: NOT FOUND", "WARNING")
            self.status_summary['learning_systems']['database'] = 'not_found'
        
        # Check learning API endpoints
        learning_endpoints = {
            "Continuous Learning": "/api/learning/continuous-learning/status",
            "Advanced Learning": "/api/learning/advanced-learning/status",
            "Autonomous Improvement": "/api/learning/autonomous-improvement/status",
            "Unified Learning": "/api/learning/unified/status"
        }
        
        for name, endpoint in learning_endpoints.items():
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ {name}: ACTIVE")
                    if 'last_update' in data:
                        self.log(f"   Last Update: {data['last_update']}")
                    self.status_summary['learning_systems'][name.lower().replace(' ', '_')] = 'active'
                else:
                    self.log(f"⚠️ {name}: HTTP {response.status_code}", "WARNING")
                    self.status_summary['learning_systems'][name.lower().replace(' ', '_')] = 'inactive'
            except Exception as e:
                self.log(f"⚠️ {name}: Not responding - {e}", "WARNING")
                self.status_summary['learning_systems'][name.lower().replace(' ', '_')] = 'error'
    
    def check_databases(self):
        """Check all databases"""
        self.log("\n" + "="*80)
        self.log("6. DATABASE STATUS")
        self.log("="*80)
        
        databases = {
            "prometheus_trading.db": "databases/prometheus_trading.db",
            "prometheus_portfolio.db": "databases/prometheus_portfolio.db",
            "prometheus_learning.db": "databases/prometheus_learning.db",
            "prometheus_analytics.db": "databases/prometheus_analytics.db",
            "internal_paper_trading.db": "internal_paper_trading.db"
        }
        
        for name, path in databases.items():
            if os.path.exists(path):
                size_mb = os.path.getsize(path) / 1024 / 1024
                mod_time = datetime.fromtimestamp(os.path.getmtime(path))
                age = datetime.now() - mod_time
                self.log(f"✅ {name}: {size_mb:.2f} MB (modified {age.total_seconds()/3600:.1f}h ago)")
                self.status_summary['databases'][name] = {'size_mb': size_mb, 'exists': True}
            else:
                self.log(f"⚠️ {name}: NOT FOUND", "WARNING")
                self.status_summary['databases'][name] = {'exists': False}
    
    def generate_summary(self):
        """Generate final summary"""
        self.log("\n" + "="*80)
        self.log("FINAL SUMMARY")
        self.log("="*80)
        
        # Prometheus Systems
        processes = self.status_summary['prometheus_systems'].get('processes', 0)
        self.log(f"Prometheus Processes: {processes}")
        
        # Servers
        servers_up = sum(1 for s in self.status_summary['servers'].values() if s == 'UP')
        servers_total = len(self.status_summary['servers'])
        self.log(f"Backend Servers: {servers_up}/{servers_total} UP")
        
        # Trading Brokers
        alpaca_status = self.status_summary['trading_brokers'].get('alpaca', {})
        ib_status = self.status_summary['trading_brokers'].get('ib', {})
        self.log(f"Alpaca: {'✅ CONNECTED' if alpaca_status.get('connected') else '❌ NOT CONNECTED'}")
        self.log(f"Interactive Brokers: {'✅ CONNECTED' if ib_status.get('connected') else '❌ NOT CONNECTED'}")
        
        # Learning Systems
        learning_active = sum(1 for s in self.status_summary['learning_systems'].values() if s == 'active')
        learning_total = len([k for k in self.status_summary['learning_systems'].keys() if k != 'database'])
        self.log(f"Learning Systems: {learning_active}/{learning_total} ACTIVE")
        
        # Databases
        dbs_exist = sum(1 for d in self.status_summary['databases'].values() if d.get('exists'))
        dbs_total = len(self.status_summary['databases'])
        self.log(f"Databases: {dbs_exist}/{dbs_total} EXIST")
        
        self.log("="*80)
    
    def save_report(self):
        """Save report to file"""
        report_text = "\n".join(self.report)
        with open('FULL_STATUS_REPORT.txt', 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("FULL PROMETHEUS STATUS REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            f.write(report_text)
            f.write("\n" + "="*80 + "\n")
        
        self.log(f"\n✅ Full report saved to: FULL_STATUS_REPORT.txt")
    
    def run(self):
        """Run full status check"""
        self.log("="*80)
        self.log("FULL PROMETHEUS STATUS REPORT")
        self.log("="*80)
        self.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*80)
        
        self.check_python_processes()
        self.check_servers()
        self.check_alpaca_trading()
        self.check_ib_trading()
        self.check_learning_systems()
        self.check_databases()
        self.generate_summary()
        self.save_report()

if __name__ == "__main__":
    report = FullPrometheusStatusReport()
    report.run()

