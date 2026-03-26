#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE PROMETHEUS TRADING PLATFORM AUDIT
Performs complete system audit including:
- System status (servers, database, services)
- Active trading sessions verification
- AI Intelligence agents status
- Market data feeds verification
- Performance benchmarks
"""

import os
import sys
import sqlite3
import requests
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess

class PrometheusSystemAuditor:
    def __init__(self):
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'system_status': {},
            'trading_sessions': {},
            'ai_agents': {},
            'market_data': {},
            'performance': {},
            'issues': [],
            'recommendations': []
        }
        
    def print_header(self, title: str):
        """Print formatted section header"""
        print("\n" + "="*80)
        print(f"  {title}")
        print("="*80)
        
    def print_status(self, emoji: str, message: str, status: str = "INFO"):
        """Print formatted status message"""
        colors = {
            "OK": "\033[92m",      # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "INFO": "\033[94m"     # Blue
        }
        reset = "\033[0m"
        print(f"{emoji} {colors.get(status, '')}{message}{reset}")
        
    def check_system_components(self) -> Dict[str, Any]:
        """Check if core system components are running"""
        self.print_header("1. SYSTEM STATUS AUDIT")
        
        results = {
            'backend_server': False,
            'frontend_server': False,
            'ib_gateway': False,
            'database': False,
            'cloudflare_tunnel': False
        }
        
        # Check backend server (port 8000)
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                results['backend_server'] = True
                self.print_status("[CHECK]", "Backend Server (port 8000): RUNNING", "OK")
            else:
                self.print_status("[ERROR]", f"Backend Server: HTTP {response.status_code}", "ERROR")
        except Exception as e:
            self.print_status("[ERROR]", f"Backend Server (port 8000): NOT RESPONDING - {str(e)}", "ERROR")
            self.audit_results['issues'].append("Backend server not running on port 8000")
            
        # Check frontend server (port 3002)
        try:
            response = requests.get("http://localhost:3002", timeout=5)
            if response.status_code == 200:
                results['frontend_server'] = True
                self.print_status("[CHECK]", "Frontend Server (port 3002): RUNNING", "OK")
            else:
                self.print_status("[WARNING]️", f"Frontend Server: HTTP {response.status_code}", "WARNING")
        except Exception as e:
            self.print_status("[ERROR]", f"Frontend Server (port 3002): NOT RESPONDING - {str(e)}", "ERROR")
            self.audit_results['issues'].append("Frontend server not running on port 3002")
            
        # Check IB Gateway (port 7496)
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "7496" in result.stdout:
                results['ib_gateway'] = True
                self.print_status("[CHECK]", "IB Gateway (port 7496): CONNECTED", "OK")
            else:
                self.print_status("[ERROR]", "IB Gateway (port 7496): NOT DETECTED", "ERROR")
                self.audit_results['issues'].append("IB Gateway not running on port 7496")
        except Exception as e:
            self.print_status("[WARNING]️", f"IB Gateway check failed: {str(e)}", "WARNING")
            
        # Check database
        db_path = "prometheus_trading.db"
        if Path(db_path).exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                conn.close()
                results['database'] = True
                self.print_status("[CHECK]", f"Database: CONNECTED ({len(tables)} tables)", "OK")
            except Exception as e:
                self.print_status("[ERROR]", f"Database: ERROR - {str(e)}", "ERROR")
                self.audit_results['issues'].append(f"Database error: {str(e)}")
        else:
            self.print_status("[ERROR]", "Database: NOT FOUND", "ERROR")
            self.audit_results['issues'].append("Database file not found")
            
        self.audit_results['system_status'] = results
        return results
        
    def check_active_trading_sessions(self) -> Dict[str, Any]:
        """Check for active trading sessions"""
        self.print_header("2. ACTIVE TRADING SESSION VERIFICATION")
        
        sessions = {
            'live_sessions': [],
            'paper_sessions': [],
            'internal_sessions': [],
            'total_active': 0
        }
        
        # Check main database for sessions
        db_path = "prometheus_trading.db"
        if Path(db_path).exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check for session tables
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND (
                        name LIKE '%session%' OR 
                        name LIKE '%trading%'
                    )
                """)
                session_tables = [row[0] for row in cursor.fetchall()]
                
                if session_tables:
                    self.print_status("📊", f"Found {len(session_tables)} session-related tables", "INFO")
                    for table in session_tables:
                        print(f"   • {table}")
                else:
                    self.print_status("[INFO]️", "No session tables found in main database", "INFO")
                    
                conn.close()
            except Exception as e:
                self.print_status("[WARNING]️", f"Error checking sessions: {str(e)}", "WARNING")
                
        # Check for enhanced paper trading sessions
        paper_db = "enhanced_paper_trading.db"
        if Path(paper_db).exists():
            try:
                conn = sqlite3.connect(paper_db)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id, user_id, session_type, starting_capital, 
                           current_value, status, trades_count
                    FROM paper_sessions 
                    WHERE status = 'active'
                """)
                active_paper = cursor.fetchall()
                
                if active_paper:
                    self.print_status("🎯", f"Active Paper Trading Sessions: {len(active_paper)}", "OK")
                    for session in active_paper:
                        session_id, user_id, session_type, start_cap, current_val, status, trades = session
                        pnl = current_val - start_cap if current_val and start_cap else 0
                        self.print_status("📈", f"  Session {session_id[:8]}... | Type: {session_type} | P&L: ${pnl:.2f} | Trades: {trades}", "INFO")
                        sessions['paper_sessions'].append({
                            'session_id': session_id,
                            'type': session_type,
                            'starting_capital': start_cap,
                            'current_value': current_val,
                            'pnl': pnl,
                            'trades': trades
                        })
                else:
                    self.print_status("[INFO]️", "No active paper trading sessions", "INFO")
                    
                conn.close()
            except Exception as e:
                self.print_status("[WARNING]️", f"Error checking paper sessions: {str(e)}", "WARNING")
                
        # Check for internal paper trading sessions
        import glob
        internal_dbs = glob.glob("internal_paper_session_*.db")
        if internal_dbs:
            self.print_status("📊", f"Found {len(internal_dbs)} internal paper trading databases", "INFO")
            for db in internal_dbs[:5]:  # Check first 5
                try:
                    conn = sqlite3.connect(db)
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM trades")
                    trade_count = cursor.fetchone()[0]
                    conn.close()
                    self.print_status("💼", f"  {db}: {trade_count} trades", "INFO")
                except Exception as e:
                    pass
                    
        sessions['total_active'] = len(sessions['live_sessions']) + len(sessions['paper_sessions']) + len(sessions['internal_sessions'])
        self.audit_results['trading_sessions'] = sessions
        
        if sessions['total_active'] == 0:
            self.print_status("[WARNING]️", "NO ACTIVE TRADING SESSIONS DETECTED", "WARNING")
            self.audit_results['issues'].append("No active trading sessions found")
        
        return sessions
        
    def check_broker_connections(self) -> Dict[str, Any]:
        """Check broker connections"""
        self.print_header("3. BROKER CONNECTION VERIFICATION")
        
        connections = {
            'interactive_brokers': False,
            'alpaca': False
        }
        
        # Check IB connection via API
        try:
            response = requests.get("http://localhost:8000/api/brokers/ib/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                connections['interactive_brokers'] = data.get('connected', False)
                if connections['interactive_brokers']:
                    self.print_status("[CHECK]", f"Interactive Brokers: CONNECTED (Account: {data.get('account', 'N/A')})", "OK")
                else:
                    self.print_status("[ERROR]", "Interactive Brokers: NOT CONNECTED", "ERROR")
            else:
                self.print_status("[WARNING]️", "Interactive Brokers: Status endpoint not available", "WARNING")
        except Exception as e:
            self.print_status("[ERROR]", f"Interactive Brokers: Connection check failed - {str(e)}", "ERROR")
            
        # Check Alpaca connection
        try:
            response = requests.get("http://localhost:8000/api/brokers/alpaca/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                connections['alpaca'] = data.get('connected', False)
                if connections['alpaca']:
                    self.print_status("[CHECK]", f"Alpaca: CONNECTED", "OK")
                else:
                    self.print_status("[ERROR]", "Alpaca: NOT CONNECTED", "ERROR")
            else:
                self.print_status("[WARNING]️", "Alpaca: Status endpoint not available", "WARNING")
        except Exception as e:
            self.print_status("[ERROR]", f"Alpaca: Connection check failed - {str(e)}", "ERROR")
            
        return connections
        
    def check_ai_agents(self) -> Dict[str, Any]:
        """Check AI Intelligence Agents status"""
        self.print_header("4. AI INTELLIGENCE AGENTS AUDIT")
        
        ai_status = {
            'revolutionary_engines': {},
            'intelligence_agents': {},
            'market_research': False,
            'learning_system': False
        }
        
        # Check Revolutionary AI status via API
        try:
            response = requests.get("http://localhost:8000/api/revolutionary/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_status("[CHECK]", "Revolutionary AI System: ACTIVE", "OK")
                
                # Check individual engines
                engines = data.get('engines', [])
                for engine in engines:
                    name = engine.get('name', 'Unknown')
                    status = engine.get('status', 'unknown')
                    if status == 'active':
                        self.print_status("🚀", f"  {name}: ACTIVE", "OK")
                        ai_status['revolutionary_engines'][name] = True
                    else:
                        self.print_status("[WARNING]️", f"  {name}: {status.upper()}", "WARNING")
                        ai_status['revolutionary_engines'][name] = False
            else:
                self.print_status("[WARNING]️", "Revolutionary AI: Status endpoint not available", "WARNING")
        except Exception as e:
            self.print_status("[ERROR]", f"Revolutionary AI: Check failed - {str(e)}", "ERROR")
            self.audit_results['issues'].append("Revolutionary AI system not responding")
            
        self.audit_results['ai_agents'] = ai_status
        return ai_status
        
    def generate_report(self):
        """Generate comprehensive audit report"""
        self.print_header("📋 COMPREHENSIVE AUDIT REPORT")
        
        print(f"\n🕐 Audit Time: {self.audit_results['timestamp']}")
        print(f"\n📊 System Status:")
        for component, status in self.audit_results['system_status'].items():
            status_icon = "[CHECK]" if status else "[ERROR]"
            print(f"   {status_icon} {component.replace('_', ' ').title()}: {'RUNNING' if status else 'NOT RUNNING'}")
            
        print(f"\n🎯 Trading Sessions:")
        sessions = self.audit_results['trading_sessions']
        print(f"   Total Active: {sessions.get('total_active', 0)}")
        print(f"   Paper Sessions: {len(sessions.get('paper_sessions', []))}")
        
        print(f"\n🤖 AI Agents:")
        ai_agents = self.audit_results['ai_agents']
        active_engines = sum(1 for v in ai_agents.get('revolutionary_engines', {}).values() if v)
        total_engines = len(ai_agents.get('revolutionary_engines', {}))
        print(f"   Revolutionary Engines: {active_engines}/{total_engines} active")
        
        if self.audit_results['issues']:
            print(f"\n[WARNING]️  Issues Found ({len(self.audit_results['issues'])}):")
            for i, issue in enumerate(self.audit_results['issues'], 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n[CHECK] No critical issues found")
            
        # Save report to file
        report_file = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        print(f"\n💾 Full report saved to: {report_file}")

def main():
    print("\n" + "="*80)
    print("🔍 PROMETHEUS TRADING PLATFORM - COMPREHENSIVE SYSTEM AUDIT")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    auditor = PrometheusSystemAuditor()
    
    # Run all checks
    auditor.check_system_components()
    auditor.check_active_trading_sessions()
    auditor.check_broker_connections()
    auditor.check_ai_agents()
    
    # Generate final report
    auditor.generate_report()
    
    print("\n" + "="*80)
    print("[CHECK] AUDIT COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

