#!/usr/bin/env python3
"""
Complete System Statistics Report
"""
import os
from dotenv import load_dotenv
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import sqlite3

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def main():
    print_header("🚀 PROMETHEUS COMPLETE SYSTEM STATISTICS")
    
    # Load environment
    load_dotenv()
    
    # ========== ALPACA ACCOUNT ==========
    print_header("💰 ALPACA ACCOUNT (Crypto 24/7)")
    
    api_key = os.getenv('ALPACA_API_KEY') or os.getenv('ALPACA_LIVE_KEY')
    secret_key = os.getenv('ALPACA_SECRET_KEY') or os.getenv('ALPACA_LIVE_SECRET')
    
    api = tradeapi.REST(api_key, secret_key, base_url='https://api.alpaca.markets')
    account = api.get_account()
    
    starting_capital = 70.00
    current_value = float(account.portfolio_value)
    cash = float(account.cash)
    position_value = current_value - cash
    total_pnl = current_value - starting_capital
    total_pnl_pct = (total_pnl / starting_capital) * 100
    
    print(f"\n📊 Account Overview:")
    print(f"   Account: 910544927")
    print(f"   Status: {account.status}")
    print(f"   Starting Capital: ${starting_capital:,.2f}")
    print(f"   Current Value: ${current_value:,.2f}")
    print(f"   Cash Available: ${cash:,.2f}")
    print(f"   Position Value: ${position_value:,.2f}")
    print(f"   Total P&L: ${total_pnl:,.2f} ({total_pnl_pct:+.2f}%)")
    
    # Positions
    positions = api.list_positions()
    print(f"\n📈 Open Positions: {len(positions)}")
    
    total_unrealized_pl = 0
    for pos in positions:
        symbol = pos.symbol
        qty = float(pos.qty)
        entry = float(pos.avg_entry_price)
        current = float(pos.current_price)
        pl = float(pos.unrealized_pl)
        pl_pct = float(pos.unrealized_plpc) * 100
        
        print(f"   {symbol:<10} {qty:>10.6f} @ ${entry:>8.2f} → ${current:>8.2f} | ${pl:>+7.2f} ({pl_pct:>+6.2f}%)")
        total_unrealized_pl += pl
    
    if positions:
        print(f"   {'─' * 75}")
        print(f"   {'TOTAL':<10} {'':<10} {'':<10} {'':<10} | ${total_unrealized_pl:>+7.2f}")
    
    # ========== TRADING ACTIVITY ==========
    print_header("📊 TRADING ACTIVITY")
    
    conn = sqlite3.connect('prometheus_learning.db')
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM trade_history')
    row = cursor.fetchone()
    first_trade = row[0]
    last_trade = row[1]
    total_trades = row[2]
    
    print(f"\n📈 Overall Statistics:")
    print(f"   First Trade: {first_trade}")
    print(f"   Last Trade: {last_trade}")
    print(f"   Total Trades: {total_trades}")
    
    # Recovery mode stats (since 07:00 AM today)
    recovery_start = "2025-10-15 07:00:00"
    cursor.execute(f'SELECT COUNT(*) FROM trade_history WHERE timestamp > "{recovery_start}"')
    recovery_trades = cursor.fetchone()[0]
    
    # Calculate hours since recovery mode
    recovery_dt = datetime.strptime(recovery_start, "%Y-%m-%d %H:%M:%S")
    hours_since_recovery = (datetime.now() - recovery_dt).total_seconds() / 3600
    avg_trades_per_hour = recovery_trades / hours_since_recovery if hours_since_recovery > 0 else 0
    
    print(f"\n🔄 Recovery Mode (Since 07:00 AM):")
    print(f"   Duration: {hours_since_recovery:.1f} hours")
    print(f"   Trades: {recovery_trades}")
    print(f"   Avg Trades/Hour: {avg_trades_per_hour:.1f}")
    print(f"   Target: 3 trades/hour")
    print(f"   Status: {'[CHECK] ON TARGET' if avg_trades_per_hour <= 3.5 else '[WARNING]️ OVER LIMIT'}")
    
    # Hourly breakdown
    cursor.execute('''
        SELECT strftime('%H', timestamp) as hour, COUNT(*) as count
        FROM trade_history 
        WHERE date(timestamp) = date('now')
        GROUP BY hour
        ORDER BY hour DESC
        LIMIT 15
    ''')
    
    print(f"\n⏰ Hourly Breakdown (Today):")
    print(f"   Hour  | Trades | Status")
    print(f"   ------|--------|--------")
    
    for row in cursor.fetchall():
        hour = row[0]
        count = row[1]
        status = "[CHECK]" if count <= 3 else "[WARNING]️"
        print(f"   {hour}:00 | {count:>6} | {status}")
    
    # Recent trades
    cursor.execute('''
        SELECT timestamp, symbol, action, price, quantity
        FROM trade_history
        WHERE timestamp > datetime('now', '-2 hours')
        ORDER BY timestamp DESC
        LIMIT 10
    ''')

    print(f"\n📋 Recent Trades (Last 2 Hours):")
    print(f"   Time       | Symbol    | Action | Price      | Qty")
    print(f"   -----------|-----------|--------|------------|------------")

    for row in cursor.fetchall():
        timestamp = row[0][11:19]  # Extract time only
        symbol = row[1]
        action = row[2]
        price = float(row[3])
        qty = float(row[4])

        print(f"   {timestamp} | {symbol:<9} | {action:<6} | ${price:>9.2f} | {qty:>10.6f}")
    
    # Win rate analysis
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN action = 'BUY' THEN 1 ELSE 0 END) as buys,
            SUM(CASE WHEN action = 'SELL' THEN 1 ELSE 0 END) as sells
        FROM trade_history 
        WHERE timestamp > datetime('now', '-24 hours')
    ''')
    
    row = cursor.fetchone()
    total_24h = row[0]
    buys_24h = row[1] or 0
    sells_24h = row[2] or 0
    
    print(f"\n📊 24-Hour Trading Summary:")
    print(f"   Total Trades: {total_24h}")
    print(f"   Buy Orders: {buys_24h}")
    print(f"   Sell Orders: {sells_24h}")
    print(f"   Balance: {abs(buys_24h - sells_24h)} {'buys' if buys_24h > sells_24h else 'sells'} ahead")
    
    conn.close()
    
    # ========== COST ANALYSIS ==========
    print_header("💸 COST ANALYSIS")
    
    # Estimate trading costs
    estimated_volume_per_trade = 1.25  # Current position size
    trades_since_recovery = recovery_trades
    total_volume = trades_since_recovery * estimated_volume_per_trade
    alpaca_fee_rate = 0.0025  # 0.25%
    estimated_fees = total_volume * alpaca_fee_rate
    
    print(f"\n💰 Fee Estimates (Recovery Mode):")
    print(f"   Trades: {trades_since_recovery}")
    print(f"   Avg Trade Size: ${estimated_volume_per_trade:.2f}")
    print(f"   Total Volume: ${total_volume:.2f}")
    print(f"   Fee Rate: {alpaca_fee_rate * 100}%")
    print(f"   Estimated Fees: ${estimated_fees:.2f}")
    
    # Adjusted performance
    adjusted_pnl = total_pnl - estimated_fees
    adjusted_pnl_pct = (adjusted_pnl / starting_capital) * 100
    
    print(f"\n📊 Adjusted Performance:")
    print(f"   Gross P&L: ${total_pnl:,.2f}")
    print(f"   Est. Fees: -${estimated_fees:.2f}")
    print(f"   Net P&L: ${adjusted_pnl:,.2f}")
    print(f"   Net Return: {adjusted_pnl_pct:+.2f}%")
    
    # ========== TARGETS & PROGRESS ==========
    print_header("🎯 TARGETS & PROGRESS")
    
    daily_target_low = starting_capital * 1.06  # 6%
    daily_target_high = starting_capital * 1.09  # 9%
    weekly_target_low = starting_capital * 1.57  # 57%
    weekly_target_high = starting_capital * 1.71  # 71%
    
    print(f"\n📈 Daily Target (6-9%):")
    print(f"   Target Range: ${daily_target_low:.2f} - ${daily_target_high:.2f}")
    print(f"   Current: ${current_value:.2f}")
    print(f"   Progress: {(current_value / daily_target_low) * 100:.1f}% of low target")
    print(f"   Needed: ${daily_target_low - current_value:+.2f} to reach 6%")
    
    print(f"\n📈 7-Day Target (57-71%):")
    print(f"   Target Range: ${weekly_target_low:.2f} - ${weekly_target_high:.2f}")
    print(f"   Current: ${current_value:.2f}")
    print(f"   Progress: {(current_value / weekly_target_low) * 100:.1f}% of low target")
    print(f"   Days Remaining: ~6 days")
    
    # ========== SYSTEM HEALTH ==========
    print_header("🔧 SYSTEM HEALTH")
    
    print(f"\n[CHECK] Rate Limiting:")
    print(f"   Target: 3 trades/hour")
    print(f"   Actual: {avg_trades_per_hour:.1f} trades/hour")
    print(f"   Status: {'[CHECK] WORKING' if avg_trades_per_hour <= 3.5 else '[WARNING]️ OVER LIMIT'}")
    
    print(f"\n[CHECK] Risk Management:")
    print(f"   Position Size: 2% (${cash * 0.02:.2f})")
    print(f"   Max Positions: 8")
    print(f"   Current Positions: {len(positions)}")
    print(f"   Min Confidence: 80%")
    print(f"   Daily Loss Limit: $10")
    
    print(f"\n[CHECK] Trading Mode:")
    print(f"   Mode: RECOVERY MODE")
    print(f"   Style: CONSERVATIVE")
    print(f"   Symbols: Top 5 Crypto (BTC, ETH, SOL, LINK, UNI)")
    print(f"   Hours: 24/7")
    
    # ========== SUMMARY ==========
    print_header("📋 SUMMARY")
    
    status_emoji = "🟢" if total_pnl >= 0 else "🔴"
    rate_emoji = "[CHECK]" if avg_trades_per_hour <= 3.5 else "[WARNING]️"
    
    print(f"\n{status_emoji} Portfolio: ${current_value:.2f} ({total_pnl_pct:+.2f}%)")
    print(f"{rate_emoji} Trading Rate: {avg_trades_per_hour:.1f} trades/hour")
    print(f"💰 Cash Available: ${cash:.2f}")
    print(f"📈 Open Positions: {len(positions)}")
    print(f"🎯 Daily Target: ${daily_target_low:.2f} (need ${daily_target_low - current_value:+.2f})")
    print(f"⏰ Recovery Mode: {hours_since_recovery:.1f} hours")
    
    print("\n" + "=" * 80)
    print("  Report Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

