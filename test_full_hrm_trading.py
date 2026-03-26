#!/usr/bin/env python3
"""
Comprehensive Tests for Full HRM Trading Implementation
Tests the complete HRM architecture integration with trading system
"""

import sys
import os
from pathlib import Path
import torch
import numpy as np
from datetime import datetime
import logging

# Add paths
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_hrm_full_architecture():
    """Test full HRM architecture initialization"""
    print("\n" + "="*60)
    print("TEST 1: Full HRM Architecture Initialization")
    print("="*60)
    
    try:
        from core.hrm_full_architecture import FullHRMArchitecture, HRMTradingConfig
        
        # Create config
        config = HRMTradingConfig(
            device='cpu',
            H_cycles=2,
            L_cycles=2,
            seq_len=128  # Smaller for testing
        )
        
        # Initialize HRM
        hrm = FullHRMArchitecture(config=config, device='cpu')
        
        print("[OK] Full HRM Architecture initialized successfully")
        print(f"   Device: {hrm.device}")
        print(f"   Config: H_cycles={config.H_cycles}, L_cycles={config.L_cycles}")
        
        return True, hrm
        
    except Exception as e:
        print(f"[FAIL] Failed to initialize Full HRM: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_hrm_trading_encoder():
    """Test trading data encoder"""
    print("\n" + "="*60)
    print("TEST 2: Trading Data Encoder")
    print("="*60)
    
    try:
        from core.hrm_trading_encoder import HRMTradingEncoder
        
        encoder = HRMTradingEncoder(vocab_size=1000, seq_len=128)
        
        # Test market data encoding
        market_data = {
            'price': 150.0,
            'volume': 1000000,
            'indicators': {
                'rsi': 65.5,
                'macd': 0.8,
                'bollinger_upper': 155.0,
                'bollinger_lower': 145.0
            }
        }
        
        tokens = encoder.encode_market_data(market_data)
        
        print("[OK] Trading encoder working")
        print(f"   Encoded tokens shape: {tokens.shape}")
        print(f"   Token range: {tokens.min().item()} - {tokens.max().item()}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Trading encoder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hrm_trading_decoder():
    """Test trading decision decoder"""
    print("\n" + "="*60)
    print("TEST 3: Trading Decision Decoder")
    print("="*60)
    
    try:
        from core.hrm_trading_decoder import HRMTradingDecoder
        
        decoder = HRMTradingDecoder()
        
        # Test logits decoding
        logits = torch.randn(1, 1000)  # [batch, vocab_size]
        decoded = decoder.decode_logits(logits, top_k=3)
        
        print("[OK] Trading decoder working")
        print(f"   Primary action: {decoded['primary_action']}")
        print(f"   Primary confidence: {decoded['primary_confidence']:.3f}")
        print(f"   Top predictions: {len(decoded['predictions'])}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Trading decoder test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hrm_trading_adapter():
    """Test HRM trading adapter"""
    print("\n" + "="*60)
    print("TEST 4: HRM Trading Adapter")
    print("="*60)
    
    try:
        from core.hrm_full_architecture import FullHRMArchitecture, HRMTradingConfig
        from core.hrm_trading_adapter import HRMTradingAdapter
        from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel
        
        # Initialize HRM (smaller config for testing)
        config = HRMTradingConfig(device='cpu', seq_len=64)
        hrm = FullHRMArchitecture(config=config, device='cpu')
        adapter = HRMTradingAdapter(hrm)
        
        # Create test context
        context = HRMReasoningContext(
            market_data={
                'price': 150.0,
                'volume': 1000000,
                'indicators': {
                    'rsi': 65.5,
                    'macd': 0.8
                }
            },
            user_profile={'risk_tolerance': 'medium'},
            trading_history=[],
            current_portfolio={'cash': 10000, 'positions': {}},
            risk_preferences={'max_position_size': 0.1},
            reasoning_level=HRMReasoningLevel.HIGH_LEVEL
        )
        
        # Make decision
        decision = adapter.make_trading_decision(context)
        
        print("[OK] Trading adapter working")
        print(f"   Action: {decision['action']}")
        print(f"   Confidence: {decision['confidence']:.3f}")
        print(f"   Position size: {decision['position_size']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Trading adapter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_checkpoint_manager():
    """Test checkpoint manager"""
    print("\n" + "="*60)
    print("TEST 5: Checkpoint Manager")
    print("="*60)
    
    try:
        from core.hrm_checkpoint_manager import HRMCheckpointManager
        
        manager = HRMCheckpointManager(checkpoint_dir="test_hrm_checkpoints")
        
        # List checkpoints
        checkpoints = manager.list_checkpoints()
        
        print("[OK] Checkpoint manager working")
        print(f"   Available checkpoints: {len(checkpoints)}")
        for cp in checkpoints:
            print(f"   - {cp['name']}: {cp['description']}")
            print(f"     Downloaded: {cp['downloaded']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Checkpoint manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_integration():
    """Test full integration with trading system"""
    print("\n" + "="*60)
    print("TEST 6: Full Integration Test")
    print("="*60)
    
    try:
        from core.hrm_integration import FullHRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
        
        # Initialize full HRM engine
        engine = FullHRMTradingEngine(device='cpu', use_full_hrm=True)
        
        # Create test context
        context = HRMReasoningContext(
            market_data={
                'price': 150.0,
                'volume': 1000000,
                'indicators': {
                    'rsi': 65.5,
                    'macd': 0.8,
                    'bollinger_upper': 155.0,
                    'bollinger_lower': 145.0
                }
            },
            user_profile={'risk_tolerance': 'medium'},
            trading_history=[],
            current_portfolio={'cash': 10000, 'positions': {}},
            risk_preferences={'max_position_size': 0.1},
            reasoning_level=HRMReasoningLevel.HIGH_LEVEL
        )
        
        # Make decision
        decision = engine.make_hierarchical_decision(context)
        
        print("[OK] Full integration working")
        print(f"   Action: {decision['action']}")
        print(f"   Confidence: {decision.get('confidence', 0.0):.3f}")
        print(f"   Full HRM active: {decision.get('full_hrm', False)}")
        
        # Get metrics
        metrics = engine.get_performance_metrics()
        print(f"   Total decisions: {metrics.get('total_decisions', 0)}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Full integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("FULL HRM TRADING - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    results = {}
    
    # Test 1: Full HRM Architecture
    success, hrm = test_hrm_full_architecture()
    results['architecture'] = success
    
    # Test 2: Trading Encoder
    results['encoder'] = test_hrm_trading_encoder()
    
    # Test 3: Trading Decoder
    results['decoder'] = test_hrm_trading_decoder()
    
    # Test 4: Trading Adapter
    results['adapter'] = test_hrm_trading_adapter()
    
    # Test 5: Checkpoint Manager
    results['checkpoint_manager'] = test_checkpoint_manager()
    
    # Test 6: Full Integration
    results['integration'] = test_full_integration()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name:20} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed! Full HRM implementation is working correctly.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

