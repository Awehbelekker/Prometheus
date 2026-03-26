#!/usr/bin/env python3
"""
HYBRID AI TRADING ENGINE
Uses GPT-OSS (local/free) for routine decisions
Uses OpenAI API for complex analysis (low cost)
Optimizes cost while maximizing performance
"""

import os
import requests
import json
from datetime import datetime
from enum import Enum

class AITaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"           # Use GPT-OSS (free)
    MODERATE = "moderate"       # Use GPT-OSS (free)
    COMPLEX = "complex"         # Use OpenAI (low cost)
    CRITICAL = "critical"       # Use OpenAI (guaranteed quality)

class HybridAIEngine:
    """
    Hybrid AI Engine that intelligently routes tasks to:
    - GPT-OSS (local) for 80% of tasks (FREE)
    - OpenAI API for 20% of complex tasks (low cost)
    """
    
    def __init__(self):
        self.gpt_oss_endpoint = "http://localhost:5000"
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.use_openai = bool(self.openai_api_key)
        
        # Cost tracking
        self.gpt_oss_calls = 0
        self.openai_calls = 0
        self.total_cost = 0.0
        
        # Performance tracking
        self.decisions_made = 0
        self.cost_saved = 0.0
        
    def check_gpt_oss_available(self):
        """Check if GPT-OSS is available"""
        try:
            response = requests.get(f"{self.gpt_oss_endpoint}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def analyze_market(self, symbol, data, complexity=AITaskComplexity.MODERATE):
        """
        Analyze market data using appropriate AI
        
        SIMPLE/MODERATE: Use GPT-OSS (free)
        COMPLEX/CRITICAL: Use OpenAI (low cost)
        """
        
        # Try GPT-OSS first for simple/moderate tasks
        if complexity in [AITaskComplexity.SIMPLE, AITaskComplexity.MODERATE]:
            if self.check_gpt_oss_available():
                result = self._analyze_with_gpt_oss(symbol, data)
                if result:
                    self.gpt_oss_calls += 1
                    self.cost_saved += 0.0002  # Saved ~$0.0002 per call
                    return result
        
        # Fall back to OpenAI for complex tasks or if GPT-OSS unavailable
        if self.use_openai:
            result = self._analyze_with_openai(symbol, data, complexity)
            if result:
                self.openai_calls += 1
                self.total_cost += 0.0002  # ~$0.0002 per call with gpt-4o-mini
                return result
        
        # Final fallback: rule-based analysis
        return self._analyze_with_rules(symbol, data)
    
    def _analyze_with_gpt_oss(self, symbol, data):
        """Analyze using local GPT-OSS (FREE)"""
        try:
            prompt = f"""Analyze {symbol} trading opportunity:
Price: ${data.get('price', 0)}
Volume: {data.get('volume', 0)}
Trend: {data.get('trend', 'neutral')}

Provide: BUY/SELL/HOLD decision with confidence (0-100)"""

            response = requests.post(
                f"{self.gpt_oss_endpoint}/v1/chat/completions",
                json={
                    "model": "gpt-oss-20b",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 150,
                    "temperature": 0.3
                },
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                decision_text = result['choices'][0]['message']['content']
                
                # Parse decision
                decision = self._parse_decision(decision_text)
                decision['source'] = 'GPT-OSS (FREE)'
                decision['cost'] = 0.0
                return decision
                
        except Exception as e:
            print(f"GPT-OSS error: {e}")
            return None
    
    def _analyze_with_openai(self, symbol, data, complexity):
        """Analyze using OpenAI API (low cost)"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            # Use gpt-4o-mini for cost efficiency
            model = "gpt-4o-mini"  # $0.00015 per 1K tokens
            
            prompt = f"""Advanced analysis for {symbol}:
Price: ${data.get('price', 0)}
Volume: {data.get('volume', 0)}
Trend: {data.get('trend', 'neutral')}
Market Cap: ${data.get('market_cap', 0)}
RSI: {data.get('rsi', 50)}
MACD: {data.get('macd', 0)}

Complexity: {complexity.value}

Provide detailed BUY/SELL/HOLD decision with:
1. Decision (BUY/SELL/HOLD)
2. Confidence (0-100)
3. Reasoning (brief)
4. Risk level (LOW/MEDIUM/HIGH)"""

            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            decision_text = response.choices[0].message.content
            decision = self._parse_decision(decision_text)
            decision['source'] = f'OpenAI ({model})'
            decision['cost'] = 0.0002  # Approximate cost
            
            return decision
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None
    
    def _analyze_with_rules(self, symbol, data):
        """Fallback rule-based analysis (FREE)"""
        price = data.get('price', 0)
        volume = data.get('volume', 0)
        trend = data.get('trend', 'neutral')
        
        # Simple rule-based logic
        if trend == 'bullish' and volume > 1000000:
            decision = 'BUY'
            confidence = 65
        elif trend == 'bearish' and volume > 1000000:
            decision = 'SELL'
            confidence = 65
        else:
            decision = 'HOLD'
            confidence = 50
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': f'Rule-based: {trend} trend with {volume} volume',
            'risk': 'MEDIUM',
            'source': 'Rule-Based (FREE)',
            'cost': 0.0
        }
    
    def _parse_decision(self, text):
        """Parse AI decision text"""
        text_upper = text.upper()
        
        # Determine decision
        if 'BUY' in text_upper:
            decision = 'BUY'
        elif 'SELL' in text_upper:
            decision = 'SELL'
        else:
            decision = 'HOLD'
        
        # Extract confidence (look for numbers)
        import re
        confidence_match = re.search(r'(\d+)%?', text)
        confidence = int(confidence_match.group(1)) if confidence_match else 50
        
        # Determine risk
        if 'HIGH' in text_upper:
            risk = 'HIGH'
        elif 'LOW' in text_upper:
            risk = 'LOW'
        else:
            risk = 'MEDIUM'
        
        return {
            'decision': decision,
            'confidence': min(confidence, 100),
            'reasoning': text[:200],
            'risk': risk
        }
    
    def get_statistics(self):
        """Get usage statistics"""
        total_calls = self.gpt_oss_calls + self.openai_calls
        gpt_oss_percent = (self.gpt_oss_calls / total_calls * 100) if total_calls > 0 else 0
        openai_percent = (self.openai_calls / total_calls * 100) if total_calls > 0 else 0
        
        return {
            'total_decisions': total_calls,
            'gpt_oss_calls': self.gpt_oss_calls,
            'gpt_oss_percent': f"{gpt_oss_percent:.1f}%",
            'openai_calls': self.openai_calls,
            'openai_percent': f"{openai_percent:.1f}%",
            'total_cost': f"${self.total_cost:.4f}",
            'cost_saved': f"${self.cost_saved:.4f}",
            'cost_per_decision': f"${(self.total_cost / total_calls):.6f}" if total_calls > 0 else "$0.000000"
        }

# Example usage
if __name__ == "__main__":
    print("🤖 HYBRID AI TRADING ENGINE")
    print("=" * 60)
    print("💰 Cost Optimization: GPT-OSS (free) + OpenAI (low cost)")
    print("=" * 60)
    
    engine = HybridAIEngine()
    
    # Test with sample data
    test_data = {
        'price': 150.25,
        'volume': 5000000,
        'trend': 'bullish',
        'rsi': 65,
        'macd': 2.5
    }
    
    print("\n📊 Analyzing AAPL...")
    
    # Simple analysis (use GPT-OSS)
    result1 = engine.analyze_market('AAPL', test_data, AITaskComplexity.SIMPLE)
    print(f"\nSimple Analysis: {result1['decision']} ({result1['confidence']}%)")
    print(f"Source: {result1['source']} | Cost: ${result1['cost']:.4f}")
    
    # Complex analysis (use OpenAI if available)
    result2 = engine.analyze_market('AAPL', test_data, AITaskComplexity.COMPLEX)
    print(f"\nComplex Analysis: {result2['decision']} ({result2['confidence']}%)")
    print(f"Source: {result2['source']} | Cost: ${result2['cost']:.4f}")
    
    # Show statistics
    print("\n" + "=" * 60)
    print("📊 USAGE STATISTICS")
    print("=" * 60)
    stats = engine.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n[CHECK] Hybrid AI Engine Ready!")
    print("💡 Uses GPT-OSS (free) for 80% of decisions")
    print("💡 Uses OpenAI (low cost) for 20% complex analysis")
    print("💰 Estimated cost: <$0.01 per 100 decisions")

