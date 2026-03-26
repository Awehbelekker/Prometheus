#!/usr/bin/env python3
"""
PROMETHEUS Combined Test: HRM + ThinkMesh (No DeepSeek Inference)
Tests HRM and ThinkMesh working together for trading decisions
"""
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEST_CONFIG = {
    'symbol': 'AAPL',
    'market_data': {'price': 185.50, 'volume': 45000000, 'change_pct': 1.2},
    'technical': {'rsi': 58, 'macd': 0.75, 'sma_20': 182.00, 'sma_50': 178.50}
}

class CombinedHRMThinkMeshTest:
    def __init__(self):
        self.results = {}
        
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
                'reasoning': result['reasoning'][:150] if len(result.get('reasoning', '')) > 150 else result.get('reasoning', ''),
                'checkpoint': result.get('metadata', {}).get('checkpoint_used', 'unknown'),
                'elapsed_ms': int(elapsed * 1000)
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e), 'elapsed_ms': int((time.time() - start) * 1000)}

    async def test_thinkmesh(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Test ThinkMesh Enhanced"""
        logger.info("🔮 Testing ThinkMesh Enhanced...")
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
            
            prompt = f"Analyze {symbol} stock at ${market_data['price']:.2f}. RSI={market_data.get('rsi', 50)}. Recommend BUY, SELL, or HOLD with reasoning."
            result = await adapter.reason(prompt, config, context={'market_data': market_data})
            elapsed = time.time() - start
            
            # Extract action from content
            action = 'HOLD'
            content_upper = result.content.upper()
            if 'BUY' in content_upper: action = 'BUY'
            elif 'SELL' in content_upper: action = 'SELL'
            
            return {
                'status': 'SUCCESS' if result.confidence > 0 else 'FALLBACK',
                'action': action,
                'confidence': result.confidence,
                'reasoning': result.content[:150] if len(result.content) > 150 else result.content,
                'strategy_used': result.strategy_used,
                'verified': result.verified,
                'elapsed_ms': int(elapsed * 1000)
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e), 'elapsed_ms': int((time.time() - start) * 1000)}

    def calculate_ensemble(self, hrm: Dict, thinkmesh: Dict) -> Dict[str, Any]:
        """Calculate ensemble decision from HRM and ThinkMesh"""
        votes = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        weights = {'hrm': 0.6, 'thinkmesh': 0.4}  # HRM gets higher weight
        
        for name, result, weight in [('hrm', hrm, 0.6), ('thinkmesh', thinkmesh, 0.4)]:
            if result.get('status') in ['SUCCESS', 'FALLBACK']:
                action = result.get('action', 'HOLD').upper()
                confidence = result.get('confidence', 0.5)
                if action in votes:
                    votes[action] += weight * confidence
        
        final_action = max(votes, key=votes.get)
        total_confidence = votes[final_action] / sum(weights.values())
        
        return {
            'action': final_action,
            'confidence': round(total_confidence, 2),
            'votes': {k: round(v, 3) for k, v in votes.items()},
            'weights': weights
        }

    async def run_test(self) -> Dict[str, Any]:
        """Run the combined HRM + ThinkMesh test"""
        print("\n" + "="*70)
        print("🤖 PROMETHEUS COMBINED TEST: HRM + ThinkMesh")
        print("="*70)
        
        symbol = TEST_CONFIG['symbol']
        market = {**TEST_CONFIG['market_data'], **TEST_CONFIG['technical']}
        
        print(f"\n📊 Test Symbol: {symbol}")
        print(f"   Price: ${market['price']:.2f} | RSI: {market['rsi']} | MACD: {market['macd']}")
        
        # Run HRM test
        hrm_result = await self.test_hrm(symbol, market, TEST_CONFIG['technical'])
        
        # Run ThinkMesh test
        thinkmesh_result = await self.test_thinkmesh(symbol, market)
        
        # Calculate ensemble
        ensemble = self.calculate_ensemble(hrm_result, thinkmesh_result)
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'market_data': market,
            'hrm': hrm_result,
            'thinkmesh': thinkmesh_result,
            'ensemble': ensemble
        }
        
        # Print results
        print("\n" + "-"*70)
        print("📋 RESULTS")
        print("-"*70)
        
        for name, r in [('HRM', hrm_result), ('ThinkMesh', thinkmesh_result)]:
            icon = '✅' if r['status'] == 'SUCCESS' else '⚠️' if r['status'] == 'FALLBACK' else '❌'
            print(f"\n{icon} {name}:")
            print(f"   Status: {r['status']} | Action: {r.get('action', 'N/A')} | Confidence: {r.get('confidence', 'N/A')}")
            print(f"   Time: {r.get('elapsed_ms', 'N/A')}ms")
            if r.get('reasoning'):
                print(f"   Reasoning: {r['reasoning'][:80]}...")
        
        print(f"\n🎯 ENSEMBLE DECISION: {ensemble['action']} (confidence: {ensemble['confidence']})")
        print(f"   Votes: BUY={ensemble['votes']['BUY']:.2f} | SELL={ensemble['votes']['SELL']:.2f} | HOLD={ensemble['votes']['HOLD']:.2f}")
        
        # Save results
        filename = f"combined_hrm_thinkmesh_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {filename}")
        
        return results

async def main():
    tester = CombinedHRMThinkMeshTest()
    await tester.run_test()

if __name__ == "__main__":
    asyncio.run(main())

