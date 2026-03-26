"""
================================================================================
PROMETHEUS LONG-TERM MEMORY SYSTEM
================================================================================

This system maintains ALL historical knowledge:
- Backtest results (20Y, 50Y, 100Y, adaptive learning)
- Training data from books, research papers, articles
- Live trading performance and learnings
- Charts and visualizations
- Expert patterns and strategies

Prometheus can access this knowledge at ANY time to make better decisions!
================================================================================
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class PrometheusMemory:
    """Long-term memory system for Prometheus AI"""
    
    def __init__(self):
        self.memory = {
            'backtest_results': {},
            'training_data': {},
            'live_trading': {},
            'knowledge_base': {},
            'expert_patterns': {},
            'best_parameters': {},
            'performance_history': []
        }
        
    def load_all_memory(self):
        """Load ALL historical data into memory"""
        
        print("\n" + "="*80)
        print("🧠 LOADING PROMETHEUS LONG-TERM MEMORY")
        print("="*80)
        print()
        
        # Load backtest results
        self._load_backtest_results()
        
        # Load training/learning data
        self._load_learning_data()
        
        # Load knowledge base
        self._load_knowledge_base()
        
        # Load live trading data
        self._load_live_trading_data()
        
        # Load expert patterns
        self._load_expert_patterns()
        
        return self.memory
    
    def _load_backtest_results(self):
        """Load all backtest results"""
        
        print("📊 Loading Backtest Results...")
        
        backtest_files = {
            '20_year': 'CONTINUOUS_LEARNING_RESULTS_20Y.json',
            '50_year': 'CONTINUOUS_LEARNING_RESULTS_50Y.json',
            '100_year': 'CONTINUOUS_LEARNING_RESULTS_100Y.json',
            '30_year': 'CONTINUOUS_LEARNING_RESULTS_30Y.json',
            'adaptive': 'ADAPTIVE_MARKET_LEARNING_RESULTS.json',
            '10_year_realistic': '10_YEAR_REALISTIC_BACKTEST.json',
            '10_year': '10_YEAR_BACKTEST_RESULTS.json',
        }
        
        for name, filename in backtest_files.items():
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        data = json.load(f)
                        self.memory['backtest_results'][name] = data
                        
                        # Extract key metrics
                        if 'cagr' in data.get('final_result', {}):
                            cagr = data['final_result']['cagr'] * 100  # Convert to percentage
                            fitness = data.get('best_fitness', 0)
                            print(f"  ✅ {name}: CAGR {cagr:.1f}%, Fitness {fitness:.2f}")
                except Exception as e:
                    print(f"  ⚠️  {name}: Error loading - {e}")
        
        print()
    
    def _load_learning_data(self):
        """Load learning state and history"""
        
        print("🎓 Loading Learning Data...")
        
        learning_files = [
            'learning_state.json',
            'learning_feedback.json',
            'paper_trading_learnings.json',
            '5_year_learning_results_*.json'
        ]
        
        # Load learning state
        if os.path.exists('learning_state.json'):
            with open('learning_state.json', 'r') as f:
                self.memory['training_data']['learning_state'] = json.load(f)
                generations = self.memory['training_data']['learning_state'].get('generation', 0)
                best_fitness = self.memory['training_data']['learning_state'].get('best_fitness', 0)
                print(f"  ✅ Learning State: Gen {generations}, Fitness {best_fitness:.2f}")
        
        # Load learning feedback
        if os.path.exists('learning_feedback.json'):
            with open('learning_feedback.json', 'r') as f:
                self.memory['training_data']['feedback'] = json.load(f)
                print(f"  ✅ Learning Feedback loaded")
        
        # Load paper trading learnings
        if os.path.exists('paper_trading_learnings.json'):
            with open('paper_trading_learnings.json', 'r') as f:
                self.memory['live_trading']['paper_learnings'] = json.load(f)
                print(f"  ✅ Paper Trading Learnings loaded")
        
        print()
    
    def _load_knowledge_base(self):
        """Load knowledge from books, research, articles"""
        
        print("📚 Loading Knowledge Base...")
        
        # Load AI knowledge training data
        if os.path.exists('ai_knowledge_training_data.json'):
            with open('ai_knowledge_training_data.json', 'r') as f:
                self.memory['knowledge_base']['training_data'] = json.load(f)
                kb = self.memory['knowledge_base']['training_data']['knowledge_base']
                print(f"  ✅ {len(kb.get('books', []))} Trading Books")
                print(f"  ✅ {len(kb.get('research_papers', []))} Research Papers")
                print(f"  ✅ {len(kb.get('articles', []))} Market Insights")
        
        # Load optimized configs
        if os.path.exists('optimized_ai_config.json'):
            with open('optimized_ai_config.json', 'r') as f:
                self.memory['knowledge_base']['optimized_config'] = json.load(f)
                print(f"  ✅ Optimized AI Config")
        
        if os.path.exists('live_ai_config.json'):
            with open('live_ai_config.json', 'r') as f:
                self.memory['knowledge_base']['live_config'] = json.load(f)
                print(f"  ✅ Live AI Config")
        
        print()
    
    def _load_live_trading_data(self):
        """Load live and paper trading data"""
        
        print("💰 Loading Live Trading Data...")
        
        # Find all paper trading reports
        paper_reports = glob.glob('prometheus_active_report_*.json')
        if paper_reports:
            latest = max(paper_reports, key=os.path.getmtime)
            with open(latest, 'r') as f:
                self.memory['live_trading']['latest_report'] = json.load(f)
                print(f"  ✅ Latest Paper Trading Report: {Path(latest).name}")
        
        # Load 48-hour demo log
        if os.path.exists('48hour_demo_log.txt'):
            with open('48hour_demo_log.txt', 'r') as f:
                self.memory['live_trading']['demo_log'] = f.read()
                print(f"  ✅ 48-Hour Demo Log")
        
        print()
    
    def _load_expert_patterns(self):
        """Load expert patterns learned from trading"""
        
        print("🎯 Loading Expert Patterns...")
        
        # Find expert pattern files
        pattern_files = glob.glob('expert_patterns_*.json')
        if pattern_files:
            latest = max(pattern_files, key=os.path.getmtime)
            try:
                with open(latest, 'r') as f:
                    self.memory['expert_patterns']['learned'] = json.load(f)
                    print(f"  ✅ Expert Patterns: {Path(latest).name}")
            except:
                print(f"  ⚠️  Expert Patterns: File too large or corrupted")
        
        # Load ultimate strategies
        if os.path.exists('ultimate_strategies.json'):
            with open('ultimate_strategies.json', 'r') as f:
                self.memory['expert_patterns']['strategies'] = json.load(f)
                print(f"  ✅ Ultimate Strategies")
        
        print()
    
    def get_best_parameters(self) -> Dict[str, Any]:
        """Get the absolute best parameters from all training"""
        
        best = {
            'fitness': 0,
            'cagr': 0,
            'sharpe': 0,
            'params': None,
            'source': None
        }
        
        # Check 50-year results (BEST!)
        if '50_year' in self.memory['backtest_results']:
            result = self.memory['backtest_results']['50_year']
            fitness = result.get('best_fitness', 0)
            if fitness > best['fitness']:
                best['fitness'] = fitness
                best['cagr'] = result['final_result']['cagr'] * 100
                best['sharpe'] = result['final_result']['sharpe_ratio']
                best['params'] = result['best_params']
                best['source'] = '50-year continuous learning'
        
        # Check 100-year results
        if '100_year' in self.memory['backtest_results']:
            result = self.memory['backtest_results']['100_year']
            fitness = result.get('best_fitness', 0)
            if fitness > best['fitness']:
                best['fitness'] = fitness
                best['cagr'] = result['final_result']['cagr'] * 100
                best['sharpe'] = result['final_result']['sharpe_ratio']
                best['params'] = result['best_params']
                best['source'] = '100-year continuous learning'
        
        # Check learning state
        if 'learning_state' in self.memory['training_data']:
            state = self.memory['training_data']['learning_state']
            fitness = state.get('best_fitness', 0)
            if fitness > best['fitness']:
                best['fitness'] = fitness
                best['params'] = state['best_params']
                best['source'] = 'continuous learning state'
        
        return best
    
    def get_knowledge_summary(self) -> str:
        """Generate comprehensive knowledge summary"""
        
        summary = []
        summary.append("\n" + "="*80)
        summary.append("🧠 PROMETHEUS COMPLETE KNOWLEDGE BASE")
        summary.append("="*80)
        summary.append("")
        
        # Backtest results
        summary.append("📊 BACKTEST RESULTS:")
        for name, data in self.memory['backtest_results'].items():
            if 'final_result' in data and 'cagr' in data['final_result']:
                cagr = data['final_result']['cagr'] * 100
                fitness = data.get('best_fitness', 0)
                sharpe = data['final_result'].get('sharpe_ratio', 0)
                win_rate = data['final_result'].get('win_rate', 0) * 100
                summary.append(f"  • {name:20s}: CAGR {cagr:6.1f}% | Sharpe {sharpe:5.2f} | Win {win_rate:5.1f}% | Fitness {fitness:.2f}")
        summary.append("")
        
        # Best parameters
        best = self.get_best_parameters()
        summary.append("🏆 BEST PARAMETERS EVER:")
        summary.append(f"  Source: {best['source']}")
        summary.append(f"  Fitness: {best['fitness']:.2f}")
        summary.append(f"  CAGR: {best['cagr']:.1f}%")
        summary.append(f"  Sharpe: {best['sharpe']:.2f}")
        if best['params']:
            summary.append(f"  Win Rate: {best['params']['win_rate']*100:.1f}%")
            summary.append(f"  Avg Win: {best['params']['avg_win_pct']*100:.2f}%")
            summary.append(f"  Avg Loss: {best['params']['avg_loss_pct']*100:.2f}%")
            summary.append(f"  Trades/Day: {best['params']['trades_per_day']:.1f}")
        summary.append("")
        
        # Knowledge base
        if 'training_data' in self.memory['knowledge_base']:
            kb = self.memory['knowledge_base']['training_data']['knowledge_base']
            summary.append("📚 KNOWLEDGE BASE:")
            summary.append(f"  • {len(kb.get('books', []))} Trading Books (Market Wizards, Turtle Traders, etc.)")
            summary.append(f"  • {len(kb.get('research_papers', []))} Research Papers (Momentum, Quality Factor, etc.)")
            summary.append(f"  • {len(kb.get('articles', []))} Market Insight Categories")
            summary.append("")
        
        # Learning history
        if 'learning_state' in self.memory['training_data']:
            state = self.memory['training_data']['learning_state']
            summary.append("🎓 LEARNING HISTORY:")
            summary.append(f"  • Total Generations: {state.get('generation', 0)}")
            summary.append(f"  • Best Fitness: {state.get('best_fitness', 0):.2f}")
            summary.append(f"  • Fitness History: {len(state.get('fitness_history', []))} data points")
            summary.append("")
        
        # Live trading
        if 'latest_report' in self.memory['live_trading']:
            summary.append("💰 LIVE TRADING:")
            summary.append(f"  • Latest paper trading report available")
            if 'demo_log' in self.memory['live_trading']:
                summary.append(f"  • 48-hour demo log available")
            summary.append("")
        
        summary.append("="*80)
        summary.append(f"📅 Memory loaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("="*80)
        
        return "\n".join(summary)
    
    def save_memory_index(self):
        """Save memory index for quick access"""
        
        index = {
            'timestamp': datetime.now().isoformat(),
            'backtest_results': list(self.memory['backtest_results'].keys()),
            'best_parameters': self.get_best_parameters(),
            'knowledge_sources': len(self.memory.get('knowledge_base', {}).get('training_data', {}).get('knowledge_base', {}).get('books', [])),
            'learning_generations': self.memory.get('training_data', {}).get('learning_state', {}).get('generation', 0),
            'memory_size': {
                'backtests': len(self.memory['backtest_results']),
                'training_data': len(self.memory['training_data']),
                'live_trading': len(self.memory['live_trading']),
                'knowledge_base': len(self.memory['knowledge_base']),
                'expert_patterns': len(self.memory['expert_patterns']),
            }
        }
        
        with open('prometheus_memory_index.json', 'w') as f:
            json.dump(index, f, indent=2)
        
        return index


def main():
    """Load and display all Prometheus memory"""
    
    memory = PrometheusMemory()
    memory.load_all_memory()
    
    # Display summary
    print(memory.get_knowledge_summary())
    
    # Save index
    index = memory.save_memory_index()
    print(f"\n💾 Memory index saved to: prometheus_memory_index.json")
    print()
    
    # Show best parameters
    best = memory.get_best_parameters()
    print("="*80)
    print("🎯 READY TO USE BEST PARAMETERS")
    print("="*80)
    print()
    print("These can be loaded into ANY trading system:")
    print()
    print(f"  Win Rate: {best['params']['win_rate']*100:.2f}%")
    print(f"  Avg Win: {best['params']['avg_win_pct']*100:.2f}%")
    print(f"  Avg Loss: {best['params']['avg_loss_pct']*100:.3f}%")
    print(f"  Trades/Day: {best['params']['trades_per_day']:.1f}")
    print(f"  Max Position: {best['params']['max_position_size']*100:.1f}%")
    print(f"  Risk Tolerance: {best['params']['risk_tolerance']*100:.1f}%")
    print()
    print(f"Expected Performance: {best['cagr']:.1f}% CAGR, {best['sharpe']:.2f} Sharpe")
    print()
    print("="*80)
    print("✅ PROMETHEUS HAS COMPLETE LONG-TERM MEMORY!")
    print("="*80)
    print()
    print("Access anytime with:")
    print("  python prometheus_long_term_memory.py")
    print()


if __name__ == "__main__":
    main()
