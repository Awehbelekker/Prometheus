"""
PROMETHEUS Trading Platform - Comprehensive Post-Reboot System Audit
Provides complete status report on all system components
"""

import os
import sys
import json
import sqlite3
import asyncio
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import glob

class PrometheusSystemAuditor:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.report = {
            "audit_timestamp": datetime.now().isoformat(),
            "system_status": {},
            "trading_performance": {},
            "active_concerns": [],
            "recommendations": [],
            "configuration_status": {}
        }
    
    def print_header(self, text: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")
    
    def print_status(self, emoji: str, text: str, status: str = "INFO"):
        """Print formatted status message"""
        colors = {
            "SUCCESS": "\033[92m",  # Green
            "ERROR": "\033[91m",    # Red
            "WARNING": "\033[93m",  # Yellow
            "INFO": "\033[94m"      # Blue
        }
        reset = "\033[0m"
        print(f"{colors.get(status, '')}{emoji} {text}{reset}")
    
    # ========== SECTION 1: SYSTEM STATUS ==========
    
    def check_backend_status(self) -> Dict[str, Any]:
        """Check backend server status"""
        self.print_header("1. BACKEND SERVER STATUS")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_status("[CHECK]", f"Backend ONLINE - Port 8000", "SUCCESS")
                self.print_status("📊", f"Uptime: {data.get('uptime_seconds', 0):.2f} seconds")
                self.print_status("🗄️", f"Database: {'Connected' if data.get('database_connected') else 'Disconnected'}")
                return {"status": "online", "data": data}
            else:
                self.print_status("[ERROR]", f"Backend returned status {response.status_code}", "ERROR")
                return {"status": "error", "code": response.status_code}
        except requests.exceptions.ConnectionError:
            self.print_status("[ERROR]", "Backend OFFLINE - Not responding on port 8000", "ERROR")
            self.report["active_concerns"].append("Backend server is not running")
            return {"status": "offline"}
        except Exception as e:
            self.print_status("[ERROR]", f"Backend check failed: {e}", "ERROR")
            return {"status": "error", "error": str(e)}
    
    def check_frontend_status(self) -> Dict[str, Any]:
        """Check frontend server status"""
        self.print_header("2. FRONTEND SERVER STATUS")
        
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.print_status("[CHECK]", "Frontend ONLINE - Port 3000", "SUCCESS")
                return {"status": "online"}
            else:
                self.print_status("[WARNING]️", f"Frontend returned status {response.status_code}", "WARNING")
                return {"status": "warning", "code": response.status_code}
        except requests.exceptions.ConnectionError:
            self.print_status("[ERROR]", "Frontend OFFLINE - Not responding on port 3000", "ERROR")
            self.report["active_concerns"].append("Frontend server is not running")
            return {"status": "offline"}
        except Exception as e:
            self.print_status("[ERROR]", f"Frontend check failed: {e}", "ERROR")
            return {"status": "error", "error": str(e)}
    
    def check_database_status(self) -> Dict[str, Any]:
        """Check database files and integrity"""
        self.print_header("3. DATABASE STATUS")
        
        critical_dbs = [
            "prometheus_trading.db",
            "prometheus_learning.db",
            "live_trading.db",
            "paper_trading.db"
        ]
        
        db_status = {}
        for db_name in critical_dbs:
            if os.path.exists(db_name):
                size_mb = os.path.getsize(db_name) / (1024 * 1024)
                self.print_status("[CHECK]", f"{db_name}: {size_mb:.2f} MB", "SUCCESS")
                db_status[db_name] = {"exists": True, "size_mb": size_mb}
            else:
                self.print_status("[ERROR]", f"{db_name}: NOT FOUND", "ERROR")
                db_status[db_name] = {"exists": False}
                self.report["active_concerns"].append(f"Missing database: {db_name}")
        
        return db_status
    
    def check_active_trading_sessions(self) -> Dict[str, Any]:
        """Check for active trading sessions"""
        self.print_header("4. ACTIVE TRADING SESSIONS")
        
        sessions = {"live": [], "paper": [], "internal": []}
        
        # Check live trading database
        if os.path.exists("live_trading.db"):
            try:
                conn = sqlite3.connect("live_trading.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name LIKE '%session%'
                """)
                tables = cursor.fetchall()
                
                if tables:
                    self.print_status("📊", f"Found {len(tables)} session table(s) in live_trading.db")
                else:
                    self.print_status("[INFO]️", "No active live trading sessions found")
                
                conn.close()
            except Exception as e:
                self.print_status("[WARNING]️", f"Error checking live trading: {e}", "WARNING")
        
        # Check for recent log files
        recent_logs = sorted(glob.glob("prometheus_live_trading_*.log"), 
                           key=os.path.getmtime, reverse=True)[:3]
        
        if recent_logs:
            self.print_status("📝", f"Found {len(recent_logs)} recent trading log(s)")
            for log in recent_logs:
                mtime = datetime.fromtimestamp(os.path.getmtime(log))
                age = datetime.now() - mtime
                self.print_status("  ", f"  {log} - {age.total_seconds()/3600:.1f} hours old")
        else:
            self.print_status("[INFO]️", "No recent trading logs found")
        
        return sessions
    
    # ========== SECTION 2: TRADING PERFORMANCE ==========
    
    def analyze_trading_performance(self) -> Dict[str, Any]:
        """Analyze recent trading performance"""
        self.print_header("5. TRADING PERFORMANCE ANALYSIS")
        
        performance = {
            "total_trades": 0,
            "profitable_trades": 0,
            "total_pnl": 0.0,
            "win_rate": 0.0,
            "daily_return": 0.0
        }
        
        # Check prometheus_learning.db for trade history
        if os.path.exists("prometheus_learning.db"):
            try:
                conn = sqlite3.connect("prometheus_learning.db")
                cursor = conn.cursor()
                
                # Get recent trades (last 7 days)
                seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
                
                cursor.execute("""
                    SELECT COUNT(*) FROM trade_outcomes 
                    WHERE timestamp > ?
                """, (seven_days_ago,))
                
                count = cursor.fetchone()[0]
                performance["total_trades"] = count
                
                if count > 0:
                    self.print_status("📈", f"Total trades (last 7 days): {count}")
                    
                    # Calculate win rate and PnL if possible
                    cursor.execute("""
                        SELECT profit_loss, success FROM trade_outcomes 
                        WHERE timestamp > ?
                    """, (seven_days_ago,))
                    
                    trades = cursor.fetchall()
                    total_pnl = sum(t[0] for t in trades if t[0] is not None)
                    profitable = sum(1 for t in trades if t[1] == 1)
                    
                    performance["total_pnl"] = total_pnl
                    performance["profitable_trades"] = profitable
                    performance["win_rate"] = (profitable / count * 100) if count > 0 else 0
                    
                    self.print_status("💰", f"Total P&L: ${total_pnl:.2f}")
                    self.print_status("🎯", f"Win Rate: {performance['win_rate']:.1f}%")
                    self.print_status("[CHECK]", f"Profitable Trades: {profitable}/{count}")
                else:
                    self.print_status("[INFO]️", "No trades found in last 7 days")
                
                conn.close()
            except Exception as e:
                self.print_status("[WARNING]️", f"Error analyzing performance: {e}", "WARNING")
        else:
            self.print_status("[WARNING]️", "prometheus_learning.db not found", "WARNING")
        
        # Compare against 6-9% daily target
        if performance["daily_return"] > 0:
            if performance["daily_return"] >= 6.0:
                self.print_status("🎉", f"EXCEEDING TARGET: {performance['daily_return']:.2f}% daily return", "SUCCESS")
            elif performance["daily_return"] >= 3.0:
                self.print_status("📊", f"GOOD PROGRESS: {performance['daily_return']:.2f}% daily return")
            else:
                self.print_status("[WARNING]️", f"BELOW TARGET: {performance['daily_return']:.2f}% daily return", "WARNING")
                self.report["active_concerns"].append(f"Daily return ({performance['daily_return']:.2f}%) below 6-9% target")
        
        return performance
    
    # ========== SECTION 3: CONFIGURATION VERIFICATION ==========
    
    def verify_ib_configuration(self) -> Dict[str, Any]:
        """Verify Interactive Brokers configuration"""
        self.print_header("6. INTERACTIVE BROKERS CONFIGURATION")
        
        ib_config = {
            "account": os.getenv("IB_LIVE_ACCOUNT", "Not Set"),
            "host": os.getenv("IB_LIVE_HOST", "127.0.0.1"),
            "port": os.getenv("IB_LIVE_PORT", "7496"),
            "configured": False
        }
        
        if ib_config["account"] == "U21922116":
            self.print_status("[CHECK]", f"IB Account: {ib_config['account']}", "SUCCESS")
            ib_config["configured"] = True
        else:
            self.print_status("[WARNING]️", f"IB Account: {ib_config['account']} (Expected: U21922116)", "WARNING")
            self.report["recommendations"].append("Set IB_LIVE_ACCOUNT=U21922116 in environment")
        
        self.print_status("📡", f"IB Host: {ib_config['host']}")
        self.print_status("🔌", f"IB Port: {ib_config['port']}")
        
        # Check if IB Gateway is running (attempt connection test)
        self.print_status("🔍", "Checking IB Gateway connectivity...")
        # Note: Actual connection test would require IB API
        
        return ib_config
    
    def verify_market_data_feeds(self) -> Dict[str, Any]:
        """Verify market data feed configuration"""
        self.print_header("7. MARKET DATA FEEDS")
        
        feeds = {
            "polygon": os.getenv("POLYGON_API_KEY", "Not Set"),
            "alpaca": os.getenv("ALPACA_API_KEY", "Not Set"),
            "yahoo": "Built-in (No API key required)"
        }
        
        for feed, status in feeds.items():
            if status == "Not Set":
                self.print_status("[WARNING]️", f"{feed.upper()}: Not configured", "WARNING")
            elif "Not Set" not in status:
                masked = status[:8] + "..." if len(status) > 8 else "Configured"
                self.print_status("[CHECK]", f"{feed.upper()}: {masked}", "SUCCESS")
        
        return feeds
    
    def generate_recommendations(self):
        """Generate actionable recommendations"""
        self.print_header("8. RECOMMENDATIONS & NEXT STEPS")
        
        # Check if servers are running
        if self.report["system_status"].get("backend", {}).get("status") == "offline":
            self.report["recommendations"].append("START BACKEND: Run 'python unified_production_server.py' or 'start_servers.bat'")
            self.print_status("🔧", "START BACKEND: Run 'python unified_production_server.py'", "WARNING")
        
        if self.report["system_status"].get("frontend", {}).get("status") == "offline":
            self.report["recommendations"].append("START FRONTEND: Run 'npm start' in frontend directory")
            self.print_status("🔧", "START FRONTEND: Run 'npm start' in frontend directory", "WARNING")
        
        # Check for trading activity
        if self.report["trading_performance"].get("total_trades", 0) == 0:
            self.report["recommendations"].append("NO RECENT TRADING: Consider starting a new trading session")
            self.print_status("💡", "NO RECENT TRADING: Consider starting a new trading session")
        
        # Performance recommendations
        if self.report["trading_performance"].get("win_rate", 0) < 50:
            self.report["recommendations"].append("LOW WIN RATE: Review trading strategies and risk parameters")
            self.print_status("💡", "LOW WIN RATE: Review trading strategies and risk parameters")
        
        # Print all recommendations
        if not self.report["recommendations"]:
            self.print_status("[CHECK]", "System appears healthy - No critical recommendations", "SUCCESS")
    
    def save_report(self):
        """Save audit report to file"""
        filename = f"system_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.report, f, indent=2)
        self.print_status("💾", f"Full report saved to: {filename}")
    
    def run_audit(self):
        """Run complete system audit"""
        print("\n" + "="*80)
        print("  🚀 PROMETHEUS TRADING PLATFORM - COMPREHENSIVE SYSTEM AUDIT")
        print("="*80)
        
        # Section 1: System Status
        self.report["system_status"]["backend"] = self.check_backend_status()
        self.report["system_status"]["frontend"] = self.check_frontend_status()
        self.report["system_status"]["database"] = self.check_database_status()
        self.report["system_status"]["sessions"] = self.check_active_trading_sessions()
        
        # Section 2: Trading Performance
        self.report["trading_performance"] = self.analyze_trading_performance()
        
        # Section 3: Configuration
        self.report["configuration_status"]["ib"] = self.verify_ib_configuration()
        self.report["configuration_status"]["market_data"] = self.verify_market_data_feeds()
        
        # Section 4: Recommendations
        self.generate_recommendations()
        
        # Save report
        self.save_report()
        
        # Final summary
        self.print_header("AUDIT COMPLETE")
        concerns_count = len(self.report["active_concerns"])
        if concerns_count == 0:
            self.print_status("[CHECK]", "No critical issues detected", "SUCCESS")
        else:
            self.print_status("[WARNING]️", f"{concerns_count} concern(s) identified", "WARNING")
            for concern in self.report["active_concerns"]:
                self.print_status("  ", f"  • {concern}")

if __name__ == "__main__":
    auditor = PrometheusSystemAuditor()
    auditor.run_audit()

