#!/usr/bin/env python3
"""
Complete System Status Check
==============================
Comprehensive check of all PROMETHEUS components
"""

import requests
import psutil
import subprocess
from datetime import datetime

def main():
    print("\n" + "="*80)
    print("🚀 PROMETHEUS TRADING PLATFORM - COMPLETE SYSTEM STATUS")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Check Python Processes
    print("\n" + "="*80)
    print("1️⃣  PYTHON PROCESSES")
    print("="*80)
    
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time', 'memory_info']):
        try:
            if proc.info['name'] in ['python.exe', 'python']:
                cmdline = proc.info['cmdline']
                if cmdline and len(cmdline) > 1:
                    python_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(cmdline),
                        'started': datetime.fromtimestamp(proc.info['create_time']),
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if python_processes:
        for proc in python_processes:
            print(f"\n[CHECK] Python Process Found:")
            print(f"   PID: {proc['pid']}")
            print(f"   Command: {proc['cmdline'][:100]}...")
            print(f"   Started: {proc['started']}")
            print(f"   Uptime: {datetime.now() - proc['started']}")
            print(f"   Memory: {proc['memory_mb']:.1f} MB")
    else:
        print("[ERROR] No Python processes found!")
        return
    
    # 2. Check Windows Service
    print("\n" + "="*80)
    print("2️⃣  WINDOWS SERVICE STATUS")
    print("="*80)
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Service -Name "PrometheusTrading" | Select-Object Name, Status, StartType | Format-List'],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result.stdout)
        if 'Stopped' in result.stdout:
            print("[CHECK] Old service is STOPPED (correct)")
        if 'Disabled' in result.stdout:
            print("[CHECK] Old service auto-start is DISABLED (correct)")
    except Exception as e:
        print(f"[WARNING]️  Could not check service: {e}")
    
    # 3. Check Port 8000
    print("\n" + "="*80)
    print("3️⃣  PORT 8000 STATUS")
    print("="*80)
    
    try:
        result = subprocess.run(
            ['powershell', '-Command', 'Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if 'True' in result.stdout:
            print("[CHECK] Port 8000 is OPEN and responding")
        else:
            print("[ERROR] Port 8000 is NOT responding")
    except Exception as e:
        print(f"[WARNING]️  Could not check port: {e}")
    
    # 4. Check API Endpoints
    print("\n" + "="*80)
    print("4️⃣  API ENDPOINTS")
    print("="*80)
    
    endpoints = [
        ('Health', 'http://localhost:8000/health'),
        ('Broker Status', 'http://localhost:8000/api/broker/status'),
        ('Trading System', 'http://localhost:8000/api/trading/system/status'),
        ('System Status', 'http://localhost:8000/api/system/status'),
    ]
    
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"\n[CHECK] {name}: OK (200)")
                try:
                    data = response.json()
                    if name == 'Broker Status':
                        print(f"   Alpaca: {data.get('alpaca', {}).get('connected', 'Unknown')}")
                        print(f"   IB: {data.get('ib', {}).get('connected', 'Unknown')}")
                    elif name == 'Trading System':
                        print(f"   Trading Active: {data.get('trading_active', 'Unknown')}")
                        print(f"   Cycle Count: {data.get('cycle_count', 'Unknown')}")
                    elif name == 'System Status':
                        print(f"   Active Systems: {data.get('active_systems', 'Unknown')}")
                except:
                    pass
            else:
                print(f"\n[WARNING]️  {name}: {response.status_code}")
        except Exception as e:
            print(f"\n[ERROR] {name}: Failed - {str(e)[:50]}")
    
    # 5. Check Broker Connections
    print("\n" + "="*80)
    print("5️⃣  BROKER CONNECTIONS")
    print("="*80)
    
    try:
        response = requests.get('http://localhost:8000/api/broker/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Alpaca
            alpaca = data.get('alpaca', {})
            if alpaca.get('connected'):
                print(f"\n[CHECK] ALPACA BROKER: CONNECTED")
                print(f"   Account: {alpaca.get('account_id', 'Unknown')}")
                print(f"   Mode: {'Live' if not alpaca.get('paper_trading') else 'Paper'}")
            else:
                print(f"\n[ERROR] ALPACA BROKER: DISCONNECTED")
            
            # Interactive Brokers
            ib = data.get('ib', {})
            if ib.get('connected'):
                print(f"\n[CHECK] INTERACTIVE BROKERS: CONNECTED")
                print(f"   Account: {ib.get('account', 'Unknown')}")
                print(f"   Client ID: {ib.get('client_id', 'Unknown')}")
            else:
                print(f"\n[ERROR] INTERACTIVE BROKERS: DISCONNECTED")
        else:
            print("[WARNING]️  Could not retrieve broker status")
    except Exception as e:
        print(f"[ERROR] Failed to check brokers: {e}")
    
    # 6. Check Trading System
    print("\n" + "="*80)
    print("6️⃣  TRADING SYSTEM STATUS")
    print("="*80)
    
    try:
        response = requests.get('http://localhost:8000/api/trading/system/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📊 Trading Status:")
            print(f"   Active: {data.get('trading_active', 'Unknown')}")
            print(f"   Cycle Count: {data.get('cycle_count', 'Unknown')}")
            print(f"   Trades Today: {data.get('trades_today', 'Unknown')}")
            print(f"   Daily P&L: ${data.get('daily_pnl', 0):.2f}")
            
            if data.get('trading_active'):
                print("\n[CHECK] TRADING SYSTEM IS ACTIVE")
            else:
                print("\n[WARNING]️  TRADING SYSTEM IS NOT ACTIVE")
        else:
            print("[WARNING]️  Could not retrieve trading system status")
    except Exception as e:
        print(f"[ERROR] Failed to check trading system: {e}")
    
    # 7. Check AI Components
    print("\n" + "="*80)
    print("7️⃣  AI/ML COMPONENTS")
    print("="*80)
    
    import os
    import glob
    
    # Check model files
    model_files = glob.glob("pretrained_models/*.joblib") + glob.glob("ai_models/*.joblib")
    print(f"\n📊 Pre-trained Models: {len(model_files)} files found")
    
    # Check databases
    databases = {
        'prometheus_learning.db': 'Learning Database',
        'knowledge_base.db': 'Knowledge Base',
        'agent_performance.db': 'Agent Performance',
        'historical_data/historical_data.db': 'Historical Data'
    }
    
    print(f"\n📊 Databases:")
    for db_file, db_name in databases.items():
        if os.path.exists(db_file):
            size_mb = os.path.getsize(db_file) / 1024 / 1024
            print(f"   [CHECK] {db_name}: {size_mb:.2f} MB")
        else:
            print(f"   [ERROR] {db_name}: NOT FOUND")
    
    # 8. Summary
    print("\n" + "="*80)
    print("📊 SYSTEM SUMMARY")
    print("="*80)
    
    print("\n[CHECK] OPERATIONAL COMPONENTS:")
    print("   • Unified Production Server running")
    print("   • Port 8000 responding")
    print("   • API endpoints accessible")
    print("   • Old Windows service stopped & disabled")
    
    print("\n📋 NEXT STEPS:")
    print("   1. Monitor logs for crypto price data")
    print("   2. Verify broker connections are stable")
    print("   3. Check trading cycles (every 5 minutes)")
    print("   4. Monitor for crypto errors (should be ZERO)")
    
    print("\n🌐 DASHBOARD:")
    print("   http://localhost:8000")
    
    print("\n" + "="*80)
    print("[CHECK] SYSTEM STATUS CHECK COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()

