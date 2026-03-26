"""
PROMETHEUS Trading Platform - Monitor Optimization Performance
Real-time monitoring of optimization impact and progress to #1 ranking
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np

class OptimizationMonitor:
    """Monitor performance improvements from optimizations"""
    
    def __init__(self):
        self.baseline_score = 88.1
        self.target_score = 95.3
        self.baseline_metrics = {
            "win_rate": 68.4,
            "cagr": 15.8,
            "sharpe_ratio": 2.85,
            "max_drawdown": 8.9
        }
        self.target_metrics = {
            "win_rate": 73.8,
            "cagr": 19.2,
            "sharpe_ratio": 3.25,
            "max_drawdown": 6.2
        }
        
        self.performance_history = []
        self.load_history()
    
    def load_history(self):
        """Load historical performance data"""
        history_file = Path("optimization_performance_history.json")
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.performance_history = json.load(f)
            except:
                self.performance_history = []
    
    def save_history(self):
        """Save performance history"""
        history_file = Path("optimization_performance_history.json")
        with open(history_file, 'w') as f:
            json.dump(self.performance_history, f, indent=2)
    
    def get_current_performance(self):
        """Get current performance metrics (simulated for now)"""
        
        # Check for latest backtest or trading results
        result_files = [
            "10_YEAR_BACKTEST_RESULTS.json",
            "10_YEAR_REALISTIC_BACKTEST.json",
            "final_benchmark_results_20260114_140913.json"
        ]
        
        latest_metrics = None
        
        for result_file in result_files:
            path = Path(result_file)
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        
                        # Extract metrics from different file formats
                        if "performance" in data:
                            perf = data["performance"]
                            latest_metrics = {
                                "win_rate": perf.get("win_rate", 68.4),
                                "cagr": perf.get("cagr", 15.8),
                                "sharpe_ratio": perf.get("sharpe_ratio", 2.85),
                                "max_drawdown": abs(perf.get("max_drawdown", 8.9))
                            }
                            break
                        elif "benchmarks" in data:
                            benchmarks = data["benchmarks"]
                            if "trading_performance" in benchmarks:
                                tp = benchmarks["trading_performance"]
                                latest_metrics = {
                                    "win_rate": tp.get("win_rate", 68.4),
                                    "cagr": tp.get("cagr", 15.8),
                                    "sharpe_ratio": tp.get("sharpe_ratio", 2.85),
                                    "max_drawdown": abs(tp.get("max_drawdown", 8.9))
                                }
                                break
                except:
                    continue
        
        if not latest_metrics:
            # Use baseline metrics if no recent results found
            latest_metrics = self.baseline_metrics.copy()
        
        return latest_metrics
    
    def calculate_current_score(self, metrics):
        """Calculate overall score based on current metrics"""
        
        # Scoring weights (matching benchmark system)
        weights = {
            "win_rate": 0.15,
            "cagr": 0.15,
            "sharpe_ratio": 0.20,
            "max_drawdown": 0.10  # Lower is better for drawdown
        }
        
        # Normalize metrics to 0-100 scale
        normalized = {
            "win_rate": min(metrics["win_rate"] / 0.80 * 100, 100),  # 80% win rate = 100 points
            "cagr": min(metrics["cagr"] / 0.25 * 100, 100),  # 25% CAGR = 100 points
            "sharpe_ratio": min(metrics["sharpe_ratio"] / 4.0 * 100, 100),  # 4.0 Sharpe = 100 points
            "max_drawdown": max(100 - metrics["max_drawdown"] * 10, 0)  # Lower is better
        }
        
        # Calculate weighted score
        score = sum(normalized[key] * weights[key] for key in weights.keys())
        
        # Add base components (assuming they remain constant)
        score += 94.2 * 0.20  # AI Intelligence
        score += 95.0 * 0.10  # Multi-Exchange
        score += 96.0 * 0.05  # Order Execution
        score += 87.0 * 0.05  # Risk Management
        
        return round(score, 1)
    
    def calculate_progress(self, current_score):
        """Calculate progress toward #1 ranking"""
        
        progress = (current_score - self.baseline_score) / (self.target_score - self.baseline_score) * 100
        return max(0, min(100, progress))
    
    def display_dashboard(self):
        """Display real-time monitoring dashboard"""
        
        print("\n" + "="*80)
        print("PROMETHEUS OPTIMIZATION PERFORMANCE MONITOR")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Get current metrics
        current_metrics = self.get_current_performance()
        current_score = self.calculate_current_score(current_metrics)
        progress = self.calculate_progress(current_score)
        
        # Save to history
        self.performance_history.append({
            "timestamp": datetime.now().isoformat(),
            "score": current_score,
            "metrics": current_metrics
        })
        self.save_history()
        
        # Display current score
        print("OVERALL SCORE:")
        print("-" * 80)
        print(f"  Baseline:  {self.baseline_score}/100  (Starting point)")
        print(f"  Current:   {current_score}/100  (Now)")
        print(f"  Target:    {self.target_score}/100  (#1 Ranking)")
        print(f"  Gap:       {self.target_score - current_score:.1f} points remaining")
        print(f"  Progress:  {progress:.1f}% toward #1 ranking")
        print()
        
        # Progress bar
        bar_length = 50
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}] {progress:.1f}%")
        print()
        
        # Display metrics comparison
        print("KEY METRICS COMPARISON:")
        print("-" * 80)
        print(f"{'Metric':<20} {'Baseline':<15} {'Current':<15} {'Target':<15} {'Status':<10}")
        print("-" * 80)
        
        for metric in ["win_rate", "cagr", "sharpe_ratio", "max_drawdown"]:
            baseline = self.baseline_metrics[metric]
            current = current_metrics[metric]
            target = self.target_metrics[metric]
            
            # Determine status
            if metric == "max_drawdown":
                # Lower is better for drawdown
                if current <= target:
                    status = "✅ TARGET"
                elif current <= baseline:
                    status = "🟡 IMPROVED"
                else:
                    status = "🔴 NEEDS WORK"
            else:
                # Higher is better for other metrics
                if current >= target:
                    status = "✅ TARGET"
                elif current >= baseline:
                    status = "🟡 IMPROVED"
                else:
                    status = "🔴 NEEDS WORK"
            
            # Format metric values
            if metric == "win_rate":
                baseline_str = f"{baseline:.1f}%"
                current_str = f"{current:.1f}%"
                target_str = f"{target:.1f}%"
            elif metric in ["cagr", "max_drawdown"]:
                baseline_str = f"{baseline:.1f}%"
                current_str = f"{current:.1f}%"
                target_str = f"{target:.1f}%"
            else:
                baseline_str = f"{baseline:.2f}"
                current_str = f"{current:.2f}"
                target_str = f"{target:.2f}"
            
            metric_name = metric.replace("_", " ").title()
            print(f"{metric_name:<20} {baseline_str:<15} {current_str:<15} {target_str:<15} {status:<10}")
        
        print()
        
        # Optimization effectiveness
        print("OPTIMIZATION EFFECTIVENESS:")
        print("-" * 80)
        
        optimizations = [
            {"name": "Confidence Threshold (0.35→0.50)", "target_impact": 2.0, "status": "deployed"},
            {"name": "Dynamic Position Sizing", "target_impact": 2.5, "status": "deployed"},
            {"name": "Regime Strategy Selection", "target_impact": 1.5, "status": "deployed"},
            {"name": "Multi-Timeframe Confirmation", "target_impact": 0.8, "status": "deployed"},
            {"name": "ML Win Rate Prediction", "target_impact": 1.2, "status": "needs_training"}
        ]
        
        total_expected = sum(opt["target_impact"] for opt in optimizations)
        actual_improvement = current_score - self.baseline_score
        
        for opt in optimizations:
            status_icon = "✅" if opt["status"] == "deployed" else "⏳"
            print(f"  {status_icon} {opt['name']:<45} +{opt['target_impact']:.1f} points")
        
        print("-" * 80)
        print(f"  Total Expected Impact: +{total_expected:.1f} points")
        print(f"  Actual Improvement:    +{actual_improvement:.1f} points ({actual_improvement/total_expected*100:.0f}% of expected)")
        print()
        
        # Timeline to #1
        print("TIMELINE TO #1 RANKING:")
        print("-" * 80)
        
        if progress >= 100:
            print("  🎉 CONGRATULATIONS! #1 RANKING ACHIEVED!")
        else:
            days_elapsed = len(self.performance_history)
            if days_elapsed > 1:
                improvement_rate = (current_score - self.baseline_score) / days_elapsed
                remaining_points = self.target_score - current_score
                estimated_days = remaining_points / improvement_rate if improvement_rate > 0 else 999
                
                print(f"  Days Elapsed:        {days_elapsed}")
                print(f"  Improvement Rate:    +{improvement_rate:.2f} points/day")
                print(f"  Estimated Time:      {estimated_days:.0f} days to #1")
                print(f"  Target Date:         {(datetime.now() + timedelta(days=estimated_days)).strftime('%Y-%m-%d')}")
            else:
                print("  Status: Initial deployment - collecting performance data...")
                print("  Check back after 7 days for timeline estimate")
        
        print()
        
        # Recommendations
        print("RECOMMENDATIONS:")
        print("-" * 80)
        
        if current_score >= self.target_score:
            print("  ✅ All targets achieved!")
            print("  • Document results for #1 ranking claim")
            print("  • Prepare for live trading validation")
            print("  • Continue monitoring for consistency")
        elif progress >= 75:
            print("  🟡 Close to target - focus on:")
            if current_metrics["win_rate"] < self.target_metrics["win_rate"]:
                print("     • Train and deploy ML Win Rate Predictor")
                print("     • Fine-tune confidence thresholds")
            if current_metrics["cagr"] < self.target_metrics["cagr"]:
                print("     • Optimize position sizing for larger winners")
                print("     • Review regime-based strategy selection")
        else:
            print("  🔴 Continue optimization deployment:")
            print("     • Ensure all 5 optimizations are active")
            print("     • Monitor for 7-30 days to see full impact")
            print("     • Retrain ML models with latest data")
            print("     • Review and adjust strategy parameters")
        
        print()
        print("="*80)
    
    def generate_report(self):
        """Generate detailed performance report"""
        
        if len(self.performance_history) < 2:
            print("Not enough data for report. Need at least 2 data points.")
            return
        
        report_file = Path(f"optimization_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        
        with open(report_file, 'w') as f:
            f.write("# PROMETHEUS Optimization Performance Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            current_metrics = self.get_current_performance()
            current_score = self.calculate_current_score(current_metrics)
            progress = self.calculate_progress(current_score)
            
            f.write("## Executive Summary\n\n")
            f.write(f"- **Current Score**: {current_score}/100\n")
            f.write(f"- **Baseline Score**: {self.baseline_score}/100\n")
            f.write(f"- **Target Score**: {self.target_score}/100\n")
            f.write(f"- **Improvement**: +{current_score - self.baseline_score:.1f} points\n")
            f.write(f"- **Progress**: {progress:.1f}% toward #1 ranking\n")
            f.write(f"- **Gap Remaining**: {self.target_score - current_score:.1f} points\n\n")
            
            # Metrics table
            f.write("## Performance Metrics\n\n")
            f.write("| Metric | Baseline | Current | Target | Change | Status |\n")
            f.write("|--------|----------|---------|--------|--------|--------|\n")
            
            for metric in ["win_rate", "cagr", "sharpe_ratio", "max_drawdown"]:
                baseline = self.baseline_metrics[metric]
                current = current_metrics[metric]
                target = self.target_metrics[metric]
                change = current - baseline
                
                if metric == "max_drawdown":
                    status = "✅" if current <= target else "🔴"
                else:
                    status = "✅" if current >= target else "🔴"
                
                metric_name = metric.replace("_", " ").title()
                f.write(f"| {metric_name} | {baseline:.2f} | {current:.2f} | {target:.2f} | {change:+.2f} | {status} |\n")
            
            f.write("\n")
            
            # Historical trend
            f.write("## Historical Performance\n\n")
            f.write("```\n")
            for i, entry in enumerate(self.performance_history[-10:], 1):  # Last 10 entries
                timestamp = entry["timestamp"][:10]
                score = entry["score"]
                f.write(f"{i}. {timestamp}: {score:.1f}/100\n")
            f.write("```\n\n")
            
            f.write("---\n")
            f.write("*Generated by PROMETHEUS Optimization Monitor*\n")
        
        print(f"✅ Report saved to: {report_file}")

if __name__ == "__main__":
    monitor = OptimizationMonitor()
    
    # Display dashboard
    monitor.display_dashboard()
    
    # Generate report if enough data
    if len(monitor.performance_history) >= 2:
        print("\nGenerating detailed report...")
        monitor.generate_report()
    
    print("\n💡 Run this script daily to track optimization progress!")
    print("   Schedule: python monitor_optimization_performance.py")
