"""
🚀 PROMETHEUS WEEK-LONG AUTONOMOUS TRADING SESSION
==================================================
Duration: 7 days (continuous)
Mode: Fully autonomous with self-management
Features:
  • 24/7 monitoring for crypto opportunities
  • Market hours trading for stocks
  • Automatic position management
  • Daily learning and adaptation
  • Auto-restart on completion
  • Background training integration
"""

import asyncio
import os
from datetime import datetime, timedelta
from prometheus_active_trading_session import PrometheusActiveTradingSession

def display_config():
    """Display week-long session configuration"""
    print("\n" + "="*70)
    print("  🚀 PROMETHEUS WEEK-LONG AUTONOMOUS TRADING")
    print("="*70)
    
    print("\n📋 SESSION CONFIGURATION:")
    print("   ⏱️  Duration: 7 days (10,080 minutes)")
    print("   🔁 Mode: Continuous with 5-min scan intervals")
    print("   🔌 IB Gateway: Port 4002 (LIVE TRADING)")
    print("   🤖 Intelligence: 8 sources active")
    print("   👁️  Visual AI: 1,352 patterns loaded")
    print("   🧠 Learning Engine: Gen 359+ (92.4% top win rate)")
    print("   💰 Capital: $540 USD (full balance)")
    print("   📊 Max Trades: 8 per day")
    print("   🎯 Position Size: $10.80 (2% risk per trade)")
    
    print("\n🎯 AUTONOMOUS FEATURES:")
    print("   √ 24/7 crypto trading (BTC, ETH, SOL, AVAX, ADA, DOGE)")
    print("   √ Market hours stock trading (AAPL, MSFT, GOOGL, etc.)")
    print("   √ 24/5 forex trading (EUR/USD, GBP/USD, USD/JPY)")
    print("   √ Automatic position management")
    print("   √ Risk management (1.5% stop loss)")
    print("   √ Real-time intelligence gathering")
    print("   √ Pattern recognition across all asset classes")
    print("   √ Adaptive confidence thresholds")
    
    print("\n📈 TRADING PHILOSOPHY:")
    print("   • Execute trades when confidence > 60%")
    print("   • Scan markets every 5 minutes")
    print("   • Maximum 8 trades per day (capital preservation)")
    print("   • Small position sizes (2% risk per trade)")
    print("   • Let winners run, cut losers quickly")
    
    print("\n🔬 PARALLEL ACTIVITIES (User-Managed):")
    print("   1. Backend Training:")
    print("      → Run PROMETHEUS_ULTIMATE_LEARNING_ENGINE.py daily")
    print("      → Target: Gen 400+ with >90% win rate")
    print("   ")
    print("   2. Chart Analysis:")
    print("      → Obtain GLM-4-Flash API key")
    print("      → Run analyze_paper_trading_charts.py")
    print("      → Expand pattern library to 2,000+ patterns")
    print("   ")
    print("   3. Visual API Integration:")
    print("      → Add ZHIPUAI_API_KEY to .env")
    print("      → Unlock advanced chart analysis")
    print("      → Cost: ~$0.06 for 32 charts")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("   • Session will run for exactly 7 days")
    print("   • Check daily reports: prometheus_active_report_*.json")
    print("   • Monitor Windows Task Manager for health")
    print("   • Keep IB Gateway running on port 4002")
    print("   • Ensure stable internet connection")
    
    print("\n" + "="*70)
    print("🚀 STARTING 7-DAY AUTONOMOUS TRADING SESSION...")
    print("="*70 + "\n")


async def main():
    """Main week-long trading loop"""
    display_config()
    
    # Configuration
    TOTAL_DURATION_DAYS = 7
    SESSION_DURATION_HOURS = 8  # Run 8-hour sessions
    
    total_minutes = TOTAL_DURATION_DAYS * 24 * 60
    session_minutes = SESSION_DURATION_HOURS * 60
    
    print("🚀 LAUNCHING WEEK-LONG AUTONOMOUS TRADING...")
    print(f"⏱️  Total Duration: {TOTAL_DURATION_DAYS} days")
    print(f"🔄 Session Length: {SESSION_DURATION_HOURS} hours each")
    print(f"📊 Expected Sessions: {total_minutes // session_minutes}")
    
    start_time = datetime.now()
    end_time = start_time + timedelta(days=TOTAL_DURATION_DAYS)
    session_count = 0
    total_trades = 0
    total_pnl = 0.0
    
    print(f"\n⏰ Week-long session: {start_time.strftime('%Y-%m-%d %H:%M:%S')} → {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    while datetime.now() < end_time:
        session_count += 1
        elapsed_hours = (datetime.now() - start_time).total_seconds() / 3600
        remaining_hours = (end_time - datetime.now()).total_seconds() / 3600
        
        print("\n" + "="*70)
        print(f"  🔄 SESSION {session_count}")
        print(f"  Elapsed: {elapsed_hours:.1f} hours ({elapsed_hours/24:.1f} days)")
        print(f"  Remaining: {remaining_hours:.1f} hours ({remaining_hours/24:.1f} days)")
        print(f"  Total Trades So Far: {total_trades}")
        print(f"  Cumulative P&L: ${total_pnl:.2f}")
        print("="*70 + "\n")
        
        try:
            # Run trading session
            session = PrometheusActiveTradingSession()
            
            # Calculate remaining time for this session
            max_session_minutes = min(session_minutes, (end_time - datetime.now()).total_seconds() / 60)
            
            if max_session_minutes <= 0:
                print("⏰ Week-long duration reached!")
                break
            
            print(f"▶️  Running {max_session_minutes/60:.1f}-hour session...")
            report = await session.run_session(duration_minutes=int(max_session_minutes))
            
            # Update cumulative stats
            session_trades = report['trading_activity']['trades_executed']
            session_pnl = report['capital_info']['total_pnl']
            total_trades += session_trades
            total_pnl += session_pnl
            
            print(f"\n✅ SESSION {session_count} COMPLETE")
            print(f"   Trades: {session_trades}")
            print(f"   P&L: ${session_pnl:.2f}")
            print(f"   Duration: {report['session_info']['session_duration_minutes']:.1f} minutes")
            
            # Check if we should continue
            if datetime.now() >= end_time:
                break
            
            # Brief pause between sessions (5 minutes)
            if datetime.now() < end_time:
                print("\n⏸️  5-minute break between sessions...")
                await asyncio.sleep(300)  # 5 minutes
        
        except KeyboardInterrupt:
            print("\n\n⚠️  User interrupted - stopping gracefully...")
            break
        except Exception as e:
            print(f"\n❌ Session {session_count} error: {e}")
            print("⏸️  Waiting 10 minutes before retry...")
            await asyncio.sleep(600)  # Wait 10 minutes on error
    
    # Final summary
    print("\n" + "="*70)
    print("  ✅ WEEK-LONG AUTONOMOUS TRADING COMPLETE")
    print("="*70)
    
    duration = datetime.now() - start_time
    print(f"\n📊 FINAL STATISTICS:")
    print(f"   ⏱️  Total Duration: {duration.total_seconds()/3600:.1f} hours ({duration.days} days)")
    print(f"   🔄 Sessions Completed: {session_count}")
    print(f"   📈 Total Trades: {total_trades}")
    print(f"   💰 Cumulative P&L: ${total_pnl:.2f}")
    print(f"   📊 Avg Trades/Day: {total_trades / max(1, duration.days):.1f}")
    
    if total_trades > 0:
        print(f"   💹 Avg P&L/Trade: ${total_pnl/total_trades:.2f}")
    
    print("\n📁 Review all reports: prometheus_active_report_*.json")
    print("🎓 Next steps:")
    print("   1. Analyze trade decisions and outcomes")
    print("   2. Run backend training to evolve strategies")
    print("   3. Analyze captured charts with GLM-4-Flash")
    print("   4. Update pattern library with new learnings")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n")
    print("╔" + "═"*68 + "╗")
    print("║" + " "*20 + "PROMETHEUS TRADING PLATFORM" + " "*21 + "║")
    print("║" + " "*22 + "Week-Long Autonomous Mode" + " "*20 + "║")
    print("╚" + "═"*68 + "╝")
    
    asyncio.run(main())
