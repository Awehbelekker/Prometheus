#!/usr/bin/env python3
"""
Check Both Brokers - Positions and Account Analysis
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from ib_insync import IB, Stock
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def check_alpaca():
    """Check Alpaca positions and account"""
    print("\n" + "="*70)
    print("💼 ALPACA LIVE BROKER")
    print("="*70)
    
    client = TradingClient(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        paper=False
    )
    
    # Account info
    account = client.get_account()
    print(f"\n📊 ACCOUNT STATUS:")
    print(f"  Account: {account.account_number}")
    print(f"  Status: {account.status}")
    print(f"  Equity: ${float(account.equity):,.2f}")
    print(f"  Cash: ${float(account.cash):,.2f}")
    print(f"  Buying Power: ${float(account.buying_power):,.2f}")
    print(f"  Portfolio Value: ${float(account.portfolio_value):,.2f}")
    
    # Positions
    positions = client.get_all_positions()
    print(f"\n📈 CURRENT POSITIONS: {len(positions)}")
    
    total_pl = 0
    total_pl_pct = 0
    
    if positions:
        print(f"\n{'Symbol':<10} {'Qty':<10} {'Entry':<12} {'Current':<12} {'P&L $':<12} {'P&L %':<10} {'Value':<12}")
        print("-" * 80)
        
        for pos in positions:
            qty = float(pos.qty)
            entry = float(pos.avg_entry_price)
            current = float(pos.current_price)
            pl = float(pos.unrealized_pl)
            pl_pct = float(pos.unrealized_plpc) * 100
            value = qty * current
            
            total_pl += pl
            total_pl_pct += pl_pct
            
            status = "🟢" if pl > 0 else "🔴" if pl < 0 else "⚪"
            print(f"{status} {pos.symbol:<8} {qty:<10.4f} ${entry:<11.2f} ${current:<11.2f} ${pl:<11.2f} {pl_pct:<9.2f}% ${value:<11.2f}")
        
        avg_pl_pct = total_pl_pct / len(positions) if positions else 0
        print("-" * 80)
        print(f"{'TOTAL':<20} {'':>14} {'':>12} ${total_pl:>11.2f} {avg_pl_pct:>9.2f}%")
    else:
        print("  ✅ No positions - All cash available for trading")
    
    # Available buying power
    print(f"\n💰 TRADING CAPACITY:")
    print(f"  Available Cash: ${float(account.cash):,.2f}")
    print(f"  Buying Power: ${float(account.buying_power):,.2f}")
    print(f"  Max Position Size (3%): ${float(account.equity) * 0.03:,.2f}")
    
    return {
        'equity': float(account.equity),
        'cash': float(account.cash),
        'buying_power': float(account.buying_power),
        'positions': len(positions),
        'total_pl': total_pl
    }

def check_ib():
    """Check IB positions and account"""
    print("\n" + "="*70)
    print("💼 INTERACTIVE BROKERS (PAPER)")
    print("="*70)
    
    ib = IB()
    
    try:
        host = os.getenv('IB_HOST', '127.0.0.1')
        port = int(os.getenv('IB_PORT', '4002'))
        client_id = int(os.getenv('IB_CLIENT_ID', '9998'))
        
        ib.connect(host, port, clientId=client_id, timeout=10)
        
        if not ib.isConnected():
            print("❌ Failed to connect to IB")
            return None
        
        # Get account
        accounts = ib.managedAccounts()
        account = accounts[0] if accounts else None
        
        if not account:
            print("❌ No account found")
            return None
        
        # Account values
        account_values = ib.accountValues(account)
        
        equity = float(next((v.value for v in account_values if v.tag == 'NetLiquidation'), 0))
        cash = float(next((v.value for v in account_values if v.tag == 'TotalCashValue'), 0))
        buying_power = float(next((v.value for v in account_values if v.tag == 'BuyingPower'), 0))
        
        print(f"\n📊 ACCOUNT STATUS:")
        print(f"  Account: {account}")
        print(f"  Equity: ${equity:,.2f}")
        print(f"  Cash: ${cash:,.2f}")
        print(f"  Buying Power: ${buying_power:,.2f}")
        
        # Positions
        positions = ib.positions()
        print(f"\n📈 CURRENT POSITIONS: {len(positions)}")
        
        total_pl = 0
        
        if positions:
            print(f"\n{'Symbol':<10} {'Qty':<10} {'Entry':<12} {'Current':<12} {'P&L $':<12} {'P&L %':<10} {'Value':<12}")
            print("-" * 80)
            
            for pos in positions:
                symbol = pos.contract.symbol
                qty = pos.position
                entry = pos.avgCost
                
                # Get current price
                ticker = ib.reqMktData(pos.contract, '', False, False)
                ib.sleep(1)  # Wait for data
                
                current = ticker.marketPrice()
                if current == current:  # Check for NaN
                    value = qty * current
                    pl = (current - entry) * qty
                    pl_pct = ((current - entry) / entry * 100) if entry != 0 else 0
                    
                    total_pl += pl
                    
                    status = "🟢" if pl > 0 else "🔴" if pl < 0 else "⚪"
                    print(f"{status} {symbol:<8} {qty:<10.1f} ${entry:<11.2f} ${current:<11.2f} ${pl:<11.2f} {pl_pct:<9.2f}% ${value:<11.2f}")
                else:
                    print(f"⚪ {symbol:<8} {qty:<10.1f} ${entry:<11.2f} {'N/A':<11} {'N/A':<11} {'N/A':<9}")
                
                ib.cancelMktData(pos.contract)
            
            print("-" * 80)
            print(f"{'TOTAL':<20} {'':>14} {'':>12} ${total_pl:>11.2f}")
        else:
            print("  ✅ No positions - All cash available for trading")
        
        # Available buying power
        print(f"\n💰 TRADING CAPACITY:")
        print(f"  Available Cash: ${cash:,.2f}")
        print(f"  Buying Power: ${buying_power:,.2f}")
        print(f"  Max Position Size (3%): ${equity * 0.03:,.2f}")
        
        ib.disconnect()
        
        return {
            'equity': equity,
            'cash': cash,
            'buying_power': buying_power,
            'positions': len(positions),
            'total_pl': total_pl
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if ib.isConnected():
            ib.disconnect()
        return None

def analyze_recommendation(alpaca_data, ib_data):
    """Provide trading recommendation"""
    print("\n" + "="*70)
    print("📋 ANALYSIS & RECOMMENDATION")
    print("="*70)
    
    if not alpaca_data or not ib_data:
        print("❌ Unable to provide recommendation - missing data")
        return
    
    total_equity = alpaca_data['equity'] + ib_data['equity']
    total_cash = alpaca_data['cash'] + ib_data['cash']
    total_buying_power = alpaca_data['buying_power'] + ib_data['buying_power']
    
    print(f"\n💼 COMBINED ACCOUNT:")
    print(f"  Total Equity: ${total_equity:,.2f}")
    print(f"  Total Cash: ${total_cash:,.2f}")
    print(f"  Total Buying Power: ${total_buying_power:,.2f}")
    print(f"  Total Positions: {alpaca_data['positions'] + ib_data['positions']}")
    
    # IB analysis
    print(f"\n🔍 IB POSITION ANALYSIS:")
    ib_cash_pct = (ib_data['cash'] / ib_data['equity'] * 100) if ib_data['equity'] > 0 else 0
    ib_utilization = 100 - ib_cash_pct
    
    print(f"  Cash Available: ${ib_data['cash']:.2f} ({ib_cash_pct:.1f}%)")
    print(f"  Capital Utilized: {ib_utilization:.1f}%")
    print(f"  Buying Power: ${ib_data['buying_power']:.2f}")
    
    # Recommendation
    print(f"\n💡 RECOMMENDATION:")
    
    if ib_data['buying_power'] < 50:
        print(f"\n  ⚠️ IB BUYING POWER VERY LOW (${ib_data['buying_power']:.2f})")
        print(f"  🔴 SELL IB POSITION: YES")
        print(f"\n  REASONS:")
        print(f"    • Only ${ib_data['buying_power']:.2f} available - not enough for most trades")
        print(f"    • {ib_utilization:.1f}% of capital locked in position")
        print(f"    • Selling CRM would free up ~${ib_data['equity'] - ib_data['cash']:.2f}")
        print(f"    • This would increase buying power to ~${ib_data['equity']:.2f}")
        print(f"    • More flexibility for AI to enter high-quality trades")
        
        if ib_data['total_pl'] < 0:
            print(f"    • Position currently DOWN ${abs(ib_data['total_pl']):.2f}")
            print(f"    • Cutting loss allows capital redeployment")
        elif ib_data['total_pl'] > 0:
            print(f"    • Position currently UP ${ib_data['total_pl']:.2f}")
            print(f"    • Lock in profit and redeploy to better opportunities")
        
    elif ib_data['buying_power'] < 100:
        print(f"\n  ⚠️ IB BUYING POWER LOW (${ib_data['buying_power']:.2f})")
        print(f"  🟡 SELL IB POSITION: CONSIDER IT")
        print(f"\n  REASONS:")
        print(f"    • Buying power limited for multiple trades")
        print(f"    • Selling would improve trading flexibility")
        print(f"    • Alpaca has ${alpaca_data['buying_power']:.2f} - better distribution")
        
    else:
        print(f"\n  ✅ IB BUYING POWER ADEQUATE (${ib_data['buying_power']:.2f})")
        print(f"  🟢 SELL IB POSITION: NO")
        print(f"\n  REASONS:")
        print(f"    • Sufficient buying power for trading")
        print(f"    • Position can stay unless AI signals better opportunity")
    
    # Alpaca analysis
    print(f"\n🔍 ALPACA ANALYSIS:")
    if alpaca_data['positions'] > 0:
        print(f"  Positions: {alpaca_data['positions']}")
        print(f"  P&L: ${alpaca_data['total_pl']:.2f}")
        if alpaca_data['total_pl'] < -20:
            print(f"  ⚠️ Losing positions - Consider exits")
    
    print(f"\n📊 TRADING STRATEGY:")
    print(f"  • AI targets 8 trades/day across both brokers")
    print(f"  • Need ~${total_equity * 0.03:.2f} per position (3% risk)")
    print(f"  • Current buying power: ${total_buying_power:.2f}")
    print(f"  • Can open ~{int(total_buying_power / (total_equity * 0.03))} positions")
    
    if ib_data['buying_power'] < 50:
        print(f"\n🎯 ACTION ITEM:")
        print(f"  1. Sell CRM position on IB")
        print(f"  2. This frees up ~${ib_data['equity'] - ib_data['cash']:.2f}")
        print(f"  3. Increases IB buying power for AI trading")
        print(f"  4. Better capital utilization across both brokers")

def main():
    print("\n" + "="*70)
    print("  🔍 DUAL BROKER POSITION ANALYSIS")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*70)
    
    alpaca_data = check_alpaca()
    ib_data = check_ib()
    
    if alpaca_data and ib_data:
        analyze_recommendation(alpaca_data, ib_data)
    
    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
