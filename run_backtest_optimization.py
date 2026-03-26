#!/usr/bin/env python3
"""
🚀 PROMETHEUS BACKTEST OPTIMIZATION SUITE
Runs multiple backtest configurations to find optimal trading parameters.

Target Metrics:
- Win rate > 55%
- Profit factor > 1.5
- Sharpe ratio > 1.0
- Max drawdown < 15%
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

# Import the backtester
from prometheus_real_ai_backtest import PrometheusRealAIBacktester, BacktestMetrics

@dataclass
class BacktestConfig:
    """Configuration for a single backtest run"""
    config_id: str
    take_profit_pct: float
    stop_loss_pct: float
    max_position_pct: float
    
@dataclass
class BacktestResult:
    """Result of a single backtest run"""
    config_id: str
    take_profit_pct: float
    stop_loss_pct: float
    max_position_pct: float
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    total_trades: int
    final_capital: float
    meets_targets: bool

# Define test configurations
CONFIGURATIONS = [
    # Config 1-5: Vary Take Profit (5%, 8%, 10%, 12%, 15%) with baseline SL/Position
    BacktestConfig("TP05_SL03_POS10", 0.05, 0.03, 0.10),
    BacktestConfig("TP08_SL03_POS10", 0.08, 0.03, 0.10),
    BacktestConfig("TP10_SL03_POS10", 0.10, 0.03, 0.10),
    BacktestConfig("TP12_SL03_POS10", 0.12, 0.03, 0.10),
    BacktestConfig("TP15_SL03_POS10", 0.15, 0.03, 0.10),
    
    # Config 6-9: Vary Stop Loss (2%, 3%, 4%, 5%) with best TP
    BacktestConfig("TP10_SL02_POS10", 0.10, 0.02, 0.10),
    BacktestConfig("TP10_SL04_POS10", 0.10, 0.04, 0.10),
    BacktestConfig("TP10_SL05_POS10", 0.10, 0.05, 0.10),
    
    # Config 10-12: Vary Position Size (5%, 15%, 20%)
    BacktestConfig("TP10_SL03_POS05", 0.10, 0.03, 0.05),
    BacktestConfig("TP10_SL03_POS15", 0.10, 0.03, 0.15),
    BacktestConfig("TP10_SL03_POS20", 0.10, 0.03, 0.20),
]

SYMBOLS = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'NVDA', 'BTCUSD', 'ETHUSD']
PERIOD_DAYS = 365
INITIAL_CAPITAL = 100000.0

# Target metrics
TARGET_WIN_RATE = 55.0
TARGET_PROFIT_FACTOR = 1.5
TARGET_SHARPE = 1.0
TARGET_MAX_DRAWDOWN = 15.0

async def run_single_backtest(config: BacktestConfig) -> BacktestResult:
    """Run a single backtest configuration"""
    print(f"\n{'='*60}")
    print(f"Running Config: {config.config_id}")
    print(f"  Take Profit: {config.take_profit_pct*100:.1f}%")
    print(f"  Stop Loss: {config.stop_loss_pct*100:.1f}%")
    print(f"  Max Position: {config.max_position_pct*100:.1f}%")
    print(f"{'='*60}")
    
    backtester = PrometheusRealAIBacktester(
        initial_capital=INITIAL_CAPITAL,
        max_position_pct=config.max_position_pct,
        stop_loss_pct=config.stop_loss_pct,
        take_profit_pct=config.take_profit_pct
    )
    
    metrics = await backtester.run_backtest(SYMBOLS, PERIOD_DAYS)
    final_capital = backtester.portfolio_history[-1] if backtester.portfolio_history else INITIAL_CAPITAL
    
    meets_targets = (
        metrics.win_rate >= TARGET_WIN_RATE and
        metrics.profit_factor >= TARGET_PROFIT_FACTOR and
        metrics.sharpe_ratio >= TARGET_SHARPE and
        abs(metrics.max_drawdown) <= TARGET_MAX_DRAWDOWN
    )
    
    return BacktestResult(
        config_id=config.config_id,
        take_profit_pct=config.take_profit_pct,
        stop_loss_pct=config.stop_loss_pct,
        max_position_pct=config.max_position_pct,
        win_rate=metrics.win_rate,
        profit_factor=metrics.profit_factor,
        sharpe_ratio=metrics.sharpe_ratio,
        max_drawdown=metrics.max_drawdown,
        total_return=metrics.total_return,
        total_trades=metrics.total_trades,
        final_capital=final_capital,
        meets_targets=meets_targets
    )

def print_results_table(results: List[BacktestResult]):
    """Print comprehensive results comparison table"""
    print("\n" + "="*120)
    print("PROMETHEUS BACKTEST OPTIMIZATION RESULTS")
    print("="*120)
    print(f"{'Config ID':<20} | {'TP%':>5} | {'SL%':>5} | {'Pos%':>5} | {'WinRate':>8} | {'PF':>6} | {'Sharpe':>7} | {'MaxDD':>8} | {'Return':>10} | {'Trades':>6} | {'Target':>6}")
    print("-"*120)
    
    for r in results:
        target_status = "✅ YES" if r.meets_targets else "❌ NO"
        print(f"{r.config_id:<20} | {r.take_profit_pct*100:>5.1f} | {r.stop_loss_pct*100:>5.1f} | {r.max_position_pct*100:>5.1f} | {r.win_rate:>7.1f}% | {r.profit_factor:>6.2f} | {r.sharpe_ratio:>7.2f} | {r.max_drawdown:>7.2f}% | {r.total_return:>9.2f}% | {r.total_trades:>6} | {target_status}")
    
    print("="*120)
    print(f"\nTARGET METRICS: Win Rate > {TARGET_WIN_RATE}%, Profit Factor > {TARGET_PROFIT_FACTOR}, Sharpe > {TARGET_SHARPE}, Max Drawdown < {TARGET_MAX_DRAWDOWN}%")

def find_optimal_config(results: List[BacktestResult]) -> BacktestResult:
    """Find the optimal configuration based on composite score"""
    def score(r: BacktestResult) -> float:
        # Composite score: weighted combination of metrics
        win_score = r.win_rate / 100 * 25  # 25% weight
        pf_score = min(r.profit_factor / 3, 1) * 25  # 25% weight, capped at 3
        sharpe_score = min(max(r.sharpe_ratio + 1, 0) / 3, 1) * 25  # 25% weight
        dd_score = max(1 - abs(r.max_drawdown) / 50, 0) * 25  # 25% weight
        return win_score + pf_score + sharpe_score + dd_score
    
    return max(results, key=score)

async def main():
    """Run all backtest configurations"""
    print("🚀 PROMETHEUS BACKTEST OPTIMIZATION SUITE")
    print(f"   Running {len(CONFIGURATIONS)} configurations")
    print(f"   Period: {PERIOD_DAYS} days")
    print(f"   Symbols: {', '.join(SYMBOLS)}")
    print(f"   Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    
    results: List[BacktestResult] = []
    
    for i, config in enumerate(CONFIGURATIONS, 1):
        print(f"\n[{i}/{len(CONFIGURATIONS)}] Starting {config.config_id}...")
        try:
            result = await run_single_backtest(config)
            results.append(result)
        except Exception as e:
            print(f"❌ Error in {config.config_id}: {e}")
    
    # Print results table
    print_results_table(results)
    
    # Find and display optimal configuration
    if results:
        optimal = find_optimal_config(results)
        print(f"\n🏆 OPTIMAL CONFIGURATION: {optimal.config_id}")
        print(f"   Take Profit: {optimal.take_profit_pct*100:.1f}%")
        print(f"   Stop Loss: {optimal.stop_loss_pct*100:.1f}%")
        print(f"   Max Position: {optimal.max_position_pct*100:.1f}%")
        print(f"   Win Rate: {optimal.win_rate:.1f}%")
        print(f"   Profit Factor: {optimal.profit_factor:.2f}")
        print(f"   Sharpe Ratio: {optimal.sharpe_ratio:.2f}")
        print(f"   Max Drawdown: {optimal.max_drawdown:.2f}%")
        print(f"   Total Return: {optimal.total_return:.2f}%")
        
        # Save results to JSON
        results_file = f'backtest_optimization_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'run_date': datetime.now().isoformat(),
                'period_days': PERIOD_DAYS,
                'symbols': SYMBOLS,
                'initial_capital': INITIAL_CAPITAL,
                'target_metrics': {
                    'win_rate': TARGET_WIN_RATE,
                    'profit_factor': TARGET_PROFIT_FACTOR,
                    'sharpe_ratio': TARGET_SHARPE,
                    'max_drawdown': TARGET_MAX_DRAWDOWN
                },
                'results': [asdict(r) for r in results],
                'optimal_config': asdict(optimal)
            }, f, indent=2)
        print(f"\n📁 Results saved to {results_file}")

if __name__ == '__main__':
    asyncio.run(main())

