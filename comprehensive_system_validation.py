#!/usr/bin/env python3
"""
🎯 PHASE 3C: COMPREHENSIVE SYSTEM VALIDATION & PERFORMANCE TESTING
Final validation of the complete PROMETHEUS Trading Platform
"""

import asyncio
import json
import time
import requests
import statistics
from datetime import datetime
from typing import Dict, List, Any
import concurrent.futures

class ComprehensiveSystemValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.performance_metrics = {}
        self.validation_score = 0
        
    def test_system_health(self):
        """Test overall system health and availability"""
        print("🏥 TESTING SYSTEM HEALTH")
        print("-" * 50)
        
        health_tests = []
        
        # Backend Health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                backend_health = {
                    "status": "healthy",
                    "uptime": health_data.get("uptime_seconds", 0),
                    "version": health_data.get("version", "unknown"),
                    "errors": health_data.get("errors_total", 0)
                }
                print(f"[CHECK] Backend Health: OK (Uptime: {backend_health['uptime']:.1f}s)")
                health_tests.append(True)
            else:
                backend_health = {"status": "unhealthy", "code": response.status_code}
                print(f"[ERROR] Backend Health: FAILED ({response.status_code})")
                health_tests.append(False)
        except Exception as e:
            backend_health = {"status": "error", "error": str(e)}
            print(f"[ERROR] Backend Health: ERROR - {e}")
            health_tests.append(False)
        
        # Feature Availability
        try:
            response = requests.get(f"{self.base_url}/api/features/availability", timeout=10)
            if response.status_code == 200:
                features = response.json()
                feature_health = {
                    "status": "available",
                    "features": features.get("features", {}),
                    "missing": features.get("missing", []),
                    "fallback": features.get("fallback", [])
                }
                active_features = sum(1 for v in features.get("features", {}).values() if v)
                total_features = len(features.get("features", {}))
                print(f"[CHECK] Features: {active_features}/{total_features} active")
                health_tests.append(True)
            else:
                feature_health = {"status": "unavailable", "code": response.status_code}
                print(f"[ERROR] Features: FAILED ({response.status_code})")
                health_tests.append(False)
        except Exception as e:
            feature_health = {"status": "error", "error": str(e)}
            print(f"[ERROR] Features: ERROR - {e}")
            health_tests.append(False)
        
        self.results['system_health'] = {
            "backend": backend_health,
            "features": feature_health,
            "overall_health": all(health_tests),
            "health_score": sum(health_tests) / len(health_tests) if health_tests else 0
        }
        
        return self.results['system_health']
    
    def test_api_performance(self):
        """Test API endpoint performance and response times"""
        print(f"\n[LIGHTNING] TESTING API PERFORMANCE")
        print("-" * 50)
        
        # Test endpoints with multiple requests
        endpoints = [
            {"name": "Health Check", "url": "/health", "method": "GET"},
            {"name": "Features", "url": "/api/features/availability", "method": "GET"},
            {"name": "Market Data", "url": "/api/market-data/AAPL", "method": "GET"},
            {"name": "AI Status", "url": "/api/ai/status", "method": "GET"}
        ]
        
        performance_results = {}
        
        for endpoint in endpoints:
            print(f"   Testing {endpoint['name']}...", end=" ")
            
            response_times = []
            success_count = 0
            
            # Run 5 requests per endpoint
            for i in range(5):
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.base_url}{endpoint['url']}", timeout=15)
                    end_time = time.time()
                    
                    response_time = (end_time - start_time) * 1000  # Convert to ms
                    response_times.append(response_time)
                    
                    if response.status_code == 200:
                        success_count += 1
                        
                except Exception as e:
                    response_times.append(15000)  # Timeout penalty
            
            # Calculate metrics
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            success_rate = success_count / 5
            
            performance_results[endpoint['name']] = {
                "avg_response_ms": round(avg_response_time, 2),
                "min_response_ms": round(min_response_time, 2),
                "max_response_ms": round(max_response_time, 2),
                "success_rate": success_rate,
                "status": "good" if avg_response_time < 5000 and success_rate > 0.8 else "poor"
            }
            
            status_icon = "[CHECK]" if performance_results[endpoint['name']]['status'] == 'good' else "[WARNING]️"
            print(f"{status_icon} {avg_response_time:.0f}ms avg ({success_rate:.0%} success)")
        
        # Overall API performance
        all_response_times = []
        all_success_rates = []
        
        for result in performance_results.values():
            all_response_times.append(result['avg_response_ms'])
            all_success_rates.append(result['success_rate'])
        
        overall_performance = {
            "avg_response_time_ms": round(statistics.mean(all_response_times), 2),
            "overall_success_rate": round(statistics.mean(all_success_rates), 3),
            "endpoints": performance_results
        }
        
        print(f"\n📊 Overall API Performance:")
        print(f"   • Average Response Time: {overall_performance['avg_response_time_ms']:.0f}ms")
        print(f"   • Overall Success Rate: {overall_performance['overall_success_rate']:.1%}")
        
        self.results['api_performance'] = overall_performance
        return overall_performance
    
    def test_enhanced_reasoning_performance(self):
        """Test enhanced reasoning system performance"""
        print(f"\n🧠 TESTING ENHANCED REASONING PERFORMANCE")
        print("-" * 50)
        
        # Import the reasoning adapter
        try:
            from core.reasoning.thinkmesh_adapter import ThinkMeshAdapter, ThinkMeshConfig, ReasoningStrategy
            
            adapter = ThinkMeshAdapter(enabled=True)
            
            # Test scenarios
            test_scenarios = [
                {
                    "name": "Quick Decision",
                    "prompt": "AAPL at $150, RSI 70, recommend action: BUY/SELL/HOLD",
                    "expected_time": 1.0
                },
                {
                    "name": "Risk Analysis", 
                    "prompt": "Portfolio: 80% stocks, 20% bonds, VIX at 25. Risk level: LOW/MEDIUM/HIGH",
                    "expected_time": 1.5
                },
                {
                    "name": "Complex Strategy",
                    "prompt": "Market conditions: Rising rates, high inflation, tech earnings mixed. Strategy recommendation for next quarter.",
                    "expected_time": 2.0
                }
            ]
            
            reasoning_results = []
            
            for scenario in test_scenarios:
                print(f"   Testing {scenario['name']}...", end=" ")
                
                config = ThinkMeshConfig(
                    strategy=ReasoningStrategy.SELF_CONSISTENCY,
                    parallel_paths=3,
                    wall_clock_timeout_s=10
                )
                
                try:
                    start_time = time.time()
                    
                    # Run the reasoning test
                    result = asyncio.run(adapter.reason(
                        prompt=scenario['prompt'],
                        config=config,
                        context={}
                    ))
                    
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    reasoning_results.append({
                        "scenario": scenario['name'],
                        "success": True,
                        "response_time": response_time,
                        "confidence": result.confidence,
                        "strategy_used": result.strategy_used,
                        "backend_used": result.backend_used
                    })
                    
                    print(f"[CHECK] {response_time:.2f}s ({result.confidence:.0%} confidence)")
                    
                except Exception as e:
                    reasoning_results.append({
                        "scenario": scenario['name'],
                        "success": False,
                        "error": str(e),
                        "response_time": 0
                    })
                    print(f"[ERROR] Failed: {e}")
            
            # Calculate reasoning performance metrics
            successful_tests = [r for r in reasoning_results if r.get('success', False)]
            
            if successful_tests:
                avg_response_time = statistics.mean([r['response_time'] for r in successful_tests])
                avg_confidence = statistics.mean([r['confidence'] for r in successful_tests])
                success_rate = len(successful_tests) / len(reasoning_results)
                
                reasoning_performance = {
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "avg_confidence": avg_confidence,
                    "tests": reasoning_results,
                    "status": "operational" if success_rate > 0.8 else "degraded"
                }
                
                print(f"\n📊 Enhanced Reasoning Performance:")
                print(f"   • Success Rate: {success_rate:.1%}")
                print(f"   • Average Response Time: {avg_response_time:.2f}s")
                print(f"   • Average Confidence: {avg_confidence:.1%}")
            else:
                reasoning_performance = {
                    "success_rate": 0,
                    "status": "failed",
                    "tests": reasoning_results
                }
                print(f"\n[ERROR] Enhanced Reasoning: All tests failed")
            
        except ImportError as e:
            reasoning_performance = {
                "status": "unavailable",
                "error": f"Import error: {e}"
            }
            print(f"[ERROR] Enhanced Reasoning: Import failed - {e}")
        
        self.results['reasoning_performance'] = reasoning_performance
        return reasoning_performance
    
    def test_trading_system_integration(self):
        """Test trading system integration and functionality"""
        print(f"\n💰 TESTING TRADING SYSTEM INTEGRATION")
        print("-" * 50)
        
        trading_tests = []
        
        # Test market data endpoints
        market_symbols = ["AAPL", "MSFT", "GOOGL"]
        market_data_results = []
        
        for symbol in market_symbols:
            try:
                response = requests.get(f"{self.base_url}/api/market-data/{symbol}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    market_data_results.append({
                        "symbol": symbol,
                        "success": True,
                        "has_price": "price" in str(data).lower(),
                        "data_age": "recent"  # Simplified check
                    })
                    print(f"[CHECK] Market Data - {symbol}: OK")
                    trading_tests.append(True)
                else:
                    market_data_results.append({
                        "symbol": symbol,
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
                    print(f"[ERROR] Market Data - {symbol}: FAILED")
                    trading_tests.append(False)
            except Exception as e:
                market_data_results.append({
                    "symbol": symbol,
                    "success": False,
                    "error": str(e)
                })
                print(f"[ERROR] Market Data - {symbol}: ERROR")
                trading_tests.append(False)
        
        # Test paper trading functionality
        try:
            response = requests.get(f"{self.base_url}/api/paper-trading/portfolio", timeout=10)
            if response.status_code == 200:
                portfolio_data = response.json()
                paper_trading_status = {
                    "available": True,
                    "portfolio_accessible": True,
                    "data": portfolio_data
                }
                print(f"[CHECK] Paper Trading: Portfolio accessible")
                trading_tests.append(True)
            else:
                paper_trading_status = {
                    "available": False,
                    "error": f"HTTP {response.status_code}"
                }
                print(f"[WARNING]️ Paper Trading: Limited access ({response.status_code})")
                trading_tests.append(False)
        except Exception as e:
            paper_trading_status = {
                "available": False,
                "error": str(e)
            }
            print(f"[ERROR] Paper Trading: ERROR - {e}")
            trading_tests.append(False)
        
        trading_integration = {
            "market_data": market_data_results,
            "paper_trading": paper_trading_status,
            "overall_status": "operational" if sum(trading_tests) >= len(trading_tests) * 0.7 else "degraded",
            "success_rate": sum(trading_tests) / len(trading_tests) if trading_tests else 0
        }
        
        print(f"\n📊 Trading System Integration:")
        print(f"   • Success Rate: {trading_integration['success_rate']:.1%}")
        print(f"   • Status: {trading_integration['overall_status'].upper()}")
        
        self.results['trading_integration'] = trading_integration
        return trading_integration
    
    def calculate_overall_validation_score(self):
        """Calculate overall system validation score"""
        print(f"\n🎯 CALCULATING OVERALL VALIDATION SCORE")
        print("-" * 50)
        
        # Weight different components
        weights = {
            "system_health": 0.25,
            "api_performance": 0.25, 
            "reasoning_performance": 0.30,
            "trading_integration": 0.20
        }
        
        scores = {}
        
        # System Health Score
        health = self.results.get('system_health', {})
        scores['system_health'] = health.get('health_score', 0) * 100
        
        # API Performance Score
        api_perf = self.results.get('api_performance', {})
        api_success_rate = api_perf.get('overall_success_rate', 0)
        api_response_time = api_perf.get('avg_response_time_ms', 10000)
        # Score based on success rate and response time (good if < 5000ms)
        api_time_score = max(0, (5000 - api_response_time) / 5000) if api_response_time > 0 else 0
        scores['api_performance'] = (api_success_rate * 0.7 + api_time_score * 0.3) * 100
        
        # Reasoning Performance Score
        reasoning = self.results.get('reasoning_performance', {})
        reasoning_success = reasoning.get('success_rate', 0)
        reasoning_confidence = reasoning.get('avg_confidence', 0)
        scores['reasoning_performance'] = (reasoning_success * 0.6 + reasoning_confidence * 0.4) * 100
        
        # Trading Integration Score
        trading = self.results.get('trading_integration', {})
        scores['trading_integration'] = trading.get('success_rate', 0) * 100
        
        # Calculate weighted overall score
        overall_score = sum(scores[component] * weights[component] for component in weights.keys())
        
        print(f"📊 Component Scores:")
        for component, score in scores.items():
            print(f"   • {component.replace('_', ' ').title()}: {score:.1f}/100")
        
        print(f"\n🎯 Overall Validation Score: {overall_score:.1f}/100")
        
        # Determine grade
        if overall_score >= 90:
            grade = "EXCELLENT"
            status = "🟢"
        elif overall_score >= 80:
            grade = "GOOD"
            status = "🟡"
        elif overall_score >= 70:
            grade = "ACCEPTABLE"
            status = "🟠"
        else:
            grade = "NEEDS IMPROVEMENT"
            status = "🔴"
        
        print(f"{status} System Grade: {grade}")
        
        self.validation_score = overall_score
        self.results['validation_summary'] = {
            "overall_score": overall_score,
            "grade": grade,
            "component_scores": scores,
            "weights": weights
        }
        
        return overall_score, grade
    
    def generate_comprehensive_report(self):
        """Generate comprehensive validation report"""
        report = {
            "validation_date": datetime.now().isoformat(),
            "validation_type": "Comprehensive System Validation",
            "system_info": {
                "platform": "PROMETHEUS Trading Platform",
                "version": "2.0.0",
                "validation_phase": "3C"
            },
            "results": self.results,
            "validation_score": self.validation_score,
            "recommendations": self._generate_recommendations()
        }
        
        # Save report
        with open("comprehensive_system_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on validation results"""
        recommendations = []
        
        # System health recommendations
        health = self.results.get('system_health', {})
        if health.get('health_score', 0) < 0.9:
            recommendations.append({
                "priority": "HIGH",
                "category": "System Health",
                "issue": "System health below optimal",
                "recommendation": "Monitor backend stability and address any recurring errors"
            })
        
        # API performance recommendations
        api_perf = self.results.get('api_performance', {})
        if api_perf.get('avg_response_time_ms', 0) > 3000:
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Performance",
                "issue": "API response times above 3 seconds",
                "recommendation": "Consider API optimization or caching improvements"
            })
        
        # Enhanced reasoning recommendations
        reasoning = self.results.get('reasoning_performance', {})
        if reasoning.get('success_rate', 0) == 1.0:
            recommendations.append({
                "priority": "LOW",
                "category": "AI Enhancement",
                "issue": "Enhanced reasoning performing excellently",
                "recommendation": "Current fallback system is optimal - continue using"
            })
        
        return recommendations

async def main():
    print("🎯 PHASE 3C: COMPREHENSIVE SYSTEM VALIDATION")
    print("=" * 60)
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    validator = ComprehensiveSystemValidator()
    
    # Step 1: System Health
    validator.test_system_health()
    
    # Step 2: API Performance
    validator.test_api_performance()
    
    # Step 3: Enhanced Reasoning
    validator.test_enhanced_reasoning_performance()
    
    # Step 4: Trading Integration
    validator.test_trading_system_integration()
    
    # Step 5: Overall Score
    score, grade = validator.calculate_overall_validation_score()
    
    # Step 6: Generate Report
    report = validator.generate_comprehensive_report()
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 COMPREHENSIVE SYSTEM VALIDATION COMPLETE")
    print("=" * 60)
    print(f"🎯 Overall Score: {score:.1f}/100 ({grade})")
    print(f"📄 Report saved to: comprehensive_system_validation_report.json")
    print(f"🕐 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
