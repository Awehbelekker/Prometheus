#!/usr/bin/env python3
"""
PROMETHEUS Master Startup Script
Starts all systems in the correct order
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def main():
    print("="*80)
    print("PROMETHEUS MASTER STARTUP")
    print("="*80)
    
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Start backend server
    print("\n[1/2] Starting backend server...")
    backend_script = script_dir / 'start_backend_permanent.py'
    if backend_script.exists():
        if os.name == 'nt':  # Windows
            subprocess.Popen([sys.executable, str(backend_script)],
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen([sys.executable, str(backend_script)])
        print("✅ Backend server startup initiated")
        time.sleep(5)
    else:
        print("⚠️ Backend startup script not found")
    
    # Step 2: Verify main trading system is running
    print("\n[2/2] Checking main trading system...")
    print("Note: Main trading system should be started separately with:")
    print("  python launch_ultimate_prometheus_LIVE_TRADING.py")
    
    print("\n" + "="*80)
    print("STARTUP COMPLETE")
    print("="*80)
    print("\nBackend server should be starting...")
    print("Check http://127.0.0.1:8000/health to verify")

if __name__ == "__main__":
    main()
