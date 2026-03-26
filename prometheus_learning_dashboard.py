"""
📊 PROMETHEUS LEARNING DASHBOARD
Comprehensive visualization and reporting for trade optimization

Features:
1. Top Trades Analysis with Optimization Insights
2. Pattern Recognition Summary
3. Exit Timing Analysis
4. Symbol Performance Heatmap
5. Learning Recommendations
"""

import sqlite3
import sys
from datetime import datetime
from typing import Dict, List
import json

# Configure UTF-8 for Windows
sys.stdout.reconfigure(encoding='utf-8')

from prometheus_learning_engine import PrometheusLearningEngine

class PrometheusLearningDashboard:
    """
    Interactive dashboard for visualizing learning insights
    """
    
    def __init__(self, db_path='prometheus_learning.db'):
        self.db_path = db_path
        self.engine = PrometheusLearningEngine(db_path)
    
    def display_top_trades(self, limit: int = 20):
        """Display top performing trades with optimization analysis"""
        print("\n" + "="*80)
        print("📈 TOP PERFORMING TRADES")
        print("="*80)
        
        trades = self.engine.get_top_trades_analysis(limit=limit)
        
        if not trades:
            print("❌ No closed trades found")
            return
        
        print(f"\n{'#':<4} {'Symbol':<12} {'Profit%':<10} {'Optimal%':<10} {'Missed%':<10} {'Exit Timing':<12} {'Hold (hrs)':<10}")
        print("-"*80)
        
        for i, trade in enumerate(trades, 1):
            profit_icon = "🟢" if trade['actual_profit_pct'] > 0 else "🔴"
            timing_icon = {
                'optimal': '🎯',
                'good': '👍',
                'early': '⏰',
                'too_early': '⚠️',
                'acceptable': '✓',
                'unknown': '?'
            }.get(trade['exit_timing'], '?')
            
            print(f"{i:<4} {trade['symbol']:<12} "
                  f"{profit_icon} {trade['actual_profit_pct']:>6.2f}%  "
                  f"{'🎯 ' + str(round(trade['optimal_profit_pct'], 2)) + '%':<12} "
                  f"{trade['missed_opportunity_pct']:>6.2f}%  "
                  f"{timing_icon} {trade['exit_timing']:<12} "
                  f"{trade['hold_hours']:>6.1f}")
        
        # Calculate summary stats
        avg_profit = sum(t['actual_profit_pct'] for t in trades) / len(trades)
        avg_optimal = sum(t['optimal_profit_pct'] for t in trades) / len(trades)
        avg_missed = sum(t['missed_opportunity_pct'] for t in trades) / len(trades)
        optimal_count = len([t for t in trades if t['exit_timing'] in ['optimal', 'good']])
        
        print("-"*80)
        print(f"\n📊 SUMMARY:")
        print(f"   Average Actual Profit:    {avg_profit:>6.2f}%")
        print(f"   Average Optimal Profit:   {avg_optimal:>6.2f}%")
        print(f"   Average Missed Profit:    {avg_missed:>6.2f}%")
        print(f"   Optimal Exits:            {optimal_count}/{len(trades)} ({optimal_count/len(trades)*100:.1f}%)")
    
    def display_patterns(self):
        """Display identified successful patterns"""
        print("\n" + "="*80)
        print("🧠 IDENTIFIED SUCCESSFUL PATTERNS")
        print("="*80)
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT pattern_type, success_rate, avg_profit_pct, trade_count,
                   best_symbols, conditions
            FROM pattern_insights
            ORDER BY success_rate DESC, avg_profit_pct DESC
            LIMIT 15
        """)
        
        patterns = cursor.fetchall()
        db.close()
        
        if not patterns:
            print("❌ No patterns identified yet")
            return
        
        for i, pattern in enumerate(patterns, 1):
            pattern_type, success_rate, avg_profit, count, symbols_json, conditions_json = pattern
            symbols = json.loads(symbols_json)[:3]  # Top 3 symbols
            
            print(f"\n{i}. {pattern_type}")
            print(f"   ✅ Success Rate:   {success_rate:>6.1f}%")
            print(f"   💰 Avg Profit:     {avg_profit:>6.2f}%")
            print(f"   📊 Trade Count:    {count}")
            print(f"   🎯 Best Symbols:   {', '.join(symbols)}")
    
    def display_exit_analysis(self):
        """Display exit timing analysis"""
        print("\n" + "="*80)
        print("⏰ EXIT TIMING ANALYSIS")
        print("="*80)
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        # Get exit timing distribution
        cursor.execute("""
            SELECT exit_timing, COUNT(*) as count,
                   AVG(actual_profit_pct) as avg_profit,
                   AVG(missed_opportunity_pct) as avg_missed
            FROM trade_optimization
            GROUP BY exit_timing
            ORDER BY count DESC
        """)
        
        timing_dist = cursor.fetchall()
        
        if not timing_dist:
            print("❌ No optimization data available yet")
            db.close()
            return
        
        print(f"\n{'Exit Timing':<15} {'Count':<10} {'Avg Profit%':<15} {'Avg Missed%':<15}")
        print("-"*80)
        
        for row in timing_dist:
            timing, count, avg_profit, avg_missed = row
            timing_icon = {
                'optimal': '🎯',
                'good': '👍',
                'early': '⏰',
                'too_early': '⚠️',
                'acceptable': '✓'
            }.get(timing, '?')
            
            print(f"{timing_icon} {timing:<13} {count:<10} {avg_profit:>10.2f}%     {avg_missed:>10.2f}%")
        
        # Calculate recommendations based on exit timing
        cursor.execute("""
            SELECT AVG(missed_opportunity_pct),
                   SUM(CASE WHEN exit_timing LIKE '%early%' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM trade_optimization
        """)
        
        result = cursor.fetchone()
        if result:
            avg_missed_total, early_pct = result
            
            print(f"\n💡 INSIGHTS:")
            if avg_missed_total > 5:
                print(f"   ⚠️  Average missed opportunity: {avg_missed_total:.1f}%")
                print(f"       Consider adjusting exit strategy or using trailing stops")
            
            if early_pct > 40:
                print(f"   ⏰ {early_pct:.0f}% of trades exited early")
                print(f"       Consider extending hold times or adjusting take-profit levels")
            
            if early_pct < 20 and avg_missed_total < 3:
                print(f"   ✅ Exit timing is well-optimized!")
                print(f"       Current strategy captures most potential profits")
        
        db.close()
    
    def display_symbol_performance(self):
        """Display symbol-by-symbol performance analysis"""
        print("\n" + "="*80)
        print("🎯 SYMBOL PERFORMANCE ANALYSIS")
        print("="*80)
        
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT symbol,
                   COUNT(*) as total_trades,
                   SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as win_rate,
                   AVG((exit_price - price) / price * 100) as avg_profit,
                   SUM(profit_loss) as total_profit,
                   AVG(hold_duration_seconds) / 3600 as avg_hold_hours
            FROM trade_history
            WHERE status = 'closed' AND exit_price IS NOT NULL
            GROUP BY symbol
            HAVING total_trades >= 2
            ORDER BY win_rate DESC, avg_profit DESC
            LIMIT 20
        """)
        
        symbols = cursor.fetchall()
        db.close()
        
        if not symbols:
            print("❌ No symbol data available yet")
            return
        
        print(f"\n{'Symbol':<12} {'Trades':<10} {'Win Rate':<12} {'Avg Profit%':<15} {'Total P&L':<12} {'Avg Hold (hrs)':<15}")
        print("-"*80)
        
        for row in symbols:
            symbol, trades, win_rate, avg_profit, total_pl, avg_hold = row
            
            # Determine performance rating
            if win_rate >= 70 and avg_profit >= 5:
                rating = "⭐⭐⭐"
            elif win_rate >= 60 and avg_profit >= 3:
                rating = "⭐⭐"
            elif win_rate >= 50:
                rating = "⭐"
            else:
                rating = "⚠️"
            
            profit_icon = "🟢" if avg_profit > 0 else "🔴"
            
            print(f"{rating} {symbol:<9} {trades:<10} {win_rate:>8.1f}%    "
                  f"{profit_icon} {avg_profit:>8.2f}%      "
                  f"${total_pl:>8.2f}   {avg_hold:>8.1f}")
    
    def display_recommendations(self):
        """Display actionable recommendations"""
        print("\n" + "="*80)
        print("💡 LEARNING RECOMMENDATIONS")
        print("="*80)
        
        recommendations = self.engine.get_learning_recommendations()
        
        if not recommendations.get('action_items'):
            print("❌ No recommendations available yet")
            return
        
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎯 ACTION ITEMS:")
        
        for i, item in enumerate(recommendations['action_items'], 1):
            print(f"\n{i}. {item}")
        
        # Display insights summary
        if recommendations.get('insights'):
            print("\n\n📊 KEY INSIGHTS:")
            for insight in recommendations['insights'][:5]:
                print(f"\n   Pattern: {insight['pattern']}")
                print(f"   Success Rate: {insight['success_rate']}")
                print(f"   Avg Profit: {insight['avg_profit']}")
                print(f"   Trades: {insight['trades']}")
    
    def display_full_report(self):
        """Display complete learning dashboard"""
        print("\n" + "="*80)
        print("🚀 PROMETHEUS LEARNING DASHBOARD")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.display_top_trades(limit=15)
        self.display_patterns()
        self.display_exit_analysis()
        self.display_symbol_performance()
        self.display_recommendations()
        
        print("\n" + "="*80)
        print("✅ Dashboard Complete")
        print("="*80)


def main():
    """Main function to run the dashboard"""
    dashboard = PrometheusLearningDashboard()
    
    print("\n🧠 PROMETHEUS LEARNING DASHBOARD")
    print("="*80)
    print("\nSelect an option:")
    print("  1. Full Report (All Sections)")
    print("  2. Top Trades Analysis")
    print("  3. Pattern Recognition")
    print("  4. Exit Timing Analysis")
    print("  5. Symbol Performance")
    print("  6. Recommendations Only")
    print("  7. Run Learning Analysis (Analyze Closed Trades)")
    print("\n  0. Exit")
    
    while True:
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            dashboard.display_full_report()
        elif choice == '2':
            dashboard.display_top_trades(limit=20)
        elif choice == '3':
            dashboard.display_patterns()
        elif choice == '4':
            dashboard.display_exit_analysis()
        elif choice == '5':
            dashboard.display_symbol_performance()
        elif choice == '6':
            dashboard.display_recommendations()
        elif choice == '7':
            print("\n🔍 Running learning analysis on closed trades...")
            print("This may take several minutes for the first run...")
            
            # First identify patterns
            patterns = dashboard.engine.identify_successful_patterns(min_profit_pct=3.0)
            print(f"✅ Identified {len(patterns)} patterns")
            
            # Then analyze optimization
            summary = dashboard.engine.analyze_all_closed_trades(limit=50)
            print(f"\n✅ Analysis complete!")
            print(f"   Analyzed: {summary.get('total_analyzed', 0)} trades")
            print(f"   Optimal exits: {summary.get('optimal_exits', 0)}")
            print(f"   Avg missed opportunity: {summary.get('avg_missed_opportunity_pct', 0):.2f}%")
        else:
            print("❌ Invalid choice. Please enter 0-7.")


if __name__ == '__main__':
    main()
