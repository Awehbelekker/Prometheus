#!/usr/bin/env python3
"""
CORRECTED DIAGNOSTIC - Uses actual port 4002 and loads .env file
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Load .env file
from dotenv import load_dotenv
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    from brokers.alpaca_broker import AlpacaBroker
    import yfinance as yf
except ImportError as e:
    print(f"Error: {e}")
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv"])
    sys.exit(1)


async def check_all_systems():
    """Check all systems with CORRECT configuration"""
    print("=" * 80)
    print("  🔍 CORRECTED PROMETHEUS DIAGNOSTICS (Port 4002, .env loaded)")
    print("=" * 80)
    print()
    
    # Check environment
    print("📋 ENVIRONMENT VARIABLES:")
    print("-" * 80)
    alpaca_key = os.getenv('ALPACA_API_KEY')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY')
    ib_port = os.getenv('IB_PORT', '4002')
    ib_account = os.getenv('IB_ACCOUNT', 'U21922116')
    
    print(f"ALPACA_API_KEY: {'✅ SET (...' + alpaca_key[-4:] + ')' if alpaca_key else '❌ MISSING'}")
    print(f"ALPACA_SECRET_KEY: {'✅ SET (...' + alpaca_secret[-4:] + ')' if alpaca_secret else '❌ MISSING'}")
    print(f"IB_PORT: ✅ {ib_port}")
    print(f"IB_ACCOUNT: ✅ {ib_account}")
    print()
    
    # Test Alpaca
    print("=" * 80)
    print("  📊 ALPACA BROKER TEST")
    print("=" * 80)
    print()
    
    if alpaca_key and alpaca_secret:
        try:
            print("🔄 Connecting to Alpaca...")
            config = {
                'api_key': alpaca_key,
                'secret_key': alpaca_secret,
                'paper_trading': False  # Using LIVE keys from .env
            }
            broker = AlpacaBroker(config)
            connected = await broker.connect()
            
            if connected:
                print("✅ Alpaca: CONNECTED")
                account = await broker.get_account()
                print(f"   Account: {account.account_id}")
                print(f"   Equity: ${account.equity:.2f}")
                print(f"   Buying Power: ${account.buying_power:.2f}")
                print(f"   Cash: ${account.cash:.2f}")
                print()
                
                # Check positions
                positions = await broker.get_positions()
                print(f"📈 Alpaca Positions: {len(positions)}")
                if positions:
                    for pos in positions:
                        pnl_style = "+" if pos.unrealized_pnl > 0 else ""
                        print(f"   • {pos.symbol}: {pos.quantity} @ ${pos.avg_price:.2f}")
                        print(f"     Value: ${pos.market_value:.2f} | P&L: {pnl_style}${pos.unrealized_pnl:.2f} ({pnl_style}{pos.unrealized_pnl_percent*100:.2f}%)")
                else:
                    print("   No positions")
                
                await broker.disconnect()
            else:
                print("❌ Alpaca: CONNECTION FAILED")
        except Exception as e:
            print(f"❌ Alpaca Error: {e}")
    else:
        print("⚠️  Skipping Alpaca test - API keys not found in .env")
    
    print()
    
    # Test IB
    print("=" * 80)
    print("  📈 INTERACTIVE BROKERS TEST (Port 4002)")
    print("=" * 80)
    print()
    
    try:
        print(f"🔄 Connecting to IB on port {ib_port}...")
        config = {
            'account_id': ib_account,
            'host': '127.0.0.1',
            'port': int(ib_port),
            'client_id': 7780
        }
        broker = InteractiveBrokersBroker(config)
        connected = await broker.connect()
        
        if connected:
            print("✅ IB: CONNECTED")
            print(f"   Account: {ib_account}")
            print()
            print("⏳ Waiting for account data (3 seconds)...")
            await asyncio.sleep(3)
            
            # Account data
            if hasattr(broker, 'account_data') and broker.account_data:
                print()
                print("💰 Account Summary:")
                for tag, value in broker.account_data.items():
                    if tag in ['TotalCashValue', 'NetLiquidation', 'AvailableFunds', 'BuyingPower', 'GrossPositionValue']:
                        print(f"   {tag}: {value}")
            
            # Positions
            if hasattr(broker, 'positions_data') and broker.positions_data:
                print()
                print(f"📈 IB Positions: {len(broker.positions_data)}")
                for symbol, pos_data in broker.positions_data.items():
                    qty = pos_data.get('quantity', 0)
                    avg_price = pos_data.get('avg_price', 0)
                    
                    print()
                    print(f"   🎯 {symbol}")
                    print(f"      Quantity: {qty}")
                    print(f"      Avg Cost: ${avg_price:.2f}")
                    print(f"      Value: ${qty * avg_price:.2f}")
                    
                    # Get current price
                    try:
                        ticker = yf.Ticker(symbol)
                        current_price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
                        if current_price:
                            pnl = (current_price - avg_price) * qty
                            pnl_pct = (pnl / (avg_price * qty) * 100) if avg_price > 0 else 0
                            status = "✅ PROFIT" if pnl > 0 else "⚠️ LOSS" if pnl < 0 else "⚪ FLAT"
                            print(f"      Current: ${current_price:.2f}")
                            print(f"      P&L: ${pnl:+.2f} ({pnl_pct:+.2f}%) {status}")
                    except:
                        pass
            else:
                print()
                print("📈 IB Positions: No positions found")
            
            await broker.disconnect()
        else:
            print("❌ IB: CONNECTION FAILED")
            print()
            print("TROUBLESHOOTING:")
            print(f"1. Is IB Gateway/TWS running on port {ib_port}?")
            print("2. Is API enabled in Global Configuration?")
            print("3. Is 'Read-Only API' UNCHECKED?")
            print("4. Try: Test-NetConnection -ComputerName localhost -Port " + ib_port)
    except Exception as e:
        print(f"❌ IB Error: {e}")
    
    print()
    print("=" * 80)
    print(f"  Diagnostic completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(check_all_systems())
