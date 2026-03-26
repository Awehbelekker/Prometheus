#!/usr/bin/env python3
"""
Test GLM-4-Flash Visual AI Integration
Quick test to verify GLM API key and connectivity
"""

import os
from pathlib import Path
from core.cloud_vision_analyzer import CloudVisionAnalyzer, CloudVisionConfig

def test_glm_integration():
    """Test GLM-4-Flash integration"""
    
    print("\n" + "="*60)
    print("GLM-4-FLASH INTEGRATION TEST")
    print("="*60)
    
    # Check API key
    api_key = os.getenv('ZHIPUAI_API_KEY')
    if not api_key or api_key == 'your_zhipu_api_key_here':
        print("\n❌ ZHIPUAI_API_KEY not found or placeholder value")
        print("   Please add your GLM API key to .env file")
        print("\n   Get key from: https://open.bigmodel.cn/")
        return False
    
    print(f"\n✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Initialize analyzer
    config = CloudVisionConfig(
        provider="glm",
        model="glm-4v-flash",
        api_key=api_key,
        batch_delay=1.0
    )
    
    analyzer = CloudVisionAnalyzer(config)
    print(f"✅ Analyzer initialized: {config.provider} - {config.model}")
    
    # Find a sample chart
    chart_dir = Path("paper_trading_charts")
    if not chart_dir.exists():
        print("\n⚠️  No paper_trading_charts directory found")
        print("   Create some charts first with paper trading")
        return False
    
    charts = list(chart_dir.glob("*.png"))
    if not charts:
        print("\n⚠️  No PNG charts found in paper_trading_charts/")
        return False
    
    test_chart = charts[0]
    print(f"\n📊 Testing with: {test_chart.name}")
    
    # Analyze chart
    try:
        print("\n🔄 Calling GLM-4-Flash API...")
        result = analyzer.analyze_chart(
            str(test_chart),
            symbol="TEST",
            timeframe="5min"
        )
        
        if result.success:
            print("\n✅ SUCCESS! GLM-4-Flash is working!")
            print(f"\n📊 Analysis Results:")
            print(f"   Patterns: {len(result.patterns_detected)}")
            print(f"   Trend: {result.trend_direction} ({result.trend_strength})")
            print(f"   Confidence: {result.confidence*100:.1f}%")
            print(f"   Latency: {result.latency:.2f}s")
            
            if result.patterns_detected:
                print(f"\n   Detected Patterns:")
                for pattern in result.patterns_detected:
                    print(f"   • {pattern}")
            
            print(f"\n   Reasoning: {result.reasoning[:200]}...")
            return True
        else:
            print(f"\n❌ Analysis failed")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_glm_integration()
    
    if success:
        print("\n" + "="*60)
        print("🎉 GLM-4-FLASH READY FOR PRODUCTION!")
        print("="*60)
        print("\nNext Steps:")
        print("1. Run: python train_paper_trading_charts.py")
        print("2. Analyze all 32 captured charts")
        print("3. Discover new crypto/forex patterns")
        print("4. Improve trading signals")
    else:
        print("\n" + "="*60)
        print("⚠️  GLM-4-FLASH SETUP INCOMPLETE")
        print("="*60)
        print("\nPlease:")
        print("1. Add ZHIPUAI_API_KEY to .env file")
        print("2. Get key from: https://open.bigmodel.cn/")
        print("3. Run this test again")
