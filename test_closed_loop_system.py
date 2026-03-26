#!/usr/bin/env python3
"""
✅ QUICK TEST - Verify All Systems Work
Test the complete closed-loop learning implementation
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_enhanced_intelligence():
    """Test enhanced intelligence in live trading"""
    print("\n" + "="*60)
    print("1️⃣ Testing Enhanced Intelligence (8 Sources)")
    print("="*60)
    
    try:
        from prometheus_active_trading_session import PrometheusActiveTradingSession
        
        session = PrometheusActiveTradingSession()
        
        # Test enhanced intelligence
        enhanced = session._get_enhanced_intelligence('AAPL')
        
        print(f"✅ Enhanced intelligence loaded:")
        print(f"   Visual patterns: {enhanced.get('visual_pattern_count', 0)}")
        print(f"   Sentiment: {enhanced.get('sentiment', 0.5):.2f}")
        print(f"   Risk level: {enhanced.get('risk_level', 0.5):.2f}")
        print(f"   Opportunity: {enhanced.get('opportunity_score', 0.5):.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_visual_ai_patterns():
    """Test Visual AI pattern loading"""
    print("\n" + "="*60)
    print("2️⃣ Testing Visual AI Patterns")
    print("="*60)
    
    try:
        import json
        
        patterns_file = Path("visual_ai_patterns_cloud.json")
        
        if not patterns_file.exists():
            print("❌ Visual AI patterns file not found!")
            print("   Run: python CLOUD_VISION_TRAINING.py")
            return False
        
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        
        print(f"✅ Visual AI patterns loaded:")
        print(f"   Total analyzed: {data.get('total_analyzed', 0)}")
        print(f"   Total patterns: {data.get('total_patterns', 0)}")
        print(f"   Pattern types: {len(data.get('pattern_summary', {}))}")
        
        # Show top patterns
        pattern_summary = data.get('pattern_summary', {})
        if pattern_summary:
            print(f"\n   Top patterns:")
            for pattern, count in sorted(pattern_summary.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"     - {pattern}: {count}x")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_learning_engine():
    """Test learning engine status"""
    print("\n" + "="*60)
    print("3️⃣ Testing Learning Engine")
    print("="*60)
    
    try:
        import json
        
        strategies_file = Path("ultimate_strategies.json")
        
        if not strategies_file.exists():
            print("❌ Learning engine strategies not found!")
            print("   Learning engine may not be running")
            return False
        
        with open(strategies_file, 'r') as f:
            data = json.load(f)
        
        # Find best strategies
        best_strategies = []
        for strategy_id, strategy in data.items():
            if strategy.get('win_rate', 0) > 0.70:
                best_strategies.append({
                    'name': strategy.get('name', 'Unknown'),
                    'gen': strategy.get('generation', 0),
                    'win_rate': strategy.get('win_rate', 0),
                    'trades': strategy.get('total_trades', 0)
                })
        
        print(f"✅ Learning engine strategies loaded:")
        print(f"   Total strategies: {len(data)}")
        print(f"   High-performance (>70%): {len(best_strategies)}")
        
        if best_strategies:
            print(f"\n   Top strategy:")
            best = sorted(best_strategies, key=lambda x: x['win_rate'], reverse=True)[0]
            print(f"     Name: {best['name']}")
            print(f"     Generation: {best['gen']}")
            print(f"     Win rate: {best['win_rate']*100:.1f}%")
            print(f"     Trades: {best['trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_paper_trading_system():
    """Test paper trading system"""
    print("\n" + "="*60)
    print("4️⃣ Testing Paper Trading System")
    print("="*60)
    
    try:
        from internal_realworld_paper_trading import InternalPaperTradingLoop
        
        loop = InternalPaperTradingLoop(starting_capital=10000.0)
        
        print(f"✅ Paper trading system initialized:")
        print(f"   Starting capital: ${loop.starting_capital:,.2f}")
        print(f"   Results directory: {loop.results_dir}")
        print(f"   Charts directory: {loop.charts_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_learning_validator():
    """Test learning validator"""
    print("\n" + "="*60)
    print("5️⃣ Testing Learning Validator")
    print("="*60)
    
    try:
        from visual_ai_learning_validator import VisualAILearningValidator
        
        validator = VisualAILearningValidator()
        validator.load_visual_ai_patterns()
        validator.load_learning_engine_performance()
        
        print(f"✅ Learning validator initialized:")
        print(f"   Visual AI patterns: {len(validator.visual_ai_patterns)}")
        print(f"   Learning strategies: {len(validator.learning_engine_patterns)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_web_scraper():
    """Test web scraper"""
    print("\n" + "="*60)
    print("6️⃣ Testing Web Scraper Integration")
    print("="*60)
    
    try:
        from core.web_scraper_integration import WebScraperIntegration
        
        scraper = WebScraperIntegration()
        
        print(f"✅ Web scraper initialized:")
        print(f"   Cache duration: {scraper.cache_duration}s")
        print(f"   Data directory: {scraper.scraped_data_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def run_all_tests():
    """Run all system tests"""
    print("\n" + "="*80)
    print("🧪 PROMETHEUS CLOSED-LOOP SYSTEM - COMPREHENSIVE TEST")
    print("="*80)
    
    tests = [
        ("Enhanced Intelligence", test_enhanced_intelligence),
        ("Visual AI Patterns", test_visual_ai_patterns),
        ("Learning Engine", test_learning_engine),
        ("Paper Trading System", test_paper_trading_system),
        ("Learning Validator", test_learning_validator),
        ("Web Scraper", test_web_scraper)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("\nReady to run:")
        print("   python run_closed_loop_learning.py")
    else:
        print("\n⚠️ Some systems need attention")
        print("\nNext steps:")
        if not results[1][1]:  # Visual AI
            print("   1. Run: python CLOUD_VISION_TRAINING.py")
        if not results[2][1]:  # Learning Engine
            print("   2. Check if PROMETHEUS_ULTIMATE_LEARNING_ENGINE.py is running")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    run_all_tests()
