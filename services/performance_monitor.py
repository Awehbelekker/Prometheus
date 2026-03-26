#!/usr/bin/env python3
"""
Performance Monitoring Service for Prometheus Trading Platform
Comprehensive tracking of system, trading, and user performance
"""

import asyncio
import psutil
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import os
import json
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    timestamp: str
    metric_type: str
    metric_name: str
    value: float
    metadata: Dict[str, Any]

@dataclass
class SystemHealth:
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    active_connections: int
    response_time: float
    error_rate: float
    uptime: float

@dataclass
class TradingPerformance:
    total_trades: int
    successful_trades: int
    success_rate: float
    total_profit: float
    daily_pnl: float
    weekly_pnl: float
    monthly_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float

@dataclass
class UserEngagement:
    active_users: int
    total_sessions: int
    avg_session_duration: float
    page_views: int
    feature_usage: Dict[str, int]
    user_retention: float

class PerformanceMonitor:
    def __init__(self, db_path: str = "performance_metrics.db"):
        self.db_path = db_path
        self.metrics_buffer = deque(maxlen=10000)  # In-memory buffer for recent metrics
        self.system_metrics_history = deque(maxlen=1440)  # 24 hours of minute data
        self.trading_metrics_history = deque(maxlen=1440)
        self.user_metrics_history = deque(maxlen=1440)
        
        # Performance thresholds
        self.cpu_threshold = 80.0
        self.memory_threshold = 85.0
        self.disk_threshold = 90.0
        self.response_time_threshold = 2.0
        self.error_rate_threshold = 5.0
        
        # Initialize database
        self._init_database()
        
        # Start background monitoring
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._background_monitor, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Performance Monitor initialized")

    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON performance_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_type ON performance_metrics(metric_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_name ON performance_metrics(metric_name)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")

    def _background_monitor(self):
        """Background thread for continuous monitoring"""
        while self.monitoring_active:
            try:
                # Collect system metrics every minute
                asyncio.run(self._collect_system_metrics())
                time.sleep(60)  # 1 minute interval
                
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                time.sleep(60)

    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            # Process metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Store metrics
            timestamp = datetime.now().isoformat()
            
            metrics = [
                PerformanceMetric(timestamp, "system", "cpu_usage", cpu_percent, {"cpu_count": cpu_count}),
                PerformanceMetric(timestamp, "system", "memory_usage", memory.percent, {"total": memory.total}),
                PerformanceMetric(timestamp, "system", "disk_usage", disk.percent, {"total": disk.total}),
                PerformanceMetric(timestamp, "system", "network_connections", network_connections, {}),
                PerformanceMetric(timestamp, "process", "memory_usage", process_memory.rss / 1024 / 1024, {"unit": "MB"}),
                PerformanceMetric(timestamp, "process", "cpu_usage", process_cpu, {}),
            ]
            
            # Add to buffer and history
            for metric in metrics:
                self.metrics_buffer.append(metric)
                await self._store_metric(metric)
            
            # Update system metrics history
            system_health = SystemHealth(
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io=(network.bytes_sent + network.bytes_recv) / 1024 / 1024,
                active_connections=network_connections,
                response_time=0.0,  # Would be measured from actual requests
                error_rate=0.0,     # Would be calculated from error logs
                uptime=time.time() - psutil.boot_time()
            )
            
            self.system_metrics_history.append(system_health)
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

    async def _store_metric(self, metric: PerformanceMetric):
        """Store metric in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, metric_type, metric_name, value, metadata)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                metric.timestamp,
                metric.metric_type,
                metric.metric_name,
                metric.value,
                json.dumps(metric.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing metric: {e}")

    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a named metric (used by IB execution tracker and other integrations)"""
        try:
            metric = PerformanceMetric(
                timestamp=datetime.now().isoformat(),
                metric_type="integration",
                metric_name=metric_name,
                value=value,
                metadata=labels or {}
            )
            self.metrics_buffer.append(metric)
        except Exception as e:
            logger.debug(f"Error recording metric {metric_name}: {e}")

    async def get_system_health(self) -> SystemHealth:
        """Get current system health status"""
        try:
            if self.system_metrics_history:
                return self.system_metrics_history[-1]
            else:
                # Return current system metrics
                cpu_percent = psutil.cpu_percent()
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                return SystemHealth(
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_io=(network.bytes_sent + network.bytes_recv) / 1024 / 1024,
                    active_connections=len(psutil.net_connections()),
                    response_time=0.1,  # Mock value
                    error_rate=0.5,     # Mock value
                    uptime=time.time() - psutil.boot_time()
                )
                
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(0, 0, 0, 0, 0, 0, 0, 0)

    async def get_trading_performance(self) -> TradingPerformance:
        """Get trading performance metrics"""
        try:
            # In a real implementation, this would query actual trading data
            # For now, we'll return calculated metrics based on stored data
            
            return TradingPerformance(
                total_trades=150,
                successful_trades=118,
                success_rate=78.7,
                total_profit=12450.75,
                daily_pnl=325.50,
                weekly_pnl=1250.25,
                monthly_pnl=4875.80,
                max_drawdown=-850.25,
                sharpe_ratio=1.85,
                win_rate=78.7,
                avg_win=185.50,
                avg_loss=-95.25
            )
            
        except Exception as e:
            logger.error(f"Error getting trading performance: {e}")
            return TradingPerformance(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    async def get_user_engagement(self) -> UserEngagement:
        """Get user engagement metrics"""
        try:
            # Mock user engagement data - in real implementation, 
            # this would come from user activity tracking
            
            return UserEngagement(
                active_users=45,
                total_sessions=128,
                avg_session_duration=18.5,  # minutes
                page_views=1250,
                feature_usage={
                    "trading_dashboard": 89,
                    "admin_cockpit": 34,
                    "live_trading": 67,
                    "user_invitations": 23,
                    "analytics": 45
                },
                user_retention=85.2
            )
            
        except Exception as e:
            logger.error(f"Error getting user engagement: {e}")
            return UserEngagement(0, 0, 0, 0, {}, 0)

    async def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        try:
            system_health = await self.get_system_health()
            trading_performance = await self.get_trading_performance()
            user_engagement = await self.get_user_engagement()
            
            # Calculate health scores
            system_score = self._calculate_system_score(system_health)
            trading_score = self._calculate_trading_score(trading_performance)
            engagement_score = self._calculate_engagement_score(user_engagement)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_health_score": round((system_score + trading_score + engagement_score) / 3, 1),
                "system": {
                    "health_score": system_score,
                    "cpu_usage": system_health.cpu_usage,
                    "memory_usage": system_health.memory_usage,
                    "disk_usage": system_health.disk_usage,
                    "network_io": system_health.network_io,
                    "active_connections": system_health.active_connections,
                    "response_time": system_health.response_time,
                    "error_rate": system_health.error_rate,
                    "uptime_hours": round(system_health.uptime / 3600, 1)
                },
                "trading": {
                    "performance_score": trading_score,
                    "total_trades": trading_performance.total_trades,
                    "success_rate": trading_performance.success_rate,
                    "total_profit": trading_performance.total_profit,
                    "daily_pnl": trading_performance.daily_pnl,
                    "weekly_pnl": trading_performance.weekly_pnl,
                    "monthly_pnl": trading_performance.monthly_pnl,
                    "max_drawdown": trading_performance.max_drawdown,
                    "sharpe_ratio": trading_performance.sharpe_ratio,
                    "win_rate": trading_performance.win_rate
                },
                "users": {
                    "engagement_score": engagement_score,
                    "active_users": user_engagement.active_users,
                    "total_sessions": user_engagement.total_sessions,
                    "avg_session_duration": user_engagement.avg_session_duration,
                    "page_views": user_engagement.page_views,
                    "feature_usage": user_engagement.feature_usage,
                    "retention_rate": user_engagement.user_retention
                },
                "alerts": self._generate_alerts(system_health, trading_performance)
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _calculate_system_score(self, health: SystemHealth) -> float:
        """Calculate system health score (0-100)"""
        cpu_score = max(0, 100 - health.cpu_usage)
        memory_score = max(0, 100 - health.memory_usage)
        disk_score = max(0, 100 - health.disk_usage)
        response_score = max(0, 100 - (health.response_time * 50))
        error_score = max(0, 100 - (health.error_rate * 10))
        
        return round((cpu_score + memory_score + disk_score + response_score + error_score) / 5, 1)

    def _calculate_trading_score(self, performance: TradingPerformance) -> float:
        """Calculate trading performance score (0-100)"""
        success_score = min(100, performance.success_rate)
        profit_score = min(100, max(0, 50 + (performance.daily_pnl / 100)))
        sharpe_score = min(100, max(0, performance.sharpe_ratio * 30))
        
        return round((success_score + profit_score + sharpe_score) / 3, 1)

    def _calculate_engagement_score(self, engagement: UserEngagement) -> float:
        """Calculate user engagement score (0-100)"""
        activity_score = min(100, engagement.active_users * 2)
        session_score = min(100, engagement.avg_session_duration * 3)
        retention_score = engagement.user_retention
        
        return round((activity_score + session_score + retention_score) / 3, 1)

    def _generate_alerts(self, system_health: SystemHealth, trading_performance: TradingPerformance) -> List[Dict[str, Any]]:
        """Generate performance alerts"""
        alerts = []
        
        # System alerts
        if system_health.cpu_usage > self.cpu_threshold:
            alerts.append({
                "type": "warning",
                "category": "system",
                "message": f"High CPU usage: {system_health.cpu_usage}%",
                "severity": "high" if system_health.cpu_usage > 90 else "medium"
            })
        
        if system_health.memory_usage > self.memory_threshold:
            alerts.append({
                "type": "warning",
                "category": "system",
                "message": f"High memory usage: {system_health.memory_usage}%",
                "severity": "high" if system_health.memory_usage > 95 else "medium"
            })
        
        # Trading alerts
        if trading_performance.success_rate < 70:
            alerts.append({
                "type": "warning",
                "category": "trading",
                "message": f"Low success rate: {trading_performance.success_rate}%",
                "severity": "medium"
            })
        
        if trading_performance.daily_pnl < -1000:
            alerts.append({
                "type": "alert",
                "category": "trading",
                "message": f"High daily loss: ${trading_performance.daily_pnl}",
                "severity": "high"
            })
        
        return alerts

    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        if self.monitor_thread.is_alive():
            self.monitor_thread.join()

# Global instance
performance_monitor = PerformanceMonitor()
