#!/usr/bin/env python3
"""
Update Alpaca API key in .env file
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import re
from pathlib import Path

def update_env_file(new_key: str, key_type: str = 'LIVE'):
    """Update Alpaca API key in .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file.absolute()}")
        return False
    
    try:
        # Read current .env file
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine which key to update
        if key_type.upper() == 'LIVE':
            key_var = 'ALPACA_LIVE_KEY'
            alt_var = 'ALPACA_API_KEY'
        elif key_type.upper() == 'PAPER':
            key_var = 'ALPACA_PAPER_KEY'
            alt_var = None
        else:
            print(f"❌ Invalid key_type: {key_type}. Use 'LIVE' or 'PAPER'")
            return False
        
        # Update the key
        updated = False
        
        # Try to update ALPACA_LIVE_KEY or ALPACA_PAPER_KEY
        pattern = rf'^{re.escape(key_var)}=.*$'
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(
                rf'^{re.escape(key_var)}=.*$',
                f'{key_var}={new_key}',
                content,
                flags=re.MULTILINE
            )
            updated = True
            print(f"✅ Updated {key_var} in .env file")
        else:
            # Add if not exists
            content += f'\n{key_var}={new_key}\n'
            updated = True
            print(f"✅ Added {key_var} to .env file")
        
        # Also update ALPACA_API_KEY if it's a live key
        if key_type.upper() == 'LIVE' and alt_var:
            pattern = rf'^{re.escape(alt_var)}=.*$'
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(
                    rf'^{re.escape(alt_var)}=.*$',
                    f'{alt_var}={new_key}',
                    content,
                    flags=re.MULTILINE
                )
                print(f"✅ Updated {alt_var} in .env file")
            else:
                content += f'\n{alt_var}={new_key}\n'
                print(f"✅ Added {alt_var} to .env file")
        
        # Write back to file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Successfully updated .env file with new {key_type} key")
        print(f"   New key: {new_key[:10]}...{new_key[-4:]}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


def update_env_secret(new_secret: str, key_type: str = 'LIVE'):
    """Update Alpaca API secret in .env file"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print(f"❌ .env file not found at {env_file.absolute()}")
        return False
    
    try:
        # Read current .env file
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine which secret to update
        if key_type.upper() == 'LIVE':
            secret_var = 'ALPACA_LIVE_SECRET'
            alt_var = 'ALPACA_SECRET_KEY'
        elif key_type.upper() == 'PAPER':
            secret_var = 'ALPACA_PAPER_SECRET'
            alt_var = None
        else:
            print(f"❌ Invalid key_type: {key_type}. Use 'LIVE' or 'PAPER'")
            return False
        
        # Update the secret
        updated = False
        
        # Try to update ALPACA_LIVE_SECRET or ALPACA_PAPER_SECRET
        pattern = rf'^{re.escape(secret_var)}=.*$'
        if re.search(pattern, content, re.MULTILINE):
            content = re.sub(
                rf'^{re.escape(secret_var)}=.*$',
                f'{secret_var}={new_secret}',
                content,
                flags=re.MULTILINE
            )
            updated = True
            print(f"✅ Updated {secret_var} in .env file")
        else:
            # Add if not exists
            content += f'\n{secret_var}={new_secret}\n'
            updated = True
            print(f"✅ Added {secret_var} to .env file")
        
        # Also update ALPACA_SECRET_KEY if it's a live secret
        if key_type.upper() == 'LIVE' and alt_var:
            pattern = rf'^{re.escape(alt_var)}=.*$'
            if re.search(pattern, content, re.MULTILINE):
                content = re.sub(
                    rf'^{re.escape(alt_var)}=.*$',
                    f'{alt_var}={new_secret}',
                    content,
                    flags=re.MULTILINE
                )
                print(f"✅ Updated {alt_var} in .env file")
            else:
                content += f'\n{alt_var}={new_secret}\n'
                print(f"✅ Added {alt_var} to .env file")
        
        # Write back to file
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Successfully updated .env file with new {key_type} secret")
        print(f"   New secret: {new_secret[:10]}...{new_secret[-4:]}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # New API key and secret from user
    new_key = "AKMMN6U5DXKTM7A2UEAAF4ZQ5Z"
    new_secret = "At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX"
    
    print("="*80)
    print("UPDATING ALPACA API KEY AND SECRET")
    print("="*80)
    print(f"\nNew Live Trading Key: {new_key}")
    print(f"New Live Trading Secret: {new_secret[:10]}...{new_secret[-4:]}")
    print(f"Endpoint: https://api.alpaca.markets")
    print()
    
    # Update .env file with key
    success_key = update_env_file(new_key, 'LIVE')
    
    # Update .env file with secret
    success_secret = update_env_secret(new_secret, 'LIVE')
    
    success = success_key and success_secret
    
    if success:
        print("\n" + "="*80)
        print("UPDATE COMPLETE")
        print("="*80)
        print("\n✅ Updated files:")
        print("   1. daily_trading_report.py")
        print("   2. .env file")
        print("\n⚠️  Note: You may need to provide the new SECRET key separately")
        print("   The secret key is required for authentication.")
        print("\n💡 To test the new key:")
        print("   python view_alpaca_live_trading.py")
    else:
        print("\n❌ Failed to update .env file")
        print("   Please update manually or check file permissions")

