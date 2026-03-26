#!/usr/bin/env python3
"""
PROMETHEUS Cloud Vision Training Script

Analyzes all charts using Claude Vision API (or Gemini as fallback).
Stores results for PROMETHEUS learning system.

Usage:
    1. Set ANTHROPIC_API_KEY environment variable (or GOOGLE_AI_API_KEY)
    2. Run: python CLOUD_VISION_TRAINING.py

Cost: ~$0.005 per image (~$6.60 for 1,320 charts with Claude)
Speed: ~2-4 seconds per image
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.cloud_vision_analyzer import CloudVisionAnalyzer, CloudVisionConfig


def get_api_key():
    """Get API key from environment - prefer Claude, fallback to Gemini"""
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    gemini_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')

    if claude_key:
        print("✅ Using Claude Vision API (Anthropic)")
        return claude_key, "claude"
    elif gemini_key:
        print("✅ Using Gemini Vision API (Google)")
        return gemini_key, "gemini"
    else:
        print("\n" + "="*60)
        print("🔑 API KEY REQUIRED")
        print("="*60)
        print("\nSet one of these in your .env file:")
        print("  - ANTHROPIC_API_KEY (preferred - Claude)")
        print("  - GOOGLE_AI_API_KEY (fallback - Gemini)")
        return None, None


def load_existing_results():
    """Load any existing results to resume"""
    results_file = Path('visual_ai_patterns_cloud.json')
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
                return data.get('patterns', {})
        except:
            pass
    return {}


def save_results(results: dict, total_patterns: int):
    """Save results to JSON"""
    # Build pattern summary
    pattern_summary = {}
    for data in results.values():
        for p in data.get('patterns', []):
            pattern_summary[p] = pattern_summary.get(p, 0) + 1
    
    output = {
        'last_updated': datetime.now().isoformat(),
        'provider': 'gemini',
        'model': 'gemini-1.5-flash',
        'total_analyzed': len(results),
        'total_patterns': total_patterns,
        'patterns': results,
        'pattern_summary': pattern_summary
    }
    
    # Save main file
    with open('visual_ai_patterns_cloud.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    # Also update main patterns file
    with open('visual_ai_patterns.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    return pattern_summary


def print_progress(current, total, result):
    """Print progress bar"""
    pct = current / total * 100
    bar_len = 30
    filled = int(bar_len * current / total)
    bar = "█" * filled + "░" * (bar_len - filled)
    
    status = "✅" if result.success else "❌"
    patterns = len(result.patterns_detected)
    
    print(f"\r[{bar}] {pct:5.1f}% ({current}/{total}) {status} P:{patterns}", end="", flush=True)


def main():
    print("\n" + "="*60)
    print("☁️  PROMETHEUS CLOUD VISION TRAINING")
    print("="*60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get API key
    api_key, provider = get_api_key()
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Find charts
    charts_dir = Path('charts')
    if not charts_dir.exists():
        print(f"❌ Charts directory not found: {charts_dir}")
        return
    
    charts = sorted(charts_dir.glob('*.png'))
    print(f"\n📊 Found {len(charts)} charts to analyze")
    
    # Load existing results
    results = load_existing_results()
    already_done = set(results.keys())
    
    # Filter to charts not yet analyzed
    remaining = [c for c in charts if c.name not in already_done]
    print(f"📋 Already analyzed: {len(already_done)}")
    print(f"📋 Remaining: {len(remaining)}")
    
    if not remaining:
        print("\n✅ All charts already analyzed!")
        return
    
    # Estimate cost and time
    est_cost = len(remaining) * 0.002
    est_time = len(remaining) * 4 / 60  # 4 seconds per image
    print(f"\n💰 Estimated cost: ${est_cost:.2f}")
    print(f"⏱️  Estimated time: {est_time:.1f} minutes")

    # Confirm
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return

    # Initialize analyzer
    config = CloudVisionConfig(api_key=api_key, provider=provider)
    analyzer = CloudVisionAnalyzer(config)

    if not analyzer.api_available:
        print("❌ API not available. Check your key.")
        return

    # Process charts
    print("\n" + "-"*60)
    print("Starting analysis...")
    print("-"*60 + "\n")

    total_patterns = sum(len(r.get('patterns', [])) for r in results.values())
    start_time = time.time()
    errors = 0

    for i, chart_path in enumerate(remaining, 1):
        filename = chart_path.name

        # Extract symbol from filename
        symbol = filename.split('_')[0] if '_' in filename else "UNKNOWN"

        # Analyze
        result = analyzer.analyze_chart(str(chart_path), symbol)

        # Store result
        results[filename] = {
            'patterns': result.patterns_detected,
            'trend': result.trend_direction,
            'trend_strength': result.trend_strength,
            'support': result.support_levels,
            'resistance': result.resistance_levels,
            'confidence': result.confidence,
            'signal': result.signal_quality,
            'reasoning': result.reasoning,
            'analyzed_at': datetime.now().isoformat(),
            'analysis_time': result.latency,
            'success': result.success
        }

        if result.success:
            total_patterns += len(result.patterns_detected)
        else:
            errors += 1

        # Progress
        print_progress(i, len(remaining), result)

        # Save every 10 charts
        if i % 10 == 0:
            pattern_summary = save_results(results, total_patterns)
            elapsed = time.time() - start_time
            rate = i / (elapsed / 60)
            print(f"\n   💾 Saved. {i}/{len(remaining)} done. {rate:.1f}/min. "
                  f"Patterns: {total_patterns}")

    # Final save
    print("\n\n" + "="*60)
    print("📊 TRAINING COMPLETE")
    print("="*60)

    pattern_summary = save_results(results, total_patterns)

    elapsed = time.time() - start_time
    stats = analyzer.get_stats()

    print(f"\n✅ Analyzed: {len(remaining)} charts")
    print(f"⏱️  Time: {elapsed/60:.1f} minutes")
    print(f"📈 Total patterns found: {total_patterns}")
    print(f"❌ Errors: {errors}")
    print(f"💰 Estimated cost: ${len(remaining) * 0.002:.2f}")

    if pattern_summary:
        print("\n📋 Pattern Summary:")
        sorted_patterns = sorted(pattern_summary.items(), key=lambda x: -x[1])
        for pattern, count in sorted_patterns[:15]:
            print(f"   {pattern}: {count}")

    print(f"\n💾 Results saved to: visual_ai_patterns.json")
    print(f"💾 Backup saved to: visual_ai_patterns_cloud.json")


if __name__ == "__main__":
    main()

