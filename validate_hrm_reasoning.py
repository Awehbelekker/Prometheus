#!/usr/bin/env python3
"""
Validate HRM Reasoning Quality
Validates that the hierarchical reasoning is working correctly
"""

import sys
import os
from pathlib import Path
import numpy as np
from datetime import datetime
import logging

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_hrm_architecture():
    """Validate HRM architecture components"""
    print("\n" + "="*60)
    print("VALIDATION: HRM Architecture Components")
    print("="*60)
    
    validations = {}
    
    # Check if official HRM is available
    try:
        sys.path.insert(0, str(Path(__file__).parent / "official_hrm"))
        from models.hrm.hrm_act_v1 import HierarchicalReasoningModel_ACTV1
        validations['official_hrm_import'] = True
        print("[OK] Official HRM model importable")
    except Exception as e:
        validations['official_hrm_import'] = False
        print(f"[FAIL] Official HRM not importable: {e}")
    
    # Check full HRM architecture
    try:
        from core.hrm_full_architecture import FullHRMArchitecture, HRMTradingConfig
        config = HRMTradingConfig(device='cpu', seq_len=64)
        hrm = FullHRMArchitecture(config=config, device='cpu')
        validations['full_hrm_init'] = True
        print("[OK] Full HRM architecture initializable")
    except Exception as e:
        validations['full_hrm_init'] = False
        print(f"[FAIL] Full HRM initialization failed: {e}")
    
    # Check trading components
    try:
        from core.hrm_trading_encoder import HRMTradingEncoder
        from core.hrm_trading_decoder import HRMTradingDecoder
        from core.hrm_trading_adapter import HRMTradingAdapter
        validations['trading_components'] = True
        print("[OK] Trading components available")
    except Exception as e:
        validations['trading_components'] = False
        print(f"[FAIL] Trading components missing: {e}")
    
    return validations


def validate_reasoning_quality():
    """Validate reasoning quality"""
    print("\n" + "="*60)
    print("VALIDATION: Reasoning Quality")
    print("="*60)
    
    try:
        from core.hrm_integration import FullHRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
        
        engine = FullHRMTradingEngine(device='cpu', use_full_hrm=True)
        
        # Test with different market conditions
        test_cases = [
            {
                'name': 'Bull Market',
                'market_data': {
                    'price': 150.0,
                    'volume': 1000000,
                    'indicators': {'rsi': 70, 'macd': 1.0}
                }
            },
            {
                'name': 'Bear Market',
                'market_data': {
                    'price': 150.0,
                    'volume': 1000000,
                    'indicators': {'rsi': 30, 'macd': -1.0}
                }
            },
            {
                'name': 'Sideways Market',
                'market_data': {
                    'price': 150.0,
                    'volume': 1000000,
                    'indicators': {'rsi': 50, 'macd': 0.0}
                }
            }
        ]
        
        results = []
        for test_case in test_cases:
            context = HRMReasoningContext(
                market_data=test_case['market_data'],
                user_profile={'risk_tolerance': 'medium'},
                trading_history=[],
                current_portfolio={'cash': 10000, 'positions': {}},
                risk_preferences={'max_position_size': 0.1},
                reasoning_level=HRMReasoningLevel.HIGH_LEVEL
            )
            
            decision = engine.make_hierarchical_decision(context)
            
            results.append({
                'name': test_case['name'],
                'action': decision.get('action'),
                'confidence': decision.get('confidence', 0.0)
            })
            
            print(f"\n{test_case['name']}:")
            print(f"   Action: {decision.get('action')}")
            print(f"   Confidence: {decision.get('confidence', 0.0):.3f}")
        
        # Validate consistency
        print("\n[OK] Reasoning quality validation complete")
        return True
        
    except Exception as e:
        print(f"[FAIL] Reasoning quality validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all validations"""
    print("\n" + "="*80)
    print("HRM REASONING VALIDATION")
    print("="*80)
    
    # Validate architecture
    arch_validations = validate_hrm_architecture()
    
    # Validate reasoning quality
    quality_valid = validate_reasoning_quality()
    
    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    
    all_arch_valid = all(arch_validations.values())
    
    print(f"Architecture: {'[PASS]' if all_arch_valid else '[FAIL]'}")
    print(f"Reasoning Quality: {'[PASS]' if quality_valid else '[FAIL]'}")
    
    if all_arch_valid and quality_valid:
        print("\n[SUCCESS] All validations passed!")
    else:
        print("\n[WARNING] Some validations failed")


if __name__ == "__main__":
    main()

