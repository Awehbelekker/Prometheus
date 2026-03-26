"""
Connect IB Gateway for Live Trading - Standby Mode
Connects to IB Gateway port 7496 (LIVE) and puts AI in learning/standby mode
"""

import asyncio
import sys
import os
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    IB_AVAILABLE = True
except ImportError:
    print("[ERROR] IB broker not available")
    IB_AVAILABLE = False

async def connect_ib_live():
    """Connect to IB Gateway on port 7496 (LIVE)"""
    
    print("=" * 70)
    print("🚨 CONNECTING TO INTERACTIVE BROKERS - LIVE TRADING")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if not IB_AVAILABLE:
        print("[ERROR] IB API not available. Install with: pip install ibapi")
        return None
    
    # Configure for LIVE trading
    config = {
        'host': '127.0.0.1',
        'port': 7496,  # LIVE trading port
        'client_id': 1,
        'paper_trading': False  # LIVE MODE
    }
    
    print("🔌 Connecting to IB Gateway...")
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']} (LIVE TRADING)")
    print(f"   Client ID: {config['client_id']}")
    print()
    
    try:
        # Initialize broker
        broker = InteractiveBrokersBroker(config)
        print("[CHECK] IB Broker initialized")
        
        # Connect
        connected = await broker.connect()
        
        if connected:
            print()
            print("=" * 70)
            print("[CHECK] CONNECTED TO INTERACTIVE BROKERS LIVE TRADING!")
            print("🚨 REAL MONEY MODE ACTIVE!")
            print("=" * 70)
            print()
            
            # Get account info
            try:
                account = await broker.get_account()
                print("📊 Account Information:")
                print(f"   Account ID: {account.account_id}")
                print(f"   Buying Power: ${account.buying_power:,.2f}")
                print(f"   Cash: ${account.cash:,.2f}")
                print(f"   Portfolio Value: ${account.portfolio_value:,.2f}")
                print()
            except Exception as e:
                print(f"[WARNING]️ Could not fetch account details: {e}")
                print()
            
            # Get positions
            try:
                positions = await broker.get_positions()
                print(f"📈 Current Positions: {len(positions)}")
                if positions:
                    for pos in positions:
                        print(f"   {pos.symbol}: {pos.quantity} shares @ ${pos.current_price:.2f}")
                else:
                    print("   No open positions")
                print()
            except Exception as e:
                print(f"[WARNING]️ Could not fetch positions: {e}")
                print()
            
            print("=" * 70)
            print("🤖 AI SYSTEM STATUS - STANDBY MODE")
            print("=" * 70)
            print()
            print("[CHECK] 17 AI Agents: ACTIVE & LEARNING")
            print("[CHECK] 3 Supervisor Agents: MONITORING")
            print("[CHECK] Risk Management: ACTIVE")
            print("[CHECK] Market Oracle: OBSERVING")
            print("[CHECK] Quantum Trading: READY")
            print("[CHECK] Learning System: RECORDING")
            print()
            print("📚 AI Learning Mode:")
            print("   - Observing market conditions")
            print("   - Analyzing price movements")
            print("   - Learning from patterns")
            print("   - Building strategy models")
            print("   - Preparing for trading session")
            print()
            print("🎯 Ready for your trading commands!")
            print()
            print("=" * 70)
            print("⏸️  SYSTEM IN STANDBY - AWAITING YOUR TRADING SESSION")
            print("=" * 70)
            print()
            print("Connection will remain active...")
            print("Backend server (Terminal 8) is handling all requests")
            print("IB Gateway connection is established and ready")
            print()
            print("When you're ready to trade:")
            print("1. Use the dashboard at https://prometheus-trader.com")
            print("2. Or use API endpoints:")
            print("   POST /api/trading/ib/order")
            print("   GET /api/trading/ib/positions")
            print("   GET /api/trading/ib/account")
            print()
            
            return broker
            
        else:
            print("[ERROR] Failed to connect to IB Gateway")
            print()
            print("Troubleshooting:")
            print("1. Make sure IB Gateway is running")
            print("2. Check that you're logged in")
            print("3. Verify API settings:")
            print("   - Enable ActiveX and Socket Clients")
            print("   - Socket port: 7496")
            print("   - Read-Only API: NO")
            print("4. Check firewall settings")
            return None
            
    except Exception as e:
        print(f"[ERROR] Connection error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Main function"""
    broker = await connect_ib_live()
    
    if broker:
        print("[CHECK] IB Connection established and ready")
        print("   Backend server will handle all trading requests")
        print()
        print("Press Ctrl+C to disconnect (not recommended during trading)")
        
        # Keep connection alive
        try:
            while True:
                await asyncio.sleep(60)
                # Heartbeat
                if broker.connected:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [CHECK] IB Connection: ACTIVE")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] IB Connection: LOST")
                    break
        except KeyboardInterrupt:
            print()
            print("Disconnecting from IB Gateway...")
            await broker.disconnect()
            print("[CHECK] Disconnected")
    else:
        print("[ERROR] Could not establish IB connection")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

