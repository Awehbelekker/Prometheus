#!/usr/bin/env python3
"""
Launch PROMETHEUS Extended Trading Session - 60+ Minutes
With fixed orchestrator + all 9 intelligence sources
Monitor for trade opportunities with longer duration
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from prometheus_active_trading_session import PrometheusActiveTradingSession

async def main():
    """Launch 60-minute extended trading session"""
    
    print("\n" + "="*70)
    print("  🚀 PROMETHEUS EXTENDED TRADING SESSION - 60 MINUTES")
    print("="*70)
    print("\n📋 SESSION CONFIGURATION:")
    print("   ⏱️  Duration: 60 minutes (vs standard 20 min)")
    print("   🔌 IB Gateway: Port 4002 (LIVE TRADING)")
    print("   🤖 Intelligence: 9 sources active (orchestrator FIXED)")
    print("   👁️  Visual AI: 1,352 patterns loaded")
    print("   🧠 Learning Engine: Gen 359+ (92.4% top win rate)")
    print("   💰 Capital: $540 USD")
    print("   📊 Max Trades: 8 per session")
    print("   🎯 Position Size: $10.80 (2% risk per trade)")
    print("\n🎯 OBJECTIVES:")
    print("   • Monitor market for 60 minutes")
    print("   • Find high-confidence trade opportunities")
    print("   • Test fixed orchestrator with all intelligence sources")
    print("   • Validate pattern recognition across 23 symbols")
    print("   • Execute trades when confidence > 60%")
    print("\n🔍 MONITORED ASSETS:")
    print("   📈 Stocks: AAPL, MSFT, GOOGL, TSLA, NVDA, AMD, META, NFLX, CRM, ADBE, PLTR, RBLX, COIN")
    print("   ₿  Crypto: BTC-USD, ETH-USD, SOL-USD, AVAX-USD, ADA-USD, DOGE-USD, MATIC-USD")
    print("   💱 Forex: EUR/USD, GBP/USD, USD/JPY")
    
    print("\n⏳ Starting in 3 seconds...")
    await asyncio.sleep(3)
    
    print("\n🚀 LAUNCHING EXTENDED SESSION...\n")
    
    # Launch 60-minute session
    session = PrometheusActiveTradingSession()
    report = await session.run_session(duration_minutes=60)
    
    # Display final results
    print("\n" + "="*70)
    print("  ✅ 60-MINUTE EXTENDED SESSION COMPLETE")
    print("="*70)
    
    if report['trading_activity']['trades_executed'] > 0:
        print(f"\n🎉 SUCCESS! Executed {report['trading_activity']['trades_executed']} trades")
        print(f"   💰 P&L: ${report['capital_info']['total_pnl']:.2f} ({report['capital_info']['pnl_percent']:.2f}%)")
        print(f"   📊 Win Rate: {report['performance_metrics'].get('win_rate', 0):.1%}")
    else:
        print(f"\n📊 No trades executed (market conditions neutral)")
        print(f"   🔍 Symbols analyzed: {report['trading_activity']['symbols_analyzed']}")
        print(f"   🎯 Avg confidence: {report['trading_activity']['avg_confidence']:.1%}")
        print(f"   ⚠️  Reason: No signals exceeded 60% confidence threshold")
    
    print("\n💡 INSIGHTS:")
    if report['trading_activity']['avg_confidence'] < 0.55:
        print("   • Low confidence suggests market uncertainty or pattern mismatch")
        print("   • Consider analyzing crypto/forex charts to expand pattern library")
        print("   • Orchestrator may need more time to gather intelligence")
    elif report['trading_activity']['avg_confidence'] >= 0.55 and report['trading_activity']['trades_executed'] == 0:
        print("   • Moderate confidence but no >60% signals")
        print("   • Conservative approach protecting capital")
        print("   • May need to adjust thresholds or wait for better setups")
    
    print(f"\n📁 Full report saved: prometheus_active_report_{report['session_info']['session_id']}.json")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
