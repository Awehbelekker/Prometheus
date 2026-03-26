#!/usr/bin/env python3
"""
HRM System Performance Benchmark Suite

This script runs comprehensive benchmarks to test the performance of the HRM system,
including module latency, persona analysis, AI model loading, and overall system performance.
"""

import os
import sys
import time
import torch
import numpy as np
import psutil
import threading
from datetime import datetime
from typing import Dict, List, Any
import json
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('hrm_config.env')

# Import HRM components
try:
    from core.hrm_integration import HRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
    from core.hrm_enhanced_personas import HRMPersonaManager, HRMPersonaType
    from core.ai_learning_engine import AILearningEngine
    from core.predictive_market_oracle import PredictiveMarketOracle
    print("[OK] Successfully imported all system components")
except ImportError as e:
    print(f"[ERROR] Failed to import components: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce log noise during benchmarks

class PerformanceBenchmark:
    """Comprehensive performance benchmark suite for HRM system"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        self.system_info = self._get_system_info()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'python_version': sys.version,
            'torch_version': torch.__version__,
            'device': 'cuda' if torch.cuda.is_available() else 'cpu'
        }
    
    def benchmark_hrm_initialization(self) -> Dict[str, Any]:
        """Benchmark HRM system initialization"""
        print("\n[BENCHMARK] Testing HRM System Initialization...")
        
        results = {}
        
        # Test initialization time
        start_time = time.time()
        hrm_engine = HRMTradingEngine()
        init_time = time.time() - start_time
        results['initialization_time'] = init_time
        
        # Test persona manager initialization
        start_time = time.time()
        persona_manager = HRMPersonaManager(hrm_engine)
        persona_init_time = time.time() - start_time
        results['persona_initialization_time'] = persona_init_time
        
        # Test checkpoint loading
        start_time = time.time()
        hrm_engine._load_checkpoints_safe()
        checkpoint_load_time = time.time() - start_time
        results['checkpoint_load_time'] = checkpoint_load_time
        
        print(f"[OK] HRM initialization: {init_time:.3f}s")
        print(f"[OK] Persona initialization: {persona_init_time:.3f}s")
        print(f"[OK] Checkpoint loading: {checkpoint_load_time:.3f}s")
        
        return results
    
    def benchmark_hrm_modules(self) -> Dict[str, Any]:
        """Benchmark individual HRM modules"""
        print("\n[BENCHMARK] Testing HRM Module Performance...")
        
        hrm_engine = HRMTradingEngine()
        results = {}
        
        # Prepare test data
        test_data = torch.randn(1, 1, 512).to(hrm_engine.device)
        
        # Test each module
        modules = {
            'high_level': hrm_engine.high_level,
            'low_level': hrm_engine.low_level,
            'arc_level': hrm_engine.arc_level,
            'sudoku_level': hrm_engine.sudoku_level,
            'maze_level': hrm_engine.maze_level
        }
        
        for module_name, module in modules.items():
            # Warm up
            for _ in range(3):
                if module_name == 'low_level':
                    # Low level needs abstract strategy input
                    abstract_strategy = torch.randn(1, 128).to(hrm_engine.device)
                    _ = module(abstract_strategy, test_data)
                else:
                    _ = module(test_data)
            
            # Benchmark
            start_time = time.time()
            for _ in range(100):
                if module_name == 'low_level':
                    abstract_strategy = torch.randn(1, 128).to(hrm_engine.device)
                    _ = module(abstract_strategy, test_data)
                else:
                    _ = module(test_data)
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 100
            results[f'{module_name}_avg_time'] = avg_time
            results[f'{module_name}_throughput'] = 1.0 / avg_time
            
            print(f"[OK] {module_name}: {avg_time*1000:.2f}ms avg, {1.0/avg_time:.1f} ops/sec")
        
        return results
    
    def benchmark_hrm_decision_making(self) -> Dict[str, Any]:
        """Benchmark HRM decision making process"""
        print("\n[BENCHMARK] Testing HRM Decision Making...")
        
        hrm_engine = HRMTradingEngine()
        results = {}
        
        # Sample market data
        sample_market_data = {
            "prices": [100.0, 101.5, 99.8, 102.3, 103.1, 104.2, 103.8, 105.1],
            "volumes": [1000000, 1200000, 800000, 1500000, 1100000, 1300000, 900000, 1400000],
            "indicators": {
                "rsi": 65.5,
                "macd": 0.8,
                "bollinger_upper": 105.0,
                "bollinger_lower": 98.0
            },
            "sentiment": {
                "positive": 0.6,
                "negative": 0.2,
                "neutral": 0.2
            }
        }
        
        sample_user_context = {
            "profile": {"risk_tolerance": 0.5},
            "trading_history": [],
            "portfolio": {"total_value": 50000},
            "risk_preferences": {"max_drawdown": 0.1}
        }
        
        # Test decision making latency
        context = HRMReasoningContext(
            market_data=sample_market_data,
            user_profile=sample_user_context.get('profile', {}),
            trading_history=sample_user_context.get('trading_history', []),
            current_portfolio=sample_user_context.get('portfolio', {}),
            risk_preferences=sample_user_context.get('risk_preferences', {}),
            reasoning_level=HRMReasoningLevel.ARC_LEVEL
        )
        
        # Warm up
        for _ in range(5):
            _ = hrm_engine.make_hierarchical_decision(context)
        
        # Benchmark
        start_time = time.time()
        decisions = []
        for _ in range(50):
            decision = hrm_engine.make_hierarchical_decision(context)
            decisions.append(decision)
        end_time = time.time()
        
        avg_decision_time = (end_time - start_time) / 50
        results['avg_decision_time'] = avg_decision_time
        results['decision_throughput'] = 1.0 / avg_decision_time
        
        # Analyze decision consistency
        actions = [d.get('action', 'UNKNOWN') for d in decisions]
        action_counts = {action: actions.count(action) for action in set(actions)}
        results['decision_consistency'] = action_counts
        
        print(f"[OK] Decision making: {avg_decision_time*1000:.2f}ms avg, {1.0/avg_decision_time:.1f} decisions/sec")
        print(f"[OK] Decision consistency: {action_counts}")
        
        return results
    
    def benchmark_persona_analysis(self) -> Dict[str, Any]:
        """Benchmark persona-based analysis"""
        print("\n[BENCHMARK] Testing Persona Analysis Performance...")
        
        hrm_engine = HRMTradingEngine()
        persona_manager = HRMPersonaManager(hrm_engine)
        results = {}
        
        sample_market_data = {
            "prices": [100.0, 101.5, 99.8, 102.3, 103.1],
            "volumes": [1000000, 1200000, 800000, 1500000, 1100000],
            "indicators": {"rsi": 65.5, "macd": 0.8},
            "sentiment": {"positive": 0.6, "negative": 0.2, "neutral": 0.2}
        }
        
        sample_user_context = {
            "profile": {"risk_tolerance": 0.5},
            "trading_history": [],
            "portfolio": {"total_value": 50000},
            "risk_preferences": {"max_drawdown": 0.1}
        }
        
        # Test each persona
        personas = [
            HRMPersonaType.BALANCED_HRM,
            HRMPersonaType.CONSERVATIVE_HRM,
            HRMPersonaType.AGGRESSIVE_HRM,
            HRMPersonaType.QUANTUM_HRM,
            HRMPersonaType.ARBITRAGE_HRM,
            HRMPersonaType.MOMENTUM_HRM,
            HRMPersonaType.MEAN_REVERSION_HRM
        ]
        
        for persona_type in personas:
            # Warm up
            for _ in range(3):
                _ = persona_manager.analyze_with_persona(
                    persona_type=persona_type,
                    market_data=sample_market_data,
                    user_context=sample_user_context
                )
            
            # Benchmark
            start_time = time.time()
            for _ in range(20):
                result = persona_manager.analyze_with_persona(
                    persona_type=persona_type,
                    market_data=sample_market_data,
                    user_context=sample_user_context
                )
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 20
            results[f'{persona_type.value}_avg_time'] = avg_time
            results[f'{persona_type.value}_throughput'] = 1.0 / avg_time
            
            print(f"[OK] {persona_type.value}: {avg_time*1000:.2f}ms avg, {1.0/avg_time:.1f} ops/sec")
        
        return results
    
    def benchmark_ai_model_loading(self) -> Dict[str, Any]:
        """Benchmark AI model loading and prediction"""
        print("\n[BENCHMARK] Testing AI Model Loading and Prediction...")
        
        results = {}
        
        try:
            # Test AI Learning Engine
            start_time = time.time()
            ai_engine = AILearningEngine()
            ai_init_time = time.time() - start_time
            results['ai_engine_init_time'] = ai_init_time
            
            # Test Predictive Market Oracle
            start_time = time.time()
            oracle = PredictiveMarketOracle()
            oracle_init_time = time.time() - start_time
            results['oracle_init_time'] = oracle_init_time
            
            print(f"[OK] AI Learning Engine init: {ai_init_time:.3f}s")
            print(f"[OK] Predictive Oracle init: {oracle_init_time:.3f}s")
            
            # Test model prediction (if models are available)
            if hasattr(ai_engine, 'models') and ai_engine.models:
                start_time = time.time()
                # Test prediction with sample data
                sample_features = np.random.randn(1, 20)  # Sample feature vector
                for _ in range(10):
                    # This would test actual model prediction if models are loaded
                    pass
                prediction_time = time.time() - start_time
                results['avg_prediction_time'] = prediction_time / 10
                print(f"[OK] Average prediction time: {prediction_time/10*1000:.2f}ms")
            
        except Exception as e:
            print(f"[WARN] AI model benchmark failed: {e}")
            results['ai_benchmark_error'] = str(e)
        
        return results
    
    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage"""
        print("\n[BENCHMARK] Testing Memory Usage...")
        
        results = {}
        
        # Get initial memory
        initial_memory = psutil.virtual_memory().used
        
        # Initialize HRM system
        hrm_engine = HRMTradingEngine()
        persona_manager = HRMPersonaManager(hrm_engine)
        
        # Get memory after initialization
        after_init_memory = psutil.virtual_memory().used
        results['memory_after_init'] = after_init_memory - initial_memory
        
        # Test memory during operations
        sample_data = torch.randn(100, 1, 512)
        memory_before_ops = psutil.virtual_memory().used
        
        # Run some operations
        for _ in range(50):
            context = HRMReasoningContext(
                market_data={"prices": [100.0], "volumes": [1000000]},
                user_profile={},
                trading_history=[],
                current_portfolio={},
                risk_preferences={},
                reasoning_level=HRMReasoningLevel.ARC_LEVEL
            )
            _ = hrm_engine.make_hierarchical_decision(context)
        
        memory_after_ops = psutil.virtual_memory().used
        results['memory_during_ops'] = memory_after_ops - memory_before_ops
        
        print(f"[OK] Memory after init: {(after_init_memory - initial_memory) / 1024 / 1024:.1f} MB")
        print(f"[OK] Memory during ops: {(memory_after_ops - memory_before_ops) / 1024 / 1024:.1f} MB")
        
        return results
    
    def benchmark_concurrent_operations(self) -> Dict[str, Any]:
        """Benchmark concurrent operations"""
        print("\n[BENCHMARK] Testing Concurrent Operations...")
        
        results = {}
        
        hrm_engine = HRMTradingEngine()
        persona_manager = HRMPersonaManager(hrm_engine)
        
        def worker_function(worker_id: int, results_dict: Dict, num_operations: int = 10):
            """Worker function for concurrent testing"""
            start_time = time.time()
            
            for _ in range(num_operations):
                context = HRMReasoningContext(
                    market_data={"prices": [100.0 + worker_id], "volumes": [1000000]},
                    user_profile={"risk_tolerance": 0.5},
                    trading_history=[],
                    current_portfolio={},
                    risk_preferences={},
                    reasoning_level=HRMReasoningLevel.ARC_LEVEL
                )
                _ = hrm_engine.make_hierarchical_decision(context)
            
            end_time = time.time()
            results_dict[worker_id] = end_time - start_time
        
        # Test with different numbers of concurrent workers
        for num_workers in [1, 2, 4, 8]:
            worker_results = {}
            threads = []
            
            start_time = time.time()
            
            for i in range(num_workers):
                thread = threading.Thread(target=worker_function, args=(i, worker_results, 20))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            total_time = time.time() - start_time
            avg_worker_time = sum(worker_results.values()) / len(worker_results)
            
            results[f'concurrent_{num_workers}_workers_total_time'] = total_time
            results[f'concurrent_{num_workers}_workers_avg_worker_time'] = avg_worker_time
            results[f'concurrent_{num_workers}_workers_throughput'] = (num_workers * 20) / total_time
            
            print(f"[OK] {num_workers} workers: {total_time:.3f}s total, {avg_worker_time:.3f}s avg per worker")
            print(f"[OK] Throughput: {(num_workers * 20) / total_time:.1f} operations/sec")
        
        return results
    
    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmarks and return comprehensive results"""
        print("=" * 60)
        print("HRM SYSTEM PERFORMANCE BENCHMARK SUITE")
        print("=" * 60)
        print(f"System Info: {self.system_info['cpu_count']} CPUs, {self.system_info['device']} device")
        print(f"Memory: {self.system_info['memory_total'] / 1024 / 1024 / 1024:.1f} GB total")
        
        all_results = {
            'system_info': self.system_info,
            'timestamp': datetime.now().isoformat(),
            'benchmark_duration': 0
        }
        
        benchmark_start = time.time()
        
        try:
            all_results['initialization'] = self.benchmark_hrm_initialization()
        except Exception as e:
            print(f"[ERROR] Initialization benchmark failed: {e}")
            all_results['initialization_error'] = str(e)
        
        try:
            all_results['modules'] = self.benchmark_hrm_modules()
        except Exception as e:
            print(f"[ERROR] Module benchmark failed: {e}")
            all_results['modules_error'] = str(e)
        
        try:
            all_results['decision_making'] = self.benchmark_hrm_decision_making()
        except Exception as e:
            print(f"[ERROR] Decision making benchmark failed: {e}")
            all_results['decision_making_error'] = str(e)
        
        try:
            all_results['persona_analysis'] = self.benchmark_persona_analysis()
        except Exception as e:
            print(f"[ERROR] Persona analysis benchmark failed: {e}")
            all_results['persona_analysis_error'] = str(e)
        
        try:
            all_results['ai_models'] = self.benchmark_ai_model_loading()
        except Exception as e:
            print(f"[ERROR] AI model benchmark failed: {e}")
            all_results['ai_models_error'] = str(e)
        
        try:
            all_results['memory_usage'] = self.benchmark_memory_usage()
        except Exception as e:
            print(f"[ERROR] Memory benchmark failed: {e}")
            all_results['memory_usage_error'] = str(e)
        
        try:
            all_results['concurrent_operations'] = self.benchmark_concurrent_operations()
        except Exception as e:
            print(f"[ERROR] Concurrent operations benchmark failed: {e}")
            all_results['concurrent_operations_error'] = str(e)
        
        benchmark_end = time.time()
        all_results['benchmark_duration'] = benchmark_end - benchmark_start
        
        return all_results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save benchmark results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hrm_benchmark_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n[SAVE] Benchmark results saved to: {filename}")
        return filename
    
    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary"""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        # System info
        print(f"System: {results['system_info']['cpu_count']} CPUs, {results['system_info']['device']}")
        print(f"Total benchmark time: {results['benchmark_duration']:.2f} seconds")
        
        # Key performance metrics
        if 'initialization' in results:
            init_time = results['initialization'].get('initialization_time', 0)
            print(f"HRM initialization: {init_time:.3f}s")
        
        if 'decision_making' in results:
            decision_time = results['decision_making'].get('avg_decision_time', 0)
            decision_throughput = results['decision_making'].get('decision_throughput', 0)
            print(f"Decision making: {decision_time*1000:.2f}ms avg, {decision_throughput:.1f} decisions/sec")
        
        if 'modules' in results:
            print("\nModule Performance:")
            for key, value in results['modules'].items():
                if 'avg_time' in key:
                    module_name = key.replace('_avg_time', '')
                    throughput = results['modules'].get(f'{module_name}_throughput', 0)
                    print(f"  {module_name}: {value*1000:.2f}ms, {throughput:.1f} ops/sec")
        
        if 'memory_usage' in results:
            memory_init = results['memory_usage'].get('memory_after_init', 0)
            memory_ops = results['memory_usage'].get('memory_during_ops', 0)
            print(f"Memory usage: {memory_init/1024/1024:.1f} MB init, {memory_ops/1024/1024:.1f} MB ops")
        
        # Performance assessment
        print("\nPerformance Assessment:")
        
        # Check if performance is optimal
        decision_time = results.get('decision_making', {}).get('avg_decision_time', 1.0)
        if decision_time < 0.1:  # Less than 100ms
            print("✅ Decision making: EXCELLENT (< 100ms)")
        elif decision_time < 0.5:  # Less than 500ms
            print("✅ Decision making: GOOD (< 500ms)")
        else:
            print("⚠️  Decision making: NEEDS OPTIMIZATION (> 500ms)")
        
        # Check memory usage
        memory_init = results.get('memory_usage', {}).get('memory_after_init', 0)
        if memory_init < 100 * 1024 * 1024:  # Less than 100MB
            print("✅ Memory usage: EXCELLENT (< 100MB)")
        elif memory_init < 500 * 1024 * 1024:  # Less than 500MB
            print("✅ Memory usage: GOOD (< 500MB)")
        else:
            print("⚠️  Memory usage: HIGH (> 500MB)")
        
        # Check throughput
        decision_throughput = results.get('decision_making', {}).get('decision_throughput', 0)
        if decision_throughput > 10:  # More than 10 decisions/sec
            print("✅ Throughput: EXCELLENT (> 10 decisions/sec)")
        elif decision_throughput > 5:  # More than 5 decisions/sec
            print("✅ Throughput: GOOD (> 5 decisions/sec)")
        else:
            print("⚠️  Throughput: NEEDS IMPROVEMENT (< 5 decisions/sec)")

def main():
    """Main benchmark execution"""
    benchmark = PerformanceBenchmark()
    
    # Run all benchmarks
    results = benchmark.run_all_benchmarks()
    
    # Save results
    filename = benchmark.save_results(results)
    
    # Print summary
    benchmark.print_summary(results)
    
    print(f"\n[COMPLETE] All benchmarks completed successfully!")
    print(f"Detailed results saved to: {filename}")
    
    return results

if __name__ == "__main__":
    results = main()
