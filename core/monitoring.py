"""
Production Monitoring and Observability for MASS Framework
Provides metrics, health checks, and monitoring endpoints for cloud deployment
"""

import asyncio
import logging
import time
import psutil
import aiohttp
import redis
import pymongo
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import os
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class HealthCheck:
    """Health check result"""
    service: str
    status: HealthStatus
    response_time_ms: float
    details: Dict[str, Any]
    timestamp: datetime
    error_message: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    active_connections: int
    timestamp: datetime

class DatabaseHealthChecker:
    """Database health monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.postgres_url = config.get('postgres_url')
        self.redis_url = config.get('redis_url')
        self.mongo_url = config.get('mongo_url')
        
    async def check_postgres_health(self) -> HealthCheck:
        """Check PostgreSQL health"""
        start_time = time.time()
        
        try:
            if not self.postgres_url:
                return HealthCheck(
                    service="postgresql",
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    details={"error": "No PostgreSQL URL configured"},
                    timestamp=datetime.utcnow()
                )
            
            # Test connection
            import asyncpg
            conn = await asyncpg.connect(self.postgres_url)
            
            # Test query
            result = await conn.fetchval("SELECT 1")
            await conn.close()
            
            response_time = (time.time() - start_time) * 1000
            
            if result == 1:
                return HealthCheck(
                    service="postgresql",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=response_time,
                    details={"connection": "ok", "query_test": "passed"},
                    timestamp=datetime.utcnow()
                )
            else:
                return HealthCheck(
                    service="postgresql",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=response_time,
                    details={"connection": "ok", "query_test": "failed"},
                    timestamp=datetime.utcnow(),
                    error_message="Query test failed"
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                service="postgresql",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"connection": "failed", "error": str(e)},
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def check_redis_health(self) -> HealthCheck:
        """Check Redis health"""
        start_time = time.time()
        
        try:
            if not self.redis_url:
                return HealthCheck(
                    service="redis",
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    details={"error": "No Redis URL configured"},
                    timestamp=datetime.utcnow()
                )
            
            # Test connection
            redis_client = redis.from_url(self.redis_url)
            
            # Test ping
            result = redis_client.ping()
            
            # Test set/get
            test_key = f"health_check_{int(time.time())}"
            redis_client.set(test_key, "test_value", ex=60)
            test_value = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            response_time = (time.time() - start_time) * 1000
            
            if result and test_value == b"test_value":
                return HealthCheck(
                    service="redis",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=response_time,
                    details={"connection": "ok", "ping": "ok", "read_write": "ok"},
                    timestamp=datetime.utcnow()
                )
            else:
                return HealthCheck(
                    service="redis",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=response_time,
                    details={"connection": "ok", "ping": "failed", "read_write": "failed"},
                    timestamp=datetime.utcnow(),
                    error_message="Redis operations failed"
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                service="redis",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"connection": "failed", "error": str(e)},
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def check_mongo_health(self) -> HealthCheck:
        """Check MongoDB health"""
        start_time = time.time()
        
        try:
            if not self.mongo_url:
                return HealthCheck(
                    service="mongodb",
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    details={"error": "No MongoDB URL configured"},
                    timestamp=datetime.utcnow()
                )
            
            # Test connection
            client = pymongo.MongoClient(self.mongo_url)
            
            # Test ping
            result = client.admin.command('ping')
            
            # Test database operations
            test_db = client.test
            test_collection = test_db.health_check
            test_doc = {"test": "value", "timestamp": datetime.utcnow()}
            
            # Insert test document
            insert_result = test_collection.insert_one(test_doc)
            
            # Read test document
            read_result = test_collection.find_one({"_id": insert_result.inserted_id})
            
            # Delete test document
            test_collection.delete_one({"_id": insert_result.inserted_id})
            
            client.close()
            
            response_time = (time.time() - start_time) * 1000
            
            if result.get('ok') == 1 and read_result:
                return HealthCheck(
                    service="mongodb",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=response_time,
                    details={"connection": "ok", "ping": "ok", "crud_operations": "ok"},
                    timestamp=datetime.utcnow()
                )
            else:
                return HealthCheck(
                    service="mongodb",
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=response_time,
                    details={"connection": "ok", "ping": "failed", "crud_operations": "failed"},
                    timestamp=datetime.utcnow(),
                    error_message="MongoDB operations failed"
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                service="mongodb",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"connection": "failed", "error": str(e)},
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )

class AIHealthChecker:
    """AI services health monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.openai_key = config.get('openai_api_key')
        self.anthropic_key = config.get('anthropic_api_key')
        
    async def check_openai_health(self) -> HealthCheck:
        """Check OpenAI API health"""
        start_time = time.time()
        
        try:
            if not self.openai_key:
                return HealthCheck(
                    service="openai",
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    details={"error": "No OpenAI API key configured"},
                    timestamp=datetime.utcnow()
                )
            
            # Test OpenAI API
            headers = {
                "Authorization": f"Bearer {self.openai_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200 and 'choices' in result:
                        return HealthCheck(
                            service="openai",
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time,
                            details={"connection": "ok", "api_test": "passed"},
                            timestamp=datetime.utcnow()
                        )
                    else:
                        return HealthCheck(
                            service="openai",
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time,
                            details={"connection": "ok", "api_test": "failed", "error": result.get('error', 'Unknown error')},
                            timestamp=datetime.utcnow(),
                            error_message=f"OpenAI API error: {result.get('error', 'Unknown error')}"
                        )
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                service="openai",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"connection": "failed", "error": str(e)},
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
    
    async def check_anthropic_health(self) -> HealthCheck:
        """Check Anthropic API health"""
        start_time = time.time()
        
        try:
            if not self.anthropic_key:
                return HealthCheck(
                    service="anthropic",
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    details={"error": "No Anthropic API key configured"},
                    timestamp=datetime.utcnow()
                )
            
            # Test Anthropic API
            headers = {
                "x-api-key": self.anthropic_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Hello"}]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200 and 'content' in result:
                        return HealthCheck(
                            service="anthropic",
                            status=HealthStatus.HEALTHY,
                            response_time_ms=response_time,
                            details={"connection": "ok", "api_test": "passed"},
                            timestamp=datetime.utcnow()
                        )
                    else:
                        return HealthCheck(
                            service="anthropic",
                            status=HealthStatus.UNHEALTHY,
                            response_time_ms=response_time,
                            details={"connection": "ok", "api_test": "failed", "error": result.get('error', 'Unknown error')},
                            timestamp=datetime.utcnow(),
                            error_message=f"Anthropic API error: {result.get('error', 'Unknown error')}"
                        )
                        
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                service="anthropic",
                status=HealthStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"connection": "failed", "error": str(e)},
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )

class SystemMonitor:
    """Enhanced system monitor with performance optimization"""
    """System performance monitoring"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history: List[SystemMetrics] = []
        
        # Performance optimization settings
        self.performance_thresholds = {
            'cpu_warning': 70.0,
            'cpu_critical': 85.0,
            'memory_warning': 80.0,
            'memory_critical': 90.0,
            'response_time_warning': 1.0,
            'response_time_critical': 2.0
        }
        
        # Performance tracking
        self.performance_alerts = []
        self.optimization_recommendations = []
        self.max_history_size = config.get('max_history_size', 1000)
        
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # Network I/O
            network = psutil.net_io_counters()
            network_io = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            }
            
            # Active connections (approximate)
            active_connections = len(psutil.net_connections())
            
            metrics = SystemMetrics(
                cpu_usage_percent=cpu_usage,
                memory_usage_percent=memory_usage,
                disk_usage_percent=disk_usage,
                network_io_bytes=network_io,
                active_connections=active_connections,
                timestamp=datetime.utcnow()
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            # Trim history if too large
            if len(self.metrics_history) > self.max_history_size:
                self.metrics_history = self.metrics_history[-self.max_history_size:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"System metrics error: {e}")
            return SystemMetrics(
                cpu_usage_percent=0.0,
                memory_usage_percent=0.0,
                disk_usage_percent=0.0,
                network_io_bytes={'bytes_sent': 0, 'bytes_recv': 0},
                active_connections=0,
                timestamp=datetime.utcnow()
            )
    
    def get_metrics_history(self, hours: int = 24) -> List[SystemMetrics]:
        """Get system metrics history"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        except Exception as e:
            logger.error(f"Get metrics history error: {e}")
            return []
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds"""
        try:
            alerts = []
            current_metrics = self.get_system_metrics()
            
            # CPU alert
            if current_metrics.cpu_usage_percent > 80:
                alerts.append({
                    'type': 'high_cpu',
                    'severity': 'warning',
                    'message': f"High CPU usage: {current_metrics.cpu_usage_percent:.1f}%",
                    'timestamp': current_metrics.timestamp.isoformat()
                })
            
            # Memory alert
            if current_metrics.memory_usage_percent > 85:
                alerts.append({
                    'type': 'high_memory',
                    'severity': 'warning',
                    'message': f"High memory usage: {current_metrics.memory_usage_percent:.1f}%",
                    'timestamp': current_metrics.timestamp.isoformat()
                })
            
            # Disk alert
            if current_metrics.disk_usage_percent > 90:
                alerts.append({
                    'type': 'high_disk',
                    'severity': 'critical',
                    'message': f"High disk usage: {current_metrics.disk_usage_percent:.1f}%",
                    'timestamp': current_metrics.timestamp.isoformat()
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Performance alerts error: {e}")
            return []
    
    def analyze_performance_trends(self) -> Dict[str, Any]:
        """Analyze performance trends and provide optimization recommendations"""
        try:
            if len(self.metrics_history) < 10:
                return {'status': 'insufficient_data', 'message': 'Need at least 10 data points for analysis'}
            
            # Analyze recent metrics (last 10 data points)
            recent_metrics = self.metrics_history[-10:]
            
            # Calculate trends
            cpu_trend = self._calculate_trend([m.cpu_usage_percent for m in recent_metrics])
            memory_trend = self._calculate_trend([m.memory_usage_percent for m in recent_metrics])
            
            # Generate optimization recommendations
            recommendations = []
            
            if cpu_trend > 5:  # CPU usage increasing
                recommendations.append({
                    'type': 'cpu_optimization',
                    'priority': 'high',
                    'message': 'CPU usage is trending upward. Consider optimizing CPU-intensive operations.',
                    'suggestions': [
                        'Implement caching for frequently accessed data',
                        'Optimize database queries',
                        'Use async/await for I/O operations',
                        'Consider horizontal scaling'
                    ]
                })
            
            if memory_trend > 5:  # Memory usage increasing
                recommendations.append({
                    'type': 'memory_optimization',
                    'priority': 'medium',
                    'message': 'Memory usage is trending upward. Monitor for memory leaks.',
                    'suggestions': [
                        'Review memory usage patterns',
                        'Implement garbage collection optimization',
                        'Consider memory pooling',
                        'Monitor for memory leaks'
                    ]
                })
            
            # Check for performance bottlenecks
            avg_cpu = sum(m.cpu_usage_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_usage_percent for m in recent_metrics) / len(recent_metrics)
            
            if avg_cpu > self.performance_thresholds['cpu_warning']:
                recommendations.append({
                    'type': 'cpu_bottleneck',
                    'priority': 'critical',
                    'message': f'Average CPU usage ({avg_cpu:.1f}%) exceeds warning threshold',
                    'suggestions': ['Immediate CPU optimization required']
                })
            
            if avg_memory > self.performance_thresholds['memory_warning']:
                recommendations.append({
                    'type': 'memory_bottleneck',
                    'priority': 'critical',
                    'message': f'Average memory usage ({avg_memory:.1f}%) exceeds warning threshold',
                    'suggestions': ['Immediate memory optimization required']
                })
            
            self.optimization_recommendations = recommendations
            
            return {
                'status': 'analysis_complete',
                'trends': {
                    'cpu_trend': cpu_trend,
                    'memory_trend': memory_trend
                },
                'averages': {
                    'cpu_usage': avg_cpu,
                    'memory_usage': avg_memory
                },
                'recommendations': recommendations,
                'analysis_timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Performance trend analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend (positive = increasing, negative = decreasing)"""
        if len(values) < 2:
            return 0.0
        
        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values
        
        # Calculate slope
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get current optimization recommendations"""
        return self.optimization_recommendations

class MonitoringService:
    """Main monitoring service that coordinates all health checks"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_checker = DatabaseHealthChecker(config.get('database', {}))
        self.ai_checker = AIHealthChecker(config.get('ai_services', {}))
        self.system_monitor = SystemMonitor(config.get('system', {}))
        self.health_history: List[HealthCheck] = []
        self.max_health_history = config.get('max_health_history', 1000)
        
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        try:
            health_checks = []
            
            # Database health checks
            postgres_health = await self.db_checker.check_postgres_health()
            health_checks.append(postgres_health)
            
            redis_health = await self.db_checker.check_redis_health()
            health_checks.append(redis_health)
            
            mongo_health = await self.db_checker.check_mongo_health()
            health_checks.append(mongo_health)
            
            # AI services health checks
            openai_health = await self.ai_checker.check_openai_health()
            health_checks.append(openai_health)
            
            anthropic_health = await self.ai_checker.check_anthropic_health()
            health_checks.append(anthropic_health)
            
            # System metrics
            system_metrics = self.system_monitor.get_system_metrics()
            
            # Store health checks in history
            for check in health_checks:
                self.health_history.append(check)
            
            # Trim history if too large
            if len(self.health_history) > self.max_health_history:
                self.health_history = self.health_history[-self.max_health_history:]
            
            # Calculate overall health
            overall_status = self._calculate_overall_health(health_checks)
            
            # Get performance alerts
            alerts = self.system_monitor.get_performance_alerts()
            
            return {
                'overall_status': overall_status.value,
                'health_checks': [asdict(check) for check in health_checks],
                'system_metrics': asdict(system_metrics),
                'alerts': alerts,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health checks error: {e}")
            return {
                'overall_status': HealthStatus.UNHEALTHY.value,
                'health_checks': [],
                'system_metrics': {},
                'alerts': [{'type': 'monitoring_error', 'severity': 'critical', 'message': str(e)}],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _calculate_overall_health(self, health_checks: List[HealthCheck]) -> HealthStatus:
        """Calculate overall system health"""
        try:
            if not health_checks:
                return HealthStatus.UNKNOWN
            
            status_counts = {}
            for check in health_checks:
                status = check.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # If any service is unhealthy, overall is unhealthy
            if status_counts.get('unhealthy', 0) > 0:
                return HealthStatus.UNHEALTHY
            
            # If any service is degraded, overall is degraded
            if status_counts.get('degraded', 0) > 0:
                return HealthStatus.DEGRADED
            
            # If all services are healthy, overall is healthy
            if status_counts.get('healthy', 0) == len(health_checks):
                return HealthStatus.HEALTHY
            
            # Default to unknown
            return HealthStatus.UNKNOWN
            
        except Exception as e:
            logger.error(f"Overall health calculation error: {e}")
            return HealthStatus.UNKNOWN
    
    async def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            recent_checks = [check for check in self.health_history if check.timestamp >= cutoff_time]
            return [asdict(check) for check in recent_checks]
        except Exception as e:
            logger.error(f"Get health history error: {e}")
            return []
    
    async def get_service_status(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific service"""
        try:
            # Find the most recent health check for the service
            for check in reversed(self.health_history):
                if check.service == service_name:
                    return asdict(check)
            return None
        except Exception as e:
            logger.error(f"Get service status error: {e}")
            return None
    
    async def get_system_summary(self) -> Dict[str, Any]:
        """Get system monitoring summary"""
        try:
            # Get recent health checks
            recent_checks = self.health_history[-10:] if self.health_history else []
            
            # Calculate service availability
            service_availability = {}
            for check in recent_checks:
                service = check.service
                if service not in service_availability:
                    service_availability[service] = {'healthy': 0, 'total': 0}
                
                service_availability[service]['total'] += 1
                if check.status == HealthStatus.HEALTHY:
                    service_availability[service]['healthy'] += 1
            
            # Calculate availability percentages
            for service in service_availability:
                total = service_availability[service]['total']
                healthy = service_availability[service]['healthy']
                service_availability[service]['availability_percent'] = (healthy / total * 100) if total > 0 else 0
            
            # Get current system metrics
            current_metrics = self.system_monitor.get_system_metrics()
            
            # Get performance alerts
            alerts = self.system_monitor.get_performance_alerts()
            
            return {
                'service_availability': service_availability,
                'current_metrics': asdict(current_metrics),
                'alerts': alerts,
                'total_health_checks': len(self.health_history),
                'last_check_time': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"System summary error: {e}")
            return {
                'service_availability': {},
                'current_metrics': {},
                'alerts': [{'type': 'summary_error', 'severity': 'critical', 'message': str(e)}],
                'total_health_checks': 0,
                'last_check_time': datetime.utcnow().isoformat()
            }
