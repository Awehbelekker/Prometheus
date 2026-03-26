#!/usr/bin/env python3
"""
Analyze Alpaca Trading Losses
Identify what's going wrong and provide actionable fixes
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def analyze_alpaca_performance():
    """Comprehensive analysis of Alpaca trading performance"""
    
    try:
        conn = sqlite3.connect('prometheus_trading.db')
        cursor = conn.cursor()
        
        print("=" * 80)
        print("🔍 ALPACA TRADING PERFORMANCE ANALYSIS")
        print("=" * 80)
        
        # 1. Overall Performance (Last 7 Days)
        print("\n📊 OVERALL PERFORMANCE (Last 7 Days):")
        print("-" * 80)
        
        cursor.execute("""
            SELECT
                COUNT(*) as total_trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losses,
                MAX(pnl) as best_trade,
                MIN(pnl) as worst_trade
            FROM trade_history
            WHERE broker = 'alpaca'
            AND timestamp > datetime('now', '-7 days')
        """)
        
        row = cursor.fetchone()
        if row and row[0] > 0:
            total_trades, total_pnl, avg_pnl, wins, losses, best_trade, worst_trade = row
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
            
            print(f"Total Trades: {total_trades}")
            print(f"Total P&L: ${total_pnl:.2f}")
            print(f"Average P&L per Trade: ${avg_pnl:.2f}")
            print(f"Win Rate: {win_rate:.1f}% ({wins} wins, {losses} losses)")
            print(f"Best Trade: ${best_trade:.2f}")
            print(f"Worst Trade: ${worst_trade:.2f}")
            
            # Determine if it's critical
            if total_pnl < -50:
                print(f"\n[WARNING]️  CRITICAL: Losing ${abs(total_pnl):.2f} - Immediate action needed!")
            elif total_pnl < 0:
                print(f"\n[WARNING]️  WARNING: Losing ${abs(total_pnl):.2f} - Part of learning process")
            else:
                print(f"\n[CHECK] PROFITABLE: Making ${total_pnl:.2f}")
        else:
            print("No Alpaca trades found in last 7 days")
            conn.close()
            return
        
        # 2. Worst Performing Symbols
        print("\n\n📉 WORST PERFORMING SYMBOLS:")
        print("-" * 80)
        print(f"{'Symbol':<10} {'Trades':<10} {'Total P&L':<15} {'Avg P&L':<15} {'Win Rate':<10}")
        print("-" * 80)
        
        cursor.execute("""
            SELECT
                symbol,
                COUNT(*) as trades,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
            FROM trade_history
            WHERE broker = 'alpaca'
            AND timestamp > datetime('now', '-7 days')
            GROUP BY symbol
            ORDER BY total_pnl ASC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            symbol, trades, total_pnl, avg_pnl, win_rate = row
            print(f"{symbol:<10} {trades:<10} ${total_pnl:<14.2f} ${avg_pnl:<14.2f} {win_rate:<9.1f}%")
        
        # 3. Most Common Losing Patterns
        print("\n\n🔴 MOST COMMON LOSING TRADE PATTERNS:")
        print("-" * 80)
        print(f"{'Entry Reason':<25} {'Exit Reason':<25} {'Count':<10} {'Avg Loss':<10}")
        print("-" * 80)
        
        cursor.execute("""
            SELECT
                reason as entry_reason,
                'N/A' as exit_reason,
                COUNT(*) as count,
                AVG(pnl) as avg_loss
            FROM trade_history
            WHERE broker = 'alpaca'
            AND timestamp > datetime('now', '-7 days')
            AND pnl < 0
            GROUP BY reason
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            entry, exit_reason, count, avg_loss = row
            entry_short = (entry or 'Unknown')[:24]
            exit_short = (exit_reason or 'Unknown')[:24]
            print(f"{entry_short:<25} {exit_short:<25} {count:<10} ${avg_loss:<9.2f}")
        
        # 4. Time-based Analysis
        print("\n\n⏰ PERFORMANCE BY TIME OF DAY:")
        print("-" * 80)
        print(f"{'Hour (ET)':<15} {'Trades':<10} {'Total P&L':<15} {'Win Rate':<10}")
        print("-" * 80)
        
        cursor.execute("""
            SELECT
                CAST(strftime('%H', timestamp) AS INTEGER) as hour,
                COUNT(*) as trades,
                SUM(pnl) as total_pnl,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate
            FROM trade_history
            WHERE broker = 'alpaca'
            AND timestamp > datetime('now', '-7 days')
            GROUP BY hour
            ORDER BY total_pnl ASC
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            hour, trades, total_pnl, win_rate = row
            print(f"{hour:02d}:00-{hour:02d}:59 ET  {trades:<10} ${total_pnl:<14.2f} {win_rate:<9.1f}%")
        
        # 5. Current Strategy Parameters
        print("\n\n⚙️  CURRENT STRATEGY PARAMETERS:")
        print("-" * 80)
        print("Stop Loss: 2-5% (volatility-adjusted)")
        print("Take Profit: 5-12.5% (2.5:1 risk-reward)")
        print("Position Size: 15% max per position")
        print("Max Daily Risk: 3%")
        print("Max Drawdown: 10%")
        
        # 6. Root Cause Analysis
        print("\n\n🔍 ROOT CAUSE ANALYSIS:")
        print("-" * 80)
        
        # Check if stop losses are too tight
        cursor.execute("""
            SELECT COUNT(*)
            FROM trade_history
            WHERE broker = 'alpaca'
            AND timestamp > datetime('now', '-7 days')
            AND reason LIKE '%stop loss%'
            AND pnl < 0
        """)
        stop_loss_count = cursor.fetchone()[0]

        # Note: trade_history doesn't have exit_time, so we'll skip hold time analysis
        avg_losing_hold_time = None
        avg_winning_hold_time = None
        
        issues_found = []
        
        if stop_loss_count > total_trades * 0.4:
            issues_found.append(f"[ERROR] TOO MANY STOP LOSSES: {stop_loss_count}/{total_trades} trades ({stop_loss_count/total_trades*100:.1f}%)")
            issues_found.append("   → Stop losses may be too tight for current market volatility")
        
        if avg_losing_hold_time and avg_losing_hold_time > 12:
            issues_found.append(f"[ERROR] HOLDING LOSERS TOO LONG: Average {avg_losing_hold_time:.1f} hours")
            issues_found.append("   → Need faster exit on losing trades")
        
        if avg_winning_hold_time and avg_losing_hold_time and avg_winning_hold_time < avg_losing_hold_time:
            issues_found.append(f"[ERROR] CUTTING WINNERS TOO EARLY: Winners held {avg_winning_hold_time:.1f}h vs Losers {avg_losing_hold_time:.1f}h")
            issues_found.append("   → Let winners run longer, cut losers faster")
        
        if win_rate < 50:
            issues_found.append(f"[ERROR] LOW WIN RATE: {win_rate:.1f}% (target: 60%+)")
            issues_found.append("   → Entry signals may need refinement")
        
        if avg_pnl < 0:
            issues_found.append(f"[ERROR] NEGATIVE AVERAGE P&L: ${avg_pnl:.2f} per trade")
            issues_found.append("   → Risk/reward ratio needs adjustment")
        
        if issues_found:
            for issue in issues_found:
                print(issue)
        else:
            print("[CHECK] No major issues detected - losses are within normal learning parameters")
        
        # 7. Recommendations
        print("\n\n💡 ACTIONABLE RECOMMENDATIONS:")
        print("-" * 80)
        
        recommendations = []
        
        if stop_loss_count > total_trades * 0.4:
            recommendations.append("1. WIDEN STOP LOSSES: Increase from 2% to 3-4% to account for volatility")
        
        if win_rate < 50:
            recommendations.append("2. IMPROVE ENTRY SIGNALS: Wait for stronger confirmation before entering")
        
        if avg_pnl < 0:
            recommendations.append("3. ADJUST RISK/REWARD: Increase take-profit targets to 3:1 or 4:1")
        
        if avg_winning_hold_time and avg_losing_hold_time and avg_winning_hold_time < avg_losing_hold_time:
            recommendations.append("4. LET WINNERS RUN: Use trailing stops instead of fixed take-profit")
            recommendations.append("5. CUT LOSERS FASTER: Reduce stop-loss time from 24h to 12h")
        
        recommendations.append("6. REDUCE POSITION SIZE: Temporarily reduce to 10% while system learns")
        recommendations.append("7. FOCUS ON HIGH-CONFIDENCE TRADES: Only trade when confidence > 75%")
        recommendations.append("8. AVOID WORST PERFORMING TIMES: Skip trading during identified losing hours")
        
        for rec in recommendations:
            print(rec)
        
        # 8. Is This Critical?
        print("\n\n🎯 VERDICT:")
        print("=" * 80)
        
        if total_pnl < -100:
            print("🚨 CRITICAL: STOP TRADING IMMEDIATELY")
            print("   Losses exceed acceptable learning threshold")
            print("   Action: Pause trading, implement fixes, restart with smaller positions")
        elif total_pnl < -50:
            print("[WARNING]️  SERIOUS: Immediate adjustments needed")
            print("   Losses are significant but within learning parameters")
            print("   Action: Implement recommendations above, reduce position sizes")
        elif total_pnl < 0:
            print("[WARNING]️  NORMAL LEARNING PROCESS")
            print("   Small losses are expected during initial learning phase")
            print("   Action: Continue trading, system is learning and adapting")
            print(f"   Expected: System needs 50-100 trades to optimize (currently: {total_trades})")
        else:
            print("[CHECK] PROFITABLE: System is performing well!")
            print(f"   Current profit: ${total_pnl:.2f}")
            print("   Action: Continue current strategy")
        
        print("\n" + "=" * 80)
        
        conn.close()
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    analyze_alpaca_performance()

