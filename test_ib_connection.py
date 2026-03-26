#!/usr/bin/env python3
"""
Test Interactive Brokers Connection
"""

import os
import sys
import asyncio

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

async def test_ib_connection():
    """Test IB connection"""
    try:
        from ib_insync import IB, util
        
        ib = IB()
        host = os.getenv('IB_GATEWAY_HOST', '127.0.0.1')
        port = int(os.getenv('IB_GATEWAY_PORT', '7497'))
        client_id = int(os.getenv('IB_CLIENT_ID', '1'))
        
        print(f"Connecting to IB Gateway at {host}:{port} (Client ID: {client_id})...")
        
        await ib.connectAsync(host, port, clientId=client_id)
        
        if ib.isConnected():
            print("✅ IB Connection successful!")
            
            # Get account info
            accounts = await ib.reqManagedAccounts()
            print(f"Managed Accounts: {accounts}")
            
            ib.disconnect()
            return True
        else:
            print("❌ IB Connection failed")
            return False
            
    except ImportError:
        print("⚠️ ib_insync not installed. Install with: pip install ib_insync")
        return False
    except Exception as e:
        print(f"❌ IB Connection error: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_ib_connection())
