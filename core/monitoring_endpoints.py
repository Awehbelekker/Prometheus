"""
Monitoring and Observability API Endpoints for MASS Framework
Provides endpoints for health checks, metrics, and system monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, List
import asyncio
import json
from datetime import datetime, timezone

from .observability import observability, MetricsCollector, HealthChecker

# Create monitoring router
monitoring_router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@monitoring_router.get("/health")
async def get_health_status(request: Request):
    """
    Get comprehensive health status of all system components
    
    Returns:
        dict: Health status including overall status and individual service health
    """
    try:
        # Get database manager from app state if available
        db_manager = getattr(request.app.state, 'db_manager', None)
        
        # Run health checks
        health_results = await observability.health_checker.run_all_health_checks(db_manager)
        health_summary = observability.health_checker.get_health_summary()
        
        return {
            "status": "success",
            "data": {
                "overall": health_summary,
                "details": [result.to_dict() for result in health_results if hasattr(result, 'to_dict')]
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@monitoring_router.get("/health/simple")
async def get_simple_health():
    """
    Simple health check endpoint for load balancers and uptime monitoring
    
    Returns:
        dict: Simple health status
    """
    try:
        health_summary = observability.health_checker.get_health_summary()
        status_code = 200 if health_summary["status"] in ["healthy", "degraded"] else 503
        
        return {
            "status": health_summary["status"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception:
        raise HTTPException(status_code=503, detail="Health check unavailable")

@monitoring_router.get("/metrics")
async def get_metrics():
    """
    Get system and application metrics
    
    Returns:
        dict: Current metrics data including system and application metrics
    """
    try:
        # Collect fresh metrics
        system_metrics = observability.metrics_collector.collect_system_metrics()
        app_metrics = observability.metrics_collector.collect_application_metrics()
        
        all_metrics = system_metrics + app_metrics
        observability.metrics_collector.store_metrics(all_metrics)
        
        return {
            "status": "success",
            "data": {
                "current": [metric.to_dict() for metric in all_metrics],
                "history_count": len(observability.metrics_collector.metrics_history),
                "collection_time": datetime.now(timezone.utc).isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")

@monitoring_router.get("/metrics/history")
async def get_metrics_history(limit: int = 100):
    """
    Get historical metrics data
    
    Args:
        limit: Maximum number of historical metrics to return
        
    Returns:
        dict: Historical metrics data
    """
    try:
        history = observability.metrics_collector.metrics_history
        limited_history = history[-limit:] if len(history) > limit else history
        
        return {
            "status": "success",
            "data": {
                "metrics": [metric.to_dict() for metric in limited_history],
                "total_count": len(history),
                "returned_count": len(limited_history)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics history: {str(e)}")

@monitoring_router.get("/status")
async def get_system_status(request: Request):
    """
    Get comprehensive system status including health, metrics, and configuration
    
    Returns:
        dict: Complete system status overview
    """
    try:
        # Get monitoring data
        monitoring_data = observability.get_monitoring_data()
        
        # Get application state info
        app_state_info = {}
        if hasattr(request.app.state, 'auth_service'):
            app_state_info['authentication'] = 'available'
        if hasattr(request.app.state, 'collaboration_manager'):
            app_state_info['collaboration'] = 'available'
        if hasattr(request.app.state, 'db_manager'):
            app_state_info['database'] = 'available'
        
        return {
            "status": "success",
            "data": {
                "system": monitoring_data,
                "application": {
                    "services": app_state_info,
                    "uptime_seconds": observability._get_uptime_seconds(),
                    "version": "2.0.0",  # Version from your roadmap
                    "environment": "production"  # Could be from env var
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@monitoring_router.post("/monitoring/start")
async def start_monitoring(request: Request):
    """
    Start continuous monitoring
    
    Returns:
        dict: Monitoring start confirmation
    """
    try:
        db_manager = getattr(request.app.state, 'db_manager', None)
        await observability.start_monitoring(db_manager)
        
        return {
            "status": "success",
            "message": "Monitoring started",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@monitoring_router.post("/monitoring/stop")
async def stop_monitoring():
    """
    Stop continuous monitoring
    
    Returns:
        dict: Monitoring stop confirmation
    """
    try:
        await observability.stop_monitoring()
        
        return {
            "status": "success",
            "message": "Monitoring stopped",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@monitoring_router.get("/logs")
async def get_recent_logs(lines: int = 100):
    """
    Get recent log entries
    
    Args:
        lines: Number of recent log lines to return
        
    Returns:
        dict: Recent log entries
    """
    try:
        log_files = [
            "logs/mass_framework.log",
            "logs/metrics.log",
            "logs/health.log"
        ]
        
        logs_data = {}
        
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                    logs_data[log_file] = {
                        "lines": [line.strip() for line in recent_lines],
                        "total_lines": len(all_lines),
                        "returned_lines": len(recent_lines)
                    }
            except FileNotFoundError:
                logs_data[log_file] = {
                    "lines": [],
                    "total_lines": 0,
                    "returned_lines": 0,
                    "error": "Log file not found"
                }
        
        return {
            "status": "success",
            "data": logs_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")

@monitoring_router.get("/alerts")
async def get_active_alerts():
    """
    Get active system alerts based on health checks and metrics
    
    Returns:
        dict: Active alerts and warnings
    """
    try:
        alerts = []
        
        # Check recent health results for issues
        health_summary = observability.health_checker.get_health_summary()
        
        for service, info in health_summary.get("services", {}).items():
            if info["status"] == "unhealthy":
                alerts.append({
                    "severity": "critical",
                    "service": service,
                    "message": f"Service {service} is unhealthy",
                    "timestamp": info["last_check"]
                })
            elif info["status"] == "degraded":
                alerts.append({
                    "severity": "warning",
                    "service": service,
                    "message": f"Service {service} is degraded",
                    "timestamp": info["last_check"]
                })
        
        # Check metrics for threshold violations
        recent_metrics = observability.metrics_collector.metrics_history[-10:]
        for metric in recent_metrics:
            if metric.name == "system_cpu_usage_percent" and metric.value > 90:
                alerts.append({
                    "severity": "warning",
                    "service": "system",
                    "message": f"High CPU usage: {metric.value}%",
                    "timestamp": metric.timestamp.isoformat()
                })
            elif metric.name == "system_memory_usage_percent" and metric.value > 90:
                alerts.append({
                    "severity": "warning",
                    "service": "system",
                    "message": f"High memory usage: {metric.value}%",
                    "timestamp": metric.timestamp.isoformat()
                })
        
        return {
            "status": "success",
            "data": {
                "alerts": alerts,
                "total_count": len(alerts),
                "critical_count": len([a for a in alerts if a["severity"] == "critical"]),
                "warning_count": len([a for a in alerts if a["severity"] == "warning"])
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

# Add helper method to observability manager
def _get_uptime_seconds(self):
    """Get application uptime in seconds"""
    if not hasattr(self, '_start_time'):
        self._start_time = datetime.now(timezone.utc)
    return (datetime.now(timezone.utc) - self._start_time).total_seconds()

# Monkey patch the method
observability._get_uptime_seconds = _get_uptime_seconds.__get__(observability)
