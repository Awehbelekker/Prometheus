#!/usr/bin/env python3
"""
PROMETHEUS Adaptive Market Regime Learning
Tests and optimizes for different market conditions:
- Bull markets (high growth)
- Bear markets (downturns)
- Sideways/choppy markets
- High volatility periods
- Low volatility periods
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from run_continuous_learning_backtest import ContinuousLearningBacktest
import json
from datetime import datetime

class AdaptiveMarketLearning(ContinuousLearningBacktest):
    """Enhanced learning for different market regimes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.regime_results = {}
    
    def run_market_regime_learning(self):
        """Run learning cycles optimized for different market conditions"""
        
        print("\n" + "="*70)
        print("🌍 PROMETHEUS ADAPTIVE MARKET REGIME LEARNING")
        print("="*70)
        print()
        print("This will optimize parameters for:")
        print("  📈 Bull Markets (high momentum)")
        print("  📉 Bear Markets (risk management)")
        print("  📊 Sideways Markets (mean reversion)")
        print("  ⚡ High Volatility (rapid changes)")
        print("  😴 Low Volatility (steady growth)")
        print()
        
        # Market regime configurations
        regimes = {
            'bull_market': {
                'name': 'Bull Market Optimized',
                'years': 50,
                'generations': 30,
                'params': {
                    'trend_weight': 1.5,  # Emphasize momentum
                    'risk_tolerance': 0.08,  # Higher risk
                    'max_position_size': 0.15,  # Larger positions
                }
            },
            'bear_market': {
                'name': 'Bear Market Protection',
                'years': 50,
                'generations': 30,
                'params': {
                    'trend_weight': 0.5,  # Conservative
                    'risk_tolerance': 0.03,  # Lower risk
                    'max_position_size': 0.08,  # Smaller positions
                }
            },
            'sideways_market': {
                'name': 'Sideways/Choppy Market',
                'years': 50,
                'generations': 30,
                'params': {
                    'mean_reversion_weight': 1.5,  # Mean reversion focus
                    'risk_tolerance': 0.05,
                    'trades_per_day': 8,  # More frequent trading
                }
            },
            'high_volatility': {
                'name': 'High Volatility Regime',
                'years': 50,
                'generations': 30,
                'params': {
                    'volatility_adjustment': 1.5,
                    'risk_tolerance': 0.04,
                    'stop_loss_multiplier': 0.8,  # Tighter stops
                }
            },
            'low_volatility': {
                'name': 'Low Volatility Regime',
                'years': 50,
                'generations': 30,
                'params': {
                    'volatility_adjustment': 0.5,
                    'risk_tolerance': 0.06,
                    'max_position_size': 0.12,
                }
            },
            'balanced': {
                'name': 'All-Weather Balanced',
                'years': 100,
                'generations': 50,
                'params': {
                    'adaptive_mode': True,
                    'risk_tolerance': 0.05,
                }
            }
        }
        
        results_summary = []
        
        for regime_key, config in regimes.items():
            print("\n" + "="*70)
            print(f"🔄 LEARNING: {config['name']}")
            print("="*70)
            print(f"   Years: {config['years']}")
            print(f"   Generations: {config['generations']}")
            print(f"   Special Parameters: {config['params']}")
            print()
            
            # Update parameters for this regime
            for param, value in config['params'].items():
                if hasattr(self.best_params, param):
                    setattr(self.best_params, param, value)
            
            # Run learning for this regime
            result = self.run_continuous_learning_loop(
                max_generations=config['generations'],
                years=config['years']
            )
            
            # The result is the learning history (list), get the last entry
            final_result = None
            if result and isinstance(result, list) and len(result) > 0:
                final_result = result[-1]  # Last generation result
            
            self.regime_results[regime_key] = {
                'name': config['name'],
                'config': config,
                'learning_history': result,
                'timestamp': datetime.now().isoformat()
            }
            
            # Quick summary
            if final_result and isinstance(final_result, dict):
                final = final_result.get('result', {})
                summary = {
                    'regime': config['name'],
                    'cagr': final.get('cagr', 0) if isinstance(final, dict) else 0,
                    'sharpe': final.get('sharpe_ratio', 0) if isinstance(final, dict) else 0,
                    'win_rate': final.get('win_rate', 0) if isinstance(final, dict) else 0,
                    'max_dd': final.get('max_drawdown', 0) if isinstance(final, dict) else 0,
                    'generations': final_result.get('generation', 0)
                }
                results_summary.append(summary)
                
                print(f"\n   ✅ {config['name']} Complete!")
                print(f"      CAGR: {summary['cagr']:.2%}")
                print(f"      Sharpe: {summary['sharpe']:.2f}")
                print(f"      Win Rate: {summary['win_rate']:.1%}")
                print(f"      Max DD: {summary['max_dd']:.2%}")
            else:
                print(f"\n   ⚠️ {config['name']} completed but no valid results")
        
        # Save comprehensive results
        self._save_adaptive_results(results_summary)
        
        # Display final comparison
        self._display_regime_comparison(results_summary)
    
    def _save_adaptive_results(self, summary):
        """Save adaptive learning results"""
        output = {
            'timestamp': datetime.now().isoformat(),
            'regimes_tested': len(self.regime_results),
            'regime_results': self.regime_results,
            'summary': summary
        }
        
        filename = 'ADAPTIVE_MARKET_LEARNING_RESULTS.json'
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n💾 Adaptive results saved to: {filename}")
    
    def _display_regime_comparison(self, summary):
        """Display comparison of all regimes"""
        print("\n" + "="*70)
        print("📊 MARKET REGIME COMPARISON")
        print("="*70)
        print()
        print(f"{'Regime':<30} {'CAGR':>10} {'Sharpe':>10} {'Win%':>10} {'MaxDD':>10}")
        print("-"*70)
        
        for s in summary:
            print(f"{s['regime']:<30} {s['cagr']:>9.1%} {s['sharpe']:>10.2f} "
                  f"{s['win_rate']:>9.1%} {s['max_dd']:>9.1%}")
        
        print("="*70)
        
        # Find best regime for each metric
        best_cagr = max(summary, key=lambda x: x['cagr'])
        best_sharpe = max(summary, key=lambda x: x['sharpe'])
        best_wr = max(summary, key=lambda x: x['win_rate'])
        best_dd = max(summary, key=lambda x: -x['max_dd'])
        
        print()
        print("🏆 BEST PERFORMERS:")
        print(f"   Highest CAGR:   {best_cagr['regime']} ({best_cagr['cagr']:.1%})")
        print(f"   Best Sharpe:    {best_sharpe['regime']} ({best_sharpe['sharpe']:.2f})")
        print(f"   Highest Win%:   {best_wr['regime']} ({best_wr['win_rate']:.1%})")
        print(f"   Best Drawdown:  {best_dd['regime']} ({best_dd['max_dd']:.1%})")
        print()


def main():
    print("\n" + "="*70)
    print("🧠 PROMETHEUS ADAPTIVE MARKET REGIME LEARNING")
    print("="*70)
    print()
    print("This system will:")
    print("  1. Optimize for BULL markets (momentum focus)")
    print("  2. Optimize for BEAR markets (defensive)")
    print("  3. Optimize for SIDEWAYS markets (mean reversion)")
    print("  4. Optimize for HIGH VOLATILITY (tight risk)")
    print("  5. Optimize for LOW VOLATILITY (stable growth)")
    print("  6. Create ALL-WEATHER balanced strategy")
    print()
    print("Total runtime: 15-30 minutes")
    print()
    
    confirm = input("Start adaptive market learning? (yes/no) [yes]: ").strip().lower() or "yes"
    
    if confirm in ['yes', 'y']:
        learner = AdaptiveMarketLearning(initial_capital=10000.0)
        learner.run_market_regime_learning()
    else:
        print("Cancelled.")


if __name__ == "__main__":
    main()
