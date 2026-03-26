#!/usr/bin/env python3
"""
Fix Alpaca Credentials Configuration
Checks and fixes Alpaca API credentials in .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv, set_key

def check_alpaca_credentials():
    """Check what Alpaca credentials are currently set"""
    print("=" * 80)
    print("CHECKING ALPACA CREDENTIALS")
    print("=" * 80)
    print()
    
    load_dotenv()
    
    # All possible variable names
    possible_keys = [
        'ALPACA_LIVE_KEY',
        'ALPACA_LIVE_API_KEY', 
        'ALPACA_API_KEY',
        'APCA_API_KEY_ID',
        'ALPACA_KEY'
    ]
    
    possible_secrets = [
        'ALPACA_LIVE_SECRET',
        'ALPACA_LIVE_SECRET_KEY',
        'ALPACA_SECRET_KEY',
        'APCA_API_SECRET_KEY',
        'ALPACA_SECRET'
    ]
    
    print("Checking for API Key:")
    found_key = None
    found_key_name = None
    for key_name in possible_keys:
        value = os.getenv(key_name)
        if value:
            found_key = value
            found_key_name = key_name
            print(f"  [OK] Found: {key_name} ({len(value)} chars)")
            break
        else:
            print(f"  [NOT SET] {key_name}")
    
    print()
    print("Checking for Secret Key:")
    found_secret = None
    found_secret_name = None
    for secret_name in possible_secrets:
        value = os.getenv(secret_name)
        if value:
            found_secret = value
            found_secret_name = secret_name
            print(f"  [OK] Found: {secret_name} ({len(value)} chars)")
            break
        else:
            print(f"  [NOT SET] {secret_name}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    if found_key and found_secret:
        print(f"[OK] Alpaca credentials found!")
        print(f"   API Key: {found_key_name}")
        print(f"   Secret: {found_secret_name}")
        print()
        print("The launcher will use these credentials.")
        print("If connection still fails, check:")
        print("  1. Credentials are correct")
        print("  2. Alpaca account is active")
        print("  3. API keys have trading permissions")
        return True
    else:
        print("[ERROR] Alpaca credentials NOT FOUND")
        print()
        if not found_key:
            print("Missing: API Key")
        if not found_secret:
            print("Missing: Secret Key")
        print()
        print("SOLUTION:")
        print("Add to .env file:")
        print("  ALPACA_API_KEY=your_api_key_here")
        print("  ALPACA_SECRET_KEY=your_secret_key_here")
        print()
        print("OR")
        print("  ALPACA_LIVE_KEY=your_api_key_here")
        print("  ALPACA_LIVE_SECRET=your_secret_key_here")
        return False

def add_alpaca_to_env():
    """Add Alpaca credentials to .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("[ERROR] .env file not found!")
        return False
    
    print()
    print("=" * 80)
    print("ADD ALPACA CREDENTIALS")
    print("=" * 80)
    print()
    print("Enter your Alpaca API credentials:")
    print("(Get them from: https://app.alpaca.markets/paper/dashboard/overview)")
    print()
    
    api_key = input("Alpaca API Key: ").strip()
    secret_key = input("Alpaca Secret Key: ").strip()
    
    if not api_key or not secret_key:
        print("[ERROR] Both API key and secret key are required")
        return False
    
    # Add to .env
    set_key(env_file, 'ALPACA_API_KEY', api_key)
    set_key(env_file, 'ALPACA_SECRET_KEY', secret_key)
    
    print()
    print("[OK] Alpaca credentials added to .env file")
    print("Restart Prometheus to use new credentials")
    return True

def main():
    has_credentials = check_alpaca_credentials()
    
    if not has_credentials:
        print()
        response = input("Would you like to add Alpaca credentials now? (y/n): ").strip().lower()
        if response == 'y':
            add_alpaca_to_env()
        else:
            print()
            print("You can add credentials manually to .env file:")
            print("  ALPACA_API_KEY=your_key")
            print("  ALPACA_SECRET_KEY=your_secret")

if __name__ == "__main__":
    main()

