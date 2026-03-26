"""
PROMETHEUS Visual AI - MAXIMUM SPEED Training
==============================================
Optimized for fastest possible processing
- Uses llama3.2-vision (faster than llava:7b)
- Reduced image size for faster processing
- Simplified prompts for quicker responses
- Parallel-ready architecture
"""

import os
import sys
import json
import time
import base64
import logging
import requests
from datetime import datetime
from pathlib import Path
from PIL import Image
import io

# Set MAXIMUM priority
try:
    import psutil
    p = psutil.Process(os.getpid())
    p.nice(psutil.REALTIME_PRIORITY_CLASS)  # Highest priority
    print("[OK] Process set to REALTIME PRIORITY")
except:
    try:
        import psutil
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        print("[OK] Process set to HIGH PRIORITY")
    except:
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('visual_ai_speed_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration - OPTIMIZED FOR SPEED
OLLAMA_URL = "http://localhost:11434"
MODEL = "llama3.2-vision:latest"  # Faster model!
TIMEOUT = 120  # 2 minutes - shorter timeout
MAX_IMAGE_SIZE = 512  # Resize images for faster processing

# Simple, fast prompt
FAST_PROMPT = """Analyze this stock chart quickly. Identify:
1. Overall trend (bullish/bearish/neutral)
2. Key patterns (if any): head_shoulders, double_top, double_bottom, triangle, channel, wedge, flag
3. Confidence (0-100)

Reply in this exact format:
TREND: [bullish/bearish/neutral]
PATTERNS: [pattern1, pattern2] or [none]
CONFIDENCE: [0-100]"""


def resize_image_for_speed(image_path: str) -> str:
    """Resize image to speed up processing"""
    try:
        with Image.open(image_path) as img:
            # Resize if larger than MAX_IMAGE_SIZE
            if max(img.size) > MAX_IMAGE_SIZE:
                ratio = MAX_IMAGE_SIZE / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG', optimize=True)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        # Fallback to original
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')


def analyze_chart_fast(image_path: str, symbol: str) -> dict:
    """Fast chart analysis using optimized settings"""
    global MODEL
    
    # Resize image for speed
    image_data = resize_image_for_speed(image_path)
    
    payload = {
        "model": MODEL,
        "prompt": FAST_PROMPT,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": 0.1,  # Low for consistent results
            "num_predict": 100,  # Short response
            "num_ctx": 2048,     # Smaller context
        }
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            result = response.json()
            return parse_fast_response(result.get('response', ''))
        else:
            return None
            
    except requests.exceptions.Timeout:
        return None
    except Exception as e:
        return None


def parse_fast_response(response: str) -> dict:
    """Parse the simplified response format"""
    result = {
        'trend': 'neutral',
        'patterns': [],
        'confidence': 0.5
    }
    
    lines = response.upper().split('\n')
    for line in lines:
        if 'TREND:' in line:
            if 'BULLISH' in line:
                result['trend'] = 'bullish'
            elif 'BEARISH' in line:
                result['trend'] = 'bearish'
            else:
                result['trend'] = 'neutral'
                
        elif 'PATTERNS:' in line:
            # Extract patterns
            patterns_part = line.split('PATTERNS:')[1].strip()
            if 'NONE' not in patterns_part and patterns_part != '[]':
                # Extract pattern names
                patterns = []
                pattern_keywords = ['HEAD', 'SHOULDER', 'DOUBLE', 'TOP', 'BOTTOM', 
                                   'TRIANGLE', 'CHANNEL', 'WEDGE', 'FLAG', 'CUP', 'HANDLE']
                for kw in pattern_keywords:
                    if kw in patterns_part:
                        patterns.append(kw.lower())
                result['patterns'] = list(set(patterns))[:3]  # Max 3 patterns
                
        elif 'CONFIDENCE:' in line:
            try:
                conf_str = line.split('CONFIDENCE:')[1].strip()
                conf = int(''.join(filter(str.isdigit, conf_str[:3])))
                result['confidence'] = conf / 100
            except:
                pass
    
    return result


def run_speed_training():
    """Run optimized fast training"""
    global MODEL
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("PROMETHEUS VISUAL AI - MAXIMUM SPEED TRAINING")
    logger.info("=" * 60)
    logger.info(f"Model: {MODEL} (faster than llava)")
    logger.info(f"Image Size: {MAX_IMAGE_SIZE}px (resized for speed)")
    logger.info(f"Timeout: {TIMEOUT}s")
    logger.info("")
    
    # Check Ollama
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        models = [m['name'] for m in r.json().get('models', [])]
        if MODEL not in models and 'llama3.2-vision' not in str(models):
            logger.warning(f"Model {MODEL} not found, available: {models}")
            # Try llava as fallback
            MODEL = "llava:7b"
            logger.info(f"Using fallback model: {MODEL}")
    except:
        logger.error("Ollama not responding!")
        return
    
    # Find charts
    charts_dir = Path("charts")
    all_charts = list(charts_dir.glob("*.png"))
    logger.info(f"Total charts: {len(all_charts)}")
    
    # Load existing results
    results_file = Path("visual_ai_patterns.json")
    existing = {}
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
                # Only keep entries with actual patterns or high confidence
                for k, v in data.get('patterns', {}).items():
                    if v.get('confidence', 0) > 0.3 or len(v.get('patterns', [])) > 0:
                        existing[k] = v
        except:
            pass
    
    logger.info(f"Valid existing: {len(existing)}")
    
    # Filter unprocessed
    to_process = [c for c in all_charts if c.name not in existing]
    logger.info(f"To process: {len(to_process)}")
    logger.info("")
    
    if not to_process:
        logger.info("All charts processed!")
        return
    
    # Process charts
    results = existing.copy()
    start_time = time.time()
    success = 0
    errors = 0
    patterns_found = 0
    
    for i, chart in enumerate(to_process, 1):
        symbol = chart.stem.split('_')[0]
        
        logger.info(f"[{i}/{len(to_process)}] {chart.name[:40]}...")
        
        chart_start = time.time()
        analysis = analyze_chart_fast(str(chart), symbol)
        elapsed = time.time() - chart_start
        
        if analysis and analysis.get('confidence', 0) > 0:
            success += 1
            patterns_found += len(analysis.get('patterns', []))
            
            results[chart.name] = {
                'patterns': analysis.get('patterns', []),
                'trend': analysis.get('trend', 'neutral'),
                'trend_strength': 'medium' if analysis.get('confidence', 0) > 0.6 else 'weak',
                'support': [],
                'resistance': [],
                'confidence': analysis.get('confidence', 0.5),
                'analyzed_at': datetime.now().isoformat()
            }
            
            trend = analysis.get('trend', '?')
            pats = analysis.get('patterns', [])
            conf = analysis.get('confidence', 0)
            logger.info(f"    [OK] {trend} | {pats if pats else 'no patterns'} | {conf:.0%} | {elapsed:.1f}s")
        else:
            errors += 1
            results[chart.name] = {
                'patterns': [],
                'trend': 'neutral',
                'trend_strength': 'weak',
                'support': [],
                'resistance': [],
                'confidence': 0.0,
                'analyzed_at': datetime.now().isoformat()
            }
            logger.info(f"    [FAIL] timeout or error | {elapsed:.1f}s")
        
        # Save every 10 charts
        if i % 10 == 0:
            save_results(results, patterns_found)
            rate = i / ((time.time() - start_time) / 60)
            logger.info(f"    >> Progress: {success}/{i} success ({success/i*100:.0f}%), {rate:.1f} charts/min")
            logger.info("")
    
    # Final save
    save_results(results, patterns_found)
    
    elapsed_total = (time.time() - start_time) / 60
    logger.info("")
    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Processed: {len(to_process)}")
    logger.info(f"Success: {success} ({success/len(to_process)*100:.1f}%)")
    logger.info(f"Errors: {errors}")
    logger.info(f"Patterns found: {patterns_found}")
    logger.info(f"Time: {elapsed_total:.1f} minutes")
    logger.info(f"Rate: {len(to_process)/elapsed_total:.1f} charts/min")
    logger.info("=" * 60)


def save_results(results, total_patterns):
    """Save results"""
    pattern_summary = {}
    for data in results.values():
        for p in data.get('patterns', []):
            pattern_summary[p] = pattern_summary.get(p, 0) + 1
    
    output = {
        'last_updated': datetime.now().isoformat(),
        'total_analyzed': len(results),
        'total_patterns': total_patterns,
        'patterns': results,
        'pattern_summary': pattern_summary
    }
    
    with open('visual_ai_patterns.json', 'w') as f:
        json.dump(output, f, indent=2)


if __name__ == "__main__":
    print("")
    print("=" * 60)
    print("VISUAL AI MAXIMUM SPEED TRAINING")
    print("=" * 60)
    print("")
    print("Optimizations:")
    print("  - Using llama3.2-vision (faster model)")
    print("  - Images resized to 512px (faster processing)")
    print("  - Simplified prompts (quicker responses)")
    print("  - 120s timeout (fail fast, move on)")
    print("")
    print("Press Ctrl+C to stop (progress saved)")
    print("")
    
    try:
        run_speed_training()
    except KeyboardInterrupt:
        print("\n\nStopped by user. Progress saved.")
