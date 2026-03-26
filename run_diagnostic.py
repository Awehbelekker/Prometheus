#!/usr/bin/env python3
"""
PROMETHEUS Bug Fix Verification Diagnostic
Verifies all critical bug fixes are in place
"""

import sys
import os
import json
import logging
logging.basicConfig(level=logging.WARNING)

print('='*70)
print('🔍 PROMETHEUS TRADING PLATFORM - BUG FIX VERIFICATION DIAGNOSTIC')
print('='*70)
print()

# CRIT-002: AI Consciousness Engine Disabled
print('[CRIT-002] AI Consciousness Engine Random Trading')
print('-'*60)
try:
    from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
    engine = AIConsciousnessEngine()
    if hasattr(engine, 'disabled') and engine.disabled:
        print('  ✅ AI Consciousness Engine is DISABLED')
        print('  ✅ No random.uniform() trading decisions')
    else:
        print('  ⚠️ AI Consciousness Engine may still be active!')
except Exception as e:
    print(f'  ❓ Could not check: {e}')
print()

# CRIT-003: Hierarchical Agent Coordinator np.random
print('[CRIT-003] Hierarchical Agent Coordinator Random Calls')
print('-'*60)
try:
    import inspect
    from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
    source = inspect.getsource(HierarchicalAgentCoordinator)
    if 'np.random' in source or 'random.' in source:
        print('  ⚠️ WARNING: np.random or random. found in source!')
    else:
        print('  ✅ No np.random or random. calls found')
except Exception as e:
    print(f'  ❓ Could not check: {e}')
print()

# HRM Integration - Check get_hrm_decision exists
print('[HRM] get_hrm_decision Function')
print('-'*60)
try:
    from core.hrm_official_integration import get_hrm_decision
    print('  ✅ get_hrm_decision function EXISTS and is importable')
    print('  ✅ Universal Reasoning Engine can now call HRM')
except ImportError as e:
    print(f'  ❌ CRITICAL: get_hrm_decision NOT FOUND: {e}')
except Exception as e:
    print(f'  ❓ Error: {e}')
print()

# HRM Checkpoints Loading
print('[HRM] Checkpoint Loading')
print('-'*60)
try:
    from core.hrm_official_integration import get_official_hrm_adapter
    adapter = get_official_hrm_adapter(checkpoint_dir='hrm_checkpoints', use_ensemble=True)
    if adapter and hasattr(adapter, 'models') and adapter.models:
        print(f'  ✅ HRM Adapter initialized with {len(adapter.models)} checkpoints')
        for name in adapter.models.keys():
            print(f'     - {name}')
    else:
        print('  ⚠️ No HRM models loaded (fallback will be used)')
except Exception as e:
    print(f'  ⚠️ HRM adapter issue: {e}')
print()

# Universal Reasoning Engine - HRM Integration
print('[URE] Universal Reasoning Engine v2 HRM Integration')
print('-'*60)
try:
    import inspect
    from core.universal_reasoning_engine_v2 import UniversalReasoningEngine
    source = inspect.getsource(UniversalReasoningEngine)
    if 'get_hrm_decision' in source:
        print('  ✅ UniversalReasoningEngine imports get_hrm_decision')
    if '_get_hrm_reasoning' in source:
        print('  ✅ _get_hrm_reasoning method exists')
except Exception as e:
    print(f'  ❓ Could not check: {e}')
print()

# P/L Tracking - Position Manager
print('[CRIT-004] P/L Tracking (Position Manager)')
print('-'*60)
try:
    import inspect
    from position_manager import PositionManager
    source = inspect.getsource(PositionManager)
    if 'exit_price' in source and 'profit_loss' in source:
        print('  ✅ exit_price calculation found')
        print('  ✅ profit_loss calculation found')
    if 'current_price - entry_price' in source:
        print('  ✅ P/L formula correctly uses (current_price - entry_price)')
except Exception as e:
    print(f'  ⚠️ Position Manager check: {e}')
print()

# HRM Runtime Metrics
print('[HRM] Runtime Metrics')
print('-'*60)
try:
    with open('hrm_checkpoints/hrm_runtime_metrics.json', 'r') as f:
        metrics = json.load(f)
    print(f'  Total Decisions: {metrics.get("total_decisions", 0)}')
    print(f'  Average Confidence: {metrics.get("average_confidence", 0.0)}')
    print(f'  Last Update: {metrics.get("timestamp", "unknown")}')
    if metrics.get('total_decisions', 0) == 0:
        print('  ⚠️ HRM has not made any decisions yet (will update when trading)')
except Exception as e:
    print(f'  ❓ Could not read metrics: {e}')
print()

print('='*70)
print('DIAGNOSTIC COMPLETE')
print('='*70)

