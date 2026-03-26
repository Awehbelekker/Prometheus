#!/usr/bin/env python3
"""
PERFORMANCE MONITORING DASHBOARD
Real-time performance monitoring for Prometheus
"""

import asyncio
import aiohttp
import time
import psutil
from datetime import datetime
import json

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.metrics = {
            "response_times": [],
            "cpu_usage": [],
            "memory_usage": [],
            "error_count": 0,
            "success_count": 0
        }
    
    async def monitor_performance(self):
        """Monitor system performance in real-time"""
        print("PROMETHEUS PERFORMANCE MONITORING")
        print("=" * 50)
        print(f"Monitoring started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while True:
                await self.collect_metrics()
                self.display_metrics()
                await asyncio.sleep(5)  # Monitor every 5 seconds
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            self.display_summary()
    
    async def collect_metrics(self):
        """Collect performance metrics"""
        # Test server response time
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=5) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        self.metrics["response_times"].append(response_time)
                        self.metrics["success_count"] += 1
                    else:
                        self.metrics["error_count"] += 1
        except Exception as e:
            self.metrics["error_count"] += 1
        
        # Collect system metrics
        self.metrics["cpu_usage"].append(psutil.cpu_percent())
        self.metrics["memory_usage"].append(psutil.virtual_memory().percent)
        
        # Keep only last 20 measurements
        for key in ["response_times", "cpu_usage", "memory_usage"]:
            if len(self.metrics[key]) > 20:
                self.metrics[key] = self.metrics[key][-20:]
    
    def display_metrics(self):
        """Display current metrics"""
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] ", end="")
        
        if self.metrics["response_times"]:
            avg_response = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            print(f"Response: {avg_response:.3f}s ", end="")
        
        if self.metrics["cpu_usage"]:
            avg_cpu = sum(self.metrics["cpu_usage"]) / len(self.metrics["cpu_usage"])
            print(f"CPU: {avg_cpu:.1f}% ", end="")
        
        if self.metrics["memory_usage"]:
            avg_memory = sum(self.metrics["memory_usage"]) / len(self.metrics["memory_usage"])
            print(f"Memory: {avg_memory:.1f}% ", end="")
        
        print(f"Success: {self.metrics['success_count']} Errors: {self.metrics['error_count']}", end="")
    
    def display_summary(self):
        """Display monitoring summary"""
        print("\n\nPERFORMANCE MONITORING SUMMARY")
        print("=" * 40)
        
        if self.metrics["response_times"]:
            avg_response = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
            min_response = min(self.metrics["response_times"])
            max_response = max(self.metrics["response_times"])
            print(f"Average Response Time: {avg_response:.3f}s")
            print(f"Min Response Time: {min_response:.3f}s")
            print(f"Max Response Time: {max_response:.3f}s")
        
        if self.metrics["cpu_usage"]:
            avg_cpu = sum(self.metrics["cpu_usage"]) / len(self.metrics["cpu_usage"])
            print(f"Average CPU Usage: {avg_cpu:.1f}%")
        
        if self.metrics["memory_usage"]:
            avg_memory = sum(self.metrics["memory_usage"]) / len(self.metrics["memory_usage"])
            print(f"Average Memory Usage: {avg_memory:.1f}%")
        
        total_requests = self.metrics["success_count"] + self.metrics["error_count"]
        if total_requests > 0:
            success_rate = (self.metrics["success_count"] / total_requests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {self.metrics['success_count']}")
        print(f"Errors: {self.metrics['error_count']}")

async def main():
    """Main monitoring function"""
    monitor = PerformanceMonitor()
    await monitor.monitor_performance()

if __name__ == "__main__":
    asyncio.run(main())
