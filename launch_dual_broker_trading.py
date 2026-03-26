"""
PROMETHEUS DUAL BROKER AUTONOMOUS TRADING LAUNCHER
Runs simultaneous trading sessions on both IB Gateway and Alpaca
"""

import asyncio
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Set environment for live trading
os.environ['LIVE_TRADING_ENABLED'] = 'true'
os.environ['ALPACA_PAPER_TRADING'] = 'false'

print("\n" + "="*80)
print("  🚀 PROMETHEUS DUAL BROKER AUTONOMOUS TRADING")
print("  💰 FULL CAPITAL DEPLOYMENT: $374.06")
print("="*80)

print("\n📊 BROKER CONFIGURATION:")
print("   • IB Gateway (U21922116): $251.58 (67%)")
print("   • Alpaca Live API: $122.48 (33%)")
print("\n🎯 STRATEGY:")
print("   • Visual AI: 1,352 patterns")
print("   • Intelligence: 8 real-world sources")
print("   • Learning: Gen 359+ (92.4% win rate)")
print("   • Assets: Stocks, Crypto, Forex")

# Configuration
TOTAL_DURATION_DAYS = 7
SESSION_DURATION_HOURS = 8
BREAK_BETWEEN_SESSIONS_MINUTES = 5

total_hours = TOTAL_DURATION_DAYS * 24
expected_sessions = int(total_hours / SESSION_DURATION_HOURS)

print(f"\n⏱️  DURATION:")
print(f"   • Total: {TOTAL_DURATION_DAYS} days ({total_hours} hours)")
print(f"   • Session length: {SESSION_DURATION_HOURS} hours each")
print(f"   • Expected sessions: ~{expected_sessions} per broker")
print(f"   • Break between: {BREAK_BETWEEN_SESSIONS_MINUTES} minutes")

# Statistics tracking
stats = {
    'ib': {
        'sessions_completed': 0,
        'total_trades': 0,
        'total_pnl': 0,
        'errors': 0,
        'last_portfolio_value': 251.58
    },
    'alpaca': {
        'sessions_completed': 0,
        'total_trades': 0,
        'total_pnl': 0,
        'errors': 0,
        'last_portfolio_value': 122.48
    }
}

async def run_ib_session(session_num, duration_minutes):
    """Run IB Gateway trading session"""
    try:
        print(f"\n🔵 IB SESSION {session_num} STARTING...")
        print(f"   Account: U21922116 | Capital: ${stats['ib']['last_portfolio_value']:.2f}")
        
        # Import and run IB session
        from prometheus_active_trading_session import PrometheusActiveTradingSession
        
        session = PrometheusActiveTradingSession(
            capital=stats['ib']['last_portfolio_value'],
            use_ib=True
        )
        
        await session.run_session(duration_minutes=duration_minutes)
        
        # Get latest report
        reports = sorted(Path('.').glob('prometheus_active_report_*.json'), 
                        key=lambda p: p.stat().st_mtime, reverse=True)
        
        if reports:
            with open(reports[0], 'r') as f:
                report = json.load(f)
                
            stats['ib']['sessions_completed'] += 1
            stats['ib']['total_trades'] += report.get('trading_activity', {}).get('trades_executed', 0)
            stats['ib']['total_pnl'] += report.get('total_pnl', 0)
            stats['ib']['last_portfolio_value'] = report.get('final_portfolio_value', stats['ib']['last_portfolio_value'])
            
            print(f"\n✅ IB SESSION {session_num} COMPLETE")
            print(f"   Trades: {report.get('trading_activity', {}).get('trades_executed', 0)}")
            print(f"   P&L: ${report.get('total_pnl', 0):.2f}")
            print(f"   Portfolio: ${stats['ib']['last_portfolio_value']:.2f}")
        
        return True
        
    except Exception as e:
        stats['ib']['errors'] += 1
        print(f"\n❌ IB SESSION {session_num} ERROR: {str(e)[:200]}")
        return False

async def run_alpaca_session(session_num, duration_minutes):
    """Run Alpaca trading session"""
    try:
        print(f"\n🟢 ALPACA SESSION {session_num} STARTING...")
        print(f"   Capital: ${stats['alpaca']['last_portfolio_value']:.2f}")
        
        # Import and run Alpaca session
        from prometheus_active_trading_session import PrometheusActiveTradingSession
        
        session = PrometheusActiveTradingSession(
            capital=stats['alpaca']['last_portfolio_value'],
            use_ib=False  # Use Alpaca
        )
        
        await session.run_session(duration_minutes=duration_minutes)
        
        # Get latest report
        reports = sorted(Path('.').glob('prometheus_active_report_*.json'), 
                        key=lambda p: p.stat().st_mtime, reverse=True)
        
        if reports:
            with open(reports[0], 'r') as f:
                report = json.load(f)
                
            stats['alpaca']['sessions_completed'] += 1
            stats['alpaca']['total_trades'] += report.get('trading_activity', {}).get('trades_executed', 0)
            stats['alpaca']['total_pnl'] += report.get('total_pnl', 0)
            stats['alpaca']['last_portfolio_value'] = report.get('final_portfolio_value', stats['alpaca']['last_portfolio_value'])
            
            print(f"\n✅ ALPACA SESSION {session_num} COMPLETE")
            print(f"   Trades: {report.get('trading_activity', {}).get('trades_executed', 0)}")
            print(f"   P&L: ${report.get('total_pnl', 0):.2f}")
            print(f"   Portfolio: ${stats['alpaca']['last_portfolio_value']:.2f}")
        
        return True
        
    except Exception as e:
        stats['alpaca']['errors'] += 1
        print(f"\n❌ ALPACA SESSION {session_num} ERROR: {str(e)[:200]}")
        return False

async def run_dual_session(session_num):
    """Run both brokers simultaneously"""
    duration_minutes = SESSION_DURATION_HOURS * 60
    
    print(f"\n{'='*80}")
    print(f"  🔥 DUAL BROKER SESSION {session_num}")
    print(f"  Duration: {SESSION_DURATION_HOURS} hours ({duration_minutes} minutes)")
    print(f"{'='*80}")
    
    # Run both sessions in parallel
    ib_task = asyncio.create_task(run_ib_session(session_num, duration_minutes))
    alpaca_task = asyncio.create_task(run_alpaca_session(session_num, duration_minutes))
    
    # Wait for both to complete
    ib_result, alpaca_result = await asyncio.gather(ib_task, alpaca_task, return_exceptions=True)
    
    # Print session summary
    print(f"\n{'='*80}")
    print(f"  📊 SESSION {session_num} SUMMARY")
    print(f"{'='*80}")
    
    total_portfolio = stats['ib']['last_portfolio_value'] + stats['alpaca']['last_portfolio_value']
    total_pnl = stats['ib']['total_pnl'] + stats['alpaca']['total_pnl']
    total_trades = stats['ib']['total_trades'] + stats['alpaca']['total_trades']
    
    print(f"\n💰 COMBINED PORTFOLIO: ${total_portfolio:.2f}")
    print(f"   • IB: ${stats['ib']['last_portfolio_value']:.2f} (Trades: {stats['ib']['total_trades']})")
    print(f"   • Alpaca: ${stats['alpaca']['last_portfolio_value']:.2f} (Trades: {stats['alpaca']['total_trades']})")
    print(f"\n📈 TOTAL P&L: ${total_pnl:.2f} ({(total_pnl/374.06)*100:.2f}%)")
    print(f"📊 TOTAL TRADES: {total_trades}")
    print(f"❌ ERRORS: IB {stats['ib']['errors']} | Alpaca {stats['alpaca']['errors']}")

async def main():
    """Main dual broker trading loop"""
    start_time = datetime.now()
    end_time = start_time + timedelta(days=TOTAL_DURATION_DAYS)
    session_count = 0
    
    print(f"\n🚀 STARTING DUAL BROKER AUTONOMOUS TRADING")
    print(f"   Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Total Capital: $374.06")
    
    try:
        while datetime.now() < end_time:
            session_count += 1
            
            # Run dual session
            await run_dual_session(session_count)
            
            # Check if we should continue
            if datetime.now() >= end_time:
                break
            
            # Break between sessions
            print(f"\n⏸️  Break for {BREAK_BETWEEN_SESSIONS_MINUTES} minutes...")
            print(f"   Sessions completed: {session_count}/{expected_sessions}")
            
            remaining = end_time - datetime.now()
            remaining_hours = remaining.total_seconds() / 3600
            print(f"   Time remaining: {remaining_hours:.1f} hours")
            
            await asyncio.sleep(BREAK_BETWEEN_SESSIONS_MINUTES * 60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTED BY USER")
    except Exception as e:
        print(f"\n\n❌ CRITICAL ERROR: {str(e)}")
    
    # Final summary
    print("\n" + "="*80)
    print("  🏁 DUAL BROKER TRADING COMPLETE")
    print("="*80)
    
    duration = datetime.now() - start_time
    duration_hours = duration.total_seconds() / 3600
    
    print(f"\n⏱️  DURATION: {duration_hours:.1f} hours ({duration.days} days)")
    print(f"📊 SESSIONS: {session_count} dual sessions completed")
    
    print(f"\n💰 FINAL PORTFOLIO:")
    total_portfolio = stats['ib']['last_portfolio_value'] + stats['alpaca']['last_portfolio_value']
    print(f"   Total: ${total_portfolio:.2f}")
    print(f"   • IB: ${stats['ib']['last_portfolio_value']:.2f}")
    print(f"   • Alpaca: ${stats['alpaca']['last_portfolio_value']:.2f}")
    
    total_pnl = stats['ib']['total_pnl'] + stats['alpaca']['total_pnl']
    total_pnl_pct = (total_pnl / 374.06) * 100
    
    print(f"\n📈 TOTAL P&L: ${total_pnl:.2f} ({total_pnl_pct:+.2f}%)")
    print(f"   • IB: ${stats['ib']['total_pnl']:.2f}")
    print(f"   • Alpaca: ${stats['alpaca']['total_pnl']:.2f}")
    
    print(f"\n📊 TOTAL TRADES: {stats['ib']['total_trades'] + stats['alpaca']['total_trades']}")
    print(f"   • IB: {stats['ib']['total_trades']}")
    print(f"   • Alpaca: {stats['alpaca']['total_trades']}")
    
    print(f"\n❌ ERRORS:")
    print(f"   • IB: {stats['ib']['errors']}")
    print(f"   • Alpaca: {stats['alpaca']['errors']}")
    
    # Save final report
    final_report = {
        'start_time': start_time.isoformat(),
        'end_time': datetime.now().isoformat(),
        'duration_hours': duration_hours,
        'sessions_completed': session_count,
        'initial_capital': 374.06,
        'final_portfolio': total_portfolio,
        'total_pnl': total_pnl,
        'total_pnl_percent': total_pnl_pct,
        'brokers': stats
    }
    
    report_file = f"dual_broker_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(final_report, f, indent=2)
    
    print(f"\n💾 Final report saved: {report_file}")
    print("\n" + "="*80)
    print("  ✅ PROMETHEUS DUAL BROKER TRADING COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    print("\n⚡ Press Ctrl+C at any time to safely stop trading\n")
    asyncio.run(main())
