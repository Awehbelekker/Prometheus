#!/usr/bin/env python3
"""
📊 REAL-TIME AI MONITORING DASHBOARD
Monitors PROMETHEUS AI trading decisions and performance in real-time
"""

import requests
import time
import json
from datetime import datetime, timedelta
import os

class PrometheusAIMonitor:
    """Real-time AI trading monitor"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.last_ai_decisions = 0
        self.last_balance = 0.0
        self.session_start_time = datetime.now()
        self.decision_history = []
        self.performance_history = []
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_ai_status(self):
        """Get current AI status"""
        try:
            response = requests.get(f"{self.base_url}/api/ai-trading/health", timeout=3)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_trading_performance(self):
        """Get current trading performance"""
        try:
            response = requests.get(f"{self.base_url}/api/paper-trading/performance", timeout=3)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def get_revolutionary_engines(self):
        """Get Revolutionary Engines status"""
        try:
            response = requests.get(f"{self.base_url}/api/revolutionary/status", timeout=3)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None
    
    def test_ai_decision(self):
        """Test AI decision making with live market data"""
        try:
            test_payload = {
                "symbol": "AAPL",
                "market_data": {
                    "price": 175.50,
                    "change_percent": 1.2,
                    "volume": 50000000,
                    "rsi": 65.5,
                    "macd": 0.8
                },
                "strategy_context": "Live trading session - real-time analysis",
                "analysis_type": "technical",
                "time_horizon": "short_term",
                "risk_tolerance": "moderate",
                "model_size": "120b"
            }
            
            response = requests.post(
                f"{self.base_url}/api/ai-trading/trading-strategy", 
                json=test_payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                decision = {
                    "timestamp": datetime.now(),
                    "symbol": "AAPL",
                    "action": data.get('data', {}).get('action', 'HOLD'),
                    "confidence": data.get('data', {}).get('confidence', 0.0),
                    "reasoning": data.get('data', {}).get('reasoning', 'No reasoning provided')[:100]
                }
                self.decision_history.append(decision)
                # Keep only last 10 decisions
                if len(self.decision_history) > 10:
                    self.decision_history.pop(0)
                return decision
            return None
        except:
            return None
    
    def calculate_performance_metrics(self, performance_data):
        """Calculate performance metrics"""
        if not performance_data:
            return {}
        
        current_balance = performance_data.get('current_balance', 250.0)
        initial_capital = 250.0
        
        # Calculate returns
        total_return = ((current_balance - initial_capital) / initial_capital) * 100
        
        # Calculate session duration
        session_duration = datetime.now() - self.session_start_time
        hours_elapsed = session_duration.total_seconds() / 3600
        
        # Estimate daily return (extrapolate from current session)
        if hours_elapsed > 0:
            hourly_return = total_return / hours_elapsed
            estimated_daily_return = hourly_return * 24
        else:
            estimated_daily_return = 0.0
        
        return {
            "total_return": total_return,
            "estimated_daily_return": estimated_daily_return,
            "session_duration": session_duration,
            "hours_elapsed": hours_elapsed
        }
    
    def display_dashboard(self):
        """Display the real-time dashboard"""
        self.clear_screen()
        
        print("🚀 PROMETHEUS AI TRADING - REAL-TIME MONITOR")
        print("=" * 70)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Session: {(datetime.now() - self.session_start_time).total_seconds() / 3600:.1f}h")
        print("=" * 70)
        
        # AI Status Section
        ai_status = self.get_ai_status()
        print("\n🤖 AI INTELLIGENCE STATUS")
        print("-" * 40)
        if ai_status:
            gpt_20b = "[CHECK] ONLINE" if ai_status.get('gpt_oss_20b') else "[ERROR] OFFLINE"
            gpt_120b = "[CHECK] ONLINE" if ai_status.get('gpt_oss_120b') else "[ERROR] OFFLINE"
            print(f"   GPT-OSS 20B:  {gpt_20b}")
            print(f"   GPT-OSS 120B: {gpt_120b}")
            
            services = ai_status.get('services', {})
            active_services = sum(1 for s in services.values() if s)
            print(f"   Active Services: {active_services}/{len(services)}")
        else:
            print("   [ERROR] AI Status: UNAVAILABLE")
        
        # Trading Performance Section
        performance = self.get_trading_performance()
        print("\n💰 TRADING PERFORMANCE")
        print("-" * 40)
        if performance:
            current_balance = performance.get('current_balance', 0)
            total_trades = performance.get('total_trades', 0)
            ai_decisions = performance.get('ai_decisions', 0)
            
            metrics = self.calculate_performance_metrics(performance)
            
            print(f"   Current Balance: ${current_balance:.2f}")
            print(f"   Total Return: {metrics.get('total_return', 0):.2f}%")
            print(f"   Est. Daily Return: {metrics.get('estimated_daily_return', 0):.2f}%")
            print(f"   Total Trades: {total_trades}")
            print(f"   AI Decisions: {ai_decisions}")
            
            # Performance indicator
            daily_return = metrics.get('estimated_daily_return', 0)
            if daily_return >= 6.0:
                print("   🎯 Performance: ON TARGET (6-9% daily)")
            elif daily_return >= 3.0:
                print("   [WARNING]️ Performance: BELOW TARGET")
            else:
                print("   🔄 Performance: WARMING UP")
        else:
            print("   [ERROR] Performance: DATA UNAVAILABLE")
        
        # Revolutionary Engines Section
        engines = self.get_revolutionary_engines()
        print("\n[LIGHTNING] REVOLUTIONARY ENGINES")
        print("-" * 40)
        if engines:
            engine_status = engines.get('engines', {})
            active_engines = sum(1 for e in engine_status.values() if e)
            print(f"   Active Engines: {active_engines}/{len(engine_status)}")
            
            for engine_name, status in engine_status.items():
                status_icon = "[CHECK]" if status else "[ERROR]"
                print(f"   {status_icon} {engine_name.upper()}")
        else:
            print("   [ERROR] Engines: STATUS UNAVAILABLE")
        
        # Recent AI Decisions Section
        print("\n🧠 RECENT AI DECISIONS")
        print("-" * 40)
        if self.decision_history:
            for decision in self.decision_history[-5:]:  # Show last 5 decisions
                timestamp = decision['timestamp'].strftime('%H:%M:%S')
                action = decision['action']
                confidence = decision['confidence']
                reasoning = decision['reasoning'][:50] + "..." if len(decision['reasoning']) > 50 else decision['reasoning']
                
                print(f"   {timestamp} | {action} | {confidence:.2f} | {reasoning}")
        else:
            print("   🔄 Generating AI decisions...")
        
        # System Health Section
        print("\n📊 SYSTEM HEALTH")
        print("-" * 40)
        
        # Check if all critical systems are operational
        ai_healthy = ai_status and ai_status.get('gpt_oss_20b') and ai_status.get('gpt_oss_120b')
        trading_active = performance and performance.get('active_sessions', 0) > 0
        engines_active = engines and engines.get('status') == 'operational'
        
        health_score = sum([ai_healthy, trading_active, engines_active])
        
        if health_score == 3:
            print("   [CHECK] System Status: FULLY OPERATIONAL")
            print("   🚀 Ready for maximum performance trading")
        elif health_score == 2:
            print("   [WARNING]️ System Status: MOSTLY OPERATIONAL")
            print("   🔧 Minor issues detected")
        else:
            print("   [ERROR] System Status: NEEDS ATTENTION")
            print("   🛠️ Critical issues require resolution")
        
        print("\n" + "=" * 70)
        print("Press Ctrl+C to stop monitoring | Updates every 10 seconds")
        print("=" * 70)
    
    def run_monitor(self):
        """Run the real-time monitor"""
        print("🚀 Starting PROMETHEUS AI Real-Time Monitor...")
        print("⏳ Initializing dashboard...")
        time.sleep(2)
        
        try:
            while True:
                # Test AI decision making
                ai_decision = self.test_ai_decision()
                
                # Display dashboard
                self.display_dashboard()
                
                # Wait before next update
                time.sleep(10)
                
        except KeyboardInterrupt:
            print("\n\n[WARNING]️ Monitoring stopped by user")
            print("📊 Final Session Summary:")
            
            # Display final summary
            performance = self.get_trading_performance()
            if performance:
                metrics = self.calculate_performance_metrics(performance)
                print(f"   Session Duration: {metrics.get('hours_elapsed', 0):.1f} hours")
                print(f"   Total Return: {metrics.get('total_return', 0):.2f}%")
                print(f"   AI Decisions Made: {len(self.decision_history)}")
                print(f"   Final Balance: ${performance.get('current_balance', 0):.2f}")
            
            print("\n[CHECK] Monitor shutdown complete")
        
        except Exception as e:
            print(f"\n💥 Monitor error: {e}")

def main():
    """Main function"""
    monitor = PrometheusAIMonitor()
    monitor.run_monitor()

if __name__ == "__main__":
    main()
