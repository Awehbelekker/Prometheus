#!/usr/bin/env python3      78
""" 
AI Capabilities Benchmark: Prometheus vs OpenAI
Comprehensive comparison of reasoning, decision-making, and trading intelligence
"""

import sys
import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import numpy as np

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'ai_vs_openai_benchmark_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIVsOpenAIBenchmark:
    """
    Comprehensive benchmark comparing Prometheus AI vs OpenAI
    """
    
    def __init__(self):
        self.results = {
            'prometheus': {},
            'openai': {},
            'comparison': {}
        }
        self.test_scenarios = self._create_test_scenarios()
        
    def _create_test_scenarios(self) -> List[Dict]:
        """Create diverse test scenarios for benchmarking"""
        return [
            {
                'name': 'Market Analysis',
                'description': 'Analyze current market conditions and provide trading recommendation',
                'market_data': {
                    'symbol': 'SPY',
                    'price': 450.0,
                    'volume': 50000000,
                    'volatility': 0.02,
                    'trend': 'up',
                    'rsi': 65,
                    'macd': 1.5
                },
                'context': 'Market showing bullish signals with increasing volume'
            },
            {
                'name': 'Risk Assessment',
                'description': 'Assess risk for a potential trade',
                'market_data': {
                    'symbol': 'BTC-USD',
                    'price': 35000.0,
                    'volatility': 0.05,
                    'volume': 2000000000,
                    'trend': 'volatile'
                },
                'context': 'High volatility crypto market, assess entry risk'
            },
            {
                'name': 'Portfolio Optimization',
                'description': 'Optimize portfolio allocation across multiple assets',
                'portfolio': {
                    'SPY': {'quantity': 100, 'value': 45000},
                    'QQQ': {'quantity': 50, 'value': 18000},
                    'BTC-USD': {'quantity': 0.5, 'value': 17500}
                },
                'context': 'Rebalance portfolio for better risk-adjusted returns'
            },
            {
                'name': 'Pattern Recognition',
                'description': 'Identify trading patterns in historical data',
                'market_data': {
                    'symbol': 'AAPL',
                    'price': 175.0,
                    'historical_pattern': 'head_and_shoulders',
                    'volume_spike': True
                },
                'context': 'Identify if pattern suggests reversal or continuation'
            },
            {
                'name': 'Multi-Timeframe Analysis',
                'description': 'Analyze across multiple timeframes',
                'market_data': {
                    'symbol': 'MSFT',
                    'price': 380.0,
                    '1min': {'trend': 'up', 'volume': 'high'},
                    '5min': {'trend': 'up', 'volume': 'medium'},
                    '1hour': {'trend': 'sideways', 'volume': 'low'},
                    '1day': {'trend': 'up', 'volume': 'medium'}
                },
                'context': 'Conflicting signals across timeframes, determine best action'
            },
            {
                'name': 'Regime Detection',
                'description': 'Detect current market regime',
                'market_data': {
                    'symbol': 'SPY',
                    'price': 450.0,
                    'volatility': 0.03,
                    'vix': 18.5,
                    'trend': 'uncertain',
                    'volume': 'declining'
                },
                'context': 'Market showing mixed signals, determine regime'
            },
            {
                'name': 'Strategy Selection',
                'description': 'Select best trading strategy for current conditions',
                'market_data': {
                    'symbol': 'TSLA',
                    'price': 250.0,
                    'volatility': 0.04,
                    'trend': 'up',
                    'volume': 'high'
                },
                'strategies': ['momentum', 'mean_reversion', 'breakout', 'swing'],
                'context': 'Select optimal strategy for current market conditions'
            },
            {
                'name': 'Confidence Calibration',
                'description': 'Provide well-calibrated confidence scores',
                'market_data': {
                    'symbol': 'NVDA',
                    'price': 500.0,
                    'indicators': {'rsi': 55, 'macd': 0.2, 'bollinger': 'middle'},
                    'trend': 'sideways'
                },
                'context': 'Uncertain market conditions, calibrate confidence appropriately'
            }
        ]
    
    async def test_prometheus(self, scenario: Dict) -> Dict:
        """Test Prometheus AI capabilities"""
        logger.info(f"Testing Prometheus: {scenario['name']}")
        
        start_time = time.time()
        result = {
            'scenario': scenario['name'],
            'success': False,
            'response': None,
            'reasoning': None,
            'confidence': None,
            'action': None,
            'time_taken': 0,
            'error': None
        }
        
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            
            engine = UniversalReasoningEngine()
            
            # Prepare context
            context = {
                'market_data': scenario.get('market_data', {}),
                'portfolio': scenario.get('portfolio', {}),
                'user_profile': {},
                'trading_history': [],
                'risk_preferences': {}
            }
            
            # Make decision
            decision = engine.make_ultimate_decision(context)
            
            result['success'] = True
            result['response'] = decision
            result['action'] = decision.get('action', 'UNKNOWN')
            result['confidence'] = decision.get('confidence', 0.0)
            result['reasoning'] = decision.get('reasoning_sources', {})
            result['time_taken'] = time.time() - start_time
            
            logger.info(f"  ✅ Prometheus: {result['action']} (confidence: {result['confidence']:.3f}, time: {result['time_taken']:.3f}s)")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"  ❌ Prometheus failed: {e}")
            import traceback
            traceback.print_exc()
        
        return result
    
    async def test_openai(self, scenario: Dict) -> Dict:
        """Test OpenAI capabilities"""
        logger.info(f"Testing OpenAI: {scenario['name']}")
        
        start_time = time.time()
        result = {
            'scenario': scenario['name'],
            'success': False,
            'response': None,
            'reasoning': None,
            'confidence': None,
            'action': None,
            'time_taken': 0,
            'error': None
        }
        
        try:
            import openai
            import os
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                result['error'] = 'OPENAI_API_KEY not found'
                logger.warning("  ⚠️ OpenAI API key not found - skipping OpenAI test")
                return result
            
            # Prepare prompt
            prompt = self._create_openai_prompt(scenario)
            
            # Call OpenAI
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert trading AI. Provide trading recommendations with confidence scores."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            # Parse response
            parsed = self._parse_openai_response(response_text)
            
            result['success'] = True
            result['response'] = response_text
            result['action'] = parsed.get('action', 'UNKNOWN')
            result['confidence'] = parsed.get('confidence', 0.5)
            result['reasoning'] = parsed.get('reasoning', '')
            result['time_taken'] = time.time() - start_time
            
            logger.info(f"  ✅ OpenAI: {result['action']} (confidence: {result['confidence']:.3f}, time: {result['time_taken']:.3f}s)")
            
        except ImportError:
            result['error'] = 'OpenAI library not installed'
            logger.warning("  ⚠️ OpenAI library not installed - install with: pip install openai")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"  ❌ OpenAI failed: {e}")
        
        return result
    
    def _create_openai_prompt(self, scenario: Dict) -> str:
        """Create prompt for OpenAI"""
        prompt = f"""
Scenario: {scenario['name']}
Description: {scenario['description']}
Context: {scenario.get('context', '')}

Market Data:
{json.dumps(scenario.get('market_data', {}), indent=2)}

"""
        if 'portfolio' in scenario:
            prompt += f"Portfolio:\n{json.dumps(scenario['portfolio'], indent=2)}\n\n"
        
        prompt += """
Please provide:
1. Recommended action (BUY, SELL, or HOLD)
2. Confidence score (0.0 to 1.0)
3. Brief reasoning

Format your response as JSON:
{
  "action": "BUY|SELL|HOLD",
  "confidence": 0.0-1.0,
  "reasoning": "your reasoning here"
}
"""
        return prompt
    
    def _parse_openai_response(self, response_text: str) -> Dict:
        """Parse OpenAI response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed
        except:
            pass
        
        # Fallback: extract action and confidence from text
        action = 'HOLD'
        confidence = 0.5
        
        if 'BUY' in response_text.upper():
            action = 'BUY'
        elif 'SELL' in response_text.upper():
            action = 'SELL'
        
        # Try to find confidence number
        import re
        conf_match = re.search(r'confidence[:\s]+([0-9.]+)', response_text, re.IGNORECASE)
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
                if confidence > 1.0:
                    confidence = confidence / 100.0
            except:
                pass
        
        return {
            'action': action,
            'confidence': confidence,
            'reasoning': response_text
        }
    
    async def run_benchmark(self):
        """Run comprehensive benchmark"""
        logger.info("=" * 80)
        logger.info("AI CAPABILITIES BENCHMARK: PROMETHEUS vs OPENAI")
        logger.info("=" * 80)
        logger.info("")
        
        prometheus_results = []
        openai_results = []
        
        for i, scenario in enumerate(self.test_scenarios, 1):
            logger.info(f"\n[{i}/{len(self.test_scenarios)}] Testing: {scenario['name']}")
            logger.info("-" * 80)
            
            # Test Prometheus
            prometheus_result = await self.test_prometheus(scenario)
            prometheus_results.append(prometheus_result)
            
            # Test OpenAI
            openai_result = await self.test_openai(scenario)
            openai_results.append(openai_result)
            
            # Brief comparison
            if prometheus_result['success'] and openai_result['success']:
                logger.info(f"\nComparison:")
                logger.info(f"  Prometheus: {prometheus_result['action']} ({prometheus_result['confidence']:.3f}) - {prometheus_result['time_taken']:.3f}s")
                logger.info(f"  OpenAI:     {openai_result['action']} ({openai_result['confidence']:.3f}) - {openai_result['time_taken']:.3f}s")
        
        # Calculate metrics
        self.results['prometheus'] = self._calculate_metrics(prometheus_results)
        self.results['openai'] = self._calculate_metrics(openai_results)
        self.results['comparison'] = self._compare_results(prometheus_results, openai_results)
        
        # Generate report
        self._generate_report()
        
        return self.results
    
    def _calculate_metrics(self, results: List[Dict]) -> Dict:
        """Calculate performance metrics"""
        successful = [r for r in results if r['success']]
        
        if not successful:
            return {
                'success_rate': 0.0,
                'avg_time': 0.0,
                'avg_confidence': 0.0,
                'total_tests': len(results)
            }
        
        return {
            'success_rate': len(successful) / len(results),
            'avg_time': np.mean([r['time_taken'] for r in successful]),
            'avg_confidence': np.mean([r['confidence'] for r in successful]),
            'total_tests': len(results),
            'successful_tests': len(successful)
        }
    
    def _compare_results(self, prometheus_results: List[Dict], openai_results: List[Dict]) -> Dict:
        """Compare Prometheus vs OpenAI results"""
        comparison = {
            'speed': {},
            'accuracy': {},
            'confidence': {},
            'overall': {}
        }
        
        # Speed comparison
        prometheus_times = [r['time_taken'] for r in prometheus_results if r['success']]
        openai_times = [r['time_taken'] for r in openai_results if r['success']]
        
        if prometheus_times and openai_times:
            comparison['speed'] = {
                'prometheus_avg': np.mean(prometheus_times),
                'openai_avg': np.mean(openai_times),
                'faster': 'Prometheus' if np.mean(prometheus_times) < np.mean(openai_times) else 'OpenAI',
                'speedup': np.mean(openai_times) / np.mean(prometheus_times) if np.mean(prometheus_times) > 0 else 0
            }
        
        # Success rate comparison
        prometheus_success = sum(1 for r in prometheus_results if r['success'])
        openai_success = sum(1 for r in openai_results if r['success'])
        
        comparison['accuracy'] = {
            'prometheus_success_rate': prometheus_success / len(prometheus_results) if prometheus_results else 0,
            'openai_success_rate': openai_success / len(openai_results) if openai_results else 0,
            'better': 'Prometheus' if prometheus_success > openai_success else 'OpenAI'
        }
        
        # Confidence comparison
        prometheus_conf = [r['confidence'] for r in prometheus_results if r['success']]
        openai_conf = [r['confidence'] for r in openai_results if r['success']]
        
        if prometheus_conf and openai_conf:
            comparison['confidence'] = {
                'prometheus_avg': np.mean(prometheus_conf),
                'openai_avg': np.mean(openai_conf),
                'more_confident': 'Prometheus' if np.mean(prometheus_conf) > np.mean(openai_conf) else 'OpenAI'
            }
        
        return comparison
    
    def _generate_report(self):
        """Generate comprehensive benchmark report"""
        report_filename = f"ai_vs_openai_benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write("# AI Capabilities Benchmark: Prometheus vs OpenAI\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # Prometheus Results
            f.write("## Prometheus AI Results\n\n")
            prometheus_metrics = self.results['prometheus']
            f.write(f"- **Success Rate**: {prometheus_metrics.get('success_rate', 0):.1%}\n")
            f.write(f"- **Average Response Time**: {prometheus_metrics.get('avg_time', 0):.3f}s\n")
            f.write(f"- **Average Confidence**: {prometheus_metrics.get('avg_confidence', 0):.3f}\n")
            f.write(f"- **Tests Passed**: {prometheus_metrics.get('successful_tests', 0)}/{prometheus_metrics.get('total_tests', 0)}\n\n")
            
            # OpenAI Results
            f.write("## OpenAI Results\n\n")
            openai_metrics = self.results['openai']
            f.write(f"- **Success Rate**: {openai_metrics.get('success_rate', 0):.1%}\n")
            f.write(f"- **Average Response Time**: {openai_metrics.get('avg_time', 0):.3f}s\n")
            f.write(f"- **Average Confidence**: {openai_metrics.get('avg_confidence', 0):.3f}\n")
            f.write(f"- **Tests Passed**: {openai_metrics.get('successful_tests', 0)}/{openai_metrics.get('total_tests', 0)}\n\n")
            
            # Comparison
            f.write("## Comparison\n\n")
            comparison = self.results['comparison']
            
            if 'speed' in comparison and comparison['speed']:
                f.write("### Speed\n\n")
                f.write(f"- **Prometheus**: {comparison['speed'].get('prometheus_avg', 0):.3f}s\n")
                f.write(f"- **OpenAI**: {comparison['speed'].get('openai_avg', 0):.3f}s\n")
                f.write(f"- **Winner**: {comparison['speed'].get('faster', 'N/A')}\n")
                if comparison['speed'].get('speedup', 0) > 0:
                    f.write(f"- **Speedup**: {comparison['speed'].get('speedup', 0):.2f}x\n")
                f.write("\n")
            
            if 'accuracy' in comparison:
                f.write("### Accuracy\n\n")
                f.write(f"- **Prometheus Success Rate**: {comparison['accuracy'].get('prometheus_success_rate', 0):.1%}\n")
                f.write(f"- **OpenAI Success Rate**: {comparison['accuracy'].get('openai_success_rate', 0):.1%}\n")
                f.write(f"- **Winner**: {comparison['accuracy'].get('better', 'N/A')}\n\n")
            
            if 'confidence' in comparison and comparison['confidence']:
                f.write("### Confidence Calibration\n\n")
                f.write(f"- **Prometheus Average**: {comparison['confidence'].get('prometheus_avg', 0):.3f}\n")
                f.write(f"- **OpenAI Average**: {comparison['confidence'].get('openai_avg', 0):.3f}\n")
                f.write(f"- **More Confident**: {comparison['confidence'].get('more_confident', 'N/A')}\n\n")
            
            f.write("---\n\n")
            f.write("## Detailed Results\n\n")
            f.write("See log file for detailed test results.\n")
        
        logger.info(f"\n✅ Benchmark report saved to: {report_filename}")

async def main():
    benchmark = AIVsOpenAIBenchmark()
    results = await benchmark.run_benchmark()
    
    logger.info("\n" + "=" * 80)
    logger.info("BENCHMARK COMPLETE")
    logger.info("=" * 80)
    logger.info("\nSummary:")
    logger.info(f"  Prometheus Success Rate: {results['prometheus'].get('success_rate', 0):.1%}")
    logger.info(f"  OpenAI Success Rate: {results['openai'].get('success_rate', 0):.1%}")
    logger.info(f"  Prometheus Avg Time: {results['prometheus'].get('avg_time', 0):.3f}s")
    logger.info(f"  OpenAI Avg Time: {results['openai'].get('avg_time', 0):.3f}s")

if __name__ == "__main__":
    asyncio.run(main())




