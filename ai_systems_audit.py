#!/usr/bin/env python3
"""Comprehensive AI Systems Audit for PROMETHEUS Trading Platform"""
import sys
import os
import logging
logging.basicConfig(level=logging.WARNING)

def audit_ai_systems():
    print("="*70)
    print("PROMETHEUS AI SYSTEMS COMPREHENSIVE AUDIT")
    print("="*70)
    
    results = {}
    
    # 1. Core AI Systems
    print("\n[1] CORE AI SYSTEMS")
    print("-"*50)
    
    # ThinkMesh
    try:
        from core.reasoning.thinkmesh_enhanced import EnhancedThinkMeshAdapter
        adapter = EnhancedThinkMeshAdapter()
        results['ThinkMesh Enhanced'] = 'OK'
        print(f"  ThinkMesh Enhanced: AVAILABLE")
    except Exception as e:
        results['ThinkMesh Enhanced'] = 'ERROR'
        print(f"  ThinkMesh Enhanced: ERROR - {str(e)[:50]}")
    
    try:
        from core.reasoning.thinkmesh_production import ProductionThinkMeshAdapter
        adapter = ProductionThinkMeshAdapter()
        results['ThinkMesh Production'] = 'OK'
        print(f"  ThinkMesh Production: AVAILABLE")
    except Exception as e:
        results['ThinkMesh Production'] = 'ERROR'
        print(f"  ThinkMesh Production: ERROR - {str(e)[:50]}")
    
    # MASS Framework
    try:
        from core.mass_coordinator import MASSCoordinator
        mass = MASSCoordinator()
        results['MASS Coordinator'] = 'OK'
        print(f"  MASS Coordinator: AVAILABLE")
        print(f"    - Agents: {len(mass.agents)}")
    except Exception as e:
        results['MASS Coordinator'] = 'ERROR'
        print(f"  MASS Coordinator: ERROR - {str(e)[:50]}")

    # MASS Framework Optimizers
    try:
        from core.mass_framework import MassPromptOptimizer, MassTopologyOptimizer
        results['MASS Optimizers'] = 'OK'
        print(f"  MASS Optimizers: AVAILABLE")
    except Exception as e:
        results['MASS Optimizers'] = 'ERROR'
        print(f"  MASS Optimizers: ERROR - {str(e)[:50]}")
    
    # Universal Reasoning Engine
    try:
        from core.universal_reasoning_engine import UniversalReasoningEngine
        ure = UniversalReasoningEngine()
        results['Universal Reasoning Engine'] = 'OK'
        print(f"  Universal Reasoning Engine: AVAILABLE")
        if ure.official_hrm:
            results['HRM Official'] = 'OK'
            print(f"    - Official HRM: LOADED ({len(ure.official_hrm.models)} checkpoints)")
            print(f"    - Checkpoints: {list(ure.official_hrm.models.keys())}")
        else:
            results['HRM Official'] = 'NOT LOADED'
            print(f"    - Official HRM: NOT LOADED")
    except Exception as e:
        results['Universal Reasoning Engine'] = 'ERROR'
        print(f"  Universal Reasoning Engine: ERROR - {str(e)[:50]}")
    
    # 2. AI Agents
    print("\n[2] AI AGENTS")
    print("-"*50)
    
    try:
        from core.hierarchical_agent_coordinator import HierarchicalAgentCoordinator
        hac = HierarchicalAgentCoordinator()
        results['Hierarchical Agent Coordinator'] = 'OK'
        print(f"  Hierarchical Agent Coordinator: AVAILABLE")
        print(f"    - Supervisor agents: {list(hac.supervisor_agents.keys())}")
        print(f"    - Execution swarm: {list(hac.execution_swarm.keys())}")
    except Exception as e:
        results['Hierarchical Agent Coordinator'] = 'ERROR'
        print(f"  Hierarchical Agent Coordinator: ERROR - {str(e)[:50]}")
    
    # 3. AI Engines
    print("\n[3] AI ENGINES")
    print("-"*50)
    
    # GPT-OSS
    try:
        from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
        gpt = GPTOSSTradingAdapter()
        results['GPT-OSS Adapter'] = 'OK'
        print(f"  GPT-OSS Trading Adapter: AVAILABLE")
    except Exception as e:
        results['GPT-OSS Adapter'] = 'ERROR'
        print(f"  GPT-OSS Trading Adapter: ERROR - {str(e)[:50]}")
    
    # Quantum Trading
    try:
        from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
        qte = QuantumTradingEngine({'portfolio': {'max_qubits': 50}})
        results['Quantum Trading Engine'] = 'OK'
        print(f"  Quantum Trading Engine: AVAILABLE ({qte.max_qubits} qubits)")
    except Exception as e:
        results['Quantum Trading Engine'] = 'ERROR'
        print(f"  Quantum Trading Engine: ERROR - {str(e)[:50]}")
    
    # DeepConf
    try:
        from core.reasoning.official_deepconf_adapter import OfficialDeepConfAdapter
        results['DeepConf'] = 'OK'
        print(f"  DeepConf Adapter: AVAILABLE")
    except Exception as e:
        results['DeepConf'] = 'ERROR'
        print(f"  DeepConf Adapter: ERROR - {str(e)[:50]}")
    
    # Pattern Recognition
    try:
        from core.pattern_integration import PatternIntegration
        pi = PatternIntegration()
        results['Pattern Integration'] = 'OK'
        print(f"  Pattern Integration: AVAILABLE")
    except Exception as e:
        results['Pattern Integration'] = 'ERROR'
        print(f"  Pattern Integration: ERROR - {str(e)[:50]}")
    
    # 4. GLM-4 Integration
    print("\n[4] GLM-4 INTEGRATION")
    print("-"*50)

    try:
        import os
        api_key = os.getenv('ZHIPUAI_API_KEY')
        if api_key and api_key != 'your_zhipu_api_key_here':
            results['GLM-4 API Key'] = 'CONFIGURED'
            print(f"  GLM-4 API Key: CONFIGURED")
        else:
            results['GLM-4 API Key'] = 'NOT CONFIGURED'
            print(f"  GLM-4 API Key: NOT CONFIGURED")
    except:
        results['GLM-4 API Key'] = 'ERROR'
        print(f"  GLM-4 API Key: ERROR")

    # Check GLM repos
    glm_path = os.path.join(os.getcwd(), 'integrated_repos', 'GLM-4.5')
    glm_v_path = os.path.join(os.getcwd(), 'integrated_repos', 'GLM-V')
    if os.path.exists(glm_path):
        results['GLM-4.5 Repo'] = 'OK'
        print(f"  GLM-4.5 Repository: AVAILABLE")
    if os.path.exists(glm_v_path):
        results['GLM-V Repo'] = 'OK'
        print(f"  GLM-V (Vision) Repository: AVAILABLE")

    # 5. Summary
    print("\n" + "="*70)
    print("AUDIT SUMMARY")
    print("="*70)
    ok = sum(1 for v in results.values() if v == 'OK')
    configured = sum(1 for v in results.values() if v == 'CONFIGURED')
    errors = sum(1 for v in results.values() if 'ERROR' in v)
    not_loaded = sum(1 for v in results.values() if 'NOT' in str(v))
    print(f"  OPERATIONAL: {ok}")
    print(f"  CONFIGURED: {configured}")
    print(f"  NOT CONFIGURED/LOADED: {not_loaded}")
    print(f"  ERRORS: {errors}")
    print(f"  TOTAL SYSTEMS: {len(results)}")

    return results

if __name__ == "__main__":
    audit_ai_systems()

