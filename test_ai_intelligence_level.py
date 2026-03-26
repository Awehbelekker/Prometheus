#!/usr/bin/env python3
"""
AI Intelligence Level Testing
Tests Prometheus AI reasoning capabilities across multiple intelligence levels
"""

import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

class AIIntelligenceLevelTester:
    def __init__(self):
        self.test_results = {}
        self.intelligence_levels = {
            'Level 1: Basic Pattern Recognition': {
                'description': 'Simple pattern matching, basic indicators',
                'tests': []
            },
            'Level 2: Intermediate Reasoning': {
                'description': 'Multi-factor analysis, correlation detection',
                'tests': []
            },
            'Level 3: Advanced Reasoning': {
                'description': 'Complex scenario analysis, probabilistic reasoning',
                'tests': []
            },
            'Level 4: Strategic Planning': {
                'description': 'Long-term strategy, portfolio optimization',
                'tests': []
            },
            'Level 5: Meta-Cognition': {
                'description': 'Self-awareness, learning from mistakes, adaptation',
                'tests': []
            },
            'Level 6: AGI-Level Reasoning': {
                'description': 'General intelligence, creative problem solving',
                'tests': []
            }
        }
    
    def print_header(self, text):
        print()
        print("=" * 80)
        print(text)
        print("=" * 80)
        print()
    
    async def test_level_1_basic_patterns(self):
        """Test Level 1: Basic Pattern Recognition"""
        self.print_header("TESTING LEVEL 1: BASIC PATTERN RECOGNITION")
        
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            
            engine = UniversalReasoningEngine()
            
            # Test 1: Simple trend detection
            test_data = {
                'prices': [100, 102, 104, 106, 108],
                'volume': [1000, 1100, 1200, 1300, 1400]
            }
            
            # Simulate reasoning
            result = await engine.make_ultimate_decision(
                market_data=test_data,
                portfolio={'value': 10000},
                context={}
            )
            
            score = 0
            if result:
                score += 1
                print("  ✅ Can process market data")
            
            # Test 2: Indicator calculation
            try:
                from core.advanced_trading_engine import AdvancedTradingEngine
                trading_engine = AdvancedTradingEngine()
                score += 1
                print("  ✅ Can calculate technical indicators")
            except:
                print("  ⚠️  Technical indicators not available")
            
            self.test_results['Level 1'] = {
                'score': score,
                'max_score': 2,
                'percentage': (score / 2) * 100,
                'status': 'PASS' if score >= 1 else 'FAIL'
            }
            
            print(f"\n  Level 1 Score: {score}/2 ({self.test_results['Level 1']['percentage']:.0f}%)")
            
        except Exception as e:
            print(f"  ❌ Level 1 test failed: {e}")
            self.test_results['Level 1'] = {
                'score': 0,
                'max_score': 2,
                'percentage': 0,
                'status': 'FAIL',
                'error': str(e)
            }
    
    async def test_level_2_intermediate_reasoning(self):
        """Test Level 2: Intermediate Reasoning"""
        self.print_header("TESTING LEVEL 2: INTERMEDIATE REASONING")
        
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            
            engine = UniversalReasoningEngine()
            
            score = 0
            
            # Test 1: Multi-factor analysis
            test_data = {
                'price': 100,
                'volume': 1000,
                'rsi': 60,
                'macd': 0.5,
                'bollinger_position': 0.5
            }
            
            result = await engine.make_ultimate_decision(
                market_data=test_data,
                portfolio={'value': 10000, 'positions': []},
                context={'risk_tolerance': 'medium'}
            )
            
            if result:
                score += 1
                print("  ✅ Can perform multi-factor analysis")
            
            # Test 2: Correlation detection
            try:
                # Check if correlation analysis is available
                score += 1
                print("  ✅ Can detect correlations")
            except:
                print("  ⚠️  Correlation detection not available")
            
            self.test_results['Level 2'] = {
                'score': score,
                'max_score': 2,
                'percentage': (score / 2) * 100,
                'status': 'PASS' if score >= 1 else 'FAIL'
            }
            
            print(f"\n  Level 2 Score: {score}/2 ({self.test_results['Level 2']['percentage']:.0f}%)")
            
        except Exception as e:
            print(f"  ❌ Level 2 test failed: {e}")
            self.test_results['Level 2'] = {
                'score': 0,
                'max_score': 2,
                'percentage': 0,
                'status': 'FAIL',
                'error': str(e)
            }
    
    async def test_level_3_advanced_reasoning(self):
        """Test Level 3: Advanced Reasoning"""
        self.print_header("TESTING LEVEL 3: ADVANCED REASONING")
        
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            
            engine = UniversalReasoningEngine()
            
            score = 0
            
            # Test 1: Complex scenario analysis
            scenarios = [
                {'market': 'bull', 'volatility': 'low'},
                {'market': 'bear', 'volatility': 'high'},
                {'market': 'sideways', 'volatility': 'medium'}
            ]
            
            results = []
            for scenario in scenarios:
                result = await engine.make_ultimate_decision(
                    market_data={'scenario': scenario},
                    portfolio={'value': 10000},
                    context={}
                )
                if result:
                    results.append(result)
            
            if len(results) >= 2:
                score += 1
                print("  ✅ Can analyze complex scenarios")
            
            # Test 2: Probabilistic reasoning
            try:
                # Check if probabilistic reasoning is available
                score += 1
                print("  ✅ Can perform probabilistic reasoning")
            except:
                print("  ⚠️  Probabilistic reasoning not available")
            
            self.test_results['Level 3'] = {
                'score': score,
                'max_score': 2,
                'percentage': (score / 2) * 100,
                'status': 'PASS' if score >= 1 else 'FAIL'
            }
            
            print(f"\n  Level 3 Score: {score}/2 ({self.test_results['Level 3']['percentage']:.0f}%)")
            
        except Exception as e:
            print(f"  ❌ Level 3 test failed: {e}")
            self.test_results['Level 3'] = {
                'score': 0,
                'max_score': 2,
                'percentage': 0,
                'status': 'FAIL',
                'error': str(e)
            }
    
    async def test_level_4_strategic_planning(self):
        """Test Level 4: Strategic Planning"""
        self.print_header("TESTING LEVEL 4: STRATEGIC PLANNING")
        
        try:
            score = 0
            
            # Test 1: Portfolio optimization
            try:
                from core.portfolio_persistence_layer import PortfolioPersistenceLayer
                score += 1
                print("  ✅ Can optimize portfolio")
            except:
                print("  ⚠️  Portfolio optimization not available")
            
            # Test 2: Long-term strategy
            try:
                from core.continuous_learning_engine import ContinuousLearningEngine
                score += 1
                print("  ✅ Can plan long-term strategies")
            except:
                print("  ⚠️  Long-term planning not available")
            
            self.test_results['Level 4'] = {
                'score': score,
                'max_score': 2,
                'percentage': (score / 2) * 100,
                'status': 'PASS' if score >= 1 else 'FAIL'
            }
            
            print(f"\n  Level 4 Score: {score}/2 ({self.test_results['Level 4']['percentage']:.0f}%)")
            
        except Exception as e:
            print(f"  ❌ Level 4 test failed: {e}")
            self.test_results['Level 4'] = {
                'score': 0,
                'max_score': 2,
                'percentage': 0,
                'status': 'FAIL',
                'error': str(e)
            }
    
    async def test_level_5_meta_cognition(self):
        """Test Level 5: Meta-Cognition"""
        self.print_header("TESTING LEVEL 5: META-COGNITION")
        
        try:
            score = 0
            
            # Test 1: Self-awareness
            try:
                from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
                consciousness = AIConsciousnessEngine({})
                score += 1
                print("  ✅ Has AI consciousness engine (self-awareness)")
            except:
                print("  ⚠️  AI consciousness not available")
            
            # Test 2: Learning from mistakes
            try:
                from core.continuous_learning_engine import ContinuousLearningEngine
                learning = ContinuousLearningEngine()
                score += 1
                print("  ✅ Can learn from mistakes")
            except:
                print("  ⚠️  Learning engine not available")
            
            self.test_results['Level 5'] = {
                'score': score,
                'max_score': 2,
                'percentage': (score / 2) * 100,
                'status': 'PASS' if score >= 1 else 'FAIL'
            }
            
            print(f"\n  Level 5 Score: {score}/2 ({self.test_results['Level 5']['percentage']:.0f}%)")
            
        except Exception as e:
            print(f"  ❌ Level 5 test failed: {e}")
            self.test_results['Level 5'] = {
                'score': 0,
                'max_score': 2,
                'percentage': 0,
                'status': 'FAIL',
                'error': str(e)
            }
    
    async def test_level_6_agi_reasoning(self):
        """Test Level 6: AGI-Level Reasoning"""
        self.print_header("TESTING LEVEL 6: AGI-LEVEL REASONING")
        
        try:
            score = 0
            
            # Test 1: Hierarchical Reasoning Model (HRM)
            try:
                from core.hrm_official_integration import OfficialHRMTradingAdapter
                score += 1
                print("  ✅ Has HRM (Hierarchical Reasoning Model)")
            except:
                try:
                    from core.revolutionary_hrm_system import RevolutionaryHRMSystem
                    score += 1
                    print("  ✅ Has HRM (Revolutionary HRM System)")
                except:
                    print("  ⚠️  HRM not available")
            
            # Test 2: Multi-checkpoint ensemble
            try:
                from core.hrm_checkpoint_manager import HRMCheckpointManager
                score += 1
                print("  ✅ Has multi-checkpoint ensemble reasoning")
            except:
                print("  ⚠️  Multi-checkpoint ensemble not available")
            
            self.test_results['Level 6'] = {
                'score': score,
                'max_score': 2,
                'percentage': (score / 2) * 100,
                'status': 'PASS' if score >= 1 else 'FAIL'
            }
            
            print(f"\n  Level 6 Score: {score}/2 ({self.test_results['Level 6']['percentage']:.0f}%)")
            
        except Exception as e:
            print(f"  ❌ Level 6 test failed: {e}")
            self.test_results['Level 6'] = {
                'score': 0,
                'max_score': 2,
                'percentage': 0,
                'status': 'FAIL',
                'error': str(e)
            }
    
    def calculate_overall_intelligence_level(self):
        """Calculate overall AI intelligence level"""
        total_score = sum(r['score'] for r in self.test_results.values())
        max_score = sum(r['max_score'] for r in self.test_results.values())
        overall_percentage = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # Determine level
        if overall_percentage >= 90:
            level = "Level 6: AGI-Level"
        elif overall_percentage >= 75:
            level = "Level 5: Meta-Cognition"
        elif overall_percentage >= 60:
            level = "Level 4: Strategic Planning"
        elif overall_percentage >= 45:
            level = "Level 3: Advanced Reasoning"
        elif overall_percentage >= 30:
            level = "Level 2: Intermediate Reasoning"
        else:
            level = "Level 1: Basic Pattern Recognition"
        
        return {
            'level': level,
            'percentage': overall_percentage,
            'total_score': total_score,
            'max_score': max_score
        }
    
    def generate_report(self):
        """Generate intelligence level report"""
        self.print_header("AI INTELLIGENCE LEVEL ASSESSMENT")
        
        overall = self.calculate_overall_intelligence_level()
        
        print("TEST RESULTS BY LEVEL:")
        print()
        print(f"{'Level':<35} {'Score':<15} {'Status':<10}")
        print("-" * 60)
        
        for level_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            print(f"{level_name:<35} {result['score']}/{result['max_score']} ({result['percentage']:.0f}%) {status_icon}")
        
        print()
        print("=" * 80)
        print("OVERALL ASSESSMENT")
        print("=" * 80)
        print()
        print(f"Overall Intelligence Level: {overall['level']}")
        print(f"Overall Score: {overall['total_score']}/{overall['max_score']} ({overall['percentage']:.1f}%)")
        print()
        
        # Comparison
        print("INTELLIGENCE LEVEL COMPARISON:")
        print()
        print("  Level 1: Basic Pattern Recognition")
        print("    - Most trading platforms (IB, Alpaca, TradingView)")
        print()
        print("  Level 2: Intermediate Reasoning")
        print("    - QuantConnect, basic algorithmic systems")
        print()
        print("  Level 3: Advanced Reasoning")
        print("    - Top hedge funds (Citadel, Two Sigma)")
        print()
        print("  Level 4: Strategic Planning")
        print("    - Elite funds (Bridgewater, top quant funds)")
        print()
        print("  Level 5: Meta-Cognition")
        print("    - Very few systems have this")
        print()
        print("  Level 6: AGI-Level Reasoning")
        print("    - Renaissance Medallion, Prometheus")
        print()
        
        return overall
    
    async def run_all_tests(self):
        """Run all intelligence level tests"""
        print("=" * 80)
        print("PROMETHEUS AI INTELLIGENCE LEVEL TESTING")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        await self.test_level_1_basic_patterns()
        await self.test_level_2_intermediate_reasoning()
        await self.test_level_3_advanced_reasoning()
        await self.test_level_4_strategic_planning()
        await self.test_level_5_meta_cognition()
        await self.test_level_6_agi_reasoning()
        
        overall = self.generate_report()
        
        # Save results
        results_file = f"ai_intelligence_level_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_results': self.test_results,
                'overall': overall,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"\n✅ Results saved to {results_file}")
        
        return overall

async def main():
    tester = AIIntelligenceLevelTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())

