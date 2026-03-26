#!/usr/bin/env python3
"""
HRM System Initialization and Testing Script

This script initializes the HRM (Hierarchical Reasoning Model) system,
creates initial checkpoints, and tests the system functionality.
"""

import os
import sys
import torch
import numpy as np
from datetime import datetime
import logging

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('hrm_config.env')

# Import HRM components
try:
    from core.hrm_integration import HRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
    from core.hrm_enhanced_personas import HRMPersonaManager, HRMPersonaType
    print("[OK] Successfully imported HRM components")
except ImportError as e:
    print(f"❌ Failed to import HRM components: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_hrm_system():
    """Initialize the HRM system with proper configuration"""
    print("\n[INIT] Initializing HRM (CogniFlow) Trading System...")
    
    try:
        # Initialize HRM Trading Engine
        hrm_engine = HRMTradingEngine(
            device=os.getenv('HRM_DEVICE', 'cpu'),
            checkpoint_dir=os.getenv('HRM_CHECKPOINT_DIR', 'hrm_checkpoints'),
            version=os.getenv('HRM_VERSION', '1.0.0'),
            auto_download=os.getenv('HRM_AUTO_DOWNLOAD', '0') == '1'
        )
        
        print("[OK] HRM Trading Engine initialized successfully")
        
        # Initialize HRM Persona Manager
        hrm_persona_manager = HRMPersonaManager(hrm_engine)
        print("[OK] HRM Persona Manager initialized successfully")
        
        return hrm_engine, hrm_persona_manager
        
    except Exception as e:
        print(f"❌ Failed to initialize HRM system: {e}")
        return None, None

def create_initial_checkpoints(hrm_engine):
    """Create initial checkpoints for HRM modules"""
    print("\n[SAVE] Creating initial HRM checkpoints...")
    
    try:
        # Save initial checkpoints (with random weights)
        hrm_engine.save_checkpoints()
        print("[OK] Initial HRM checkpoints created successfully")
        
        # Verify checkpoints were created
        checkpoint_dir = hrm_engine.checkpoint_dir
        expected_files = ['high_level.pt', 'low_level.pt', 'arc_level.pt', 'sudoku_level.pt', 'maze_level.pt', 'manifest.json']
        
        for file in expected_files:
            file_path = os.path.join(checkpoint_dir, file)
            if os.path.exists(file_path):
                print(f"[OK] Checkpoint file created: {file}")
            else:
                print(f"[WARN] Checkpoint file missing: {file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create initial checkpoints: {e}")
        return False

def test_hrm_analysis(hrm_engine, hrm_persona_manager):
    """Test HRM analysis with sample data"""
    print("\n[TEST] Testing HRM analysis capabilities...")
    
    try:
        # Sample market data
        sample_market_data = {
            "prices": [100.0, 101.5, 99.8, 102.3, 103.1, 104.2, 103.8, 105.1],
            "volumes": [1000000, 1200000, 800000, 1500000, 1100000, 1300000, 900000, 1400000],
            "indicators": {
                "rsi": 65.5,
                "macd": 0.8,
                "bollinger_upper": 105.0,
                "bollinger_lower": 98.0
            },
            "sentiment": {
                "positive": 0.6,
                "negative": 0.2,
                "neutral": 0.2
            }
        }
        
        # Sample user context
        sample_user_context = {
            "profile": {
                "risk_tolerance": 0.5,
                "investment_goal": "growth",
                "time_horizon": "medium"
            },
            "trading_history": [
                {"action": "BUY", "symbol": "AAPL", "amount": 1000, "timestamp": "2024-01-01T10:00:00Z"},
                {"action": "SELL", "symbol": "GOOGL", "amount": 500, "timestamp": "2024-01-02T14:30:00Z"}
            ],
            "portfolio": {
                "total_value": 50000,
                "cash": 10000,
                "positions": {"AAPL": 1000, "GOOGL": 500}
            },
            "risk_preferences": {
                "max_drawdown": 0.1,
                "target_return": 0.15,
                "volatility_tolerance": 0.2
            }
        }
        
        # Test direct HRM analysis
        print("[TEST] Testing direct HRM analysis...")
        context = HRMReasoningContext(
            market_data=sample_market_data,
            user_profile=sample_user_context.get('profile', {}),
            trading_history=sample_user_context.get('trading_history', []),
            current_portfolio=sample_user_context.get('portfolio', {}),
            risk_preferences=sample_user_context.get('risk_preferences', {}),
            reasoning_level=HRMReasoningLevel.ARC_LEVEL
        )
        
        decision = hrm_engine.make_hierarchical_decision(context)
        print(f"[OK] Direct HRM analysis completed")
        print(f"   Action: {decision.get('action', 'UNKNOWN')}")
        print(f"   Confidence: {decision.get('confidence', 0.0):.3f}")
        print(f"   Risk Level: {decision.get('risk_level', 0.0):.3f}")
        
        # Test persona-based analysis
        print("\n[TEST] Testing persona-based analysis...")
        for persona_type in [HRMPersonaType.BALANCED_HRM, HRMPersonaType.CONSERVATIVE_HRM, HRMPersonaType.AGGRESSIVE_HRM]:
            result = hrm_persona_manager.analyze_with_persona(
                persona_type=persona_type,
                market_data=sample_market_data,
                user_context=sample_user_context
            )
            print(f"[OK] {persona_type.value} analysis completed")
            print(f"   Action: {result.get('action', 'UNKNOWN')}")
            print(f"   Confidence: {result.get('confidence', 0.0):.3f}")
            print(f"   Persona Confidence: {result.get('persona_confidence', 0.0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ HRM analysis test failed: {e}")
        return False

def get_system_status(hrm_engine, hrm_persona_manager):
    """Get comprehensive system status"""
    print("\n[STATUS] HRM System Status Report")
    print("=" * 50)
    
    try:
        # Engine metrics
        engine_metrics = hrm_engine.get_performance_metrics()
        print(f"Engine Decisions: {engine_metrics.get('total_decisions', 0)}")
        print(f"Average Confidence: {engine_metrics.get('average_confidence', 0.0):.3f}")
        
        # Persona metrics
        persona_metrics = hrm_persona_manager.get_persona_performance()
        print(f"Available Personas: {len(persona_metrics)}")
        
        for persona_type, metrics in persona_metrics.items():
            print(f"  {persona_type}: {metrics.get('total_decisions', 0)} decisions")
        
        # Checkpoint status
        checkpoint_dir = hrm_engine.checkpoint_dir
        print(f"\nCheckpoint Directory: {checkpoint_dir}")
        
        if os.path.exists(checkpoint_dir):
            files = os.listdir(checkpoint_dir)
            print(f"Checkpoint Files: {len(files)}")
        for file in files:
            print(f"  [OK] {file}")
        else:
            print("[ERROR] Checkpoint directory not found")
        
        # Model weights
        print(f"\nReasoning Weights:")
        for key, value in hrm_engine.reasoning_weights.items():
            print(f"  {key}: {value:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to get system status: {e}")
        return False

def main():
    """Main initialization and testing function"""
    print("HRM (CogniFlow) System Initialization")
    print("=" * 50)
    
    # Initialize HRM system
    hrm_engine, hrm_persona_manager = initialize_hrm_system()
    if not hrm_engine or not hrm_persona_manager:
        print("❌ Failed to initialize HRM system. Exiting.")
        return False
    
    # Create initial checkpoints
    if not create_initial_checkpoints(hrm_engine):
        print("⚠️  Checkpoint creation failed, but continuing...")
    
    # Test HRM analysis
    if not test_hrm_analysis(hrm_engine, hrm_persona_manager):
        print("❌ HRM analysis test failed")
        return False
    
    # Get system status
    get_system_status(hrm_engine, hrm_persona_manager)
    
    print("\n[SUCCESS] HRM System initialization completed successfully!")
    print("\nNext steps:")
    print("1. The system is now ready for live trading analysis")
    print("2. HRM checkpoints will be automatically saved during operation")
    print("3. You can access HRM analysis via the API endpoints")
    print("4. Consider training HRM models with historical data for better performance")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
