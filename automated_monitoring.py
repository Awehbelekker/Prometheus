#!/usr/bin/env python3
"""
PROMETHEUS TRADING PLATFORM - AUTOMATED MONITORING SYSTEM
========================================================
Continuous monitoring and reporting for the 48-hour demo and Revolutionary Engines
"""

import json
import requests
import sqlite3
import time
import os
from datetime import datetime, timedelta
from pathlib import Path
import csv

class PrometheusMonitoringSystem:
    def __init__(self):
        self.demo_url = "http://localhost:8000"
        self.revolutionary_url = "http://localhost:8002"
        self.reports_dir = Path("monitoring_reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def get_demo_status(self):
        """Get 48-hour demo status"""
        try:
            response = requests.get(f"{self.demo_url}/health", timeout=5)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "offline"}
    
    def get_revolutionary_performance(self):
        """Get Revolutionary Engines performance"""
        try:
            response = requests.get(f"{self.revolutionary_url}/api/revolutionary/performance", timeout=5)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "offline"}
    
    def calculate_investment_returns(self, initial_amount, performance_data):
        """Calculate returns for any investment amount"""
        if "summary" not in performance_data:
            return None
            
        total_pnl = performance_data["summary"]["total_pnl_total"]
        # Assuming $100k starting capital for performance calculation
        performance_rate = total_pnl / 100000
        current_value = initial_amount * (1 + performance_rate)
        profit = current_value - initial_amount
        profit_percentage = (profit / initial_amount) * 100
        
        return {
            "initial_amount": initial_amount,
            "current_value": current_value,
            "profit": profit,
            "profit_percentage": profit_percentage
        }
    
    def generate_monitoring_report(self):
        """Generate comprehensive monitoring report"""
        timestamp = datetime.now()
        
        # Get data
        demo_data = self.get_demo_status()
        revolutionary_data = self.get_revolutionary_performance()
        
        # Calculate runtime
        uptime_hours = demo_data.get("uptime_seconds", 0) / 3600
        remaining_hours = 48 - uptime_hours
        completion_percentage = (uptime_hours / 48) * 100
        
        # Investment calculations
        r130_returns = self.calculate_investment_returns(130, revolutionary_data)
        r1000_returns = self.calculate_investment_returns(1000, revolutionary_data)
        r10000_returns = self.calculate_investment_returns(10000, revolutionary_data)
        
        # Generate report
        report = {
            "timestamp": timestamp.isoformat(),
            "demo_status": {
                "runtime_hours": round(uptime_hours, 2),
                "remaining_hours": round(remaining_hours, 2),
                "completion_percentage": round(completion_percentage, 2),
                "status": "RUNNING" if demo_data.get("status") == "ok" else "OFFLINE"
            },
            "revolutionary_engines": {
                "status": revolutionary_data.get("summary", {}).get("status", "UNKNOWN"),
                "total_pnl_today": revolutionary_data.get("summary", {}).get("total_pnl_today", 0),
                "total_pnl_total": revolutionary_data.get("summary", {}).get("total_pnl_total", 0),
                "total_trades": revolutionary_data.get("summary", {}).get("total_trades", 0),
                "win_rate": revolutionary_data.get("summary", {}).get("win_rate", 0) * 100,
                "hourly_rate": revolutionary_data.get("summary", {}).get("total_pnl_today", 0) / max(uptime_hours, 1)
            },
            "investment_returns": {
                "R130": r130_returns,
                "R1000": r1000_returns,
                "R10000": r10000_returns
            },
            "projections": {
                "24_hour_projection": revolutionary_data.get("summary", {}).get("total_pnl_today", 0) / max(uptime_hours, 1) * 24,
                "48_hour_projection": revolutionary_data.get("summary", {}).get("total_pnl_today", 0) / max(uptime_hours, 1) * 48
            }
        }
        
        # Save to file
        filename = f"monitoring_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report, filepath
    
    def generate_csv_summary(self):
        """Generate CSV summary for spreadsheet analysis"""
        demo_data = self.get_demo_status()
        revolutionary_data = self.get_revolutionary_performance()
        
        uptime_hours = demo_data.get("uptime_seconds", 0) / 3600
        
        # CSV data
        csv_data = {
            "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Runtime_Hours": round(uptime_hours, 2),
            "Completion_%": round((uptime_hours / 48) * 100, 2),
            "Total_PnL_$": revolutionary_data.get("summary", {}).get("total_pnl_total", 0),
            "Daily_PnL_$": revolutionary_data.get("summary", {}).get("total_pnl_today", 0),
            "Total_Trades": revolutionary_data.get("summary", {}).get("total_trades", 0),
            "Win_Rate_%": revolutionary_data.get("summary", {}).get("win_rate", 0) * 100,
            "Hourly_Rate_$": revolutionary_data.get("summary", {}).get("total_pnl_today", 0) / max(uptime_hours, 1),
            "R130_Current_Value": 130 * (1 + revolutionary_data.get("summary", {}).get("total_pnl_total", 0) / 100000),
            "R130_Profit_%": (revolutionary_data.get("summary", {}).get("total_pnl_total", 0) / 100000) * 100
        }
        
        # Save/append to CSV
        csv_file = self.reports_dir / "performance_tracking.csv"
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(csv_data)
        
        return csv_file
    
    def print_status_update(self):
        """Print formatted status update to console"""
        demo_data = self.get_demo_status()
        revolutionary_data = self.get_revolutionary_performance()
        
        uptime_hours = demo_data.get("uptime_seconds", 0) / 3600
        remaining_hours = 48 - uptime_hours
        
        print(f"\n🔥 PROMETHEUS MONITORING UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        print(f"📊 48-HOUR DEMO STATUS:")
        print(f"   ⏱️  Runtime: {uptime_hours:.1f} hours ({(uptime_hours/48)*100:.1f}% complete)")
        print(f"   ⏳ Remaining: {remaining_hours:.1f} hours")
        print(f"   🎯 Status: {'RUNNING' if demo_data.get('status') == 'ok' else 'OFFLINE'}")
        
        if "summary" in revolutionary_data:
            summary = revolutionary_data["summary"]
            print(f"\n🚀 REVOLUTIONARY ENGINES:")
            print(f"   💰 Total P&L: ${summary.get('total_pnl_total', 0):,.2f}")
            print(f"   📈 Daily P&L: ${summary.get('total_pnl_today', 0):,.2f}")
            print(f"   🎯 Win Rate: {summary.get('win_rate', 0)*100:.1f}%")
            print(f"   [LIGHTNING] Hourly Rate: ${summary.get('total_pnl_today', 0)/max(uptime_hours, 1):,.2f}/hour")
            
            # R130 update
            performance_rate = summary.get('total_pnl_total', 0) / 100000
            r130_value = 130 * (1 + performance_rate)
            r130_profit = r130_value - 130
            print(f"\n💡 R130 INVESTMENT:")
            print(f"   💵 Current Value: R{r130_value:.2f}")
            print(f"   📈 Profit: R{r130_profit:.2f} ({(r130_profit/130)*100:.1f}%)")
        
        print("=" * 70)
    
    def continuous_monitoring(self, interval_minutes=30):
        """Run continuous monitoring with specified interval"""
        print(f"🎯 Starting continuous monitoring (every {interval_minutes} minutes)")
        print("📁 Reports will be saved to:", self.reports_dir.absolute())
        print("⌨️  Press Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                # Generate reports
                report, filepath = self.generate_monitoring_report()
                csv_file = self.generate_csv_summary()
                self.print_status_update()
                
                print(f"📄 Report saved: {filepath.name}")
                print(f"📊 CSV updated: {csv_file.name}")
                print(f"⏰ Next update in {interval_minutes} minutes...\n")
                
                # Wait for next interval
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")
            print(f"📁 All reports saved in: {self.reports_dir.absolute()}")

def main():
    monitor = PrometheusMonitoringSystem()
    
    print("🔥 PROMETHEUS AUTOMATED MONITORING SYSTEM")
    print("=" * 50)
    print("Options:")
    print("1. Generate single report")
    print("2. Start continuous monitoring (30 min intervals)")
    print("3. Start frequent monitoring (5 min intervals)")
    print("4. Just show current status")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        report, filepath = monitor.generate_monitoring_report()
        csv_file = monitor.generate_csv_summary()
        monitor.print_status_update()
        print(f"\n[CHECK] Report generated: {filepath}")
        print(f"[CHECK] CSV updated: {csv_file}")
        
    elif choice == "2":
        monitor.continuous_monitoring(interval_minutes=30)
        
    elif choice == "3":
        monitor.continuous_monitoring(interval_minutes=5)
        
    elif choice == "4":
        monitor.print_status_update()
        
    else:
        print("Invalid choice. Showing current status:")
        monitor.print_status_update()

if __name__ == "__main__":
    main()
