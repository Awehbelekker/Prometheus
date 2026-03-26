#!/usr/bin/env python
"""
🔍 PROMETHEUS BROKER CHECK - Check Alpaca and IB status
"""
import os
import socket
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def check_alpaca():
    """Check Alpaca account, positions, and orders"""
    print("="*70)
    print("📊 ALPACA BROKER STATUS")
    print("="*70)
    
    try:
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus
        
        client = TradingClient(
            os.getenv('ALPACA_API_KEY'),
            os.getenv('ALPACA_SECRET_KEY'),
            paper=False
        )
        
        # Account
        account = client.get_account()
        print(f"\n💰 ACCOUNT:")
        print(f"   Cash: ${float(account.cash):.2f}")
        print(f"   Buying Power: ${float(account.buying_power):.2f}")
        print(f"   Portfolio Value: ${float(account.portfolio_value):.2f}")
        print(f"   Day Trades: {account.daytrade_count}/3")
        
        # Open Orders
        print(f"\n📋 OPEN ORDERS:")
        open_orders = client.get_orders(filter=GetOrdersRequest(status=QueryOrderStatus.OPEN))
        if open_orders:
            buy_orders = [o for o in open_orders if o.side.name == 'BUY']
            sell_orders = [o for o in open_orders if o.side.name == 'SELL']
            print(f"   Total: {len(open_orders)} ({len(buy_orders)} BUY, {len(sell_orders)} SELL)")
            for o in open_orders:
                age_hours = (datetime.now(o.created_at.tzinfo) - o.created_at).total_seconds() / 3600
                print(f"   • {o.symbol}: {o.side.name} {o.qty} @ {o.type.name} ({age_hours:.1f}h old)")
        else:
            print("   No open orders")
        
        # Positions
        print(f"\n📈 POSITIONS:")
        positions = client.get_all_positions()
        if positions:
            total_value = sum(float(p.market_value) for p in positions)
            total_pnl = sum(float(p.unrealized_pl) for p in positions)
            print(f"   Total: {len(positions)} positions | Value: ${total_value:.2f} | P/L: ${total_pnl:.2f}")
            for p in positions:
                pnl_pct = float(p.unrealized_plpc) * 100
                emoji = "🟢" if pnl_pct >= 0 else "🔴"
                print(f"   {emoji} {p.symbol}: {p.qty} @ ${float(p.avg_entry_price):.4f} | {pnl_pct:+.2f}%")
        else:
            print("   No positions")
            
        return {'connected': True, 'orders': len(open_orders) if open_orders else 0}
        
    except Exception as e:
        print(f"❌ Alpaca Error: {e}")
        return {'connected': False, 'error': str(e)}


def check_ib():
    """Check Interactive Brokers connection"""
    print("\n" + "="*70)
    print("🏦 INTERACTIVE BROKERS STATUS")
    print("="*70)
    
    # Check port connectivity
    ib_ports = [
        (7496, "TWS Live"),
        (7497, "TWS Paper/Live"),
        (4001, "Gateway Paper"),
        (4002, "Gateway Live")
    ]
    
    print(f"\n🔌 PORT CHECK:")
    available_ports = []
    for port, desc in ib_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                print(f"   ✅ Port {port} ({desc}) - OPEN")
                available_ports.append(port)
            else:
                print(f"   ❌ Port {port} ({desc}) - CLOSED")
        except Exception as e:
            print(f"   ❌ Port {port} ({desc}) - ERROR: {e}")
    
    if not available_ports:
        print(f"\n⚠️  IB Gateway/TWS is NOT RUNNING!")
        print("   To enable IB trading:")
        print("   1. Start IB Gateway or TWS")
        print("   2. Enable API connections in settings")
        print("   3. Set port to 7497 (TWS) or 4001/4002 (Gateway)")
        return {'connected': False, 'reason': 'No ports accessible'}
    
    # Try to connect
    try:
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker, IB_AVAILABLE
        
        if not IB_AVAILABLE:
            print(f"\n⚠️  IB API not installed!")
            print("   Run: pip install ibapi")
            return {'connected': False, 'reason': 'ibapi not installed'}
        
        print(f"\n🔗 Attempting connection to port {available_ports[0]}...")
        # Note: Full connection test would require async context
        return {'connected': 'ports_available', 'ports': available_ports}
        
    except ImportError as e:
        print(f"\n⚠️  IB module import error: {e}")
        return {'connected': False, 'reason': str(e)}


def main():
    print("\n" + "🔷"*35)
    print("  PROMETHEUS BROKER STATUS CHECK")
    print("🔷"*35)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    alpaca_status = check_alpaca()
    ib_status = check_ib()
    
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    print(f"   Alpaca: {'✅ Connected' if alpaca_status.get('connected') else '❌ Disconnected'}")
    print(f"   IB: {'✅ Ports Available' if ib_status.get('ports') else '❌ Not Running'}")
    
    if alpaca_status.get('orders', 0) > 0:
        print(f"\n⚠️  {alpaca_status['orders']} open orders on Alpaca!")
        print("   Consider cancelling stale orders to free up buying power.")


if __name__ == "__main__":
    main()

