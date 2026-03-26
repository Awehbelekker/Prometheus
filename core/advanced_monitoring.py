"""
Advanced Monitoring System with Prometheus Integration
Provides comprehensive metrics collection, alerting, and health monitoring
"""

import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from contextlib import contextmanager
import psutil
import threading
from collections import defaultdict, deque
from enum import Enum
import json

# Prometheus client imports (install with: pip install prometheus-client)
try:
    from prometheus_client import Counter, Histogram, Gauge, Info, start_http_server, CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available. Install with: pip install prometheus-client")

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Alert:
    """Alert data structure"""
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MetricThreshold:
    """Threshold configuration for metrics"""
    warning: float
    critical: float
    evaluation_window: int = 60  # seconds
    min_samples: int = 5

class MetricsCollector:
    """
    Comprehensive metrics collection system with Prometheus integration
    """
    
    def __init__(self, enable_prometheus: bool = True, metrics_port: int = 8000):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.metrics_port = metrics_port
        self.registry = CollectorRegistry() if self.enable_prometheus else None
        
        # Internal metrics storage
        self._metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self._alerts = deque(maxlen=1000)
        self._thresholds = {}
        
        # Performance tracking
        self._operation_times = defaultdict(list)
        self._error_counts = defaultdict(int)
        
        # Initialize Prometheus metrics
        if self.enable_prometheus:
            self._init_prometheus_metrics()
            self._start_metrics_server()
        
        # Start background monitoring
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(target=self._background_monitoring, daemon=True)
        self._monitoring_thread.start()
        
        logger.info(f"Metrics collector initialized (Prometheus: {self.enable_prometheus})")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        if not self.enable_prometheus:
            return
        # System metrics
        self.system_cpu_usage = Gauge('mass_system_cpu_percent', 'CPU usage percentage', registry=self.registry)
        self.system_memory_usage = Gauge('mass_system_memory_percent', 'Memory usage percentage', registry=self.registry)
        self.system_disk_usage = Gauge('mass_system_disk_percent', 'Disk usage percentage', registry=self.registry)

        # Agent metrics
        self.agent_operations_total = Counter('mass_agent_operations_total', 'Total agent operations', ['agent_id', 'operation'], registry=self.registry)
        self.agent_operation_duration = Histogram('mass_agent_operation_duration_seconds', 'Agent operation duration', ['agent_id', 'operation'], registry=self.registry)
        self.agent_errors_total = Counter('mass_agent_errors_total', 'Total agent errors', ['agent_id', 'error_type'], registry=self.registry)
        self.active_agents = Gauge('mass_active_agents', 'Number of active agents', registry=self.registry)

        # Workflow metrics
        self.workflow_executions_total = Counter('mass_workflow_executions_total', 'Total workflow executions', ['workflow_type', 'status'], registry=self.registry)
        self.workflow_duration = Histogram('mass_workflow_duration_seconds', 'Workflow execution duration', ['workflow_type'], registry=self.registry)
        self.active_workflows = Gauge('mass_active_workflows', 'Number of active workflows', registry=self.registry)

        # Database metrics
        self.database_queries_total = Counter('mass_database_queries_total', 'Total database queries', ['operation'], registry=self.registry)
        self.database_query_duration = Histogram('mass_database_query_duration_seconds', 'Database query duration', ['operation'], registry=self.registry)
        self.database_connections = Gauge('mass_database_connections', 'Active database connections', registry=self.registry)

        # Cache metrics
        self.cache_hits_total = Counter('mass_cache_hits_total', 'Total cache hits', ['cache_type'], registry=self.registry)
        self.cache_misses_total = Counter('mass_cache_misses_total', 'Total cache misses', ['cache_type'], registry=self.registry)
        self.cache_size = Gauge('mass_cache_size_bytes', 'Cache size in bytes', ['cache_type'], registry=self.registry)

        # API metrics
        self.api_requests_total = Counter('mass_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'], registry=self.registry)
        self.api_response_time = Histogram('mass_api_response_time_seconds', 'API response time', ['method', 'endpoint'], registry=self.registry)

        # Latency suite metrics
        self.trading_order_latency_p50_ms = Gauge('mass_trading_order_latency_p50_ms', 'Trading order latency p50 (ms)', registry=self.registry)
        self.trading_order_latency_p95_ms = Gauge('mass_trading_order_latency_p95_ms', 'Trading order latency p95 (ms)', registry=self.registry)
        self.trading_order_latency_p99_ms = Gauge('mass_trading_order_latency_p99_ms', 'Trading order latency p99 (ms)', registry=self.registry)
        self.websocket_broadcast_last_p95_ms = Gauge('mass_websocket_broadcast_last_p95_ms', 'WebSocket broadcast last-client p95 latency (ms)', registry=self.registry)
        self.websocket_broadcast_avg_last_ms = Gauge('mass_websocket_broadcast_avg_last_ms', 'WebSocket broadcast avg last-client latency (ms)', registry=self.registry)
        self.ai_inference_latency_p95_ms = Gauge('mass_ai_inference_latency_p95_ms', 'AI inference latency p95 (ms)', registry=self.registry)
        self.ai_inference_latency_avg_ms = Gauge('mass_ai_inference_latency_avg_ms', 'AI inference latency avg (ms)', registry=self.registry)

        # HRM metrics
        try:
            self.hrm_decisions_total = Counter('mass_hrm_decisions_total', 'Total HRM decisions', ['persona','action','fallback'], registry=self.registry)
            self.hrm_decision_latency = Histogram('mass_hrm_decision_latency_seconds', 'HRM decision latency', ['reasoning_level'], registry=self.registry)
            self.hrm_avg_confidence = Gauge('mass_hrm_avg_confidence', 'HRM rolling average decision confidence', registry=self.registry)
            self.hrm_last_risk_level = Gauge('mass_hrm_last_risk_level', 'HRM last risk level', registry=self.registry)
            self.hrm_fallbacks_total = Counter('mass_hrm_fallbacks_total', 'Total HRM fallback decisions', registry=self.registry)
        except Exception as e:
            logger.warning(f"Failed to init HRM Prometheus metrics: {e}")
        
    def _start_metrics_server(self):
        """Start Prometheus metrics HTTP server"""
        if not self.enable_prometheus:
            return
            
        try:
            start_http_server(self.metrics_port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {self.metrics_port}")
        except Exception as e:
            logger.error(f"Failed to start metrics server: {str(e)}")
    
    def _background_monitoring(self):
        """Background thread for system monitoring"""
        while self._monitoring_active:
            try:
                self._collect_system_metrics()
                self._check_thresholds()
                time.sleep(10)  # Collect every 10 seconds
            except Exception as e:
                logger.error(f"Background monitoring error: {str(e)}")
                time.sleep(30)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_metric('system.cpu_percent', cpu_percent)
            if self.enable_prometheus:
                self.system_cpu_usage.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.record_metric('system.memory_percent', memory_percent)
            if self.enable_prometheus:
                self.system_memory_usage.set(memory_percent)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.record_metric('system.disk_percent', disk_percent)
            if self.enable_prometheus:
                self.system_disk_usage.set(disk_percent)
                
        except Exception as e:
            logger.error(f"System metrics collection error: {str(e)}")
    
    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        timestamp = datetime.now()
        metric_data = {
            'value': value,
            'timestamp': timestamp,
            'labels': labels or {}
        }
        
        self._metrics_history[metric_name].append(metric_data)
        
        # Log significant values (only at 95%+ to reduce noise)
        if metric_name.endswith('_percent') and value > 95:
            logger.warning(f"High resource usage: {metric_name} = {value:.1f}%")
    
    @contextmanager
    def measure_operation(self, operation_name: str, agent_id: str = None, labels: Dict[str, str] = None):
        """Context manager to measure operation duration"""
        start_time = time.time()
        operation_labels = labels or {}
        
        try:
            yield
            # Success case
            duration = time.time() - start_time
            self._record_operation_success(operation_name, duration, agent_id, operation_labels)
            
        except Exception as e:
            # Error case
            duration = time.time() - start_time
            self._record_operation_error(operation_name, duration, str(e), agent_id, operation_labels)
            raise
    
    def _record_operation_success(self, operation: str, duration: float, agent_id: str = None, labels: Dict[str, str] = None):
        """Record successful operation metrics"""
        if self.enable_prometheus:
            if agent_id:
                self.agent_operations_total.labels(agent_id=agent_id, operation=operation).inc()
                self.agent_operation_duration.labels(agent_id=agent_id, operation=operation).observe(duration)
            
        # Internal tracking
        self._operation_times[operation].append(duration)
        self.record_metric(f'operation.{operation}.duration', duration, labels)
    
    def _record_operation_error(self, operation: str, duration: float, error: str, agent_id: str = None, labels: Dict[str, str] = None):
        """Record operation error metrics"""
        error_type = type(error).__name__ if hasattr(error, '__name__') else 'unknown'
        
        if self.enable_prometheus and agent_id:
            self.agent_errors_total.labels(agent_id=agent_id, error_type=error_type).inc()
        
        # Internal tracking
        self._error_counts[f"{operation}.{error_type}"] += 1
        self.record_metric(f'operation.{operation}.errors', 1, labels)
    
    def record_agent_metric(self, agent_id: str, metric_name: str, value: float):
        """Record agent-specific metric"""
        full_metric_name = f'agent.{agent_id}.{metric_name}'
        self.record_metric(full_metric_name, value, {'agent_id': agent_id})
    
    def record_workflow_metric(self, workflow_id: str, metric_name: str, value: float, workflow_type: str = None):
        """Record workflow-specific metric"""
        labels = {'workflow_id': workflow_id}
        if workflow_type:
            labels['workflow_type'] = workflow_type
            
        full_metric_name = f'workflow.{workflow_id}.{metric_name}'
        self.record_metric(full_metric_name, value, labels)
    
    def record_database_operation(self, operation: str, duration: float, success: bool = True):
        """Record database operation metrics"""
        if self.enable_prometheus:
            self.database_queries_total.labels(operation=operation).inc()
            self.database_query_duration.labels(operation=operation).observe(duration)
        
        status = 'success' if success else 'error'
        self.record_metric(f'database.{operation}.{status}', duration)
    
    def record_cache_operation(self, cache_type: str, operation: str, hit: bool = None):
        """Record cache operation metrics"""
        if self.enable_prometheus:
            if hit is True:
                self.cache_hits_total.labels(cache_type=cache_type).inc()
            elif hit is False:
                self.cache_misses_total.labels(cache_type=cache_type).inc()
        
        if hit is not None:
            status = 'hit' if hit else 'miss'
            self.record_metric(f'cache.{cache_type}.{status}', 1)
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        if self.enable_prometheus:
            self.api_requests_total.labels(method=method, endpoint=endpoint, status=str(status_code)).inc()
            self.api_response_time.labels(method=method, endpoint=endpoint).observe(duration)
        
        self.record_metric(f'api.{method}.{endpoint}.response_time', duration, {
            'method': method,
            'endpoint': endpoint,
            'status': str(status_code)
        })
    
    def set_threshold(self, metric_name: str, warning: float, critical: float, evaluation_window: int = 60):
        """Set alert thresholds for a metric"""
        self._thresholds[metric_name] = MetricThreshold(warning, critical, evaluation_window)
        logger.info(f"Set thresholds for {metric_name}: warning={warning}, critical={critical}")
    
    def _check_thresholds(self):
        """Check metrics against configured thresholds"""
        current_time = datetime.now()
        
        for metric_name, threshold in self._thresholds.items():
            if metric_name not in self._metrics_history:
                continue
                
            # Get recent metrics within evaluation window
            cutoff_time = current_time - timedelta(seconds=threshold.evaluation_window)
            recent_metrics = [
                m for m in self._metrics_history[metric_name]
                if m['timestamp'] >= cutoff_time
            ]
            
            if len(recent_metrics) < threshold.min_samples:
                continue
            
            # Calculate average value
            avg_value = sum(m['value'] for m in recent_metrics) / len(recent_metrics)
            
            # Check thresholds
            if avg_value >= threshold.critical:
                self._create_alert(AlertLevel.CRITICAL, f"{metric_name} critical: {avg_value:.2f}", metric_name)
            elif avg_value >= threshold.warning:
                self._create_alert(AlertLevel.WARNING, f"{metric_name} warning: {avg_value:.2f}", metric_name)
    
    def _create_alert(self, level: AlertLevel, message: str, source: str, metadata: Dict[str, Any] = None):
        """Create and store an alert"""
        alert = Alert(level, message, datetime.now(), source, metadata or {})
        self._alerts.append(alert)
        
        # Log alert
        log_func = getattr(logger, level.value, logger.info)
        log_func(f"ALERT [{level.value.upper()}]: {message}")
        
        # TODO: Send to external alerting system (Slack, PagerDuty, etc.)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics"""
        summary = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'operations': {},
            'errors': {},
            'alerts': len(self._alerts)
        }
        
        # System metrics
        for metric_name in ['system.cpu_percent', 'system.memory_percent', 'system.disk_percent']:
            if metric_name in self._metrics_history:
                recent_values = [m['value'] for m in list(self._metrics_history[metric_name])[-10:]]
                if recent_values:
                    summary['system'][metric_name.split('.')[-1]] = {
                        'current': recent_values[-1],
                        'average': sum(recent_values) / len(recent_values),
                        'max': max(recent_values),
                        'min': min(recent_values)
                    }
        
        # Operation metrics
        for operation, durations in self._operation_times.items():
            if durations:
                recent_durations = durations[-100:]  # Last 100 operations
                summary['operations'][operation] = {
                    'count': len(durations),
                    'avg_duration': sum(recent_durations) / len(recent_durations),
                    'max_duration': max(recent_durations),
                    'min_duration': min(recent_durations)
                }
        
        # Error counts
        summary['errors'] = dict(self._error_counts)
        
        return summary
    
    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts within specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self._alerts if alert.timestamp >= cutoff_time]
    
    def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        if not self.enable_prometheus:
            return "Prometheus not available"
        
        return generate_latest(self.registry).decode('utf-8')
    
    def shutdown(self):
        """Shutdown the metrics collector"""
        self._monitoring_active = False
        if hasattr(self, '_monitoring_thread'):
            self._monitoring_thread.join(timeout=5)
        logger.info("Metrics collector shutdown complete")

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Determine overall health status
            health_status = "healthy"
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 95:
                health_status = "critical"
            elif cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
                health_status = "degraded"

            return {
                "overall_status": health_status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "uptime_seconds": time.time() - psutil.boot_time(),
                "active_alerts": len(self._alerts),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "overall_status": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    async def register_agent(self, agent) -> None:
        """Register an agent for monitoring"""
        try:
            agent_id = getattr(agent, 'agent_id', str(agent))
            logger.info(f"Registered agent for monitoring: {agent_id}")
            # Store agent registration time
            self.record_metric(f'agent.{agent_id}.registered', 1)
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")

    async def start_workflow_monitoring(self, workflow_id: str) -> None:
        """Start monitoring a workflow"""
        try:
            logger.info(f"Started monitoring workflow: {workflow_id}")
            self.record_metric(f'workflow.{workflow_id}.started', 1)
        except Exception as e:
            logger.error(f"Failed to start workflow monitoring: {e}")

    def track_phase(self, phase_name: str):
        """Context manager to track a workflow phase"""
        return self.measure_operation(f"phase.{phase_name}")

    async def get_workflow_metrics(self, workflow_id: str) -> Dict[str, Any]:
        """Get metrics for a specific workflow"""
        try:
            # Get workflow-specific metrics from history
            workflow_metrics = {}
            for metric_name, history in self._metrics_history.items():
                if f'workflow.{workflow_id}' in metric_name:
                    recent_values = [m['value'] for m in list(history)[-10:]]
                    if recent_values:
                        workflow_metrics[metric_name] = {
                            'current': recent_values[-1],
                            'average': sum(recent_values) / len(recent_values),
                            'count': len(recent_values)
                        }

            return {
                "workflow_id": workflow_id,
                "metrics": workflow_metrics,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get workflow metrics: {e}")
            return {"workflow_id": workflow_id, "error": str(e)}


class PerformanceProfiler:
    """
    Detailed performance profiling for specific operations
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self._profiles = {}
    
    @contextmanager
    def profile_operation(self, operation_name: str, detailed: bool = False):
        """Profile an operation with detailed timing"""
        start_time = time.perf_counter()
        start_cpu = time.process_time()
        
        profile_data = {
            'operation': operation_name,
            'start_time': start_time,
            'start_cpu': start_cpu,
            'steps': []
        }
        
        class ProfileContext:
            def __init__(self, profile_data):
                self.profile_data = profile_data
            
            def step(self, step_name: str):
                current_time = time.perf_counter()
                current_cpu = time.process_time()
                
                self.profile_data['steps'].append({
                    'name': step_name,
                    'wall_time': current_time - self.profile_data['start_time'],
                    'cpu_time': current_cpu - self.profile_data['start_cpu'],
                    'timestamp': current_time
                })
        
        try:
            yield ProfileContext(profile_data)
            
        finally:
            end_time = time.perf_counter()
            end_cpu = time.process_time()
            
            total_wall_time = end_time - start_time
            total_cpu_time = end_cpu - start_cpu
            
            profile_data.update({
                'total_wall_time': total_wall_time,
                'total_cpu_time': total_cpu_time,
                'cpu_usage_percent': (total_cpu_time / total_wall_time) * 100 if total_wall_time > 0 else 0
            })
            
            self._profiles[operation_name] = profile_data
            
            # Record in metrics
            self.metrics.record_metric(f'profile.{operation_name}.wall_time', total_wall_time)
            self.metrics.record_metric(f'profile.{operation_name}.cpu_time', total_cpu_time)
    
    def get_profile_report(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed profile report for an operation"""
        return self._profiles.get(operation_name)
    
    def get_all_profiles(self) -> Dict[str, Any]:
        """Get all profile data"""
        return self._profiles.copy()


# Global metrics instance (using port 9090 to avoid conflict with main API on 8000)
metrics_collector = MetricsCollector(metrics_port=9090)
performance_profiler = PerformanceProfiler(metrics_collector)

# Convenience functions
def measure_operation(operation_name: str, agent_id: str = None):
    """Decorator for measuring operation performance"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with metrics_collector.measure_operation(operation_name, agent_id):
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with metrics_collector.measure_operation(operation_name, agent_id):
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def profile_operation(operation_name: str, detailed: bool = False):
    """Decorator for detailed operation profiling"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            with performance_profiler.profile_operation(operation_name, detailed) as profiler:
                return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs):
            with performance_profiler.profile_operation(operation_name, detailed) as profiler:
                return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Initialize default thresholds
def setup_default_thresholds():
    """Setup default monitoring thresholds"""
    metrics_collector.set_threshold('system.cpu_percent', warning=80.0, critical=95.0)
    metrics_collector.set_threshold('system.memory_percent', warning=85.0, critical=95.0)
    metrics_collector.set_threshold('system.disk_percent', warning=90.0, critical=98.0)

# Setup thresholds on import
setup_default_thresholds()
