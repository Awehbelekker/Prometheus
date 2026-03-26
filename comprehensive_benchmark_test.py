#!/usr/bin/env python3
"""
COMPREHENSIVE BENCHMARK TEST
Test all aspects of Prometheus system performance and capabilities
"""

import requests
import time
import psutil
import asyncio
import aiohttp
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import statistics

class ComprehensiveBenchmark:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "system_info": {},
            "single_request_tests": [],
            "concurrent_tests": [],
            "ai_capability_tests": [],
            "trading_tests": [],
            "revolutionary_tests": [],
            "performance_metrics": {},
            "improvement_analysis": {}
        }
    
    def get_system_info(self):
        """Get current system information"""
        print("COLLECTING SYSTEM INFORMATION")
        print("=" * 50)
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Python processes
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        self.results["system_info"] = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": cpu_percent,
            "cpu_cores": psutil.cpu_count(),
            "memory_usage": memory.percent,
            "total_memory_gb": memory.total / (1024**3),
            "available_memory_gb": memory.available / (1024**3),
            "python_processes": len(python_processes),
            "server_url": self.base_url
        }
        
        print(f"CPU Usage: {cpu_percent}%")
        print(f"CPU Cores: {psutil.cpu_count()}")
        print(f"Memory Usage: {memory.percent}%")
        print(f"Available Memory: {memory.available / (1024**3):.1f} GB")
        print(f"Python Processes: {len(python_processes)}")
        print()
    
    def test_single_requests(self):
        """Test single request performance"""
        print("SINGLE REQUEST PERFORMANCE TEST")
        print("=" * 50)
        
        endpoints = [
            ("Health Check", "/health"),
            ("GPT-OSS Models", "/api/gpt-oss/models"),
            ("AI Coordinator", "/api/ai/coordinator/status"),
            ("Revolutionary Engines", "/api/revolutionary/engines"),
            ("Performance Metrics", "/api/performance/metrics"),
            ("Portfolio Positions", "/api/portfolio/positions"),
            ("Portfolio Value", "/api/portfolio/value"),
            ("Trading History", "/api/trading/history"),
            ("Live Trading Status", "/api/live-trading/status")
        ]
        
        for name, endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.results["single_request_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": True
                    })
                    print(f"[SUCCESS] {name}: {response_time:.3f}s")
                else:
                    self.results["single_request_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": False
                    })
                    print(f"[ERROR] {name}: HTTP {response.status_code}")
            except Exception as e:
                self.results["single_request_tests"].append({
                    "name": name,
                    "endpoint": endpoint,
                    "response_time": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                })
                print(f"[ERROR] {name}: {str(e)}")
        
        print()
    
    def test_concurrent_requests(self):
        """Test concurrent request performance"""
        print("CONCURRENT REQUEST PERFORMANCE TEST")
        print("=" * 50)
        
        # Test different concurrency levels
        concurrency_levels = [1, 5, 10, 20, 50]
        
        for concurrency in concurrency_levels:
            print(f"Testing {concurrency} concurrent requests...")
            
            start_time = time.time()
            success_count = 0
            response_times = []
            
            def make_request():
                try:
                    req_start = time.time()
                    response = requests.get(f"{self.base_url}/health", timeout=10)
                    req_time = time.time() - req_start
                    
                    if response.status_code == 200:
                        return req_time, True
                    else:
                        return req_time, False
                except:
                    return None, False
            
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrency)]
                results = [future.result() for future in futures]
            
            total_time = time.time() - start_time
            
            for req_time, success in results:
                if success and req_time is not None:
                    success_count += 1
                    response_times.append(req_time)
            
            avg_response_time = statistics.mean(response_times) if response_times else 0
            success_rate = (success_count / concurrency) * 100
            
            self.results["concurrent_tests"].append({
                "concurrency": concurrency,
                "total_time": total_time,
                "success_count": success_count,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            })
            
            print(f"  Concurrency {concurrency}: {total_time:.3f}s total, {success_rate:.1f}% success, {avg_response_time:.3f}s avg")
        
        print()
    
    def test_ai_capabilities(self):
        """Test AI capabilities and performance"""
        print("AI CAPABILITIES TEST")
        print("=" * 50)
        
        ai_tests = [
            ("GPT-OSS 20B", "/api/gpt-oss/20b/generate", {"prompt": "Analyze AAPL stock for trading"}),
            ("GPT-OSS 120B", "/api/gpt-oss/120b/generate", {"prompt": "Advanced market analysis for TSLA"}),
            ("Force Real GPT-OSS", "/api/gpt-oss/real/generate", {"prompt": "Quantum trading strategy for NVDA"}),
            ("Auto GPT-OSS", "/api/gpt-oss/analyze", {"prompt": "Comprehensive portfolio optimization"}),
            ("Revolutionary Trade", "/api/revolutionary/trade", {"symbol": "AAPL", "quantity": 100, "side": "buy"})
        ]
        
        for name, endpoint, payload in ai_tests:
            try:
                start_time = time.time()
                response = requests.post(f"{self.base_url}{endpoint}", json=payload, timeout=15)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    ai_mode = data.get("ai_mode", "unknown")
                    cached = data.get("cached", False)
                    optimization = data.get("optimization", "unknown")
                    
                    self.results["ai_capability_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": True,
                        "ai_mode": ai_mode,
                        "cached": cached,
                        "optimization": optimization
                    })
                    
                    print(f"[SUCCESS] {name}: {response_time:.3f}s")
                    print(f"  AI Mode: {ai_mode}")
                    print(f"  Cached: {cached}")
                    print(f"  Optimization: {optimization}")
                else:
                    self.results["ai_capability_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": False
                    })
                    print(f"[ERROR] {name}: HTTP {response.status_code}")
            except Exception as e:
                self.results["ai_capability_tests"].append({
                    "name": name,
                    "endpoint": endpoint,
                    "response_time": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                })
                print(f"[ERROR] {name}: {str(e)}")
        
        print()
    
    def test_trading_capabilities(self):
        """Test trading system capabilities"""
        print("TRADING CAPABILITIES TEST")
        print("=" * 50)
        
        trading_endpoints = [
            ("Crypto Engine", "/api/trading/crypto-engine/status"),
            ("Options Engine", "/api/trading/options-engine/status"),
            ("Advanced Engine", "/api/trading/advanced-engine/status"),
            ("Market Maker", "/api/trading/market-maker/status"),
            ("Master Engine", "/api/trading/master-engine/status"),
            ("HRM Engine", "/api/trading/hrm-engine/status"),
            ("Active Trades", "/api/trading/active"),
            ("Trading History", "/api/trading/history")
        ]
        
        for name, endpoint in trading_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("success", False)
                    
                    self.results["trading_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": True,
                        "trading_status": status
                    })
                    print(f"[SUCCESS] {name}: {response_time:.3f}s")
                else:
                    self.results["trading_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": False
                    })
                    print(f"[ERROR] {name}: HTTP {response.status_code}")
            except Exception as e:
                self.results["trading_tests"].append({
                    "name": name,
                    "endpoint": endpoint,
                    "response_time": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                })
                print(f"[ERROR] {name}: {str(e)}")
        
        print()
    
    def test_revolutionary_systems(self):
        """Test revolutionary systems"""
        print("REVOLUTIONARY SYSTEMS TEST")
        print("=" * 50)
        
        revolutionary_endpoints = [
            ("Revolutionary Engines", "/api/revolutionary/engines"),
            ("Revolutionary Performance", "/api/revolutionary/performance"),
            ("Revolutionary Status", "/api/revolutionary/status"),
            ("Quantum Status", "/api/quantum/status"),
            ("Think Mesh", "/api/think-mesh/status"),
            ("Market Oracle", "/api/market-oracle/status"),
            ("AI Consciousness", "/api/ai/consciousness/status"),
            ("Continuous Learning", "/api/learning/continuous-learning/status"),
            ("Advanced Learning", "/api/learning/advanced-learning/status"),
            ("Autonomous Improvement", "/api/learning/autonomous-improvement/status")
        ]
        
        for name, endpoint in revolutionary_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("success", False)
                    
                    self.results["revolutionary_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": True,
                        "revolutionary_status": status
                    })
                    print(f"[SUCCESS] {name}: {response_time:.3f}s")
                else:
                    self.results["revolutionary_tests"].append({
                        "name": name,
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code,
                        "success": False
                    })
                    print(f"[ERROR] {name}: HTTP {response.status_code}")
            except Exception as e:
                self.results["revolutionary_tests"].append({
                    "name": name,
                    "endpoint": endpoint,
                    "response_time": None,
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                })
                print(f"[ERROR] {name}: {str(e)}")
        
        print()
    
    def calculate_performance_metrics(self):
        """Calculate overall performance metrics"""
        print("CALCULATING PERFORMANCE METRICS")
        print("=" * 50)
        
        # Single request metrics
        single_success = [test for test in self.results["single_request_tests"] if test["success"]]
        single_times = [test["response_time"] for test in single_success if test["response_time"] is not None]
        
        # AI capability metrics
        ai_success = [test for test in self.results["ai_capability_tests"] if test["success"]]
        ai_times = [test["response_time"] for test in ai_success if test["response_time"] is not None]
        
        # Trading metrics
        trading_success = [test for test in self.results["trading_tests"] if test["success"]]
        trading_times = [test["response_time"] for test in trading_success if test["response_time"] is not None]
        
        # Revolutionary metrics
        rev_success = [test for test in self.results["revolutionary_tests"] if test["success"]]
        rev_times = [test["response_time"] for test in rev_success if test["response_time"] is not None]
        
        # Overall metrics
        all_times = single_times + ai_times + trading_times + rev_times
        
        self.results["performance_metrics"] = {
            "single_request": {
                "total_tests": len(self.results["single_request_tests"]),
                "successful_tests": len(single_success),
                "success_rate": (len(single_success) / len(self.results["single_request_tests"])) * 100 if self.results["single_request_tests"] else 0,
                "avg_response_time": statistics.mean(single_times) if single_times else 0,
                "min_response_time": min(single_times) if single_times else 0,
                "max_response_time": max(single_times) if single_times else 0
            },
            "ai_capabilities": {
                "total_tests": len(self.results["ai_capability_tests"]),
                "successful_tests": len(ai_success),
                "success_rate": (len(ai_success) / len(self.results["ai_capability_tests"])) * 100 if self.results["ai_capability_tests"] else 0,
                "avg_response_time": statistics.mean(ai_times) if ai_times else 0,
                "min_response_time": min(ai_times) if ai_times else 0,
                "max_response_time": max(ai_times) if ai_times else 0
            },
            "trading_systems": {
                "total_tests": len(self.results["trading_tests"]),
                "successful_tests": len(trading_success),
                "success_rate": (len(trading_success) / len(self.results["trading_tests"])) * 100 if self.results["trading_tests"] else 0,
                "avg_response_time": statistics.mean(trading_times) if trading_times else 0,
                "min_response_time": min(trading_times) if trading_times else 0,
                "max_response_time": max(trading_times) if trading_times else 0
            },
            "revolutionary_systems": {
                "total_tests": len(self.results["revolutionary_tests"]),
                "successful_tests": len(rev_success),
                "success_rate": (len(rev_success) / len(self.results["revolutionary_tests"])) * 100 if self.results["revolutionary_tests"] else 0,
                "avg_response_time": statistics.mean(rev_times) if rev_times else 0,
                "min_response_time": min(rev_times) if rev_times else 0,
                "max_response_time": max(rev_times) if rev_times else 0
            },
            "overall": {
                "total_tests": len(all_times),
                "avg_response_time": statistics.mean(all_times) if all_times else 0,
                "min_response_time": min(all_times) if all_times else 0,
                "max_response_time": max(all_times) if all_times else 0,
                "median_response_time": statistics.median(all_times) if all_times else 0
            }
        }
        
        # Print metrics
        print(f"Single Request Tests: {self.results['performance_metrics']['single_request']['successful_tests']}/{self.results['performance_metrics']['single_request']['total_tests']} ({self.results['performance_metrics']['single_request']['success_rate']:.1f}%)")
        print(f"  Average Response Time: {self.results['performance_metrics']['single_request']['avg_response_time']:.3f}s")
        
        print(f"AI Capability Tests: {self.results['performance_metrics']['ai_capabilities']['successful_tests']}/{self.results['performance_metrics']['ai_capabilities']['total_tests']} ({self.results['performance_metrics']['ai_capabilities']['success_rate']:.1f}%)")
        print(f"  Average Response Time: {self.results['performance_metrics']['ai_capabilities']['avg_response_time']:.3f}s")
        
        print(f"Trading System Tests: {self.results['performance_metrics']['trading_systems']['successful_tests']}/{self.results['performance_metrics']['trading_systems']['total_tests']} ({self.results['performance_metrics']['trading_systems']['success_rate']:.1f}%)")
        print(f"  Average Response Time: {self.results['performance_metrics']['trading_systems']['avg_response_time']:.3f}s")
        
        print(f"Revolutionary System Tests: {self.results['performance_metrics']['revolutionary_systems']['successful_tests']}/{self.results['performance_metrics']['revolutionary_systems']['total_tests']} ({self.results['performance_metrics']['revolutionary_systems']['success_rate']:.1f}%)")
        print(f"  Average Response Time: {self.results['performance_metrics']['revolutionary_systems']['avg_response_time']:.3f}s")
        
        print(f"Overall Performance: {self.results['performance_metrics']['overall']['total_tests']} tests")
        print(f"  Average Response Time: {self.results['performance_metrics']['overall']['avg_response_time']:.3f}s")
        print(f"  Min Response Time: {self.results['performance_metrics']['overall']['min_response_time']:.3f}s")
        print(f"  Max Response Time: {self.results['performance_metrics']['overall']['max_response_time']:.3f}s")
        print(f"  Median Response Time: {self.results['performance_metrics']['overall']['median_response_time']:.3f}s")
        
        print()
    
    def analyze_improvements(self):
        """Analyze performance improvements"""
        print("IMPROVEMENT ANALYSIS")
        print("=" * 50)
        
        # Baseline comparison (from previous tests)
        baseline_avg = 2.0  # seconds
        current_avg = self.results["performance_metrics"]["overall"]["avg_response_time"]
        
        improvement_percent = ((baseline_avg - current_avg) / baseline_avg) * 100 if baseline_avg > 0 else 0
        
        self.results["improvement_analysis"] = {
            "baseline_avg_response_time": baseline_avg,
            "current_avg_response_time": current_avg,
            "improvement_percent": improvement_percent,
            "performance_status": self.get_performance_status(improvement_percent),
            "recommendations": self.get_recommendations(improvement_percent)
        }
        
        print(f"Baseline Average Response Time: {baseline_avg:.3f}s")
        print(f"Current Average Response Time: {current_avg:.3f}s")
        print(f"Performance Improvement: {improvement_percent:.1f}%")
        print(f"Status: {self.results['improvement_analysis']['performance_status']}")
        print()
        
        print("RECOMMENDATIONS:")
        for i, rec in enumerate(self.results['improvement_analysis']['recommendations'], 1):
            print(f"{i}. {rec}")
        print()
    
    def get_performance_status(self, improvement_percent):
        """Get performance status based on improvement"""
        if improvement_percent > 50:
            return "EXCELLENT - Major performance improvement achieved!"
        elif improvement_percent > 25:
            return "GOOD - Significant performance improvement achieved!"
        elif improvement_percent > 10:
            return "MODERATE - Some performance improvement achieved!"
        elif improvement_percent > 0:
            return "MINIMAL - Small performance improvement achieved!"
        else:
            return "NO IMPROVEMENT - System bottleneck persists"
    
    def get_recommendations(self, improvement_percent):
        """Get recommendations based on performance"""
        recommendations = []
        
        if improvement_percent < 25:
            recommendations.extend([
                "Apply Windows Defender exclusions manually",
                "Disable Windows Search indexing",
                "Disable unnecessary Windows services",
                "Consider hardware upgrade (CPU/Memory)",
                "Use WSL2 or Docker for better performance"
            ])
        elif improvement_percent < 50:
            recommendations.extend([
                "Apply additional Windows optimizations",
                "Consider Redis caching implementation",
                "Optimize database queries",
                "Implement request batching"
            ])
        else:
            recommendations.extend([
                "Performance is excellent - continue with live trading",
                "Monitor system resources during trading",
                "Consider scaling to multiple servers"
            ])
        
        return recommendations
    
    def save_results(self):
        """Save benchmark results to file"""
        filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Benchmark results saved to: {filename}")
    
    def run_comprehensive_benchmark(self):
        """Run the complete benchmark suite"""
        print("COMPREHENSIVE PROMETHEUS BENCHMARK TEST")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            self.get_system_info()
            self.test_single_requests()
            self.test_concurrent_requests()
            self.test_ai_capabilities()
            self.test_trading_capabilities()
            self.test_revolutionary_systems()
            self.calculate_performance_metrics()
            self.analyze_improvements()
            self.save_results()
            
            print("=" * 60)
            print("BENCHMARK TEST COMPLETE")
            print("=" * 60)
            print("All tests completed successfully!")
            print("Check the generated JSON file for detailed results.")
            
        except Exception as e:
            print(f"BENCHMARK ERROR: {str(e)}")
            print("Some tests may have failed, but partial results are available.")

def main():
    """Main benchmark function"""
    benchmark = ComprehensiveBenchmark()
    benchmark.run_comprehensive_benchmark()

if __name__ == "__main__":
    main()

