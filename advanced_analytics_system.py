#!/usr/bin/env python3
"""
📊 PROMETHEUS Advanced Analytics & Performance Monitoring System
💎 Real-time trading performance analysis and optimization
[LIGHTNING] Enterprise-grade observability and insights
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import sqlite3
import statistics
from dataclasses import dataclass, asdict
from enum import Enum

class MetricType(Enum):
    TRADING_PERFORMANCE = "trading_performance"
    AI_PERFORMANCE = "ai_performance"
    SYSTEM_HEALTH = "system_health"
    RISK_METRICS = "risk_metrics"
    PROFITABILITY = "profitability"

@dataclass
class PerformanceMetric:
    """Individual performance metric"""
    timestamp: datetime
    metric_type: MetricType
    name: str
    value: float
    unit: str
    context: Dict[str, Any]

@dataclass
class TradingAnalytics:
    """Comprehensive trading analytics"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_trade_duration: float
    roi_percentage: float
    risk_adjusted_return: float

@dataclass
class AIPerformanceMetrics:
    """AI system performance metrics"""
    model_name: str
    avg_response_time: float
    total_requests: int
    successful_requests: int
    error_rate: float
    accuracy_score: float
    confidence_score: float
    decision_quality: float

class AdvancedAnalyticsSystem:
    """Advanced analytics and monitoring system"""
    
    def __init__(self, db_path: str = "analytics.db"):
        self.db_path = db_path
        self.metrics_buffer: List[PerformanceMetric] = []
        self.analytics_cache: Dict[str, Any] = {}
        self.monitoring_active = False
        self._initialize_database()
        
    def _initialize_database(self):
        """Initialize analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                context TEXT NOT NULL
            )
        """)
        
        # Trading sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_sessions (
                session_id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0.0,
                max_drawdown REAL DEFAULT 0.0,
                sharpe_ratio REAL DEFAULT 0.0,
                win_rate REAL DEFAULT 0.0,
                avg_trade_duration REAL DEFAULT 0.0,
                roi_percentage REAL DEFAULT 0.0,
                risk_adjusted_return REAL DEFAULT 0.0
            )
        """)
        
        # AI performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                model_name TEXT NOT NULL,
                avg_response_time REAL NOT NULL,
                total_requests INTEGER NOT NULL,
                successful_requests INTEGER NOT NULL,
                error_rate REAL NOT NULL,
                accuracy_score REAL NOT NULL,
                confidence_score REAL NOT NULL,
                decision_quality REAL NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()

    async def record_metric(self, metric: PerformanceMetric):
        """Record a performance metric"""
        self.metrics_buffer.append(metric)
        
        # Flush buffer if it gets too large
        if len(self.metrics_buffer) >= 100:
            await self.flush_metrics()

    async def flush_metrics(self):
        """Flush metrics buffer to database"""
        if not self.metrics_buffer:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for metric in self.metrics_buffer:
            cursor.execute("""
                INSERT INTO performance_metrics 
                (timestamp, metric_type, name, value, unit, context)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.timestamp.isoformat(),
                metric.metric_type.value,
                metric.name,
                metric.value,
                metric.unit,
                json.dumps(metric.context)
            ))
        
        conn.commit()
        conn.close()
        
        self.metrics_buffer.clear()

    async def analyze_trading_performance(self, session_id: str) -> TradingAnalytics:
        """Analyze trading performance for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get session data
        cursor.execute("""
            SELECT * FROM trading_sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            # Create default analytics
            return TradingAnalytics(
                session_id=session_id,
                start_time=datetime.now(),
                end_time=None,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                total_pnl=0.0,
                max_drawdown=0.0,
                sharpe_ratio=0.0,
                win_rate=0.0,
                avg_trade_duration=0.0,
                roi_percentage=0.0,
                risk_adjusted_return=0.0
            )
        
        # Convert row to TradingAnalytics
        analytics = TradingAnalytics(
            session_id=row[0],
            start_time=datetime.fromisoformat(row[1]),
            end_time=datetime.fromisoformat(row[2]) if row[2] else None,
            total_trades=row[3],
            winning_trades=row[4],
            losing_trades=row[5],
            total_pnl=row[6],
            max_drawdown=row[7],
            sharpe_ratio=row[8],
            win_rate=row[9],
            avg_trade_duration=row[10],
            roi_percentage=row[11],
            risk_adjusted_return=row[12]
        )
        
        conn.close()
        return analytics

    async def analyze_ai_performance(self, model_name: str, hours: int = 24) -> AIPerformanceMetrics:
        """Analyze AI performance over specified time period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT * FROM ai_performance 
            WHERE model_name = ? AND timestamp > ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (model_name, since_time.isoformat()))
        
        row = cursor.fetchone()
        if not row:
            # Create default metrics
            return AIPerformanceMetrics(
                model_name=model_name,
                avg_response_time=0.0,
                total_requests=0,
                successful_requests=0,
                error_rate=0.0,
                accuracy_score=0.0,
                confidence_score=0.0,
                decision_quality=0.0
            )
        
        metrics = AIPerformanceMetrics(
            model_name=row[2],
            avg_response_time=row[3],
            total_requests=row[4],
            successful_requests=row[5],
            error_rate=row[6],
            accuracy_score=row[7],
            confidence_score=row[8],
            decision_quality=row[9]
        )
        
        conn.close()
        return metrics

    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "report_type": "comprehensive_performance",
            "trading_analytics": {},
            "ai_performance": {},
            "system_health": {},
            "recommendations": []
        }
        
        # Get recent trading sessions
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT session_id FROM trading_sessions 
            ORDER BY start_time DESC LIMIT 5
        """)
        
        recent_sessions = [row[0] for row in cursor.fetchall()]
        
        # Analyze each session
        for session_id in recent_sessions:
            analytics = await self.analyze_trading_performance(session_id)
            report["trading_analytics"][session_id] = asdict(analytics)
        
        # Analyze AI performance
        for model_name in ["gpt-oss-20b", "gpt-oss-120b"]:
            ai_metrics = await self.analyze_ai_performance(model_name)
            report["ai_performance"][model_name] = asdict(ai_metrics)
        
        # System health metrics
        report["system_health"] = await self.get_system_health_metrics()
        
        # Generate recommendations
        report["recommendations"] = await self.generate_recommendations(report)
        
        conn.close()
        return report

    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        return {
            "uptime_hours": 24.5,  # Mock data
            "memory_usage_percent": 45.2,
            "cpu_usage_percent": 23.1,
            "disk_usage_percent": 67.8,
            "active_connections": 12,
            "error_rate_percent": 0.1,
            "response_time_avg_ms": 169.2,
            "throughput_requests_per_second": 15.3
        }

    async def generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        # Analyze AI performance
        for model_name, metrics in report["ai_performance"].items():
            if metrics["error_rate"] > 0.05:  # 5% error rate threshold
                recommendations.append(f"🔧 {model_name}: Error rate is {metrics['error_rate']:.1%}, consider model optimization")
            
            if metrics["avg_response_time"] > 500:  # 500ms threshold
                recommendations.append(f"[LIGHTNING] {model_name}: Response time is {metrics['avg_response_time']:.0f}ms, consider performance tuning")
        
        # Analyze trading performance
        for session_id, analytics in report["trading_analytics"].items():
            if analytics["win_rate"] < 0.6:  # 60% win rate threshold
                recommendations.append(f"📈 Session {session_id}: Win rate is {analytics['win_rate']:.1%}, review trading strategies")
            
            if analytics["sharpe_ratio"] < 1.0:  # Sharpe ratio threshold
                recommendations.append(f"📊 Session {session_id}: Sharpe ratio is {analytics['sharpe_ratio']:.2f}, optimize risk-adjusted returns")
        
        # System health recommendations
        health = report["system_health"]
        if health["memory_usage_percent"] > 80:
            recommendations.append("💾 Memory usage is high, consider system optimization")
        
        if health["error_rate_percent"] > 1.0:
            recommendations.append("🚨 System error rate is elevated, investigate error logs")
        
        if not recommendations:
            recommendations.append("[CHECK] All systems performing optimally!")
        
        return recommendations

    async def start_real_time_monitoring(self):
        """Start real-time performance monitoring"""
        self.monitoring_active = True
        
        print("📊 Starting real-time performance monitoring...")
        
        while self.monitoring_active:
            try:
                # Collect current metrics
                await self.collect_current_metrics()
                
                # Wait 30 seconds before next collection
                await asyncio.sleep(30)
                
            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def collect_current_metrics(self):
        """Collect current system metrics"""
        timestamp = datetime.now()
        
        # AI performance metrics
        ai_metric = PerformanceMetric(
            timestamp=timestamp,
            metric_type=MetricType.AI_PERFORMANCE,
            name="response_time",
            value=169.2,  # Mock current response time
            unit="ms",
            context={"model": "gpt-oss-20b", "requests_per_minute": 15}
        )
        await self.record_metric(ai_metric)
        
        # System health metrics
        health_metric = PerformanceMetric(
            timestamp=timestamp,
            metric_type=MetricType.SYSTEM_HEALTH,
            name="memory_usage",
            value=45.2,
            unit="percent",
            context={"total_memory_gb": 32, "available_memory_gb": 17.5}
        )
        await self.record_metric(health_metric)
        
        # Trading performance metrics (if active session)
        trading_metric = PerformanceMetric(
            timestamp=timestamp,
            metric_type=MetricType.TRADING_PERFORMANCE,
            name="current_pnl",
            value=1250.75,  # Mock current P&L
            unit="usd",
            context={"session_id": "live_session_001", "trades_today": 8}
        )
        await self.record_metric(trading_metric)

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.monitoring_active = False
        print("📊 Real-time monitoring stopped")

    async def export_analytics_data(self, format: str = "json") -> str:
        """Export analytics data"""
        report = await self.generate_performance_report()
        
        if format.lower() == "json":
            filename = f"prometheus_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            return filename
        else:
            raise ValueError(f"Unsupported export format: {format}")

async def main():
    """Main analytics demonstration"""
    print("📊 PROMETHEUS Advanced Analytics System")
    print("=" * 50)
    
    analytics = AdvancedAnalyticsSystem()
    
    # Generate sample report
    print("📈 Generating performance report...")
    report = await analytics.generate_performance_report()
    
    print(f"\n📊 PERFORMANCE REPORT SUMMARY:")
    print(f"   Generated: {report['generated_at']}")
    print(f"   Trading Sessions: {len(report['trading_analytics'])}")
    print(f"   AI Models Analyzed: {len(report['ai_performance'])}")
    print(f"   Recommendations: {len(report['recommendations'])}")
    
    print(f"\n🤖 AI PERFORMANCE:")
    for model, metrics in report['ai_performance'].items():
        print(f"   {model}:")
        print(f"     Response Time: {metrics['avg_response_time']:.1f}ms")
        print(f"     Success Rate: {(1-metrics['error_rate'])*100:.1f}%")
        print(f"     Decision Quality: {metrics['decision_quality']:.1f}/10")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    # Export report
    filename = await analytics.export_analytics_data()
    print(f"\n📁 Report exported: {filename}")
    
    print(f"\n[CHECK] Advanced Analytics System operational!")

if __name__ == "__main__":
    asyncio.run(main())
