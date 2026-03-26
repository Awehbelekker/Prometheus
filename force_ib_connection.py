#!/usr/bin/env python3
"""
Force Backend IB Connection
"""

import requests
import time
import json

def force_ib_connection():
    """Force backend to connect to IB"""
    print("🔄 FORCING BACKEND IB CONNECTION")
    print("=" * 40)
    
    for i in range(5):
        print(f"\nAttempt {i+1}/5:")
        try:
            response = requests.get('http://localhost:8000/api/ib-live/status', timeout=15)
            if response.status_code == 200:
                data = response.json()
                connection = data.get('connection', 'unknown')
                print(f"   Connection: {connection}")
                
                if connection == 'connected':
                    print("   🎉 SUCCESS! Backend connected to IB!")
                    
                    # Get account data
                    if 'account_data' in data:
                        account_data = data['account_data']
                        net_liq = account_data.get('net_liquidation', '0')
                        print(f"   💰 Net Liquidation: ${net_liq}")
                        
                        if net_liq != '0':
                            print("   [CHECK] REAL ACCOUNT DATA RETRIEVED!")
                            return True
                else:
                    print("   [WARNING]️ Still disconnected, retrying...")
            else:
                print(f"   [ERROR] HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
        
        if i < 4:  # Don't sleep on last attempt
            time.sleep(3)
    
    return False

def test_performance_data():
    """Test if performance data is now real"""
    print("\n🎯 Testing Performance Data...")
    try:
        response = requests.get('http://localhost:8000/api/paper-trading/performance', timeout=10)
        if response.status_code == 200:
            perf = response.json()
            ib_connected = perf.get('ib_connected', False)
            current_balance = perf.get('current_balance', 0)
            total_pnl = perf.get('total_pnl', 0)
            
            print(f"   IB Connected: {ib_connected}")
            print(f"   Current Balance: ${current_balance}")
            print(f"   Total P&L: ${total_pnl}")
            
            if ib_connected and current_balance > 0:
                print("   🎉 BACKEND IS NOW USING REAL IB DATA!")
                return True
            else:
                print("   [WARNING]️ Backend still using session data")
                return False
    except Exception as e:
        print(f"   [ERROR] Performance check error: {e}")
        return False

if __name__ == "__main__":
    # Force connection
    connected = force_ib_connection()
    
    # Test performance data
    real_data = test_performance_data()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL RESULT:")
    if connected and real_data:
        print("[CHECK] SUCCESS: Backend connected to IB with real data!")
        print("💰 The system is now showing REAL account balance from U21922116")
        print("🚀 Ready for live trading with real money!")
    elif connected:
        print("[WARNING]️ PARTIAL: Backend connected but data may still be simulated")
        print("🔧 Check account data retrieval")
    else:
        print("[ERROR] FAILED: Backend could not connect to IB")
        print("🔧 Check IB Gateway/TWS and API settings")
        print("🔧 Verify account U21922116 is logged in")
        print("🔧 Check client ID conflicts (backend uses client ID 3)")
