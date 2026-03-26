#!/usr/bin/env python3
"""
COMPREHENSIVE AI CAPABILITIES BENCHMARK
Test all AI systems, intelligence, and trading capabilities
"""

import requests
import time
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Any
import statistics

class AIBenchmarkSuite:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ai_url = "http://localhost:5000"
        self.results = {}
        self.start_time = None
        
    def log(self, message: str):
        """Log with timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] {message}")
    
    async def test_server_health(self):
        """Test all server health endpoints"""
        self.log("TESTING SERVER HEALTH")
        print("=" * 60)
        
        servers = [
            ("Main Server", f"{self.base_url}/health"),
            ("AI Server", f"{self.ai_url}/health"),
            ("Revolutionary Server", "http://localhost:8002/health")
        ]
        
        health_results = {}
        
        for name, url in servers:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as response:
                        response_time = time.time() - start_time
                        if response.status == 200:
                            data = await response.json()
                            health_results[name] = {
                                "status": "healthy",
                                "response_time": response_time,
                                "data": data
                            }
                            self.log(f"[CHECK] {name}: {response_time:.3f}s")
                        else:
                            health_results[name] = {
                                "status": "unhealthy",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {name}: HTTP {response.status}")
            except Exception as e:
                health_results[name] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {name}: {str(e)}")
        
        self.results["server_health"] = health_results
        return health_results
    
    async def test_ai_capabilities(self):
        """Test AI generation capabilities"""
        self.log("TESTING AI CAPABILITIES")
        print("=" * 60)
        
        test_prompts = [
            {
                "name": "Trading Analysis",
                "prompt": "Analyze AAPL stock for trading decision with technical indicators",
                "expected_features": ["technical", "analysis", "trading", "indicators"]
            },
            {
                "name": "Market Sentiment",
                "prompt": "What is the current market sentiment for technology stocks?",
                "expected_features": ["sentiment", "market", "technology", "analysis"]
            },
            {
                "name": "Risk Assessment",
                "prompt": "Assess the risk of investing in cryptocurrency right now",
                "expected_features": ["risk", "cryptocurrency", "assessment", "investment"]
            },
            {
                "name": "Portfolio Optimization",
                "prompt": "How should I optimize my portfolio for maximum returns with minimal risk?",
                "expected_features": ["portfolio", "optimization", "returns", "risk"]
            },
            {
                "name": "Pattern Recognition",
                "prompt": "Identify chart patterns in TSLA stock and predict price movement",
                "expected_features": ["pattern", "chart", "prediction", "price"]
            }
        ]
        
        ai_results = {}
        
        for test in test_prompts:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.ai_url}/generate",
                        json={
                            "prompt": test["prompt"],
                            "max_tokens": 300,
                            "temperature": 0.7
                        },
                        timeout=30
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            response_text = data.get("generated_text", "")
                            
                            # Analyze response quality
                            quality_score = self._analyze_response_quality(
                                response_text, 
                                test["expected_features"]
                            )
                            
                            ai_results[test["name"]] = {
                                "status": "success",
                                "response_time": response_time,
                                "quality_score": quality_score,
                                "ai_mode": data.get("ai_mode", "unknown"),
                                "real_ai": data.get("real_ai", False),
                                "capabilities": data.get("capabilities", []),
                                "response_length": len(response_text),
                                "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                            }
                            
                            self.log(f"[CHECK] {test['name']}: {response_time:.3f}s, Quality: {quality_score:.1f}/10")
                        else:
                            ai_results[test["name"]] = {
                                "status": "error",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {test['name']}: HTTP {response.status}")
            except Exception as e:
                ai_results[test["name"]] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {test['name']}: {str(e)}")
        
        self.results["ai_capabilities"] = ai_results
        return ai_results
    
    def _analyze_response_quality(self, response: str, expected_features: List[str]) -> float:
        """Analyze the quality of AI response"""
        score = 0.0
        
        # Check for expected features
        response_lower = response.lower()
        feature_count = sum(1 for feature in expected_features if feature in response_lower)
        score += (feature_count / len(expected_features)) * 4.0  # 4 points for features
        
        # Check response length (not too short, not too long)
        if 100 <= len(response) <= 1000:
            score += 2.0  # 2 points for appropriate length
        elif 50 <= len(response) < 100:
            score += 1.0  # 1 point for short but acceptable
        
        # Check for structured content (headers, lists, etc.)
        if any(marker in response for marker in ["-", "•", "1.", "2.", "3.", "MARKET", "TECHNICAL", "RISK"]):
            score += 2.0  # 2 points for structure
        
        # Check for specific trading terms
        trading_terms = ["buy", "sell", "hold", "price", "market", "analysis", "risk", "return"]
        term_count = sum(1 for term in trading_terms if term in response_lower)
        score += (term_count / len(trading_terms)) * 2.0  # 2 points for trading relevance
        
        return min(score, 10.0)  # Cap at 10
    
    async def test_ai_agents(self):
        """Test all AI agents"""
        self.log("TESTING AI AGENTS")
        print("=" * 60)
        
        agents = [
            "synergycore", "cogniflow", "edgemind", 
            "neuralmesh", "codeswarm"
        ]
        
        agent_results = {}
        
        for agent in agents:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}/api/ai/agents/{agent}/status",
                        timeout=5
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            agent_results[agent] = {
                                "status": "active",
                                "response_time": response_time,
                                "data": data
                            }
                            self.log(f"[CHECK] {agent.title()}: {response_time:.3f}s")
                        else:
                            agent_results[agent] = {
                                "status": "error",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {agent.title()}: HTTP {response.status}")
            except Exception as e:
                agent_results[agent] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {agent.title()}: {str(e)}")
        
        self.results["ai_agents"] = agent_results
        return agent_results
    
    async def test_revolutionary_systems(self):
        """Test revolutionary AI systems"""
        self.log("TESTING REVOLUTIONARY SYSTEMS")
        print("=" * 60)
        
        systems = [
            ("AI Coordinator", "/api/ai/coordinator/status"),
            ("Quantum Engine", "/api/quantum/status"),
            ("Think Mesh", "/api/think-mesh/status"),
            ("Market Oracle", "/api/market-oracle/status"),
            ("AI Consciousness", "/api/ai/consciousness/status")
        ]
        
        system_results = {}
        
        for name, endpoint in systems:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=5
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            system_results[name] = {
                                "status": "operational",
                                "response_time": response_time,
                                "data": data
                            }
                            self.log(f"[CHECK] {name}: {response_time:.3f}s")
                        else:
                            system_results[name] = {
                                "status": "error",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {name}: HTTP {response.status}")
            except Exception as e:
                system_results[name] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {name}: {str(e)}")
        
        self.results["revolutionary_systems"] = system_results
        return system_results
    
    async def test_learning_systems(self):
        """Test AI learning systems"""
        self.log("TESTING LEARNING SYSTEMS")
        print("=" * 60)
        
        learning_systems = [
            ("Continuous Learning", "/api/learning/continuous-learning/status"),
            ("Advanced Learning", "/api/learning/advanced-learning/status"),
            ("Autonomous Improvement", "/api/learning/autonomous-improvement/status")
        ]
        
        learning_results = {}
        
        for name, endpoint in learning_systems:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=5
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            learning_results[name] = {
                                "status": "active",
                                "response_time": response_time,
                                "data": data
                            }
                            self.log(f"[CHECK] {name}: {response_time:.3f}s")
                        else:
                            learning_results[name] = {
                                "status": "error",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {name}: HTTP {response.status}")
            except Exception as e:
                learning_results[name] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {name}: {str(e)}")
        
        self.results["learning_systems"] = learning_results
        return learning_results
    
    async def test_trading_engines(self):
        """Test all trading engines"""
        self.log("TESTING TRADING ENGINES")
        print("=" * 60)
        
        engines = [
            ("Crypto Engine", "/api/trading/crypto-engine/status"),
            ("Options Engine", "/api/trading/options-engine/status"),
            ("Advanced Engine", "/api/trading/advanced-engine/status"),
            ("Market Maker", "/api/trading/market-maker/status"),
            ("Master Engine", "/api/trading/master-engine/status"),
            ("HRM Engine", "/api/trading/hrm-engine/status")
        ]
        
        engine_results = {}
        
        for name, endpoint in engines:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=5
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            engine_results[name] = {
                                "status": "operational",
                                "response_time": response_time,
                                "data": data
                            }
                            self.log(f"[CHECK] {name}: {response_time:.3f}s")
                        else:
                            engine_results[name] = {
                                "status": "error",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {name}: HTTP {response.status}")
            except Exception as e:
                engine_results[name] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {name}: {str(e)}")
        
        self.results["trading_engines"] = engine_results
        return engine_results
    
    async def test_trading_capabilities(self):
        """Test trading functionality"""
        self.log("TESTING TRADING CAPABILITIES")
        print("=" * 60)
        
        trading_tests = [
            ("Portfolio Positions", "/api/portfolio/positions"),
            ("Portfolio Value", "/api/portfolio/value"),
            ("Trading History", "/api/trading/history"),
            ("Active Trades", "/api/trading/active"),
            ("Live Trading Status", "/api/live-trading/status")
        ]
        
        trading_results = {}
        
        for name, endpoint in trading_tests:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.base_url}{endpoint}",
                        timeout=5
                    ) as response:
                        response_time = time.time() - start_time
                        
                        if response.status == 200:
                            data = await response.json()
                            trading_results[name] = {
                                "status": "success",
                                "response_time": response_time,
                                "data": data
                            }
                            self.log(f"[CHECK] {name}: {response_time:.3f}s")
                        else:
                            trading_results[name] = {
                                "status": "error",
                                "response_time": response_time,
                                "error": f"HTTP {response.status}"
                            }
                            self.log(f"[ERROR] {name}: HTTP {response.status}")
            except Exception as e:
                trading_results[name] = {
                    "status": "error",
                    "response_time": 0,
                    "error": str(e)
                }
                self.log(f"[ERROR] {name}: {str(e)}")
        
        self.results["trading_capabilities"] = trading_results
        return trading_results
    
    async def test_performance_metrics(self):
        """Test system performance"""
        self.log("TESTING PERFORMANCE METRICS")
        print("=" * 60)
        
        # Test response times under load
        load_test_results = await self._load_test()
        
        # Test concurrent requests
        concurrent_results = await self._concurrent_test()
        
        performance_results = {
            "load_test": load_test_results,
            "concurrent_test": concurrent_results
        }
        
        self.results["performance"] = performance_results
        return performance_results
    
    async def _load_test(self):
        """Test system under load"""
        self.log("Running load test...")
        
        test_prompts = [
            "Analyze AAPL stock",
            "What are market trends?",
            "Assess crypto risk",
            "Optimize portfolio",
            "Predict TSLA price"
        ]
        
        response_times = []
        
        for i in range(10):  # 10 requests
            prompt = test_prompts[i % len(test_prompts)]
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.ai_url}/generate",
                        json={"prompt": prompt, "max_tokens": 200},
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            response_times.append(time.time() - start_time)
            except Exception as e:
                self.log(f"Load test error: {e}")
        
        if response_times:
            return {
                "avg_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "total_requests": len(response_times),
                "success_rate": len(response_times) / 10 * 100
            }
        else:
            return {"error": "No successful responses"}
    
    async def _concurrent_test(self):
        """Test concurrent request handling"""
        self.log("Running concurrent test...")
        
        async def make_request(session, prompt):
            try:
                start_time = time.time()
                async with session.post(
                    f"{self.ai_url}/generate",
                    json={"prompt": prompt, "max_tokens": 100},
                    timeout=30
                ) as response:
                    response_time = time.time() - start_time
                    return {"success": response.status == 200, "response_time": response_time}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        prompts = [
            "Analyze AAPL", "Analyze TSLA", "Analyze MSFT",
            "Analyze GOOGL", "Analyze AMZN"
        ]
        
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            tasks = [make_request(session, prompt) for prompt in prompts]
            results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.get("success", False))
        response_times = [r.get("response_time", 0) for r in results if r.get("success", False)]
        
        return {
            "total_time": total_time,
            "concurrent_requests": len(prompts),
            "successful_requests": successful,
            "success_rate": successful / len(prompts) * 100,
            "avg_response_time": statistics.mean(response_times) if response_times else 0
        }
    
    def generate_report(self):
        """Generate comprehensive benchmark report"""
        self.log("GENERATING BENCHMARK REPORT")
        print("=" * 60)
        
        # Calculate overall scores
        total_tests = 0
        passed_tests = 0
        avg_response_time = 0
        response_times = []
        
        for category, results in self.results.items():
            if isinstance(results, dict):
                for test_name, test_result in results.items():
                    total_tests += 1
                    if test_result.get("status") in ["success", "healthy", "active", "operational"]:
                        passed_tests += 1
                    if "response_time" in test_result and test_result["response_time"] > 0:
                        response_times.append(test_result["response_time"])
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            "benchmark_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "test_duration": time.time() - self.start_time if self.start_time else 0
            },
            "detailed_results": self.results
        }
        
        # Save report
        with open("ai_benchmark_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"Test Duration: {time.time() - self.start_time:.1f}s")
        print("=" * 60)
        
        if success_rate >= 90:
            print("🎉 EXCELLENT: System performing at optimal level!")
        elif success_rate >= 80:
            print("[CHECK] GOOD: System performing well with minor issues")
        elif success_rate >= 70:
            print("[WARNING]️ FAIR: System needs some improvements")
        else:
            print("[ERROR] POOR: System needs significant improvements")
        
        return report
    
    async def run_full_benchmark(self):
        """Run complete benchmark suite"""
        self.start_time = time.time()
        self.log("STARTING COMPREHENSIVE AI BENCHMARK")
        print("=" * 60)
        print(f"Benchmark started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Run all tests
        await self.test_server_health()
        await self.test_ai_capabilities()
        await self.test_ai_agents()
        await self.test_revolutionary_systems()
        await self.test_learning_systems()
        await self.test_trading_engines()
        await self.test_trading_capabilities()
        await self.test_performance_metrics()
        
        # Generate report
        report = self.generate_report()
        
        self.log("BENCHMARK COMPLETE")
        return report

async def main():
    """Main benchmark function"""
    benchmark = AIBenchmarkSuite()
    await benchmark.run_full_benchmark()

if __name__ == "__main__":
    asyncio.run(main())

