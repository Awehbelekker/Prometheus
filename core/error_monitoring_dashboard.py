"""
Error Monitoring Dashboard and Analytics System
Real-time error tracking, alerting, and performance monitoring
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sqlite3
from collections import defaultdict, deque

from core.error_handling import (
    TradingError, ErrorSeverity, ErrorCategory, ErrorContext,
    error_database, error_logger
)

logger = logging.getLogger(__name__)

@dataclass
class ErrorAlert:
    """Error alert configuration"""
    error_type: str
    severity: ErrorSeverity
    threshold: int  # Number of errors in time window
    time_window_minutes: int
    enabled: bool = True
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = ["log", "email"]

@dataclass
class SystemHealth:
    """System health metrics"""
    timestamp: datetime
    broker_health: Dict[str, str]  # broker -> health status
    error_rate: float  # errors per minute
    critical_errors: int
    total_errors: int
    uptime_percentage: float
    last_error: Optional[datetime] = None

class ErrorAnalytics:
    """Error analytics and trend analysis"""
    
    def __init__(self):
        self.error_trends = deque(maxlen=1440)  # 24 hours of minute-by-minute data
        self.broker_performance = defaultdict(lambda: {
            'total_errors': 0,
            'critical_errors': 0,
            'last_error': None,
            'error_rate': 0.0
        })
    
    def analyze_error_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Analyze error trends over time"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in error_database.errors
            if datetime.fromisoformat(error['timestamp']) > cutoff
        ]
        
        if not recent_errors:
            return {
                'trend': 'stable',
                'error_rate': 0.0,
                'peak_hour': None,
                'most_common_error': None,
                'broker_reliability': {}
            }
        
        # Calculate error rate (errors per hour)
        error_rate = len(recent_errors) / hours
        
        # Find peak error hour
        hourly_errors = defaultdict(int)
        for error in recent_errors:
            hour = datetime.fromisoformat(error['timestamp']).hour
            hourly_errors[hour] += 1
        
        peak_hour = max(hourly_errors.items(), key=lambda x: x[1])[0] if hourly_errors else None
        
        # Find most common error type
        error_types = defaultdict(int)
        for error in recent_errors:
            error_types[error['category']] += 1
        
        most_common_error = max(error_types.items(), key=lambda x: x[1])[0] if error_types else None
        
        # Calculate broker reliability
        broker_reliability = {}
        for broker in ['IB', 'Alpaca']:
            broker_errors = [e for e in recent_errors if e['context']['broker'] == broker]
            total_operations = 100  # Assume 100 operations per hour (rough estimate)
            reliability = max(0, (total_operations - len(broker_errors)) / total_operations * 100)
            broker_reliability[broker] = reliability
        
        # Determine trend
        if error_rate < 1:
            trend = 'excellent'
        elif error_rate < 5:
            trend = 'good'
        elif error_rate < 10:
            trend = 'warning'
        else:
            trend = 'critical'
        
        return {
            'trend': trend,
            'error_rate': error_rate,
            'peak_hour': peak_hour,
            'most_common_error': most_common_error,
            'broker_reliability': broker_reliability,
            'total_errors': len(recent_errors)
        }
    
    def get_broker_performance(self, hours: int = 24) -> Dict[str, Any]:
        """Get broker performance metrics"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_errors = [
            error for error in error_database.errors
            if datetime.fromisoformat(error['timestamp']) > cutoff
        ]
        
        performance = {}
        for broker in ['IB', 'Alpaca']:
            broker_errors = [e for e in recent_errors if e['context']['broker'] == broker]
            critical_errors = [e for e in broker_errors if e['severity'] == 'critical']
            
            performance[broker] = {
                'total_errors': len(broker_errors),
                'critical_errors': len(critical_errors),
                'error_rate_per_hour': len(broker_errors) / hours,
                'last_error': broker_errors[-1]['timestamp'] if broker_errors else None,
                'health_status': self._calculate_health_status(len(broker_errors), len(critical_errors), hours)
            }
        
        return performance
    
    def _calculate_health_status(self, total_errors: int, critical_errors: int, hours: int) -> str:
        """Calculate health status based on error metrics"""
        if critical_errors > 0:
            return 'CRITICAL'
        elif total_errors > hours * 2:  # More than 2 errors per hour
            return 'WARNING'
        elif total_errors > hours * 0.5:  # More than 0.5 errors per hour
            return 'DEGRADED'
        else:
            return 'HEALTHY'

class ErrorAlertManager:
    """Manages error alerts and notifications"""
    
    def __init__(self):
        self.alerts = [
            ErrorAlert(
                error_type="ConnectionError",
                severity=ErrorSeverity.HIGH,
                threshold=3,
                time_window_minutes=10
            ),
            ErrorAlert(
                error_type="AuthenticationError",
                severity=ErrorSeverity.CRITICAL,
                threshold=1,
                time_window_minutes=5
            ),
            ErrorAlert(
                error_type="OrderExecutionError",
                severity=ErrorSeverity.HIGH,
                threshold=2,
                time_window_minutes=15
            ),
            ErrorAlert(
                error_type="MarketDataError",
                severity=ErrorSeverity.MEDIUM,
                threshold=5,
                time_window_minutes=10
            )
        ]
        self.alert_history = deque(maxlen=1000)
    
    async def check_alerts(self):
        """Check if any alerts should be triggered"""
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            # Count recent errors of this type
            cutoff = datetime.now() - timedelta(minutes=alert.time_window_minutes)
            recent_errors = [
                error for error in error_database.errors
                if (datetime.fromisoformat(error['timestamp']) > cutoff and
                    error['category'] == alert.error_type.lower() and
                    error['severity'] == alert.severity.value)
            ]
            
            if len(recent_errors) >= alert.threshold:
                await self._trigger_alert(alert, recent_errors)
    
    async def _trigger_alert(self, alert: ErrorAlert, errors: List[Dict[str, Any]]):
        """Trigger an alert"""
        alert_data = {
            'alert_id': f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'alert_type': alert.error_type,
            'severity': alert.severity.value,
            'threshold': alert.threshold,
            'actual_count': len(errors),
            'time_window': alert.time_window_minutes,
            'timestamp': datetime.now().isoformat(),
            'errors': errors[-5:]  # Last 5 errors for context
        }
        
        self.alert_history.append(alert_data)
        
        # Log the alert
        logger.critical(f"🚨 ALERT TRIGGERED: {alert.error_type} - {len(errors)} errors in {alert.time_window_minutes} minutes")
        
        # Send notifications
        for channel in alert.notification_channels:
            await self._send_notification(channel, alert_data)
    
    async def _send_notification(self, channel: str, alert_data: Dict[str, Any]):
        """Send notification through specified channel"""
        if channel == "log":
            logger.critical(f"ALERT: {alert_data['alert_type']} - {alert_data['actual_count']} errors")
        elif channel == "email":
            # TODO: Implement email notifications
            logger.info("Email notification would be sent here")
        elif channel == "webhook":
            # TODO: Implement webhook notifications
            logger.info("Webhook notification would be sent here")

class ErrorMonitoringDashboard:
    """Main error monitoring dashboard"""
    
    def __init__(self):
        self.analytics = ErrorAnalytics()
        self.alert_manager = ErrorAlertManager()
        self.health_history = deque(maxlen=1440)  # 24 hours of health data
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous error monitoring"""
        self.monitoring_active = True
        logger.info("🔍 Starting error monitoring dashboard")
        
        while self.monitoring_active:
            try:
                # Update system health
                await self._update_system_health()
                
                # Check for alerts
                await self.alert_manager.check_alerts()
                
                # Log monitoring status
                if len(self.health_history) % 10 == 0:  # Every 10 minutes
                    await self._log_monitoring_status()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            await asyncio.sleep(interval_seconds)
    
    async def stop_monitoring(self):
        """Stop error monitoring"""
        self.monitoring_active = False
        logger.info("⏹️ Stopped error monitoring dashboard")
    
    async def _update_system_health(self):
        """Update system health metrics"""
        try:
            # Get recent errors (last hour)
            cutoff = datetime.now() - timedelta(hours=1)
            recent_errors = [
                error for error in error_database.errors
                if datetime.fromisoformat(error['timestamp']) > cutoff
            ]
            
            # Calculate broker health
            broker_health = {}
            for broker in ['IB', 'Alpaca']:
                broker_errors = [e for e in recent_errors if e['context']['broker'] == broker]
                critical_errors = [e for e in broker_errors if e['severity'] == 'critical']
                
                if critical_errors:
                    broker_health[broker] = 'CRITICAL'
                elif len(broker_errors) > 5:
                    broker_health[broker] = 'WARNING'
                elif len(broker_errors) > 0:
                    broker_health[broker] = 'DEGRADED'
                else:
                    broker_health[broker] = 'HEALTHY'
            
            # Calculate error rate (errors per minute)
            error_rate = len(recent_errors) / 60.0  # Last hour / 60 minutes
            
            # Calculate uptime percentage (simplified)
            uptime_percentage = max(0, 100 - (error_rate * 10))  # Rough calculation
            
            # Get last error time
            last_error = None
            if recent_errors:
                last_error = max(recent_errors, key=lambda x: x['timestamp'])['timestamp']
            
            health = SystemHealth(
                timestamp=datetime.now(),
                broker_health=broker_health,
                error_rate=error_rate,
                critical_errors=len([e for e in recent_errors if e['severity'] == 'critical']),
                total_errors=len(recent_errors),
                uptime_percentage=uptime_percentage,
                last_error=last_error
            )
            
            self.health_history.append(health)
            
        except Exception as e:
            logger.error(f"Failed to update system health: {e}")
    
    async def _log_monitoring_status(self):
        """Log current monitoring status"""
        if not self.health_history:
            return
        
        latest_health = self.health_history[-1]
        
        logger.info("📊 Error Monitoring Status:")
        logger.info(f"   Error Rate: {latest_health.error_rate:.2f} errors/min")
        logger.info(f"   Critical Errors: {latest_health.critical_errors}")
        logger.info(f"   Uptime: {latest_health.uptime_percentage:.1f}%")
        logger.info(f"   Broker Health: {latest_health.broker_health}")
    
    def get_dashboard_data(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Get error summary
            error_summary = error_database.get_error_summary(hours)
            
            # Get analytics
            analytics = self.analytics.analyze_error_trends(hours)
            broker_performance = self.analytics.get_broker_performance(hours)
            
            # Get recent alerts
            recent_alerts = list(self.alert_manager.alert_history)[-10:]  # Last 10 alerts
            
            # Get system health
            current_health = self.health_history[-1] if self.health_history else None
            
            return {
                'timestamp': datetime.now().isoformat(),
                'time_range_hours': hours,
                'error_summary': error_summary,
                'analytics': analytics,
                'broker_performance': broker_performance,
                'recent_alerts': recent_alerts,
                'system_health': asdict(current_health) if current_health else None,
                'monitoring_status': {
                    'active': self.monitoring_active,
                    'health_data_points': len(self.health_history),
                    'alert_history_count': len(self.alert_manager.alert_history)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, List[Any]]:
        """Get health trends over time"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_health = [
            health for health in self.health_history
            if health.timestamp > cutoff
        ]
        
        if not recent_health:
            return {'timestamps': [], 'error_rates': [], 'uptime': []}
        
        return {
            'timestamps': [h.timestamp.isoformat() for h in recent_health],
            'error_rates': [h.error_rate for h in recent_health],
            'uptime': [h.uptime_percentage for h in recent_health],
            'critical_errors': [h.critical_errors for h in recent_health]
        }
    
    def export_error_report(self, hours: int = 24, format: str = 'json') -> Union[str, Dict[str, Any]]:
        """Export error report in specified format"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours)
            recent_errors = [
                error for error in error_database.errors
                if datetime.fromisoformat(error['timestamp']) > cutoff
            ]
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'time_range_hours': hours,
                'total_errors': len(recent_errors),
                'errors_by_category': defaultdict(int),
                'errors_by_broker': defaultdict(int),
                'errors_by_severity': defaultdict(int),
                'detailed_errors': recent_errors[-100:]  # Last 100 errors
            }
            
            # Categorize errors
            for error in recent_errors:
                report['errors_by_category'][error['category']] += 1
                report['errors_by_broker'][error['context']['broker']] += 1
                report['errors_by_severity'][error['severity']] += 1
            
            if format == 'json':
                return json.dumps(report, indent=2, default=str)
            else:
                return report
                
        except Exception as e:
            logger.error(f"Failed to export error report: {e}")
            return f"Error generating report: {e}"

# Global instances
error_monitoring_dashboard = ErrorMonitoringDashboard()
error_analytics = ErrorAnalytics()
error_alert_manager = ErrorAlertManager()

# Utility functions
async def start_error_monitoring():
    """Start the error monitoring system"""
    await error_monitoring_dashboard.start_monitoring()

async def stop_error_monitoring():
    """Stop the error monitoring system"""
    await error_monitoring_dashboard.stop_monitoring()

def get_error_dashboard_data(hours: int = 24) -> Dict[str, Any]:
    """Get error dashboard data"""
    return error_monitoring_dashboard.get_dashboard_data(hours)

def export_error_report(hours: int = 24, format: str = 'json') -> Union[str, Dict[str, Any]]:
    """Export error report"""
    return error_monitoring_dashboard.export_error_report(hours, format)
