"""
PROMETHEUS ALL SYSTEMS MONITOR
Real-time dashboard showing status of all training systems
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

def load_json_safe(filepath):
    """Load JSON file safely"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

def format_time_ago(timestamp_str):
    """Format timestamp as time ago"""
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - ts
        
        if delta.seconds < 60:
            return f"{delta.seconds}s ago"
        elif delta.seconds < 3600:
            return f"{delta.seconds // 60}m ago"
        elif delta.seconds < 86400:
            return f"{delta.seconds // 3600}h ago"
        else:
            return f"{delta.days}d ago"
    except:
        return "Unknown"

def monitor_learning_engine():
    """Monitor learning engine status"""
    print("\n" + "="*80)
    print("🧠 PROMETHEUS LEARNING ENGINE")
    print("="*80)
    
    strategies_file = "ultimate_strategies.json"
    if not os.path.exists(strategies_file):
        print("❌ Not running (no strategies file)")
        return
    
    data = load_json_safe(strategies_file)
    if not data:
        print("❌ Could not load strategies")
        return
    
    # Get all strategies
    strategies = []
    for key, value in data.items():
        if isinstance(value, dict) and 'name' in value:
            strategies.append(value)
    
    strategies.sort(key=lambda x: x.get('win_rate', 0), reverse=True)
    
    print(f"✅ Status: RUNNING")
    print(f"📊 Total Strategies: {len(strategies)}")
    
    # Total backtests
    total_backtests = sum(s.get('total_backtests', 0) for s in strategies)
    print(f"🔬 Total Backtests: {total_backtests:,}")
    
    # Top 5 strategies
    print(f"\n🏆 TOP 5 STRATEGIES:")
    for i, strategy in enumerate(strategies[:5], 1):
        name = strategy.get('name', 'Unknown')
        win_rate = strategy.get('win_rate', 0) * 100
        sharpe = strategy.get('sharpe_ratio', 0)
        trades = strategy.get('total_trades', 0)
        print(f"   {i}. {name:25} | Win: {win_rate:.1f}% | Sharpe: {sharpe:.2f} | {trades:,} trades")

def monitor_cloud_vision():
    """Monitor Claude Vision training"""
    print("\n" + "="*80)
    print("☁️ CLOUD VISION TRAINING")
    print("="*80)
    
    progress_file = "cloud_vision_progress.json"
    patterns_file = "chart_patterns_database.json"
    
    if not os.path.exists(progress_file):
        print("❌ Not running (no progress file)")
        return
    
    progress = load_json_safe(progress_file)
    patterns = load_json_safe(patterns_file)
    
    if not progress:
        print("❌ Could not load progress")
        return
    
    charts_done = progress.get('charts_analyzed', 0)
    total_charts = progress.get('total_charts', 1250)
    pct = (charts_done / total_charts) * 100
    
    print(f"✅ Status: RUNNING")
    print(f"📊 Progress: {charts_done}/{total_charts} charts ({pct:.1f}%)")
    
    if patterns:
        total_patterns = len(patterns.get('patterns', []))
        print(f"🎨 Patterns Detected: {total_patterns}")
    
    # ETA
    if charts_done > 0:
        remaining = total_charts - charts_done
        rate = progress.get('rate_per_minute', 12.4)
        eta_minutes = remaining / rate
        eta_hours = eta_minutes / 60
        
        if eta_hours < 1:
            print(f"⏱️ ETA: {eta_minutes:.0f} minutes")
        else:
            print(f"⏱️ ETA: {eta_hours:.1f} hours")
    
    # Last update
    last_update = progress.get('last_update', '')
    if last_update:
        print(f"🕐 Last Update: {format_time_ago(last_update)}")

def monitor_extended_training():
    """Monitor extended historical training"""
    print("\n" + "="*80)
    print("📈 EXTENDED HISTORICAL TRAINING")
    print("="*80)
    
    # Find latest results file
    files = list(Path('.').glob('extended_training_*yr_*.json'))
    if not files:
        print("⚠️ No training results yet")
        return
    
    latest = max(files, key=lambda x: x.stat().st_mtime)
    data = load_json_safe(str(latest))
    
    if not data:
        print("❌ Could not load results")
        return
    
    # Handle list format
    if isinstance(data, list):
        results = data
        years = 5  # Default
        completed = True
    else:
        years = data.get('years', 'Unknown')
        completed = data.get('training_completed', False)
        results = data.get('results', [])
    
    if completed:
        print(f"✅ Status: COMPLETED ({years} years)")
    else:
        print(f"⏸️ Status: PAUSED ({years} years)")
    
    # Results
    if results:
        print(f"📊 Strategies Tested: {len(results)}")
        
        # Best strategy
        best = max(results, key=lambda x: x.get('avg_cagr_pct', 0))
        print(f"\n🥇 BEST STRATEGY:")
        print(f"   Name: {best.get('strategy_name', 'Unknown')}")
        print(f"   CAGR: {best.get('avg_cagr_pct', 0):.2f}%")
        print(f"   Sharpe: {best.get('avg_sharpe_ratio', 0):.2f}")
        print(f"   Win Rate: {best.get('avg_win_rate_pct', 0):.1f}%")
        print(f"   Max DD: {best.get('avg_max_drawdown_pct', 0):.1f}%")
    
    # File info
    file_time = datetime.fromtimestamp(latest.stat().st_mtime)
    print(f"\n📁 Latest Results: {latest.name}")
    print(f"🕐 Created: {format_time_ago(file_time.strftime('%Y-%m-%d %H:%M:%S'))}")

def monitor_all():
    """Display full system dashboard"""
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("╔" + "="*78 + "╗")
    print("║" + " " * 20 + "PROMETHEUS SYSTEMS MONITOR" + " " * 32 + "║")
    print("║" + " " * 24 + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " " * 30 + "║")
    print("╚" + "="*78 + "╝")
    
    monitor_learning_engine()
    monitor_cloud_vision()
    monitor_extended_training()
    
    print("\n" + "="*80)
    print("💡 Commands:")
    print("   python extended_historical_training.py --years 5  # Run 5-year test")
    print("   python check_training_status.py                   # Quick status")
    print("="*80 + "\n")

if __name__ == "__main__":
    import sys
    
    if "--loop" in sys.argv:
        # Continuous monitoring
        try:
            while True:
                monitor_all()
                print("🔄 Refreshing in 30s... (Ctrl+C to stop)")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n✋ Monitoring stopped")
    else:
        # One-time status
        monitor_all()
