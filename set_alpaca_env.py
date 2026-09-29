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
    os.environ['ALPACA_LIVE_KEY'] = os.getenv('ALPACA_LIVE_KEY', '')
    os.environ['ALPACA_LIVE_SECRET'] = os.getenv('ALPACA_LIVE_SECRET', '')
    os.environ['ALPACA_LIVE_BASE_URL'] = 'https://api.alpaca.markets'

    # Alpaca Paper Trading (Simulated)
    # Endpoint: https://paper-api.alpaca.markets/v2
    os.environ['ALPACA_PAPER_KEY'] = os.getenv('ALPACA_PAPER_KEY', '')
    os.environ['ALPACA_PAPER_SECRET'] = os.getenv('ALPACA_PAPER_SECRET', '')
    os.environ['ALPACA_PAPER_BASE_URL'] = 'https://paper-api.alpaca.markets'

    # Default Alpaca config (uses LIVE by default)
    os.environ['ALPACA_API_KEY'] = os.getenv('ALPACA_API_KEY', '')
    os.environ['ALPACA_SECRET_KEY'] = os.getenv('ALPACA_SECRET_KEY', '')
    os.environ['ALPACA_BASE_URL'] = 'https://api.alpaca.markets'

    print("[CHECK] Environment variables set successfully!")
    
    # Test system status
    print("\nRunning system status check...")
    subprocess.run(['python', 'system_status_check.py'])

if __name__ == "__main__":
    set_alpaca_environment()
