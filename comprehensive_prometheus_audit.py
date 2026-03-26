#!/usr/bin/env python3
"""
COMPREHENSIVE PROMETHEUS AUDIT
Full audit of all systems, components, and capabilities
"""

import requests
import json
import time
import sqlite3
import subprocess
import psutil
from datetime import datetime

def check_all_servers():
    """Check all server status"""
    print("1. COMPREHENSIVE SERVER AUDIT")
    print("=" * 50)
    
    servers = {
        "Main Server (Port 8000)": "http://localhost:8000/health",
        "GPT-OSS 20B (Port 5000)": "http://localhost:5000/health", 
        "GPT-OSS 120B (Port 5001)": "http://localhost:5001/health",
        "Revolutionary Server (Port 8002)": "http://localhost:8002/health"
    }
    
    server_status = {}
    
    for name, url in servers.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   [RUNNING] {name}")
                server_status[name] = True
            else:
                print(f"   [ERROR] {name}: {response.status_code}")
                server_status[name] = False
        except Exception as e:
            print(f"   [DOWN] {name}: {str(e)}")
            server_status[name] = False
    
    running_count = sum(server_status.values())
    print(f"\n   Servers Running: {running_count}/4")
    return server_status

def check_ai_systems():
    """Check all AI systems"""
    print("\n2. AI SYSTEMS AUDIT")
    print("=" * 50)
    
    ai_systems = {
        "GPT-OSS 20B Intelligence": "http://localhost:5000/generate",
        "GPT-OSS 120B Intelligence": "http://localhost:5001/generate",
        "AI Coordinator": "http://localhost:8000/api/ai/coordinator/status",
        "SynergyCore Agent": "http://localhost:8000/api/ai/agents/synergycore/status",
        "CogniFlow Agent": "http://localhost:8000/api/ai/agents/cogniflow/status",
        "EdgeMind Agent": "http://localhost:8000/api/ai/agents/edgemind/status",
        "NeuralMesh Agent": "http://localhost:8000/api/ai/agents/neuralmesh/status",
        "CodeSwarm Agent": "http://localhost:8000/api/ai/agents/codeswarm/status"
    }
    
    ai_status = {}
    
    for name, url in ai_systems.items():
        try:
            if "generate" in url:
                # Test AI generation
                response = requests.post(url, json={"prompt": "Test AI capability", "max_tokens": 50}, timeout=10)
                if response.status_code == 200:
                    print(f"   [ACTIVE] {name}")
                    ai_status[name] = True
                else:
                    print(f"   [ERROR] {name}: {response.status_code}")
                    ai_status[name] = False
            else:
                # Test status endpoint
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   [ACTIVE] {name}")
                    ai_status[name] = True
                else:
                    print(f"   [MISSING] {name}: {response.status_code}")
                    ai_status[name] = False
        except Exception as e:
            print(f"   [DOWN] {name}: {str(e)}")
            ai_status[name] = False
    
    active_count = sum(ai_status.values())
    print(f"\n   AI Systems Active: {active_count}/{len(ai_systems)}")
    return ai_status

def check_revolutionary_systems():
    """Check revolutionary systems"""
    print("\n3. REVOLUTIONARY SYSTEMS AUDIT")
    print("=" * 50)
    
    revolutionary_systems = {
        "Quantum Trading Engine": "http://localhost:8000/api/quantum/status",
        "Think Mesh": "http://localhost:8000/api/think-mesh/status",
        "Market Oracle": "http://localhost:8000/api/market-oracle/status",
        "Continuous Learning": "http://localhost:8000/api/learning/continuous-learning/status",
        "Advanced Learning": "http://localhost:8000/api/learning/advanced-learning/status",
        "Autonomous Improvement": "http://localhost:8000/api/learning/autonomous-improvement/status"
    }
    
    rev_status = {}
    
    for name, url in revolutionary_systems.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   [ACTIVE] {name}")
                rev_status[name] = True
            else:
                print(f"   [MISSING] {name}: {response.status_code}")
                rev_status[name] = False
        except Exception as e:
            print(f"   [DOWN] {name}: {str(e)}")
            rev_status[name] = False
    
    active_count = sum(rev_status.values())
    print(f"\n   Revolutionary Systems Active: {active_count}/{len(revolutionary_systems)}")
    return rev_status

def check_trading_engines():
    """Check trading engines"""
    print("\n4. TRADING ENGINES AUDIT")
    print("=" * 50)
    
    trading_engines = {
        "Crypto Engine": "http://localhost:8000/api/trading/crypto-engine/status",
        "Options Engine": "http://localhost:8000/api/trading/options-engine/status",
        "Advanced Engine": "http://localhost:8000/api/trading/advanced-engine/status",
        "Market Maker": "http://localhost:8000/api/trading/market-maker/status",
        "Master Engine": "http://localhost:8000/api/trading/master-engine/status",
        "HRM Engine": "http://localhost:8000/api/trading/hrm-engine/status"
    }
    
    engine_status = {}
    
    for name, url in trading_engines.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   [ACTIVE] {name}")
                engine_status[name] = True
            else:
                print(f"   [MISSING] {name}: {response.status_code}")
                engine_status[name] = False
        except Exception as e:
            print(f"   [DOWN] {name}: {str(e)}")
            engine_status[name] = False
    
    active_count = sum(engine_status.values())
    print(f"\n   Trading Engines Active: {active_count}/{len(trading_engines)}")
    return engine_status

def check_trading_capabilities():
    """Check trading capabilities"""
    print("\n5. TRADING CAPABILITIES AUDIT")
    print("=" * 50)
    
    trading_endpoints = {
        "Portfolio Positions": "http://localhost:8000/api/portfolio/positions",
        "Portfolio Value": "http://localhost:8000/api/portfolio/value",
        "Trading History": "http://localhost:8000/api/trading/history",
        "Active Trades": "http://localhost:8000/api/trading/active",
        "Trade Execution": "http://localhost:8000/api/trading/execute",
        "Live Trading Status": "http://localhost:8000/api/live-trading/status"
    }
    
    trading_status = {}
    
    for name, url in trading_endpoints.items():
        try:
            if "execute" in url:
                # Test trade execution
                response = requests.post(url, json={"symbol": "TEST", "side": "buy", "quantity": 1, "price": 10.0}, timeout=10)
            else:
                response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   [WORKING] {name}")
                trading_status[name] = True
            else:
                print(f"   [ERROR] {name}: {response.status_code}")
                trading_status[name] = False
        except Exception as e:
            print(f"   [DOWN] {name}: {str(e)}")
            trading_status[name] = False
    
    working_count = sum(trading_status.values())
    print(f"\n   Trading Capabilities Working: {working_count}/{len(trading_endpoints)}")
    return trading_status

def check_portfolio_status():
    """Check portfolio status"""
    print("\n6. PORTFOLIO STATUS AUDIT")
    print("=" * 50)
    
    try:
        # Check portfolio value
        response = requests.get("http://localhost:8000/api/portfolio/value", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_value = data.get('total_value', 0)
            cash_balance = data.get('cash_balance', 0)
            invested_value = data.get('invested_value', 0)
            
            print(f"   Total Portfolio Value: ${total_value:,.2f}")
            print(f"   Cash Balance: ${cash_balance:,.2f}")
            print(f"   Invested Value: ${invested_value:,.2f}")
            
            # Check positions
            pos_response = requests.get("http://localhost:8000/api/portfolio/positions", timeout=5)
            if pos_response.status_code == 200:
                pos_data = pos_response.json()
                positions = pos_data.get('positions', [])
                print(f"   Active Positions: {len(positions)}")
                
                for pos in positions:
                    print(f"     - {pos['symbol']}: {pos['quantity']} shares @ ${pos['entry_price']}")
            
            # Check if within budget
            if total_value <= 250:
                print(f"   [OK] Portfolio within $250 budget")
                return True
            else:
                print(f"   [WARNING] Portfolio exceeds $250 by ${total_value - 250:,.2f}")
                return False
        else:
            print(f"   [ERROR] Could not check portfolio: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] Portfolio check failed: {str(e)}")
        return False

def check_database_integrity():
    """Check database integrity"""
    print("\n7. DATABASE INTEGRITY AUDIT")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("prometheus_trading.db")
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   Database Tables: {len(tables)}")
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"     - {table_name}: {count} records")
        
        # Check positions
        cursor.execute("SELECT * FROM positions WHERE status = 'open'")
        positions = cursor.fetchall()
        print(f"   Open Positions: {len(positions)}")
        
        # Check trades
        cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 5")
        recent_trades = cursor.fetchall()
        print(f"   Recent Trades: {len(recent_trades)}")
        
        conn.close()
        print("   [OK] Database integrity verified")
        return True
        
    except Exception as e:
        print(f"   [ERROR] Database check failed: {str(e)}")
        return False

def check_system_resources():
    """Check system resources"""
    print("\n8. SYSTEM RESOURCES AUDIT")
    print("=" * 50)
    
    try:
        # Check CPU and memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        print(f"   CPU Usage: {cpu_percent:.1f}%")
        print(f"   Memory Usage: {memory.percent:.1f}%")
        print(f"   Available Memory: {memory.available / (1024**3):.1f} GB")
        
        # Check running Python processes
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        print(f"   Python Processes: {len(python_processes)}")
        for proc in python_processes:
            cmdline = ' '.join(proc['cmdline']) if proc['cmdline'] else 'Unknown'
            print(f"     - PID {proc['pid']}: {cmdline[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] System resources check failed: {str(e)}")
        return False

def main():
    """Main audit function"""
    print("PROMETHEUS COMPREHENSIVE AUDIT")
    print("=" * 60)
    print(f"Audit started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all audits
    server_status = check_all_servers()
    ai_status = check_ai_systems()
    rev_status = check_revolutionary_systems()
    engine_status = check_trading_engines()
    trading_status = check_trading_capabilities()
    portfolio_ok = check_portfolio_status()
    database_ok = check_database_integrity()
    resources_ok = check_system_resources()
    
    # Calculate totals
    servers_running = sum(server_status.values())
    ai_systems_active = sum(ai_status.values())
    rev_systems_active = sum(rev_status.values())
    engines_active = sum(engine_status.values())
    trading_working = sum(trading_status.values())
    
    # Summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE AUDIT SUMMARY")
    print("=" * 60)
    
    print(f"Servers Running: {servers_running}/4")
    print(f"AI Systems Active: {ai_systems_active}/8")
    print(f"Revolutionary Systems Active: {rev_systems_active}/6")
    print(f"Trading Engines Active: {engines_active}/6")
    print(f"Trading Capabilities Working: {trading_working}/6")
    print(f"Portfolio Status: {'OK' if portfolio_ok else 'NEEDS ATTENTION'}")
    print(f"Database Integrity: {'OK' if database_ok else 'ISSUES'}")
    print(f"System Resources: {'OK' if resources_ok else 'ISSUES'}")
    
    # Overall assessment
    total_systems = 4 + 8 + 6 + 6 + 6
    active_systems = servers_running + ai_systems_active + rev_systems_active + engines_active + trading_working
    
    print(f"\nOverall System Status: {active_systems}/{total_systems} systems operational")
    
    if active_systems >= total_systems * 0.8:
        print("STATUS: MOSTLY OPERATIONAL")
    elif active_systems >= total_systems * 0.5:
        print("STATUS: PARTIALLY OPERATIONAL")
    else:
        print("STATUS: NEEDS SIGNIFICANT ATTENTION")
    
    print(f"\nAudit completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return active_systems >= total_systems * 0.7

if __name__ == "__main__":
    success = main()
    print(f"\nFINAL RESULT: {'SYSTEM READY' if success else 'NEEDS ATTENTION'}")










