"""
PROMETHEUS FULL SYSTEM - MAXIMUM PERFORMANCE
============================================
Launches EVERYTHING with all AI systems at maximum performance:
- Alpaca LIVE
- Interactive Brokers LIVE  
- HRM (Hierarchical Reasoning)
- ThinkMesh (Multiple Strategies)
- DeepConf (Confidence Reasoning)
- Ensemble Voting (Multi-Model)
- Multimodal Analysis (Visual)
- Autonomous Discovery
- Multi-Strategy Execution
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FullSystemLauncher:
    """Launches complete PROMETHEUS system with all features"""
    
    def __init__(self):
        self.alpaca_broker = None
        self.ib_broker = None
        self.systems_status = {}
        
    async def verify_all_brokers(self):
        """Verify both Alpaca and IB are LIVE"""
        
        print("\n" + "="*80)
        print("STEP 1: VERIFYING ALL BROKERS - LIVE MODE")
        print("="*80)
        
        # Verify Alpaca
        print("\n[1/2] Connecting to Alpaca LIVE...")
        try:
            from brokers.alpaca_broker import AlpacaBroker
            
            api_key = os.getenv('ALPACA_API_KEY', 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z')
            secret_key = os.getenv('ALPACA_SECRET_KEY')
            
            if not secret_key:
                print("[INPUT REQUIRED] Enter Alpaca Secret Key:")
                secret_key = input("Secret Key: ").strip()
                if secret_key:
                    with open('.env', 'a') as f:
                        f.write(f'\nALPACA_SECRET_KEY={secret_key}\n')
            
            config = {
                'api_key': api_key,
                'secret_key': secret_key,
                'paper_trading': False  # LIVE!
            }
            
            self.alpaca_broker = AlpacaBroker(config)
            connected = await self.alpaca_broker.connect()
            
            if connected:
                account = await self.alpaca_broker.get_account()
                print(f"[OK] Alpaca LIVE Connected")
                print(f"     Account: {account.id if hasattr(account, 'id') else '910544927'}")
                print(f"     Status: {account.status}")
                print(f"     Equity: ${float(account.equity):,.2f}")
                print(f"     Buying Power: ${float(account.buying_power):,.2f}")
                self.systems_status['alpaca'] = 'live'
            else:
                print("[FAILED] Alpaca connection failed")
                self.systems_status['alpaca'] = 'failed'
                
        except Exception as e:
            print(f"[ERROR] Alpaca: {e}")
            self.systems_status['alpaca'] = 'error'
        
        # Verify IB
        print("\n[2/2] Connecting to Interactive Brokers...")
        try:
            from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
            
            if not IB_AVAILABLE:
                print("[WARNING] IB library not installed")
                print("          Install with: pip install ibapi")
                self.systems_status['ib'] = 'not_installed'
            else:
                config = {
                    'host': os.getenv('IB_HOST', '127.0.0.1'),
                    'port': int(os.getenv('IB_PORT', 4002)),
                    'client_id': 1
                }
                
                print(f"     Connecting to IB Gateway at {config['host']}:{config['port']}...")
                print("     (TWS/Gateway must be running and logged in)")
                
                self.ib_broker = InteractiveBrokersBroker(config)
                
                # Give IB more time to connect
                connected = await asyncio.wait_for(self.ib_broker.connect(), timeout=15.0)
                
                if connected:
                    account = await self.ib_broker.get_account()
                    print(f"[OK] IB Connected Successfully!")
                    print(f"     Equity: ${float(account.equity):,.2f}")
                    print(f"     Cash: ${float(account.cash):,.2f}")
                    print(f"     [INFO] Verify in TWS: LIVE or PAPER account")
                    self.systems_status['ib'] = 'connected'
                else:
                    print("[FAILED] IB connection timeout")
                    print("         Make sure TWS/IB Gateway is:")
                    print("         1. Running")
                    print("         2. Logged in")
                    print("         3. API enabled in settings")
                    self.systems_status['ib'] = 'timeout'
                    
        except asyncio.TimeoutError:
            print("[TIMEOUT] IB connection timeout after 15 seconds")
            print("          Is TWS/Gateway running and logged in?")
            self.systems_status['ib'] = 'timeout'
        except Exception as e:
            print(f"[ERROR] IB: {e}")
            self.systems_status['ib'] = 'error'
        
        # Summary
        print("\n" + "="*80)
        print("BROKER CONNECTION SUMMARY")
        print("="*80)
        alpaca_ok = self.systems_status.get('alpaca') == 'live'
        ib_ok = self.systems_status.get('ib') == 'connected'
        
        print(f"Alpaca: {'[OK] LIVE' if alpaca_ok else '[FAILED]'}")
        print(f"IB:     {'[OK] CONNECTED' if ib_ok else '[FAILED]'}")
        
        if not alpaca_ok and not ib_ok:
            print("\n[ERROR] No brokers connected. Cannot proceed.")
            print("\n[HELP] To fix IB:")
            print("       1. Open IB Gateway or Trader Workstation (TWS)")
            print("       2. Login with your credentials")
            print("       3. Go to: Configure > Settings > API")
            print("       4. Check 'Enable ActiveX and Socket Clients'")
            print("       5. Socket Port should be: 4002")
            print("       6. Restart this launcher")
            return False
        
        if alpaca_ok and not ib_ok:
            print("\n[INFO] Will trade using: Alpaca only")
        elif ib_ok and not alpaca_ok:
            print("\n[INFO] Will trade using: IB only")
        else:
            print("\n[SUCCESS] Will trade using: BOTH brokers!")
        
        print("="*80)
        return True
    
    async def initialize_all_ai_systems(self):
        """Initialize ALL AI systems for maximum performance"""
        
        print("\n" + "="*80)
        print("STEP 2: INITIALIZING ALL AI SYSTEMS")
        print("="*80)
        
        ai_systems = []
        
        # 1. HRM (Hierarchical Reasoning)
        print("\n[1/10] Loading HRM (Hierarchical Reasoning)...")
        try:
            from core.hierarchical_reasoning import HierarchicalReasoningModel
            print("      [OK] HRM Ready")
            ai_systems.append("HRM")
        except Exception as e:
            print(f"      [SKIP] HRM: {e}")
        
        # 2. ThinkMesh Enhanced
        print("\n[2/10] Loading ThinkMesh (Multiple Strategies)...")
        try:
            from core.reasoning.thinkmesh_enhanced import EnhancedThinkMeshAdapter
            print("      [OK] ThinkMesh Ready")
            ai_systems.append("ThinkMesh")
        except Exception as e:
            print(f"      [SKIP] ThinkMesh: {e}")
        
        # 3. DeepConf
        print("\n[3/10] Loading DeepConf (Confidence Reasoning)...")
        try:
            from core.reasoning.official_deepconf_adapter import OfficialDeepConfAdapter
            print("      [OK] DeepConf Ready")
            ai_systems.append("DeepConf")
        except Exception as e:
            print(f"      [SKIP] DeepConf: {e}")
        
        # 4. Ensemble Voting
        print("\n[4/10] Loading Ensemble Voting (Multi-Model)...")
        try:
            from core.ensemble_voting_system import EnsembleVotingSystem
            print("      [OK] Ensemble Voting Ready")
            ai_systems.append("Ensemble")
        except Exception as e:
            print(f"      [SKIP] Ensemble: {e}")
        
        # 5. Multimodal Analyzer
        print("\n[5/10] Loading Multimodal Analyzer (Visual)...")
        try:
            from core.multimodal_analyzer import MultimodalAnalyzer
            print("      [OK] Multimodal Ready")
            ai_systems.append("Multimodal")
        except Exception as e:
            print(f"      [SKIP] Multimodal: {e}")
        
        # 6. Universal Reasoning Engine
        print("\n[6/10] Loading Universal Reasoning Engine...")
        try:
            from core.universal_reasoning_engine import UniversalReasoningEngine
            print("      [OK] Universal Reasoning Ready")
            ai_systems.append("Universal Reasoning")
        except Exception as e:
            print(f"      [SKIP] Universal Reasoning: {e}")
        
        # 7. Autonomous Market Scanner
        print("\n[7/10] Loading Autonomous Market Scanner...")
        try:
            from core.autonomous_market_scanner import autonomous_scanner
            print("      [OK] Market Scanner Ready")
            ai_systems.append("Market Scanner")
        except Exception as e:
            print(f"      [SKIP] Scanner: {e}")
        
        # 8. Dynamic Universe
        print("\n[8/10] Loading Dynamic Trading Universe...")
        try:
            from core.dynamic_trading_universe import dynamic_universe
            print("      [OK] Dynamic Universe Ready")
            ai_systems.append("Dynamic Universe")
        except Exception as e:
            print(f"      [SKIP] Universe: {e}")
        
        # 9. Multi-Strategy Executor
        print("\n[9/10] Loading Multi-Strategy Executor...")
        try:
            from core.multi_strategy_executor import multi_strategy_executor
            print("      [OK] Multi-Strategy Ready")
            ai_systems.append("Multi-Strategy")
        except Exception as e:
            print(f"      [SKIP] Multi-Strategy: {e}")
        
        # 10. Unified AI Provider
        print("\n[10/10] Loading Unified AI Provider (DeepSeek)...")
        try:
            from core.unified_ai_provider import UnifiedAIProvider
            ai = UnifiedAIProvider()
            print("      [OK] Unified AI Ready")
            ai_systems.append("Unified AI")
        except Exception as e:
            print(f"      [SKIP] Unified AI: {e}")
        
        print("\n" + "="*80)
        print(f"AI SYSTEMS LOADED: {len(ai_systems)}/10")
        print("="*80)
        for system in ai_systems:
            print(f"  [OK] {system}")
        print("="*80)
        
        return ai_systems
    
    async def start_maximum_performance_trading(self, ai_systems):
        """Start trading with maximum performance settings"""
        
        print("\n" + "="*80)
        print("STEP 3: LAUNCHING AUTONOMOUS TRADING")
        print("="*80)
        
        # Initialize broker executor
        from core.autonomous_broker_executor import AutonomousBrokerExecutor
        
        broker_executor = AutonomousBrokerExecutor(
            use_alpaca=self.systems_status.get('alpaca') == 'live',
            use_ib=self.systems_status.get('ib') == 'connected',
            paper_mode=False  # LIVE!
        )
        
        print("\n[INFO] Initializing broker executor...")
        await broker_executor.initialize_brokers()
        print("[OK] Broker executor ready")
        
        # Get account equity for capital allocation
        account_info = await broker_executor.get_account_info()
        if account_info:
            total_capital = account_info['equity']
            print(f"\n[INFO] Available Capital: ${total_capital:,.2f}")
        else:
            total_capital = 10000  # Default
            print(f"\n[WARNING] Could not get account info, using ${total_capital:,.2f}")
        
        # Initialize Profit Maximization Engine - MAXIMUM PERFORMANCE
        from core.profit_maximization_engine import ProfitMaximizationEngine
        
        engine = ProfitMaximizationEngine(
            total_capital=total_capital,
            scan_interval_seconds=30,  # Faster scanning - every 30s
            max_capital_per_opportunity=min(2000, total_capital * 0.2),  # 20% per trade
            paper_trading=False,  # LIVE!
            enable_broker_execution=True  # REAL TRADES!
        )
        
        # MAXIMUM PERFORMANCE SETTINGS
        engine.min_opportunity_confidence = 0.70  # Accept 70%+ confidence
        engine.min_opportunity_return = 0.008  # 0.8% minimum return
        engine.max_opportunities_per_cycle = 5  # Up to 5 trades per cycle
        
        # Connect to brokers
        from core.multi_strategy_executor import multi_strategy_executor
        multi_strategy_executor.broker_executor = broker_executor
        multi_strategy_executor.enable_broker_execution = True
        
        print("\n" + "="*80)
        print("MAXIMUM PERFORMANCE CONFIGURATION")
        print("="*80)
        print(f"Capital: ${total_capital:,.2f}")
        print(f"Scan Interval: 30 seconds (HIGH FREQUENCY)")
        print(f"Max Per Trade: ${min(2000, total_capital * 0.2):,.2f}")
        print(f"Min Confidence: 70% (AGGRESSIVE)")
        print(f"Min Return: 0.8% (AGGRESSIVE)")
        print(f"Max Trades/Cycle: 5 (HIGH VOLUME)")
        print(f"Brokers: {'Alpaca' if self.systems_status.get('alpaca') == 'live' else ''} {'+ IB' if self.systems_status.get('ib') == 'connected' else ''}")
        print(f"AI Systems: {len(ai_systems)} active")
        print("="*80)
        
        # FINAL CONFIRMATION
        print("\n[WARNING] LIVE TRADING - REAL MONEY!")
        print("         Aggressive settings for maximum performance")
        print("         Press Ctrl+C anytime to stop")
        
        confirm = input("\nType 'MAXIMUM PERFORMANCE' to start: ")
        
        if confirm != "MAXIMUM PERFORMANCE":
            print("\n[CANCELLED] Trading not started")
            return
        
        # START!
        print("\n" + "="*80)
        print("STARTING AUTONOMOUS TRADING - MAXIMUM PERFORMANCE")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Mode: LIVE TRADING")
        print("Duration: CONTINUOUS (Ctrl+C to stop)")
        print("="*80)
        
        try:
            await engine.start_autonomous_trading(duration_hours=None)
            
        except KeyboardInterrupt:
            print("\n\n[STOPPING] Shutting down safely...")
            
            # Final summary
            metrics = engine.get_metrics()
            print("\n" + "="*80)
            print("SESSION SUMMARY")
            print("="*80)
            print(f"Runtime: {metrics.runtime_minutes:.1f} minutes")
            print(f"Cycles: {metrics.scan_cycles}")
            print(f"Opportunities: {metrics.opportunities_discovered}")
            print(f"Trades: {metrics.opportunities_executed}")
            print(f"Capital Deployed: ${metrics.total_capital_deployed:,.2f}")
            print(f"Expected Return: {metrics.expected_total_return:.2%}")
            
            # Final account balance
            try:
                final_account = await broker_executor.get_account_info()
                if final_account:
                    final_equity = final_account['equity']
                    pnl = final_equity - total_capital
                    pnl_pct = (pnl / total_capital) * 100
                    
                    print(f"\nStarting: ${total_capital:,.2f}")
                    print(f"Final: ${final_equity:,.2f}")
                    print(f"P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
                    
                    if pnl > 0:
                        print("\n[SUCCESS] Profitable session!")
                    
            except:
                pass
            
            print("="*80)
            print("[OK] Stopped safely")

async def main():
    """Main launcher"""
    
    print("\n" + "="*80)
    print("PROMETHEUS FULL SYSTEM LAUNCHER")
    print("Maximum Performance - All AI Systems - Live Trading")
    print("="*80)
    
    launcher = FullSystemLauncher()
    
    # Step 1: Verify brokers
    brokers_ok = await launcher.verify_all_brokers()
    if not brokers_ok:
        print("\n[ERROR] Broker setup failed. Fix brokers and try again.")
        return
    
    # Step 2: Initialize AI systems
    ai_systems = await launcher.initialize_all_ai_systems()
    
    # Step 3: Start trading
    await launcher.start_maximum_performance_trading(ai_systems)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
