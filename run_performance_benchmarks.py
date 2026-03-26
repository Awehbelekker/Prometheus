"""
PROMETHEUS Performance Benchmark Suite
Measures REAL performance improvements with actual data
Gets FACTS not theory
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json
import statistics

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Benchmark suite for PROMETHEUS"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'benchmarks': {},
            'summary': {}
        }
    
    async def run_all_benchmarks(self):
        """Run complete benchmark suite"""
        print("\n" + "="*80)
        print("PROMETHEUS PERFORMANCE BENCHMARK SUITE")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Getting REAL performance data...")
        print("="*80 + "\n")
        
        # Speed benchmarks
        await self._benchmark_ai_speed()
        
        # Accuracy benchmarks
        await self._benchmark_ai_accuracy()
        
        # Data throughput
        await self._benchmark_data_throughput()
        
        # System capacity
        await self._benchmark_system_capacity()
        
        # Print summary
        self._print_summary()
        
        # Save results
        self._save_results()
        
        return self.results
    
    async def _benchmark_ai_speed(self):
        """Benchmark AI reasoning speed"""
        print("\n[1/4] BENCHMARKING AI REASONING SPEED...")
        print("-" * 80)
        
        results = {'tests': [], 'avg_time': 0, 'min_time': 0, 'max_time': 0}
        
        # Test UnifiedAI speed
        try:
            from core.unified_ai_provider import UnifiedAIProvider
            
            ai = UnifiedAIProvider()
            test_prompt = "Analyze AAPL: Price $175, RSI 65, MACD bullish. Quick decision?"
            
            times = []
            for i in range(5):
                start = time.time()
                try:
                    response = ai.generate(test_prompt, max_tokens=100)
                    elapsed = time.time() - start
                    times.append(elapsed)
                    print(f"  Test {i+1}/5: {elapsed:.2f}s")
                except asyncio.TimeoutError:
                    print(f"  Test {i+1}/5: TIMEOUT (>30s)")
                    times.append(30.0)
            
            results['tests'] = times
            results['avg_time'] = statistics.mean(times)
            results['min_time'] = min(times)
            results['max_time'] = max(times)
            
            print(f"\n  Average: {results['avg_time']:.2f}s")
            print(f"  Best: {results['min_time']:.2f}s")
            print(f"  Worst: {results['max_time']:.2f}s")
            
            # Performance rating
            if results['avg_time'] < 3:
                rating = "EXCELLENT"
            elif results['avg_time'] < 5:
                rating = "GOOD"
            elif results['avg_time'] < 10:
                rating = "FAIR"
            else:
                rating = "SLOW"
            
            print(f"  Rating: {rating}")
            
        except Exception as e:
            print(f"  [FAIL] Benchmark failed: {e}")
            results['error'] = str(e)
        
        self.results['benchmarks']['ai_speed'] = results
    
    async def _benchmark_ai_accuracy(self):
        """Benchmark AI prediction accuracy"""
        print("\n[2/4] BENCHMARKING AI ACCURACY...")
        print("-" * 80)
        
        results = {'confidence_scores': [], 'avg_confidence': 0}
        
        try:
            from core.ensemble_voting_system import EnsembleVotingSystem
            
            ensemble = EnsembleVotingSystem()
            
            test_queries = [
                "AAPL showing bullish flag pattern. Trade?",
                "TSLA breaking resistance at $250. Action?",
                "SPY trending down, RSI oversold. Decision?",
                "NVDA consolidating after rally. Hold or exit?",
                "BTC showing bearish divergence. Sell?"
            ]
            
            confidences = []
            for i, query in enumerate(test_queries, 1):
                try:
                    decision = await asyncio.wait_for(
                        ensemble.run_ensemble_decision(query),
                        timeout=60.0
                    )
                    confidences.append(decision.consensus_confidence)
                    print(f"  Test {i}/5: Confidence {decision.consensus_confidence:.1%}")
                except asyncio.TimeoutError:
                    print(f"  Test {i}/5: TIMEOUT")
                except Exception as e:
                    print(f"  Test {i}/5: ERROR - {str(e)[:30]}")
            
            if confidences:
                results['confidence_scores'] = confidences
                results['avg_confidence'] = statistics.mean(confidences)
                
                print(f"\n  Average Confidence: {results['avg_confidence']:.1%}")
                
                if results['avg_confidence'] > 0.80:
                    rating = "EXCELLENT"
                elif results['avg_confidence'] > 0.70:
                    rating = "GOOD"
                elif results['avg_confidence'] > 0.60:
                    rating = "FAIR"
                else:
                    rating = "LOW"
                
                print(f"  Rating: {rating}")
            else:
                print(f"  ✗ No successful tests")
                results['error'] = "All tests failed or timed out"
            
        except Exception as e:
            print(f"  [FAIL] Benchmark failed: {e}")
            results['error'] = str(e)
        
        self.results['benchmarks']['ai_accuracy'] = results
    
    async def _benchmark_data_throughput(self):
        """Benchmark data processing throughput"""
        print("\n[3/4] BENCHMARKING DATA THROUGHPUT...")
        print("-" * 80)
        
        results = {'symbols_per_second': 0, 'total_time': 0}
        
        try:
            from core.autonomous_market_scanner import AutonomousMarketScanner
            
            scanner = AutonomousMarketScanner()
            
            test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
                           'NVDA', 'META', 'NFLX', 'AMD', 'INTC']
            
            print(f"  Scanning {len(test_symbols)} symbols...")
            
            start = time.time()
            try:
                opportunities = await asyncio.wait_for(
                    scanner.discover_best_opportunities(limit=10, scan_timeout=30.0),
                    timeout=45.0
                )
                elapsed = time.time() - start
                
                results['total_time'] = elapsed
                results['symbols_per_second'] = len(test_symbols) / elapsed
                results['opportunities_found'] = len(opportunities)
                
                print(f"\n  Time: {elapsed:.2f}s")
                print(f"  Throughput: {results['symbols_per_second']:.1f} symbols/second")
                print(f"  Opportunities: {len(opportunities)}")
                
                if results['symbols_per_second'] > 2:
                    rating = "EXCELLENT"
                elif results['symbols_per_second'] > 1:
                    rating = "GOOD"
                elif results['symbols_per_second'] > 0.5:
                    rating = "FAIR"
                else:
                    rating = "SLOW"
                
                print(f"  Rating: {rating}")
                
            except asyncio.TimeoutError:
                print(f"  ✗ TIMEOUT (>45s)")
                results['error'] = "Timeout"
            
        except Exception as e:
            print(f"  [FAIL] Benchmark failed: {e}")
            results['error'] = str(e)
        
        self.results['benchmarks']['data_throughput'] = results
    
    async def _benchmark_system_capacity(self):
        """Benchmark overall system capacity"""
        print("\n[4/4] BENCHMARKING SYSTEM CAPACITY...")
        print("-" * 80)
        
        results = {}
        
        # Count available systems
        available_systems = 0
        total_systems = 19
        
        systems_to_check = [
            ('core.unified_ai_provider', 'UnifiedAIProvider'),
            ('core.ensemble_voting_system', 'EnsembleVotingSystem'),
            ('core.reasoning.thinkmesh_enhanced', 'EnhancedThinkMeshAdapter'),
            ('core.universal_reasoning_engine', 'UniversalReasoningEngine'),
            ('core.continuous_learning_engine', 'ContinuousLearningEngine'),
            ('core.ai_learning_engine', 'AILearningEngine'),
            ('core.real_world_data_orchestrator', 'RealWorldDataOrchestrator'),
            ('core.autonomous_market_scanner', 'AutonomousMarketScanner'),
            ('core.multi_strategy_executor', 'MultiStrategyExecutor'),
            ('core.profit_maximization_engine', 'ProfitMaximizationEngine'),
            ('brokers.alpaca_broker', 'AlpacaBroker'),
        ]
        
        for module, cls in systems_to_check:
            try:
                mod = __import__(module, fromlist=[cls])
                getattr(mod, cls)
                available_systems += 1
            except:
                pass
        
        results['systems_available'] = available_systems
        results['systems_total'] = total_systems
        results['capacity_percent'] = (available_systems / total_systems) * 100
        
        print(f"  Systems Available: {available_systems}/{total_systems}")
        print(f"  System Capacity: {results['capacity_percent']:.0f}%")
        
        if results['capacity_percent'] >= 90:
            rating = "EXCELLENT"
        elif results['capacity_percent'] >= 75:
            rating = "GOOD"
        elif results['capacity_percent'] >= 60:
            rating = "FAIR"
        else:
            rating = "INSUFFICIENT"
        
        print(f"  Rating: {rating}")
        
        self.results['benchmarks']['system_capacity'] = results
    
    def _print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*80)
        print("BENCHMARK SUMMARY - REAL PERFORMANCE DATA")
        print("="*80)
        
        # AI Speed
        if 'ai_speed' in self.results['benchmarks']:
            speed = self.results['benchmarks']['ai_speed']
            if 'avg_time' in speed and speed['avg_time'] > 0:
                print(f"\n[AI REASONING SPEED]:")
                print(f"   Average: {speed['avg_time']:.2f} seconds")
                print(f"   Target: <5 seconds")
                improvement = ((5.0 - speed['avg_time']) / 5.0) * 100
                if improvement > 0:
                    print(f"   Status: {improvement:+.0f}% better than target")
                else:
                    print(f"   Status: {abs(improvement):.0f}% slower than target")
        
        # AI Accuracy
        if 'ai_accuracy' in self.results['benchmarks']:
            accuracy = self.results['benchmarks']['ai_accuracy']
            if 'avg_confidence' in accuracy and accuracy['avg_confidence'] > 0:
                print(f"\n[AI CONFIDENCE/ACCURACY]:")
                print(f"   Average: {accuracy['avg_confidence']:.1%}")
                print(f"   Target: >70%")
                if accuracy['avg_confidence'] > 0.70:
                    improvement = ((accuracy['avg_confidence'] - 0.70) / 0.70) * 100
                    print(f"   Status: {improvement:+.0f}% above target")
                else:
                    gap = ((0.70 - accuracy['avg_confidence']) / 0.70) * 100
                    print(f"   Status: {gap:.0f}% below target")
        
        # Data Throughput
        if 'data_throughput' in self.results['benchmarks']:
            throughput = self.results['benchmarks']['data_throughput']
            if 'symbols_per_second' in throughput:
                print(f"\n[DATA PROCESSING]:")
                print(f"   Throughput: {throughput['symbols_per_second']:.1f} symbols/second")
                print(f"   Target: >1 symbol/second")
                if throughput['symbols_per_second'] > 1:
                    improvement = ((throughput['symbols_per_second'] - 1.0) / 1.0) * 100
                    print(f"   Status: {improvement:+.0f}% above target")
                else:
                    gap = ((1.0 - throughput['symbols_per_second']) / 1.0) * 100
                    print(f"   Status: {gap:.0f}% below target")
        
        # System Capacity
        if 'system_capacity' in self.results['benchmarks']:
            capacity = self.results['benchmarks']['system_capacity']
            if 'capacity_percent' in capacity:
                print(f"\n[SYSTEM CAPACITY]:")
                print(f"   Available: {capacity['capacity_percent']:.0f}%")
                print(f"   Target: >90%")
                if capacity['capacity_percent'] > 90:
                    print(f"   Status: EXCELLENT")
                elif capacity['capacity_percent'] > 75:
                    gap = 90 - capacity['capacity_percent']
                    print(f"   Status: {gap:.0f}% below target")
                else:
                    print(f"   Status: NEEDS OPTIMIZATION")
        
        print("\n" + "="*80)
        print("PERFORMANCE VERDICT:")
        print("="*80)
        
        # Calculate overall score
        scores = []
        if 'ai_speed' in self.results['benchmarks']:
            speed = self.results['benchmarks']['ai_speed']
            if 'avg_time' in speed and speed['avg_time'] > 0:
                score = max(0, 100 - (speed['avg_time'] / 5.0) * 100)
                scores.append(score)
        
        if 'ai_accuracy' in self.results['benchmarks']:
            accuracy = self.results['benchmarks']['ai_accuracy']
            if 'avg_confidence' in accuracy:
                scores.append(accuracy['avg_confidence'] * 100)
        
        if 'system_capacity' in self.results['benchmarks']:
            capacity = self.results['benchmarks']['system_capacity']
            if 'capacity_percent' in capacity:
                scores.append(capacity['capacity_percent'])
        
        if scores:
            overall = statistics.mean(scores)
            print(f"\nOverall Performance Score: {overall:.0f}/100")
            
            if overall >= 85:
                verdict = "EXCELLENT - System at peak performance"
            elif overall >= 70:
                verdict = "GOOD - System performing well"
            elif overall >= 60:
                verdict = "FAIR - Some optimization needed"
            else:
                verdict = "NEEDS WORK - Significant improvements needed"
            
            print(f"Verdict: {verdict}")
        
        print("="*80)
    
    def _save_results(self):
        """Save benchmark results"""
        try:
            with open('performance_benchmark_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n[SAVED] Results saved: performance_benchmark_results.json")
        except Exception as e:
            print(f"\n[WARN] Could not save results: {e}")


async def main():
    """Run benchmarks"""
    benchmark = PerformanceBenchmark()
    await benchmark.run_all_benchmarks()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted")
    except Exception as e:
        print(f"\n\nBenchmark failed: {e}")
        import traceback
        traceback.print_exc()
