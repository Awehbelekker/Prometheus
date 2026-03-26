"""
Cloud Monitoring and Observability for MASS Framework
Implements comprehensive monitoring, logging, and observability features
"""

import os
import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil
import asyncio
from contextlib import asynccontextmanager

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/mass_framework.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class MetricData:
    """Structured metric data"""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str] = None
    unit: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass 
class HealthCheckResult:
    """Health check result structure"""
    service: str
    status: str  # "healthy", "unhealthy", "degraded"
    timestamp: datetime
    response_time_ms: float
    details: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class MetricsCollector:
    """Collects system and application metrics"""
    
    def __init__(self):
        self.metrics_history: List[MetricData] = []
        self.max_history_size = 1000
        
    def collect_system_metrics(self) -> List[MetricData]:
        """Collect system-level metrics"""
        timestamp = datetime.now(timezone.utc)
        metrics = []
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(MetricData(
            name="system_cpu_usage_percent",
            value=cpu_percent,
            timestamp=timestamp,
            unit="percent"
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(MetricData(
            name="system_memory_usage_percent",
            value=memory.percent,
            timestamp=timestamp,
            unit="percent"
        ))
        
        metrics.append(MetricData(
            name="system_memory_available_bytes",
            value=memory.available,
            timestamp=timestamp,
            unit="bytes"
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics.append(MetricData(
            name="system_disk_usage_percent",
            value=(disk.used / disk.total) * 100,
            timestamp=timestamp,
            unit="percent"
        ))
        
        # Network metrics
        net_io = psutil.net_io_counters()
        metrics.append(MetricData(
            name="system_network_bytes_sent",
            value=net_io.bytes_sent,
            timestamp=timestamp,
            unit="bytes"
        ))
        
        metrics.append(MetricData(
            name="system_network_bytes_recv",
            value=net_io.bytes_recv,
            timestamp=timestamp,
            unit="bytes"
        ))
        
        return metrics
    
    def collect_application_metrics(self, app_state: Dict[str, Any] = None) -> List[MetricData]:
        """Collect application-specific metrics"""
        timestamp = datetime.now(timezone.utc)
        metrics = []
        
        # Process metrics
        process = psutil.Process()
        metrics.append(MetricData(
            name="app_memory_usage_mb",
            value=process.memory_info().rss / (1024 * 1024),
            timestamp=timestamp,
            unit="MB"
        ))
        
        metrics.append(MetricData(
            name="app_cpu_percent",
            value=process.cpu_percent(),
            timestamp=timestamp,
            unit="percent"
        ))
        
        # File descriptor count
        try:
            fd_count = process.num_fds() if hasattr(process, 'num_fds') else 0
            metrics.append(MetricData(
                name="app_file_descriptors",
                value=fd_count,
                timestamp=timestamp,
                unit="count"
            ))
        except:
            pass
        
        # Thread count
        metrics.append(MetricData(
            name="app_thread_count",
            value=process.num_threads(),
            timestamp=timestamp,
            unit="count"
        ))
        
        # Application-specific metrics
        if app_state:
            # Active agents count
            if 'active_agents' in app_state:
                metrics.append(MetricData(
                    name="app_active_agents",
                    value=len(app_state['active_agents']),
                    timestamp=timestamp,
                    unit="count"
                ))
            
            # Database connections
            if 'db_connections' in app_state:
                metrics.append(MetricData(
                    name="app_db_connections",
                    value=app_state['db_connections'],
                    timestamp=timestamp,
                    unit="count"
                ))
        
        return metrics
    
    def store_metrics(self, metrics: List[MetricData]):
        """Store metrics in memory and optionally persist"""
        self.metrics_history.extend(metrics)
        
        # Trim history if too large
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
        
        # Log metrics
        for metric in metrics:
            logging.info(f"METRIC: {metric.name}={metric.value}{metric.unit}")
    
    def get_metrics_json(self) -> str:
        """Get metrics as JSON for export"""
        return json.dumps([metric.to_dict() for metric in self.metrics_history], indent=2)

class HealthChecker:
    """Performs health checks on system components"""
    
    def __init__(self):
        self.health_history: List[HealthCheckResult] = []
        self.max_history_size = 100
    
    async def check_database_health(self, db_manager=None) -> HealthCheckResult:
        """Check database connectivity and performance"""
        start_time = time.time()
        timestamp = datetime.now(timezone.utc)
        
        try:
            if db_manager:
                # Simple query test
                result = await asyncio.to_thread(
                    db_manager.execute_query, 
                    "SELECT 1 as test", 
                    {}
                )
                response_time = (time.time() - start_time) * 1000
                
                if result:
                    return HealthCheckResult(
                        service="database",
                        status="healthy",
                        timestamp=timestamp,
                        response_time_ms=response_time,
                        details={"query_result": "ok"}
                    )
                else:
                    return HealthCheckResult(
                        service="database",
                        status="unhealthy",
                        timestamp=timestamp,
                        response_time_ms=response_time,
                        details={"error": "No result from test query"}
                    )
            else:
                return HealthCheckResult(
                    service="database",
                    status="unhealthy",
                    timestamp=timestamp,
                    response_time_ms=0,
                    details={"error": "Database manager not available"}
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service="database",
                status="unhealthy",
                timestamp=timestamp,
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_api_health(self) -> HealthCheckResult:
        """Check API server health"""
        start_time = time.time()
        timestamp = datetime.now(timezone.utc)
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('http://localhost:8000/health', timeout=5) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        return HealthCheckResult(
                            service="api",
                            status="healthy",
                            timestamp=timestamp,
                            response_time_ms=response_time,
                            details={"status_code": response.status}
                        )
                    else:
                        return HealthCheckResult(
                            service="api",
                            status="degraded",
                            timestamp=timestamp,
                            response_time_ms=response_time,
                            details={"status_code": response.status}
                        )
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheckResult(
                service="api",
                status="unhealthy",
                timestamp=timestamp,
                response_time_ms=response_time,
                details={"error": str(e)}
            )
    
    async def check_system_resources(self) -> HealthCheckResult:
        """Check system resource availability"""
        timestamp = datetime.now(timezone.utc)
        
        try:
            # CPU check
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Health thresholds
            cpu_threshold = 90.0
            memory_threshold = 90.0
            disk_threshold = 90.0
            
            issues = []
            if cpu_percent > cpu_threshold:
                issues.append(f"High CPU usage: {cpu_percent}%")
            if memory.percent > memory_threshold:
                issues.append(f"High memory usage: {memory.percent}%")
            if (disk.used / disk.total) * 100 > disk_threshold:
                issues.append(f"High disk usage: {(disk.used / disk.total) * 100:.1f}%")
            
            if issues:
                status = "degraded" if len(issues) <= 1 else "unhealthy"
            else:
                status = "healthy"
            
            return HealthCheckResult(
                service="system_resources",
                status=status,
                timestamp=timestamp,
                response_time_ms=0,
                details={
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": (disk.used / disk.total) * 100,
                    "issues": issues
                }
            )
            
        except Exception as e:
            return HealthCheckResult(
                service="system_resources",
                status="unhealthy",
                timestamp=timestamp,
                response_time_ms=0,
                details={"error": str(e)}
            )
    
    async def run_all_health_checks(self, db_manager=None) -> List[HealthCheckResult]:
        """Run all health checks"""
        results = []
        
        # Run checks concurrently
        tasks = [
            self.check_system_resources(),
            self.check_api_health(),
            self.check_database_health(db_manager)
        ]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    service_names = ["system_resources", "api", "database"]
                    results[i] = HealthCheckResult(
                        service=service_names[i],
                        status="unhealthy",
                        timestamp=datetime.now(timezone.utc),
                        response_time_ms=0,
                        details={"error": str(result)}
                    )
            
        except Exception as e:
            logging.error(f"Error running health checks: {e}")
        
        # Store results
        self.health_history.extend(results)
        if len(self.health_history) > self.max_history_size:
            self.health_history = self.health_history[-self.max_history_size:]
        
        # Log results
        for result in results:
            if isinstance(result, HealthCheckResult):
                logging.info(f"HEALTH: {result.service}={result.status} ({result.response_time_ms:.1f}ms)")
        
        return results
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        if not self.health_history:
            return {"status": "unknown", "services": {}}
        
        # Get latest results for each service
        latest_results = {}
        for result in reversed(self.health_history):
            if isinstance(result, HealthCheckResult) and result.service not in latest_results:
                latest_results[result.service] = result
        
        # Determine overall status
        statuses = [result.status for result in latest_results.values()]
        if "unhealthy" in statuses:
            overall_status = "unhealthy"
        elif "degraded" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                service: {
                    "status": result.status,
                    "response_time_ms": result.response_time_ms,
                    "last_check": result.timestamp.isoformat()
                }
                for service, result in latest_results.items()
            }
        }

class ObservabilityManager:
    """Manages observability features including metrics and health checks"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker()
        self.monitoring_active = False
        self.monitoring_interval = 30  # seconds
        self._monitoring_task = None
        
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
    
    async def start_monitoring(self, db_manager=None):
        """Start continuous monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(
            self._monitoring_loop(db_manager)
        )
        logging.info("Observability monitoring started")
    
    async def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        logging.info("Observability monitoring stopped")
    
    async def _monitoring_loop(self, db_manager=None):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect metrics
                system_metrics = self.metrics_collector.collect_system_metrics()
                app_metrics = self.metrics_collector.collect_application_metrics()
                
                all_metrics = system_metrics + app_metrics
                self.metrics_collector.store_metrics(all_metrics)
                
                # Run health checks
                await self.health_checker.run_all_health_checks(db_manager)
                
                # Wait for next interval
                await asyncio.sleep(self.monitoring_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    def get_monitoring_data(self) -> Dict[str, Any]:
        """Get comprehensive monitoring data"""
        return {
            "health": self.health_checker.get_health_summary(),
            "metrics": {
                "latest": [
                    metric.to_dict() 
                    for metric in self.metrics_collector.metrics_history[-10:]
                ],
                "count": len(self.metrics_collector.metrics_history)
            },
            "monitoring": {
                "active": self.monitoring_active,
                "interval_seconds": self.monitoring_interval
            }
        }
    
    @asynccontextmanager
    async def monitoring_context(self, db_manager=None):
        """Context manager for monitoring lifecycle"""
        await self.start_monitoring(db_manager)
        try:
            yield self
        finally:
            await self.stop_monitoring()

# Global observability instance
observability = ObservabilityManager()

def setup_observability_logging():
    """Setup structured logging for observability"""
    
    # Create custom logger for metrics
    metrics_logger = logging.getLogger('mass_framework.metrics')
    metrics_handler = logging.FileHandler('logs/metrics.log')
    metrics_handler.setFormatter(
        logging.Formatter('%(asctime)s - METRIC - %(message)s')
    )
    metrics_logger.addHandler(metrics_handler)
    metrics_logger.setLevel(logging.INFO)
    
    # Create custom logger for health checks
    health_logger = logging.getLogger('mass_framework.health')
    health_handler = logging.FileHandler('logs/health.log')
    health_handler.setFormatter(
        logging.Formatter('%(asctime)s - HEALTH - %(message)s')
    )
    health_logger.addHandler(health_handler)
    health_logger.setLevel(logging.INFO)
    
    return metrics_logger, health_logger

# Setup logging
setup_observability_logging()
