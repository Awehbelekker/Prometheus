#!/usr/bin/env python3
"""
Test Alpaca Connection
"""

import os
import alpaca_trade_api as tradeapi

# Set credentials
api_key = "PKVMBY8RX3NZ9YERXYT4"
api_secret = "nIqQG0ljmFJCbcC00k5Voz4Q3Nah2VAmVMBJh7zV"
base_url = "https://paper-api.alpaca.markets"

print(f"🔑 Testing Alpaca Connection...")
print(f"   API Key: {api_key}")
print(f"   Secret: {api_secret[:8]}...")
print(f"   Base URL: {base_url}")
print()

try:
    # Create API connection
    api = tradeapi.REST(
        api_key,
        api_secret,
        base_url,
        api_version='v2'
    )
    
    print("🔗 Attempting to connect...")
    
    # Test connection
    account = api.get_account()
    
    print("[CHECK] CONNECTION SUCCESSFUL!")
    print(f"   Account ID: {account.id}")
    print(f"   Account Status: {account.status}")
    print(f"   Buying Power: ${account.buying_power}")
    print(f"   Cash: ${account.cash}")
    
except Exception as e:
    print(f"[ERROR] CONNECTION FAILED: {e}")
    print(f"   Error Type: {type(e).__name__}")
    
    # Try to get more detailed error info
    if hasattr(e, 'response'):
        print(f"   Response Status: {e.response.status_code}")
        print(f"   Response Text: {e.response.text}")
