#!/usr/bin/env python3
"""
FIXED VISUAL AI TRAINER
========================
Properly calls LLaVA with correct timeout and error handling
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import asyncio
import base64
import requests
import json
import time
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('visual_ai_fixed_training.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)


class FixedVisualAITrainer:
    """Fixed Visual AI trainer with proper LLaVA integration"""
    
    def __init__(self):
        self.model = "llava:7b"
        self.endpoint = "http://localhost:11434"
        self.timeout = 180  # 3 minutes per image
        self.batch_size = 5
        self.results = {
            'start_time': datetime.now().isoformat(),
            'charts_analyzed': 0,
            'patterns_found': [],
            'errors': 0
        }
    
    def analyze_chart(self, image_path: Path) -> dict:
        """Analyze a single chart with LLaVA"""
        
        # Load and encode image
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        symbol = image_path.stem.split('_')[0]
        
        prompt = f"""Analyze this {symbol} trading chart carefully.

Identify and report:
1. PATTERNS: Any chart patterns (head and shoulders, double top/bottom, triangles, flags, wedges, cup and handle, etc.)
2. SUPPORT: Key support price levels (be specific)
3. RESISTANCE: Key resistance price levels (be specific)
4. TREND: Overall trend direction (bullish/bearish/neutral)
5. STRENGTH: Trend strength (strong/moderate/weak)
6. CONFIDENCE: Your confidence in this analysis (0.0-1.0)

Format exactly as:
PATTERNS: [list or "None detected"]
SUPPORT: [comma-separated prices]
RESISTANCE: [comma-separated prices]
TREND: [bullish/bearish/neutral]
STRENGTH: [strong/moderate/weak]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]
"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "num_predict": 1024
            }
        }
        
        try:
            start = time.time()
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            elapsed = time.time() - start
            
            if response.status_code == 200:
                result = response.json()
                llava_response = result.get('response', '')
                
                # Parse response
                analysis = self._parse_response(llava_response)
                analysis['chart'] = image_path.name
                analysis['symbol'] = symbol
                analysis['latency'] = elapsed
                analysis['success'] = True
                
                return analysis
            else:
                return {'chart': image_path.name, 'success': False, 'error': f'Status {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'chart': image_path.name, 'success': False, 'error': 'timeout'}
        except Exception as e:
            return {'chart': image_path.name, 'success': False, 'error': str(e)[:100]}
    
    def _parse_response(self, response: str) -> dict:
        """Parse LLaVA response"""
        
        patterns = []
        support = []
        resistance = []
        trend = 'neutral'
        strength = 'moderate'
        confidence = 0.5
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('PATTERNS:'):
                text = line.replace('PATTERNS:', '').strip()
                if text.lower() != 'none detected':
                    patterns = [p.strip() for p in text.split(',') if p.strip()]
            elif line.startswith('SUPPORT:'):
                text = line.replace('SUPPORT:', '').strip()
                support = [p.strip() for p in text.split(',') if p.strip()]
            elif line.startswith('RESISTANCE:'):
                text = line.replace('RESISTANCE:', '').strip()
                resistance = [p.strip() for p in text.split(',') if p.strip()]
            elif line.startswith('TREND:'):
                trend = line.replace('TREND:', '').strip().lower()
            elif line.startswith('STRENGTH:'):
                strength = line.replace('STRENGTH:', '').strip().lower()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence = float(line.replace('CONFIDENCE:', '').strip())
                except:
                    confidence = 0.5
        
        return {
            'patterns': patterns,
            'support': support,
            'resistance': resistance,
            'trend': trend,
            'strength': strength,
            'confidence': confidence
        }
    
    def run_training(self, max_charts: int = 50):
        """Run training on charts"""
        
        logger.info("=" * 60)
        logger.info("FIXED VISUAL AI TRAINING")
        logger.info("=" * 60)
        
        charts_dir = Path("charts")
        charts = list(charts_dir.glob("*.png"))[:max_charts]
        
        logger.info(f"Training on {len(charts)} charts")
        logger.info(f"Estimated time: {len(charts) * 1} - {len(charts) * 3} minutes")
        logger.info("")
        
        all_results = []
        
        for i, chart in enumerate(charts):
            logger.info(f"[{i+1}/{len(charts)}] Analyzing {chart.name}...")
            
            result = self.analyze_chart(chart)
            all_results.append(result)
            
            if result.get('success'):
                self.results['charts_analyzed'] += 1
                patterns = result.get('patterns', [])
                self.results['patterns_found'].extend(patterns)
                
                logger.info(f"         Patterns: {patterns if patterns else 'None'}")
                logger.info(f"         Trend: {result.get('trend')}")
                logger.info(f"         Latency: {result.get('latency', 0):.1f}s")
            else:
                self.results['errors'] += 1
                logger.warning(f"         Error: {result.get('error')}")
        
        # Save results
        self.results['end_time'] = datetime.now().isoformat()
        with open('visual_ai_fixed_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("TRAINING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Charts analyzed: {self.results['charts_analyzed']}")
        logger.info(f"Errors: {self.results['errors']}")
        logger.info(f"Unique patterns: {len(set(self.results['patterns_found']))}")


if __name__ == "__main__":
    trainer = FixedVisualAITrainer()
    trainer.run_training(max_charts=50)  # Start with 50 charts
