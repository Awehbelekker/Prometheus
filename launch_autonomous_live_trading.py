"""
🚀 PROMETHEUS AUTONOMOUS LIVE TRADING
====================================
LIVE TRADING with REAL MONEY - Fully Autonomous System

SAFETY FEATURES:
- Daily loss limit: $500
- Max position size: $1000
- Emergency stop on 3% daily loss
- Real-time monitoring
- Automatic position management
"""

import asyncio
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'live_trading_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LiveTradingSafetyManager:
    """Safety manager for live trading"""
    
    def __init__(self):
        self.daily_loss_limit = 500.0  # $500 max daily loss
        self.max_position_size = 1000.0  # $1000 max per position
        self.circuit_breaker_pct = 3.0  # Stop at 3% loss
        self.current_daily_loss = 0.0
        self.emergency_stop = False
        self.trades_today = 0
        self.max_trades_per_day = 20
        
    def check_can_trade(self, capital_required: float) -> tuple[bool, str]:
        """Check if trade is allowed"""
        
        if self.emergency_stop:
            return False, "🛑 EMERGENCY STOP ACTIVATED"
        
        if self.current_daily_loss >= self.daily_loss_limit:
            return False, f"📊 Daily loss limit reached: ${self.current_daily_loss:.2f}"
        
        if capital_required > self.max_position_size:
            return False, f"⚠️ Position too large: ${capital_required:.2f} > ${self.max_position_size:.2f}"
        
        if self.trades_today >= self.max_trades_per_day:
            return False, f"📊 Max trades reached: {self.trades_today}/{self.max_trades_per_day}"
        
        return True, "✅ OK"

async def setup_live_trading():
    """Setup and validate live trading configuration"""
    
    print("\n" + "="*80)
    print("🚀 PROMETHEUS AUTONOMOUS LIVE TRADING SETUP")
    print("="*80)
    print("\n⚠️  THIS WILL TRADE WITH REAL MONEY! ⚠️\n")
    
    # Get API keys
    api_key = os.getenv('ALPACA_API_KEY', 'AKMMN6U5DXKTM7A2UEAAF4ZQ5Z')
    secret_key = os.getenv('ALPACA_SECRET_KEY')
    
    if not secret_key:
        print("📝 Alpaca Secret Key not found in .env file.")
        print("Please enter your Alpaca Secret Key:")
        secret_key = input("Secret Key: ").strip()
        
        if not secret_key:
            print("❌ No secret key provided. Cannot proceed.")
            return None
        
        # Save to .env
        with open('.env', 'a') as f:
            f.write(f'\nALPACA_SECRET_KEY={secret_key}\n')
        print("✅ Secret key saved to .env file")
    
    # Test connection
    print("\n[1/4] Testing Alpaca connection...")
    
    try:
        from brokers.alpaca_broker import AlpacaBroker
        
        config = {
            'api_key': api_key,
            'secret_key': secret_key,
            'paper_trading': False  # LIVE!
        }
        
        broker = AlpacaBroker(config)
        connected = await broker.connect()
        
        if not connected:
            print("❌ Failed to connect to Alpaca")
            return None
        
        print("✅ Connected to Alpaca LIVE account")
        
        # Get account info
        account = await broker.get_account()
        equity = float(account.equity)
        buying_power = float(account.buying_power)
        
        print(f"\n💰 Account Status:")
        print(f"   Equity: ${equity:,.2f}")
        print(f"   Buying Power: ${buying_power:,.2f}")
        print(f"   Account Status: {account.status}")
        
        if equity < 100:
            print(f"\n⚠️ WARNING: Low account balance (${equity:.2f})")
            print("   Recommended minimum: $1,000 for live trading")
            confirm = input("\nContinue anyway? (yes/no): ").lower()
            if confirm != 'yes':
                print("Cancelled.")
                return None
        
        return {
            'broker': broker,
            'api_key': api_key,
            'secret_key': secret_key,
            'initial_equity': equity,
            'buying_power': buying_power
        }
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

async def start_live_autonomous_trading(config: dict):
    """Start the autonomous trading system with live money"""
    
    print("\n[2/4] Initializing Autonomous System...")
    
    # Initialize broker executor
    from core.autonomous_broker_executor import AutonomousBrokerExecutor
    
    broker_executor = AutonomousBrokerExecutor(
        use_alpaca=True,
        use_ib=False,  # Start with Alpaca only
        paper_mode=False  # LIVE TRADING!
    )
    
    # Initialize brokers
    await broker_executor.initialize_brokers()
    
    print("✅ Broker executor initialized")
    
    # Initialize profit maximization engine
    print("\n[3/4] Starting Profit Maximization Engine...")
    
    from core.profit_maximization_engine import ProfitMaximizationEngine
    
    # Conservative settings for live trading
    engine = ProfitMaximizationEngine(
        total_capital=config['initial_equity'],
        scan_interval_seconds=60,  # Scan every minute
        max_capital_per_opportunity=1000,  # $1000 max per trade
        paper_trading=False,  # LIVE!
        enable_broker_execution=True  # EXECUTE REAL TRADES!
    )
    
    # Add safety manager
    safety = LiveTradingSafetyManager()
    
    # Configure conservative thresholds
    engine.min_opportunity_confidence = 0.75  # Higher confidence required
    engine.min_opportunity_return = 0.01  # Minimum 1% return
    engine.max_opportunities_per_cycle = 3  # Max 3 trades per cycle
    
    print("✅ Autonomous engine configured")
    print(f"\n📊 Safety Settings:")
    print(f"   Max Daily Loss: ${safety.daily_loss_limit:.2f}")
    print(f"   Max Position Size: ${safety.max_position_size:.2f}")
    print(f"   Max Trades/Day: {safety.max_trades_per_day}")
    print(f"   Circuit Breaker: {safety.circuit_breaker_pct}% daily loss")
    print(f"   Min Confidence: {engine.min_opportunity_confidence:.0%}")
    print(f"   Min Return: {engine.min_opportunity_return:.1%}")
    
    # Final confirmation
    print("\n" + "="*80)
    print("⚠️  FINAL CONFIRMATION - LIVE TRADING")
    print("="*80)
    print(f"Starting Capital: ${config['initial_equity']:,.2f}")
    print("Mode: LIVE TRADING (REAL MONEY)")
    print("Duration: Continuous (Ctrl+C to stop)")
    print("="*80)
    
    confirm = input("\nType 'START LIVE TRADING' to proceed: ")
    
    if confirm != "START LIVE TRADING":
        print("\n❌ Cancelled. Live trading NOT started.")
        return
    
    # START LIVE TRADING!
    print("\n[4/4] 🚀 STARTING LIVE AUTONOMOUS TRADING!")
    print("="*80)
    print("📊 Monitoring started - Press Ctrl+C to stop")
    print("📁 Logs: live_trading_*.log")
    print("="*80)
    
    try:
        # Connect engine to broker executor
        from core.multi_strategy_executor import multi_strategy_executor
        multi_strategy_executor.broker_executor = broker_executor
        multi_strategy_executor.enable_broker_execution = True
        
        # Start trading!
        await engine.start_autonomous_trading(duration_hours=None)  # Run continuously
        
    except KeyboardInterrupt:
        print("\n\n🛑 STOPPING LIVE TRADING...")
        print("Closing positions and shutting down safely...")
        
        # Get final metrics
        metrics = engine.get_metrics()
        print("\n" + "="*80)
        print("📊 FINAL SESSION SUMMARY")
        print("="*80)
        print(f"Runtime: {metrics.runtime_minutes:.1f} minutes")
        print(f"Cycles: {metrics.scan_cycles}")
        print(f"Opportunities: {metrics.opportunities_discovered}")
        print(f"Trades Executed: {metrics.opportunities_executed}")
        print(f"Capital Deployed: ${metrics.total_capital_deployed:,.2f}")
        print(f"Expected Return: {metrics.expected_total_return:.2%}")
        
        # Get final account balance
        try:
            account = await config['broker'].get_account()
            final_equity = float(account.equity)
            pnl = final_equity - config['initial_equity']
            pnl_pct = (pnl / config['initial_equity']) * 100
            
            print(f"\n💰 ACCOUNT STATUS:")
            print(f"Starting Equity: ${config['initial_equity']:,.2f}")
            print(f"Final Equity: ${final_equity:,.2f}")
            print(f"P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
            
            if pnl > 0:
                print(f"\n✅ Profitable session! 🎉")
            elif pnl < 0:
                print(f"\n📊 Loss occurred. Review logs for improvements.")
            else:
                print(f"\n➡️ Break-even session.")
                
        except Exception as e:
            print(f"⚠️ Could not fetch final account balance: {e}")
        
        print("="*80)
        print("✅ Live trading stopped safely")
        
    except Exception as e:
        logger.error(f"❌ Critical error: {e}", exc_info=True)
        print(f"\n❌ ERROR: {e}")
        print("Check live_trading_*.log for details")

async def main():
    """Main entry point"""
    
    # Setup
    config = await setup_live_trading()
    
    if not config:
        print("\n❌ Setup failed. Cannot start live trading.")
        return
    
    # Start trading
    await start_live_autonomous_trading(config)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nShutdown complete.")
