"""
PROMETHEUS DUAL-BROKER WEEK-LONG TRADING
========================================
Launches simultaneous trading on BOTH brokers with ALL systems:
- IB Gateway (U21922116): $251.58
- Alpaca Markets: $122.48
- Total Capital: $374.06

ALL SYSTEMS ENABLED:
✅ Visual AI: 1,352 patterns
✅ Intelligence: 8 sources (Reddit, Twitter, Google Trends, Bloomberg, Economic, Weather, Crypto, Market Data)
✅ Learning Engine: Gen 359+ (92.4% win rate)
✅ Real-World Data Orchestrator
✅ Multi-asset trading: Stocks, Crypto, Forex
✅ Continuous learning & adaptation
"""

import asyncio
import os
import sys
import time
from datetime import datetime, timedelta
import subprocess
import signal

# Ensure environment is set for LIVE trading
os.environ['LIVE_TRADING_ENABLED'] = 'true'
os.environ['ALPACA_PAPER_TRADING'] = 'false'

# Load from .env
from dotenv import load_dotenv
load_dotenv()

print("\n" + "="*80)
print("  🚀 PROMETHEUS DUAL-BROKER AUTONOMOUS TRADING SYSTEM")
print("  Week-Long Operation with ALL Systems Active")
print("="*80)
print("\n💰 CAPITAL ALLOCATION:")
print("   IB Gateway (U21922116): $251.58 (67%)")
print("   Alpaca Markets: $122.48 (33%)")
print("   TOTAL: $374.06")
print("\n🧠 ACTIVE SYSTEMS:")
print("   ✅ Visual AI: 1,352 chart patterns")
print("   ✅ Intelligence: 8 real-world data sources")
print("   ✅ Learning Engine: Gen 359+ (92.4% win rate)")
print("   ✅ Multi-Asset: Stocks, Crypto, Forex")
print("   ✅ Risk Management: 2% position sizing, 1.5% stop-loss")
print("\n⏱️  DURATION: 7 days (168 hours)")
print("   Session Length: 8 hours each")
print("   Break Between: 5 minutes")
print("   Expected Sessions: ~21 total")
print("\n" + "="*80)

# Week-long parameters
TOTAL_DURATION_DAYS = 7
SESSION_DURATION_HOURS = 8
BREAK_MINUTES = 5

class DualBrokerCoordinator:
    """Coordinates trading across both IB and Alpaca"""
    
    def __init__(self):
        self.ib_process = None
        self.alpaca_process = None
        self.running = True
        self.sessions_completed = 0
        self.start_time = datetime.now()
        
        # Cumulative statistics
        self.total_trades = 0
        self.total_pnl = 0.0
        self.ib_trades = 0
        self.alpaca_trades = 0
        self.ib_pnl = 0.0
        self.alpaca_pnl = 0.0
        
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n⚠️  SHUTDOWN SIGNAL RECEIVED")
        print("   Stopping both brokers gracefully...")
        self.running = False
        self.stop_all_processes()
        sys.exit(0)
    
    def stop_all_processes(self):
        """Stop both broker processes"""
        if self.ib_process:
            print("   🛑 Stopping IB session...")
            self.ib_process.terminate()
            try:
                self.ib_process.wait(timeout=10)
            except:
                self.ib_process.kill()
        
        if self.alpaca_process:
            print("   🛑 Stopping Alpaca session...")
            self.alpaca_process.terminate()
            try:
                self.alpaca_process.wait(timeout=10)
            except:
                self.alpaca_process.kill()
    
    async def run_dual_session(self, session_hours):
        """Run both brokers simultaneously for specified hours"""
        print(f"\n{'='*80}")
        print(f"  📊 SESSION {self.sessions_completed + 1} - DUAL BROKER TRADING")
        print(f"{'='*80}")
        print(f"⏰ Duration: {session_hours} hours")
        print(f"🎯 Strategy: Independent operation on each broker")
        print(f"💰 IB Capital: $251.58 | Alpaca Capital: $122.48")
        
        # Create IB-specific session file
        ib_session_code = """
import asyncio
import os
import sys
os.environ['LIVE_TRADING_ENABLED'] = 'true'
os.environ['ALPACA_PAPER_TRADING'] = 'false'
os.environ['PRIMARY_BROKER'] = 'IB'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prometheus_active_trading_session import PrometheusActiveTradingSession

async def main():
    session = PrometheusActiveTradingSession(session_id=f"ib_dual_broker_{os.getpid()}")
    await session.initialize_ib_connection()
    duration_minutes = """ + str(session_hours * 60) + """
    await session.run_session(duration_minutes=duration_minutes)

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        # Create Alpaca-specific session file
        alpaca_session_code = """
import asyncio
import os
import sys
os.environ['LIVE_TRADING_ENABLED'] = 'true'
os.environ['ALPACA_PAPER_TRADING'] = 'false'
os.environ['PRIMARY_BROKER'] = 'ALPACA'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prometheus_active_trading_session import PrometheusActiveTradingSession

async def main():
    session = PrometheusActiveTradingSession(session_id=f"alpaca_dual_broker_{os.getpid()}")
    duration_minutes = """ + str(session_hours * 60) + """
    await session.run_session(duration_minutes=duration_minutes)

if __name__ == "__main__":
    asyncio.run(main())
"""
        
        # Write temporary session files
        with open('temp_ib_session.py', 'w') as f:
            f.write(ib_session_code)
        
        with open('temp_alpaca_session.py', 'w') as f:
            f.write(alpaca_session_code)
        
        # Launch both processes
        print(f"\n🚀 Launching IB Gateway session...")
        self.ib_process = subprocess.Popen(
            [sys.executable, 'temp_ib_session.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        await asyncio.sleep(5)  # Stagger startup
        
        print(f"🚀 Launching Alpaca session...")
        self.alpaca_process = subprocess.Popen(
            [sys.executable, 'temp_alpaca_session.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        print(f"\n✅ Both brokers active!")
        print(f"   IB Process ID: {self.ib_process.pid}")
        print(f"   Alpaca Process ID: {self.alpaca_process.pid}")
        
        # Monitor both processes
        session_start = datetime.now()
        session_end = session_start + timedelta(hours=session_hours)
        
        while datetime.now() < session_end and self.running:
            # Check if processes are still running
            ib_running = self.ib_process.poll() is None
            alpaca_running = self.alpaca_process.poll() is None
            
            if not ib_running or not alpaca_running:
                print(f"\n⚠️  Process status: IB={'Running' if ib_running else 'Stopped'}, Alpaca={'Running' if alpaca_running else 'Stopped'}")
                if not ib_running and not alpaca_running:
                    break
            
            # Progress update every 30 minutes
            elapsed = (datetime.now() - session_start).total_seconds() / 3600
            remaining = (session_end - datetime.now()).total_seconds() / 3600
            
            if elapsed % 0.5 < 0.01:  # Every 30 min
                print(f"\n📊 Session Progress: {elapsed:.1f}h elapsed, {remaining:.1f}h remaining")
                print(f"   IB: {'✅ Active' if ib_running else '❌ Stopped'}")
                print(f"   Alpaca: {'✅ Active' if alpaca_running else '❌ Stopped'}")
            
            await asyncio.sleep(60)  # Check every minute
        
        # Session complete - stop processes
        print(f"\n⏰ Session {self.sessions_completed + 1} completed")
        self.stop_all_processes()
        
        # Collect results
        await self.collect_session_results()
        
        self.sessions_completed += 1
    
    async def collect_session_results(self):
        """Collect and summarize results from both brokers"""
        print(f"\n📊 Collecting session results...")
        
        import json
        import glob
        
        # Find latest IB reports
        ib_reports = sorted(glob.glob('prometheus_active_report_ib_*.json'), 
                           key=os.path.getmtime, reverse=True)
        
        # Find latest Alpaca reports
        alpaca_reports = sorted(glob.glob('prometheus_active_report_alpaca_*.json'),
                               key=os.path.getmtime, reverse=True)
        
        if ib_reports:
            with open(ib_reports[0]) as f:
                ib_data = json.load(f)
                ib_trades = ib_data.get('trading_activity', {}).get('trades_executed', 0)
                ib_pnl = ib_data.get('total_pnl', 0)
                self.ib_trades += ib_trades
                self.ib_pnl += ib_pnl
                print(f"   IB: {ib_trades} trades, ${ib_pnl:.2f} P&L")
        
        if alpaca_reports:
            with open(alpaca_reports[0]) as f:
                alpaca_data = json.load(f)
                alpaca_trades = alpaca_data.get('trading_activity', {}).get('trades_executed', 0)
                alpaca_pnl = alpaca_data.get('total_pnl', 0)
                self.alpaca_trades += alpaca_trades
                self.alpaca_pnl += alpaca_pnl
                print(f"   Alpaca: {alpaca_trades} trades, ${alpaca_pnl:.2f} P&L")
        
        self.total_trades = self.ib_trades + self.alpaca_trades
        self.total_pnl = self.ib_pnl + self.alpaca_pnl
    
    async def run_week_long(self):
        """Run week-long dual-broker trading"""
        signal.signal(signal.SIGINT, self.signal_handler)
        
        end_time = self.start_time + timedelta(days=TOTAL_DURATION_DAYS)
        
        print(f"\n🚀 Starting {TOTAL_DURATION_DAYS}-day autonomous dual-broker trading")
        print(f"   Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while datetime.now() < end_time and self.running:
            try:
                # Run session
                await self.run_dual_session(SESSION_DURATION_HOURS)
                
                # Check if we have time for another session
                if datetime.now() + timedelta(hours=SESSION_DURATION_HOURS) > end_time:
                    print(f"\n✅ Reached end of {TOTAL_DURATION_DAYS}-day period")
                    break
                
                # Break between sessions
                if self.running and datetime.now() < end_time:
                    print(f"\n⏸️  {BREAK_MINUTES}-minute break between sessions...")
                    print(f"   Total sessions completed: {self.sessions_completed}")
                    print(f"   Combined trades: {self.total_trades}")
                    print(f"   Combined P&L: ${self.total_pnl:.2f}")
                    
                    for i in range(BREAK_MINUTES):
                        if not self.running:
                            break
                        await asyncio.sleep(60)
                        if (i + 1) % 1 == 0:
                            print(f"   Break: {i+1}/{BREAK_MINUTES} minutes...")
            
            except Exception as e:
                print(f"\n❌ Session error: {e}")
                print(f"   Waiting 10 minutes before restart...")
                await asyncio.sleep(600)
                continue
        
        # Final summary
        self.print_final_summary()
    
    def print_final_summary(self):
        """Print final week summary"""
        duration = datetime.now() - self.start_time
        hours = duration.total_seconds() / 3600
        
        print("\n" + "="*80)
        print("  🏁 PROMETHEUS DUAL-BROKER WEEK SUMMARY")
        print("="*80)
        print(f"\n⏱️  DURATION:")
        print(f"   Total Runtime: {hours:.1f} hours ({duration.days} days)")
        print(f"   Sessions Completed: {self.sessions_completed}")
        
        print(f"\n💰 TRADING RESULTS:")
        print(f"   Combined Trades: {self.total_trades}")
        print(f"   Combined P&L: ${self.total_pnl:.2f}")
        
        print(f"\n📊 BY BROKER:")
        print(f"   IB Gateway:")
        print(f"      Trades: {self.ib_trades}")
        print(f"      P&L: ${self.ib_pnl:.2f}")
        print(f"      Starting: $251.58")
        print(f"      Ending: ${251.58 + self.ib_pnl:.2f}")
        
        print(f"\n   Alpaca Markets:")
        print(f"      Trades: {self.alpaca_trades}")
        print(f"      P&L: ${self.alpaca_pnl:.2f}")
        print(f"      Starting: $122.48")
        print(f"      Ending: ${122.48 + self.alpaca_pnl:.2f}")
        
        print(f"\n📈 FINAL PORTFOLIO:")
        initial_capital = 251.58 + 122.48
        final_capital = initial_capital + self.total_pnl
        roi = (self.total_pnl / initial_capital) * 100
        
        print(f"   Initial Capital: ${initial_capital:.2f}")
        print(f"   Final Capital: ${final_capital:.2f}")
        print(f"   Total Return: ${self.total_pnl:.2f} ({roi:+.2f}%)")
        
        print("\n" + "="*80)
        print("  ✅ WEEK-LONG DUAL-BROKER TRADING COMPLETE")
        print("="*80 + "\n")

async def main():
    """Main entry point"""
    coordinator = DualBrokerCoordinator()
    await coordinator.run_week_long()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Manual shutdown - exiting gracefully")
