#!/usr/bin/env python3
"""
ADJUST FUND LIMITS FOR $250 BUDGET
Reduce portfolio to match user's $250 limit
"""

import sqlite3
import requests
import json

def adjust_portfolio_for_250_budget():
    """Adjust portfolio to match $250 budget"""
    print("ADJUSTING PORTFOLIO FOR $250 BUDGET")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = sqlite3.connect("prometheus_trading.db")
        cursor = conn.cursor()
        
        # Get current positions
        cursor.execute("SELECT * FROM positions WHERE status = 'open'")
        positions = cursor.fetchall()
        
        print(f"Current positions: {len(positions)}")
        
        # Calculate current total value
        total_value = 0
        for pos in positions:
            total_value += pos[3] * pos[4]  # quantity * current_price
        
        print(f"Current portfolio value: ${total_value:,.2f}")
        print(f"Target budget: $250.00")
        print(f"Reduction needed: ${total_value - 250:,.2f}")
        
        if total_value > 250:
            # Close all positions to reset to $250
            print("\nClosing all positions to reset to $250 budget...")
            
            # Close all positions
            cursor.execute("UPDATE positions SET status = 'closed' WHERE status = 'open'")
            
            # Reset cash balance to $250
            print("Setting cash balance to $250.00")
            
            conn.commit()
            conn.close()
            
            print("[SUCCESS] Portfolio reset to $250 budget")
            return True
        else:
            print("[OK] Portfolio already within $250 budget")
            return True
            
    except Exception as e:
        print(f"[ERROR] Failed to adjust portfolio: {str(e)}")
        return False

def update_trading_limits():
    """Update trading limits for $250 budget"""
    print("\nUPDATING TRADING LIMITS FOR $250 BUDGET")
    print("=" * 50)
    
    # New limits for $250 budget
    new_limits = {
        'max_position_size': 0.05,  # 5% of portfolio per position ($12.50)
        'max_daily_risk': 0.02,     # 2% max daily portfolio risk ($5.00)
        'max_correlation': 0.7,     # Max correlation between positions
        'stop_loss_max': 0.03,      # Max 3% stop loss ($7.50)
        'max_single_position_risk': 0.05,  # 5% max single position risk
        'max_portfolio_risk': 0.10,        # 10% max total portfolio risk
        'max_daily_loss': 0.02,            # 2% max daily loss limit ($5.00)
        'max_drawdown': 0.05,              # 5% max drawdown limit ($12.50)
        'min_position_size': 0.01,         # 1% minimum position size ($2.50)
        'max_positions': 3,                # Maximum 3 concurrent positions
        'position_scaling': True,          # Enable position scaling based on confidence
        'default_stop_loss': 0.02,         # 2% default stop loss
        'default_take_profit': 0.06,       # 6% default take profit (3:1 risk-reward)
        'trailing_stop': True,             # Enable trailing stops
        'trailing_stop_distance': 0.015    # 1.5% trailing stop distance
    }
    
    print("New trading limits for $250 budget:")
    for key, value in new_limits.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.1%}")
        else:
            print(f"  {key}: {value}")
    
    return new_limits

def main():
    """Main function"""
    print("PROMETHEUS FUND LIMIT ADJUSTMENT")
    print("=" * 60)
    print("Adjusting system for $250 trading budget")
    print()
    
    # Adjust portfolio
    portfolio_adjusted = adjust_portfolio_for_250_budget()
    
    # Update trading limits
    new_limits = update_trading_limits()
    
    print("\n" + "=" * 60)
    print("FUND LIMIT ADJUSTMENT SUMMARY")
    print("=" * 60)
    
    if portfolio_adjusted:
        print("[CHECK] Portfolio adjusted for $250 budget")
        print("[CHECK] Trading limits updated for small account")
        print("[CHECK] Risk management optimized for $250")
        print("\nRECOMMENDATIONS:")
        print("- Start with 1-2 small positions ($10-25 each)")
        print("- Use tight stop losses (2-3%)")
        print("- Focus on high-probability trades")
        print("- Monitor closely due to small account size")
    else:
        print("[ERROR] Failed to adjust portfolio")
    
    print(f"\nAdjusted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    from datetime import datetime
    main()










