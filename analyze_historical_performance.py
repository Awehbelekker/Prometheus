"""
Analyze historical trading performance from PROMETHEUS databases
Calculate actual returns, win rates, and compare to 6-9% daily target
"""

import sqlite3
import json
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_performance():
    """Analyze trading performance from prometheus_learning.db"""
    
    print("\n" + "="*80)
    print("📊 PROMETHEUS HISTORICAL PERFORMANCE ANALYSIS")
    print("="*80 + "\n")
    
    try:
        conn = sqlite3.connect("prometheus_learning.db")
        cursor = conn.cursor()
        
        # ========== TRADE HISTORY ANALYSIS ==========
        print("📈 TRADE HISTORY ANALYSIS")
        print("-" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM trade_history")
        total_trades = cursor.fetchone()[0]
        print(f"Total Trades: {total_trades}")
        
        # Get trades by action
        cursor.execute("""
            SELECT action, COUNT(*) 
            FROM trade_history 
            GROUP BY action
        """)
        actions = cursor.fetchall()
        for action, count in actions:
            print(f"  {action}: {count}")
        
        # Get trades by broker
        cursor.execute("""
            SELECT broker, COUNT(*) 
            FROM trade_history 
            GROUP BY broker
        """)
        brokers = cursor.fetchall()
        print(f"\nTrades by Broker:")
        for broker, count in brokers:
            print(f"  {broker}: {count}")
        
        # Get most traded symbols
        cursor.execute("""
            SELECT symbol, COUNT(*) as trade_count
            FROM trade_history 
            GROUP BY symbol
            ORDER BY trade_count DESC
            LIMIT 10
        """)
        symbols = cursor.fetchall()
        print(f"\nTop 10 Most Traded Symbols:")
        for symbol, count in symbols:
            print(f"  {symbol}: {count} trades")
        
        # Get date range
        cursor.execute("""
            SELECT MIN(timestamp), MAX(timestamp)
            FROM trade_history
        """)
        min_date, max_date = cursor.fetchone()
        print(f"\nTrading Period:")
        print(f"  First Trade: {min_date}")
        print(f"  Last Trade: {max_date}")
        
        if min_date and max_date:
            start = datetime.fromisoformat(min_date)
            end = datetime.fromisoformat(max_date)
            days = (end - start).days + 1
            print(f"  Duration: {days} days")
            print(f"  Avg Trades/Day: {total_trades / days:.1f}")
        
        # ========== PERFORMANCE METRICS ANALYSIS ==========
        print("\n" + "="*80)
        print("💰 PERFORMANCE METRICS ANALYSIS")
        print("-" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM performance_metrics")
        total_metrics = cursor.fetchone()[0]
        print(f"Total Performance Records: {total_metrics}")
        
        # Get latest performance metrics
        cursor.execute("""
            SELECT * FROM performance_metrics
            ORDER BY timestamp DESC
            LIMIT 1
        """)
        columns = [desc[0] for desc in cursor.description]
        latest = cursor.fetchone()
        
        if latest:
            metrics = dict(zip(columns, latest))
            print(f"\nLatest Performance Snapshot ({metrics.get('timestamp', 'N/A')}):")
            print(f"  Total Trades: {metrics.get('total_trades', 0)}")
            print(f"  Winning Trades: {metrics.get('winning_trades', 0)}")
            print(f"  Losing Trades: {metrics.get('losing_trades', 0)}")
            
            total = metrics.get('total_trades', 0)
            winning = metrics.get('winning_trades', 0)
            if total > 0:
                win_rate = (winning / total) * 100
                print(f"  Win Rate: {win_rate:.2f}%")
            
            # Check for P&L columns
            if 'total_pnl' in metrics:
                print(f"  Total P&L: ${metrics.get('total_pnl', 0):.2f}")
            if 'portfolio_value' in metrics:
                print(f"  Portfolio Value: ${metrics.get('portfolio_value', 0):.2f}")
            if 'return_pct' in metrics:
                print(f"  Return: {metrics.get('return_pct', 0):.2f}%")
        
        # Calculate average performance over time
        cursor.execute("""
            SELECT 
                AVG(CAST(winning_trades AS FLOAT) / NULLIF(total_trades, 0)) * 100 as avg_win_rate,
                COUNT(*) as snapshots
            FROM performance_metrics
            WHERE total_trades > 0
        """)
        avg_win_rate, snapshots = cursor.fetchone()
        if avg_win_rate:
            print(f"\nAverage Win Rate (across {snapshots} snapshots): {avg_win_rate:.2f}%")
        
        # ========== OPEN POSITIONS ANALYSIS ==========
        print("\n" + "="*80)
        print("📊 CURRENT OPEN POSITIONS")
        print("-" * 80)
        
        cursor.execute("SELECT COUNT(*) FROM open_positions")
        open_count = cursor.fetchone()[0]
        print(f"Total Open Positions: {open_count}")
        
        if open_count > 0:
            # First check what columns exist
            cursor.execute("PRAGMA table_info(open_positions)")
            columns_info = cursor.fetchall()
            col_names = [col[1] for col in columns_info]

            # Build query based on available columns
            base_cols = "symbol, side, quantity, entry_price"
            if "current_price" in col_names:
                base_cols += ", current_price"
            if "unrealized_pnl" in col_names:
                base_cols += ", unrealized_pnl"

            cursor.execute(f"SELECT {base_cols} FROM open_positions")
            positions = cursor.fetchall()
            print(f"\nPosition Details:")

            for pos in positions:
                symbol = pos[0]
                side = pos[1]
                qty = pos[2]
                entry = pos[3]

                if len(pos) > 4:
                    current = pos[4] if pos[4] else entry
                    if len(pos) > 5:
                        pnl = pos[5] if pos[5] else 0
                        print(f"  {symbol}: {side} {qty} @ ${entry:.2f} (Current: ${current:.2f}, P&L: ${pnl:.2f})")
                    else:
                        pnl_calc = (current - entry) * qty if side == "LONG" else (entry - current) * qty
                        print(f"  {symbol}: {side} {qty} @ ${entry:.2f} (Current: ${current:.2f}, Est P&L: ${pnl_calc:.2f})")
                else:
                    print(f"  {symbol}: {side} {qty} @ ${entry:.2f}")
        
        # ========== DAILY PERFORMANCE CALCULATION ==========
        print("\n" + "="*80)
        print("🎯 DAILY PERFORMANCE vs TARGET (6-9%)")
        print("-" * 80)
        
        # Try to calculate daily returns from performance_metrics
        cursor.execute("""
            SELECT timestamp, portfolio_value
            FROM performance_metrics
            WHERE portfolio_value IS NOT NULL
            ORDER BY timestamp
        """)
        portfolio_history = cursor.fetchall()
        
        if len(portfolio_history) >= 2:
            # Group by date
            daily_values = defaultdict(list)
            for ts, value in portfolio_history:
                date = ts.split('T')[0] if 'T' in ts else ts.split(' ')[0]
                daily_values[date].append(value)
            
            # Calculate daily returns
            dates = sorted(daily_values.keys())
            if len(dates) >= 2:
                print(f"\nDaily Returns Analysis:")
                daily_returns = []
                
                for i in range(1, min(len(dates), 8)):  # Show last 7 days
                    prev_date = dates[i-1]
                    curr_date = dates[i]
                    prev_value = daily_values[prev_date][-1]  # End of day value
                    curr_value = daily_values[curr_date][-1]
                    
                    if prev_value > 0:
                        daily_return = ((curr_value - prev_value) / prev_value) * 100
                        daily_returns.append(daily_return)
                        
                        status = "[CHECK]" if daily_return >= 6.0 else "[WARNING]️" if daily_return >= 3.0 else "[ERROR]"
                        print(f"  {curr_date}: {daily_return:+.2f}% {status}")
                
                if daily_returns:
                    avg_daily = sum(daily_returns) / len(daily_returns)
                    print(f"\nAverage Daily Return: {avg_daily:.2f}%")
                    
                    if avg_daily >= 6.0:
                        print(f"[CHECK] EXCEEDING TARGET: {avg_daily:.2f}% >= 6.0%")
                    elif avg_daily >= 3.0:
                        print(f"[WARNING]️ BELOW TARGET: {avg_daily:.2f}% < 6.0% (but positive)")
                    else:
                        print(f"[ERROR] SIGNIFICANTLY BELOW TARGET: {avg_daily:.2f}% << 6.0%")
        else:
            print("[WARNING]️ Insufficient portfolio value history to calculate daily returns")
        
        # ========== SUMMARY & RECOMMENDATIONS ==========
        print("\n" + "="*80)
        print("📋 SUMMARY & RECOMMENDATIONS")
        print("-" * 80)
        
        print(f"\n[CHECK] Strengths:")
        print(f"  • {total_trades} trades executed (extensive history)")
        print(f"  • {total_metrics} performance snapshots recorded")
        print(f"  • System has been actively trading")
        
        print(f"\n[WARNING]️ Areas for Improvement:")
        if avg_win_rate and avg_win_rate < 50:
            print(f"  • Win rate ({avg_win_rate:.1f}%) below 50% - review strategy selection")
        if open_count > 0:
            print(f"  • {open_count} open positions - monitor for exit opportunities")
        
        print(f"\n💡 Recommendations:")
        print(f"  1. Start new trading session to generate fresh performance data")
        print(f"  2. Monitor win rate and adjust strategies if below 50%")
        print(f"  3. Focus on achieving 6-9% daily return target")
        print(f"  4. Review most profitable symbols and strategies")
        print(f"  5. Ensure risk management parameters are optimal")
        
        conn.close()
        
        # Save summary to file
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "total_trades": total_trades,
            "total_metrics": total_metrics,
            "open_positions": open_count,
            "avg_win_rate": avg_win_rate if avg_win_rate else 0,
            "latest_timestamp": max_date if max_date else "N/A"
        }
        
        with open("performance_analysis_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Summary saved to: performance_analysis_summary.json")
        
    except Exception as e:
        print(f"[ERROR] Error analyzing performance: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("[CHECK] Analysis Complete")
    print("="*80 + "\n")

if __name__ == "__main__":
    analyze_performance()

