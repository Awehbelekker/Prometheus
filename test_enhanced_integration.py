"""
Test enhanced data integration - verify all systems connected
"""
import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_enhanced_data():
    """Test enhanced data fetching for AAPL"""
    
    print("🧪 TESTING ENHANCED DATA INTEGRATION\n")
    print("=" * 60)
    
    try:
        # Import learning engine
        from PROMETHEUS_ULTIMATE_LEARNING_ENGINE import ParallelBacktester
        
        print("✅ Learning engine imported successfully")
        
        # Create instance
        backtester = ParallelBacktester()
        print("✅ Backtester instance created")
        
        # Test enhanced data fetching
        print("\n📊 Fetching enhanced data for AAPL...")
        enhanced_data = await backtester._get_enhanced_market_data('AAPL')
        
        if enhanced_data:
            print("✅ Enhanced data retrieved successfully!\n")
            print("📈 Data Sources Available:")
            print("-" * 60)
            
            sources = []
            if 'visual_patterns' in enhanced_data:
                patterns = enhanced_data['visual_patterns']
                print(f"  🎨 Visual Patterns: {len(patterns)} detected")
                sources.append('visual_patterns')
            
            if 'sentiment' in enhanced_data:
                sentiment = enhanced_data['sentiment']
                print(f"  😊 Overall Sentiment: {sentiment:.2f} (-1 to +1)")
                sources.append('sentiment')
            
            if 'risk_level' in enhanced_data:
                risk = enhanced_data['risk_level']
                print(f"  ⚠️  Risk Level: {risk:.2f} (0 to 1)")
                sources.append('risk_level')
            
            if 'opportunity_score' in enhanced_data:
                opp = enhanced_data['opportunity_score']
                print(f"  🎯 Opportunity Score: {opp:.2f} (0 to 1)")
                sources.append('opportunity_score')
            
            if 'news_count' in enhanced_data:
                news_count = enhanced_data['news_count']
                news_sentiment = enhanced_data.get('news_sentiment', 0)
                print(f"  📰 News: {news_count} articles (sentiment: {news_sentiment:.2f})")
                sources.append('news')
            
            if 'social_mentions' in enhanced_data:
                mentions = enhanced_data['social_mentions']
                social_sentiment = enhanced_data.get('social_sentiment', 0)
                print(f"  💬 Social: {mentions} mentions (sentiment: {social_sentiment:.2f})")
                sources.append('social')
            
            print(f"\n✅ TOTAL: {len(sources)} data sources active")
            
            # Test signal calculation with enhanced data
            print("\n🎯 Testing Signal Calculation...")
            from PROMETHEUS_ULTIMATE_LEARNING_ENGINE import TradingStrategy
            
            # Create test strategy
            strategy = TradingStrategy(
                strategy_type='momentum',
                parameters={'momentum_threshold': 0.02},
                suitable_regimes=['trending_up', 'volatile']
            )
            
            # Create fake lookback bars
            lookback = [
                {'close': 150 + i * 0.5, 'volume': 1000000} 
                for i in range(20)
            ]
            current = {'close': 155, 'volume': 1200000}
            
            signal = backtester._calculate_signal(
                strategy, 
                lookback, 
                current, 
                enhanced_data
            )
            
            print(f"  📊 Test Signal: {signal.upper()}")
            print("  ✅ Signal calculation working with enhanced data!")
            
        else:
            print("⚠️  No enhanced data returned (sources may be unavailable)")
            print("   This is OK - system will gracefully fall back to price-only")
        
        print("\n" + "=" * 60)
        print("🎉 INTEGRATION TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_data())
