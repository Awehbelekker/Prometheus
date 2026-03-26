#!/usr/bin/env python3
"""
Set Alpaca environment variables and test system status
"""

import os
import subprocess

def set_alpaca_environment():
    """Set Alpaca API credentials in environment"""
    print("Setting Alpaca environment variables...")

    # Alpaca Live Trading (Real Money)
    # Endpoint: https://api.alpaca.markets
    os.environ['ALPACA_LIVE_KEY'] = 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z'
    os.environ['ALPACA_LIVE_SECRET'] = 'At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX'
    os.environ['ALPACA_LIVE_BASE_URL'] = 'https://api.alpaca.markets'

    # Alpaca Paper Trading (Simulated)
    # Endpoint: https://paper-api.alpaca.markets/v2
    os.environ['ALPACA_PAPER_KEY'] = 'PKGIGLKU24GYR6A5U5LHX7BI4V'
    os.environ['ALPACA_PAPER_SECRET'] = '7paLc4eD3qY8My4EjQsWgPrteYti1uyK1tvaya1rtqxM'
    os.environ['ALPACA_PAPER_BASE_URL'] = 'https://paper-api.alpaca.markets'

    # Default Alpaca config (uses LIVE by default)
    os.environ['ALPACA_API_KEY'] = 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z'
    os.environ['ALPACA_SECRET_KEY'] = 'At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX'
    os.environ['ALPACA_BASE_URL'] = 'https://api.alpaca.markets'

    print("[CHECK] Environment variables set successfully!")
    
    # Test system status
    print("\nRunning system status check...")
    subprocess.run(['python', 'system_status_check.py'])

if __name__ == "__main__":
    set_alpaca_environment()
