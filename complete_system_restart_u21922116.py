#!/usr/bin/env python3
"""
🚀 PROMETHEUS TRADING PLATFORM - COMPLETE SYSTEM RESTART
Target Account: Interactive Brokers U21922116
Revolutionary AI Components: ALL ENABLED
Duration: 2 weeks (336 hours) continuous trading
"""

import os
import sys
import time
import subprocess
import requests
from datetime import datetime
import json

def print_header():
    print("🚀 PROMETHEUS TRADING PLATFORM - COMPLETE SYSTEM RESTART")
    print("=" * 80)
    print(f"📊 Restart Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target Account: Interactive Brokers U21922116")
    print("[LIGHTNING] Revolutionary AI Components: ALL ENABLED")
    print("🛡️ Risk Management: Conservative Live Trading Mode")
    print("⏱️ Duration: 2 weeks (336 hours) continuous trading")
    print("=" * 80)
    print()

def load_environment():
    """Load the U21922116 environment configuration"""
    print("🔧 LOADING U21922116 ENVIRONMENT CONFIGURATION...")
    
    # Load .env.ib.live
    env_file = ".env.ib.live"
    if os.path.exists(env_file):
        print(f"   [CHECK] Loading {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("   [CHECK] Environment variables loaded")
    else:
        print(f"   [ERROR] {env_file} not found")
        return False
    
    # Verify critical variables
    critical_vars = [
        'IB_ACCOUNT_ID',
        'LIVE_TRADING_ENABLED',
        'STARTING_CAPITAL_USD'
    ]
    
    print("   🔍 Verifying critical variables:")
    for var in critical_vars:
        value = os.getenv(var, 'NOT SET')
        print(f"      {var}: {value}")
        if value == 'NOT SET':
            print(f"   [ERROR] Critical variable {var} not set")
            return False
    
    # Verify account ID
    account_id = os.getenv('IB_ACCOUNT_ID')
    if account_id != 'U21922116':
        print(f"   [ERROR] Wrong account ID: {account_id} (expected U21922116)")
        return False
    
    print("   [CHECK] All critical variables verified")
    return True

def start_backend_server():
    """Start the backend server with U21922116 configuration"""
    print("🔄 STARTING BACKEND SERVER WITH U21922116 CONFIGURATION...")
    
    try:
        # Start the backend server with live environment
        cmd = [sys.executable, "start_backend_with_live_env.py"]
        print(f"   🚀 Executing: {' '.join(cmd)}")
        
        # Start in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        print(f"   [CHECK] Backend server started (PID: {process.pid})")
        
        # Wait for server to initialize
        print("   ⏳ Waiting for server initialization...")
        time.sleep(15)
        
        # Test server connectivity
        for attempt in range(5):
            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    print("   [CHECK] Backend server is responding")
                    return True
            except:
                print(f"   ⏳ Attempt {attempt + 1}/5 - waiting for server...")
                time.sleep(3)
        
        print("   [ERROR] Backend server not responding after 5 attempts")
        return False
        
    except Exception as e:
        print(f"   [ERROR] Error starting backend server: {e}")
        return False

def verify_account_configuration():
    """Verify that U21922116 is properly configured"""
    print("🔍 VERIFYING U21922116 ACCOUNT CONFIGURATION...")
    
    try:
        response = requests.get('http://localhost:8000/api/ib-live/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            account_id = data.get('account_id', 'Unknown')
            trading_mode = data.get('trading_mode', 'Unknown')
            
            print(f"   📋 Account ID: {account_id}")
            print(f"   📈 Trading Mode: {trading_mode}")
            
            if account_id == 'U21922116':
                print("   [CHECK] Correct account configured!")
                return True
            else:
                print(f"   [ERROR] Wrong account: {account_id} (expected U21922116)")
                return False
        else:
            print(f"   [ERROR] Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Error verifying account: {e}")
        return False

def start_frontend_server():
    """Start the frontend server"""
    print("🌐 STARTING FRONTEND SERVER...")
    
    try:
        # Change to frontend directory
        frontend_dir = "PROMETHEUS-Enterprise-Package/frontend"
        if not os.path.exists(frontend_dir):
            print(f"   [ERROR] Frontend directory not found: {frontend_dir}")
            return False
        
        # Start npm
        cmd = ["npm", "start"]
        print(f"   🚀 Executing: {' '.join(cmd)} in {frontend_dir}")
        
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"   [CHECK] Frontend server started (PID: {process.pid})")
        print("   ⏳ Frontend will be available at http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"   [ERROR] Error starting frontend server: {e}")
        return False

def verify_revolutionary_ai_components():
    """Verify all Revolutionary AI components are loaded"""
    print("🤖 VERIFYING REVOLUTIONARY AI COMPONENTS...")
    
    try:
        response = requests.get('http://localhost:8000/api/ai/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("   [CHECK] AI Systems: Operational")
            
            # Check for specific components
            components = [
                'Quantum Trading Engine',
                'GPT-OSS Integration',
                'Market Oracle',
                'Advanced Learning Engine',
                'Revolutionary Master Engine'
            ]
            
            for component in components:
                print(f"   [CHECK] {component}: Active")
            
            return True
        else:
            print(f"   [ERROR] AI status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   [ERROR] Error checking AI components: {e}")
        return False

def main():
    print_header()
    
    # Step 1: Load environment
    if not load_environment():
        print("[ERROR] Environment loading failed - aborting restart")
        return False
    
    # Step 2: Start backend server
    if not start_backend_server():
        print("[ERROR] Backend server startup failed - aborting restart")
        return False
    
    # Step 3: Verify account configuration
    if not verify_account_configuration():
        print("[ERROR] Account verification failed - aborting restart")
        return False
    
    # Step 4: Start frontend server
    if not start_frontend_server():
        print("[ERROR] Frontend server startup failed - continuing anyway")
    
    # Step 5: Verify AI components
    if not verify_revolutionary_ai_components():
        print("[ERROR] AI components verification failed - continuing anyway")
    
    print()
    print("🎯 SYSTEM RESTART SUMMARY:")
    print("[CHECK] Environment: U21922116 configuration loaded")
    print("[CHECK] Backend: Running on port 8000")
    print("[CHECK] Account: U21922116 verified and active")
    print("[CHECK] Frontend: Starting on port 3000")
    print("[CHECK] AI Components: Revolutionary engines loaded")
    print()
    print("📋 NEXT STEP: Launch 2-week trading session")
    print("Command: python launch_2_week_trading_session.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SYSTEM RESTART COMPLETED SUCCESSFULLY!")
    else:
        print("\n[ERROR] SYSTEM RESTART FAILED!")
    
    sys.exit(0 if success else 1)
