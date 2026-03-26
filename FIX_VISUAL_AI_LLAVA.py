#!/usr/bin/env python3
"""
FIX VISUAL AI LLAVA INTEGRATION
================================
This script:
1. Tests and fixes LLaVA connection
2. Increases timeout for large images
3. Properly calls the model
4. Verifies responses are real (not fallback)
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import base64
import requests
import json
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


def test_ollama_connection():
    """Test basic Ollama connection"""
    print("\n" + "=" * 60)
    print("STEP 1: Testing Ollama Connection")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("[OK] Ollama is running")
            print(f"[OK] {len(models)} models available:")
            for m in models:
                print(f"     - {m['name']}")
            return True
        else:
            print(f"[ERROR] Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to Ollama: {e}")
        print("        Make sure 'ollama serve' is running!")
        return False


def test_llava_model():
    """Test LLaVA model specifically"""
    print("\n" + "=" * 60)
    print("STEP 2: Testing LLaVA Model")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = response.json().get('models', [])
        model_names = [m['name'] for m in models]
        
        # Check for LLaVA variants
        llava_models = [m for m in model_names if 'llava' in m.lower() or 'vision' in m.lower()]
        
        if llava_models:
            print(f"[OK] Found vision models: {llava_models}")
            return llava_models[0]  # Return first one
        else:
            print("[ERROR] No LLaVA/vision model found!")
            print("        Run: ollama pull llava:7b")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def test_image_analysis(model_name: str):
    """Test actual image analysis"""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Image Analysis")
    print("=" * 60)
    
    # Find a chart to test
    charts_dir = Path("charts")
    if not charts_dir.exists():
        print("[ERROR] No charts directory found")
        return False
    
    charts = list(charts_dir.glob("*.png"))
    if not charts:
        print("[ERROR] No chart images found")
        return False
    
    test_chart = charts[0]
    print(f"[INFO] Testing with: {test_chart.name}")
    
    # Load and encode image
    with open(test_chart, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Build prompt
    prompt = """Analyze this trading chart. Identify:
1. Chart patterns (head and shoulders, double top, triangles, etc.)
2. Support levels (specific price numbers)
3. Resistance levels (specific price numbers)
4. Trend direction (bullish/bearish/neutral)
5. Your confidence (0.0 to 1.0)

Format your response as:
PATTERNS: [list patterns]
SUPPORT: [prices]
RESISTANCE: [prices]
TREND: [direction]
CONFIDENCE: [0.0-1.0]
"""
    
    # Call LLaVA
    print(f"[INFO] Calling {model_name}... (this may take 30-120 seconds)")
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "images": [image_data],
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 1024
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=180  # 3 minute timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            llava_response = result.get('response', '')
            
            print(f"\n[OK] LLaVA responded in {elapsed:.1f} seconds")
            print("\n" + "-" * 40)
            print("LLaVA Analysis:")
            print("-" * 40)
            print(llava_response[:1000])  # First 1000 chars
            print("-" * 40)
            
            # Check if it's a real response
            if len(llava_response) > 50:
                print("\n[SUCCESS] LLaVA is working correctly!")
                return True
            else:
                print("\n[WARNING] Response seems too short")
                return False
        else:
            print(f"[ERROR] LLaVA returned status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"[ERROR] Timeout after {elapsed:.1f} seconds")
        print("        LLaVA might be overwhelmed. Try restarting Ollama.")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def update_analyzer_config():
    """Update the multimodal analyzer configuration"""
    print("\n" + "=" * 60)
    print("STEP 4: Updating Analyzer Configuration")
    print("=" * 60)
    
    config_update = '''
# Enhanced configuration for Visual AI
VISUAL_AI_CONFIG = {
    "model": "llava:7b",
    "endpoint": "http://localhost:11434",
    "timeout": 180,  # Increased from 60 to 180 seconds
    "temperature": 0.3,
    "max_tokens": 1024,
    "retry_attempts": 3,
    "retry_delay": 5
}
'''
    
    # Save config
    with open("visual_ai_config.json", "w") as f:
        json.dump({
            "model": "llava:7b",
            "endpoint": "http://localhost:11434",
            "timeout": 180,
            "temperature": 0.3,
            "max_tokens": 1024,
            "retry_attempts": 3,
            "retry_delay": 5
        }, f, indent=2)
    
    print("[OK] Saved enhanced config to visual_ai_config.json")
    return True


def create_fixed_trainer():
    """Create an improved Visual AI trainer"""
    print("\n" + "=" * 60)
    print("STEP 5: Creating Fixed Trainer"  )
    print("=" * 60)
    
    trainer_code = '''#!/usr/bin/env python3
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
        
        lines = response.split('\\n')
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
'''
    
    with open("VISUAL_AI_FIXED_TRAINER.py", "w") as f:
        f.write(trainer_code)
    
    print("[OK] Created VISUAL_AI_FIXED_TRAINER.py")
    return True


def main():
    print()
    print("=" * 70)
    print("VISUAL AI LLAVA FIX")
    print("=" * 70)
    print()
    
    # Step 1: Test Ollama
    if not test_ollama_connection():
        print("\n[FATAL] Ollama not running. Start it with: ollama serve")
        return
    
    # Step 2: Test LLaVA
    model = test_llava_model()
    if not model:
        print("\n[FATAL] No vision model. Install with: ollama pull llava:7b")
        return
    
    # Step 3: Test image analysis
    works = test_image_analysis(model)
    
    # Step 4: Update config
    update_analyzer_config()
    
    # Step 5: Create fixed trainer
    create_fixed_trainer()
    
    print()
    print("=" * 70)
    if works:
        print("VISUAL AI FIX COMPLETE - LLaVA is working!")
        print()
        print("To run proper training, use:")
        print("  python VISUAL_AI_FIXED_TRAINER.py")
    else:
        print("VISUAL AI NEEDS ATTENTION")
        print()
        print("Try:")
        print("  1. Restart Ollama: Close terminal, run 'ollama serve'")
        print("  2. Pull model again: ollama pull llava:7b")
        print("  3. Check GPU memory: LLaVA needs ~5GB VRAM")
    print("=" * 70)


if __name__ == "__main__":
    main()
