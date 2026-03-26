#!/usr/bin/env python3
"""
📊 REAL-TIME TRADING MONITOR
Monitors PROMETHEUS performance and AI decision generation in real-time
"""

import requests
import time
import json
from datetime import datetime, timedelta
import threading
import os

class RealTimeTradingMonitor:
    """Real-time monitoring of PROMETHEUS trading performance"""
    
    def __init__(self):
        self.is_monitoring = False
        self.start_time = None
        self.last_ai_decisions = 0
        self.last_balance = 0.0
        self.decision_history = []
        self.performance_log = []
        
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.is_monitoring = True
        self.start_time = datetime.now()
        
        print("🚀 PROMETHEUS REAL-TIME MONITORING STARTED")
        print("=" * 60)
        print(f"⏰ Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Monitoring: AI decisions, performance, system health")
        print("=" * 60)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        return monitor_thread
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                self._collect_metrics()
                self._display_status()
                time.sleep(10)  # Update every 10 seconds
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(5)
    
    def _collect_metrics(self):
        """Collect system metrics"""
        current_time = datetime.now()
        
        # Collect AI status
        ai_status = self._get_ai_status()
        
        # Collect trading performance
        trading_status = self._get_trading_status()
        
        # Collect system health
        system_health = self._get_system_health()
        
        # Create metrics snapshot
        metrics = {
            "timestamp": current_time.isoformat(),
            "ai_status": ai_status,
            "trading_status": trading_status,
            "system_health": system_health,
            "uptime_minutes": (current_time - self.start_time).total_seconds() / 60
        }
        
        self.performance_log.append(metrics)
        
        # Keep only last 100 entries
        if len(self.performance_log) > 100:
            self.performance_log.pop(0)
    
    def _get_ai_status(self):
        """Get AI system status"""
        try:
            response = requests.get("http://localhost:8000/api/ai/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"ai_available": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"ai_available": False, "error": str(e)}
    
    def _get_trading_status(self):
        """Get trading system status"""
        try:
            response = requests.get("http://localhost:8000/api/paper-trading/performance", timeout=5)
            if response.status_code == 200:
                return response.json()
            return {"active_sessions": 0, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"active_sessions": 0, "error": str(e)}
    
    def _get_system_health(self):
        """Get system health status"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            backend_healthy = response.status_code == 200
            
            # Check GPT-OSS models
            gpt_oss_20b = self._check_gpt_oss("http://localhost:5000")
            gpt_oss_120b = self._check_gpt_oss("http://localhost:5001")
            
            return {
                "backend_healthy": backend_healthy,
                "gpt_oss_20b_available": gpt_oss_20b,
                "gpt_oss_120b_available": gpt_oss_120b
            }
        except Exception as e:
            return {"backend_healthy": False, "error": str(e)}
    
    def _check_gpt_oss(self, endpoint):
        """Check GPT-OSS model availability"""
        try:
            response = requests.get(f"{endpoint}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _display_status(self):
        """Display current status"""
        if not self.performance_log:
            return
        
        latest = self.performance_log[-1]
        current_time = datetime.now()
        
        # Clear screen (works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🚀 PROMETHEUS REAL-TIME TRADING MONITOR")
        print("=" * 60)
        print(f"⏰ Current Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Uptime: {latest['uptime_minutes']:.1f} minutes")
        print("=" * 60)
        
        # AI Status
        ai_status = latest['ai_status']
        ai_available = ai_status.get('ai_available', False)
        available_models = ai_status.get('available_models', [])
        
        print("🤖 AI INTELLIGENCE STATUS:")
        print(f"   Status: {'[CHECK] ACTIVE' if ai_available else '[ERROR] INACTIVE'}")
        print(f"   Models: {len(available_models)} available")
        
        if available_models:
            gpt_oss_models = [m for m in available_models if 'gpt_oss' in m.lower()]
            if gpt_oss_models:
                print(f"   GPT-OSS: [CHECK] {gpt_oss_models}")
            else:
                print("   GPT-OSS: [ERROR] Not detected")
        
        # Trading Status
        trading_status = latest['trading_status']
        active_sessions = trading_status.get('active_sessions', 0)
        current_balance = trading_status.get('current_balance', 0)
        total_trades = trading_status.get('total_trades', 0)
        ai_decisions = trading_status.get('ai_decisions', 0)
        
        print("\n💰 LIVE TRADING STATUS:")
        print(f"   Sessions: {'[CHECK] ACTIVE' if active_sessions > 0 else '[ERROR] INACTIVE'} ({active_sessions})")
        print(f"   Balance: ${current_balance:.2f}")
        print(f"   Total Trades: {total_trades}")
        print(f"   AI Decisions: {ai_decisions}")
        
        # Calculate decision rate
        if len(self.performance_log) > 1:
            prev_decisions = self.performance_log[-2]['trading_status'].get('ai_decisions', 0)
            new_decisions = ai_decisions - prev_decisions
            if new_decisions > 0:
                print(f"   🧠 New Decisions: +{new_decisions} (last 10s)")
        
        # System Health
        system_health = latest['system_health']
        backend_healthy = system_health.get('backend_healthy', False)
        gpt_oss_20b = system_health.get('gpt_oss_20b_available', False)
        gpt_oss_120b = system_health.get('gpt_oss_120b_available', False)
        
        print("\n🔧 SYSTEM HEALTH:")
        print(f"   Backend: {'[CHECK] HEALTHY' if backend_healthy else '[ERROR] UNHEALTHY'}")
        print(f"   GPT-OSS 20B: {'[CHECK] AVAILABLE' if gpt_oss_20b else '[ERROR] UNAVAILABLE'}")
        print(f"   GPT-OSS 120B: {'[CHECK] AVAILABLE' if gpt_oss_120b else '[ERROR] UNAVAILABLE'}")
        
        # Performance Summary
        if len(self.performance_log) >= 6:  # At least 1 minute of data
            self._display_performance_summary()
        
        print("\n" + "=" * 60)
        print("Press Ctrl+C to stop monitoring")
    
    def _display_performance_summary(self):
        """Display performance summary"""
        recent_logs = self.performance_log[-6:]  # Last 6 entries (1 minute)
        
        # Calculate AI decision rate
        first_decisions = recent_logs[0]['trading_status'].get('ai_decisions', 0)
        last_decisions = recent_logs[-1]['trading_status'].get('ai_decisions', 0)
        decisions_per_minute = last_decisions - first_decisions
        
        # Calculate system availability
        healthy_checks = sum(1 for log in recent_logs if log['system_health'].get('backend_healthy', False))
        availability = (healthy_checks / len(recent_logs)) * 100
        
        print("\n📊 PERFORMANCE SUMMARY (Last 1 minute):")
        print(f"   AI Decisions/min: {decisions_per_minute}")
        print(f"   System Availability: {availability:.1f}%")
        
        if decisions_per_minute > 0:
            print("   🎯 AI Decision Generation: [CHECK] ACTIVE")
        else:
            print("   🎯 AI Decision Generation: [WARNING]️ LOW ACTIVITY")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        print("\n⏹️ Monitoring stopped")
    
    def save_performance_log(self, filename=None):
        """Save performance log to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"prometheus_performance_log_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.performance_log, f, indent=2)
        
        print(f"📄 Performance log saved to: {filename}")

def main():
    """Main monitoring function"""
    monitor = RealTimeTradingMonitor()
    
    try:
        # Start monitoring
        monitor_thread = monitor.start_monitoring()
        
        # Keep main thread alive
        while monitor.is_monitoring:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopping monitor...")
        monitor.stop_monitoring()
        
        # Save performance log
        monitor.save_performance_log()
        
        print("[CHECK] Monitoring session complete")

if __name__ == "__main__":
    main()
