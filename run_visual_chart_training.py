#!/usr/bin/env python3
"""
PROMETHEUS Visual Chart Training (Fixed)
=========================================
Trains visual AI on chart patterns using cloud vision API.
Fixes the API key tuple bug and clears failed patterns.

This script:
1. Clears all failed pattern entries
2. Re-analyzes all charts with the correct API configuration  
3. Saves results for the learning system
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root
sys.path.insert(0, str(Path(__file__).parent))


def get_api_config():
    """Get API configuration - returns dict with properly separated key and provider"""
    config = {
        'provider': None,
        'api_key': None,
        'model': None,
        'endpoint': None
    }
    
    # Check available keys (in order of preference)
    openai_key = os.getenv('OPENAI_API_KEY')
    glm_key = os.getenv('ZHIPUAI_API_KEY')
    gemini_key = os.getenv('GOOGLE_AI_API_KEY') or os.getenv('GEMINI_API_KEY')
    claude_key = os.getenv('ANTHROPIC_API_KEY')
    
    # Print available keys
    print("\n🔑 API Keys Status:")
    print(f"   {'✅' if openai_key else '❌'} OpenAI: {'Available' if openai_key else 'Not set'}")
    print(f"   {'✅' if glm_key else '❌'} GLM-4: {'Available' if glm_key else 'Not set'}")
    print(f"   {'✅' if gemini_key else '❌'} Gemini: {'Available' if gemini_key else 'Not set'}")
    print(f"   {'✅' if claude_key else '❌'} Claude: {'Available' if claude_key else 'Not set'}")
    
    # Select provider (OpenAI > GLM > Gemini > Claude)
    if openai_key:
        config['provider'] = 'openai'
        config['api_key'] = openai_key
        config['model'] = 'gpt-4o-mini'
        config['endpoint'] = 'https://api.openai.com/v1/chat/completions'
        print(f"\n🚀 Selected: OpenAI GPT-4o-mini")
    elif glm_key:
        config['provider'] = 'glm'
        config['api_key'] = glm_key
        config['model'] = 'glm-4v-flash'
        config['endpoint'] = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
        print(f"\n🚀 Selected: GLM-4-Flash")
    elif gemini_key:
        config['provider'] = 'gemini'
        config['api_key'] = gemini_key
        config['model'] = 'gemini-1.5-flash'
        config['endpoint'] = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
        print(f"\n🚀 Selected: Google Gemini 1.5 Flash")
    elif claude_key:
        config['provider'] = 'claude'
        config['api_key'] = claude_key
        config['model'] = 'claude-sonnet-4-20250514'
        config['endpoint'] = 'https://api.anthropic.com/v1/messages'
        print(f"\n🚀 Selected: Claude Sonnet 4")
    else:
        print(f"\n❌ No vision API keys found!")
        print(f"   Add one of these to .env file:")
        print(f"   - OPENAI_API_KEY")
        print(f"   - ZHIPUAI_API_KEY")
        print(f"   - GOOGLE_AI_API_KEY")
        print(f"   - ANTHROPIC_API_KEY")
        return None
    
    return config


def analyze_chart_openai(config, image_path, symbol):
    """Analyze chart using OpenAI Vision"""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {config["api_key"]}'
    }
    
    prompt = f"""Analyze this {symbol} stock/crypto chart for trading patterns.

Identify:
1. Chart patterns (head & shoulders, double top/bottom, triangles, flags, wedges, etc.)
2. Overall trend direction (bullish/bearish/neutral)
3. Trend strength (strong/moderate/weak)
4. Key support levels (price numbers)
5. Key resistance levels (price numbers)
6. Trading signal quality (strong/moderate/weak)

Respond in JSON format:
{{
    "patterns": ["pattern1", "pattern2"],
    "trend": "bullish/bearish/neutral",
    "trend_strength": "strong/moderate/weak",
    "support_levels": [100.0, 95.0],
    "resistance_levels": [110.0, 115.0],
    "signal_quality": "strong/moderate/weak",
    "confidence": 0.85,
    "reasoning": "brief analysis"
}}"""

    payload = {
        'model': config['model'],
        'messages': [
            {
                'role': 'user',
                'content': [
                    {'type': 'text', 'text': prompt},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/png;base64,{image_data}'
                        }
                    }
                ]
            }
        ],
        'max_tokens': 1024,
        'temperature': 0.2
    }
    
    response = requests.post(config['endpoint'], headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    
    result = response.json()
    text = result['choices'][0]['message']['content']
    return parse_analysis_response(text)


def analyze_chart_claude(config, image_path, symbol):
    """Analyze chart using Claude Vision"""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # FIXED: api_key must be a string, not a tuple!
    api_key = config['api_key']
    if isinstance(api_key, tuple):
        api_key = api_key[0]  # Take first element if accidentally a tuple
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key,  # Must be string!
        'anthropic-version': '2023-06-01'
    }
    
    prompt = f"""Analyze this {symbol} stock/crypto chart for trading patterns.

Identify:
1. Chart patterns (head & shoulders, double top/bottom, triangles, flags, wedges, etc.)
2. Overall trend direction (bullish/bearish/neutral)
3. Trend strength (strong/moderate/weak)
4. Key support levels (price numbers)
5. Key resistance levels (price numbers)
6. Trading signal quality (strong/moderate/weak)

Respond in JSON format:
{{
    "patterns": ["pattern1", "pattern2"],
    "trend": "bullish/bearish/neutral",
    "trend_strength": "strong/moderate/weak",
    "support_levels": [100.0, 95.0],
    "resistance_levels": [110.0, 115.0],
    "signal_quality": "strong/moderate/weak",
    "confidence": 0.85,
    "reasoning": "brief analysis"
}}"""

    payload = {
        'model': config['model'],
        'max_tokens': 1024,
        'messages': [
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/png',
                            'data': image_data
                        }
                    },
                    {
                        'type': 'text',
                        'text': prompt
                    }
                ]
            }
        ]
    }
    
    response = requests.post(config['endpoint'], headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    
    result = response.json()
    text = result['content'][0]['text']
    return parse_analysis_response(text)


def analyze_chart_gemini(config, image_path, symbol):
    """Analyze chart using Gemini Vision"""
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = f"""Analyze this {symbol} stock/crypto chart for trading patterns.

Identify:
1. Chart patterns (head & shoulders, double top/bottom, triangles, flags, wedges, etc.)
2. Overall trend direction (bullish/bearish/neutral)
3. Trend strength (strong/moderate/weak)
4. Key support levels (price numbers)
5. Key resistance levels (price numbers)
6. Trading signal quality (strong/moderate/weak)

Respond in JSON format:
{{
    "patterns": ["pattern1", "pattern2"],
    "trend": "bullish/bearish/neutral",
    "trend_strength": "strong/moderate/weak",
    "support_levels": [100.0, 95.0],
    "resistance_levels": [110.0, 115.0],
    "signal_quality": "strong/moderate/weak",
    "confidence": 0.85,
    "reasoning": "brief analysis"
}}"""

    headers = {'Content-Type': 'application/json'}
    
    payload = {
        'contents': [{
            'parts': [
                {'text': prompt},
                {
                    'inline_data': {
                        'mime_type': 'image/png',
                        'data': image_data
                    }
                }
            ]
        }],
        'generationConfig': {
            'temperature': 0.2,
            'maxOutputTokens': 1024
        }
    }
    
    url = f"{config['endpoint']}?key={config['api_key']}"
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    
    result = response.json()
    text = result['candidates'][0]['content']['parts'][0]['text']
    return parse_analysis_response(text)


def parse_analysis_response(text):
    """Parse JSON response from any provider"""
    import re
    
    # Try to extract JSON from response
    try:
        # Look for JSON block
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            data = json.loads(json_match.group())
            return {
                'patterns': data.get('patterns', []),
                'trend': data.get('trend', 'neutral'),
                'trend_strength': data.get('trend_strength', 'weak'),
                'support_levels': data.get('support_levels', []),
                'resistance_levels': data.get('resistance_levels', []),
                'signal_quality': data.get('signal_quality', 'weak'),
                'confidence': data.get('confidence', 0.5),
                'reasoning': data.get('reasoning', text[:200]),
                'success': True
            }
    except json.JSONDecodeError:
        pass
    
    # Fallback - try to parse text
    return {
        'patterns': [],
        'trend': 'neutral',
        'trend_strength': 'weak',
        'support_levels': [],
        'resistance_levels': [],
        'signal_quality': 'weak',
        'confidence': 0.3,
        'reasoning': text[:200] if text else 'Failed to parse response',
        'success': False
    }


def analyze_chart(config, image_path, symbol):
    """Analyze chart using configured provider"""
    provider = config['provider']
    
    if provider == 'openai':
        return analyze_chart_openai(config, image_path, symbol)
    elif provider == 'claude':
        return analyze_chart_claude(config, image_path, symbol)
    elif provider == 'gemini':
        return analyze_chart_gemini(config, image_path, symbol)
    elif provider == 'glm':
        # GLM uses OpenAI-compatible API
        return analyze_chart_openai(config, image_path, symbol)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def save_results(results, pattern_summary, output_file='visual_ai_patterns.json'):
    """Save results to JSON"""
    output = {
        'last_updated': datetime.now().isoformat(),
        'total_analyzed': len(results),
        'successful_analyses': sum(1 for r in results.values() if r.get('success', False)),
        'total_patterns': sum(len(r.get('patterns', [])) for r in results.values()),
        'patterns': results,
        'pattern_summary': pattern_summary
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Also save to cloud file
    with open('visual_ai_patterns_cloud.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    return output


def main():
    print("\n" + "="*70)
    print("🎨 PROMETHEUS Visual Chart Training (Fixed)")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get API configuration
    config = get_api_config()
    if not config:
        return
    
    # Find all chart directories
    chart_dirs = []
    
    # Main charts directory
    charts_dir = Path('charts')
    if charts_dir.exists():
        chart_dirs.append(charts_dir)
    
    # Paper trading charts
    paper_charts = Path('paper_trading_charts')
    if paper_charts.exists():
        chart_dirs.append(paper_charts)
    
    # Collect all charts
    all_charts = []
    for chart_dir in chart_dirs:
        all_charts.extend(list(chart_dir.glob('*.png')))
    
    print(f"\n📊 Found {len(all_charts)} charts to analyze")
    
    if not all_charts:
        print("❌ No charts found!")
        return
    
    # Load existing results and clear failed ones
    patterns_file = Path('visual_ai_patterns.json')
    existing_results = {}
    
    if patterns_file.exists():
        try:
            with open(patterns_file, 'r') as f:
                data = json.load(f)
                old_patterns = data.get('patterns', {})
                
                # Keep only successful analyses
                for name, result in old_patterns.items():
                    if result.get('success', False) and 'Error' not in result.get('reasoning', ''):
                        existing_results[name] = result
                
                print(f"📂 Loaded {len(old_patterns)} existing patterns")
                print(f"✅ Keeping {len(existing_results)} successful analyses")
                print(f"🗑️  Cleared {len(old_patterns) - len(existing_results)} failed analyses")
        except Exception as e:
            print(f"⚠️ Could not load existing patterns: {e}")
    
    # Filter charts to those needing analysis
    charts_to_analyze = [c for c in all_charts if c.name not in existing_results]
    
    print(f"\n📋 Charts needing analysis: {len(charts_to_analyze)}")
    
    if not charts_to_analyze:
        print("✅ All charts already successfully analyzed!")
        return
    
    # Estimate time and cost
    est_time = len(charts_to_analyze) * 3 / 60  # ~3 seconds per chart
    est_cost = len(charts_to_analyze) * 0.002  # ~$0.002 per image
    
    print(f"\n📊 Analysis Plan:")
    print(f"   ⏱️  Estimated time: {est_time:.1f} minutes")
    print(f"   💰 Estimated cost: ${est_cost:.2f}")
    
    confirm = input("\nProceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    # Analyze charts
    results = existing_results.copy()
    pattern_counts = {}
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    print("\n" + "-"*70)
    print("Starting analysis...")
    print("-"*70 + "\n")
    
    for i, chart_path in enumerate(charts_to_analyze, 1):
        filename = chart_path.name
        symbol = filename.split('_')[0]
        
        try:
            print(f"[{i}/{len(charts_to_analyze)}] 🔬 {filename}...", end=" ", flush=True)
            
            analysis = analyze_chart(config, str(chart_path), symbol)
            
            results[filename] = {
                'patterns': analysis['patterns'],
                'trend': analysis['trend'],
                'trend_strength': analysis['trend_strength'],
                'support': analysis['support_levels'],
                'resistance': analysis['resistance_levels'],
                'confidence': analysis['confidence'],
                'signal': analysis['signal_quality'],
                'reasoning': analysis['reasoning'],
                'analyzed_at': datetime.now().isoformat(),
                'success': analysis['success']
            }
            
            if analysis['success']:
                success_count += 1
                for p in analysis['patterns']:
                    pattern_counts[p] = pattern_counts.get(p, 0) + 1
                print(f"✅ {len(analysis['patterns'])} patterns, {analysis['trend']}")
            else:
                error_count += 1
                print(f"⚠️ Parse failed")
            
            # Rate limit
            time.sleep(1.0)
            
            # Save every 10 charts
            if i % 10 == 0:
                save_results(results, pattern_counts)
                elapsed = time.time() - start_time
                rate = i / (elapsed / 60) if elapsed > 0 else 0
                print(f"\n   💾 Saved. Progress: {i}/{len(charts_to_analyze)}, Rate: {rate:.1f}/min\n")
                
        except Exception as e:
            error_count += 1
            results[filename] = {
                'patterns': [],
                'trend': 'neutral',
                'trend_strength': 'weak',
                'support': [],
                'resistance': [],
                'confidence': 0.0,
                'signal': 'weak',
                'reasoning': f'Error: {str(e)[:100]}',
                'analyzed_at': datetime.now().isoformat(),
                'success': False
            }
            print(f"❌ Error: {str(e)[:50]}")
            time.sleep(2.0)  # Back off on errors
    
    # Final save
    save_results(results, pattern_counts)
    
    # Summary
    elapsed = time.time() - start_time
    total_patterns = sum(len(r.get('patterns', [])) for r in results.values())
    
    print("\n" + "="*70)
    print("📊 VISUAL CHART TRAINING COMPLETE")
    print("="*70)
    print(f"✅ Total charts analyzed: {len(results)}")
    print(f"✅ Successful this session: {success_count}")
    print(f"❌ Errors this session: {error_count}")
    print(f"🎯 Total patterns detected: {total_patterns}")
    print(f"⏱️  Time elapsed: {elapsed/60:.1f} minutes")
    
    if pattern_counts:
        print(f"\n📈 Top Patterns Detected:")
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"   {pattern}: {count}")
    
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Training interrupted. Progress saved.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
