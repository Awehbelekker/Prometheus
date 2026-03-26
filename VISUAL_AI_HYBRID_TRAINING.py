"""
PROMETHEUS Visual AI - HYBRID Training
=======================================
Combines:
1. Code-based technical analysis (reliable patterns)
2. AI vision for trend confirmation (what AI is good at)

This is MORE RELIABLE than pure AI vision analysis!
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
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('visual_ai_hybrid_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from PIL import Image
    import io
    HAS_PIL = True
except:
    HAS_PIL = False

try:
    import numpy as np
    HAS_NUMPY = True
except:
    HAS_NUMPY = False


class HybridChartAnalyzer:
    """
    Hybrid analyzer that combines:
    - Code-based pattern detection (reliable)
    - AI vision for trend/sentiment (what AI does well)
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.timeout = 120
        
    def analyze_chart(self, image_path: str, symbol: str) -> Dict:
        """
        Analyze chart using hybrid approach
        """
        result = {
            'symbol': symbol,
            'patterns': [],
            'trend': 'neutral',
            'trend_strength': 'weak',
            'support': [],
            'resistance': [],
            'confidence': 0.5,
            'method': 'hybrid'
        }
        
        # Step 1: Get AI trend analysis (simple question AI can answer)
        ai_result = self._get_ai_trend(image_path, symbol)
        if ai_result:
            result['trend'] = ai_result.get('trend', 'neutral')
            result['confidence'] = ai_result.get('confidence', 0.5)
        
        # Step 2: Code-based pattern detection from image pixels
        if HAS_PIL and HAS_NUMPY:
            code_patterns = self._detect_patterns_from_image(image_path)
            result['patterns'] = code_patterns.get('patterns', [])
            result['support'] = code_patterns.get('support', [])
            result['resistance'] = code_patterns.get('resistance', [])
            result['trend_strength'] = code_patterns.get('strength', 'weak')
        
        return result
    
    def _get_ai_trend(self, image_path: str, symbol: str) -> Optional[Dict]:
        """
        Ask AI a SIMPLE question it can answer reliably:
        Just the trend direction - bullish, bearish, or sideways
        """
        
        # Load and resize image for faster processing
        try:
            if HAS_PIL:
                with Image.open(image_path) as img:
                    # Resize to speed up
                    img = img.resize((512, 384), Image.LANCZOS)
                    buf = io.BytesIO()
                    img.save(buf, format='PNG')
                    img_data = base64.b64encode(buf.getvalue()).decode()
            else:
                with open(image_path, 'rb') as f:
                    img_data = base64.b64encode(f.read()).decode()
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None
        
        # SIMPLE prompt - just ask about trend direction
        # AI is GOOD at this simple task
        prompt = """Look at this stock price chart. 
        
Is the overall price trend:
- BULLISH (prices going UP)
- BEARISH (prices going DOWN)  
- NEUTRAL (prices going SIDEWAYS)

Reply with just ONE WORD: BULLISH, BEARISH, or NEUTRAL"""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llava:7b",
                    "prompt": prompt,
                    "images": [img_data],
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 20  # Very short response
                    }
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                text = response.json().get('response', '').upper()
                
                if 'BULLISH' in text or 'UP' in text:
                    return {'trend': 'bullish', 'confidence': 0.7}
                elif 'BEARISH' in text or 'DOWN' in text:
                    return {'trend': 'bearish', 'confidence': 0.7}
                else:
                    return {'trend': 'neutral', 'confidence': 0.5}
                    
        except Exception as e:
            logger.warning(f"AI trend failed: {e}")
            
        return None
    
    def _detect_patterns_from_image(self, image_path: str) -> Dict:
        """
        Detect patterns using code analysis of the image pixels.
        This is MORE RELIABLE than asking AI to identify patterns.
        """
        
        result = {
            'patterns': [],
            'support': [],
            'resistance': [],
            'strength': 'weak'
        }
        
        try:
            with Image.open(image_path) as img:
                # Convert to grayscale numpy array
                img_gray = img.convert('L')
                pixels = np.array(img_gray)
                
                # Find the chart area (where prices are drawn)
                # Look for the main line in the image
                height, width = pixels.shape
                
                # Sample price levels from the image
                # Dark pixels on light background = price line
                threshold = np.mean(pixels)
                
                # Find price line y-coordinates at various x points
                price_points = []
                for x in range(int(width * 0.1), int(width * 0.9), 10):
                    column = pixels[:, x]
                    # Find darkest point (the price line)
                    y = np.argmin(column)
                    if column[y] < threshold:
                        price_points.append((x, height - y))  # Flip y
                
                if len(price_points) < 10:
                    return result
                
                # Extract just y values (prices)
                prices = [p[1] for p in price_points]
                
                # Detect patterns from price movement
                patterns = []
                
                # 1. Detect trend direction and strength
                start_price = np.mean(prices[:5])
                end_price = np.mean(prices[-5:])
                mid_price = np.mean(prices[len(prices)//2-2:len(prices)//2+3])
                
                price_change = (end_price - start_price) / start_price
                
                if abs(price_change) > 0.1:
                    result['strength'] = 'strong'
                elif abs(price_change) > 0.05:
                    result['strength'] = 'moderate'
                else:
                    result['strength'] = 'weak'
                
                # 2. Detect basic patterns
                
                # Double top: two peaks with valley between
                peaks = self._find_peaks(prices)
                valleys = self._find_valleys(prices)
                
                if len(peaks) >= 2:
                    # Check if top two peaks are similar height
                    peak_heights = sorted([prices[p] for p in peaks], reverse=True)
                    if len(peak_heights) >= 2:
                        if abs(peak_heights[0] - peak_heights[1]) / peak_heights[0] < 0.03:
                            patterns.append('Double Top')
                
                if len(valleys) >= 2:
                    valley_depths = sorted([prices[v] for v in valleys])
                    if len(valley_depths) >= 2:
                        if abs(valley_depths[0] - valley_depths[1]) / valley_depths[0] < 0.03:
                            patterns.append('Double Bottom')
                
                # Head and shoulders: three peaks, middle highest
                if len(peaks) >= 3:
                    sorted_peaks = sorted(peaks)
                    if len(sorted_peaks) >= 3:
                        left = prices[sorted_peaks[0]]
                        head = prices[sorted_peaks[len(sorted_peaks)//2]]
                        right = prices[sorted_peaks[-1]]
                        
                        if head > left and head > right:
                            if abs(left - right) / left < 0.05:
                                patterns.append('Head and Shoulders')
                
                # Triangle: converging highs and lows
                if len(peaks) >= 3 and len(valleys) >= 3:
                    peak_trend = (prices[peaks[-1]] - prices[peaks[0]]) / len(peaks)
                    valley_trend = (prices[valleys[-1]] - prices[valleys[0]]) / len(valleys)
                    
                    if peak_trend < 0 and valley_trend > 0:
                        patterns.append('Symmetrical Triangle')
                    elif peak_trend < 0 and abs(valley_trend) < 0.01:
                        patterns.append('Descending Triangle')
                    elif abs(peak_trend) < 0.01 and valley_trend > 0:
                        patterns.append('Ascending Triangle')
                
                # Channel: parallel trend lines
                if result['strength'] != 'weak':
                    if len(peaks) >= 2 and len(valleys) >= 2:
                        patterns.append('Channel')
                
                result['patterns'] = patterns[:3]  # Top 3 patterns
                
                # Support/Resistance from valleys/peaks
                if valleys:
                    min_val = min(prices[v] for v in valleys)
                    result['support'] = [round(min_val, 2)]
                if peaks:
                    max_val = max(prices[p] for p in peaks)
                    result['resistance'] = [round(max_val, 2)]
                
        except Exception as e:
            logger.warning(f"Pattern detection error: {e}")
        
        return result
    
    def _find_peaks(self, data: list, threshold: int = 3) -> List[int]:
        """Find local maxima in price data"""
        peaks = []
        for i in range(threshold, len(data) - threshold):
            if all(data[i] > data[i-j] for j in range(1, threshold+1)):
                if all(data[i] > data[i+j] for j in range(1, threshold+1)):
                    peaks.append(i)
        return peaks
    
    def _find_valleys(self, data: list, threshold: int = 3) -> List[int]:
        """Find local minima in price data"""
        valleys = []
        for i in range(threshold, len(data) - threshold):
            if all(data[i] < data[i-j] for j in range(1, threshold+1)):
                if all(data[i] < data[i+j] for j in range(1, threshold+1)):
                    valleys.append(i)
        return valleys


def run_hybrid_training():
    """Run hybrid Visual AI training"""
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("PROMETHEUS VISUAL AI - HYBRID TRAINING")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Hybrid approach:")
    logger.info("  1. AI Vision: Simple trend detection (reliable)")
    logger.info("  2. Code Analysis: Pattern detection (accurate)")
    logger.info("")
    
    # Initialize analyzer
    analyzer = HybridChartAnalyzer()
    
    # Find charts
    charts_dir = Path("charts")
    all_charts = sorted(list(charts_dir.glob("*.png")))
    logger.info(f"Total charts: {len(all_charts)}")
    
    # Load existing results
    results = {}
    results_file = Path("visual_ai_patterns.json")
    if results_file.exists():
        try:
            with open(results_file) as f:
                data = json.load(f)
                # Keep entries with patterns
                for k, v in data.get('patterns', {}).items():
                    if v.get('patterns') or v.get('confidence', 0) > 0.6:
                        results[k] = v
        except:
            pass
    
    logger.info(f"Existing quality results: {len(results)}")
    
    # Filter unprocessed
    to_process = [c for c in all_charts if c.name not in results]
    logger.info(f"To process: {len(to_process)}")
    logger.info("")
    
    if not to_process:
        logger.info("All done!")
        return
    
    # Process
    start_time = time.time()
    success = 0
    patterns_found = 0
    
    for i, chart in enumerate(to_process, 1):
        symbol = chart.stem.split('_')[0]
        
        logger.info(f"[{i}/{len(to_process)}] {chart.name}")
        
        t0 = time.time()
        result = analyzer.analyze_chart(str(chart), symbol)
        elapsed = time.time() - t0
        
        # Save result
        results[chart.name] = {
            'patterns': result.get('patterns', []),
            'trend': result.get('trend', 'neutral'),
            'trend_strength': result.get('trend_strength', 'weak'),
            'support': result.get('support', []),
            'resistance': result.get('resistance', []),
            'confidence': result.get('confidence', 0.5),
            'analyzed_at': datetime.now().isoformat(),
            'method': 'hybrid'
        }
        
        if result.get('patterns'):
            patterns_found += len(result['patterns'])
            success += 1
            logger.info(f"  ✓ {result['trend']} | Patterns: {result['patterns']} | {elapsed:.1f}s")
        else:
            logger.info(f"  ~ {result['trend']} | No patterns | {elapsed:.1f}s")
        
        # Save every 10
        if i % 10 == 0:
            save_results(results, patterns_found)
            rate = i / ((time.time() - start_time) / 60)
            logger.info(f"  >> Progress: {i}/{len(to_process)}, Patterns: {patterns_found}, Rate: {rate:.1f}/min")
            logger.info("")
    
    # Final save
    save_results(results, patterns_found)
    
    total_time = (time.time() - start_time) / 60
    logger.info("")
    logger.info("=" * 60)
    logger.info("HYBRID TRAINING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Processed: {len(to_process)}")
    logger.info(f"With patterns: {success}")
    logger.info(f"Total patterns: {patterns_found}")
    logger.info(f"Time: {total_time:.1f} min")
    logger.info("=" * 60)


def save_results(results, total_patterns):
    """Save results"""
    pattern_summary = {}
    for data in results.values():
        for p in data.get('patterns', []):
            pattern_summary[p] = pattern_summary.get(p, 0) + 1
    
    with open('visual_ai_patterns.json', 'w') as f:
        json.dump({
            'last_updated': datetime.now().isoformat(),
            'total_analyzed': len(results),
            'total_patterns': total_patterns,
            'patterns': results,
            'pattern_summary': pattern_summary
        }, f, indent=2)


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("HYBRID VISUAL AI TRAINING")
    print("=" * 60)
    print()
    print("This uses a BETTER approach:")
    print("  - AI handles: Trend direction (what it's good at)")
    print("  - Code handles: Pattern detection (more reliable)")
    print()
    print("Expected: FASTER and MORE ACCURATE!")
    print()
    
    run_hybrid_training()
