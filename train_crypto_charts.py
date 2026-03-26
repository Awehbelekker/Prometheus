#!/usr/bin/env python3
"""
Quick Crypto Chart Training Script
Analyzes only crypto charts using OpenAI GPT-4V (fastest option)
"""

import os
import sys
import json
import time
import base64
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import openai

load_dotenv()

# Configuration
CRYPTO_PREFIXES = ['BTC', 'ETH', 'SOL', 'DOGE', 'AVAX', 'LINK', 'ADA', 'XRP', 'DOT', 'LTC', 'ATOM', 'MATIC']
CHARTS_DIR = 'charts'
OUTPUT_FILE = 'visual_ai_patterns.json'

def get_crypto_charts():
    """Get all crypto chart files"""
    charts = []
    for f in os.listdir(CHARTS_DIR):
        if f.endswith('.png') and any(f.startswith(p + '_') for p in CRYPTO_PREFIXES):
            charts.append(f)
    return charts

def analyze_chart(client, chart_path):
    """Analyze a single chart using GPT-4V"""
    with open(chart_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = """Analyze this cryptocurrency price chart. Identify:
1. Chart patterns (Head & Shoulders, Double Top/Bottom, Triangles, Wedges, etc.)
2. Trend direction (bullish, bearish, neutral)
3. Key support/resistance levels
4. Overall sentiment (1-10)

Return JSON only:
{"patterns": [{"name": "pattern", "confidence": 0.0-1.0}], "trend": "bullish/bearish/neutral", "sentiment": 1-10, "support": [], "resistance": []}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                ]}
            ],
            max_tokens=500,
            temperature=0.2
        )
        
        content = response.choices[0].message.content
        # Extract JSON from response
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        
        return json.loads(content.strip())
    except Exception as e:
        print(f"    Error: {e}")
        return None

def main():
    print("=" * 60)
    print("PROMETHEUS Crypto Chart Training")
    print("=" * 60)

    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set in .env")
        return

    client = openai.OpenAI(api_key=api_key)

    # Get crypto charts
    charts = get_crypto_charts()
    print(f"\nFound {len(charts)} crypto charts to analyze")
    
    # Load existing patterns
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = {'patterns': {}, 'last_updated': '', 'total_analyzed': 0}
    
    # Analyze each chart
    analyzed = 0
    for i, chart in enumerate(charts):
        # Skip if already analyzed
        if chart in data.get('patterns', {}):
            print(f"  [{i+1}/{len(charts)}] {chart} - Already analyzed, skipping")
            continue
        
        print(f"  [{i+1}/{len(charts)}] Analyzing {chart}...")
        
        result = analyze_chart(client, os.path.join(CHARTS_DIR, chart))
        
        if result:
            data['patterns'][chart] = {
                'analyzed_at': datetime.now().isoformat(),
                'patterns_detected': result.get('patterns', []),
                'trend': result.get('trend', 'neutral'),
                'sentiment': result.get('sentiment', 5),
                'support': result.get('support', []),
                'resistance': result.get('resistance', [])
            }
            analyzed += 1
            print(f"    OK: {result.get('trend', 'neutral')} - {len(result.get('patterns', []))} patterns")

        # Rate limiting
        time.sleep(0.5)

        # Save progress every 10 charts
        if analyzed % 10 == 0:
            data['last_updated'] = datetime.now().isoformat()
            data['total_analyzed'] = len(data.get('patterns', {}))
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"    Progress saved ({analyzed} new charts)")

    # Final save
    data['last_updated'] = datetime.now().isoformat()
    data['total_analyzed'] = len(data.get('patterns', {}))
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print("\n" + "=" * 60)
    print(f"Analyzed {analyzed} new crypto charts")
    print(f"Total patterns in database: {data['total_analyzed']}")
    print("=" * 60)

if __name__ == "__main__":
    main()

