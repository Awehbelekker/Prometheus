"""
Quick status check for Prometheus - Run this anytime to see what's happening
"""
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def check_status():
    print("\n" + "="*70)
    print(f"PROMETHEUS STATUS CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Check Alpaca
    print("\n[1/3] ALPACA STATUS...")
    try:
        from brokers.alpaca_broker import AlpacaBroker
        alpaca = AlpacaBroker({
            'api_key': os.getenv('ALPACA_API_KEY'),
            'secret_key': os.getenv('ALPACA_SECRET_KEY'),
            'paper_trading': False
        })
        if await alpaca.connect():
            account = await alpaca.get_account()
            positions = await alpaca.get_positions()
            
            equity = float(account.equity)
            cash = float(account.cash)
            
            print(f"  [OK] Connected")
            print(f"       Equity: ${equity:,.2f}")
            print(f"       Cash: ${cash:,.2f}")
            print(f"       Open Positions: {len(positions)}")
            
            if positions:
                print(f"\n       Current Positions:")
                for pos in positions:
                    pnl = float(pos.unrealized_pl)
                    pnl_pct = float(pos.unrealized_plpc) * 100
                    symbol_str = f"{pos.symbol}"
                    qty_str = f"{float(pos.qty)}"
                    side_str = f"{pos.side.upper()}"
                    pnl_str = f"${pnl:+.2f}" if pnl >= 0 else f"${pnl:.2f}"
                    pnl_pct_str = f"({pnl_pct:+.2f}%)"
                    
                    print(f"       - {symbol_str} {qty_str} {side_str} {pnl_str} {pnl_pct_str}")
            
            await alpaca.disconnect()
        else:
            print(f"  [ERROR] Failed to connect")
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # Check IB
    print("\n[2/3] IB TWS STATUS...")
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print(f"  [SKIP] IB library not installed")
        else:
            ib = InteractiveBrokersBroker({
                'host': '127.0.0.1',
                'port': int(os.getenv('IB_PORT', '4002')),
                'client_id': 2,
                'account_id': 'U21922116',
                'paper_trading': False
            })
            
            if await asyncio.wait_for(ib.connect(), timeout=5.0):
                account = await ib.get_account()
                
                equity = float(account.equity)
                cash = float(account.cash)
                
                print(f"  [OK] Connected")
                print(f"       Equity: ${equity:,.2f}")
                print(f"       Cash: ${cash:,.2f}")
                
                await ib.disconnect()
            else:
                print(f"  [SKIP] IB not connected (optional)")
    except asyncio.TimeoutError:
        print(f"  [SKIP] IB timeout (optional)")
    except Exception as e:
        print(f"  [SKIP] IB error: {e}")
    
    # Check log files
    print("\n[3/3] RECENT ACTIVITY...")
    try:
        if os.path.exists('prometheus.log'):
            with open('prometheus.log', 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                recent = lines[-10:] if len(lines) > 10 else lines
                
                print(f"  Last 10 log entries:")
                for line in recent:
                    if 'INFO' in line or 'WARNING' in line or 'ERROR' in line:
                        print(f"  {line.strip()[:65]}")
        else:
            print(f"  [INFO] No log file yet (system just started)")
    except Exception as e:
        print(f"  [INFO] Could not read logs: {e}")
    
    print("\n" + "="*70)
    print("STATUS CHECK COMPLETE")
    print("="*70)
    print("\nTo stop trading: Press Ctrl+C in the Prometheus window")
    print("To restart: Double-click LAUNCH_PROMETHEUS.bat")

if __name__ == "__main__":
    asyncio.run(check_status())
