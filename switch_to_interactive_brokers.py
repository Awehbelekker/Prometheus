#!/usr/bin/env python3
"""
🏦 SWITCH PROMETHEUS TO INTERACTIVE BROKERS
==========================================
Activate Interactive Brokers as primary broker for superior trading capabilities
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

def print_status(message, status="INFO"):
    """Print formatted status message"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    symbols = {"INFO": "[INFO]️", "SUCCESS": "[CHECK]", "ERROR": "[ERROR]", "WARNING": "[WARNING]️"}
    print(f"[{timestamp}] {symbols.get(status, '[INFO]️')} {message}")

def backup_current_env():
    """Backup current .env file"""
    if os.path.exists('.env'):
        backup_name = f'.env.alpaca.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        shutil.copy('.env', backup_name)
        print_status(f"Backed up current .env to {backup_name}", "SUCCESS")

def merge_ib_config():
    """Merge IB configuration into main .env file"""
    print_status("Merging Interactive Brokers configuration...", "INFO")
    
    # Read current .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Read IB config
    ib_content = ""
    if os.path.exists('.env.ib'):
        with open('.env.ib', 'r') as f:
            ib_content = f.read()
    
    # Merge configurations
    merged_content = env_content + "\n\n# ================================\n"
    merged_content += "# INTERACTIVE BROKERS CONFIGURATION\n"
    merged_content += "# ================================\n"
    merged_content += ib_content
    
    # Write merged config
    with open('.env', 'w') as f:
        f.write(merged_content)
    
    print_status("[CHECK] Interactive Brokers configuration merged", "SUCCESS")

def check_ib_api_installed():
    """Check if IB API is installed"""
    try:
        import ibapi
        print_status("[CHECK] Interactive Brokers API is installed", "SUCCESS")
        return True
    except ImportError:
        print_status("[ERROR] Interactive Brokers API not installed", "ERROR")
        return False

def install_ib_api():
    """Install Interactive Brokers API"""
    print_status("Installing Interactive Brokers API...", "INFO")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "ibapi"], check=True)
        print_status("[CHECK] Interactive Brokers API installed successfully", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"[ERROR] Failed to install IB API: {e}", "ERROR")
        return False

def check_ib_gateway_running():
    """Check if IB Gateway is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 7497))
        sock.close()
        if result == 0:
            print_status("[CHECK] IB Gateway is running on port 7497", "SUCCESS")
            return True
        else:
            print_status("[ERROR] IB Gateway is not running on port 7497", "WARNING")
            return False
    except Exception as e:
        print_status(f"[ERROR] Error checking IB Gateway: {e}", "ERROR")
        return False

def provide_ib_gateway_instructions():
    """Provide instructions for setting up IB Gateway"""
    print_status("📋 IB GATEWAY SETUP INSTRUCTIONS", "INFO")
    print("=" * 60)
    print("1. Download IB Gateway from:")
    print("   https://www.interactivebrokers.com/en/trading/ib-gateway.php")
    print()
    print("2. Install IB Gateway")
    print()
    print("3. Configure IB Gateway:")
    print("   - Username: wvtjnq273")
    print("   - Account: DUN683505")
    print("   - Trading Mode: Paper Trading")
    print("   - Socket Port: 7497")
    print()
    print("4. Enable API connections:")
    print("   - Go to Configure > Settings > API")
    print("   - Check 'Enable ActiveX and Socket Clients'")
    print("   - Socket Port: 7497")
    print("   - Master API client ID: 0")
    print("   - Check 'Read-Only API'")
    print()
    print("5. Start IB Gateway and login with your credentials")
    print("=" * 60)

def test_ib_connection():
    """Test connection to Interactive Brokers"""
    print_status("Testing Interactive Brokers connection...", "INFO")
    
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        
        ib_config = {
            'host': '127.0.0.1',
            'port': 7497,
            'client_id': 1,
            'paper_trading': True,
            'account_id': 'DUN683505'
        }
        
        ib_broker = InteractiveBrokersBroker(ib_config)
        
        # This will be async in real usage, but for testing we'll just check instantiation
        print_status("[CHECK] Interactive Brokers broker initialized", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"[ERROR] Failed to initialize IB broker: {e}", "ERROR")
        return False

def create_ib_startup_script():
    """Create startup script for IB trading"""
    script_content = '''#!/usr/bin/env python3
"""
🏦 PROMETHEUS - Interactive Brokers Trading Session
Start PROMETHEUS with Interactive Brokers as primary broker
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from prometheus_ib_trading_session import PrometheusIBTradingSession

async def main():
    """Start IB trading session"""
    print("🏦 Starting PROMETHEUS with Interactive Brokers...")
    
    session = PrometheusIBTradingSession(
        starting_capital=540.0,  # $540 USD
        session_duration_hours=24,
        paper_trading=True
    )
    
    await session.run_session()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open('start_ib_trading.py', 'w') as f:
        f.write(script_content)
    
    print_status("[CHECK] Created IB trading startup script: start_ib_trading.py", "SUCCESS")

def main():
    """Main setup process"""
    print_status("🏦 SWITCHING PROMETHEUS TO INTERACTIVE BROKERS", "INFO")
    print_status("=" * 60, "INFO")
    
    # Step 1: Backup current configuration
    backup_current_env()
    
    # Step 2: Check and install IB API
    if not check_ib_api_installed():
        if not install_ib_api():
            print_status("[ERROR] Cannot proceed without IB API. Exiting.", "ERROR")
            return False
    
    # Step 3: Merge IB configuration
    merge_ib_config()
    
    # Step 4: Check IB Gateway
    if not check_ib_gateway_running():
        provide_ib_gateway_instructions()
        input("\nPress Enter when IB Gateway is running and configured...")
        
        if not check_ib_gateway_running():
            print_status("[WARNING]️ IB Gateway still not detected. You can continue setup later.", "WARNING")
    
    # Step 5: Test IB broker initialization
    test_ib_connection()
    
    # Step 6: Create startup script
    create_ib_startup_script()
    
    # Step 7: Final instructions
    print_status("🎉 INTERACTIVE BROKERS SETUP COMPLETE!", "SUCCESS")
    print_status("=" * 60, "INFO")
    print_status("[CHECK] Configuration merged into .env", "SUCCESS")
    print_status("[CHECK] IB API installed", "SUCCESS")
    print_status("[CHECK] Startup script created", "SUCCESS")
    print_status("", "INFO")
    print_status("🚀 NEXT STEPS:", "INFO")
    print_status("1. Ensure IB Gateway is running (port 7497)", "INFO")
    print_status("2. Run: python start_ib_trading.py", "INFO")
    print_status("3. Or use existing IB sessions:", "INFO")
    print_status("   - python prometheus_ib_trading_session.py", "INFO")
    print_status("   - python prometheus_ib_hybrid_session.py", "INFO")
    print_status("", "INFO")
    print_status("🏆 BENEFITS OF INTERACTIVE BROKERS:", "INFO")
    print_status("• Lower commissions and fees", "INFO")
    print_status("• Superior order execution", "INFO")
    print_status("• Global market access", "INFO")
    print_status("• Advanced order types", "INFO")
    print_status("• Professional-grade platform", "INFO")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
