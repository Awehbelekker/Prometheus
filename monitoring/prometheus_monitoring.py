#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Enhanced Monitoring & Alerting System
Enterprise-grade monitoring for trading operations
"""

import time
import json
import psutil
import sqlite3
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Prometheus Metrics
TRADE_COUNTER = Counter('prometheus_trades_total', 'Total number of trades', ['symbol', 'order_type', 'status'])
TRADE_LATENCY = Histogram('prometheus_trade_latency_seconds', 'Trade execution latency')
PORTFOLIO_VALUE = Gauge('prometheus_portfolio_value_usd', 'Total portfolio value in USD', ['user_id'])
MARKET_DATA_REQUESTS = Counter('prometheus_market_data_requests_total', 'Market data requests', ['provider', 'symbol'])
API_REQUESTS = Counter('prometheus_api_requests_total', 'API requests', ['endpoint', 'method', 'status'])
SYSTEM_CPU = Gauge('prometheus_system_cpu_percent', 'System CPU usage percentage')
SYSTEM_MEMORY = Gauge('prometheus_system_memory_percent', 'System memory usage percentage')
ACTIVE_USERS = Gauge('prometheus_active_users', 'Number of active users')
ERROR_RATE = Counter('prometheus_errors_total', 'Total errors', ['component', 'error_type'])

@dataclass
class Alert:
    """Alert data structure."""
    id: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    component: str
    message: str
    timestamp: datetime
    resolved: bool = False
    acknowledged: bool = False
    metadata: Dict[str, Any] = None

class PrometheusMonitoring:
    """Comprehensive monitoring system for PROMETHEUS Trading Platform."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        self.alerts: List[Alert] = []
        self.alert_handlers = []
        self.metrics_db = "monitoring/metrics.db"
        self.setup_logging()
        self.setup_database()
        
    def _default_config(self) -> Dict[str, Any]:
        """Default monitoring configuration."""
        return {
            "metrics_port": 8001,
            "alert_thresholds": {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "trade_latency": 5.0,
                "error_rate": 0.05,
                "portfolio_drawdown": 0.10
            },
            "email_alerts": {
                "enabled": True,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "from_email": "alerts@prometheus-trading.com",
                "to_emails": ["admin@prometheus-trading.com"]
            },
            "monitoring_interval": 30,  # seconds
            "retention_days": 30
        }
    
    def setup_logging(self):
        """Setup monitoring logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('monitoring/prometheus_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_database(self):
        """Setup monitoring database."""
        import os
        os.makedirs("monitoring", exist_ok=True)
        
        conn = sqlite3.connect(self.metrics_db)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                labels TEXT,
                component TEXT
            )
        """)
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                severity TEXT NOT NULL,
                component TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                acknowledged BOOLEAN DEFAULT FALSE,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def start_metrics_server(self):
        """Start Prometheus metrics server."""
        try:
            start_http_server(self.config["metrics_port"])
            self.logger.info(f"Metrics server started on port {self.config['metrics_port']}")
        except Exception as e:
            self.logger.error(f"Failed to start metrics server: {e}")
    
    def record_trade_metrics(self, trade_data: Dict[str, Any]):
        """Record trade-specific metrics."""
        symbol = trade_data.get("symbol", "UNKNOWN")
        order_type = trade_data.get("order_type", "UNKNOWN")
        status = trade_data.get("status", "UNKNOWN")
        latency = trade_data.get("execution_time", 0)
        
        # Update Prometheus metrics
        TRADE_COUNTER.labels(symbol=symbol, order_type=order_type, status=status).inc()
        TRADE_LATENCY.observe(latency)
        
        # Store in database
        self._store_metric("trade_executed", 1, {
            "symbol": symbol,
            "order_type": order_type,
            "status": status,
            "latency": latency
        })
        
        # Check for alerts
        if latency > self.config["alert_thresholds"]["trade_latency"]:
            self.create_alert(
                severity="HIGH",
                component="trading_engine",
                message=f"High trade latency detected: {latency:.2f}s for {symbol}",
                metadata=trade_data
            )
    
    def record_portfolio_metrics(self, user_id: str, portfolio_data: Dict[str, Any]):
        """Record portfolio-specific metrics."""
        total_value = portfolio_data.get("total_value", 0)
        daily_return = portfolio_data.get("daily_return", 0)
        total_return = portfolio_data.get("total_return", 0)
        
        # Update Prometheus metrics
        PORTFOLIO_VALUE.labels(user_id=user_id).set(total_value)
        
        # Store in database
        self._store_metric("portfolio_value", total_value, {"user_id": user_id})
        self._store_metric("daily_return", daily_return, {"user_id": user_id})
        
        # Check for drawdown alerts
        if total_return < -self.config["alert_thresholds"]["portfolio_drawdown"]:
            self.create_alert(
                severity="MEDIUM",
                component="portfolio_management",
                message=f"Portfolio drawdown alert for user {user_id}: {total_return:.2%}",
                metadata={"user_id": user_id, "drawdown": total_return}
            )
    
    def record_system_metrics(self):
        """Record system performance metrics."""
        # CPU and Memory usage
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Update Prometheus metrics
        SYSTEM_CPU.set(cpu_percent)
        SYSTEM_MEMORY.set(memory.percent)
        
        # Store in database
        self._store_metric("cpu_usage", cpu_percent)
        self._store_metric("memory_usage", memory.percent)
        self._store_metric("disk_usage", disk.percent)
        
        # Check for system alerts
        if cpu_percent > self.config["alert_thresholds"]["cpu_usage"]:
            self.create_alert(
                severity="HIGH",
                component="system",
                message=f"High CPU usage: {cpu_percent:.1f}%"
            )
        
        if memory.percent > self.config["alert_thresholds"]["memory_usage"]:
            self.create_alert(
                severity="HIGH",
                component="system",
                message=f"High memory usage: {memory.percent:.1f}%"
            )
        
        if disk.percent > self.config["alert_thresholds"]["disk_usage"]:
            self.create_alert(
                severity="CRITICAL",
                component="system",
                message=f"High disk usage: {disk.percent:.1f}%"
            )
    
    def record_api_metrics(self, endpoint: str, method: str, status_code: int, response_time: float):
        """Record API request metrics."""
        status = "success" if 200 <= status_code < 400 else "error"
        
        # Update Prometheus metrics
        API_REQUESTS.labels(endpoint=endpoint, method=method, status=status).inc()
        
        # Store in database
        self._store_metric("api_request", 1, {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time
        })
    
    def record_market_data_metrics(self, provider: str, symbol: str, success: bool):
        """Record market data request metrics."""
        status = "success" if success else "error"
        
        # Update Prometheus metrics
        MARKET_DATA_REQUESTS.labels(provider=provider, symbol=symbol).inc()
        
        if not success:
            ERROR_RATE.labels(component="market_data", error_type="request_failed").inc()
    
    def create_alert(self, severity: str, component: str, message: str, metadata: Dict[str, Any] = None):
        """Create and process an alert."""
        alert = Alert(
            id=f"alert_{int(time.time())}_{len(self.alerts)}",
            severity=severity,
            component=component,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.alerts.append(alert)
        self._store_alert(alert)
        self._process_alert(alert)
        
        self.logger.warning(f"ALERT [{severity}] {component}: {message}")
    
    def _store_metric(self, metric_name: str, value: float, labels: Dict[str, Any] = None):
        """Store metric in database."""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO metrics (metric_name, metric_value, labels, component)
                VALUES (?, ?, ?, ?)
            """, (metric_name, value, json.dumps(labels or {}), labels.get("component") if labels else None))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to store metric: {e}")
    
    def _store_alert(self, alert: Alert):
        """Store alert in database."""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO alerts (id, severity, component, message, timestamp, resolved, acknowledged, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id, alert.severity, alert.component, alert.message,
                alert.timestamp, alert.resolved, alert.acknowledged,
                json.dumps(alert.metadata or {})
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Failed to store alert: {e}")
    
    def _process_alert(self, alert: Alert):
        """Process alert through configured handlers."""
        # Email alerts
        if self.config["email_alerts"]["enabled"]:
            self._send_email_alert(alert)
        
        # Custom alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")
    
    def _send_email_alert(self, alert: Alert):
        """Send email alert."""
        try:
            email_config = self.config["email_alerts"]
            
            msg = MimeMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = f"PROMETHEUS Alert [{alert.severity}] - {alert.component}"
            
            body = f"""
            Alert Details:
            - Severity: {alert.severity}
            - Component: {alert.component}
            - Message: {alert.message}
            - Timestamp: {alert.timestamp}
            - Metadata: {json.dumps(alert.metadata, indent=2)}
            
            Please investigate and take appropriate action.
            
            PROMETHEUS Trading Platform Monitoring System
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            # Note: In production, use proper authentication
            # server.login(email_config["username"], email_config["password"])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Active alerts
        active_alerts = [alert for alert in self.alerts if not alert.resolved]
        critical_alerts = [alert for alert in active_alerts if alert.severity == "CRITICAL"]
        
        # Calculate health score
        health_score = 100
        if cpu_percent > 80: health_score -= 20
        if memory.percent > 85: health_score -= 20
        if disk.percent > 90: health_score -= 30
        health_score -= len(critical_alerts) * 15
        health_score = max(0, health_score)
        
        return {
            "health_score": health_score,
            "status": "healthy" if health_score > 80 else "degraded" if health_score > 50 else "critical",
            "timestamp": datetime.now().isoformat(),
            "system_metrics": {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent
            },
            "alerts": {
                "total": len(self.alerts),
                "active": len(active_alerts),
                "critical": len(critical_alerts)
            },
            "services": {
                "database": self._check_database_health(),
                "market_data": self._check_market_data_health(),
                "trading_engines": self._check_trading_engines_health()
            }
        }
    
    def _check_database_health(self) -> str:
        """Check database health."""
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return "healthy"
        except Exception:
            return "unhealthy"
    
    def _check_market_data_health(self) -> str:
        """Check market data service health."""
        # This would check actual market data connections
        return "healthy"  # Placeholder
    
    def _check_trading_engines_health(self) -> str:
        """Check trading engines health."""
        # This would check actual trading engine status
        return "healthy"  # Placeholder
    
    def generate_monitoring_report(self, hours: int = 24) -> Dict[str, Any]:
        """Generate comprehensive monitoring report."""
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        try:
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            # Get metrics for the period
            cursor.execute("""
                SELECT metric_name, AVG(metric_value) as avg_value, 
                       MIN(metric_value) as min_value, MAX(metric_value) as max_value,
                       COUNT(*) as count
                FROM metrics 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY metric_name
            """, (start_time, end_time))
            
            metrics_summary = {}
            for row in cursor.fetchall():
                metrics_summary[row[0]] = {
                    "average": row[1],
                    "minimum": row[2],
                    "maximum": row[3],
                    "count": row[4]
                }
            
            # Get alerts for the period
            cursor.execute("""
                SELECT severity, component, COUNT(*) as count
                FROM alerts 
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY severity, component
            """, (start_time, end_time))
            
            alerts_summary = {}
            for row in cursor.fetchall():
                key = f"{row[0]}_{row[1]}"
                alerts_summary[key] = row[2]
            
            conn.close()
            
            return {
                "report_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "hours": hours
                },
                "metrics_summary": metrics_summary,
                "alerts_summary": alerts_summary,
                "system_health": self.get_system_health(),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate monitoring report: {e}")
            return {"error": str(e)}
    
    async def start_monitoring_loop(self):
        """Start continuous monitoring loop."""
        self.logger.info("Starting PROMETHEUS monitoring loop")
        
        while True:
            try:
                # Record system metrics
                self.record_system_metrics()
                
                # Update active users count (placeholder)
                ACTIVE_USERS.set(10)  # This would be actual active user count
                
                # Clean up old metrics
                self._cleanup_old_metrics()
                
                await asyncio.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(5)  # Short delay before retry
    
    def _cleanup_old_metrics(self):
        """Clean up old metrics based on retention policy."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config["retention_days"])
            
            conn = sqlite3.connect(self.metrics_db)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM metrics WHERE timestamp < ?", (cutoff_date,))
            cursor.execute("DELETE FROM alerts WHERE timestamp < ? AND resolved = TRUE", (cutoff_date,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old metrics: {e}")


# Global monitoring instance
monitoring = PrometheusMonitoring()

def initialize_monitoring():
    """Initialize monitoring system."""
    monitoring.start_metrics_server()
    return monitoring

async def start_monitoring():
    """Start monitoring system."""
    await monitoring.start_monitoring_loop()

if __name__ == "__main__":
    # Start monitoring system
    monitoring.start_metrics_server()
    asyncio.run(monitoring.start_monitoring_loop())
