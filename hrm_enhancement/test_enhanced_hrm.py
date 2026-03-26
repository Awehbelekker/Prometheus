#!/usr/bin/env python3
"""
Test script for Enhanced HRM Integration
Tests the integration between official HRM and PROMETHEUS HRM
"""

import sys
from pathlib import Path
import logging

# Add integration directory to path
sys.path.append(str(Path(__file__).parent / "hrm_enhancement"))

try:
    from enhanced_hrm_integration import EnhancedHRMTradingEngine, HRMReasoningContext
    logger = logging.getLogger(__name__)
    
    def test_enhanced_hrm():
        """Test enhanced HRM functionality"""
        print("🧪 Testing Enhanced HRM Integration...")
        
        # Initialize enhanced HRM
        enhanced_hrm = EnhancedHRMTradingEngine()
        
        # Test context
        context = HRMReasoningContext(
            market_data={
                'price': 150.0,
                'volume': 1000000,
                'indicators': {'rsi': 65, 'macd': 0.5, 'bollinger_upper': 155, 'bollinger_lower': 145}
            },
            user_profile={'risk_tolerance': 'medium', 'experience': 'intermediate'},
            trading_history=[],
            current_portfolio={'cash': 10000, 'positions': {}},
            risk_preferences={'max_position_size': 0.1, 'stop_loss': 0.05},
            reasoning_level='HIGH_LEVEL'
        )
        
        # Test decision making
        print("\n📊 Testing decision making...")
        decision = enhanced_hrm.make_enhanced_decision(context)
        print(f"Decision: {decision}")
        
        # Test metrics
        print("\n📈 Testing metrics...")
        metrics = enhanced_hrm.get_enhancement_metrics()
        print(f"Metrics: {metrics}")
        
        print("\n✅ Enhanced HRM test completed successfully!")
        return True
        
    if __name__ == "__main__":
        test_enhanced_hrm()
        
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("Make sure to run the integration script first")
except Exception as e:
    print(f"[ERROR] Test error: {e}")
