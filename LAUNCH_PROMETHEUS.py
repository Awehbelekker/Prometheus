#!/usr/bin/env python3
"""
PROMETHEUS UNIFIED LAUNCHER
Single entry point for the complete Prometheus trading system

This launcher:
- Integrates all systems from both workspaces
- Uses unified configuration from .env
- Supports full system initialization
- Includes official HRM integration
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main launcher from Trading Platform
# This is the primary, most up-to-date launcher
from launch_ultimate_prometheus_LIVE_TRADING import PrometheusLiveTradingLauncher

def main():
    """Main entry point for Prometheus system"""
    print("=" * 80)
    print("PROMETHEUS UNIFIED TRADING SYSTEM")
    print("=" * 80)
    print("Launching from unified entry point...")
    print("Using: launch_ultimate_prometheus_LIVE_TRADING.py")
    print("=" * 80)
    print()
    
    # Initialize and run the main launcher
    launcher = PrometheusLiveTradingLauncher(standalone_mode=True)
    
    # Run the system
    import asyncio
    asyncio.run(launcher.run())

if __name__ == "__main__":
    main()


