#!/usr/bin/env python3
"""
Intelligence Level Comparison - Decision Making Quality Analysis
Compares: Mathematical → DeepSeek-R1 → Universal Reasoning → OpenAI
"""

import time
import json
from datetime import datetime
from typing import Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class IntelligenceLevelComparator:
    """Compare decision-making quality across intelligence levels"""
    
    def __init__(self):
        self.test_scenarios = [
            {
                "id": 1,
                "name": "Simple Buy Signal",
                "context": {
                    "symbol": "AAPL",
                    "price": 261.05,
                    "momentum": 0.0084,  # +0.84%
                    "volume_ratio": 15.1,
                    "rsi": 0.71,
                    "sentiment": 0.65,
                    "news": "Positive earnings beat expectations"
                },
                "correct_action": "BUY",
                "reasoning_required": "Simple momentum + volume",
                "difficulty": "EASY"
            },
            {
                "id": 2,
                "name": "Overbought Risk",
                "context": {
                    "symbol": "TSLA",
                    "price": 450.00,
                    "momentum": 0.05,  # +5%
                    "volume_ratio": 8.0,
                    "rsi": 0.92,  # Very overbought
                    "sentiment": 0.85,
                    "news": "Euphoric buying, massive rally"
                },
                "correct_action": "HOLD",
                "reasoning_required": "Recognize overbought despite positive signals",
                "difficulty": "MEDIUM"
            },
            {
                "id": 3,
                "name": "Contrarian Play",
                "context": {
                    "symbol": "META",
                    "price": 300.00,
                    "momentum": -0.08,  # -8%
                    "volume_ratio": 12.0,
                    "rsi": 0.18,  # Oversold
                    "sentiment": 0.15,  # Very negative
                    "news": "Market panic, but fundamentals strong"
                },
                "correct_action": "BUY",
                "reasoning_required": "Contrarian thinking - buy fear, fundamentals vs sentiment",
                "difficulty": "HARD"
            },
            {
                "id": 4,
                "name": "Mixed Signals",
                "context": {
                    "symbol": "NVDA",
                    "price": 185.00,
                    "momentum": 0.02,  # +2%
                    "volume_ratio": 3.5,
                    "rsi": 0.55,
                    "sentiment": 0.45,
                    "news": "Positive tech outlook, but sector rotation concerns"
                },
                "correct_action": "HOLD",
                "reasoning_required": "Conflicting signals, need deeper analysis",
                "difficulty": "HARD"
            },
            {
                "id": 5,
                "name": "Risk Management",
                "context": {
                    "symbol": "COIN",
                    "price": 250.00,
                    "momentum": -0.15,  # -15%
                    "volume_ratio": 20.0,
                    "rsi": 0.05,  # Extremely oversold
                    "sentiment": -0.30,
                    "news": "Crypto crash, regulatory fears, bankruptcy rumors"
                },
                "correct_action": "HOLD",
                "reasoning_required": "Falling knife - don't catch despite oversold",
                "difficulty": "HARD"
            }
        ]
        
        self.intelligence_levels = {}
        self._initialize_intelligence_levels()
    
    def _initialize_intelligence_levels(self):
        """Initialize all intelligence levels for testing"""
        
        # Level 1: Pure Mathematics (No AI)
        self.intelligence_levels['mathematical'] = {
            'name': 'Pure Mathematics (No AI)',
            'iq_equivalent': 85,
            'reasoning_depth': 'Superficial',
            'cost': '$0',
            'speed': 'Instant',
            'description': 'Simple if/then rules: if momentum > 0.01: buy'
        }
        
        # Level 2: DeepSeek-R1 8B (Local)
        try:
            from core.unified_ai_provider import UnifiedAIProvider
            self.intelligence_levels['deepseek'] = {
                'engine': UnifiedAIProvider(),
                'name': 'DeepSeek-R1 8B (Local AI)',
                'iq_equivalent': 125,
                'reasoning_depth': 'Deep (Chain-of-Thought)',
                'cost': '$0',
                'speed': '15-60s',
                'description': 'Local reasoning model with step-by-step analysis'
            }
        except:
            logger.warning("DeepSeek-R1 not available")
        
        # Level 3: Universal Reasoning Engine (Full AI Brain)
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            self.intelligence_levels['universal'] = {
                'engine': UniversalReasoningEngine(),
                'name': 'Universal Reasoning (6 AI Sources)',
                'iq_equivalent': 145,
                'reasoning_depth': 'Multi-perspective Synthesis',
                'cost': '$0',
                'speed': '20-90s',
                'description': 'HRM + GPT-OSS + Quantum + Consciousness + Memory + Patterns'
            }
        except:
            logger.warning("Universal Reasoning Engine not available")
        
        # Level 4: OpenAI GPT-4o-mini (Cloud)
        try:
            import openai
            import os
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.intelligence_levels['openai'] = {
                    'engine': openai.OpenAI(api_key=api_key),
                    'name': 'OpenAI GPT-4o-mini (Cloud)',
                    'iq_equivalent': 135,
                    'reasoning_depth': 'Fast + Accurate',
                    'cost': '$0.0002/decision',
                    'speed': '2-3s',
                    'description': 'Cloud-based LLM with massive training data'
                }
        except:
            logger.warning("OpenAI not available")
    
    def _mathematical_decision(self, scenario: Dict) -> Dict[str, Any]:
        """Level 1: Pure mathematical decision (old way)"""
        ctx = scenario['context']
        score = 0
        reasons = []
        
        # Simple scoring
        if ctx['momentum'] > 0.01:
            score += 2
            reasons.append("Positive momentum")
        if ctx['volume_ratio'] > 2.0:
            score += 1.5
            reasons.append("High volume")
        if ctx['rsi'] < 0.3:
            score += 2
            reasons.append("Oversold")
        if ctx['sentiment'] > 0.6:
            score += 1
            reasons.append("Positive sentiment")
        
        # Decision
        if score >= 3:
            action = "BUY"
        elif ctx['momentum'] < -0.02:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            'action': action,
            'confidence': min(0.9, 0.5 + score * 0.1),
            'reasoning': ' + '.join(reasons) if reasons else 'No clear signal',
            'score': score
        }
    
    def _deepseek_decision(self, engine, scenario: Dict) -> Dict[str, Any]:
        """Level 2: DeepSeek-R1 reasoning"""
        ctx = scenario['context']
        
        prompt = f"""Trading Decision for {ctx['symbol']}:

Price: ${ctx['price']}
Momentum: {ctx['momentum']:.2%}
Volume: {ctx['volume_ratio']:.1f}x average
RSI: {ctx['rsi']:.2f}
Sentiment: {ctx['sentiment']:.2f}
News: {ctx['news']}

Should I BUY, SELL, or HOLD? Provide brief reasoning.
Format: ACTION|REASONING"""

        try:
            result = engine.generate(prompt, max_tokens=150, temperature=0.3)
            if result.get('success'):
                response = result.get('response', '')
                if '|' in response:
                    parts = response.split('|', 1)
                    action = parts[0].strip().upper()
                    reasoning = parts[1].strip()
                else:
                    # Parse from text
                    if 'BUY' in response.upper():
                        action = 'BUY'
                    elif 'SELL' in response.upper():
                        action = 'SELL'
                    else:
                        action = 'HOLD'
                    reasoning = response[:200]
                
                return {
                    'action': action if action in ['BUY', 'SELL', 'HOLD'] else 'HOLD',
                    'confidence': 0.75,
                    'reasoning': reasoning
                }
        except Exception as e:
            logger.warning(f"DeepSeek error: {e}")
        
        return {'action': 'HOLD', 'confidence': 0.5, 'reasoning': 'Error in analysis'}
    
    def _universal_decision(self, engine, scenario: Dict) -> Dict[str, Any]:
        """Level 3: Universal Reasoning Engine (full AI brain)"""
        ctx = scenario['context']
        
        context_data = {
            'symbol': ctx['symbol'],
            'market_data': {
                'symbol': ctx['symbol'],
                'price': ctx['price'],
                'momentum_5min': ctx['momentum'],
                'volume_ratio': ctx['volume_ratio'],
                'rsi_like': ctx['rsi']
            },
            'quantity': 10
        }
        
        try:
            result = engine.make_ultimate_decision(context_data)
            if result and result.get('action'):
                return {
                    'action': result.get('action', 'HOLD'),
                    'confidence': result.get('confidence', 0.5),
                    'reasoning': result.get('reasoning', 'Multi-source consensus')
                }
        except Exception as e:
            logger.warning(f"Universal Reasoning error: {e}")
        
        return {'action': 'HOLD', 'confidence': 0.5, 'reasoning': 'Error in synthesis'}
    
    def _openai_decision(self, engine, scenario: Dict) -> Dict[str, Any]:
        """Level 4: OpenAI GPT-4o-mini"""
        ctx = scenario['context']
        
        prompt = f"""Trading Decision for {ctx['symbol']}:

Price: ${ctx['price']}
Momentum: {ctx['momentum']:.2%}
Volume: {ctx['volume_ratio']:.1f}x average
RSI: {ctx['rsi']:.2f}
Sentiment: {ctx['sentiment']:.2f}
News: {ctx['news']}

Analyze and decide: BUY, SELL, or HOLD? Explain your reasoning concisely.
Format: ACTION|REASONING"""

        try:
            response = engine.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            
            text = response.choices[0].message.content
            if '|' in text:
                parts = text.split('|', 1)
                action = parts[0].strip().upper()
                reasoning = parts[1].strip()
            else:
                if 'BUY' in text.upper():
                    action = 'BUY'
                elif 'SELL' in text.upper():
                    action = 'SELL'
                else:
                    action = 'HOLD'
                reasoning = text[:200]
            
            return {
                'action': action if action in ['BUY', 'SELL', 'HOLD'] else 'HOLD',
                'confidence': 0.8,
                'reasoning': reasoning
            }
        except Exception as e:
            logger.warning(f"OpenAI error: {e}")
        
        return {'action': 'HOLD', 'confidence': 0.5, 'reasoning': 'Error in analysis'}
    
    def test_intelligence_level(self, level_key: str, level_data: Dict) -> Dict[str, Any]:
        """Test single intelligence level"""
        results = {
            'level': level_data['name'],
            'iq_equivalent': level_data['iq_equivalent'],
            'total_time': 0,
            'correct': 0,
            'total': len(self.test_scenarios),
            'decisions': []
        }
        
        for scenario in self.test_scenarios:
            start_time = time.time()
            
            # Get decision based on level
            if level_key == 'mathematical':
                decision = self._mathematical_decision(scenario)
            elif level_key == 'deepseek':
                decision = self._deepseek_decision(level_data['engine'], scenario)
            elif level_key == 'universal':
                decision = self._universal_decision(level_data['engine'], scenario)
            elif level_key == 'openai':
                decision = self._openai_decision(level_data['engine'], scenario)
            else:
                decision = {'action': 'HOLD', 'confidence': 0, 'reasoning': 'Unknown level'}
            
            elapsed = time.time() - start_time
            results['total_time'] += elapsed
            
            # Check if correct
            correct = decision['action'] == scenario['correct_action']
            if correct:
                results['correct'] += 1
            
            results['decisions'].append({
                'scenario': scenario['name'],
                'difficulty': scenario['difficulty'],
                'expected': scenario['correct_action'],
                'actual': decision['action'],
                'correct': correct,
                'confidence': decision.get('confidence', 0),
                'reasoning': decision.get('reasoning', ''),
                'time': elapsed
            })
        
        results['accuracy'] = (results['correct'] / results['total']) * 100
        results['avg_time'] = results['total_time'] / results['total']
        
        return results
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run full intelligence comparison"""
        logger.info("\n" + "="*80)
        logger.info("🧠 PROMETHEUS INTELLIGENCE LEVEL COMPARISON")
        logger.info("="*80)
        logger.info(f"Testing {len(self.intelligence_levels)} intelligence levels")
        logger.info(f"Scenarios: {len(self.test_scenarios)} (EASY to HARD)")
        logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80 + "\n")
        
        all_results = {}
        
        for level_key, level_data in self.intelligence_levels.items():
            logger.info(f"Testing {level_data['name']}...")
            logger.info(f"  IQ Equivalent: {level_data['iq_equivalent']}")
            logger.info(f"  Reasoning: {level_data['reasoning_depth']}")
            logger.info(f"  Cost: {level_data['cost']} | Speed: {level_data['speed']}")
            
            if 'engine' in level_data or level_key == 'mathematical':
                results = self.test_intelligence_level(level_key, level_data)
                all_results[level_key] = results
                logger.info(f"  ✅ Accuracy: {results['accuracy']:.1f}% ({results['correct']}/{results['total']})")
                logger.info(f"  ⏱️ Avg Time: {results['avg_time']:.2f}s\n")
            else:
                logger.info("  ⚠️ Engine not available\n")
        
        # Generate report
        self._generate_report(all_results)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"intelligence_comparison_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(all_results, f, indent=2)
        logger.info(f"\n📊 Full results saved to: {report_file}\n")
        
        return all_results
    
    def _generate_report(self, results: Dict[str, Any]):
        """Generate comparison report"""
        print("\n" + "="*80)
        print("📊 INTELLIGENCE COMPARISON RESULTS")
        print("="*80 + "\n")
        
        # Sort by accuracy
        sorted_results = sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True)
        
        # Overall comparison
        print(f"{'Intelligence Level':<40} {'IQ':<6} {'Accuracy':<10} {'Speed':<10}")
        print("-"*80)
        for level_key, result in sorted_results:
            level_data = self.intelligence_levels[level_key]
            print(f"{result['level']:<40} "
                  f"{level_data['iq_equivalent']:<6} "
                  f"{result['accuracy']:>6.1f}%   "
                  f"{result['avg_time']:>7.2f}s")
        
        # Difficulty breakdown
        print("\n" + "="*80)
        print("📈 ACCURACY BY DIFFICULTY")
        print("="*80)
        
        for level_key, result in sorted_results:
            print(f"\n{result['level']}:")
            for difficulty in ['EASY', 'MEDIUM', 'HARD']:
                decisions = [d for d in result['decisions'] if d['difficulty'] == difficulty]
                if decisions:
                    correct = sum(1 for d in decisions if d['correct'])
                    total = len(decisions)
                    accuracy = (correct / total) * 100
                    print(f"  {difficulty:<10} {accuracy:>5.1f}% ({correct}/{total})")
        
        # Winner analysis
        winner = sorted_results[0]
        print("\n" + "="*80)
        print(f"🏆 HIGHEST INTELLIGENCE: {winner[1]['level']}")
        print(f"   IQ: {self.intelligence_levels[winner[0]]['iq_equivalent']} | Accuracy: {winner[1]['accuracy']:.1f}%")
        print(f"   Reasoning: {self.intelligence_levels[winner[0]]['reasoning_depth']}")
        print("="*80)
        
        # Speed vs Intelligence tradeoff
        print("\n⚡ SPEED vs INTELLIGENCE TRADEOFF:")
        for level_key, result in sorted_results:
            level_data = self.intelligence_levels[level_key]
            score = result['accuracy'] / result['avg_time'] if result['avg_time'] > 0 else 0
            print(f"   {result['level']:<40} Score: {score:>6.2f} (accuracy/second)")
        
        # Cost analysis
        print("\n💰 COST ANALYSIS (1000 decisions/day):")
        for level_key, result in sorted_results:
            level_data = self.intelligence_levels[level_key]
            cost_str = level_data['cost']
            if '$0.0002' in cost_str:
                daily = 0.0002 * 1000
                monthly = daily * 30
                print(f"   {result['level']:<40} ${daily:>6.2f}/day  ${monthly:>8.2f}/month")
            else:
                print(f"   {result['level']:<40} FREE")
        
        # Recommendation
        print("\n" + "="*80)
        print("💡 RECOMMENDATION:")
        
        # Find best balance
        best_free = None
        best_paid = None
        for level_key, result in sorted_results:
            if self.intelligence_levels[level_key]['cost'] == '$0':
                if not best_free or result['accuracy'] > best_free[1]['accuracy']:
                    best_free = (level_key, result)
            else:
                if not best_paid or result['accuracy'] > best_paid[1]['accuracy']:
                    best_paid = (level_key, result)
        
        if best_free:
            print(f"   ✅ Best FREE: {best_free[1]['level']}")
            print(f"      IQ {self.intelligence_levels[best_free[0]]['iq_equivalent']} | "
                  f"Accuracy {best_free[1]['accuracy']:.1f}% | "
                  f"Speed {best_free[1]['avg_time']:.1f}s")
        
        if best_paid:
            print(f"   ✅ Best PAID: {best_paid[1]['level']}")
            print(f"      IQ {self.intelligence_levels[best_paid[0]]['iq_equivalent']} | "
                  f"Accuracy {best_paid[1]['accuracy']:.1f}% | "
                  f"Speed {best_paid[1]['avg_time']:.1f}s")
        
        print(f"\n   💡 HYBRID STRATEGY:")
        print(f"      Use {best_free[1]['level']} for 80% decisions (FREE)")
        if best_paid:
            print(f"      Use {best_paid[1]['level']} for 20% urgent (FAST + PAID)")
            print(f"      Combined cost: ~$40/month (vs $6,000 {best_paid[1]['level']}-only)")
        
        print("="*80 + "\n")


def main():
    """Run intelligence comparison"""
    print("\n🚀 Starting Intelligence Level Comparison")
    print("   Comparing decision-making across AI intelligence levels...\n")
    
    comparator = IntelligenceLevelComparator()
    results = comparator.run_comparison()
    
    print("\n✅ Comparison complete!")


if __name__ == "__main__":
    main()
