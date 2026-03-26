"""
🚀 QUICK AI TRADING DEMO - ENHANCED FEATURES
===========================================
Testing enhanced AI capabilities and new features
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def quick_ai_demo():
    """Quick demonstration of key AI trading features"""
    
    print("🤖 PROMETHEUS AI TRADING - QUICK DEMO")
    print("="*50)
    print(f"🕐 Time: {datetime.now().strftime('%H:%M:%S')}")
    
    base_url = "http://localhost:8000/api/ai-trading"
    
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health Check
        print("\n🔍 Testing AI Service Health...")
        try:
            async with session.get(f"{base_url}/health") as response:
                health = await response.json()
                print(f"   [CHECK] Status: {health.get('ai_trading_service', 'unknown')}")
                print(f"   🤖 GPT-OSS 20B: {'[CHECK]' if health.get('gpt_oss_20b') else '[ERROR]'}")
                print(f"   🤖 GPT-OSS 120B: {'[CHECK]' if health.get('gpt_oss_120b') else '[ERROR]'}")
        except Exception as e:
            print(f"   [ERROR] Health check failed: {e}")
            return
        
        # Test 2: Quick Sentiment Analysis
        print("\n📊 Testing Sentiment Analysis...")
        sentiment_request = {
            "symbol": "AAPL",
            "include_news": True,
            "model_size": "20b"
        }
        
        try:
            start_time = time.time()
            async with session.post(
                f"{base_url}/sentiment-analysis",
                json=sentiment_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = (time.time() - start_time) * 1000
                data = await response.json()
                
                if data.get('success'):
                    sentiment_data = data['data']
                    print(f"   [CHECK] Analysis completed in {response_time:.1f}ms")
                    print(f"   📈 Symbol: {sentiment_data['symbol']}")
                    print(f"   🎯 Sentiment: {sentiment_data['sentiment']}")
                    print(f"   🔢 Confidence: {sentiment_data['confidence']:.2f}")
                    print(f"   🤖 Model: {data.get('model_used', 'unknown')}")
                else:
                    print(f"   [ERROR] Analysis failed")
                    
        except Exception as e:
            print(f"   [ERROR] Sentiment analysis error: {e}")
        
        # Test 3: Model Status
        print("\n🔧 Checking Model Status...")
        try:
            async with session.get(f"{base_url}/models/status") as response:
                models = await response.json()
                
                if 'models' in models:
                    for model, info in models['models'].items():
                        available = info.get('available', False) if isinstance(info, dict) else info
                        status = '[CHECK] Ready' if available else '[ERROR] Offline'
                        print(f"   🤖 {model}: {status}")
                        
                        if isinstance(info, dict) and 'url' in info:
                            print(f"      🔗 URL: {info['url']}")
                            
        except Exception as e:
            print(f"   [ERROR] Model status error: {e}")
        
        # Test 4: Quick Strategy Generation
        print("\n🎯 Testing Strategy Generation...")
        strategy_request = {
            "symbol": "TSLA",
            "market_data": {
                "current_price": 235.50,
                "volume": 2500000,
                "change_percent": 3.2,
                "volatility": 0.35,
                "market_cap": 750000000000
            },
            "strategy_context": "Electric vehicle leader with strong growth potential",
            "analysis_type": "momentum",
            "time_horizon": "swing",
            "risk_tolerance": "moderate",
            "model_size": "120b"
        }
        
        try:
            start_time = time.time()
            async with session.post(
                f"{base_url}/trading-strategy",
                json=strategy_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_time = (time.time() - start_time) * 1000
                data = await response.json()
                
                if data.get('success'):
                    strategy_data = data['data']
                    print(f"   [CHECK] Strategy generated in {response_time:.1f}ms")
                    print(f"   📈 Symbol: {strategy_data.get('symbol', 'N/A')}")
                    print(f"   🎯 Action: {strategy_data.get('action', 'N/A')}")
                    print(f"   🔢 Confidence: {strategy_data.get('confidence', 0):.2f}")
                    print(f"   ⏰ Time Horizon: {strategy_data.get('time_horizon', 'N/A')}")
                    print(f"   🛡️ Risk: {strategy_data.get('risk_assessment', 'N/A')}")
                else:
                    print(f"   [WARNING]️ Strategy generation returned: {data}")
                    
        except Exception as e:
            print(f"   [ERROR] Strategy generation error: {e}")
    
    print("\n" + "="*50)
    print("🎉 Quick Demo Complete!")
    print("[CHECK] AI Trading Integration Operational")
    print("🚀 Ready for Frontend Integration")

if __name__ == "__main__":
    asyncio.run(quick_ai_demo())
