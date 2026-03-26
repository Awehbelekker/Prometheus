#!/usr/bin/env python3
"""
REAL-TIME PERFORMANCE MONITOR
Monitor Prometheus performance in real-time
"""

import asyncio
import aiohttp
import time
import psutil
from datetime import datetime

class UltraFastMonitor:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.metrics = {
            "response_times": [],
            "cpu_usage": [],
            "memory_usage": [],
            "error_count": 0,
            "success_count": 0
        }
    
    async def monitor_ultra_fast(self):
        """Monitor system performance in real-time"""
        print("ULTRA-FAST PROMETHEUS PERFORMANCE MONITOR")
        print("=" * 60)
        print(f"Monitoring started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to stop monitoring")
        print()
        
        try:
            while True:
                await self.collect_ultra_metrics()
                self.display_ultra_metrics()
                await asyncio.sleep(2)  # Monitor every 2 seconds
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            self.display_ultra_summary()
    
    async def collect_ultra_metrics(self):
        """Collect ultra-fast performance metrics"""
        # Test server response time
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=3) as response:
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
        
        # Keep only last 50 measurements
        for key in ["response_times", "cpu_usage", "memory_usage"]:
            if len(self.metrics[key]) > 50:
                self.metrics[key] = self.metrics[key][-50:]
    
    def display_ultra_metrics(self):
        """Display current ultra-fast metrics"""
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
    
    def display_ultra_summary(self):
        """Display ultra-fast monitoring summary"""
        print("\n\nULTRA-FAST PERFORMANCE MONITORING SUMMARY")
        print("=" * 50)
        
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
    monitor = UltraFastMonitor()
    await monitor.monitor_ultra_fast()

if __name__ == "__main__":
    asyncio.run(main())
