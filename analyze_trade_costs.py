#!/usr/bin/env python3
"""
Analyze Alpaca Trade Costs and Performance
"""
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import sqlite3

def analyze_costs():
    """Analyze trade costs and performance"""
    
    print("\n" + "=" * 80)
    print("💰 ALPACA TRADE COST ANALYSIS")
    print("=" * 80)
    
    # Load environment
    load_dotenv()
    
    # Connect to Alpaca LIVE
    api_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET')
    
    api = tradeapi.REST(
        api_key,
        secret_key,
        base_url='https://api.alpaca.markets'
    )
    
    # Get account info
    account = api.get_account()
    
    print(f"\n📊 ACCOUNT SUMMARY:")
    print(f"   Starting Capital (estimated): $70.00")
    print(f"   Current Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"   Current Cash: ${float(account.cash):,.2f}")
    print(f"   Open Position Value: ${float(account.portfolio_value) - float(account.cash):,.2f}")
    
    # Calculate total P&L
    starting_capital = 70.00  # Approximate starting point
    current_value = float(account.portfolio_value)
    total_pnl = current_value - starting_capital
    total_pnl_pct = (total_pnl / starting_capital) * 100
    
    print(f"\n💵 PERFORMANCE:")
    print(f"   Total P&L: ${total_pnl:,.2f}")
    print(f"   Total Return: {total_pnl_pct:.2f}%")
    
    # Get recent activities (includes fills and fees)
    try:
        # Get activities from last 24 hours
        activities = api.get_activities(activity_types='FILL', date=datetime.now().date())
        
        print(f"\n📋 RECENT FILLS (Last 24 Hours):")
        print(f"{'Time':<20} {'Symbol':<10} {'Side':<6} {'Qty':<12} {'Price':<12} {'Value':<12}")
        print("-" * 80)
        
        total_buy_value = 0
        total_sell_value = 0
        trade_count = 0
        
        for activity in activities[:20]:  # Last 20 fills
            timestamp = activity.transaction_time.strftime('%Y-%m-%d %H:%M:%S')
            symbol = activity.symbol
            side = activity.side
            qty = float(activity.qty)
            price = float(activity.price)
            value = qty * price
            
            print(f"{timestamp:<20} {symbol:<10} {side:<6} {qty:<12.6f} ${price:<11.2f} ${value:<11.2f}")
            
            if side == 'buy':
                total_buy_value += value
            else:
                total_sell_value += value
            
            trade_count += 1
        
        print("-" * 80)
        print(f"Total Trades: {trade_count}")
        print(f"Total Buy Value: ${total_buy_value:.2f}")
        print(f"Total Sell Value: ${total_sell_value:.2f}")
        print(f"Net Trading: ${total_sell_value - total_buy_value:.2f}")
        
    except Exception as e:
        print(f"[WARNING]️ Could not fetch activities: {e}")
    
    # Analyze current positions
    positions = api.list_positions()
    
    print(f"\n📈 CURRENT POSITIONS ANALYSIS:")
    print(f"{'Symbol':<10} {'Qty':<12} {'Entry':<12} {'Current':<12} {'P&L':<12} {'P&L %':<10}")
    print("-" * 80)
    
    total_unrealized_pl = 0
    total_position_value = 0
    
    for position in positions:
        symbol = position.symbol
        qty = float(position.qty)
        entry_price = float(position.avg_entry_price)
        current_price = float(position.current_price)
        unrealized_pl = float(position.unrealized_pl)
        unrealized_plpc = float(position.unrealized_plpc) * 100
        position_value = qty * current_price
        
        print(f"{symbol:<10} {qty:<12.6f} ${entry_price:<11.2f} ${current_price:<11.2f} ${unrealized_pl:<11.2f} {unrealized_plpc:<9.2f}%")
        
        total_unrealized_pl += unrealized_pl
        total_position_value += position_value
    
    print("-" * 80)
    print(f"Total Position Value: ${total_position_value:.2f}")
    print(f"Total Unrealized P&L: ${total_unrealized_pl:.2f}")
    
    # COST ANALYSIS
    print(f"\n💸 COST ANALYSIS:")
    print(f"\n📌 Alpaca Crypto Trading Costs:")
    print(f"   Maker Fee: 0.25% (when adding liquidity)")
    print(f"   Taker Fee: 0.25% (when removing liquidity)")
    print(f"   Typical Fee per Trade: 0.25% of trade value")
    
    # Estimate fees based on trading volume
    estimated_total_volume = total_buy_value + abs(total_sell_value)
    estimated_fees = estimated_total_volume * 0.0025  # 0.25% fee
    
    print(f"\n💰 ESTIMATED FEES:")
    print(f"   Total Trading Volume: ${estimated_total_volume:.2f}")
    print(f"   Estimated Fees (0.25%): ${estimated_fees:.2f}")
    
    # Adjusted P&L
    adjusted_pnl = total_pnl - estimated_fees
    adjusted_pnl_pct = (adjusted_pnl / starting_capital) * 100
    
    print(f"\n📊 ADJUSTED PERFORMANCE (After Fees):")
    print(f"   Gross P&L: ${total_pnl:.2f}")
    print(f"   Estimated Fees: -${estimated_fees:.2f}")
    print(f"   Net P&L: ${adjusted_pnl:.2f}")
    print(f"   Net Return: {adjusted_pnl_pct:.2f}%")
    
    # Check learning database
    try:
        conn = sqlite3.connect('prometheus_learning.db')
        cursor = conn.cursor()
        
        # Get trade count from database
        cursor.execute("""
            SELECT COUNT(*), 
                   SUM(CASE WHEN action = 'BUY' THEN 1 ELSE 0 END) as buys,
                   SUM(CASE WHEN action = 'SELL' THEN 1 ELSE 0 END) as sells
            FROM trade_history 
            WHERE timestamp > datetime('now', '-24 hours')
        """)
        
        row = cursor.fetchone()
        if row:
            total_trades = row[0]
            buys = row[1] or 0
            sells = row[2] or 0
            
            print(f"\n📊 TRADING ACTIVITY (Last 24 Hours):")
            print(f"   Total Trades: {total_trades}")
            print(f"   Buy Orders: {buys}")
            print(f"   Sell Orders: {sells}")
            print(f"   Avg Trades/Hour: {total_trades / 24:.1f}")
        
        conn.close()
    except Exception as e:
        print(f"[WARNING]️ Could not read learning database: {e}")
    
    # RECOMMENDATIONS
    print(f"\n💡 ANALYSIS & RECOMMENDATIONS:")
    
    if total_pnl < 0:
        print(f"\n[WARNING]️ CURRENT STATUS: LOSING MONEY")
        print(f"   Current Loss: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)")
        print(f"   Estimated Fees: ${estimated_fees:.2f}")
        print(f"   Net Loss: ${adjusted_pnl:.2f}")
        
        print(f"\n🔍 POSSIBLE CAUSES:")
        print(f"   1. Trading fees eating into small profits")
        print(f"   2. Position sizes too small ($1.17 per trade)")
        print(f"   3. Too many trades (churning)")
        print(f"   4. Market conditions unfavorable")
        print(f"   5. Entry/exit timing needs improvement")
        
        print(f"\n[CHECK] RECOMMENDATIONS:")
        print(f"   1. [CHECK] Already limited to 3 trades/hour (good!)")
        print(f"   2. [CHECK] Already using 80%+ confidence (good!)")
        print(f"   3. Consider: Hold positions longer to reduce fees")
        print(f"   4. Consider: Increase position size when capital grows")
        print(f"   5. Monitor: Win rate and average profit per trade")
        
    else:
        print(f"\n[CHECK] CURRENT STATUS: PROFITABLE")
        print(f"   Current Profit: ${total_pnl:.2f} ({total_pnl_pct:.2f}%)")
        print(f"   Keep current strategy!")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    analyze_costs()

