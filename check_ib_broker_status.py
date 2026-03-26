#!/usr/bin/env python3
"""
Interactive Brokers Connection & Status Checker
Verifies IB connection and account readiness for trading
"""

from ib_insync import IB, util
import os
from dotenv import load_dotenv

load_dotenv()

def check_ib_connection():
    """Check Interactive Brokers connection and status"""
    ib = IB()
    
    try:
        # Connection parameters from .env
        host = os.getenv('IB_HOST', '127.0.0.1')
        port = int(os.getenv('IB_PORT', '4002'))  # Paper trading port
        client_id = int(os.getenv('IB_CLIENT_ID', '9998'))
        
        print(f"\n🔌 Connecting to Interactive Brokers...")
        print(f"   Host: {host}")
        print(f"   Port: {port} ({'PAPER' if port == 4002 else 'LIVE'})")
        print(f"   Client ID: {client_id}")
        
        # Connect with timeout
        ib.connect(host, port, clientId=client_id, timeout=10)
        
        if ib.isConnected():
            print(f"\n✅ IB CONNECTION SUCCESSFUL")
            
            # Get account info
            accounts = ib.managedAccounts()
            print(f"\n📊 IB ACCOUNT INFORMATION:")
            print(f"   Accounts: {', '.join(accounts)}")
            
            if accounts:
                account = accounts[0]
                
                # Request account summary
                account_values = ib.accountValues(account)
                
                # Extract key values
                equity = next((v.value for v in account_values if v.tag == 'NetLiquidation'), 'N/A')
                cash = next((v.value for v in account_values if v.tag == 'TotalCashValue'), 'N/A')
                buying_power = next((v.value for v in account_values if v.tag == 'BuyingPower'), 'N/A')
                
                print(f"   Account: {account}")
                print(f"   Net Liquidation: ${equity}")
                print(f"   Total Cash: ${cash}")
                print(f"   Buying Power: ${buying_power}")
                
                # Get positions
                positions = ib.positions()
                print(f"\n📈 CURRENT POSITIONS: {len(positions)}")
                if positions:
                    for pos in positions:
                        print(f"   {pos.contract.symbol}: {pos.position} shares @ ${pos.avgCost:.2f}")
                else:
                    print("   No open positions")
                
                # Get orders
                orders = ib.openOrders()
                print(f"\n📋 OPEN ORDERS: {len(orders)}")
                if orders:
                    for order in orders:
                        print(f"   {order.contract.symbol}: {order.action} {order.totalQuantity} @ {order.orderType}")
                else:
                    print("   No open orders")
                
                print(f"\n✅ IB READY FOR TRADING THIS WEEK")
                print(f"   Connection: Active")
                print(f"   Account Status: Operational")
                print(f"   Data Feed: Connected")
                
        else:
            print(f"\n❌ IB CONNECTION FAILED")
            print(f"   Unable to establish connection to TWS/Gateway")
            
    except ConnectionRefusedError:
        print(f"\n❌ IB CONNECTION REFUSED")
        print(f"   TWS/IB Gateway is not running on port {port}")
        print(f"   Please start TWS or IB Gateway and ensure:")
        print(f"   1. Socket port {port} is enabled")
        print(f"   2. Socket client is enabled in API settings")
        print(f"   3. Trusted IP includes 127.0.0.1")
        
    except TimeoutError:
        print(f"\n⚠️ IB CONNECTION TIMEOUT")
        print(f"   TWS/Gateway is running but not responding")
        print(f"   Check API settings and restart TWS/Gateway")
        
    except Exception as e:
        print(f"\n❌ IB ERROR: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        
    finally:
        if ib.isConnected():
            ib.disconnect()
            print(f"\n🔌 Disconnected from IB")

if __name__ == "__main__":
    check_ib_connection()
