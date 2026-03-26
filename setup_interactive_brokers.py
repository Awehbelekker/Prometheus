#!/usr/bin/env python3
"""
Interactive Brokers Setup and Integration for PROMETHEUS Trading Platform
Sets up IB paper trading with your credentials: wvtjnq273 / DUN683505
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any
import subprocess

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractiveBrokersSetup:
    """Setup Interactive Brokers integration for PROMETHEUS"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.ib_credentials = {
            'username': 'wvtjnq273',
            'account_number': 'DUN683505',
            'paper_trading': True
        }
        
    def run_setup(self):
        """Run complete IB setup process"""
        print("🏦 INTERACTIVE BROKERS SETUP FOR PROMETHEUS")
        print("=" * 60)
        print(f"Setting up IB Paper Trading Account: {self.ib_credentials['account_number']}")
        print(f"Username: {self.ib_credentials['username']}")
        print("=" * 60)
        
        # Step 1: Install IB API
        self._install_ib_api()
        
        # Step 2: Download IB Gateway
        self._setup_ib_gateway()
        
        # Step 3: Configure environment
        self._configure_environment()
        
        # Step 4: Create test connection
        self._test_connection()
        
        # Step 5: Integration with PROMETHEUS
        self._integrate_with_prometheus()
        
        print("\n[CHECK] Interactive Brokers setup complete!")
        print("Next steps:")
        print("1. Start IB Gateway with your credentials")
        print("2. Run the paper trading test")
        print("3. Begin live paper trading with PROMETHEUS")
    
    def _install_ib_api(self):
        """Install Interactive Brokers API"""
        print("\n🔧 STEP 1: Installing Interactive Brokers API")
        print("-" * 40)
        
        try:
            # Try to import ibapi
            import ibapi
            print("[CHECK] IB API already installed")
            return
        except ImportError:
            pass
        
        print("Installing IB API...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'ibapi'], check=True)
            print("[CHECK] IB API installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to install IB API: {e}")
            print("Manual installation:")
            print("pip install ibapi")
            sys.exit(1)
    
    def _setup_ib_gateway(self):
        """Setup IB Gateway download instructions"""
        print("\n🖥️ STEP 2: IB Gateway Setup")
        print("-" * 40)
        
        print("You need to download and install IB Gateway:")
        print("1. Go to: https://www.interactivebrokers.com/en/trading/ib-gateway.php")
        print("2. Download IB Gateway for Windows")
        print("3. Install IB Gateway")
        print("4. Configure for Paper Trading:")
        print(f"   - Username: {self.ib_credentials['username']}")
        print(f"   - Account: {self.ib_credentials['account_number']}")
        print("   - Trading Mode: Paper Trading")
        print("   - Socket Port: 7497 (Paper Trading)")
        print("5. Enable API connections in IB Gateway settings")
        
        input("\nPress Enter when IB Gateway is installed and configured...")
    
    def _configure_environment(self):
        """Configure environment variables"""
        print("\n⚙️ STEP 3: Configuring Environment")
        print("-" * 40)
        
        # Create .env.ib file
        env_content = f"""# Interactive Brokers Configuration for PROMETHEUS
# Paper Trading Account: {self.ib_credentials['account_number']}

# IB API Configuration
IB_ENABLED=true
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
IB_PAPER_TRADING=true
IB_ACCOUNT_ID={self.ib_credentials['account_number']}
IB_USERNAME={self.ib_credentials['username']}

# Trading Configuration for R 10,000 (~$540 USD)
STARTING_CAPITAL_USD=540.0
STARTING_CAPITAL_ZAR=10000.0

# Risk Management for Small Account
MAX_POSITION_SIZE_PERCENT=2.0
MAX_DAILY_TRADES=5
MAX_PORTFOLIO_RISK_PERCENT=1.0
DEFAULT_STOP_LOSS_PERCENT=2.0
EMERGENCY_STOP_LOSS_PERCENT=5.0
MAX_DAILY_LOSS_DOLLARS=25.0

# Broker Selection
PRIMARY_BROKER=interactive_brokers
SECONDARY_BROKER=alpaca
ENABLE_MULTI_BROKER=true

# Paper Trading Validation
VALIDATE_REAL_MARKET_DATA=true
PAPER_TRADING_MODE=ib_paper
"""
        
        env_file = self.project_root / '.env.ib'
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"[CHECK] Created IB configuration: {env_file}")
        
        # Update main .env file
        self._update_main_env()
    
    def _update_main_env(self):
        """Update main .env file with IB settings"""
        env_file = self.project_root / '.env'
        
        # Read existing .env
        env_content = ""
        if env_file.exists():
            with open(env_file, 'r') as f:
                env_content = f.read()
        
        # Add IB settings if not present
        ib_settings = """
# Interactive Brokers Integration
IB_ENABLED=true
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1
IB_PAPER_TRADING=true
PRIMARY_BROKER=interactive_brokers
"""
        
        if "IB_ENABLED" not in env_content:
            env_content += ib_settings
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print("[CHECK] Updated main .env file with IB settings")
    
    def _test_connection(self):
        """Test IB connection"""
        print("\n🔌 STEP 4: Testing IB Connection")
        print("-" * 40)
        
        print("Testing connection to IB Gateway...")
        print("Make sure IB Gateway is running with:")
        print(f"- Username: {self.ib_credentials['username']}")
        print("- Paper Trading Mode")
        print("- API enabled on port 7497")
        
        # Create test script
        test_script = self.project_root / 'test_ib_connection.py'
        test_code = '''#!/usr/bin/env python3
"""Test Interactive Brokers connection"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_ib_connection():
    """Test IB connection"""
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        
        config = {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1,
            'paper_trading': True,
            'account_id': 'DUN683505'
        }
        
        print("🔌 Connecting to Interactive Brokers...")
        broker = InteractiveBrokersBroker(config)
        
        connected = await broker.connect()
        
        if connected:
            print("[CHECK] Successfully connected to IB!")
            
            # Test account info
            try:
                account = await broker.get_account()
                print(f"📊 Account ID: {account.account_id}")
                print(f"💰 Portfolio Value: ${account.portfolio_value:,.2f}")
                print(f"💵 Cash: ${account.cash:,.2f}")
                print(f"🔥 Buying Power: ${account.buying_power:,.2f}")
            except Exception as e:
                print(f"[WARNING]️ Account info error: {e}")
            
            # Test market data
            try:
                market_data = await broker.get_market_data('AAPL')
                print(f"📈 AAPL Price: ${market_data['price']:.2f}")
                print(f"📊 Bid/Ask: ${market_data['bid']:.2f}/${market_data['ask']:.2f}")
            except Exception as e:
                print(f"[WARNING]️ Market data error: {e}")
            
            await broker.disconnect()
            print("[CHECK] IB connection test successful!")
            return True
            
        else:
            print("[ERROR] Failed to connect to IB")
            print("Make sure:")
            print("1. IB Gateway is running")
            print("2. You're logged in with paper trading account")
            print("3. API is enabled in IB Gateway settings")
            print("4. Port 7497 is available")
            return False
            
    except ImportError as e:
        print(f"[ERROR] IB API not available: {e}")
        print("Install with: pip install ibapi")
        return False
    except Exception as e:
        print(f"[ERROR] Connection test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_ib_connection())
'''
        
        with open(test_script, 'w') as f:
            f.write(test_code)
        
        print(f"[CHECK] Created test script: {test_script}")
        
        # Run test
        input("\nPress Enter to run connection test (make sure IB Gateway is running)...")
        
        try:
            result = subprocess.run([sys.executable, str(test_script)], 
                                  capture_output=True, text=True, timeout=30)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
        except subprocess.TimeoutExpired:
            print("[WARNING]️ Connection test timed out")
        except Exception as e:
            print(f"[ERROR] Test execution error: {e}")
    
    def _integrate_with_prometheus(self):
        """Integrate IB with PROMETHEUS"""
        print("\n🚀 STEP 5: PROMETHEUS Integration")
        print("-" * 40)
        
        # Create IB paper trading launcher
        launcher_script = self.project_root / 'start_ib_paper_trading.py'
        launcher_code = f'''#!/usr/bin/env python3
"""
Start PROMETHEUS with Interactive Brokers Paper Trading
Account: {self.ib_credentials['account_number']} (~$540 USD / R 10,000)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def start_ib_paper_trading():
    """Start PROMETHEUS with IB paper trading"""
    print("🏦 PROMETHEUS + INTERACTIVE BROKERS PAPER TRADING")
    print("=" * 60)
    print("Account: {self.ib_credentials['account_number']}")
    print("Starting Capital: $540 USD (R 10,000)")
    print("Trading Mode: Paper Trading with Real Market Data")
    print("=" * 60)
    
    # Set environment variables
    os.environ['IB_ENABLED'] = 'true'
    os.environ['IB_HOST'] = '127.0.0.1'
    os.environ['IB_PORT'] = '7497'
    os.environ['IB_CLIENT_ID'] = '1'
    os.environ['IB_PAPER_TRADING'] = 'true'
    os.environ['IB_ACCOUNT_ID'] = '{self.ib_credentials['account_number']}'
    os.environ['PRIMARY_BROKER'] = 'interactive_brokers'
    os.environ['STARTING_CAPITAL_USD'] = '540.0'
    os.environ['MAX_POSITION_SIZE_PERCENT'] = '2.0'
    os.environ['MAX_DAILY_LOSS_DOLLARS'] = '25.0'
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        from brokers.universal_broker_interface import BrokerManager
        
        # Initialize broker manager
        broker_manager = BrokerManager()
        
        # Setup IB broker
        ib_config = {{
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1,
            'paper_trading': True,
            'account_id': '{self.ib_credentials['account_number']}'
        }}
        
        ib_broker = InteractiveBrokersBroker(ib_config)
        broker_manager.register_broker('interactive_brokers', ib_broker, is_primary=True)
        
        # Connect to IB
        print("🔌 Connecting to Interactive Brokers...")
        connected = await ib_broker.connect()
        
        if connected:
            print("[CHECK] Connected to IB Paper Trading!")
            
            # Get account info
            account = await ib_broker.get_account()
            print(f"💰 Portfolio Value: ${{account.portfolio_value:,.2f}}")
            print(f"💵 Available Cash: ${{account.cash:,.2f}}")
            print(f"🔥 Buying Power: ${{account.buying_power:,.2f}}")
            
            print("\\n🚀 Ready for paper trading with real market data!")
            print("You can now:")
            print("1. Test market data feeds")
            print("2. Place paper trades")
            print("3. Monitor real-time performance")
            print("4. Validate strategies before going live")
            
            # Keep connection alive
            print("\\nPress Ctrl+C to stop...")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("\\n🛑 Stopping IB paper trading...")
                await ib_broker.disconnect()
                print("[CHECK] Disconnected from IB")
        else:
            print("[ERROR] Failed to connect to IB")
            print("Make sure IB Gateway is running and configured")
            
    except Exception as e:
        print(f"[ERROR] Error: {{e}}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(start_ib_paper_trading())
'''
        
        with open(launcher_script, 'w') as f:
            f.write(launcher_code)
        
        print(f"[CHECK] Created IB paper trading launcher: {launcher_script}")
        
        # Create requirements update
        requirements_ib = self.project_root / 'requirements-ib.txt'
        ib_requirements = """# Interactive Brokers Integration Requirements
ibapi>=9.81.1.post1
"""
        
        with open(requirements_ib, 'w') as f:
            f.write(ib_requirements)
        
        print(f"[CHECK] Created IB requirements: {requirements_ib}")
        print("Install with: pip install -r requirements-ib.txt")

def main():
    """Main setup function"""
    setup = InteractiveBrokersSetup()
    setup.run_setup()

if __name__ == "__main__":
    main()
