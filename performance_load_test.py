#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Performance Load Testing
Enterprise-grade performance validation for production readiness
"""

import asyncio
import aiohttp
import time
import statistics
import json
import psutil
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any
import subprocess
import sys

@dataclass
class LoadTestResult:
    """Data class for load test results."""
    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    success_rate: float
    error_details: List[str]

class PrometheusLoadTester:
    """Comprehensive load testing for PROMETHEUS Trading Platform."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
        self.start_time = None
        self.end_time = None
        
    async def test_health_endpoint_load(self, concurrent_users: int = 50, requests_per_user: int = 10):
        """Test health endpoint under load."""
        print(f"🔥 Testing health endpoint with {concurrent_users} concurrent users, {requests_per_user} requests each")
        
        async def make_health_request(session, user_id):
            results = []
            for i in range(requests_per_user):
                start_time = time.time()
                try:
                    async with session.get(f"{self.base_url}/health") as response:
                        end_time = time.time()
                        results.append({
                            "user_id": user_id,
                            "request_id": i,
                            "status_code": response.status,
                            "response_time": end_time - start_time,
                            "success": response.status == 200
                        })
                except Exception as e:
                    end_time = time.time()
                    results.append({
                        "user_id": user_id,
                        "request_id": i,
                        "status_code": 0,
                        "response_time": end_time - start_time,
                        "success": False,
                        "error": str(e)
                    })
            return results
        
        # Run concurrent requests
        async with aiohttp.ClientSession() as session:
            tasks = [make_health_request(session, user_id) for user_id in range(concurrent_users)]
            all_results = await asyncio.gather(*tasks)
        
        # Flatten results
        flat_results = [result for user_results in all_results for result in user_results]
        
        # Calculate metrics
        total_requests = len(flat_results)
        successful_requests = sum(1 for r in flat_results if r["success"])
        failed_requests = total_requests - successful_requests
        response_times = [r["response_time"] for r in flat_results if r["success"]]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        test_duration = max(r["response_time"] for r in flat_results)
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0
        success_rate = (successful_requests / total_requests) * 100
        
        error_details = [r.get("error", "") for r in flat_results if not r["success"]]
        
        result = LoadTestResult(
            test_name="Health Endpoint Load Test",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            requests_per_second=requests_per_second,
            success_rate=success_rate,
            error_details=error_details[:10]  # Limit error details
        )
        
        self.results.append(result)
        return result
    
    def test_database_performance(self, num_operations: int = 1000):
        """Test database performance under load."""
        print(f"💾 Testing database performance with {num_operations} operations")
        
        import sqlite3
        import tempfile
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute("""
                CREATE TABLE performance_test (
                    id INTEGER PRIMARY KEY,
                    symbol TEXT,
                    price REAL,
                    quantity INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            # Test insert performance
            insert_times = []
            for i in range(num_operations):
                start_time = time.time()
                cursor.execute(
                    "INSERT INTO performance_test (symbol, price, quantity) VALUES (?, ?, ?)",
                    (f"TEST{i % 100}", 100.0 + (i % 50), 10 + (i % 90))
                )
                conn.commit()
                end_time = time.time()
                insert_times.append(end_time - start_time)
            
            # Test select performance
            select_times = []
            for i in range(100):  # Test 100 selects
                start_time = time.time()
                cursor.execute("SELECT * FROM performance_test WHERE symbol = ? LIMIT 10", (f"TEST{i}",))
                results = cursor.fetchall()
                end_time = time.time()
                select_times.append(end_time - start_time)
            
            conn.close()
            
            # Calculate metrics
            avg_insert_time = statistics.mean(insert_times)
            avg_select_time = statistics.mean(select_times)
            
            result = LoadTestResult(
                test_name="Database Performance Test",
                total_requests=num_operations + 100,
                successful_requests=num_operations + 100,
                failed_requests=0,
                average_response_time=(avg_insert_time + avg_select_time) / 2,
                min_response_time=min(min(insert_times), min(select_times)),
                max_response_time=max(max(insert_times), max(select_times)),
                requests_per_second=num_operations / sum(insert_times) if sum(insert_times) > 0 else 0,
                success_rate=100.0,
                error_details=[]
            )
            
            self.results.append(result)
            return result
            
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_cpu_memory_usage(self, duration_seconds: int = 30):
        """Test CPU and memory usage under simulated load."""
        print(f"🖥️  Testing CPU and memory usage for {duration_seconds} seconds")
        
        def cpu_intensive_task():
            """Simulate CPU-intensive trading calculations."""
            end_time = time.time() + 1  # Run for 1 second
            while time.time() < end_time:
                # Simulate trading calculations
                prices = [100 + i * 0.1 for i in range(1000)]
                moving_avg = sum(prices[-20:]) / 20
                volatility = statistics.stdev(prices[-50:]) if len(prices) >= 50 else 0
                result = moving_avg * volatility
        
        # Monitor system resources
        process = psutil.Process()
        cpu_percentages = []
        memory_usage = []
        
        start_time = time.time()
        
        # Start CPU-intensive tasks
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit tasks continuously
            futures = []
            
            while time.time() - start_time < duration_seconds:
                # Submit new tasks
                for _ in range(2):
                    futures.append(executor.submit(cpu_intensive_task))
                
                # Monitor resources
                cpu_percent = process.cpu_percent()
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                cpu_percentages.append(cpu_percent)
                memory_usage.append(memory_mb)
                
                time.sleep(0.1)  # Sample every 100ms
                
                # Clean up completed futures
                futures = [f for f in futures if not f.done()]
            
            # Wait for remaining tasks
            for future in futures:
                future.result()
        
        # Calculate metrics
        avg_cpu = statistics.mean(cpu_percentages) if cpu_percentages else 0
        max_cpu = max(cpu_percentages) if cpu_percentages else 0
        avg_memory = statistics.mean(memory_usage) if memory_usage else 0
        max_memory = max(memory_usage) if memory_usage else 0
        
        result = LoadTestResult(
            test_name="CPU/Memory Usage Test",
            total_requests=len(cpu_percentages),
            successful_requests=len(cpu_percentages),
            failed_requests=0,
            average_response_time=avg_cpu,  # Using CPU as response time metric
            min_response_time=min(cpu_percentages) if cpu_percentages else 0,
            max_response_time=max_cpu,
            requests_per_second=len(cpu_percentages) / duration_seconds,
            success_rate=100.0,
            error_details=[f"Avg Memory: {avg_memory:.1f}MB", f"Max Memory: {max_memory:.1f}MB"]
        )
        
        self.results.append(result)
        return result
    
    def test_concurrent_calculations(self, num_threads: int = 10, calculations_per_thread: int = 100):
        """Test concurrent trading calculations."""
        print(f"🧮 Testing concurrent calculations with {num_threads} threads, {calculations_per_thread} calculations each")
        
        def trading_calculations(thread_id):
            """Simulate complex trading calculations."""
            results = []
            for i in range(calculations_per_thread):
                start_time = time.time()
                
                # Simulate market data processing
                prices = [100 + (i + thread_id) * 0.1 + j * 0.01 for j in range(100)]
                
                # Calculate technical indicators
                sma_20 = sum(prices[-20:]) / 20
                sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20
                
                # Calculate volatility
                volatility = statistics.stdev(prices[-30:]) if len(prices) >= 30 else 0
                
                # Simulate trading decision
                signal = "buy" if sma_20 > sma_50 and volatility < 2.0 else "hold"
                
                end_time = time.time()
                results.append({
                    "thread_id": thread_id,
                    "calculation_id": i,
                    "processing_time": end_time - start_time,
                    "signal": signal,
                    "success": True
                })
            
            return results
        
        # Run concurrent calculations
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(trading_calculations, thread_id) for thread_id in range(num_threads)]
            all_results = [future.result() for future in as_completed(futures)]
        
        # Flatten results
        flat_results = [result for thread_results in all_results for result in thread_results]
        
        # Calculate metrics
        processing_times = [r["processing_time"] for r in flat_results]
        total_requests = len(flat_results)
        successful_requests = sum(1 for r in flat_results if r["success"])
        
        result = LoadTestResult(
            test_name="Concurrent Calculations Test",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=total_requests - successful_requests,
            average_response_time=statistics.mean(processing_times),
            min_response_time=min(processing_times),
            max_response_time=max(processing_times),
            requests_per_second=total_requests / sum(processing_times),
            success_rate=(successful_requests / total_requests) * 100,
            error_details=[]
        )
        
        self.results.append(result)
        return result
    
    async def run_comprehensive_load_test(self):
        """Run comprehensive load testing suite."""
        print("🚀 Starting PROMETHEUS Comprehensive Load Testing")
        print("=" * 60)
        
        self.start_time = datetime.now()
        
        # Test 1: Health endpoint load
        await self.test_health_endpoint_load(concurrent_users=25, requests_per_user=20)
        
        # Test 2: Database performance
        self.test_database_performance(num_operations=500)
        
        # Test 3: CPU/Memory usage
        self.test_cpu_memory_usage(duration_seconds=15)
        
        # Test 4: Concurrent calculations
        self.test_concurrent_calculations(num_threads=8, calculations_per_thread=50)
        
        self.end_time = datetime.now()
        
        # Generate report
        self.generate_performance_report()
    
    def generate_performance_report(self):
        """Generate comprehensive performance report."""
        print("\n" + "=" * 60)
        print("📊 PROMETHEUS PERFORMANCE LOAD TEST REPORT")
        print("=" * 60)
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        print(f"Test Duration: {total_duration:.2f} seconds")
        print(f"Test Timestamp: {self.start_time.isoformat()}")
        
        overall_success = True
        
        for result in self.results:
            print(f"\n🔍 {result.test_name}")
            print("-" * 40)
            print(f"Total Requests: {result.total_requests}")
            print(f"Successful: {result.successful_requests}")
            print(f"Failed: {result.failed_requests}")
            print(f"Success Rate: {result.success_rate:.1f}%")
            print(f"Avg Response Time: {result.average_response_time:.4f}s")
            print(f"Min Response Time: {result.min_response_time:.4f}s")
            print(f"Max Response Time: {result.max_response_time:.4f}s")
            print(f"Requests/Second: {result.requests_per_second:.2f}")
            
            # Performance thresholds
            if result.success_rate < 95:
                print("[WARNING]️  WARNING: Success rate below 95%")
                overall_success = False
            
            if result.average_response_time > 1.0:
                print("[WARNING]️  WARNING: Average response time above 1 second")
                overall_success = False
            
            if result.error_details:
                print("Error Details:", result.error_details[:3])
        
        # Overall assessment
        print("\n" + "=" * 60)
        if overall_success:
            print("🎉 PERFORMANCE TEST PASSED - System ready for enterprise load!")
        else:
            print("[WARNING]️  PERFORMANCE ISSUES DETECTED - Review warnings above")
        
        # Save detailed report
        report_data = {
            "timestamp": self.start_time.isoformat(),
            "duration_seconds": total_duration,
            "overall_success": overall_success,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "total_requests": r.total_requests,
                    "successful_requests": r.successful_requests,
                    "failed_requests": r.failed_requests,
                    "success_rate": r.success_rate,
                    "average_response_time": r.average_response_time,
                    "min_response_time": r.min_response_time,
                    "max_response_time": r.max_response_time,
                    "requests_per_second": r.requests_per_second,
                    "error_details": r.error_details
                }
                for r in self.results
            ]
        }
        
        report_filename = f"performance_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📁 Detailed report saved: {report_filename}")
        print("=" * 60)


async def main():
    """Main entry point for load testing."""
    tester = PrometheusLoadTester()
    await tester.run_comprehensive_load_test()


if __name__ == "__main__":
    asyncio.run(main())
