#!/usr/bin/env python3
"""
Fix Alpaca Connection Issues
Diagnoses and fixes Alpaca API connection problems
"""

import os
import sys
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def check_all_alpaca_credentials():
    """Check all possible Alpaca credential environment variables"""
    print("="*80)
    print("CHECKING ALL ALPACA CREDENTIALS")
    print("="*80)
    
    credentials = {
        'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
        'ALPACA_SECRET_KEY': os.getenv('ALPACA_SECRET_KEY'),
        'APCA_API_KEY_ID': os.getenv('APCA_API_KEY_ID'),
        'APCA_API_SECRET_KEY': os.getenv('APCA_API_SECRET_KEY'),
        'ALPACA_LIVE_KEY': os.getenv('ALPACA_LIVE_KEY'),
        'ALPACA_LIVE_SECRET': os.getenv('ALPACA_LIVE_SECRET'),
        'ALPACA_PAPER_KEY': os.getenv('ALPACA_PAPER_KEY'),
        'ALPACA_PAPER_SECRET': os.getenv('ALPACA_PAPER_SECRET'),
    }
    
    found = []
    for key, value in credentials.items():
        if value:
            masked = value[:10] + '...' + value[-4:] if len(value) > 14 else '***'
            print(f"✅ {key}: {masked}")
            found.append((key, value))
        else:
            print(f"❌ {key}: NOT SET")
    
    return found

def test_alpaca_credentials(api_key, secret_key, paper=True):
    """Test Alpaca credentials"""
    base_url = 'https://paper-api.alpaca.markets' if paper else 'https://api.alpaca.markets'
    
    print(f"\nTesting credentials against: {base_url}")
    
    headers = {
        'APCA-API-KEY-ID': api_key,
        'APCA-API-SECRET-KEY': secret_key
    }
    
    try:
        response = requests.get(f'{base_url}/v2/account', headers=headers, timeout=10)
        
        if response.status_code == 200:
            account = response.json()
            print("✅ CREDENTIALS VALID!")
            print(f"   Account Number: {account.get('account_number', 'N/A')}")
            print(f"   Status: {account.get('status', 'N/A')}")
            print(f"   Equity: ${float(account.get('equity', 0)):,.2f}")
            return True, account
        elif response.status_code == 401:
            print("❌ UNAUTHORIZED - Invalid API key or secret")
            print(f"   Response: {response.text[:200]}")
            return False, None
        elif response.status_code == 403:
            print("❌ FORBIDDEN - API key may not have required permissions")
            print(f"   Response: {response.text[:200]}")
            return False, None
        else:
            print(f"❌ ERROR - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return False, None

def find_working_credentials():
    """Try all credential combinations to find working ones"""
    print("\n" + "="*80)
    print("TESTING ALL CREDENTIAL COMBINATIONS")
    print("="*80)
    
    # Get all credentials
    api_keys = [
        ('ALPACA_API_KEY', os.getenv('ALPACA_API_KEY')),
        ('APCA_API_KEY_ID', os.getenv('APCA_API_KEY_ID')),
        ('ALPACA_LIVE_KEY', os.getenv('ALPACA_LIVE_KEY')),
        ('ALPACA_PAPER_KEY', os.getenv('ALPACA_PAPER_KEY')),
    ]
    
    secret_keys = [
        ('ALPACA_SECRET_KEY', os.getenv('ALPACA_SECRET_KEY')),
        ('APCA_API_SECRET_KEY', os.getenv('APCA_API_SECRET_KEY')),
        ('ALPACA_LIVE_SECRET', os.getenv('ALPACA_LIVE_SECRET')),
        ('ALPACA_PAPER_SECRET', os.getenv('ALPACA_PAPER_SECRET')),
    ]
    
    # Filter out None values
    api_keys = [(name, key) for name, key in api_keys if key]
    secret_keys = [(name, secret) for name, secret in secret_keys if secret]
    
    # Try paper trading first
    print("\n[1] Testing PAPER TRADING credentials...")
    for api_name, api_key in api_keys:
        for secret_name, secret_key in secret_keys:
            print(f"\n   Trying: {api_name} + {secret_name}")
            valid, account = test_alpaca_credentials(api_key, secret_key, paper=True)
            if valid:
                print(f"\n✅ FOUND WORKING PAPER TRADING CREDENTIALS!")
                print(f"   Use: {api_name} and {secret_name}")
                return api_key, secret_key, True, account
    
    # Try live trading
    print("\n[2] Testing LIVE TRADING credentials...")
    for api_name, api_key in api_keys:
        for secret_name, secret_key in secret_keys:
            print(f"\n   Trying: {api_name} + {secret_name}")
            valid, account = test_alpaca_credentials(api_key, secret_key, paper=False)
            if valid:
                print(f"\n✅ FOUND WORKING LIVE TRADING CREDENTIALS!")
                print(f"   Use: {api_name} and {secret_name}")
                return api_key, secret_key, False, account
    
    print("\n❌ No working credentials found")
    return None, None, None, None

def update_env_file(api_key, secret_key, paper_trading):
    """Update .env file with working credentials"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("\n⚠️ .env file not found. Creating new one...")
        env_file.touch()
    
    # Read existing content
    lines = []
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    
    # Update or add credentials
    updated = False
    new_lines = []
    
    # Remove old Alpaca entries
    for line in lines:
        if not any(key in line.upper() for key in ['ALPACA_API_KEY', 'ALPACA_SECRET_KEY', 'APCA_API_KEY_ID', 'APCA_API_SECRET_KEY']):
            new_lines.append(line)
        else:
            updated = True
    
    # Add new credentials
    if paper_trading:
        new_lines.append(f"ALPACA_API_KEY={api_key}\n")
        new_lines.append(f"ALPACA_SECRET_KEY={secret_key}\n")
        new_lines.append(f"ALPACA_PAPER_TRADING=true\n")
    else:
        new_lines.append(f"ALPACA_API_KEY={api_key}\n")
        new_lines.append(f"ALPACA_SECRET_KEY={secret_key}\n")
        new_lines.append(f"ALPACA_PAPER_TRADING=false\n")
    
    # Write back
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ Updated .env file with working credentials")
    return True

def main():
    print("="*80)
    print("ALPACA CONNECTION FIX")
    print("="*80)
    
    # Step 1: Check all credentials
    found_creds = check_all_alpaca_credentials()
    
    if not found_creds:
        print("\n❌ No Alpaca credentials found in environment")
        print("   Please set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env file")
        return
    
    # Step 2: Find working credentials
    api_key, secret_key, paper_trading, account = find_working_credentials()
    
    if api_key and secret_key:
        # Step 3: Update .env file
        update_env_file(api_key, secret_key, paper_trading)
        
        print("\n" + "="*80)
        print("✅ ALPACA CONNECTION FIXED!")
        print("="*80)
        print(f"\nWorking credentials have been saved to .env file")
        print(f"Mode: {'PAPER TRADING' if paper_trading else 'LIVE TRADING'}")
        if account:
            print(f"Account: {account.get('account_number', 'N/A')}")
            print(f"Equity: ${float(account.get('equity', 0)):,.2f}")
    else:
        print("\n" + "="*80)
        print("❌ COULD NOT FIX ALPACA CONNECTION")
        print("="*80)
        print("\nPossible issues:")
        print("  1. API keys are incorrect or expired")
        print("  2. Account may be suspended or inactive")
        print("  3. API keys may not have required permissions")
        print("  4. Network connectivity issues")
        print("\nNext steps:")
        print("  1. Verify API keys in Alpaca dashboard: https://app.alpaca.markets/")
        print("  2. Check account status")
        print("  3. Regenerate API keys if needed")
        print("  4. Ensure API keys have trading permissions enabled")

if __name__ == "__main__":
    main()

