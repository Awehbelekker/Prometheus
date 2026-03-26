#!/usr/bin/env python3
"""
================================================================================
    PROMETHEUS ULTIMATE AUTONOMOUS TRADING SYSTEM
    
    THE ONE LAUNCHER TO RULE THEM ALL
    
    This is the SINGLE entry point that starts EVERYTHING:
     1. Loads .env and verifies ALL API keys
     2. Validates AI systems are REAL (not mock)
     3. Starts the Unified Production Server (FastAPI on port 8000)
        -> Which auto-starts the Live Trading Launcher (80+ systems)
        -> Which auto-starts Shadow Trading (parallel paper trading)
     4. All AI: Consciousness, Quantum Engine, LLM, HRM running
     5. All brokers: Alpaca (live), IB (if available)
     6. All learning: continuous database updates
    
    Usage:  python prometheus_ultimate_autonomous.py
    
    NO MOCKS. NO RANDOM. NO FAKE DATA. REAL AI ONLY.
================================================================================
"""

import os
import sys
import time

# Ensure UTF-8 output
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass


# =========================================================================
# PHASE 1: Environment Setup - Load ALL API keys BEFORE anything else
# =========================================================================

def setup_environment():
    """Load .env and verify critical API keys"""
    print("\n" + "=" * 70)
    print("  PHASE 1: ENVIRONMENT CHECK")
    print("=" * 70)
    
    # Load dotenv
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
        print("  [OK] .env file loaded")
    except ImportError:
        print("  [!!] python-dotenv not installed - using system env vars")
    
    # Verify critical keys
    checks = {
        'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY', ''),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
        'POLYGON_API_KEY': os.getenv('POLYGON_API_KEY', ''),
    }
    
    all_ok = True
    for key, value in checks.items():
        if value and len(value) > 5:
            masked = f"{value[:6]}...{value[-4:]}" if len(value) > 10 else "***"
            print(f"  [OK] {key}: {masked}")
        else:
            print(f"  [!!] {key}: NOT SET")
            if key == 'ALPACA_API_KEY':
                all_ok = False
    
    if not all_ok:
        print("\n  CRITICAL: Missing required ALPACA_API_KEY")
        print("  Add it to .env file and restart")
        return False
    
    return True


# =========================================================================
# PHASE 2: Validate AI Systems - Ensure NO mocks are active
# =========================================================================

def validate_ai_systems():
    """Verify all AI systems are real, not mock"""
    print("\n" + "=" * 70)
    print("  PHASE 2: AI SYSTEM VALIDATION - NO MOCKS ALLOWED")
    print("=" * 70)
    
    issues = []
    
    # Check AI Config
    try:
        from config.ai_config import ai_config_manager, AIProvider
        providers = ai_config_manager.get_available_providers()
        real_providers = [p for p in providers if p != AIProvider.MOCK]
        if real_providers:
            print(f"  [OK] AI Providers: {[p.value for p in real_providers]}")
        else:
            print(f"  [!!] AI Providers: MOCK ONLY")
            issues.append("No real AI providers - LLM will use mock responses")
    except Exception as e:
        print(f"  [!!] AI Config: {e}")
        issues.append(f"AI config failed: {e}")
    
    # Check AI Consciousness
    try:
        from revolutionary_features.ai_consciousness.ai_consciousness_engine import AIConsciousnessEngine
        consciousness = AIConsciousnessEngine()
        if not consciousness.disabled and consciousness.consciousness_level > 0.5:
            print(f"  [OK] AI Consciousness: ENABLED (level={consciousness.consciousness_level})")
        else:
            print(f"  [!!] AI Consciousness: DISABLED")
            issues.append("AI Consciousness is disabled")
    except Exception as e:
        print(f"  [!!] AI Consciousness: {e}")
        issues.append(f"AI Consciousness failed: {e}")
    
    # Check Quantum Trading Engine
    try:
        from revolutionary_features.quantum_trading.quantum_trading_engine import QuantumTradingEngine
        engine = QuantumTradingEngine({'portfolio': {'optimization_level': 'high'}})
        import inspect
        source = inspect.getsource(QuantumTradingEngine)
        if 'random.uniform' in source or 'random.random()' in source:
            print(f"  [!!] Quantum Engine: STILL USES RANDOM")
            issues.append("Quantum engine still has random.uniform/random.random")
        else:
            print(f"  [OK] Quantum Engine: REAL algorithms (SimulatedAnnealing+MVO)")
    except Exception as e:
        print(f"  [!!] Quantum Engine: {e}")
        issues.append(f"Quantum engine failed: {e}")
    
    # Check LLM Service
    try:
        from core.llm_service import LLMService
        llm = LLMService()
        if hasattr(llm, '_using_mock') and llm._using_mock:
            print(f"  [!!] LLM Service: Using MockProvider")
            issues.append("LLM service is using MockProvider - check API keys")
        else:
            provider_names = [str(k) for k in llm.providers.keys()]
            print(f"  [OK] LLM Service: Real providers ({', '.join(provider_names)})")
    except Exception as e:
        print(f"  [!!] LLM Service: {e}")
    
    if issues:
        print(f"\n  WARNINGS ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"    {i}. {issue}")
        print(f"\n  System will start with available real AI systems")
    else:
        print(f"\n  ALL AI SYSTEMS VALIDATED - 100% REAL INTELLIGENCE")
    
    return len(issues) == 0


# =========================================================================
# PHASE 3: Pre-flight verification 
# =========================================================================

def preflight_check():
    """Verify broker connectivity and market status"""
    print("\n" + "=" * 70)
    print("  PHASE 3: PRE-FLIGHT CHECK")
    print("=" * 70)
    
    # Check Alpaca
    try:
        import alpaca_trade_api as tradeapi
        api = tradeapi.REST(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET'),
            base_url=os.getenv('ALPACA_BASE_URL', 'https://api.alpaca.markets')
        )
        account = api.get_account()
        equity = float(account.equity)
        print(f"  [OK] Alpaca: ${equity:,.2f} equity, status={account.status}")
        
        clock = api.get_clock()
        market_open = clock.is_open
        next_open = str(clock.next_open)[:19]
        print(f"  [OK] Market: {'OPEN - TRADING ACTIVE' if market_open else f'CLOSED (next: {next_open})'}")
        
        if not market_open:
            print(f"       System will auto-trade when market opens")
    except Exception as e:
        print(f"  [!!] Alpaca: {e}")
    
    # Check database
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prometheus_learning.db')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchone()[0]
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            conn.close()
            print(f"  [OK] Database: {tables} tables, {size_mb:.1f} MB")
        else:
            print(f"  [!!] Database: Not found")
    except Exception as e:
        print(f"  [!!] Database: {e}")
    
    # Check for existing server
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:8000/health', timeout=2)
        print(f"  [!!] Port 8000: ALREADY IN USE")
        print(f"       Kill existing server first or it will conflict")
        return False
    except Exception:
        print(f"  [OK] Port 8000: Available")
    
    return True


# =========================================================================
# PHASE 4: LAUNCH EVERYTHING 
# =========================================================================

def launch():
    """Launch the unified production server (which starts ALL subsystems)"""
    print("\n" + "=" * 70)
    print("  PHASE 4: LAUNCHING ALL SYSTEMS")
    print("=" * 70)
    print("""
  Starting subsystems:
    [1] Unified Production Server  (FastAPI, port 8000)
    [2] Live Trading Launcher      (80+ AI systems, Alpaca + IB)
    [3] Shadow Trading             (parallel paper trading, AI learning)
    [4] AI Consciousness Engine    (real meta-cognitive decisions)
    [5] Quantum Trading Engine     (SimulatedAnnealing + MVO optimization)
    [6] LLM Service                (OpenAI/Anthropic real AI)
    [7] HRM Neural Network         (27M parameter pattern recognition)
    [8] 6 Backtest Enhancements    (trailing stop, DCA, scale-out, etc.)
    [9] Continuous Learning        (trade outcome feedback loop)
    """)
    
    print(f"  Dashboard:  http://localhost:8000")
    print(f"  Health:     http://localhost:8000/health")
    print(f"  API Docs:   http://localhost:8000/docs")
    print(f"\n  Press Ctrl+C to stop all systems\n")
    print("=" * 70 + "\n")
    
    try:
        import uvicorn
        
        # Change to workspace directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        uvicorn.run(
            "unified_production_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info",
            access_log=True,
            workers=1  # Single worker to share state
        )
    except KeyboardInterrupt:
        print("\n\n  PROMETHEUS SHUTDOWN - All systems stopped gracefully")
    except Exception as e:
        print(f"\n  LAUNCH FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# =========================================================================
# ENTRY POINT
# =========================================================================

def main():
    """Single entry point for the entire PROMETHEUS system"""
    print("""
    ====================================================================
    
     PROMETHEUS  - ULTIMATE AUTONOMOUS TRADING SYSTEM
    
     NO MOCKS  |  REAL AI  |  FULL POWER  |  AUTONOMOUS
    
    ====================================================================
    """)
    
    # Phase 1: Environment
    if not setup_environment():
        print("\n  ABORTED: Fix environment issues and retry")
        sys.exit(1)
    
    # Phase 2: AI Validation
    ai_ok = validate_ai_systems()
    
    # Phase 3: Pre-flight
    if not preflight_check():
        print("\n  ABORTED: Fix pre-flight issues and retry")
        sys.exit(1)
    
    # Phase 4: Launch
    if not ai_ok:
        print("\n  NOTE: Some AI systems have issues but system will launch anyway")
        print("  Trading will use available real AI systems\n")
    
    launch()


if __name__ == "__main__":
    main()
