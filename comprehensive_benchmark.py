"""
PROMETHEUS LLM & AI BENCHMARK
Test DeepSeek-R1 vs other LLMs and overall AI system performance
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

console = Console()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class LLMBenchmark:
    """Benchmark different LLM providers"""
    
    def __init__(self):
        self.results = {}
        
    def test_deepseek(self):
        """Test DeepSeek-R1 reasoning"""
        console.print("[cyan]Testing DeepSeek-R1...[/cyan]")
        
        try:
            from core.deepseek_adapter import DeepSeekAdapter
            
            deepseek = DeepSeekAdapter(
                endpoint=os.getenv('GPT_OSS_API_ENDPOINT', 'http://localhost:11434'),
                model=os.getenv('DEEPSEEK_MODEL', 'deepseek-r1:14b')
            )
            
            # Test 1: Simple market analysis
            start = time.time()
            result = deepseek.generate(
                "Analyze: Stock at $100, RSI=70, MACD bullish. Trade?",
                max_tokens=200,
                temperature=0.7
            )
            latency = time.time() - start
            
            if result.get('success'):
                response = result.get('response', '')
                
                self.results['DeepSeek-R1'] = {
                    'status': '✅ WORKING',
                    'latency': latency,
                    'response_length': len(response),
                    'cost': 0.0,
                    'model': result.get('model', 'deepseek-r1:14b'),
                    'quality': self._assess_quality(response)
                }
                console.print(f"  ✅ Response in {latency:.2f}s")
                return True
            else:
                self.results['DeepSeek-R1'] = {
                    'status': '❌ FAILED',
                    'error': result.get('error', 'Unknown error'),
                    'cost': 0.0
                }
                console.print(f"  ❌ Failed: {result.get('error')}")
                return False
                
        except Exception as e:
            self.results['DeepSeek-R1'] = {
                'status': '❌ ERROR',
                'error': str(e),
                'cost': 0.0
            }
            console.print(f"  ❌ Error: {e}")
            return False
    
    def test_openai(self):
        """Test OpenAI GPT-4"""
        console.print("[cyan]Testing OpenAI GPT-4o-mini...[/cyan]")
        
        openai_key = os.getenv('OPENAI_API_KEY', '')
        if not openai_key or len(openai_key) < 20:
            self.results['OpenAI'] = {
                'status': '⚠️ SKIPPED',
                'reason': 'No API key configured'
            }
            console.print("  ⚠️ Skipped (no API key)")
            return False
        
        try:
            import openai
            client = openai.OpenAI(api_key=openai_key)
            
            start = time.time()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": "Analyze: Stock at $100, RSI=70, MACD bullish. Trade?"
                }],
                max_tokens=200,
                temperature=0.7
            )
            latency = time.time() - start
            
            response_text = response.choices[0].message.content
            
            self.results['OpenAI'] = {
                'status': '✅ WORKING',
                'latency': latency,
                'response_length': len(response_text),
                'cost': 0.002,  # Approximate
                'model': 'gpt-4o-mini',
                'quality': self._assess_quality(response_text),
                'tokens': response.usage.total_tokens
            }
            console.print(f"  ✅ Response in {latency:.2f}s (cost: $0.002)")
            return True
            
        except Exception as e:
            self.results['OpenAI'] = {
                'status': '❌ ERROR',
                'error': str(e),
                'cost': 0.0
            }
            console.print(f"  ❌ Error: {e}")
            return False
    
    def test_unified_ai_provider(self):
        """Test Unified AI Provider (main system)"""
        console.print("[cyan]Testing Unified AI Provider...[/cyan]")
        
        try:
            from core.unified_ai_provider import UnifiedAIProvider
            
            provider = UnifiedAIProvider()
            
            # Test market analysis
            start = time.time()
            result = provider.analyze_market({
                'symbol': 'AAPL',
                'price': 180.50,
                'rsi': 65.2,
                'macd': 'bullish',
                'volume': 1000000
            })
            latency = time.time() - start
            
            self.results['Unified AI'] = {
                'status': '✅ WORKING',
                'latency': latency,
                'action': result.get('action', 'HOLD'),
                'confidence': result.get('confidence', 0),
                'cost': result.get('cost', 0.0),
                'source': result.get('source', 'Unknown')
            }
            console.print(f"  ✅ Analysis complete in {latency:.2f}s")
            console.print(f"     Action: {result.get('action')}, Confidence: {result.get('confidence'):.2f}")
            return True
            
        except Exception as e:
            self.results['Unified AI'] = {
                'status': '❌ ERROR',
                'error': str(e)
            }
            console.print(f"  ❌ Error: {e}")
            return False
    
    def _assess_quality(self, response: str) -> str:
        """Assess response quality"""
        response_lower = response.lower()
        
        # Check for trading terms
        has_action = any(word in response_lower for word in ['buy', 'sell', 'hold', 'wait'])
        has_reason = any(word in response_lower for word in ['because', 'since', 'due to', 'rsi', 'macd'])
        has_detail = len(response) > 50
        
        if has_action and has_reason and has_detail:
            return "⭐⭐⭐ Excellent"
        elif has_action and has_reason:
            return "⭐⭐ Good"
        elif has_action:
            return "⭐ Basic"
        else:
            return "❓ Unclear"
    
    def run_benchmark(self):
        """Run all LLM benchmarks"""
        
        console.print()
        console.print(Panel.fit(
            "[bold cyan]PROMETHEUS LLM BENCHMARK[/bold cyan]\n"
            "[dim]Testing AI/LLM providers[/dim]",
            style="bold white on blue"
        ))
        console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("[cyan]Running benchmarks...", total=3)
            
            # Test DeepSeek
            self.test_deepseek()
            progress.advance(task)
            
            # Test OpenAI (if available)
            self.test_openai()
            progress.advance(task)
            
            # Test Unified Provider
            self.test_unified_ai_provider()
            progress.advance(task)
        
        console.print()
        self.print_results()
    
    def print_results(self):
        """Print benchmark results"""
        
        console.print()
        console.print("[bold green]📊 LLM BENCHMARK RESULTS[/bold green]")
        console.print("="*80)
        console.print()
        
        # Results table
        table = Table(box=box.ROUNDED)
        table.add_column("Provider", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Latency", justify="right", style="yellow")
        table.add_column("Cost", justify="right", style="green")
        table.add_column("Quality", justify="center", style="magenta")
        
        for provider, result in self.results.items():
            status = result.get('status', '❓')
            latency = f"{result.get('latency', 0):.2f}s" if 'latency' in result else "N/A"
            cost = f"${result.get('cost', 0):.4f}" if 'cost' in result else "N/A"
            quality = result.get('quality', 'N/A')
            
            table.add_row(provider, status, latency, cost, quality)
        
        console.print(table)
        console.print()
        
        # Analysis
        console.print("[bold cyan]📈 ANALYSIS[/bold cyan]")
        console.print("="*80)
        
        # Find working providers
        working = [p for p, r in self.results.items() if '✅' in r.get('status', '')]
        
        if working:
            console.print(f"[green]✅ {len(working)}/{len(self.results)} providers working[/green]")
            console.print()
            
            # Compare latencies
            latencies = {p: r.get('latency', float('inf')) 
                        for p, r in self.results.items() 
                        if 'latency' in r}
            
            if latencies:
                fastest = min(latencies, key=latencies.get)
                console.print(f"⚡ Fastest: [yellow]{fastest}[/yellow] ({latencies[fastest]:.2f}s)")
            
            # Compare costs
            costs = {p: r.get('cost', 0) 
                    for p, r in self.results.items() 
                    if 'cost' in r}
            
            if costs:
                cheapest = min(costs, key=costs.get)
                console.print(f"💰 Cheapest: [green]{cheapest}[/green] (${costs[cheapest]:.4f})")
            
            console.print()
            
            # Recommendation
            if 'DeepSeek-R1' in working:
                console.print("[bold green]✅ RECOMMENDATION: DeepSeek-R1[/bold green]")
                console.print("  • FREE (zero cost)")
                console.print("  • Local (privacy)")
                console.print("  • Good quality")
                console.print("  • Currently active ✅")
            
        else:
            console.print("[red]❌ No working LLM providers found[/red]")
            console.print()
            console.print("Troubleshooting:")
            console.print("  1. Check if Ollama is running: ollama list")
            console.print("  2. Check if DeepSeek-R1 is installed: ollama pull deepseek-r1:14b")
            console.print("  3. Configure API keys in .env file")
        
        console.print()
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save benchmark results"""
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'benchmark_type': 'LLM Performance',
            'results': self.results
        }
        
        filename = f"llm_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        console.print(f"💾 Results saved to: [cyan]{filename}[/cyan]")
        console.print()


class TradingSystemBenchmark:
    """Benchmark overall trading system with current AI"""
    
    def __init__(self):
        self.results = {}
    
    def run_quick_backtest(self):
        """Run quick 5-year backtest with current AI"""
        
        console.print()
        console.print(Panel.fit(
            "[bold magenta]TRADING SYSTEM BENCHMARK[/bold magenta]\n"
            "[dim]Testing Prometheus with current AI configuration[/dim]",
            style="bold white on magenta"
        ))
        console.print()
        
        console.print("[cyan]Running 5-year backtest with DeepSeek-R1...[/cyan]")
        console.print()
        
        try:
            from run_continuous_learning_backtest import ContinuousLearningBacktest, TradingParameters
            
            # Load current AI parameters
            if os.path.exists('live_ai_config.json'):
                with open('live_ai_config.json', 'r') as f:
                    config = json.load(f)
                    params_dict = config.get('parameters', {})
                    
                params = TradingParameters(
                    win_rate=params_dict.get('win_rate', 0.711),
                    avg_win_pct=params_dict.get('avg_win_pct', 0.03),
                    avg_loss_pct=params_dict.get('avg_loss_pct', 0.0045),
                    trades_per_day=params_dict.get('trades_per_day', 8),
                    max_position_size=params_dict.get('max_position_size', 0.12),
                    transaction_cost=params_dict.get('transaction_cost', 0.001),
                    slippage=params_dict.get('slippage', 0.0005),
                    risk_tolerance=params_dict.get('risk_tolerance', 0.05)
                )
                
                console.print("[green]✅ Using AI-optimized parameters[/green]")
                console.print(f"  Win Rate: {params.win_rate*100:.2f}%")
                console.print(f"  Trades/Day: {params.trades_per_day}")
                console.print()
            else:
                console.print("[yellow]⚠️ Using default parameters[/yellow]")
                console.print()
                params = TradingParameters()
            
            # Run backtest
            backtest = ContinuousLearningBacktest()
            start = time.time()
            result = backtest.run_backtest(params, years=5)
            duration = time.time() - start
            
            self.results['5-Year Backtest'] = {
                'duration': duration,
                'cagr': result.cagr * 100,
                'sharpe': result.sharpe_ratio,
                'win_rate': result.win_rate * 100,
                'max_dd': result.max_drawdown,
                'fitness': result.fitness_score,
                'trades': result.total_trades,
                'final_capital': result.final_capital
            }
            
            console.print(f"[green]✅ Backtest complete in {duration:.1f}s[/green]")
            console.print()
            
            self.print_trading_results()
            
        except Exception as e:
            console.print(f"[red]❌ Backtest failed: {e}[/red]")
            console.print()
    
    def print_trading_results(self):
        """Print trading benchmark results"""
        
        if not self.results:
            return
        
        result = self.results['5-Year Backtest']
        
        console.print("[bold green]📊 TRADING SYSTEM RESULTS[/bold green]")
        console.print("="*80)
        console.print()
        
        table = Table(box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="yellow")
        table.add_column("Assessment", style="green")
        
        # CAGR
        cagr = result['cagr']
        cagr_rating = "🔥 EXCEPTIONAL" if cagr > 100 else "⭐ EXCELLENT" if cagr > 50 else "✅ GOOD" if cagr > 20 else "⚠️ MODERATE"
        table.add_row("CAGR", f"{cagr:.2f}%", cagr_rating)
        
        # Sharpe
        sharpe = result['sharpe']
        sharpe_rating = "🔥 EXCEPTIONAL" if sharpe > 10 else "⭐ EXCELLENT" if sharpe > 5 else "✅ GOOD" if sharpe > 2 else "⚠️ MODERATE"
        table.add_row("Sharpe Ratio", f"{sharpe:.2f}", sharpe_rating)
        
        # Win Rate
        win_rate = result['win_rate']
        win_rating = "🔥 EXCEPTIONAL" if win_rate > 70 else "⭐ EXCELLENT" if win_rate > 60 else "✅ GOOD" if win_rate > 50 else "⚠️ MODERATE"
        table.add_row("Win Rate", f"{win_rate:.2f}%", win_rating)
        
        # Max Drawdown
        max_dd = abs(result['max_dd'])
        dd_rating = "🔥 EXCEPTIONAL" if max_dd < 1 else "⭐ EXCELLENT" if max_dd < 5 else "✅ GOOD" if max_dd < 10 else "⚠️ HIGH"
        table.add_row("Max Drawdown", f"{max_dd:.2f}%", dd_rating)
        
        # Fitness
        fitness = result['fitness']
        fitness_rating = "🔥 EXCEPTIONAL" if fitness > 200 else "⭐ EXCELLENT" if fitness > 100 else "✅ GOOD" if fitness > 50 else "⚠️ MODERATE"
        table.add_row("Fitness Score", f"{fitness:.2f}", fitness_rating)
        
        table.add_row("Total Trades", f"{result['trades']:,}", "")
        table.add_row("Final Capital", f"${result['final_capital']:,.2f}", "")
        table.add_row("Duration", f"{result['duration']:.1f}s", "")
        
        console.print(table)
        console.print()
        
        # Overall verdict
        if cagr > 100 and sharpe > 10 and win_rate > 70:
            console.print("[bold green]🏆 VERDICT: WORLD-CLASS PERFORMANCE[/bold green]")
            console.print("  Prometheus with DeepSeek-R1 AI is performing at elite level!")
        elif cagr > 50 and sharpe > 5:
            console.print("[bold green]⭐ VERDICT: EXCELLENT PERFORMANCE[/bold green]")
            console.print("  Prometheus is significantly outperforming market benchmarks!")
        elif cagr > 20 and sharpe > 2:
            console.print("[bold green]✅ VERDICT: SOLID PERFORMANCE[/bold green]")
            console.print("  Prometheus is beating market averages with good risk management!")
        else:
            console.print("[yellow]⚠️ VERDICT: ACCEPTABLE PERFORMANCE[/yellow]")
            console.print("  Consider running more training or adjusting parameters.")
        
        console.print()


def main():
    console.clear()
    
    console.print()
    console.print("="*80)
    console.print("[bold cyan]PROMETHEUS COMPREHENSIVE BENCHMARK[/bold cyan]")
    console.print("="*80)
    console.print()
    console.print("This benchmark will test:")
    console.print("  1. LLM providers (DeepSeek-R1, OpenAI, etc.)")
    console.print("  2. Unified AI system integration")
    console.print("  3. Trading system performance (5-year backtest)")
    console.print()
    
    choice = input("Run benchmark? (yes/no) [yes]: ").strip().lower() or "yes"
    
    if choice not in ['yes', 'y']:
        print("Cancelled.")
        return
    
    # Part 1: LLM Benchmark
    llm_bench = LLMBenchmark()
    llm_bench.run_benchmark()
    
    # Part 2: Trading System Benchmark
    console.print()
    trading_choice = input("Run trading system benchmark? (yes/no) [yes]: ").strip().lower() or "yes"
    
    if trading_choice in ['yes', 'y']:
        trading_bench = TradingSystemBenchmark()
        trading_bench.run_quick_backtest()
    
    console.print("="*80)
    console.print("[bold green]✅ BENCHMARK COMPLETE![/bold green]")
    console.print("="*80)
    console.print()


if __name__ == "__main__":
    main()
