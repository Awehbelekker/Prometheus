#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Performance Analysis
"""
import time
import sqlite3
import requests
import psutil
import logging
from datetime import datetime
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
    
    def analyze_system_resources(self) -> Dict[str, Any]:
        """Analyze system resource utilization"""
        logger.info("Analyzing system resources...")
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('C:')
        
        return {
            "cpu_usage_percent": cpu_percent,
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "memory_used_gb": round(memory.used / (1024**3), 2),
            "memory_percent": memory.percent,
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_percent": round((disk.used / disk.total) * 100, 2)
        }
    
    def analyze_api_performance(self) -> Dict[str, Any]:
        """Analyze API endpoint performance"""
        logger.info("Analyzing API performance...")
        
        endpoints = [
            "/health",
            "/api/market-data/AAPL",
            "/api/features/availability",
            "/api/paper-trading/market-data"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            times = []
            errors = 0
            
            # Test each endpoint 5 times
            for i in range(5):
                try:
                    start_time = time.time()
                    
                    if endpoint.startswith("/api/paper-trading"):
                        response = requests.get(f"http://localhost:8002{endpoint}", timeout=10)
                    else:
                        response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    
                    if response.status_code == 200:
                        times.append(response_time)
                    else:
                        errors += 1
                        
                except Exception as e:
                    errors += 1
                    logger.warning(f"Error testing {endpoint}: {e}")
            
            if times:
                results[endpoint] = {
                    "avg_response_time_ms": round(sum(times) / len(times), 2),
                    "min_response_time_ms": round(min(times), 2),
                    "max_response_time_ms": round(max(times), 2),
                    "success_rate": round((len(times) / 5) * 100, 2),
                    "errors": errors
                }
            else:
                results[endpoint] = {
                    "avg_response_time_ms": 0,
                    "min_response_time_ms": 0,
                    "max_response_time_ms": 0,
                    "success_rate": 0,
                    "errors": errors
                }
        
        return results
    
    def analyze_database_performance(self) -> Dict[str, Any]:
        """Analyze database query performance"""
        logger.info("Analyzing database performance...")
        
        databases = [
            'prometheus_trading.db',
            'enhanced_paper_trading.db',
            'gamification.db'
        ]
        
        results = {}
        
        for db_name in databases:
            try:
                start_time = time.time()
                
                with sqlite3.connect(db_name) as conn:
                    cursor = conn.cursor()
                    
                    # Test basic query performance
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    
                    # Test a more complex query if tables exist
                    if tables:
                        table_name = tables[0][0]
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                    else:
                        count = 0
                
                end_time = time.time()
                query_time = (end_time - start_time) * 1000
                
                results[db_name] = {
                    "connection_time_ms": round(query_time, 2),
                    "tables_count": len(tables),
                    "sample_table_rows": count,
                    "status": "healthy"
                }
                
            except Exception as e:
                results[db_name] = {
                    "connection_time_ms": 0,
                    "tables_count": 0,
                    "sample_table_rows": 0,
                    "status": f"error: {str(e)}"
                }
        
        return results
    
    def identify_bottlenecks(self) -> List[Dict[str, Any]]:
        """Identify system bottlenecks"""
        logger.info("Identifying bottlenecks...")
        
        bottlenecks = []
        
        # Check API response times
        api_results = self.results.get('api_performance', {})
        for endpoint, metrics in api_results.items():
            if metrics['avg_response_time_ms'] > 1000:  # > 1 second
                bottlenecks.append({
                    "type": "API Performance",
                    "component": endpoint,
                    "issue": f"Slow response time: {metrics['avg_response_time_ms']}ms",
                    "severity": "high" if metrics['avg_response_time_ms'] > 3000 else "medium",
                    "recommendation": "Optimize endpoint or add caching"
                })
        
        # Check system resources
        system_resources = self.results.get('system_resources', {})
        if system_resources.get('cpu_usage_percent', 0) > 80:
            bottlenecks.append({
                "type": "System Resources",
                "component": "CPU",
                "issue": f"High CPU usage: {system_resources['cpu_usage_percent']}%",
                "severity": "high",
                "recommendation": "Optimize CPU-intensive operations"
            })
        
        if system_resources.get('memory_percent', 0) > 85:
            bottlenecks.append({
                "type": "System Resources", 
                "component": "Memory",
                "issue": f"High memory usage: {system_resources['memory_percent']}%",
                "severity": "high",
                "recommendation": "Optimize memory usage or increase RAM"
            })
        
        return bottlenecks
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run comprehensive performance analysis"""
        logger.info("Starting comprehensive performance analysis...")
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_resources": self.analyze_system_resources(),
            "api_performance": self.analyze_api_performance(),
            "database_performance": self.analyze_database_performance()
        }
        
        self.results["bottlenecks"] = self.identify_bottlenecks()
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate performance analysis report"""
        if not self.results:
            self.run_comprehensive_analysis()
        
        report = []
        report.append("PROMETHEUS TRADING PLATFORM - PERFORMANCE ANALYSIS REPORT")
        report.append("=" * 70)
        report.append(f"Analysis Date: {self.results['timestamp']}")
        report.append("")
        
        # System Resources
        report.append("SYSTEM RESOURCES:")
        report.append("-" * 30)
        resources = self.results['system_resources']
        report.append(f"CPU Usage: {resources['cpu_usage_percent']}%")
        report.append(f"Memory: {resources['memory_used_gb']}GB / {resources['memory_total_gb']}GB ({resources['memory_percent']}%)")
        report.append(f"Disk: {resources['disk_used_gb']}GB / {resources['disk_total_gb']}GB ({resources['disk_percent']}%)")
        report.append("")
        
        # API Performance
        report.append("API PERFORMANCE:")
        report.append("-" * 30)
        for endpoint, metrics in self.results['api_performance'].items():
            status = "GOOD" if metrics['avg_response_time_ms'] < 1000 else "SLOW"
            report.append(f"{endpoint}: {metrics['avg_response_time_ms']}ms avg ({status})")
        report.append("")
        
        # Database Performance
        report.append("DATABASE PERFORMANCE:")
        report.append("-" * 30)
        for db, metrics in self.results['database_performance'].items():
            report.append(f"{db}: {metrics['connection_time_ms']}ms, {metrics['tables_count']} tables ({metrics['status']})")
        report.append("")
        
        # Bottlenecks
        report.append("IDENTIFIED BOTTLENECKS:")
        report.append("-" * 30)
        bottlenecks = self.results['bottlenecks']
        if bottlenecks:
            for bottleneck in bottlenecks:
                report.append(f"[{bottleneck['severity'].upper()}] {bottleneck['component']}: {bottleneck['issue']}")
                report.append(f"  Recommendation: {bottleneck['recommendation']}")
        else:
            report.append("No significant bottlenecks identified")
        
        return "\n".join(report)

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    report = analyzer.generate_report()
    
    print(report)
    
    # Save results
    with open("performance_analysis_results.json", "w") as f:
        import json
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: performance_analysis_results.json")
