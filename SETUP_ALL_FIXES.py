#!/usr/bin/env python3
"""
Quick Setup Script for All Fixes
Implements all solutions for the three critical issues
"""

import os
import sys


def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    print_header("🚀 PROMETHEUS TRADING PLATFORM - FIX IMPLEMENTATION")
    
    print("""
This script will guide you through implementing all fixes for:
1. ✅ Alpaca Broker Issues
2. ✅ IB Random Position Analysis  
3. ✅ Terminal Display Improvements

All code fixes have been implemented in the codebase.
Follow these steps to complete the setup:
""")
    
    print_header("STEP 1: Set Alpaca API Keys")
    print("""
Run these commands in PowerShell (replace with your actual keys):

    $env:ALPACA_API_KEY = "YOUR_ALPACA_API_KEY_HERE"
    $env:ALPACA_SECRET_KEY = "YOUR_ALPACA_SECRET_KEY_HERE"

Or set permanently:

    [System.Environment]::SetEnvironmentVariable('ALPACA_API_KEY', 'YOUR_KEY', 'User')
    [System.Environment]::SetEnvironmentVariable('ALPACA_SECRET_KEY', 'YOUR_SECRET', 'User')
    # Then restart PowerShell

Status: 🟡 MANUAL ACTION REQUIRED
""")
    
    print_header("STEP 2: Install Required Packages")
    print("""
Run this command to install Rich library for enhanced terminal display:

    pip install rich

Status: 🟡 MANUAL ACTION REQUIRED
""")
    
    print_header("STEP 3: Start IB Gateway/TWS")
    print("""
1. Open IB Gateway or Trader Workstation
2. Login with credentials
3. Go to: Global Configuration → API → Settings
4. Enable: "Enable ActiveX and Socket Clients"
5. Set Socket port: 7496
6. Uncheck: "Read-Only API"
7. Check: "Allow connections from localhost only"
8. Click OK and restart Gateway

Test connection:
    Test-NetConnection -ComputerName localhost -Port 7496

Status: 🟡 MANUAL ACTION REQUIRED
""")
    
    print_header("STEP 4: Code Fixes Applied")
    print("""
✅ COMPLETED: Added place_order alias to AlpacaBroker
    File: brokers/alpaca_broker.py
    Line: ~450 (after get_order method)
    
✅ COMPLETED: Created enhanced terminal display module
    File: enhanced_terminal_display.py
    Usage: from enhanced_terminal_display import dashboard, log_info
    
✅ COMPLETED: Fixed unicode encoding issues
    All file operations now use utf-8 encoding
    
Status: ✅ COMPLETE (No action needed)
""")
    
    print_header("STEP 5: Test Your Fixes")
    print("""
After completing Steps 1-3, run these tests:

1. Test Alpaca Connection:
    python -c "import os; from brokers.alpaca_broker import AlpacaBroker; import asyncio; asyncio.run(AlpacaBroker({'api_key': os.getenv('ALPACA_API_KEY'), 'secret_key': os.getenv('ALPACA_SECRET_KEY'), 'paper_trading': True}).connect())"

2. Test IB Connection & Check Positions:
    python check_ib_positions.py

3. Test Enhanced Terminal Display:
    python enhanced_terminal_display.py

4. Run Full Diagnostics:
    python diagnose_all_issues.py

Status: 🟡 READY TO TEST
""")
    
    print_header("STEP 6: Start Trading with Fixes")
    print("""
Once all tests pass, start your trading system:

    python improved_dual_broker_trading.py

The system now includes:
✅ Working Alpaca broker with place_order method
✅ IB position monitoring (when Gateway is running)
✅ Enhanced terminal display with Rich formatting
✅ Color-coded logging for better readability
✅ Real-time dashboard with positions and P&L

Status: 🟡 READY TO START (after tests)
""")
    
    print_header("📋 ISSUE RESOLUTION SUMMARY")
    print("""
ISSUE 1: Alpaca Broker Problems
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Fixed: Added place_order() alias method to AlpacaBroker
⚠️  Action: Set ALPACA_API_KEY and ALPACA_SECRET_KEY environment variables
✅ Info: Current crypto positions down 7-13% (within normal volatility)

ISSUE 2: IB Random Position  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Cannot connect: IB Gateway/TWS not running on port 7496
⚠️  Action: Start IB Gateway/TWS and enable API settings
✅ Tool: Use check_ib_positions.py to analyze position once connected

ISSUE 3: Terminal Display Issues
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Fixed: Created enhanced_terminal_display.py with Rich library
✅ Fixed: Unicode encoding issues resolved (utf-8)
✅ Added: Color-coded logging (INFO=blue, SUCCESS=green, WARNING=yellow, ERROR=red)
✅ Added: Real-time dashboard with positions, P&L, and stats
⚠️  Action: Install Rich library (pip install rich)
""")
    
    print_header("🎯 QUICK COMMAND REFERENCE")
    print("""
# Set API keys (PowerShell):
$env:ALPACA_API_KEY = "your_key"
$env:ALPACA_SECRET_KEY = "your_secret"

# Install packages:
pip install rich

# Test connections:
python diagnose_all_issues.py

# Check IB positions:
python check_ib_positions.py

# Test enhanced display:
python enhanced_terminal_display.py

# Start trading:
python improved_dual_broker_trading.py
""")
    
    print_header("📚 DOCUMENTATION FILES CREATED")
    print("""
✅ COMPREHENSIVE_SOLUTIONS.md - Complete solution guide
✅ enhanced_terminal_display.py - Rich terminal UI module  
✅ diagnose_all_issues.py - Comprehensive diagnostic tool
✅ brokers/alpaca_broker.py - Fixed with place_order alias

All files are in your workspace and ready to use!
""")
    
    print("\n" + "=" * 80)
    print("  Setup guide completed! Follow the steps above to implement all fixes.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
