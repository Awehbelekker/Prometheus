#!/usr/bin/env python3
"""
DAILY TRADING REPORT
====================

Generates a comprehensive daily trading report for PROMETHEUS
"""

import os
import json
import requests
import time
from datetime import datetime, timedelta

def generate_daily_trading_report():
    """Generate comprehensive daily trading report"""
    print("PROMETHEUS DAILY TRADING REPORT")
    print("=" * 80)
    print("Date: {}".format(datetime.now().strftime("%A, %B %d, %Y")))
    print("Time: {}".format(datetime.now().strftime("%H:%M:%S")))
    print("=" * 80)
    
    # Set environment variables
    os.environ['ALPACA_LIVE_KEY'] = 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z'
    os.environ['ALPACA_LIVE_SECRET'] = 'At2pPUS7TyGj3vAdjRAA6wuDXQDKkaejxTGL5w3rBhJX'
    os.environ['ALPACA_PAPER_KEY'] = 'PKL57SQSLF436UTL8PKA'
    os.environ['ALPACA_PAPER_SECRET'] = 'KohlWcBbNmntvKv2oZ9fd9kCxKqd1tchYvS642NA'
    
    # Initialize report data
    report_data = {
        "date": datetime.now().isoformat(),
        "system_status": {},
        "portfolio_summary": {},
        "trading_activity": {},
        "broker_status": {},
        "performance_metrics": {},
        "risk_analysis": {},
        "recommendations": {}
    }
    
    print("\n1. SYSTEM STATUS")
    print("-" * 60)
    
    # Check server status
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            report_data["system_status"]["server"] = {
                "status": health_data.get('status', 'Unknown'),
                "version": health_data.get('version', 'Unknown'),
                "server": health_data.get('server', 'Unknown')
            }
            print("   Server Status: {}".format(health_data.get('status', 'Unknown')))
            print("   Server: {}".format(health_data.get('server', 'Unknown')))
            print("   Version: {}".format(health_data.get('version', 'Unknown')))
        else:
            print("   WARNING: Server health check failed")
    except Exception as e:
        print("   ERROR: Server not responding: {}".format(e))
    
    # Check live trading status
    try:
        response = requests.get('http://localhost:8000/api/live-trading/status', timeout=5)
        if response.status_code == 200:
            live_data = response.json()
            live_trading = live_data.get('live_trading', {})
            report_data["system_status"]["live_trading"] = {
                "enabled": live_trading.get('enabled', False),
                "active": live_trading.get('active', False)
            }
            print("   Live Trading: {}".format(live_trading.get('enabled', False)))
            print("   Live Trading Active: {}".format(live_trading.get('active', False)))
    except Exception as e:
        print("   WARNING: Live trading status error: {}".format(e))
    
    print("\n2. PORTFOLIO SUMMARY")
    print("-" * 60)
    
    # Check portfolio value
    try:
        response = requests.get('http://localhost:8000/api/portfolio/value', timeout=5)
        if response.status_code == 200:
            portfolio_data = response.json()
            total_value = portfolio_data.get('total_value', 0)
            cash_balance = portfolio_data.get('cash_balance', 0)
            invested_value = portfolio_data.get('invested_value', 0)
            unrealized_pnl = portfolio_data.get('unrealized_pnl', 0)
            total_return_pct = portfolio_data.get('total_return_pct', 0)
            
            report_data["portfolio_summary"] = {
                "total_value": total_value,
                "cash_balance": cash_balance,
                "invested_value": invested_value,
                "unrealized_pnl": unrealized_pnl,
                "total_return_pct": total_return_pct
            }
            
            print("   Total Portfolio Value: ${:,.2f}".format(total_value))
            print("   Cash Balance: ${:,.2f}".format(cash_balance))
            print("   Invested Value: ${:,.2f}".format(invested_value))
            print("   Unrealized P&L: ${:,.2f}".format(unrealized_pnl))
            print("   Total Return: {:.2%}".format(total_return_pct))
            
            # Calculate daily return target progress
            target_daily_return = 0.07  # 7%
            if total_value > 0:
                daily_return_needed = target_daily_return * total_value
                print("   Daily Return Target: ${:,.2f} ({:.1%})".format(daily_return_needed, target_daily_return))
                if unrealized_pnl > 0:
                    progress = (unrealized_pnl / daily_return_needed) * 100
                    print("   Progress to Target: {:.1f}%".format(progress))
        else:
            print("   WARNING: Portfolio status check failed")
    except Exception as e:
        print("   WARNING: Portfolio status error: {}".format(e))
    
    print("\n3. TRADING ACTIVITY")
    print("-" * 60)
    
    # Check active trades
    try:
        response = requests.get('http://localhost:8000/api/trading/active', timeout=5)
        if response.status_code == 200:
            trading_data = response.json()
            active_trades = trading_data.get('active_trades', [])
            today_trades = trading_data.get('today_trades', 0)
            
            report_data["trading_activity"] = {
                "active_trades": len(active_trades),
                "today_trades": today_trades,
                "trades": active_trades
            }
            
            print("   Active Trades: {}".format(len(active_trades)))
            print("   Today's Trades: {}".format(today_trades))
            
            if active_trades:
                print("   Active Positions:")
                for i, trade in enumerate(active_trades[:5]):  # Show first 5
                    symbol = trade.get('symbol', 'Unknown')
                    side = trade.get('side', 'Unknown')
                    quantity = trade.get('quantity', 0)
                    price = trade.get('price', 0)
                    pnl = trade.get('unrealized_pnl', 0)
                    print("     {}. {} {} {} @ ${:.2f} (P&L: ${:.2f})".format(
                        i+1, symbol, side, quantity, price, pnl))
            else:
                print("   No active positions")
        else:
            print("   WARNING: Trading activity check failed")
    except Exception as e:
        print("   WARNING: Trading activity error: {}".format(e))
    
    # Check trading history
    try:
        response = requests.get('http://localhost:8000/api/trading/history', timeout=5)
        if response.status_code == 200:
            history_data = response.json()
            recent_trades = history_data.get('trades', [])
            
            print("   Historical Trades: {}".format(len(recent_trades)))
            
            if recent_trades:
                print("   Recent Trades:")
                for i, trade in enumerate(recent_trades[:3]):  # Show last 3
                    symbol = trade.get('symbol', 'Unknown')
                    side = trade.get('side', 'Unknown')
                    quantity = trade.get('quantity', 0)
                    price = trade.get('price', 0)
                    timestamp = trade.get('timestamp', 'Unknown')
                    print("     {}. {} {} {} @ ${:.2f} ({})".format(
                        i+1, symbol, side, quantity, price, timestamp))
            else:
                print("   No historical trades")
        else:
            print("   WARNING: Trading history check failed")
    except Exception as e:
        print("   WARNING: Trading history error: {}".format(e))
    
    print("\n4. BROKER STATUS")
    print("-" * 60)
    
    # Check IB connection
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 7496))
        sock.close()
        
        if result == 0:
            print("   IB Live Trading: Connected (127.0.0.1:7496)")
            report_data["broker_status"]["ib"] = {"status": "connected", "host": "127.0.0.1", "port": 7496}
        else:
            print("   IB Live Trading: Disconnected (code: {})".format(result))
            report_data["broker_status"]["ib"] = {"status": "disconnected", "error_code": result}
    except Exception as e:
        print("   IB Live Trading: Connection error: {}".format(e))
        report_data["broker_status"]["ib"] = {"status": "error", "error": str(e)}
    
    # Check Alpaca live connection
    try:
        headers = {
            'APCA-API-KEY-ID': os.environ['ALPACA_LIVE_KEY'],
            'APCA-API-SECRET-KEY': os.environ['ALPACA_LIVE_SECRET']
        }
        
        response = requests.get(
            'https://api.alpaca.markets/v2/account',
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            account_data = response.json()
            buying_power = float(account_data.get('buying_power', 0))
            portfolio_value = float(account_data.get('portfolio_value', 0))
            print("   Alpaca Live Trading: Connected")
            print("   Account: {}".format(account_data.get('id', 'N/A')[:8] + '...'))
            print("   Buying Power: ${:,.2f}".format(buying_power))
            print("   Portfolio Value: ${:,.2f}".format(portfolio_value))
            report_data["broker_status"]["alpaca_live"] = {
                "status": "connected",
                "account": account_data.get('id', 'N/A'),
                "buying_power": buying_power,
                "portfolio_value": portfolio_value
            }
        else:
            print("   Alpaca Live Trading: Connection issue (status: {})".format(response.status_code))
            report_data["broker_status"]["alpaca_live"] = {"status": "error", "status_code": response.status_code}
    except Exception as e:
        print("   Alpaca Live Trading: Connection error: {}".format(e))
        report_data["broker_status"]["alpaca_live"] = {"status": "error", "error": str(e)}
    
    # Check Alpaca paper connection
    try:
        headers = {
            'APCA-API-KEY-ID': os.environ['ALPACA_PAPER_KEY'],
            'APCA-API-SECRET-KEY': os.environ['ALPACA_PAPER_SECRET']
        }
        
        response = requests.get(
            'https://paper-api.alpaca.markets/v2/account',
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            account_data = response.json()
            buying_power = float(account_data.get('buying_power', 0))
            portfolio_value = float(account_data.get('portfolio_value', 0))
            print("   Alpaca Paper Trading: Connected")
            print("   Account: {}".format(account_data.get('id', 'N/A')[:8] + '...'))
            print("   Buying Power: ${:,.2f}".format(buying_power))
            print("   Portfolio Value: ${:,.2f}".format(portfolio_value))
            report_data["broker_status"]["alpaca_paper"] = {
                "status": "connected",
                "account": account_data.get('id', 'N/A'),
                "buying_power": buying_power,
                "portfolio_value": portfolio_value
            }
        else:
            print("   Alpaca Paper Trading: Connection issue (status: {})".format(response.status_code))
            report_data["broker_status"]["alpaca_paper"] = {"status": "error", "status_code": response.status_code}
    except Exception as e:
        print("   Alpaca Paper Trading: Connection error: {}".format(e))
        report_data["broker_status"]["alpaca_paper"] = {"status": "error", "error": str(e)}
    
    print("\n5. PERFORMANCE ANALYSIS")
    print("-" * 60)
    
    # Calculate performance metrics
    try:
        response = requests.get('http://localhost:8000/api/portfolio/value', timeout=5)
        if response.status_code == 200:
            portfolio_data = response.json()
            total_value = portfolio_data.get('total_value', 0)
            total_return_pct = portfolio_data.get('total_return_pct', 0)
            
            # Performance assessment
            target_daily_return = 0.07  # 7%
            current_time = datetime.now()
            market_open_time = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close_time = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
            
            if current_time < market_open_time:
                market_status = "Pre-market"
                next_event = market_open_time.strftime("%H:%M")
            elif current_time > market_close_time:
                market_status = "After-hours"
                next_event = "Next trading day"
            else:
                market_status = "Open"
                hours_elapsed = (current_time - market_open_time).total_seconds() / 3600
                hours_remaining = (market_close_time - current_time).total_seconds() / 3600
                next_event = "{} hours remaining".format(hours_remaining)
            
            print("   Market Status: {}".format(market_status))
            print("   Next Event: {}".format(next_event))
            
            # Return analysis
            if total_return_pct > 0:
                print("   Current Return: {:.2%} (Positive)".format(total_return_pct))
            elif total_return_pct < 0:
                print("   Current Return: {:.2%} (Negative)".format(total_return_pct))
            else:
                print("   Current Return: 0.00% (No trades yet)")
            
            # Target analysis
            if total_return_pct >= target_daily_return:
                print("   TARGET ACHIEVED: {:.2%} >= {:.1%}".format(total_return_pct, target_daily_return))
            else:
                remaining_return = target_daily_return - total_return_pct
                print("   Target Remaining: {:.2%}".format(remaining_return))
                
                if total_value > 0:
                    remaining_dollar = remaining_return * total_value
                    print("   Dollar Target Remaining: ${:,.2f}".format(remaining_dollar))
            
            report_data["performance_metrics"] = {
                "market_status": market_status,
                "current_return": total_return_pct,
                "target_daily_return": target_daily_return,
                "target_achieved": total_return_pct >= target_daily_return
            }
        else:
            print("   WARNING: Performance analysis failed")
    except Exception as e:
        print("   WARNING: Performance analysis error: {}".format(e))
    
    print("\n6. RISK ANALYSIS")
    print("-" * 60)
    
    # Risk assessment
    try:
        response = requests.get('http://localhost:8000/api/portfolio/value', timeout=5)
        if response.status_code == 200:
            portfolio_data = response.json()
            total_value = portfolio_data.get('total_value', 0)
            invested_value = portfolio_data.get('invested_value', 0)
            unrealized_pnl = portfolio_data.get('unrealized_pnl', 0)
            
            # Calculate risk metrics
            if total_value > 0:
                exposure_pct = (invested_value / total_value) * 100
                print("   Portfolio Exposure: {:.1f}%".format(exposure_pct))
                
                if exposure_pct > 80:
                    risk_level = "HIGH"
                elif exposure_pct > 50:
                    risk_level = "MEDIUM"
                else:
                    risk_level = "LOW"
                
                print("   Risk Level: {}".format(risk_level))
                
                # Drawdown analysis
                if unrealized_pnl < 0:
                    drawdown_pct = abs(unrealized_pnl / total_value) * 100
                    print("   Current Drawdown: {:.2%}".format(drawdown_pct / 100))
                    
                    if drawdown_pct > 10:
                        print("   WARNING: Drawdown exceeds 10% limit")
                    elif drawdown_pct > 5:
                        print("   CAUTION: Drawdown exceeds 5% threshold")
                else:
                    print("   Current Drawdown: 0.00%")
                
                report_data["risk_analysis"] = {
                    "exposure_pct": exposure_pct,
                    "risk_level": risk_level,
                    "drawdown_pct": abs(unrealized_pnl / total_value) * 100 if unrealized_pnl < 0 else 0
                }
        else:
            print("   WARNING: Risk analysis failed")
    except Exception as e:
        print("   WARNING: Risk analysis error: {}".format(e))
    
    print("\n7. RECOMMENDATIONS")
    print("-" * 60)
    
    # Generate recommendations
    try:
        response = requests.get('http://localhost:8000/api/trading/active', timeout=5)
        if response.status_code == 200:
            trading_data = response.json()
            today_trades = trading_data.get('today_trades', 0)
            
            if today_trades == 0:
                print("   RECOMMENDATION: No trades executed today")
                print("   ACTION: System should start executing trades based on market signals")
                print("   TARGET: Execute first trade within next hour")
                report_data["recommendations"] = {
                    "status": "no_trades",
                    "action": "start_trading",
                    "target": "execute_first_trade"
                }
            elif today_trades < 5:
                print("   RECOMMENDATION: Low trading activity")
                print("   ACTION: Increase trading frequency to reach 6-8% daily target")
                print("   TARGET: Execute 5+ trades today")
                report_data["recommendations"] = {
                    "status": "low_activity",
                    "action": "increase_frequency",
                    "target": "5_plus_trades"
                }
            else:
                print("   RECOMMENDATION: Good trading activity")
                print("   ACTION: Continue current strategy and monitor performance")
                print("   TARGET: Maintain momentum towards 6-8% daily return")
                report_data["recommendations"] = {
                    "status": "good_activity",
                    "action": "continue_strategy",
                    "target": "maintain_momentum"
                }
        else:
            print("   RECOMMENDATION: Check system status")
            print("   ACTION: Verify all connections and restart if needed")
            report_data["recommendations"] = {
                "status": "system_check",
                "action": "verify_connections",
                "target": "restart_if_needed"
            }
    except Exception as e:
        print("   RECOMMENDATION: System monitoring error")
        print("   ACTION: Check system health and connections")
        report_data["recommendations"] = {
            "status": "monitoring_error",
            "action": "check_health",
            "target": "fix_connections"
        }
    
    # Save report to file
    with open("daily_trading_report_{}.json".format(datetime.now().strftime("%Y%m%d")), "w") as f:
        json.dump(report_data, f, indent=2)
    
    print("\n8. SUMMARY")
    print("-" * 60)
    print("   Report Generated: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print("   System Status: {}".format(report_data["system_status"].get("server", {}).get("status", "Unknown")))
    print("   Portfolio Value: ${:,.2f}".format(report_data["portfolio_summary"].get("total_value", 0)))
    print("   Today's Trades: {}".format(report_data["trading_activity"].get("today_trades", 0)))
    print("   Current Return: {:.2%}".format(report_data["portfolio_summary"].get("total_return_pct", 0)))
    print("   Target Progress: {:.1f}%".format(
        (report_data["portfolio_summary"].get("total_return_pct", 0) / 0.07) * 100 if report_data["portfolio_summary"].get("total_return_pct", 0) > 0 else 0
    ))
    
    print("\nDAILY TRADING REPORT COMPLETE")
    print("=" * 80)
    print("Report saved to: daily_trading_report_{}.json".format(datetime.now().strftime("%Y%m%d")))
    
    return report_data

if __name__ == "__main__":
    generate_daily_trading_report()

