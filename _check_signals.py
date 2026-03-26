#!/usr/bin/env python3
"""
Diagnostic: Check AI signal generation
"""
import os
import asyncio
from dotenv import load_dotenv
load_dotenv()

print("=" * 60)
print("  PROMETHEUS AI SIGNAL DIAGNOSTIC")
print("=" * 60)

# Test crypto signals (should work 24/7)
test_symbols = ['BTC/USD', 'ETH/USD', 'AAPL']

async def test_signals():
    # Check if we can import and get market data
    print("\n📊 Testing Market Data Retrieval...")
    
    try:
        from core.real_time_market_data import RealTimeMarketDataOrchestrator
        market_data_service = RealTimeMarketDataOrchestrator()
        print("   ✅ RealTimeMarketDataOrchestrator loaded")
    except Exception as e:
        print(f"   ❌ Market data service failed: {e}")
        market_data_service = None
    
    # Test AI systems availability
    print("\n🤖 Checking AI Systems...")
    
    ai_systems = {}
    
    # Market Oracle
    try:
        from revolutionary_features.oracle.market_oracle_engine import MarketOracleEngine
        ai_systems['oracle'] = MarketOracleEngine()
        print("   ✅ Market Oracle Engine")
    except Exception as e:
        print(f"   ❌ Market Oracle: {e}")
    
    # Quantum Trading
    try:
        from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
        ai_systems['quantum'] = QuantumTradingEngine()
        print("   ✅ Quantum Trading Engine")
    except Exception as e:
        print(f"   ❌ Quantum Trading: {e}")
    
    # HRM
    try:
        from core.hierarchical_reasoning import HierarchicalReasoningModel
        ai_systems['hrm'] = HierarchicalReasoningModel()
        print("   ✅ Hierarchical Reasoning Model (HRM)")
    except Exception as e:
        print(f"   ❌ HRM: {e}")
    
    # GPT-OSS
    try:
        from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
        ai_systems['gpt_oss'] = GPTOSSTradingAdapter()
        print("   ✅ GPT-OSS Trading Adapter")
    except Exception as e:
        print(f"   ❌ GPT-OSS: {e}")
    
    print(f"\n📊 Loaded {len(ai_systems)} AI systems")
    
    # Test market data for symbols
    print("\n📈 Testing Market Data for Symbols...")
    for symbol in test_symbols:
        try:
            if market_data_service:
                data = await market_data_service.get_real_time_data(symbol)
                if data:
                    print(f"   ✅ {symbol}: ${data.get('price', 'N/A')}")
                else:
                    print(f"   ⚠️  {symbol}: No data returned")
        except Exception as e:
            print(f"   ❌ {symbol}: {e}")
    
    # Test signal generation on BTC/USD
    print("\n🎯 Testing Signal Generation (BTC/USD)...")
    
    # Simple technical analysis
    try:
        import yfinance as yf
        btc = yf.Ticker("BTC-USD")
        hist = btc.history(period="5d", interval="1h")
        if not hist.empty:
            current_price = hist['Close'].iloc[-1]
            price_change = (hist['Close'].iloc[-1] / hist['Close'].iloc[-24] - 1) * 100
            avg_volume = hist['Volume'].mean()
            
            print(f"   BTC Price: ${current_price:,.2f}")
            print(f"   24h Change: {price_change:+.2f}%")
            
            # Simple signal logic
            if price_change > 3:
                action = "STRONG_BUY"
                confidence = min(0.9, 0.5 + price_change/10)
            elif price_change > 1:
                action = "BUY"
                confidence = 0.6 + price_change/20
            elif price_change < -3:
                action = "STRONG_SELL"
                confidence = min(0.9, 0.5 + abs(price_change)/10)
            elif price_change < -1:
                action = "SELL"
                confidence = 0.6 + abs(price_change)/20
            else:
                action = "HOLD"
                confidence = 0.4
            
            print(f"\n   📊 SIGNAL RESULT:")
            print(f"   Action: {action}")
            print(f"   Confidence: {confidence*100:.1f}%")
            print(f"   Would Execute: {'YES' if confidence >= 0.50 else 'NO'} (threshold: 50%)")
        else:
            print("   ❌ No historical data available")
    except Exception as e:
        print(f"   ❌ Signal test failed: {e}")
    
    print("\n" + "=" * 60)

# Run
asyncio.run(test_signals())

