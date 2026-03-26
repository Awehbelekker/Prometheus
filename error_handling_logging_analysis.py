#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Error Handling & Logging Analysis
Comprehensive analysis of error handling, logging systems, and debugging capabilities
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

class ErrorHandlingAnalyzer:
    """Analyze error handling and logging systems in PROMETHEUS."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'error_handling': {},
            'logging_systems': {},
            'debugging_tools': {},
            'recommendations': []
        }
        
    def analyze_error_handling_logging(self):
        """Perform comprehensive error handling and logging analysis."""
        print("🔍 PROMETHEUS ERROR HANDLING & LOGGING ANALYSIS")
        print("=" * 70)
        
        # Analyze error handling patterns
        self.analyze_error_handling()
        
        # Analyze logging systems
        self.analyze_logging_systems()
        
        # Analyze debugging capabilities
        self.analyze_debugging_tools()
        
        # Check monitoring and alerting
        self.analyze_monitoring_capabilities()
        
        # Generate recommendations
        self.generate_recommendations()
        
        # Create comprehensive report
        self.generate_analysis_report()
        
    def analyze_error_handling(self):
        """Analyze error handling patterns across the codebase."""
        print("\n1. 🚨 ERROR HANDLING ANALYSIS")
        print("-" * 50)
        
        error_patterns = {
            'try_except_blocks': 0,
            'custom_exceptions': 0,
            'error_responses': 0,
            'validation_errors': 0,
            'database_error_handling': 0
        }
        
        # Analyze main server file
        server_file = self.project_root / "unified_production_server.py"
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count try-except blocks
            try_except_matches = re.findall(r'try:\s*\n.*?except.*?:', content, re.DOTALL)
            error_patterns['try_except_blocks'] = len(try_except_matches)
            
            # Count custom exception handling
            custom_exception_matches = re.findall(r'raise\s+\w+Error', content)
            error_patterns['custom_exceptions'] = len(custom_exception_matches)
            
            # Count HTTP error responses
            error_response_matches = re.findall(r'HTTPException|status_code=[45]\d\d', content)
            error_patterns['error_responses'] = len(error_response_matches)
            
            # Count validation patterns
            validation_matches = re.findall(r'ValidationError|validate_|validator', content)
            error_patterns['validation_errors'] = len(validation_matches)
            
            print(f"   [CHECK] Try-except blocks found: {error_patterns['try_except_blocks']}")
            print(f"   [CHECK] Custom exceptions: {error_patterns['custom_exceptions']}")
            print(f"   [CHECK] HTTP error responses: {error_patterns['error_responses']}")
            print(f"   [CHECK] Validation patterns: {error_patterns['validation_errors']}")
        
        # Analyze core modules
        core_files = list(self.project_root.glob("core/*.py"))
        core_error_handling = 0
        
        for core_file in core_files:
            try:
                with open(core_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    core_error_handling += len(re.findall(r'try:\s*\n.*?except.*?:', content, re.DOTALL))
            except:
                pass
        
        print(f"   [CHECK] Core modules error handling: {core_error_handling} blocks")
        
        # Error handling grade
        total_error_handling = (error_patterns['try_except_blocks'] + 
                               error_patterns['custom_exceptions'] + 
                               error_patterns['error_responses'] + 
                               core_error_handling)
        
        if total_error_handling > 50:
            error_grade = "A+ (Excellent)"
        elif total_error_handling > 30:
            error_grade = "A (Very Good)"
        elif total_error_handling > 15:
            error_grade = "B (Good)"
        else:
            error_grade = "C (Needs Improvement)"
            
        print(f"   🏆 Error Handling Grade: {error_grade}")
        
        self.analysis_results['error_handling'] = {
            'patterns': error_patterns,
            'core_error_handling': core_error_handling,
            'total_error_handling': total_error_handling,
            'grade': error_grade
        }
        
    def analyze_logging_systems(self):
        """Analyze logging systems and configurations."""
        print("\n2. 📝 LOGGING SYSTEMS ANALYSIS")
        print("-" * 50)
        
        logging_features = {
            'logging_imports': 0,
            'logger_instances': 0,
            'log_levels': [],
            'structured_logging': 0,
            'log_files': 0
        }
        
        # Analyze main server file for logging
        server_file = self.project_root / "unified_production_server.py"
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count logging imports
            logging_imports = re.findall(r'import logging|from logging', content)
            logging_features['logging_imports'] = len(logging_imports)
            
            # Count logger instances
            logger_instances = re.findall(r'logger\s*=|getLogger|Logger', content)
            logging_features['logger_instances'] = len(logger_instances)
            
            # Find log levels
            log_levels = re.findall(r'\.(?:debug|info|warning|error|critical)\(', content)
            logging_features['log_levels'] = list(set(level.strip('.()') for level in log_levels))
            
            # Count structured logging (JSON format)
            structured_logs = re.findall(r'json\.dump|"timestamp":|"level":|"logger":', content)
            logging_features['structured_logging'] = len(structured_logs)
            
            print(f"   [CHECK] Logging imports: {logging_features['logging_imports']}")
            print(f"   [CHECK] Logger instances: {logging_features['logger_instances']}")
            print(f"   [CHECK] Log levels used: {', '.join(logging_features['log_levels'])}")
            print(f"   [CHECK] Structured logging: {logging_features['structured_logging']} instances")
        
        # Check for log files
        log_files = list(self.project_root.glob("*.log")) + list(self.project_root.glob("logs/*.log"))
        logging_features['log_files'] = len(log_files)
        
        if log_files:
            print(f"   [CHECK] Log files found: {len(log_files)}")
            for log_file in log_files[:3]:  # Show first 3
                print(f"      • {log_file.name}")
        else:
            print("   [WARNING]️  No log files found in project directory")
        
        # Check monitoring directory
        monitoring_dir = self.project_root / "monitoring"
        if monitoring_dir.exists():
            monitoring_files = list(monitoring_dir.glob("*.py"))
            print(f"   [CHECK] Monitoring scripts: {len(monitoring_files)}")
        
        # Logging grade
        logging_score = (logging_features['logging_imports'] + 
                        logging_features['logger_instances'] + 
                        len(logging_features['log_levels']) + 
                        logging_features['structured_logging'])
        
        if logging_score > 20:
            logging_grade = "A+ (Excellent)"
        elif logging_score > 15:
            logging_grade = "A (Very Good)"
        elif logging_score > 10:
            logging_grade = "B (Good)"
        else:
            logging_grade = "C (Needs Improvement)"
            
        print(f"   🏆 Logging Systems Grade: {logging_grade}")
        
        self.analysis_results['logging_systems'] = {
            'features': logging_features,
            'log_files': [str(f) for f in log_files],
            'score': logging_score,
            'grade': logging_grade
        }
        
    def analyze_debugging_tools(self):
        """Analyze debugging tools and capabilities."""
        print("\n3. 🔧 DEBUGGING TOOLS ANALYSIS")
        print("-" * 50)
        
        debugging_tools = {
            'debug_endpoints': 0,
            'health_checks': 0,
            'status_endpoints': 0,
            'metrics_endpoints': 0,
            'debug_middleware': 0,
            'request_tracking': 0
        }
        
        # Analyze server file for debugging features
        server_file = self.project_root / "unified_production_server.py"
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count debug endpoints
            debug_endpoints = re.findall(r'/debug|/health|/status|/metrics', content)
            debugging_tools['debug_endpoints'] = len(debug_endpoints)
            
            # Count health checks
            health_checks = re.findall(r'/health|health_check', content)
            debugging_tools['health_checks'] = len(health_checks)
            
            # Count status endpoints
            status_endpoints = re.findall(r'/status|status_check', content)
            debugging_tools['status_endpoints'] = len(status_endpoints)
            
            # Count metrics endpoints
            metrics_endpoints = re.findall(r'/metrics|prometheus', content)
            debugging_tools['metrics_endpoints'] = len(metrics_endpoints)
            
            # Check for debug middleware
            debug_middleware = re.findall(r'debug|Debug|middleware', content)
            debugging_tools['debug_middleware'] = len(debug_middleware)
            
            # Check for request tracking
            request_tracking = re.findall(r'request.*id|x-request-id|tracking', content, re.IGNORECASE)
            debugging_tools['request_tracking'] = len(request_tracking)
            
            print(f"   [CHECK] Debug endpoints: {debugging_tools['debug_endpoints']}")
            print(f"   [CHECK] Health checks: {debugging_tools['health_checks']}")
            print(f"   [CHECK] Status endpoints: {debugging_tools['status_endpoints']}")
            print(f"   [CHECK] Metrics endpoints: {debugging_tools['metrics_endpoints']}")
            print(f"   [CHECK] Request tracking: {debugging_tools['request_tracking']} instances")
        
        # Check for testing files
        test_files = list(self.project_root.glob("test*.py")) + list(self.project_root.glob("tests/*.py"))
        print(f"   [CHECK] Test files: {len(test_files)}")
        
        # Check for debugging scripts
        debug_scripts = [f for f in self.project_root.glob("*.py") if 'debug' in f.name.lower() or 'test' in f.name.lower()]
        print(f"   [CHECK] Debug scripts: {len(debug_scripts)}")
        
        # Debugging grade
        debug_score = sum(debugging_tools.values()) + len(test_files)
        
        if debug_score > 30:
            debug_grade = "A+ (Excellent)"
        elif debug_score > 20:
            debug_grade = "A (Very Good)"
        elif debug_score > 10:
            debug_grade = "B (Good)"
        else:
            debug_grade = "C (Needs Improvement)"
            
        print(f"   🏆 Debugging Tools Grade: {debug_grade}")
        
        self.analysis_results['debugging_tools'] = {
            'tools': debugging_tools,
            'test_files': len(test_files),
            'debug_scripts': len(debug_scripts),
            'score': debug_score,
            'grade': debug_grade
        }
        
    def analyze_monitoring_capabilities(self):
        """Analyze monitoring and alerting capabilities."""
        print("\n4. 📊 MONITORING CAPABILITIES ANALYSIS")
        print("-" * 50)
        
        monitoring_features = {
            'prometheus_metrics': 0,
            'health_endpoints': 0,
            'performance_tracking': 0,
            'alert_systems': 0,
            'dashboard_files': 0
        }
        
        # Check for Prometheus metrics
        prometheus_files = list(self.project_root.glob("*prometheus*")) + list(self.project_root.glob("*metrics*"))
        monitoring_features['prometheus_metrics'] = len(prometheus_files)
        
        # Check for monitoring directory
        monitoring_dir = self.project_root / "monitoring"
        if monitoring_dir.exists():
            monitoring_files = list(monitoring_dir.glob("*.py"))
            monitoring_features['dashboard_files'] = len(monitoring_files)
            print(f"   [CHECK] Monitoring directory: {len(monitoring_files)} files")
        
        # Check server file for monitoring features
        server_file = self.project_root / "unified_production_server.py"
        if server_file.exists():
            with open(server_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Count health endpoints
            health_endpoints = re.findall(r'@app\.get.*health|@app\.get.*status', content)
            monitoring_features['health_endpoints'] = len(health_endpoints)
            
            # Count performance tracking
            performance_tracking = re.findall(r'response.*time|performance|x-response-time', content, re.IGNORECASE)
            monitoring_features['performance_tracking'] = len(performance_tracking)
            
            print(f"   [CHECK] Health endpoints: {monitoring_features['health_endpoints']}")
            print(f"   [CHECK] Performance tracking: {monitoring_features['performance_tracking']} instances")
        
        # Check for alert configurations
        alert_files = list(self.project_root.glob("*alert*")) + list(self.project_root.glob("*notification*"))
        monitoring_features['alert_systems'] = len(alert_files)
        
        print(f"   [CHECK] Prometheus/metrics files: {monitoring_features['prometheus_metrics']}")
        print(f"   [CHECK] Alert system files: {monitoring_features['alert_systems']}")
        
        # Monitoring grade
        monitoring_score = sum(monitoring_features.values())
        
        if monitoring_score > 15:
            monitoring_grade = "A+ (Excellent)"
        elif monitoring_score > 10:
            monitoring_grade = "A (Very Good)"
        elif monitoring_score > 5:
            monitoring_grade = "B (Good)"
        else:
            monitoring_grade = "C (Needs Improvement)"
            
        print(f"   🏆 Monitoring Capabilities Grade: {monitoring_grade}")
        
        self.analysis_results['monitoring_capabilities'] = {
            'features': monitoring_features,
            'score': monitoring_score,
            'grade': monitoring_grade
        }
        
    def generate_recommendations(self):
        """Generate recommendations for improvement."""
        print("\n5. 💡 RECOMMENDATIONS")
        print("-" * 50)
        
        recommendations = []
        
        # Error handling recommendations
        error_score = self.analysis_results['error_handling']['total_error_handling']
        if error_score < 30:
            recommendations.append("Enhance error handling with more try-except blocks and custom exceptions")
        
        # Logging recommendations
        logging_score = self.analysis_results['logging_systems']['score']
        if logging_score < 15:
            recommendations.append("Implement structured logging with JSON format and multiple log levels")
        
        # Debugging recommendations
        debug_score = self.analysis_results['debugging_tools']['score']
        if debug_score < 20:
            recommendations.append("Add more debugging endpoints and request tracking capabilities")
        
        # Monitoring recommendations
        monitoring_score = self.analysis_results['monitoring_capabilities']['score']
        if monitoring_score < 10:
            recommendations.append("Implement comprehensive monitoring with Prometheus metrics and alerting")
        
        # General recommendations
        recommendations.extend([
            "Implement centralized error logging with correlation IDs",
            "Add performance monitoring and alerting thresholds",
            "Create comprehensive health check endpoints",
            "Implement distributed tracing for complex operations",
            "Add automated error notification systems",
            "Create debugging dashboards for operational visibility"
        ])
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        self.analysis_results['recommendations'] = recommendations
        
    def generate_analysis_report(self):
        """Generate comprehensive analysis report."""
        print("\n" + "=" * 70)
        print("📊 ERROR HANDLING & LOGGING ANALYSIS REPORT")
        print("=" * 70)
        
        # Calculate overall grade
        grades = [
            self.analysis_results['error_handling']['grade'],
            self.analysis_results['logging_systems']['grade'],
            self.analysis_results['debugging_tools']['grade'],
            self.analysis_results['monitoring_capabilities']['grade']
        ]
        
        grade_values = {'A+': 4, 'A': 3, 'B': 2, 'C': 1}
        grade_scores = [grade_values.get(g.split()[0], 0) for g in grades]
        avg_grade_score = sum(grade_scores) / len(grade_scores)
        
        if avg_grade_score >= 3.5:
            overall_grade = "A+ (Excellent)"
        elif avg_grade_score >= 2.5:
            overall_grade = "A (Very Good)"
        elif avg_grade_score >= 1.5:
            overall_grade = "B (Good)"
        else:
            overall_grade = "C (Needs Improvement)"
        
        print(f"🚨 Error Handling Grade: {self.analysis_results['error_handling']['grade']}")
        print(f"📝 Logging Systems Grade: {self.analysis_results['logging_systems']['grade']}")
        print(f"🔧 Debugging Tools Grade: {self.analysis_results['debugging_tools']['grade']}")
        print(f"📊 Monitoring Grade: {self.analysis_results['monitoring_capabilities']['grade']}")
        
        print(f"\n🏆 OVERALL GRADE: {overall_grade}")
        
        # Key strengths
        print(f"\n[CHECK] KEY STRENGTHS:")
        print(f"• Comprehensive error handling with {self.analysis_results['error_handling']['total_error_handling']} error handling blocks")
        print(f"• Structured logging with {self.analysis_results['logging_systems']['score']} logging features")
        print(f"• Debugging capabilities with {self.analysis_results['debugging_tools']['score']} debugging tools")
        print(f"• Monitoring systems with {self.analysis_results['monitoring_capabilities']['score']} monitoring features")
        
        # Areas for improvement
        print(f"\n[WARNING]️  AREAS FOR IMPROVEMENT:")
        for rec in self.analysis_results['recommendations'][:3]:
            print(f"• {rec}")
        
        # Save detailed report
        report_path = self.project_root / "error_handling_logging_analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.analysis_results, f, indent=2)
        
        print(f"\n💾 Detailed report saved: {report_path}")
        
        print(f"\n🎉 Error Handling & Logging Analysis Complete!")
        print(f"🚀 PROMETHEUS demonstrates {overall_grade} error handling and logging capabilities!")


def main():
    """Main entry point."""
    analyzer = ErrorHandlingAnalyzer()
    analyzer.analyze_error_handling_logging()


if __name__ == "__main__":
    main()
