#!/usr/bin/env python3
"""
Run All Benchmarks and Backtests for Prometheus
Comprehensive testing suite to validate system performance
"""

import asyncio
import sys
import time
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

class ComprehensiveTestRunner:
    def __init__(self):
        self.results = {
            'benchmarks': {},
            'backtests': {},
            'performance': {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_duration = {}

    def _write_error_artifact(self, context: str, error: Exception):
        """Persist full crash details for intermittent benchmark orchestration failures."""
        try:
            logs_dir = Path("logs")
            logs_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            error_file = logs_dir / f"all_benchmarks_backtests_error_{ts}.log"
            trace_text = traceback.format_exc()
            with error_file.open('w', encoding='utf-8') as f:
                f.write("PROMETHEUS Benchmark/Backtest Orchestrator Failure\n")
                f.write("=" * 72 + "\n")
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Context: {context}\n")
                f.write(f"Error: {error}\n\n")
                f.write("Traceback:\n")
                f.write(trace_text)
            print(f"🧾 Error details saved to: {error_file}")
        except Exception as log_error:
            print(f"⚠️ Failed to write error artifact: {log_error}")
        
    def print_header(self, text):
        print()
        print("=" * 80)
        print(text)
        print("=" * 80)
        print()
    
    def run_benchmark(self, name, script_path, description):
        """Run a benchmark script"""
        self.print_header(f"BENCHMARK: {name}")
        print(f"Description: {description}")
        print(f"Script: {script_path}")
        print()
        
        if not Path(script_path).exists():
            print(f"[SKIP] {script_path} not found")
            return None
        
        start_time = time.time()
        try:
            import subprocess
            env = dict(__import__('os').environ)
            env['PYTHONIOENCODING'] = 'utf-8'
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                env=env,
                timeout=300  # 5 minute timeout per test
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print("[OK] Benchmark completed successfully")
                print(f"Duration: {duration:.2f} seconds")
                print()
                if result.stdout:
                    print("Output:")
                    print(result.stdout[-1000:])  # Last 1000 chars
                return {
                    'status': 'success',
                    'duration': duration,
                    'output': result.stdout[-500:] if result.stdout else ''
                }
            else:
                print(f"[WARNING] Benchmark had issues (return code: {result.returncode})")
                print(f"Duration: {duration:.2f} seconds")
                if result.stderr:
                    print("Errors:")
                    print(result.stderr[-500:])
                return {
                    'status': 'warning',
                    'duration': duration,
                    'error': result.stderr[-500:] if result.stderr else ''
                }
        except subprocess.TimeoutExpired:
            print("[ERROR] Benchmark timed out after 5 minutes")
            self._write_error_artifact(f"run_benchmark timeout: {name}", TimeoutError("Benchmark timed out after 5 minutes"))
            return {'status': 'timeout', 'duration': 300}
        except Exception as e:
            print(f"[ERROR] Benchmark failed: {e}")
            self._write_error_artifact(f"run_benchmark exception: {name}", e)
            return {'status': 'error', 'error': str(e)}
    
    async def run_async_benchmark(self, name, module_path, function_name, description):
        """Run an async benchmark"""
        self.print_header(f"BENCHMARK: {name}")
        print(f"Description: {description}")
        print()
        
        start_time = time.time()
        try:
            # Import and run async function
            import importlib
            module = importlib.import_module(module_path.replace('.py', '').replace('/', '.'))
            func = getattr(module, function_name)
            
            result = await func()
            duration = time.time() - start_time
            
            print("[OK] Benchmark completed successfully")
            print(f"Duration: {duration:.2f} seconds")
            print()
            
            return {
                'status': 'success',
                'duration': duration,
                'result': result
            }
        except Exception as e:
            duration = time.time() - start_time
            print(f"[ERROR] Benchmark failed: {e}")
            return {
                'status': 'error',
                'duration': duration,
                'error': str(e)
            }
    
    def run_system_performance_benchmark(self):
        """Run system performance benchmarks"""
        self.print_header("SYSTEM PERFORMANCE BENCHMARK")
        
        import psutil
        import time
        
        metrics = {}
        
        # CPU benchmark
        print("Testing CPU performance...")
        start = time.time()
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_time = time.time() - start
        metrics['cpu'] = {
            'usage_percent': cpu_percent,
            'test_duration': cpu_time
        }
        print(f"  CPU Usage: {cpu_percent:.1f}%")
        
        # Memory benchmark
        print("Testing memory performance...")
        memory = psutil.virtual_memory()
        metrics['memory'] = {
            'used_percent': memory.percent,
            'used_gb': memory.used / (1024**3),
            'total_gb': memory.total / (1024**3)
        }
        print(f"  Memory: {memory.percent:.1f}% used ({memory.used / (1024**3):.1f} GB / {memory.total / (1024**3):.1f} GB)")
        
        # Database performance
        print("Testing database performance...")
        try:
            import sqlite3
            db_path = "prometheus_trading.db"
            if Path(db_path).exists():
                start = time.time()
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                conn.close()
                db_time = time.time() - start
                metrics['database'] = {
                    'connection_time': db_time,
                    'tables': table_count
                }
                print(f"  Database: {table_count} tables, connection time: {db_time*1000:.2f}ms")
        except Exception as e:
            print(f"  Database test failed: {e}")
        
        self.results['performance']['system'] = metrics
        return metrics
    
    def run_ai_performance_benchmark(self):
        """Run AI system performance benchmarks"""
        self.print_header("AI SYSTEM PERFORMANCE BENCHMARK")
        
        metrics = {}
        
        # Test CPT-OSS
        print("Testing CPT-OSS...")
        try:
            from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
            start = time.time()
            gpt_oss = GPTOSSTradingAdapter()
            init_time = time.time() - start
            metrics['cpt_oss'] = {
                'initialization_time': init_time,
                'available': True,
                'model_size': getattr(gpt_oss, 'model_size', '20b')
            }
            print(f"  CPT-OSS: Available (Model: {metrics['cpt_oss']['model_size']})")
            print(f"  Initialization: {init_time:.2f} seconds")
        except Exception as e:
            metrics['cpt_oss'] = {'available': False, 'error': str(e)[:50]}
            print(f"  CPT-OSS: Not available ({str(e)[:50]})")
        
        # Test Universal Reasoning Engine
        print("Testing Universal Reasoning Engine...")
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            start = time.time()
            engine = UniversalReasoningEngine()
            init_time = time.time() - start
            metrics['reasoning_engine'] = {
                'initialization_time': init_time,
                'available': True
            }
            print(f"  Reasoning Engine: Available")
            print(f"  Initialization: {init_time:.2f} seconds")
        except Exception as e:
            metrics['reasoning_engine'] = {'available': False, 'error': str(e)[:50]}
            print(f"  Reasoning Engine: Not available ({str(e)[:50]})")
        
        # Test Market Oracle
        print("Testing Market Oracle...")
        try:
            from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
            start = time.time()
            oracle = MarketOracleEngine({})
            init_time = time.time() - start
            metrics['market_oracle'] = {
                'initialization_time': init_time,
                'available': True
            }
            print(f"  Market Oracle: Available")
            print(f"  Initialization: {init_time:.2f} seconds")
        except Exception as e:
            metrics['market_oracle'] = {'available': False, 'error': str(e)[:50]}
            print(f"  Market Oracle: Not available ({str(e)[:50]})")
        
        self.results['performance']['ai'] = metrics
        return metrics
    
    def run_trading_engine_benchmark(self):
        """Run trading engine benchmarks"""
        self.print_header("TRADING ENGINE BENCHMARK")
        
        metrics = {}
        
        # Test Alpaca connection
        print("Testing Alpaca broker...")
        try:
            import alpaca_trade_api as tradeapi
            from dotenv import load_dotenv
            import os
            load_dotenv()
            
            api_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY')
            secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET')
            
            if api_key and secret_key:
                start = time.time()
                api = tradeapi.REST(api_key, secret_key, 'https://api.alpaca.markets', api_version='v2')
                account = api.get_account()
                connection_time = time.time() - start
                
                metrics['alpaca'] = {
                    'connected': True,
                    'connection_time': connection_time,
                    'account_status': account.status,
                    'portfolio_value': float(account.portfolio_value)
                }
                print(f"  Alpaca: Connected ({connection_time:.2f}s)")
                print(f"  Account: {account.account_number}")
                print(f"  Portfolio: ${float(account.portfolio_value):,.2f}")
            else:
                metrics['alpaca'] = {'connected': False, 'reason': 'No credentials'}
                print("  Alpaca: No credentials")
        except Exception as e:
            metrics['alpaca'] = {'connected': False, 'error': str(e)[:50]}
            print(f"  Alpaca: Connection failed ({str(e)[:50]})")
        
        # Test IB Gateway
        print("Testing IB Gateway...")
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            start = time.time()
            result = sock.connect_ex(('127.0.0.1', 7497))
            sock.close()
            connection_time = time.time() - start
            
            metrics['ib_gateway'] = {
                'port_open': result == 0,
                'connection_time': connection_time,
                'port': 7497
            }
            if result == 0:
                print(f"  IB Gateway: Port open ({connection_time*1000:.2f}ms)")
            else:
                print("  IB Gateway: Port closed")
        except Exception as e:
            metrics['ib_gateway'] = {'port_open': False, 'error': str(e)[:50]}
            print(f"  IB Gateway: Test failed ({str(e)[:50]})")
        
        self.results['performance']['trading'] = metrics
        return metrics
    
    async def run_all_tests(self):
        """Run all benchmarks and backtests"""
        print("=" * 80)
        print("PROMETHEUS COMPREHENSIVE BENCHMARK & BACKTEST SUITE")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_start = time.time()
        
        # 1. System Performance Benchmarks
        self.run_system_performance_benchmark()
        
        # 2. AI Performance Benchmarks
        self.run_ai_performance_benchmark()
        
        # 3. Trading Engine Benchmarks
        self.run_trading_engine_benchmark()
        
        # 4. Run comprehensive benchmarks
        print()
        self.print_header("RUNNING COMPREHENSIVE BENCHMARKS")
        
        benchmark_scripts = [
            ('Comprehensive Benchmarking System', 'prometheus_comprehensive_benchmarking_system.py', 
             'Full system benchmarking suite'),
            ('Industry Benchmark', 'industry_leading_benchmark.py', 
             'Industry comparison benchmarks'),
            ('Intelligence Benchmark', 'intelligence_benchmark.py', 
             'AI intelligence benchmarks'),
            ('Performance Benchmarking', 'performance_benchmarking_suite.py', 
             'Performance metrics'),
        ]
        
        for name, script, desc in benchmark_scripts:
            result = self.run_benchmark(name, script, desc)
            if result:
                self.results['benchmarks'][name] = result
            time.sleep(2)  # Brief pause between tests
        
        # 5. Run backtests
        print()
        self.print_header("RUNNING BACKTESTS")
        
        backtest_scripts = [
            ('Historical Backtest', 'prometheus_historical_backtest.py', 
             'Historical data backtesting'),
            ('Enhanced Backtest', 'prometheus_enhanced_backtest.py', 
             'Enhanced backtesting with full features'),
            ('Comprehensive Backtest Benchmark', 'comprehensive_backtest_benchmark.py', 
             'Comprehensive backtest comparison'),
        ]
        
        for name, script, desc in backtest_scripts:
            result = self.run_benchmark(name, script, desc)
            if result:
                self.results['backtests'][name] = result
            time.sleep(2)  # Brief pause between tests
        
        total_duration = time.time() - total_start
        
        # Generate report
        self.generate_report(total_duration)
        
        return self.results
    
    def generate_report(self, total_duration):
        """Generate comprehensive test report"""
        self.print_header("COMPREHENSIVE TEST REPORT")
        
        print("TEST SUMMARY:")
        print()
        
        # Performance metrics
        if 'performance' in self.results:
            print("PERFORMANCE METRICS:")
            perf = self.results['performance']
            
            if 'system' in perf:
                sys_perf = perf['system']
                print(f"  CPU Usage: {sys_perf.get('cpu', {}).get('usage_percent', 'N/A')}%")
                print(f"  Memory: {sys_perf.get('memory', {}).get('used_percent', 'N/A')}%")
            
            if 'ai' in perf:
                ai_perf = perf['ai']
                print(f"  CPT-OSS: {'Available' if ai_perf.get('cpt_oss', {}).get('available') else 'Not Available'}")
                print(f"  Reasoning Engine: {'Available' if ai_perf.get('reasoning_engine', {}).get('available') else 'Not Available'}")
                print(f"  Market Oracle: {'Available' if ai_perf.get('market_oracle', {}).get('available') else 'Not Available'}")
            
            if 'trading' in perf:
                trading_perf = perf['trading']
                print(f"  Alpaca: {'Connected' if trading_perf.get('alpaca', {}).get('connected') else 'Not Connected'}")
                print(f"  IB Gateway: {'Open' if trading_perf.get('ib_gateway', {}).get('port_open') else 'Closed'}")
        
        print()
        
        # Benchmark results
        print("BENCHMARK RESULTS:")
        print()
        for name, result in self.results['benchmarks'].items():
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)
            icon = "[OK]" if status == 'success' else "[WARNING]" if status == 'warning' else "[ERROR]"
            print(f"  {icon} {name}: {status} ({duration:.2f}s)")
        
        print()
        
        # Backtest results
        print("BACKTEST RESULTS:")
        print()
        for name, result in self.results['backtests'].items():
            status = result.get('status', 'unknown')
            duration = result.get('duration', 0)
            icon = "[OK]" if status == 'success' else "[WARNING]" if status == 'warning' else "[ERROR]"
            print(f"  {icon} {name}: {status} ({duration:.2f}s)")
        
        print()
        print("=" * 80)
        print(f"TOTAL TEST DURATION: {total_duration:.2f} seconds")
        print("=" * 80)
        
        # Save results
        report_file = Path("benchmark_backtest_results.json")
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print()
        print(f"Detailed results saved to: {report_file}")
        print()

async def main():
    runner = ComprehensiveTestRunner()
    try:
        await runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        traceback.print_exc()
        runner._write_error_artifact("main execution", e)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

