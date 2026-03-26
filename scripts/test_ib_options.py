#!/usr/bin/env python3
"""
🧪 INTERACTIVE BROKERS OPTIONS INTEGRATION TEST
Test the new IB options trading system with real market data
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_ib_options_integration():
    """Test Interactive Brokers options integration"""
    print("🚀 TESTING INTERACTIVE BROKERS OPTIONS INTEGRATION")
    print("=" * 60)
    
    try:
        # Import the IB options integration
        from PROMETHEUS-Enterprise-Package.backend.core.ib_options_integration import ib_options
        
        print("[CHECK] IB Options integration imported successfully")
        
        # Test symbols
        test_symbols = ['AAPL', 'SPY', 'QQQ', 'TSLA']
        
        for symbol in test_symbols:
            print(f"\n📊 Testing options chain for {symbol}...")
            
            try:
                # Get options chain
                chain = await ib_options.get_options_chain(symbol)
                
                if chain:
                    print(f"[CHECK] {symbol} Options Chain Retrieved:")
                    print(f"   Underlying Price: ${chain.underlying_price:.2f}")
                    print(f"   Expiration Dates: {len(chain.expiration_dates)}")
                    print(f"   Strikes Available: {len(chain.strikes)}")
                    print(f"   Calls: {len(chain.calls)}")
                    print(f"   Puts: {len(chain.puts)}")
                    
                    # Show sample call option
                    if chain.calls:
                        sample_call = chain.calls[0]
                        print(f"   Sample Call: {sample_call.symbol}")
                        print(f"     Strike: ${sample_call.strike}")
                        print(f"     Price: ${sample_call.price:.2f}")
                        print(f"     Delta: {sample_call.delta:.4f}")
                        print(f"     IV: {sample_call.implied_volatility:.2%}")
                    
                    # Show sample put option
                    if chain.puts:
                        sample_put = chain.puts[0]
                        print(f"   Sample Put: {sample_put.symbol}")
                        print(f"     Strike: ${sample_put.strike}")
                        print(f"     Price: ${sample_put.price:.2f}")
                        print(f"     Delta: {sample_put.delta:.4f}")
                        print(f"     IV: {sample_put.implied_volatility:.2%}")
                        
                else:
                    print(f"[ERROR] No options chain available for {symbol}")
                    
            except Exception as e:
                print(f"[ERROR] Error testing {symbol}: {e}")
                
        # Test strategy execution (dry run)
        print(f"\n🎯 Testing Options Strategy Execution...")
        
        try:
            # Test covered call strategy
            result = await ib_options.execute_options_strategy('AAPL', 'covered_call', 1)
            
            print(f"Strategy Execution Result:")
            print(f"  Success: {result.success}")
            print(f"  Order ID: {result.order_id}")
            print(f"  Contract: {result.contract_symbol}")
            print(f"  Side: {result.side}")
            print(f"  Quantity: {result.quantity}")
            print(f"  Price: ${result.price:.2f}")
            print(f"  Strategy: {result.strategy}")
            
            if not result.success:
                print(f"  Error: {result.error_message}")
                
        except Exception as e:
            print(f"[ERROR] Error testing strategy execution: {e}")
            
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Make sure the IB options integration is properly installed")
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        
    print("\n" + "=" * 60)
    print("🏁 IB Options Integration Test Complete")

async def test_revolutionary_options_engine():
    """Test the updated revolutionary options engine"""
    print("\n🔥 TESTING REVOLUTIONARY OPTIONS ENGINE WITH IB INTEGRATION")
    print("=" * 60)
    
    try:
        from PROMETHEUS-Enterprise-Package.backend.revolutionary_options_engine import PrometheusRevolutionaryOptionsEngine
        
        # Initialize engine
        engine = PrometheusRevolutionaryOptionsEngine("test_key", "test_secret")
        print("[CHECK] Revolutionary Options Engine initialized")
        
        # Test real options chain retrieval
        test_symbols = ['AAPL', 'SPY']
        
        for symbol in test_symbols:
            print(f"\n📈 Testing real options chain for {symbol}...")
            
            try:
                chain_data = await engine.get_real_options_chain(symbol)
                
                if chain_data:
                    print(f"[CHECK] {symbol} Real Options Data:")
                    print(f"   Source: {chain_data.get('source', 'Unknown')}")
                    print(f"   Underlying Price: ${chain_data.get('underlying_price', 0):.2f}")
                    print(f"   Calls: {len(chain_data.get('calls', []))}")
                    print(f"   Puts: {len(chain_data.get('puts', []))}")
                    print(f"   Expirations: {len(chain_data.get('expiration_dates', []))}")
                    
                    # Show sample data
                    calls = chain_data.get('calls', [])
                    if calls:
                        sample = calls[0]
                        print(f"   Sample Call: {sample.get('symbol', 'N/A')}")
                        print(f"     Strike: ${sample.get('strike', 0)}")
                        print(f"     Price: ${sample.get('price', 0):.2f}")
                        print(f"     Delta: {sample.get('delta', 0):.4f}")
                        
                else:
                    print(f"[ERROR] No options data for {symbol}")
                    
            except Exception as e:
                print(f"[ERROR] Error testing {symbol}: {e}")
                
        # Test engine status
        print(f"\n⚙️ Testing Engine Status...")
        status = await engine.get_engine_status()
        print(f"Engine Status: {status.get('status', 'unknown')}")
        print(f"Active Strategies: {status.get('active_strategies', 0)}")
        print(f"Features: {status.get('features', [])}")
        
    except Exception as e:
        print(f"[ERROR] Error testing revolutionary options engine: {e}")
        
    print("\n" + "=" * 60)
    print("🏁 Revolutionary Options Engine Test Complete")

async def main():
    """Main test function"""
    print("🧪 PROMETHEUS IB OPTIONS INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test 1: IB Options Integration
    await test_ib_options_integration()
    
    # Test 2: Revolutionary Options Engine
    await test_revolutionary_options_engine()
    
    print("\n🎉 ALL TESTS COMPLETED!")
    print("=" * 80)

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('.env.live')
    
    # Run tests
    asyncio.run(main())
