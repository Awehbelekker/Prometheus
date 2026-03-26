#!/usr/bin/env python3
"""
Analyze 32 Paper Trading Charts
Expand crypto/forex pattern coverage & improve signal confidence
Works with Gemini (since GLM API key not yet added)
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.cloud_vision_analyzer import CloudVisionAnalyzer, CloudVisionConfig

def main():
    """Analyze all charts in paper_trading_charts/ directory"""
    
    print("\n" + "="*70)
    print("  📊 PROMETHEUS CHART ANALYSIS - Expand Pattern Coverage")
    print("="*70)
    
    # Check for charts
    charts_dir = project_root / "paper_trading_charts"
    if not charts_dir.exists():
        print(f"\n❌ ERROR: Directory not found: {charts_dir}")
        return
    
    chart_files = list(charts_dir.glob("*.png"))
    if not chart_files:
        print(f"\n❌ ERROR: No PNG files found in {charts_dir}")
        return
    
    print(f"\n📁 Found {len(chart_files)} charts to analyze")
    print(f"   📂 Directory: {charts_dir}")
    
    # Check API keys
    has_gemini = bool(os.getenv('GOOGLE_AI_API_KEY'))
    has_glm = bool(os.getenv('ZHIPUAI_API_KEY')) and os.getenv('ZHIPUAI_API_KEY') != 'your_zhipu_api_key_here'
    has_claude = bool(os.getenv('ANTHROPIC_API_KEY'))
    has_openai = bool(os.getenv('OPENAI_API_KEY')) and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'
    
    print(f"\n🔑 API Key Status:")
    print(f"   {'✅' if has_openai else '❌'} OpenAI GPT-4o-mini: {'Available' if has_openai else 'Missing'}")
    print(f"   {'✅' if has_gemini else '❌'} Google Gemini: {'Available' if has_gemini else 'Missing'}")
    print(f"   {'✅' if has_glm else '❌'} GLM-4-Flash: {'Available' if has_glm else 'Missing/Placeholder'}")
    print(f"   {'✅' if has_claude else '❌'} Claude: {'Available' if has_claude else 'Missing'}")
    
    # Determine provider - prioritize OpenAI (user chose this option)
    if has_openai:
        provider = "openai"
        model = "gpt-4o-mini"
        print(f"\n🚀 Using: OpenAI GPT-4o-mini (user selected)")
    elif has_glm:
        provider = "glm"
        model = "glm-4v-flash"
        print(f"\n🚀 Using: GLM-4-Flash (fastest, cheapest)")
    elif has_gemini:
        provider = "google"
        model = "gemini-2.0-flash-exp"
        print(f"\n🚀 Using: Google Gemini (may hit rate limits)")
    elif has_claude:
        provider = "claude"
        model = "claude-sonnet-4-20250514"
        print(f"\n🚀 Using: Anthropic Claude Sonnet 4")
    else:
        print(f"\n❌ ERROR: No vision API keys available!")
        print(f"\n💡 SOLUTION: Add at least one API key to .env file:")
        print(f"   • OPENAI_API_KEY=your_key_here (GPT-4o-mini - RECOMMENDED)")
        print(f"   • ZHIPUAI_API_KEY=your_key_here (GLM-4-Flash)")
        print(f"   • GOOGLE_AI_API_KEY=your_key_here (Gemini)")
        print(f"   • ANTHROPIC_API_KEY=your_key_here (Claude)")
        return
    
    # Initialize analyzer
    config = CloudVisionConfig(
        provider=provider,
        model=model,
        batch_delay=2.0 if provider == "google" else 1.0  # Slower for Gemini
    )
    
    analyzer = CloudVisionAnalyzer(config)
    batch_size = 5  # Process 5 at a time
    
    print(f"\n⚙️  Configuration:")
    print(f"   🔹 Provider: {provider}")
    print(f"   🔹 Model: {model}")
    print(f"   🔹 Batch Size: {batch_size}")
    print(f"   🔹 Batch Delay: {config.batch_delay}s")
    
    estimated_cost = len(chart_files) * 0.002  # ~$0.002 per image
    estimated_time = (len(chart_files) / batch_size) * (config.batch_delay + 3)
    
    print(f"\n📊 Analysis Plan:")
    print(f"   📈 Total Charts: {len(chart_files)}")
    print(f"   ⏱️  Estimated Time: {estimated_time/60:.1f} minutes")
    print(f"   💰 Estimated Cost: ${estimated_cost:.3f}")
    
    # Group by symbol
    symbol_groups = {}
    for chart_file in chart_files:
        symbol = chart_file.name.split('_')[0]
        if symbol not in symbol_groups:
            symbol_groups[symbol] = []
        symbol_groups[symbol].append(chart_file)
    
    print(f"\n📊 Charts by Symbol:")
    for symbol, charts in sorted(symbol_groups.items()):
        print(f"   {symbol}: {len(charts)} charts")
    
    # Confirm
    print(f"\n⚠️  Ready to analyze {len(chart_files)} charts")
    response = input("   Continue? (y/n): ").strip().lower()
    
    if response != 'y':
        print("\n❌ Analysis cancelled")
        return
    
    # Analyze charts
    print(f"\n🔄 Starting analysis...\n")
    results = []
    total_patterns = 0
    
    for i, chart_file in enumerate(chart_files, 1):
        print(f"   [{i}/{len(chart_files)}] Analyzing {chart_file.name}...", end=" ")
        
        try:
            # Extract symbol from filename (e.g., "AAPL_entry_AAPL_BUY_1768103134.png" -> "AAPL")
            symbol = chart_file.name.split('_')[0]
            
            # Analyze (pass path, not bytes)
            result = analyzer.analyze_chart(str(chart_file), symbol)
            
            # ChartAnalysisResult is a dataclass, not a dict
            if result and result.success:
                patterns = result.patterns_detected
                total_patterns += len(patterns)
                
                results.append({
                    'file': chart_file.name,
                    'symbol': chart_file.name.split('_')[0],
                    'patterns': patterns,
                    'trend': result.trend_direction,
                    'trend_strength': result.trend_strength,
                    'confidence': result.confidence,
                    'support_levels': result.support_levels,
                    'resistance_levels': result.resistance_levels,
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"✅ {len(patterns)} patterns")
            else:
                print(f"⚠️  No patterns detected")
            
            # Rate limit pause
            if i % batch_size == 0 and i < len(chart_files):
                print(f"   ⏸️  Batch complete, waiting {config.batch_delay}s...")
                import time
                time.sleep(config.batch_delay)
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Save results
    results_file = project_root / f"chart_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'analysis_date': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'total_charts': len(chart_files),
            'total_patterns': total_patterns,
            'results': results
        }, f, indent=2)
    
    # Summary
    print(f"\n" + "="*70)
    print(f"  ✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n📊 Results:")
    print(f"   ✅ Charts Analyzed: {len(results)}/{len(chart_files)}")
    print(f"   🔍 Total Patterns: {total_patterns}")
    print(f"   📈 Avg Patterns/Chart: {total_patterns/len(results):.1f}" if results else "   📈 Avg Patterns/Chart: 0")
    
    # Pattern breakdown
    if total_patterns > 0:
        all_patterns = []
        for r in results:
            all_patterns.extend([p['pattern'] for p in r['patterns']])
        
        from collections import Counter
        pattern_counts = Counter(all_patterns)
        
        print(f"\n🔍 Pattern Distribution:")
        for pattern, count in pattern_counts.most_common():
            print(f"   {pattern}: {count}")
    
    print(f"\n📁 Results saved: {results_file.name}")
    
    # Next steps
    print(f"\n💡 NEXT STEPS:")
    if total_patterns > 0:
        print(f"   ✅ New patterns discovered!")
        print(f"   📊 Add these to visual_ai_patterns_cloud.json")
        print(f"   🚀 Run extended trading session to test improved signals")
    else:
        print(f"   ⚠️  No new patterns found")
        if not has_glm:
            print(f"   💡 Try GLM-4-Flash API for better pattern detection")
            print(f"   📋 See: GLM_API_SETUP_GUIDE.md")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
