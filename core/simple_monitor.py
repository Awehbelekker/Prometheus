"""
PROMETHEUS Trading Platform - Simple Performance Monitor
Basic performance tracking and metrics
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any, List
from collections import deque

class SimplePerformanceMonitor:
    """Simple performance monitoring."""
    
    def __init__(self, max_samples: int = 100):
        self.max_samples = max_samples
        self.response_times = deque(maxlen=max_samples)
        self.start_time = time.time()
    
    def record_response_time(self, response_time: float):
        """Record API response time."""
        self.response_times.append({
            'time': response_time,
            'timestamp': time.time()
        })
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_available_mb': memory.available // (1024 * 1024),
            'uptime_seconds': time.time() - self.start_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.response_times:
            avg_response = 0
            max_response = 0
        else:
            times = [item['time'] for item in self.response_times]
            avg_response = sum(times) / len(times)
            max_response = max(times)
        
        return {
            'average_response_time': avg_response,
            'max_response_time': max_response,
            'total_requests': len(self.response_times),
            'system_stats': self.get_system_stats()
        }

# Global monitor instance
performance_monitor = SimplePerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            performance_monitor.record_response_time(end_time - start_time)
    return wrapper
