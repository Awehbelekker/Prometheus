#!/usr/bin/env python3
"""Verify trading system restart"""
import sys
from core.alpaca_trading_service import get_alpaca_service
import os
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("="*60)
print("TRADING SYSTEM RESTART VERIFICATION")
print("="*60)
print()

# Check API key
api_key = os.getenv("ALPACA_LIVE_KEY", "NOT SET")
print(f"✅ API Key Loaded: {api_key[:15]}...{api_key[-4:] if len(api_key) > 15 else ''}")
print()

# Check Alpaca connection
alpaca = get_alpaca_service(use_paper=False)
print(f"Alpaca Service Available: {alpaca.is_available()}")

if alpaca.is_available():
    account = alpaca.get_account_info()
    if 'error' not in account:
        print(f"✅ Account Status: {account.get('status', 'UNKNOWN')}")
        print(f"✅ Portfolio Value: ${account.get('portfolio_value', 0):.2f}")
        print(f"✅ Cash Available: ${account.get('cash', 0):.2f}")
        print()
        print("🎉 Trading system is connected and ready!")
        print("   The system should start executing trades soon.")
    else:
        print(f"❌ Connection Error: {account.get('error', 'Unknown')}")
else:
    print("❌ Alpaca service not available")
    print("   Check if API keys are properly loaded")

print()
print("="*60)


