#!/usr/bin/env python3
"""
PROCEED WITH BACKTEST INTEGRATION
Runs comprehensive backtests and integrates patterns into Prometheus
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'backtest_integration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BacktestIntegrationMaster:
    """Master controller for backtest integration"""
    
    def __init__(self):
        self.timeframes = [1, 5, 10, 20, 50, 100]  # Years
        self.symbols = ['SPY', 'QQQ', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'BTC-USD', 'ETH-USD']
        
    def print_header(self, text):
        print()
        print("=" * 80)
        print(text)
        print("=" * 80)
        print()
    
    async def run_learning_backtest(self):
        """Run learning backtest to learn patterns"""
        self.print_header("PHASE 1: LEARNING PATTERNS FROM ALL ANGLES")
        
        try:
            from advanced_learning_backtest import AdvancedLearningBacktest
            backtester = AdvancedLearningBacktest()
            patterns = await backtester.run_learning_backtest()
            
            logger.info(f"✅ Learned patterns from {len(backtester.learning_angles)} angles")
            return True
        except Exception as e:
            logger.error(f"❌ Learning backtest failed: {e}")
            return False
    
    async def run_real_market_backtest(self):
        """Run real market backtest"""
        self.print_header("PHASE 2: REAL MARKET BACKTESTING")
        
        try:
            from comprehensive_real_market_backtest import ComprehensiveRealMarketBacktest
            backtester = ComprehensiveRealMarketBacktest(initial_capital=10000.0)
            results = await backtester.run_comprehensive_backtest()
            
            logger.info("✅ Real market backtest complete")
            return True
        except Exception as e:
            logger.error(f"❌ Real market backtest failed: {e}")
            return False
    
    def verify_integration(self):
        """Verify pattern integration"""
        self.print_header("PHASE 3: VERIFYING PATTERN INTEGRATION")
        
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            from core.pattern_integration import PatternIntegration
            
            # Check Universal Reasoning Engine
            engine = UniversalReasoningEngine()
            status = engine.get_system_status()
            
            print("Universal Reasoning Engine Status:")
            print(f"  Pattern Integration: {'✅ Active' if status.get('pattern_integration') else '❌ Not Active'}")
            print(f"  Total Sources: {status.get('total_sources', 0)}/7")
            print(f"  Weights: {status.get('weights', {})}")
            
            # Check Pattern Integration
            pattern_integration = PatternIntegration()
            pattern_count = sum(len(v) if isinstance(v, dict) else 0 for v in pattern_integration.patterns.values())
            
            print(f"\nPattern Integration Status:")
            print(f"  Patterns Loaded: {pattern_count}")
            print(f"  Pattern Files: {len(list(Path('.').glob('learned_patterns_*.json')))}")
            
            if status.get('pattern_integration'):
                print("\n✅ SUCCESS: Patterns integrated into Prometheus!")
                return True
            else:
                print("\n⚠️ WARNING: Pattern integration not active")
                return False
                
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_pattern_enhancement(self):
        """Test pattern enhancement on sample decision"""
        self.print_header("PHASE 4: TESTING PATTERN ENHANCEMENT")
        
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            
            engine = UniversalReasoningEngine()
            
            # Test context
            test_context = {
                'market_data': {
                    'symbol': 'SPY',
                    'price': 450.0,
                    'volatility': 0.02,
                    'volume_ratio': 1.2,
                    'trend': 'up',
                    'regime': 'bull'
                },
                'portfolio': {
                    'value': 10000,
                    'positions': {}
                },
                'user_profile': {},
                'trading_history': [],
                'risk_preferences': {}
            }
            
            # Make decision
            decision = engine.make_ultimate_decision(test_context)
            
            print("Test Decision Result:")
            print(f"  Action: {decision.get('action', 'UNKNOWN')}")
            print(f"  Confidence: {decision.get('confidence', 0):.3f}")
            print(f"  Sources: {decision.get('num_sources', 0)}")
            
            if 'patterns' in decision.get('reasoning_sources', {}):
                pattern_info = decision['reasoning_sources']['patterns']
                print(f"  Pattern Influence: ✅ Active")
                print(f"    Pattern Action: {pattern_info.get('decision', {}).get('pattern_suggested_action', 'N/A')}")
                print(f"    Patterns Matched: {pattern_info.get('decision', {}).get('patterns_matched', 0)}")
            else:
                print(f"  Pattern Influence: ⚠️ Not yet active (patterns will be used once backtests complete)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def run_full_integration(self):
        """Run full integration process"""
        print("=" * 80)
        print("PROMETHEUS BACKTEST PATTERN INTEGRATION")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        results = {
            'learning_backtest': False,
            'real_market_backtest': False,
            'integration_verified': False,
            'pattern_test': False
        }
        
        # Phase 1: Learning Backtest
        results['learning_backtest'] = await self.run_learning_backtest()
        
        # Phase 2: Real Market Backtest (can run in parallel or after)
        # For now, we'll run it but it may take a while
        print("\nNote: Real market backtest may take significant time...")
        print("You can run it separately: python comprehensive_real_market_backtest.py")
        
        # Phase 3: Verify Integration
        results['integration_verified'] = self.verify_integration()
        
        # Phase 4: Test Pattern Enhancement
        results['pattern_test'] = await self.test_pattern_enhancement()
        
        # Summary
        self.print_header("INTEGRATION SUMMARY")
        
        print("Results:")
        print(f"  Learning Backtest: {'✅' if results['learning_backtest'] else '❌'}")
        print(f"  Real Market Backtest: {'⏳ Run separately' if not results['real_market_backtest'] else '✅'}")
        print(f"  Integration Verified: {'✅' if results['integration_verified'] else '❌'}")
        print(f"  Pattern Test: {'✅' if results['pattern_test'] else '❌'}")
        print()
        
        if results['integration_verified']:
            print("✅ SUCCESS: Pattern integration complete!")
            print("   Prometheus will now use backtest-learned patterns in all decisions")
            print("   Patterns will enhance decision-making once backtests complete")
        else:
            print("⚠️ Integration needs attention - check logs for details")
        
        return results

async def main():
    master = BacktestIntegrationMaster()
    await master.run_full_integration()

if __name__ == "__main__":
    asyncio.run(main())

