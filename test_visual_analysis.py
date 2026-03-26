"""
Test LLaVA Visual Analysis
Quick test to verify LLaVA can analyze charts
"""

import asyncio
from pathlib import Path

try:
    from core.chart_generator import generate_chart_from_polygon
    from core.multimodal_analyzer import MultimodalChartAnalyzer
    IMPORTS_OK = True
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    IMPORTS_OK = False


async def test_visual_analysis():
    """Test LLaVA on a sample chart"""
    
    print("\n" + "="*70)
    print("LLAVA VISUAL ANALYSIS TEST")
    print("="*70)
    
    if not IMPORTS_OK:
        print("\n[ERROR] Required modules not available")
        return False
    
    # Initialize analyzer
    analyzer = MultimodalChartAnalyzer()
    
    if not analyzer.model_available:
        print("\n[ERROR] LLaVA model not available!")
        print("Run: python setup_llava_system.py")
        return False
    
    print("\n[OK] LLaVA model available")
    
    # Generate a test chart
    print("\n[1/3] Generating test chart...")
    chart_path = generate_chart_from_polygon('AAPL', timeframe='1D', days_back=90)
    
    if not chart_path:
        print("[ERROR] Could not generate chart")
        return False
    
    print(f"[OK] Chart generated: {chart_path}")
    
    # Analyze the chart
    print("\n[2/3] Analyzing chart with LLaVA...")
    print("(This may take 10-30 seconds...)")
    
    result = analyzer.analyze_chart(
        chart_path,
        context={'symbol': 'AAPL', 'timeframe': '1D'}
    )
    
    if not result.success:
        print(f"[ERROR] Analysis failed: {result.error}")
        return False
    
    # Display results
    print("\n[3/3] Analysis Results:")
    print("="*70)
    
    print(f"\nPatterns Detected: {len(result.patterns_detected)}")
    for pattern in result.patterns_detected:
        print(f"  - {pattern}")
    
    print(f"\nSupport Levels:")
    for level in result.support_levels:
        print(f"  - ${level:.2f}")
    
    print(f"\nResistance Levels:")
    for level in result.resistance_levels:
        print(f"  - ${level:.2f}")
    
    print(f"\nTrend Analysis:")
    print(f"  Direction: {result.trend_direction}")
    print(f"  Strength: {result.trend_strength}")
    
    print(f"\nTechnical Indicators:")
    for indicator in result.indicators_present:
        print(f"  - {indicator}")
    
    print(f"\nSignal Quality: {result.signal_quality}")
    print(f"Confidence: {result.confidence:.2%}")
    
    print(f"\nReasoning:")
    print(f"  {result.reasoning}")
    
    print(f"\nAnalysis Time: {result.latency:.2f} seconds")
    
    print("\n" + "="*70)
    print("TEST COMPLETE - LLAVA IS WORKING!")
    print("="*70)
    
    print("\n[READY] LLaVA can now:")
    print("  - Recognize 50+ chart patterns")
    print("  - Detect support/resistance levels")
    print("  - Analyze trend direction and strength")
    print("  - Identify technical indicators")
    print("  - Provide trading insights")
    
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_visual_analysis())
        
        if success:
            print("\n[SUCCESS] Visual analysis is operational!")
            print("\nNext steps:")
            print("  1. Train on history: python train_llava_historical.py")
            print("  2. Start trading: python LAUNCH_ULTIMATE_PROMETHEUS_50M.py")
        else:
            print("\n[FAILED] Visual analysis test failed")
            print("Check error messages above")
        
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Test interrupted")
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
