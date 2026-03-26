#!/usr/bin/env python3
"""
Configuration Validation
Validates all configuration on startup
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def validate_configuration():
    """Validate all configuration"""
    print("=" * 80)
    print("CONFIGURATION VALIDATION")
    print("=" * 80)
    print()
    
    errors = []
    warnings = []
    
    # Validate Alpaca credentials
    alpaca_key = (os.getenv('ALPACA_API_KEY') or 
                 os.getenv('ALPACA_LIVE_KEY') or
                 os.getenv('APCA_API_KEY_ID'))
    alpaca_secret = (os.getenv('ALPACA_SECRET_KEY') or 
                    os.getenv('ALPACA_LIVE_SECRET') or
                    os.getenv('APCA_API_SECRET_KEY'))
    
    if not alpaca_key or not alpaca_secret:
        warnings.append("Alpaca credentials not found (optional for IB-only trading)")
    else:
        if len(alpaca_key) < 20:
            errors.append("Alpaca API key appears invalid (too short)")
        if len(alpaca_secret) < 20:
            errors.append("Alpaca secret key appears invalid (too short)")
        print("[OK] Alpaca credentials: Valid")
    
    # Validate IB configuration
    # Valid ports: 7496=TWS Live, 7497=TWS Paper, 4001=Gateway Paper, 4002=Gateway Live
    ib_port = os.getenv('IB_PORT', '4002')
    try:
        ib_port_int = int(ib_port)
        valid_ports = {7496: "TWS Live", 7497: "TWS Paper", 4001: "Gateway Paper", 4002: "Gateway Live"}
        if ib_port_int not in valid_ports:
            warnings.append(f"IB port {ib_port} is unusual (expected one of {list(valid_ports.keys())})")
        else:
            mode = valid_ports[ib_port_int]
            print(f"[OK] IB Port: {ib_port} ({mode})")
    except ValueError:
        errors.append(f"IB_PORT must be a number, got: {ib_port}")
    
    ib_account = os.getenv('IB_ACCOUNT', '')
    if not ib_account:
        warnings.append("IB_ACCOUNT not set (will use default)")
    else:
        print(f"[OK] IB Account: {ib_account}")
    
    # Validate database paths
    critical_dbs = ['prometheus_trading.db', 'portfolio_persistence.db']
    for db in critical_dbs:
        if not Path(db).exists():
            errors.append(f"Critical database not found: {db}")
        else:
            print(f"[OK] Database: {db} exists")
    
    # Validate risk limits
    try:
        daily_loss_limit = float(os.getenv('DAILY_LOSS_LIMIT', '25'))
        if daily_loss_limit <= 0:
            errors.append("DAILY_LOSS_LIMIT must be positive")
        elif daily_loss_limit > 1000:
            warnings.append(f"DAILY_LOSS_LIMIT is very high: ${daily_loss_limit}")
        else:
            print(f"[OK] Daily Loss Limit: ${daily_loss_limit}")
    except ValueError:
        errors.append("DAILY_LOSS_LIMIT must be a number")
    
    # Validate position sizing
    try:
        position_size = float(os.getenv('POSITION_SIZE_PCT', '0.08'))
        if position_size <= 0 or position_size > 1:
            errors.append("POSITION_SIZE_PCT must be between 0 and 1")
        else:
            print(f"[OK] Position Size: {position_size*100}%")
    except ValueError:
        errors.append("POSITION_SIZE_PCT must be a number")
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        warnings.append(".env file not found (using system environment)")
    else:
        print("[OK] .env file exists")
    
    # Summary
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print()
    
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(f"  [ERROR] {error}")
        print()
        return False
    
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"  [WARNING] {warning}")
        print()
    
    if not errors and not warnings:
        print("[OK] All configuration validated successfully!")
        print()
        return True
    
    if not errors:
        print("[OK] Configuration is valid (some warnings)")
        print()
        return True
    
    return False

if __name__ == "__main__":
    success = validate_configuration()
    if not success:
        print("=" * 80)
        print("VALIDATION FAILED - Please fix errors before starting")
        print("=" * 80)
        exit(1)
    else:
        print("=" * 80)
        print("VALIDATION PASSED - Configuration is ready")
        print("=" * 80)

