#!/usr/bin/env python3
"""
PROMETHEUS Combined AI Test: HRM + DeepSeek + ThinkMesh
Tests all three AI systems working together for trading decisions
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test configuration
TEST_CONFIG = {
    'symbol': 'AAPL',
    'market_data': {
        'price': 185.50,
        'volume': 45000000,
        'change_pct': 1.2,
        'high': 187.00,
        'low': 183.50,
        'open': 184.00
    },
    'technical_indicators': {
        'rsi': 58,
        'macd': 0.75,
        'macd_signal': 0.50,
        'sma_20': 182.00,
        'sma_50': 178.50,
        'bollinger_upper': 190.00,
        'bollinger_lower': 175.00
    }
}

class CombinedAITester:
    def __init__(self):
        self.results = {}
        self.start_time = None
        
    async def test_hrm(self, symbol: str, market_data: Dict, technical: Dict) -> Dict[str, Any]:
        """Test HRM Official Integration"""
        logger.info("🧠 Testing HRM Official...")
        start = time.time()
        try:
            from core.hrm_official_integration import get_hrm_decision
            result = await get_hrm_decision(symbol, market_data, technical)
            elapsed = time.time() - start
            return {
                'status': 'SUCCESS',
                'action': result['action'],
                'confidence': result['confidence'],
                'reasoning': result['reasoning'][:100] + '...' if len(result.get('reasoning', '')) > 100 else result.get('reasoning', ''),
                'checkpoint': result.get('metadata', {}).get('checkpoint_used', 'unknown'),
                'elapsed_ms': int(elapsed * 1000)
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e), 'elapsed_ms': int((time.time() - start) * 1000)}

    async def test_deepseek(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Test DeepSeek-R1 via Ollama"""
        logger.info("🚀 Testing DeepSeek-R1...")
        start = time.time()
        try:
            from core.deepseek_adapter import DeepSeekAdapter
            adapter = DeepSeekAdapter(model="deepseek-r1:14b")
            
            # Test market analysis
            test_data = {'symbol': symbol, **market_data, 'rsi': 58, 'macd': 'bullish', 'trend': 'uptrend'}
            result = adapter.analyze_market(test_data)
            elapsed = time.time() - start
            
            return {
                'status': 'SUCCESS' if result.get('action') else 'FALLBACK',
                'action': result.get('action', 'HOLD'),
                'confidence': result.get('confidence', 0),
                'reasoning': str(result.get('reasoning', ''))[:100],
                'cost': result.get('cost', 0.0),
                'elapsed_ms': int(elapsed * 1000)
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e), 'elapsed_ms': int((time.time() - start) * 1000)}

    async def test_thinkmesh(self, symbol: str, market_data: Dict, risk_params: Dict) -> Dict[str, Any]:
        """Test ThinkMesh Enhanced"""
        logger.info("🔮 Testing ThinkMesh...")
        start = time.time()
        try:
            from core.reasoning.thinkmesh_enhanced import EnhancedThinkMeshAdapter, ThinkMeshConfig, ReasoningStrategy
            
            adapter = EnhancedThinkMeshAdapter(enabled=True)
            config = ThinkMeshConfig(
                strategy=ReasoningStrategy.SELF_CONSISTENCY,
                parallel_paths=3,
                require_final_answer=True,
                wall_clock_timeout_s=15,
                max_total_tokens=1000
            )
            
            prompt = f"Analyze {symbol} at ${market_data['price']:.2f}. RSI={market_data.get('rsi', 50)}. Should I BUY, SELL, or HOLD?"
            result = await adapter.reason(prompt, config, context={'market_data': market_data})
            elapsed = time.time() - start
            
            return {
                'status': 'SUCCESS' if result.confidence > 0 else 'FALLBACK',
                'action': self._extract_action(result.content),
                'confidence': result.confidence,
                'strategy_used': result.strategy_used,
                'verified': result.verified,
                'elapsed_ms': int(elapsed * 1000)
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e), 'elapsed_ms': int((time.time() - start) * 1000)}

    def _extract_action(self, content: str) -> str:
        """Extract BUY/SELL/HOLD from content"""
        content_upper = content.upper()
        if 'BUY' in content_upper: return 'BUY'
        if 'SELL' in content_upper: return 'SELL'
        return 'HOLD'

    async def run_combined_test(self) -> Dict[str, Any]:
        """Run all AI systems and compare results"""
        print("\n" + "="*70)
        print("🤖 PROMETHEUS COMBINED AI TEST: HRM + DeepSeek + ThinkMesh")
        print("="*70)
        
        symbol = TEST_CONFIG['symbol']
        market = TEST_CONFIG['market_data']
        tech = TEST_CONFIG['technical_indicators']
        risk = {'max_loss': 0.02, 'position_size': 0.05}
        
        print(f"\n📊 Testing Symbol: {symbol}")
        print(f"   Price: ${market['price']:.2f} | RSI: {tech['rsi']} | MACD: {tech['macd']}")
        
        # Run all tests
        hrm_result = await self.test_hrm(symbol, market, tech)
        deepseek_result = await self.test_deepseek(symbol, market)
        thinkmesh_result = await self.test_thinkmesh(symbol, {**market, 'rsi': tech['rsi']}, risk)
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'hrm': hrm_result,
            'deepseek': deepseek_result,
            'thinkmesh': thinkmesh_result,
            'ensemble': self._calculate_ensemble(hrm_result, deepseek_result, thinkmesh_result)
        }
        
        # Print summary
        self._print_summary(results)
        
        # Save results
        filename = f'combined_ai_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
        
        return results

    def _calculate_ensemble(self, hrm, deepseek, thinkmesh) -> Dict[str, Any]:
        """Calculate ensemble decision from all AI sources"""
        votes = {'BUY': 0, 'SELL': 0, 'HOLD': 0}
        weights = {'hrm': 0.4, 'deepseek': 0.3, 'thinkmesh': 0.3}
        
        for name, result in [('hrm', hrm), ('deepseek', deepseek), ('thinkmesh', thinkmesh)]:
            if result.get('status') in ['SUCCESS', 'FALLBACK']:
                action = result.get('action', 'HOLD').upper()
                if action in votes:
                    votes[action] += weights[name]
        
        final_action = max(votes, key=votes.get)
        return {'action': final_action, 'votes': votes, 'weights': weights}

    def _print_summary(self, results):
        print("\n" + "-"*70)
        print("📋 RESULTS SUMMARY")
        print("-"*70)
        
        for name in ['hrm', 'deepseek', 'thinkmesh']:
            r = results[name]
            status_icon = '✅' if r['status'] == 'SUCCESS' else '⚠️' if r['status'] == 'FALLBACK' else '❌'
            print(f"\n{status_icon} {name.upper()}:")
            print(f"   Status: {r['status']} | Action: {r.get('action', 'N/A')} | Confidence: {r.get('confidence', 'N/A')}")
            print(f"   Time: {r.get('elapsed_ms', 'N/A')}ms")
        
        ens = results['ensemble']
        print(f"\n🎯 ENSEMBLE DECISION: {ens['action']}")
        print(f"   Votes: BUY={ens['votes']['BUY']:.1f} | SELL={ens['votes']['SELL']:.1f} | HOLD={ens['votes']['HOLD']:.1f}")

async def main():
    tester = CombinedAITester()
    await tester.run_combined_test()

if __name__ == "__main__":
    asyncio.run(main())

