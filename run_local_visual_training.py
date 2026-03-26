#!/usr/bin/env python3
"""
PROMETHEUS Background Visual Training with Local LLaVA
=======================================================
Runs chart pattern training using local Ollama LLaVA model.
No API costs, runs in background, learns from trading patterns.
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('visual_training_local.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434"
MODEL = "llava:7b"


def check_ollama():
    """Check if Ollama is running with LLaVA"""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            for m in models:
                if 'llava' in m.get('name', '').lower():
                    logger.info(f"Found LLaVA model: {m['name']}")
                    return True
            logger.warning("LLaVA model not found in Ollama")
            return False
    except Exception as e:
        logger.error(f"Ollama not available: {e}")
        return False


def analyze_chart_local(image_path: str, symbol: str) -> dict:
    """Analyze chart using local LLaVA"""
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = f"""Analyze this {symbol} stock/crypto chart for trading patterns.

Identify:
1. Chart patterns (head & shoulders, double top/bottom, triangles, flags, wedges, channels)
2. Trend direction (bullish/bearish/neutral)
3. Trend strength (strong/moderate/weak)
4. Key support levels
5. Key resistance levels
6. Overall signal quality

Respond in JSON format only:
{{"patterns": ["pattern1"], "trend": "bullish", "trend_strength": "moderate", "support": [100], "resistance": [110], "signal": "moderate", "confidence": 0.7}}"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 512
        }
    }
    
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=300  # 5 min timeout for local model
        )
        
        if resp.status_code == 200:
            result = resp.json()
            text = result.get('response', '')
            return parse_response(text)
        else:
            return {'success': False, 'error': f"Status {resp.status_code}"}
            
    except requests.Timeout:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def parse_response(text: str) -> dict:
    """Parse LLaVA response"""
    import re
    
    try:
        # Find JSON in response
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            data = json.loads(json_match.group())
            return {
                'patterns': data.get('patterns', []),
                'trend': data.get('trend', 'neutral'),
                'trend_strength': data.get('trend_strength', 'weak'),
                'support': data.get('support', []),
                'resistance': data.get('resistance', []),
                'signal': data.get('signal', 'weak'),
                'confidence': data.get('confidence', 0.5),
                'success': True
            }
    except json.JSONDecodeError:
        pass
    
    # Fallback parsing
    text_lower = text.lower()
    trend = 'neutral'
    if 'bullish' in text_lower:
        trend = 'bullish'
    elif 'bearish' in text_lower:
        trend = 'bearish'
    
    patterns = []
    pattern_names = ['double top', 'double bottom', 'head and shoulders', 'triangle', 
                     'flag', 'wedge', 'channel', 'breakout', 'support', 'resistance']
    for p in pattern_names:
        if p in text_lower:
            patterns.append(p)
    
    return {
        'patterns': patterns,
        'trend': trend,
        'trend_strength': 'weak',
        'support': [],
        'resistance': [],
        'signal': 'weak',
        'confidence': 0.4,
        'success': True,
        'raw_text': text[:200]
    }


def save_results(results: dict, pattern_counts: dict):
    """Save results to JSON"""
    output = {
        'last_updated': datetime.now().isoformat(),
        'provider': 'local_llava',
        'model': MODEL,
        'total_analyzed': len(results),
        'successful_analyses': sum(1 for r in results.values() if r.get('success', False)),
        'total_patterns': sum(len(r.get('patterns', [])) for r in results.values()),
        'patterns': results,
        'pattern_summary': pattern_counts
    }
    
    with open('visual_ai_patterns_local.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    return output


def run_visual_training():
    """Main training loop"""
    logger.info("="*70)
    logger.info("PROMETHEUS LOCAL VISUAL TRAINING")
    logger.info("="*70)
    logger.info(f"Model: {MODEL}")
    logger.info(f"Started: {datetime.now()}")
    
    # Check Ollama
    if not check_ollama():
        logger.error("Ollama with LLaVA not available!")
        return
    
    # Find charts
    chart_dirs = ['charts', 'paper_trading_charts']
    all_charts = []
    for d in chart_dirs:
        chart_dir = Path(d)
        if chart_dir.exists():
            all_charts.extend(list(chart_dir.glob('*.png')))
    
    logger.info(f"Found {len(all_charts)} charts")
    
    if not all_charts:
        logger.error("No charts found!")
        return
    
    # Load existing results
    results_file = Path('visual_ai_patterns_local.json')
    existing_results = {}
    if results_file.exists():
        try:
            with open(results_file, 'r') as f:
                data = json.load(f)
                existing_results = data.get('patterns', {})
                # Keep only successful analyses
                existing_results = {k: v for k, v in existing_results.items() 
                                   if v.get('success', False)}
                logger.info(f"Loaded {len(existing_results)} existing successful analyses")
        except:
            pass
    
    # Filter to unprocessed charts
    charts_to_process = [c for c in all_charts if c.name not in existing_results]
    logger.info(f"Charts to process: {len(charts_to_process)}")
    
    if not charts_to_process:
        logger.info("All charts already processed!")
        return
    
    # Estimate time (local model ~30-60 sec per image)
    est_time = len(charts_to_process) * 45 / 60
    logger.info(f"Estimated time: {est_time:.0f} minutes")
    
    # Process charts
    results = existing_results.copy()
    pattern_counts = {}
    success_count = 0
    error_count = 0
    start_time = time.time()
    
    for i, chart_path in enumerate(charts_to_process, 1):
        filename = chart_path.name
        symbol = filename.split('_')[0]
        
        logger.info(f"[{i}/{len(charts_to_process)}] Analyzing: {filename}")
        
        try:
            analysis = analyze_chart_local(str(chart_path), symbol)
            
            results[filename] = {
                'patterns': analysis.get('patterns', []),
                'trend': analysis.get('trend', 'neutral'),
                'trend_strength': analysis.get('trend_strength', 'weak'),
                'support': analysis.get('support', []),
                'resistance': analysis.get('resistance', []),
                'confidence': analysis.get('confidence', 0.0),
                'signal': analysis.get('signal', 'weak'),
                'analyzed_at': datetime.now().isoformat(),
                'success': analysis.get('success', False)
            }
            
            if analysis.get('success', False):
                success_count += 1
                for p in analysis.get('patterns', []):
                    pattern_counts[p] = pattern_counts.get(p, 0) + 1
                logger.info(f"  OK: {len(analysis.get('patterns', []))} patterns, {analysis.get('trend')}")
            else:
                error_count += 1
                logger.warning(f"  FAIL: {analysis.get('error', 'Unknown')}")
            
            # Save every 5 charts
            if i % 5 == 0:
                save_results(results, pattern_counts)
                elapsed = time.time() - start_time
                rate = i / (elapsed / 60) if elapsed > 0 else 0
                logger.info(f"  Saved. Rate: {rate:.1f} charts/min")
                
        except Exception as e:
            error_count += 1
            results[filename] = {
                'patterns': [],
                'trend': 'neutral',
                'success': False,
                'error': str(e)[:100],
                'analyzed_at': datetime.now().isoformat()
            }
            logger.error(f"  ERROR: {str(e)[:50]}")
    
    # Final save
    save_results(results, pattern_counts)
    
    elapsed = time.time() - start_time
    logger.info("="*70)
    logger.info("VISUAL TRAINING COMPLETE")
    logger.info("="*70)
    logger.info(f"Total processed: {len(charts_to_process)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Errors: {error_count}")
    logger.info(f"Time: {elapsed/60:.1f} minutes")
    logger.info(f"Patterns found: {sum(pattern_counts.values())}")
    if pattern_counts:
        logger.info("Top patterns:")
        for p, c in sorted(pattern_counts.items(), key=lambda x: -x[1])[:5]:
            logger.info(f"  {p}: {c}")
    logger.info("="*70)


if __name__ == "__main__":
    try:
        run_visual_training()
    except KeyboardInterrupt:
        logger.info("\nTraining interrupted. Progress saved.")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
