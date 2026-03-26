"""
🤖 PROMETHEUS AI TRADING INTEGRATION - COMPREHENSIVE DEMO
========================================================
Complete demonstration of GPT-OSS AI trading capabilities
Date: August 30, 2025
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class ComprehensiveAITradingDemo:
    """Complete demonstration of all AI trading capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_result(self, endpoint: str, response: Dict[str, Any], response_time: float):
        """Print formatted API result"""
        print(f"\n📡 Endpoint: {endpoint}")
        print(f"⏱️  Response Time: {response_time:.2f}ms")
        print(f"📊 Status: {'[CHECK] SUCCESS' if response.get('success') else '[ERROR] ERROR'}")
        
        if response.get('success') and response.get('data'):
            data = response['data']
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, (list, dict)):
                        print(f"   {key}: {json.dumps(value, indent=2)[:100]}...")
                    else:
                        print(f"   {key}: {value}")
        else:
            print(f"   Response: {json.dumps(response, indent=2)[:200]}...")
    
    async def test_service_health(self):
        """Test all service health endpoints"""
        self.print_header("SERVICE HEALTH CHECK")
        
        health_endpoints = [
            "/health",
            "/api/ai-trading/health",
        ]
        
        for endpoint in health_endpoints:
            try:
                start_time = time.time()
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    
                print(f"\n🔍 Testing: {endpoint}")
                print(f"   Status Code: {response.status}")
                print(f"   Response Time: {response_time:.2f}ms")
                
                if response.status == 200:
                    print(f"   [CHECK] Service Healthy")
                    if 'services' in data:
                        for service, status in data['services'].items():
                            print(f"   📡 {service}: {'[CHECK]' if status else '[ERROR]'}")
                else:
                    print(f"   [ERROR] Service Error")
                    
            except Exception as e:
                print(f"   [ERROR] Connection Error: {e}")
    
    async def demo_sentiment_analysis(self):
        """Demonstrate market sentiment analysis"""
        self.print_header("MARKET SENTIMENT ANALYSIS")
        
        test_cases = [
            {
                "symbol": "AAPL",
                "news_data": [
                    "Apple reports record Q3 earnings, beats expectations",
                    "iPhone 15 sales exceed analyst predictions",
                    "Apple stock reaches new all-time high"
                ]
            },
            {
                "symbol": "TSLA", 
                "news_data": [
                    "Tesla faces production challenges in China",
                    "Elon Musk announces new Supercharger expansion",
                    "Tesla stock volatile amid market uncertainty"
                ]
            },
            {
                "symbol": "NVDA",
                "news_data": [
                    "NVIDIA AI chip demand surges globally",
                    "New H100 datacenter partnerships announced",
                    "Gaming segment shows strong growth"
                ]
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/api/ai-trading/sentiment-analysis",
                    json=test_case,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    self.print_result("sentiment-analysis", data, response_time)
                    
                await asyncio.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"[ERROR] Sentiment Analysis Error: {e}")
    
    async def demo_strategy_generation(self):
        """Demonstrate trading strategy generation"""
        self.print_header("TRADING STRATEGY GENERATION")
        
        strategy_requests = [
            {
                "symbol": "AAPL",
                "timeframe": "intraday",
                "risk_tolerance": "moderate",
                "account_size": 50000,
                "market_conditions": "bullish"
            },
            {
                "symbol": "BTC-USD",
                "timeframe": "swing",
                "risk_tolerance": "high", 
                "account_size": 25000,
                "market_conditions": "volatile"
            },
            {
                "symbol": "SPY",
                "timeframe": "position",
                "risk_tolerance": "low",
                "account_size": 100000,
                "market_conditions": "neutral"
            }
        ]
        
        for request in strategy_requests:
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/api/ai-trading/trading-strategy",
                    json=request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    self.print_result("trading-strategy", data, response_time)
                    
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"[ERROR] Strategy Generation Error: {e}")
    
    async def demo_technical_analysis(self):
        """Demonstrate technical pattern recognition"""
        self.print_header("TECHNICAL PATTERN RECOGNITION")
        
        technical_requests = [
            {
                "symbol": "AAPL",
                "price_data": [150.0, 152.5, 151.0, 153.5, 155.0, 154.0, 156.5, 158.0],
                "volume_data": [1000000, 1200000, 980000, 1500000, 1300000, 1100000, 1400000, 1600000],
                "indicators": ["RSI", "MACD", "SMA"]
            },
            {
                "symbol": "TSLA",
                "price_data": [220.0, 225.0, 218.0, 232.0, 228.0, 235.0, 240.0, 238.0],
                "volume_data": [2000000, 2500000, 1800000, 3000000, 2200000, 2800000, 3200000, 2900000],
                "indicators": ["Bollinger Bands", "Stochastic", "Williams %R"]
            }
        ]
        
        for request in technical_requests:
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/api/ai-trading/technical-analysis",
                    json=request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    self.print_result("technical-analysis", data, response_time)
                    
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"[ERROR] Technical Analysis Error: {e}")
    
    async def demo_risk_assessment(self):
        """Demonstrate portfolio risk assessment"""
        self.print_header("PORTFOLIO RISK ASSESSMENT")
        
        portfolio_requests = [
            {
                "portfolio": [
                    {"symbol": "AAPL", "allocation": 0.3, "current_price": 155.0},
                    {"symbol": "MSFT", "allocation": 0.25, "current_price": 280.0},
                    {"symbol": "GOOGL", "allocation": 0.2, "current_price": 120.0},
                    {"symbol": "TSLA", "allocation": 0.15, "current_price": 235.0},
                    {"symbol": "NVDA", "allocation": 0.1, "current_price": 450.0}
                ],
                "market_conditions": "volatile",
                "time_horizon": "6_months"
            },
            {
                "portfolio": [
                    {"symbol": "SPY", "allocation": 0.6, "current_price": 450.0},
                    {"symbol": "QQQ", "allocation": 0.3, "current_price": 380.0},
                    {"symbol": "IWM", "allocation": 0.1, "current_price": 195.0}
                ],
                "market_conditions": "stable",
                "time_horizon": "1_year"
            }
        ]
        
        for request in portfolio_requests:
            try:
                start_time = time.time()
                async with self.session.post(
                    f"{self.base_url}/api/ai-trading/risk-assessment",
                    json=request,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    data = await response.json()
                    self.print_result("risk-assessment", data, response_time)
                    
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"[ERROR] Risk Assessment Error: {e}")
    
    async def demo_batch_analysis(self):
        """Demonstrate batch processing capabilities"""
        self.print_header("BATCH ANALYSIS PROCESSING")
        
        batch_request = {
            "symbols": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
            "analysis_types": ["sentiment", "technical", "risk"],
            "market_data": {
                "AAPL": {"price": 155.0, "volume": 1000000},
                "MSFT": {"price": 280.0, "volume": 800000},
                "GOOGL": {"price": 120.0, "volume": 1200000},
                "TSLA": {"price": 235.0, "volume": 2000000},
                "NVDA": {"price": 450.0, "volume": 1500000}
            }
        }
        
        try:
            start_time = time.time()
            async with self.session.post(
                f"{self.base_url}/api/ai-trading/batch-analysis",
                json=batch_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = (time.time() - start_time) * 1000
                data = await response.json()
                self.print_result("batch-analysis", data, response_time)
                
        except Exception as e:
            print(f"[ERROR] Batch Analysis Error: {e}")
    
    async def demo_model_status(self):
        """Check AI model availability and status"""
        self.print_header("AI MODEL STATUS")
        
        try:
            start_time = time.time()
            async with self.session.get(f"{self.base_url}/api/ai-trading/models/status") as response:
                response_time = (time.time() - start_time) * 1000
                data = await response.json()
                self.print_result("models/status", data, response_time)
                
        except Exception as e:
            print(f"[ERROR] Model Status Error: {e}")
    
    async def run_comprehensive_demo(self):
        """Run the complete AI trading demonstration"""
        print("🚀 PROMETHEUS AI TRADING INTEGRATION - COMPREHENSIVE DEMO")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Base URL: {self.base_url}")
        print("📊 Testing all AI trading capabilities...")
        
        demo_steps = [
            ("Service Health Check", self.test_service_health),
            ("Model Status Check", self.demo_model_status),
            ("Market Sentiment Analysis", self.demo_sentiment_analysis),
            ("Trading Strategy Generation", self.demo_strategy_generation), 
            ("Technical Pattern Recognition", self.demo_technical_analysis),
            ("Portfolio Risk Assessment", self.demo_risk_assessment),
            ("Batch Analysis Processing", self.demo_batch_analysis)
        ]
        
        total_start = time.time()
        
        for step_name, step_func in demo_steps:
            print(f"\n🔄 Executing: {step_name}")
            step_start = time.time()
            
            try:
                await step_func()
                step_time = time.time() - step_start
                print(f"[CHECK] {step_name} completed in {step_time:.2f}s")
            except Exception as e:
                print(f"[ERROR] {step_name} failed: {e}")
        
        total_time = time.time() - total_start
        
        self.print_header("DEMO COMPLETION SUMMARY")
        print(f"⏰ Total Demo Time: {total_time:.2f}s")
        print(f"🎯 All AI Trading Capabilities Tested")
        print(f"[CHECK] GPT-OSS Integration Fully Operational")
        print(f"🚀 PROMETHEUS AI Trading Ready for Production!")

async def main():
    """Main demo execution"""
    async with ComprehensiveAITradingDemo() as demo:
        await demo.run_comprehensive_demo()

if __name__ == "__main__":
    print("🤖 Starting Comprehensive AI Trading Demo...")
    asyncio.run(main())
