#!/usr/bin/env python3
"""
🎯 Train Visual AI on Paper Trading Charts
Analyze the charts captured during paper trading to see what patterns exist
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from core.cloud_vision_analyzer import CloudVisionAnalyzer, CloudVisionConfig


def train_on_paper_trading_charts():
    """Train Visual AI on newly captured paper trading charts"""
    
    print("\n" + "="*80)
    print("🎯 VISUAL AI TRAINING - Paper Trading Charts")
    print("="*80)
    
    # Find paper trading charts
    charts_dir = Path("paper_trading_charts")
    if not charts_dir.exists():
        print("❌ No paper trading charts found!")
        print("   Run: python internal_realworld_paper_trading.py")
        return
    
    charts = list(charts_dir.glob("*.png"))
    print(f"\n📊 Found {len(charts)} paper trading charts")
    
    if not charts:
        print("❌ No charts to analyze!")
        return
    
    # Load existing Visual AI patterns
    patterns_file = Path("visual_ai_patterns_cloud.json")
    existing_patterns = {}
    
    if patterns_file.exists():
        with open(patterns_file, 'r') as f:
            data = json.load(f)
            existing_patterns = data.get('patterns', {})
            print(f"📂 Loaded {len(existing_patterns)} existing patterns")
    
    # Initialize analyzer
    config = CloudVisionConfig()
    analyzer = CloudVisionAnalyzer(config)
    
    if not analyzer.api_available:
        print("\n⚠️ Visual AI API not available!")
        print("   Set GOOGLE_AI_API_KEY or ANTHROPIC_API_KEY in .env")
        return
    
    print(f"\n🔬 Analyzing {len(charts)} new charts...")
    print(f"⏱️  Estimated time: {len(charts) * 3 / 60:.1f} minutes")
    print(f"💰 Estimated cost: ${len(charts) * 0.002:.2f}")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    # Analyze each chart
    new_patterns = {}
    pattern_count = 0
    
    for i, chart_path in enumerate(charts, 1):
        filename = chart_path.name
        
        # Skip if already analyzed
        if filename in existing_patterns:
            print(f"[{i}/{len(charts)}] ⏭️  Skipped (already analyzed): {filename}")
            continue
        
        # Extract symbol from filename (e.g., "AAPL_entry_...")
        symbol = filename.split('_')[0]
        
        try:
            print(f"[{i}/{len(charts)}] 🔬 Analyzing: {filename}")
            
            result = analyzer.analyze_chart(str(chart_path), symbol)
            
            # Convert result to dict
            patterns_found = result.patterns_detected if hasattr(result, 'patterns_detected') else []
            
            new_patterns[filename] = {
                'patterns': patterns_found,
                'trend': result.trend_direction if hasattr(result, 'trend_direction') else 'unknown',
                'trend_strength': result.trend_strength if hasattr(result, 'trend_strength') else 'weak',
                'support': result.support_levels if hasattr(result, 'support_levels') else [],
                'resistance': result.resistance_levels if hasattr(result, 'resistance_levels') else [],
                'confidence': result.confidence if hasattr(result, 'confidence') else 0.0,
                'signal': result.signal if hasattr(result, 'signal') else 'neutral',
                'reasoning': result.reasoning if hasattr(result, 'reasoning') else '',
                'analyzed_at': datetime.now().isoformat(),
                'analysis_time': 0.0,
                'success': True
            }
            
            pattern_count += len(patterns_found)
            
            if patterns_found:
                print(f"   ✅ Found {len(patterns_found)} patterns: {', '.join(patterns_found[:3])}")
            else:
                print(f"   ℹ️  No patterns detected")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            new_patterns[filename] = {
                'patterns': [],
                'trend': 'neutral',
                'success': False,
                'reasoning': str(e)
            }
    
    # Merge with existing patterns
    all_patterns = {**existing_patterns, **new_patterns}
    
    # Build pattern summary
    pattern_summary = {}
    for data in all_patterns.values():
        for p in data.get('patterns', []):
            pattern_summary[p] = pattern_summary.get(p, 0) + 1
    
    # Save results
    output = {
        'last_updated': datetime.now().isoformat(),
        'provider': 'gemini',
        'model': 'gemini-1.5-flash',
        'total_analyzed': len(all_patterns),
        'total_patterns': pattern_count,
        'patterns': all_patterns,
        'pattern_summary': pattern_summary
    }
    
    # Save to main file
    with open('visual_ai_patterns_cloud.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETE")
    print("="*80)
    print(f"\n📊 Results:")
    print(f"   New charts analyzed: {len(new_patterns)}")
    print(f"   New patterns found: {pattern_count}")
    print(f"   Total patterns in database: {sum(pattern_summary.values())}")
    
    if pattern_summary:
        print(f"\n🏆 Top Patterns (Overall):")
        for pattern, count in sorted(pattern_summary.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {pattern:<40} | {count:>4}x")
    
    print(f"\n💾 Saved to: visual_ai_patterns_cloud.json")
    print(f"📂 Also updated: visual_ai_patterns.json")
    
    # Also save to visual_ai_patterns.json
    with open('visual_ai_patterns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n✅ Visual AI training complete!")
    print("🔄 Next: Run validation to see what we learned!")


if __name__ == "__main__":
    train_on_paper_trading_charts()
