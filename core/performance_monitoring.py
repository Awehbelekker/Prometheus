
# Performance monitoring and metrics for MASS Framework
import time
import psutil
import asyncio
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    active_agents: int
    requests_per_second: float
    average_response_time: float
    error_rate: float

class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.request_times: List[float] = []
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()
        
    async def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        # Calculate RPS
        current_time = time.time()
        elapsed = current_time - self.start_time
        rps = self.request_count / elapsed if elapsed > 0 else 0
        
        # Calculate average response time
        avg_response_time = sum(self.request_times) / len(self.request_times) if self.request_times else 0
        
        # Calculate error rate
        error_rate = (self.error_count / self.request_count) * 100 if self.request_count > 0 else 0
        
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            active_agents=0,  # To be implemented
            requests_per_second=rps,
            average_response_time=avg_response_time,
            error_rate=error_rate
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics
        if len(self.metrics_history) > 100:
            self.metrics_history.pop(0)
            
        return metrics
        
    def record_request(self, response_time: float, success: bool = True):
        """Record a request for metrics"""
        self.request_count += 1
        self.request_times.append(response_time)
        
        if not success:
            self.error_count += 1
            
        # Keep only last 1000 request times
        if len(self.request_times) > 1000:
            self.request_times.pop(0)

    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a named metric (compatibility with IB execution tracker)"""
        self.record_request(value)
            
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        if not self.metrics_history:
            return {}
            
        latest = self.metrics_history[-1]
        return {
            "current": asdict(latest),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "uptime_seconds": time.time() - self.start_time
        }
