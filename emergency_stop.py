#!/usr/bin/env python3
'''
🚨 PROMETHEUS EMERGENCY STOP
Immediately halt all trading activity
'''

import requests
import subprocess
import sys

def emergency_stop():
    print("🚨 PROMETHEUS EMERGENCY STOP ACTIVATED")
    print("=" * 50)
    
    try:
        # 1. Stop the main server
        print("1. Stopping main server...")
        subprocess.run(['pkill', '-f', 'launch_prometheus.py'], check=False)
        subprocess.run(['pkill', '-f', 'unified_production_server'], check=False)
        
        # 2. Try to cancel all open orders via API
        print("2. Attempting to cancel all open orders...")
        try:
            response = requests.post("http://localhost:8000/api/emergency/cancel_all_orders", timeout=10)
            if response.status_code == 200:
                print("[CHECK] All orders cancelled successfully")
            else:
                print("[WARNING]️ Could not cancel orders via API")
        except:
            print("[WARNING]️ Could not reach API to cancel orders")
        
        # 3. Log emergency stop
        print("3. Logging emergency stop...")
        with open('emergency_stop.log', 'a') as f:
            from datetime import datetime
            f.write(f"{datetime.now()}: Emergency stop activated\n")
        
        print("[CHECK] Emergency stop completed")
        print("📞 Contact your broker if needed to manually close positions")
        
    except Exception as e:
        print(f"[ERROR] Emergency stop error: {e}")
        print("📞 IMMEDIATELY contact your broker to halt trading!")

if __name__ == "__main__":
    emergency_stop()
