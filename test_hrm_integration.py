#!/usr/bin/env python3
"""
Test HRM Integration - Verify full mesh is working
Tests: Checkpoint loading, HRM reasoning, Trading integration, Training system
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_checkpoint_manager():
    """Test 1: Checkpoint Manager"""
    print("\n" + "="*60)
    print("TEST 1: HRM Checkpoint Manager")
    print("="*60)
    
    try:
        from core.hrm_checkpoint_manager import HRMCheckpointManager
        
        manager = HRMCheckpointManager(checkpoint_dir="hrm_checkpoints")
        
        print(f"✓ Checkpoint manager initialized: {manager.checkpoint_dir}")
        
        # Check available checkpoints
        for name, info in manager.CHECKPOINTS.items():
            path = manager.get_checkpoint_path(name)
            exists = path and Path(path).exists() if path else False
            status = "✓ EXISTS" if exists else "⚠ NEEDS DOWNLOAD"
            print(f"  {name}: {status}")
            if not exists:
                print(f"    Downloading from {info['repo_id']}...")
                downloaded = manager.download_checkpoint(name)
                if downloaded:
                    print(f"    ✓ Downloaded to {downloaded}")
                else:
                    print(f"    ✗ Download failed")
        
        return True
        
    except Exception as e:
        print(f"✗ Checkpoint Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hrm_model_loading():
    """Test 2: HRM Model Loading"""
    print("\n" + "="*60)
    print("TEST 2: HRM Model Loading")
    print("="*60)
    
    try:
        from core.hrm_official_integration import OfficialHRMTradingAdapter
        
        print("Loading HRM models...")
        adapter = OfficialHRMTradingAdapter(
            checkpoint_dir="hrm_checkpoints",
            device="cpu",  # Use CPU for testing
            use_ensemble=True
        )
        
        print(f"✓ Adapter initialized on device: {adapter.device}")
        print(f"✓ Loaded {len(adapter.models)} models:")
        
        for name in adapter.models.keys():
            print(f"    - {name}")
        
        return len(adapter.models) > 0
        
    except Exception as e:
        print(f"✗ HRM Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hrm_reasoning():
    """Test 3: HRM Reasoning"""
    print("\n" + "="*60)
    print("TEST 3: HRM Reasoning")
    print("="*60)
    
    try:
        from core.hrm_official_integration import get_official_hrm_adapter
        from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
        
        adapter = get_official_hrm_adapter(checkpoint_dir="hrm_checkpoints")
        
        if adapter is None or len(adapter.models) == 0:
            print("⚠ No HRM models loaded - testing fallback")
        
        # Create test context
        context = HRMReasoningContext(
            market_data={
                'symbol': 'AAPL',
                'price': 185.50,
                'volume': 45000000,
                'change_pct': 1.5,
                'bid': 185.45,
                'ask': 185.55,
                'rsi': 58,
                'macd': 0.5
            },
            user_profile={'risk_tolerance': 'medium'},
            trading_history=[],
            current_portfolio={'cash': 10000, 'positions': {}},
            risk_preferences={'max_position_size': 0.1},
            reasoning_level=HRMReasoningLevel.HIGH_LEVEL
        )
        
        print("Testing reasoning on AAPL...")
        decision = adapter.reason(context)
        
        print(f"✓ HRM Decision:")
        print(f"    Action: {decision.action}")
        print(f"    Confidence: {decision.confidence:.2%}")
        print(f"    Checkpoint: {decision.checkpoint_used}")
        print(f"    Reasoning: {decision.reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ HRM Reasoning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_hrm_decision():
    """Test 4: Async HRM Decision (as used by trading system)"""
    print("\n" + "="*60)
    print("TEST 4: Async HRM Decision")
    print("="*60)
    
    try:
        from core.hrm_official_integration import get_hrm_decision
        
        market_data = {
            'price': 425.00,
            'volume': 30000000,
            'change_pct': 2.3,
            'bid': 424.90,
            'ask': 425.10
        }
        
        technical_indicators = {
            'rsi': 62,
            'macd': 1.2,
            'macd_signal': 0.8,
            'sma_20': 420,
            'sma_50': 410
        }
        
        print("Getting HRM decision for MSFT...")
        decision = await get_hrm_decision('MSFT', market_data, technical_indicators)
        
        print(f"✓ Async HRM Decision:")
        print(f"    Action: {decision['action']}")
        print(f"    Confidence: {decision['confidence']:.2%}")
        print(f"    Risk Score: {decision['risk_score']:.2f}")
        print(f"    HRM Available: {decision['metadata'].get('hrm_available', False)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Async HRM Decision test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hrm_training_system():
    """Test 5: HRM Training System"""
    print("\n" + "="*60)
    print("TEST 5: HRM Training System")
    print("="*60)
    
    try:
        from core.hrm_trading_trainer import HRMTradingTrainer
        
        print("Initializing HRM Trading Trainer...")
        trainer = HRMTradingTrainer(device='cpu')
        
        status = trainer.get_training_status()
        print(f"✓ Training Status:")
        print(f"    Total Samples: {status['total_samples']}")
        print(f"    Epochs Trained: {status['epochs_trained']}")
        print(f"    Ready to Train: {status['ready_to_train']}")
        
        # Add a few test samples
        import numpy as np
        print("\nAdding test training samples...")
        
        for i in range(5):
            trainer.add_training_sample(
                market_data={
                    'price': 100 + np.random.uniform(-10, 10),
                    'volume': 1000000,
                    'change_percent': np.random.uniform(-3, 3)
                },
                technical_indicators={
                    'rsi': 50 + np.random.uniform(-20, 20),
                    'macd': np.random.uniform(-1, 1)
                },
                action=['BUY', 'SELL', 'HOLD'][i % 3],
                profit_loss=np.random.uniform(-20, 40),
                confidence=0.7,
                symbol='TEST'
            )
        
        print(f"✓ Added 5 test samples (total: {trainer.get_training_status()['total_samples']})")
        
        return True
        
    except Exception as e:
        print(f"✗ HRM Training test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hrm_integration():
    """Test 6: HRM Trading Integration"""
    print("\n" + "="*60)
    print("TEST 6: HRM Trading Integration")
    print("="*60)
    
    try:
        from core.hrm_trading_integration import (
            get_hrm_integration,
            hrm_status,
            hrm_get_prediction
        )
        
        print("Getting HRM integration status...")
        status = hrm_status()
        
        print(f"✓ Integration Status:")
        print(f"    Enabled: {status.get('enabled', False)}")
        print(f"    Total Samples: {status.get('total_samples', 0)}")
        print(f"    Ready to Train: {status.get('ready_to_train', False)}")
        
        # Test prediction
        print("\nTesting prediction...")
        prediction = hrm_get_prediction(
            symbol='GOOGL',
            market_data={'price': 175, 'volume': 20000000, 'change_percent': 0.5},
            technical_indicators={'rsi': 55, 'macd': 0.3}
        )
        
        print(f"✓ Prediction:")
        print(f"    Status: {prediction.get('status', 'unknown')}")
        print(f"    Action: {prediction.get('action', 'unknown')}")
        print(f"    Confidence: {prediction.get('confidence', 0):.2%}")
        
        return True
        
    except Exception as e:
        print(f"✗ HRM Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_universal_reasoning_hrm():
    """Test 7: Universal Reasoning Engine HRM Integration"""
    print("\n" + "="*60)
    print("TEST 7: Universal Reasoning Engine HRM Integration")
    print("="*60)
    
    try:
        from core.universal_reasoning_engine_v2 import UniversalReasoningEngineV2
        
        engine = UniversalReasoningEngineV2()
        
        print("✓ Universal Reasoning Engine initialized")
        print(f"    HRM Weight: {engine.weights.get('hrm', 0):.0%}")
        print(f"    HRM Enabled: {engine._is_source_enabled('hrm')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Universal Reasoning test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all HRM integration tests"""
    print("\n" + "="*60)
    print("       HRM INTEGRATION TEST SUITE")
    print("       Verifying full 'thinking mesh' is working")
    print("="*60)
    
    results = {}
    
    # Run tests
    results['checkpoint_manager'] = test_checkpoint_manager()
    results['model_loading'] = test_hrm_model_loading()
    results['reasoning'] = test_hrm_reasoning()
    results['async_decision'] = await test_async_hrm_decision()
    results['training_system'] = test_hrm_training_system()
    results['integration'] = test_hrm_integration()
    results['universal_reasoning'] = test_universal_reasoning_hrm()
    
    # Summary
    print("\n" + "="*60)
    print("       TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL HRM SYSTEMS WORKING - 'Thinking Mesh' is ACTIVE!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed - check logs above")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
