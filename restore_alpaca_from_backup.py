#!/usr/bin/env python3
"""
Restore Alpaca credentials from .env.backup to .env
"""

from pathlib import Path
from dotenv import set_key

def restore_alpaca_credentials():
    """Restore Alpaca credentials from backup"""
    backup_file = Path('.env.backup')
    env_file = Path('.env')
    
    if not backup_file.exists():
        print("[ERROR] .env.backup file not found")
        return False
    
    print("=" * 80)
    print("RESTORING ALPACA CREDENTIALS FROM BACKUP")
    print("=" * 80)
    print()
    
    # Read backup file
    backup_content = backup_file.read_text(encoding='utf-8', errors='ignore')
    lines = backup_content.split('\n')
    
    # Find Alpaca credentials
    alpaca_vars = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Check if it's an Alpaca credential
            key_upper = key.upper()
            if any(x in key_upper for x in ['ALPACA', 'APCA']) and any(x in key_upper for x in ['KEY', 'SECRET', 'ID']):
                alpaca_vars[key] = value
                print(f"[FOUND] {key} = {value[:20]}..." if len(value) > 20 else f"[FOUND] {key} = {value}")
    
    if not alpaca_vars:
        print("[ERROR] No Alpaca credentials found in backup file")
        return False
    
    print()
    print(f"Found {len(alpaca_vars)} Alpaca variable(s)")
    print()
    
    # Add to .env file
    print("Adding to .env file...")
    for key, value in alpaca_vars.items():
        set_key(env_file, key, value)
        print(f"[OK] Added {key}")
    
    print()
    print("=" * 80)
    print("RESTORATION COMPLETE")
    print("=" * 80)
    print()
    print("Alpaca credentials restored from backup!")
    print("Restart Prometheus to use the credentials.")
    print()
    
    return True

if __name__ == "__main__":
    restore_alpaca_credentials()

