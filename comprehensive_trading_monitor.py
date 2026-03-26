#!/usr/bin/env python3
"""
Comprehensive PROMETHEUS Trading Monitor
=======================================

Real-time monitoring of all trading activities across all markets
"""

import requests
import time
import json
from datetime import datetime, timedelta
import os

def monitor_comprehensive_trading():
    """Monitor all PROMETHEUS trading activities"""
    print("PROMETHEUS COMPREHENSIVE TRADING MONITOR")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    base_url = "http://localhost:8000"
    
    # Track metrics
    start_time = datetime.now()
    start_value = 250.0
    target_daily_return = 0.07  # 7% daily target
    target_value = start_value * (1 + target_daily_return)
    
    print(f"Starting Portfolio Value: ${start_value:.2f}")
    print(f"Target Daily Value: ${target_value:.2f} (+{target_daily_return*100:.1f}%)")
    print("=" * 70)
    
    # Market status tracking
    market_status = {
        'crypto': {'active': False, 'symbols': 0, 'trades': 0},
        'stocks': {'active': False, 'symbols': 0, 'trades': 0},
        'forex': {'active': False, 'symbols': 0, 'trades': 0},
        'overnight': {'active': False, 'symbols': 0, 'trades': 0}
    }
    
    while True:
        try:
            # Get system health
            health_response = requests.get(f"{base_url}/health", timeout=5)
            health_data = health_response.json() if health_response.status_code == 200 else {}
            
            # Get live trading status
            trading_response = requests.get(f"{base_url}/api/live-trading/status", timeout=5)
            trading_data = trading_response.json() if trading_response.status_code == 200 else {}
            
            # Get portfolio value
            portfolio_response = requests.get(f"{base_url}/api/portfolio/value", timeout=5)
            portfolio_data = portfolio_response.json() if portfolio_response.status_code == 200 else {}
            
            # Get active trades
            active_response = requests.get(f"{base_url}/api/trading/active", timeout=5)
            active_data = active_response.json() if active_response.status_code == 200 else {}
            
            # Get trading history
            history_response = requests.get(f"{base_url}/api/trading/history", timeout=5)
            history_data = history_response.json() if history_response.status_code == 200 else {}
            
            # Calculate metrics
            current_time = datetime.now()
            elapsed_hours = (current_time - start_time).total_seconds() / 3600
            current_value = portfolio_data.get('total_value', start_value)
            current_return = (current_value - start_value) / start_value * 100
            progress_to_target = (current_value - start_value) / (target_value - start_value) * 100
            
            # Display status
            print(f"\n[{current_time.strftime('%H:%M:%S')}] COMPREHENSIVE STATUS")
            print(f"Portfolio Value: ${current_value:.2f} ({current_return:+.2f}%)")
            print(f"Progress to Target: {progress_to_target:.1f}%")
            print(f"Elapsed Time: {elapsed_hours:.1f} hours")
            
            # System status
            print(f"System Health: {health_data.get('status', 'Unknown')}")
            print(f"Live Trading: {trading_data.get('live_trading', {}).get('enabled', False)}")
            print(f"Active Trades: {active_data.get('count', 0)}")
            print(f"Total Trades: {history_data.get('count', 0)}")
            
            # Market breakdown
            print("\nMARKET STATUS:")
            print(f"  Crypto (24/7): {market_status['crypto']['symbols']} symbols, {market_status['crypto']['trades']} trades")
            print(f"  Stocks (Extended): {market_status['stocks']['symbols']} symbols, {market_status['stocks']['trades']} trades")
            print(f"  Forex (24/5): {market_status['forex']['symbols']} symbols, {market_status['forex']['trades']} trades")
            print(f"  Overnight (IB): {market_status['overnight']['symbols']} symbols, {market_status['overnight']['trades']} trades")
            
            # Performance analysis
            if elapsed_hours > 0:
                hourly_return = current_return / elapsed_hours
                projected_daily = hourly_return * 24
                print(f"\nPERFORMANCE ANALYSIS:")
                print(f"  Hourly Return: {hourly_return:+.2f}%")
                print(f"  Projected Daily: {projected_daily:+.2f}%")
                
                if projected_daily >= 6.0:
                    print("  STATUS: ON TRACK FOR 6-8% DAILY TARGET!")
                elif projected_daily >= 3.0:
                    print("  STATUS: MODERATE PROGRESS - Need more trades")
                else:
                    print("  STATUS: NEEDS ACCELERATION - System may need tuning")
            
            # Check for issues
            if current_return < -5:
                print("  WARNING: Portfolio down >5% - Check risk management")
            
            if active_data.get('count', 0) == 0 and history_data.get('count', 0) == 0:
                print("  WARNING: NO TRADING ACTIVITY - System may need activation")
            
            # System recommendations
            print("\nSYSTEM RECOMMENDATIONS:")
            if history_data.get('count', 0) == 0:
                print("  1. Check if main trading launcher is running")
                print("  2. Verify broker connections (IB and Alpaca)")
                print("  3. Check market conditions and confidence thresholds")
                print("  4. Monitor for 30+ minutes to see first trades")
            elif history_data.get('count', 0) < 10:
                print("  1. System is starting - first trades detected")
                print("  2. Monitor for more trading activity")
                print("  3. Check if confidence thresholds need adjustment")
            else:
                print("  1. System is actively trading")
                print("  2. Monitor performance and risk management")
                print("  3. Track progress towards 6-8% daily target")
            
            print("-" * 70)
            
            # Wait before next check
            time.sleep(30)  # Check every 30 seconds
            
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")
            print("Waiting 60 seconds before retry...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_comprehensive_trading()

