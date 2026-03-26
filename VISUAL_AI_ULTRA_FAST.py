"""
PROMETHEUS Visual AI - ULTRA FAST Training
==========================================
Maximum speed optimizations:
- Smallest model (llava:7b at 4.4GB)
- Tiny images (384px)
- Minimal prompt
- Short timeout (60s)
- Direct API calls
"""

import os
import sys
import json
import time
import base64
import requests
from datetime import datetime
from pathlib import Path

# Try to import PIL, fallback to basic
try:
    from PIL import Image
    import io
    HAS_PIL = True
except:
    HAS_PIL = False

print("=" * 50)
print("ULTRA FAST VISUAL AI TRAINING")
print("=" * 50)

# Configuration - ULTRA OPTIMIZED
OLLAMA_URL = "http://localhost:11434"
MODEL = "llava:7b"  # Smallest vision model
TIMEOUT = 60  # 1 minute max
IMAGE_SIZE = 384  # Small images

# Super simple prompt - just get trend
PROMPT = "What is the trend? Reply with ONE word: BULLISH, BEARISH, or NEUTRAL"


def load_image(path):
    """Load and resize image"""
    if HAS_PIL:
        try:
            with Image.open(path) as img:
                # Resize small
                if max(img.size) > IMAGE_SIZE:
                    ratio = IMAGE_SIZE / max(img.size)
                    new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                    img = img.resize(new_size, Image.LANCZOS)
                buf = io.BytesIO()
                img.save(buf, format='PNG', optimize=True)
                return base64.b64encode(buf.getvalue()).decode()
        except:
            pass
    
    # Fallback
    with open(path, 'rb') as f:
        return base64.b64encode(f.read()).decode()


def analyze(image_path):
    """Ultra fast analysis"""
    img_data = load_image(image_path)
    
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "images": [img_data],
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 20,  # Very short response
            "num_ctx": 1024,   # Small context
        }
    }
    
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            response = r.json().get('response', '').upper()
            if 'BULLISH' in response:
                return {'trend': 'bullish', 'confidence': 0.7}
            elif 'BEARISH' in response:
                return {'trend': 'bearish', 'confidence': 0.7}
            else:
                return {'trend': 'neutral', 'confidence': 0.5}
    except:
        pass
    return None


def main():
    print(f"Model: {MODEL} (4.4GB - smallest)")
    print(f"Image: {IMAGE_SIZE}px (tiny)")
    print(f"Timeout: {TIMEOUT}s")
    print()
    
    # Find charts
    charts = list(Path("charts").glob("*.png"))
    print(f"Total charts: {len(charts)}")
    
    # Load existing
    results = {}
    if Path("visual_ai_patterns.json").exists():
        try:
            with open("visual_ai_patterns.json") as f:
                data = json.load(f)
                for k, v in data.get('patterns', {}).items():
                    if v.get('confidence', 0) > 0.3:
                        results[k] = v
        except:
            pass
    
    print(f"Already done: {len(results)}")
    
    to_do = [c for c in charts if c.name not in results]
    print(f"To process: {len(to_do)}")
    print()
    
    if not to_do:
        print("All done!")
        return
    
    # Process
    start = time.time()
    ok = 0
    fail = 0
    
    for i, chart in enumerate(to_do, 1):
        symbol = chart.stem.split('_')[0]
        t0 = time.time()
        
        result = analyze(str(chart))
        elapsed = time.time() - t0
        
        if result:
            ok += 1
            results[chart.name] = {
                'patterns': [],
                'trend': result['trend'],
                'trend_strength': 'medium',
                'support': [],
                'resistance': [],
                'confidence': result['confidence'],
                'analyzed_at': datetime.now().isoformat()
            }
            print(f"[{i}/{len(to_do)}] {symbol}: {result['trend']} ({elapsed:.1f}s) OK")
        else:
            fail += 1
            results[chart.name] = {
                'patterns': [],
                'trend': 'neutral',
                'trend_strength': 'weak',
                'support': [],
                'resistance': [],
                'confidence': 0.0,
                'analyzed_at': datetime.now().isoformat()
            }
            print(f"[{i}/{len(to_do)}] {symbol}: TIMEOUT ({elapsed:.1f}s)")
        
        # Save every 10
        if i % 10 == 0:
            with open("visual_ai_patterns.json", 'w') as f:
                json.dump({
                    'last_updated': datetime.now().isoformat(),
                    'total_analyzed': len(results),
                    'total_patterns': 0,
                    'patterns': results,
                    'pattern_summary': {}
                }, f, indent=2)
            rate = i / ((time.time() - start) / 60)
            print(f"   -- Saved. {ok}/{i} success, {rate:.1f}/min --")
    
    # Final save
    with open("visual_ai_patterns.json", 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'total_analyzed': len(results),
            'total_patterns': 0,
            'patterns': results,
            'pattern_summary': {}
        }, f, indent=2)
    
    total_time = (time.time() - start) / 60
    print()
    print("=" * 50)
    print("DONE!")
    print(f"Success: {ok}/{len(to_do)} ({ok/len(to_do)*100:.0f}%)")
    print(f"Time: {total_time:.1f} min")
    print(f"Rate: {len(to_do)/total_time:.1f} charts/min")
    print("=" * 50)


if __name__ == "__main__":
    main()
