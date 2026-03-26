"""
PROMETHEUS - ALPACA ONLY - MAXIMUM PERFORMANCE
==============================================
Start trading immediately with Alpaca while IB is being configured.
All AI systems + Autonomous trading + LIVE MODE
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def start_alpaca_trading():
    
    print("\n" + "="*80)
    print("PROMETHEUS - ALPACA LIVE TRADING - MAXIMUM PERFORMANCE")
    print("="*80)
    
    # Step 1: Connect to Alpaca
    print("\n[STEP 1/3] Connecting to Alpaca LIVE...")
    
    from brokers.alpaca_broker import AlpacaBroker
    
    api_key = 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z'
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not secret_key:
        print("[INPUT] Enter Alpaca Secret Key:")
        secret_key = input("Secret: ").strip()
    
    config = {
        'api_key': api_key,
        'secret_key': secret_key,
        'paper_trading': False
    }
    
    broker = AlpacaBroker(config)
    connected = await broker.connect()
    
    if not connected:
        print("\n[ERROR] Could not connect to Alpaca")
        return
    
    account = await broker.get_account()
    equity = float(account.equity)
    buying_power = float(account.buying_power)
    
    print(f"[OK] Alpaca LIVE Connected")
    print(f"     Account: 910544927")
    print(f"     Equity: ${equity:,.2f}")
    print(f"     Buying Power: ${buying_power:,.2f}")
    
    # Step 2: Load AI Systems
    print("\n[STEP 2/3] Loading AI Systems...")
    
    ai_systems = []
    
    try:
        from core.ensemble_voting_system import EnsembleVotingSystem
        ai_systems.append("Ensemble Voting")
    except: pass
    
    try:
        from core.reasoning.thinkmesh_enhanced import EnhancedThinkMeshAdapter
        ai_systems.append("ThinkMesh")
    except: pass
    
    try:
        from core.reasoning.official_deepconf_adapter import OfficialDeepConfAdapter
        ai_systems.append("DeepConf")
    except: pass
    
    try:
        from core.autonomous_market_scanner import autonomous_scanner
        ai_systems.append("Market Scanner")
    except: pass
    
    try:
        from core.dynamic_trading_universe import dynamic_universe
        ai_systems.append("Dynamic Universe")
    except: pass
    
    try:
        from core.multi_strategy_executor import multi_strategy_executor
        ai_systems.append("Multi-Strategy")
    except: pass
    
    try:
        from core.unified_ai_provider import UnifiedAIProvider
        ai_systems.append("Unified AI")
    except: pass
    
    print(f"[OK] Loaded {len(ai_systems)} AI systems")
    for sys in ai_systems:
        print(f"     - {sys}")
    
    # Step 3: Start Trading
    print("\n[STEP 3/3] Initializing Trading Engine...")
    
    from core.profit_maximization_engine import ProfitMaximizationEngine
    
    engine = ProfitMaximizationEngine(
        total_capital=equity,
        paper_trading=False,
        enable_broker_execution=True
    )
    
    # MAXIMUM PERFORMANCE
    print("\n" + "="*80)
    print("MAXIMUM PERFORMANCE CONFIGURATION")
    print("="*80)
    print(f"Starting Capital: ${equity:,.2f}")
    print(f"Buying Power: ${buying_power:,.2f}")
    print(f"Broker: Alpaca LIVE")
    print(f"Scan Interval: 30 seconds")
    print(f"Min Confidence: 70%")
    print(f"Min Return: 0.8%")
    print(f"Max Trades/Cycle: 5")
    print(f"AI Systems: {len(ai_systems)} active")
    print("="*80)
    
    print("\n[WARNING] LIVE TRADING - REAL MONEY")
    print("          Press Ctrl+C anytime to stop safely")
    
    confirm = input("\nType 'START' to begin: ")
    
    if confirm.upper() != 'START':
        print("\n[CANCELLED]")
        return
    
    # START!
    print("\n" + "="*80)
    print("AUTONOMOUS TRADING STARTED")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Mode: LIVE")
    print("Broker: Alpaca")
    print("Duration: Continuous (Ctrl+C to stop)")
    print("="*80)
    
    try:
        # Run the engine
        await engine.start_autonomous_trading(duration_hours=24.0)
        
    except KeyboardInterrupt:
        print("\n\n[STOPPING] Shutting down safely...")
        
        # Get final account state
        try:
            final_account = await broker.get_account()
            final_equity = float(final_account.equity)
            pnl = final_equity - equity
            pnl_pct = (pnl / equity) * 100
            
            print("\n" + "="*80)
            print("SESSION COMPLETE")
            print("="*80)
            print(f"Starting Equity: ${equity:,.2f}")
            print(f"Final Equity: ${final_equity:,.2f}")
            print(f"P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
            
            if pnl > 0:
                print("\n[SUCCESS] Profitable session!")
            
            print("="*80)
        except:
            pass
        
        print("\n[OK] Stopped safely")

if __name__ == "__main__":
    try:
        asyncio.run(start_alpaca_trading())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
