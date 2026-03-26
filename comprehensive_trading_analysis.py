#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE PROMETHEUS TRADING ANALYSIS
Analyze trade authenticity, performance gaps, and system effectiveness
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import statistics

class PrometheusTradeAnalyzer:
    def __init__(self, report_file: str):
        self.report_file = report_file
        self.data = None
        self.trades_df = None
        self.load_data()
    
    def load_data(self):
        """Load trading session data"""
        try:
            with open(self.report_file, 'r') as f:
                self.data = json.load(f)
            
            # Convert trades to DataFrame for analysis
            if 'trades' in self.data:
                self.trades_df = pd.DataFrame(self.data['trades'])
                self.trades_df['timestamp'] = pd.to_datetime(self.trades_df['timestamp'])
                print(f"[CHECK] Loaded {len(self.trades_df)} trades from {self.report_file}")
            else:
                print("[ERROR] No trades data found in report")
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
    
    def analyze_data_authenticity(self) -> Dict[str, Any]:
        """1. Trade Data Authenticity Analysis"""
        print("\n🔍 TRADE DATA AUTHENTICITY ANALYSIS")
        print("=" * 60)
        
        authenticity_results = {
            "total_trades": len(self.trades_df),
            "real_data_trades": 0,
            "simulated_data_trades": 0,
            "weekend_trades": 0,
            "after_hours_trades": 0,
            "suspicious_patterns": [],
            "data_sources": {},
            "price_authenticity": {}
        }
        
        # Check real_data flags
        real_data_count = self.trades_df['real_data'].sum() if 'real_data' in self.trades_df.columns else 0
        authenticity_results["real_data_trades"] = real_data_count
        authenticity_results["simulated_data_trades"] = len(self.trades_df) - real_data_count
        
        # Check trading times
        for _, trade in self.trades_df.iterrows():
            trade_time = trade['timestamp']
            
            # Weekend trading check
            if trade_time.weekday() >= 5:  # Saturday = 5, Sunday = 6
                authenticity_results["weekend_trades"] += 1
            
            # After hours trading check (before 9:30 AM or after 4:00 PM ET)
            trade_hour = trade_time.hour
            if trade_hour < 9 or (trade_hour == 9 and trade_time.minute < 30) or trade_hour >= 16:
                authenticity_results["after_hours_trades"] += 1
        
        # Analyze price patterns for simulation indicators
        execution_prices = self.trades_df['execution_price'].values
        current_prices = self.trades_df['current_price'].values
        
        # Check for hash-based or algorithmic price patterns
        price_diffs = np.diff(execution_prices)
        if len(price_diffs) > 10:
            # Look for suspiciously regular patterns
            price_variance = np.var(price_diffs)
            price_mean = np.mean(price_diffs)
            
            authenticity_results["price_authenticity"] = {
                "price_variance": float(price_variance),
                "price_mean": float(price_mean),
                "suspicious_regularity": price_variance < 0.01  # Very low variance suggests simulation
            }
        
        # Check for identical slippage across all trades (simulation indicator)
        if 'slippage' in self.trades_df.columns:
            unique_slippages = self.trades_df['slippage'].nunique()
            if unique_slippages == 1:
                authenticity_results["suspicious_patterns"].append("Identical slippage across all trades")
        
        # Print results
        print(f"📊 Total Trades: {authenticity_results['total_trades']}")
        print(f"[CHECK] Real Data Trades: {authenticity_results['real_data_trades']} ({authenticity_results['real_data_trades']/authenticity_results['total_trades']*100:.1f}%)")
        print(f"🎭 Simulated Data Trades: {authenticity_results['simulated_data_trades']} ({authenticity_results['simulated_data_trades']/authenticity_results['total_trades']*100:.1f}%)")
        print(f"📅 Weekend Trades: {authenticity_results['weekend_trades']}")
        print(f"🕐 After-Hours Trades: {authenticity_results['after_hours_trades']}")
        
        if authenticity_results["suspicious_patterns"]:
            print(f"[WARNING]️ Suspicious Patterns: {', '.join(authenticity_results['suspicious_patterns'])}")
        
        return authenticity_results
    
    def analyze_performance_gap(self) -> Dict[str, Any]:
        """2. Performance Gap Investigation"""
        print("\n📈 PERFORMANCE GAP INVESTIGATION")
        print("=" * 60)
        
        session_summary = self.data.get('session_summary', {})
        
        performance_analysis = {
            "actual_performance": {
                "total_return": session_summary.get('total_return', 0) * 100,
                "daily_return_rate": session_summary.get('daily_return_rate', 0) * 100,
                "duration_hours": session_summary.get('duration_hours', 0),
                "total_pnl": session_summary.get('total_pnl', 0),
                "max_drawdown": session_summary.get('max_drawdown', 0) * 100
            },
            "target_performance": {
                "daily_target_min": 6.0,  # 6% daily target
                "daily_target_max": 9.0,  # 9% daily target
                "72h_target_min": 18.0,   # 18% for 72 hours
                "72h_target_max": 27.0    # 27% for 72 hours
            },
            "performance_gaps": {},
            "underperformance_factors": []
        }
        
        actual_daily = performance_analysis["actual_performance"]["daily_return_rate"]
        actual_total = performance_analysis["actual_performance"]["total_return"]
        
        # Calculate performance gaps
        daily_gap_min = performance_analysis["target_performance"]["daily_target_min"] - actual_daily
        daily_gap_max = performance_analysis["target_performance"]["daily_target_max"] - actual_daily
        total_gap_min = performance_analysis["target_performance"]["72h_target_min"] - actual_total
        total_gap_max = performance_analysis["target_performance"]["72h_target_max"] - actual_total
        
        performance_analysis["performance_gaps"] = {
            "daily_shortfall_min": max(0, daily_gap_min),
            "daily_shortfall_max": max(0, daily_gap_max),
            "total_shortfall_min": max(0, total_gap_min),
            "total_shortfall_max": max(0, total_gap_max)
        }
        
        # Identify underperformance factors
        if actual_daily < 6.0:
            performance_analysis["underperformance_factors"].append("Daily returns below 6% target")
        
        if performance_analysis["actual_performance"]["max_drawdown"] > 5.0:
            performance_analysis["underperformance_factors"].append("High drawdown indicates poor risk management")
        
        # Analyze trade frequency and size
        avg_trade_size = self.trades_df['size'].mean() if 'size' in self.trades_df.columns else 0
        total_capital = session_summary.get('starting_capital', 5000)
        avg_position_size_pct = (avg_trade_size / total_capital) * 100
        
        if avg_position_size_pct < 2.0:
            performance_analysis["underperformance_factors"].append("Position sizes too small for meaningful returns")
        
        # Print results
        print(f"🎯 Target Daily Return: {performance_analysis['target_performance']['daily_target_min']}-{performance_analysis['target_performance']['daily_target_max']}%")
        print(f"📊 Actual Daily Return: {actual_daily:.2f}%")
        print(f"📉 Daily Shortfall: {performance_analysis['performance_gaps']['daily_shortfall_min']:.2f}-{performance_analysis['performance_gaps']['daily_shortfall_max']:.2f}%")
        print(f"🎯 Target 72h Return: {performance_analysis['target_performance']['72h_target_min']}-{performance_analysis['target_performance']['72h_target_max']}%")
        print(f"📊 Actual 72h Return: {actual_total:.2f}%")
        print(f"📉 Total Shortfall: {performance_analysis['performance_gaps']['total_shortfall_min']:.2f}-{performance_analysis['performance_gaps']['total_shortfall_max']:.2f}%")
        
        if performance_analysis["underperformance_factors"]:
            print(f"\n[WARNING]️ Underperformance Factors:")
            for factor in performance_analysis["underperformance_factors"]:
                print(f"   • {factor}")
        
        return performance_analysis
    
    def analyze_strategy_effectiveness(self) -> Dict[str, Any]:
        """3. Trading Strategy Effectiveness"""
        print("\n[LIGHTNING] TRADING STRATEGY EFFECTIVENESS")
        print("=" * 60)
        
        strategy_analysis = {
            "engine_performance": {},
            "win_rate_analysis": {},
            "trade_timing": {},
            "position_sizing": {},
            "market_conditions": {}
        }
        
        # Analyze performance by engine type
        if 'engine' in self.trades_df.columns:
            engine_performance = {}
            for engine in self.trades_df['engine'].unique():
                engine_trades = self.trades_df[self.trades_df['engine'] == engine]
                engine_pnl = engine_trades['pnl'].sum() if 'pnl' in engine_trades.columns else 0
                engine_performance[engine] = {
                    "trades": len(engine_trades),
                    "total_pnl": float(engine_pnl),
                    "avg_pnl_per_trade": float(engine_pnl / len(engine_trades)) if len(engine_trades) > 0 else 0,
                    "win_rate": float((engine_trades['pnl'] > 0).sum() / len(engine_trades) * 100) if 'pnl' in engine_trades.columns else 0
                }
            strategy_analysis["engine_performance"] = engine_performance
        
        # Overall win rate analysis
        if 'pnl' in self.trades_df.columns:
            winning_trades = (self.trades_df['pnl'] > 0).sum()
            total_trades = len(self.trades_df)
            win_rate = (winning_trades / total_trades) * 100
            
            strategy_analysis["win_rate_analysis"] = {
                "overall_win_rate": float(win_rate),
                "winning_trades": int(winning_trades),
                "losing_trades": int(total_trades - winning_trades),
                "avg_win": float(self.trades_df[self.trades_df['pnl'] > 0]['pnl'].mean()) if winning_trades > 0 else 0,
                "avg_loss": float(self.trades_df[self.trades_df['pnl'] < 0]['pnl'].mean()) if (total_trades - winning_trades) > 0 else 0
            }
        
        # Trade timing analysis
        if 'timestamp' in self.trades_df.columns:
            self.trades_df['hour'] = self.trades_df['timestamp'].dt.hour
            hourly_performance = self.trades_df.groupby('hour')['pnl'].agg(['count', 'sum', 'mean']).to_dict()
            strategy_analysis["trade_timing"] = {
                "hourly_distribution": hourly_performance,
                "most_active_hour": int(self.trades_df['hour'].mode().iloc[0]) if len(self.trades_df) > 0 else 0
            }
        
        # Position sizing analysis
        if 'size' in self.trades_df.columns:
            strategy_analysis["position_sizing"] = {
                "avg_position_size": float(self.trades_df['size'].mean()),
                "min_position_size": float(self.trades_df['size'].min()),
                "max_position_size": float(self.trades_df['size'].max()),
                "position_size_std": float(self.trades_df['size'].std())
            }
        
        # Print results
        print("🏆 Engine Performance:")
        for engine, perf in strategy_analysis["engine_performance"].items():
            print(f"   {engine}: {perf['trades']} trades, ${perf['total_pnl']:.2f} PnL, {perf['win_rate']:.1f}% win rate")
        
        if strategy_analysis["win_rate_analysis"]:
            wr = strategy_analysis["win_rate_analysis"]
            print(f"\n📊 Overall Win Rate: {wr['overall_win_rate']:.1f}%")
            print(f"💰 Average Win: ${wr['avg_win']:.2f}")
            print(f"💸 Average Loss: ${wr['avg_loss']:.2f}")
        
        return strategy_analysis
    
    def generate_recommendations(self, authenticity: Dict, performance: Dict, strategy: Dict) -> List[str]:
        """5. System Performance Recommendations"""
        print("\n🎯 SYSTEM PERFORMANCE RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = []
        
        # Data authenticity recommendations
        if authenticity["simulated_data_trades"] > 0:
            recommendations.append("🚨 CRITICAL: Eliminate all simulated data - use only real market data for authentic results")
        
        if authenticity["weekend_trades"] > 0:
            recommendations.append("⏰ Implement proper market hours validation - no weekend trading with fake data")
        
        if authenticity["after_hours_trades"] > 0:
            recommendations.append("🕐 Restrict trading to market hours (9:30 AM - 4:00 PM ET) for realistic conditions")
        
        # Performance gap recommendations
        daily_shortfall = performance["performance_gaps"]["daily_shortfall_min"]
        if daily_shortfall > 0:
            recommendations.append(f"📈 Increase daily returns by {daily_shortfall:.1f}% to meet 6% daily target")
            
            if daily_shortfall > 3:
                recommendations.append("[LIGHTNING] Consider more aggressive position sizing or higher-frequency trading")
            
            if daily_shortfall > 5:
                recommendations.append("🔄 Fundamental strategy overhaul needed - current approach insufficient")
        
        # Strategy effectiveness recommendations
        if strategy["win_rate_analysis"]["overall_win_rate"] < 60:
            recommendations.append("🎯 Improve trade selection - win rate below 60% indicates poor entry signals")
        
        avg_position_pct = (strategy["position_sizing"]["avg_position_size"] / 5000) * 100
        if avg_position_pct < 3:
            recommendations.append("💪 Increase position sizes - current sizes too small for meaningful returns")
        
        # Engine-specific recommendations
        for engine, perf in strategy["engine_performance"].items():
            if perf["win_rate"] < 50:
                recommendations.append(f"[ERROR] Disable or fix {engine} engine - {perf['win_rate']:.1f}% win rate is unprofitable")
            elif perf["avg_pnl_per_trade"] < 1:
                recommendations.append(f"[WARNING]️ Optimize {engine} engine - average profit per trade too low")
        
        # Market data quality recommendations
        if "suspicious_regularity" in authenticity.get("price_authenticity", {}):
            if authenticity["price_authenticity"]["suspicious_regularity"]:
                recommendations.append("🔍 Price patterns suggest simulation - verify real market data integration")
        
        # Print recommendations
        for i, rec in enumerate(recommendations, 1):
            print(f"{i:2d}. {rec}")
        
        return recommendations

def main():
    """Main analysis function"""
    print("🔍 COMPREHENSIVE PROMETHEUS TRADING ANALYSIS")
    print("=" * 70)
    print(f"Analysis Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Analyzing trade authenticity, performance gaps, and system effectiveness")
    print("=" * 70)
    
    # Initialize analyzer
    analyzer = PrometheusTradeAnalyzer('revolutionary_session_report_revolutionary_20250905_010808.json')
    
    if analyzer.data is None:
        print("[ERROR] Failed to load trading data")
        return
    
    # Perform comprehensive analysis
    authenticity_results = analyzer.analyze_data_authenticity()
    performance_results = analyzer.analyze_performance_gap()
    strategy_results = analyzer.analyze_strategy_effectiveness()
    
    # Generate recommendations
    recommendations = analyzer.generate_recommendations(
        authenticity_results, 
        performance_results, 
        strategy_results
    )
    
    # Summary
    print("\n🎯 ANALYSIS SUMMARY")
    print("=" * 60)
    
    # Data authenticity verdict
    if authenticity_results["real_data_trades"] == authenticity_results["total_trades"]:
        print("[CHECK] DATA AUTHENTICITY: All trades use real market data")
    else:
        print(f"[ERROR] DATA AUTHENTICITY: {authenticity_results['simulated_data_trades']} trades use simulated data")
    
    # Performance verdict
    actual_daily = performance_results["actual_performance"]["daily_return_rate"]
    if actual_daily >= 6.0:
        print(f"[CHECK] PERFORMANCE: {actual_daily:.2f}% daily return meets target")
    else:
        print(f"[ERROR] PERFORMANCE: {actual_daily:.2f}% daily return below 6% target")
    
    # Strategy verdict
    overall_win_rate = strategy_results["win_rate_analysis"]["overall_win_rate"]
    if overall_win_rate >= 60:
        print(f"[CHECK] STRATEGY: {overall_win_rate:.1f}% win rate indicates effective trading")
    else:
        print(f"[ERROR] STRATEGY: {overall_win_rate:.1f}% win rate needs improvement")
    
    print(f"\n📋 TOTAL RECOMMENDATIONS: {len(recommendations)}")
    print("🚀 Implement these changes to achieve 6-9% daily returns with authentic market data")

if __name__ == "__main__":
    main()
