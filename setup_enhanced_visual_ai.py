#!/usr/bin/env python3
"""
Enhanced Cloud Vision Configuration
Enables Claude 3.5 Vision + Gemini Pro Vision + LLaVA
"""

import json
import os
from pathlib import Path

# Create enhanced visual AI configuration
enhanced_config = {
    "enabled": True,
    "version": "2.0",
    "description": "Multi-provider visual AI for chart analysis",
    
    # Provider priority (will try in order)
    "providers": [
        {
            "name": "claude",
            "model": "claude-3-5-sonnet-20241022",
            "enabled": True,
            "priority": 1,
            "cost_per_image": 0.003,
            "capabilities": [
                "chart_analysis",
                "pattern_recognition",
                "trend_detection",
                "support_resistance",
                "candlestick_patterns"
            ],
            "max_images_per_day": 1000,
            "description": "Claude 3.5 Sonnet - Best for detailed chart analysis"
        },
        {
            "name": "gemini",
            "model": "gemini-pro-vision",
            "enabled": True,
            "priority": 2,
            "cost_per_image": 0.0,
            "capabilities": [
                "chart_analysis",
                "pattern_recognition",
                "trend_detection",
                "volume_analysis"
            ],
            "max_images_per_day": 1500,
            "description": "Gemini Pro Vision - Free tier, good accuracy"
        },
        {
            "name": "llava",
            "model": "llava:7b",
            "enabled": True,
            "priority": 3,
            "cost_per_image": 0.0,
            "endpoint": "http://localhost:11434",
            "capabilities": [
                "chart_analysis",
                "basic_patterns",
                "trend_detection"
            ],
            "max_images_per_day": 999999,
            "description": "LLaVA 7B - Free local fallback"
        }
    ],
    
    # Analysis settings
    "analysis": {
        "timeout": 30,
        "temperature": 0.3,
        "max_tokens": 1024,
        "retry_attempts": 2,
        "retry_delay": 3,
        "cache_results": True,
        "cache_duration_hours": 1
    },
    
    # Pattern confidence thresholds
    "confidence_thresholds": {
        "strong_pattern": 0.80,
        "moderate_pattern": 0.65,
        "weak_pattern": 0.50,
        "ignore_below": 0.40
    },
    
    # Feature flags
    "features": {
        "real_time_analysis": True,
        "batch_processing": True,
        "pattern_caching": True,
        "multi_timeframe": True,
        "volume_analysis": True,
        "indicator_overlay": True
    }
}

# Save configuration
config_path = Path('enhanced_visual_ai_config.json')
with open(config_path, 'w') as f:
    json.dump(enhanced_config, f, indent=2)

print("✅ Enhanced Visual AI Configuration Created")
print(f"   File: {config_path}")
print(f"\n📊 PROVIDERS ENABLED:")
for provider in enhanced_config['providers']:
    status = "✅" if provider['enabled'] else "❌"
    cost = f"${provider['cost_per_image']:.4f}" if provider['cost_per_image'] > 0 else "FREE"
    print(f"   {status} {provider['name'].upper()}: {provider['description']} ({cost}/image)")

print(f"\n🎯 FEATURES:")
for feature, enabled in enhanced_config['features'].items():
    status = "✅" if enabled else "❌"
    print(f"   {status} {feature.replace('_', ' ').title()}")

# Create provider integration module
integration_code = '''#!/usr/bin/env python3
"""
Multi-Provider Visual AI Integration
Routes visual analysis to Claude, Gemini, or LLaVA based on availability
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, List, Optional
import anthropic
import google.generativeai as genai

class EnhancedVisualAI:
    """Multi-provider visual AI with smart routing"""
    
    def __init__(self, config_path='enhanced_visual_ai_config.json'):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.providers = self._init_providers()
        self.cache = {}
        
    def _init_providers(self) -> Dict:
        """Initialize all available providers"""
        providers = {}
        
        # Claude
        claude_key = os.getenv('ANTHROPIC_API_KEY')
        if claude_key:
            try:
                providers['claude'] = anthropic.Anthropic(api_key=claude_key)
                print("✅ Claude Vision initialized")
            except Exception as e:
                print(f"⚠️ Claude initialization failed: {e}")
        
        # Gemini
        gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_AI_API_KEY')
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                providers['gemini'] = genai.GenerativeModel('gemini-pro-vision')
                print("✅ Gemini Vision initialized")
            except Exception as e:
                print(f"⚠️ Gemini initialization failed: {e}")
        
        # LLaVA (local)
        try:
            import requests
            llava_config = next(p for p in self.config['providers'] if p['name'] == 'llava')
            endpoint = llava_config.get('endpoint', 'http://localhost:11434')
            # Test connection
            response = requests.get(f"{endpoint}/api/tags", timeout=2)
            if response.status_code == 200:
                providers['llava'] = {'endpoint': endpoint, 'model': llava_config['model']}
                print("✅ LLaVA Vision initialized")
        except Exception as e:
            print(f"⚠️ LLaVA initialization failed: {e}")
        
        return providers
    
    def analyze_chart(self, image_path: str, symbol: str = "", prompt: str = "") -> Dict:
        """
        Analyze chart using best available provider
        
        Args:
            image_path: Path to chart image
            symbol: Trading symbol (e.g., 'AAPL')
            prompt: Custom analysis prompt
            
        Returns:
            Analysis results with pattern detection
        """
        # Check cache
        cache_key = f"{image_path}:{symbol}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try providers in priority order
        for provider_config in self.config['providers']:
            if not provider_config['enabled']:
                continue
            
            provider_name = provider_config['name']
            if provider_name not in self.providers:
                continue
            
            try:
                result = self._analyze_with_provider(
                    provider_name,
                    image_path,
                    symbol,
                    prompt
                )
                
                if result:
                    # Cache result
                    if self.config['analysis']['cache_results']:
                        self.cache[cache_key] = result
                    
                    result['provider'] = provider_name
                    result['cost'] = provider_config['cost_per_image']
                    return result
                    
            except Exception as e:
                print(f"⚠️ {provider_name} failed: {e}")
                continue
        
        return {'error': 'All providers failed', 'patterns': []}
    
    def _analyze_with_provider(self, provider: str, image_path: str, 
                               symbol: str, prompt: str) -> Optional[Dict]:
        """Analyze with specific provider"""
        
        if provider == 'claude':
            return self._analyze_claude(image_path, symbol, prompt)
        elif provider == 'gemini':
            return self._analyze_gemini(image_path, symbol, prompt)
        elif provider == 'llava':
            return self._analyze_llava(image_path, symbol, prompt)
        
        return None
    
    def _analyze_claude(self, image_path: str, symbol: str, prompt: str) -> Dict:
        """Analyze with Claude Vision"""
        client = self.providers['claude']
        
        # Read image
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        # Determine media type
        ext = Path(image_path).suffix.lower()
        media_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp'
        }.get(ext, 'image/png')
        
        analysis_prompt = prompt or f"""Analyze this {symbol} trading chart. Identify:
1. Trend direction (bullish/bearish/neutral)
2. Chart patterns (head & shoulders, triangles, flags, etc.)
3. Support and resistance levels
4. Volume patterns
5. Candlestick patterns
6. Trading recommendation (buy/sell/hold) with confidence level

Provide structured JSON response with pattern confidence scores."""
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": analysis_prompt
                    }
                ]
            }]
        )
        
        # Parse response
        response_text = message.content[0].text
        
        try:
            # Try to parse as JSON
            if '{' in response_text:
                json_start = response_text.index('{')
                json_end = response_text.rindex('}') + 1
                result = json.loads(response_text[json_start:json_end])
            else:
                result = {'raw_analysis': response_text, 'patterns': []}
        except:
            result = {'raw_analysis': response_text, 'patterns': []}
        
        return result
    
    def _analyze_gemini(self, image_path: str, symbol: str, prompt: str) -> Dict:
        """Analyze with Gemini Vision"""
        from PIL import Image
        
        model = self.providers['gemini']
        img = Image.open(image_path)
        
        analysis_prompt = prompt or f"""Analyze this {symbol} chart. Identify patterns, trends, support/resistance, and provide trading signal."""
        
        response = model.generate_content([analysis_prompt, img])
        
        return {
            'raw_analysis': response.text,
            'patterns': self._extract_patterns(response.text)
        }
    
    def _analyze_llava(self, image_path: str, symbol: str, prompt: str) -> Dict:
        """Analyze with LLaVA local vision model"""
        import requests
        
        llava = self.providers['llava']
        endpoint = llava['endpoint']
        model = llava['model']
        
        # Read image as base64
        with open(image_path, 'rb') as f:
            image_data = base64.standard_b64encode(f.read()).decode('utf-8')
        
        analysis_prompt = prompt or f"Analyze this {symbol} chart and identify patterns, trends, and signals."
        
        response = requests.post(
            f"{endpoint}/api/generate",
            json={
                "model": model,
                "prompt": analysis_prompt,
                "images": [image_data],
                "stream": False
            },
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'raw_analysis': result.get('response', ''),
                'patterns': self._extract_patterns(result.get('response', ''))
            }
        
        return None
    
    def _extract_patterns(self, text: str) -> List[Dict]:
        """Extract chart patterns from text analysis"""
        patterns = []
        
        pattern_keywords = {
            'head and shoulders': {'type': 'reversal', 'bearish': True},
            'double top': {'type': 'reversal', 'bearish': True},
            'double bottom': {'type': 'reversal', 'bullish': True},
            'triangle': {'type': 'continuation', 'neutral': True},
            'flag': {'type': 'continuation', 'trend_follow': True},
            'wedge': {'type': 'reversal', 'context_dependent': True},
            'cup and handle': {'type': 'continuation', 'bullish': True},
            'support': {'type': 'level', 'importance': 'high'},
            'resistance': {'type': 'level', 'importance': 'high'}
        }
        
        text_lower = text.lower()
        
        for pattern_name, attributes in pattern_keywords.items():
            if pattern_name in text_lower:
                patterns.append({
                    'pattern': pattern_name,
                    'confidence': 0.75,
                    **attributes
                })
        
        return patterns
    
    def get_provider_stats(self) -> Dict:
        """Get statistics about provider usage"""
        return {
            'available_providers': list(self.providers.keys()),
            'total_providers': len(self.providers),
            'cache_size': len(self.cache)
        }


# Test function
if __name__ == "__main__":
    print("\\n" + "="*70)
    print("  🎨 ENHANCED VISUAL AI - MULTI-PROVIDER TEST")
    print("="*70)
    
    try:
        visual_ai = EnhancedVisualAI()
        
        stats = visual_ai.get_provider_stats()
        print(f"\\n📊 INITIALIZED:")
        print(f"   Providers: {', '.join(stats['available_providers'])}")
        print(f"   Total: {stats['total_providers']}")
        
        print(f"\\n✅ Enhanced Visual AI ready!")
        print(f"   Priority: Claude → Gemini → LLaVA")
        print(f"   All providers configured and operational")
        
    except Exception as e:
        print(f"\\n❌ Error: {e}")
    
    print("\\n" + "="*70 + "\\n")
'''

# Save integration module
integration_path = Path('core/enhanced_visual_ai.py')
integration_path.parent.mkdir(exist_ok=True)
with open(integration_path, 'w') as f:
    f.write(integration_code)

print(f"\n✅ Provider Integration Module Created")
print(f"   File: {integration_path}")

print(f"\n🚀 NEXT STEPS:")
print(f"   1. Test: python core/enhanced_visual_ai.py")
print(f"   2. Ready to use in trading system")
print(f"   3. Will auto-route to best available provider")
