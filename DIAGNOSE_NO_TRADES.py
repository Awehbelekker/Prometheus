#!/usr/bin/env python3
"""
Diagnose why no trades are being executed
"""
import sys
import os
from datetime import datetime, timedelta
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

print("="*80)
print("DIAGNOSING WHY NO TRADES ARE EXECUTING")
print("="*80)
print()

# Check 1: Minimum confidence threshold
print("1. CHECKING TRADING PARAMETERS")
print("-" * 40)
min_confidence = 0.45  # From launch_ultimate_prometheus_LIVE_TRADING.py
print(f"   Minimum Confidence Required: {min_confidence*100:.0f}%")
print(f"   Position Size: 8% of capital")
print(f"   Max Positions: 15")
print(f"   Max Trades/Hour: 20")
print()

# Check 2: Recent trades from database
print("2. CHECKING RECENT TRADES")
print("-" * 40)
try:
    db = sqlite3.connect('prometheus_learning.db')
    cursor = db.cursor()
    
    # Get recent trades (last 24 hours)
    one_day_ago = (datetime.now() - timedelta(days=1)).isoformat()
    cursor.execute("""
        SELECT symbol, action, timestamp, ai_confidence 
        FROM trade_history 
        WHERE timestamp > ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    """, (one_day_ago,))
    
    recent_trades = cursor.fetchall()
    
    if recent_trades:
        print(f"   ✅ Found {len(recent_trades)} trades in last 24 hours:")
        for trade in recent_trades[:5]:
            symbol, action, timestamp, confidence = trade
            print(f"      {symbol}: {action} @ {confidence*100:.1f}% confidence ({timestamp})")
    else:
        print("   ❌ No trades in last 24 hours")
    
    # Get total trades
    cursor.execute("SELECT COUNT(*) FROM trade_history")
    total_trades = cursor.fetchone()[0]
    print(f"   Total trades in database: {total_trades}")
    
    db.close()
except Exception as e:
    print(f"   ⚠️  Could not check database: {e}")

print()

# Check 3: Current positions
print("3. CHECKING CURRENT POSITIONS")
print("-" * 40)
try:
    from core.alpaca_trading_service import get_alpaca_service
    alpaca = get_alpaca_service(use_paper=False)
    
    if alpaca.is_available():
        positions = alpaca.get_positions()
        account = alpaca.get_account_info()
        
        print(f"   Portfolio Value: ${account.get('portfolio_value', 0):.2f}")
        print(f"   Cash Available: ${account.get('cash', 0):.2f}")
        print(f"   Buying Power: ${account.get('buying_power', 0):.2f}")
        print(f"   Current Positions: {len(positions)}")
        
        if positions:
            print("   Open Positions:")
            for pos in positions:
                print(f"      {pos['symbol']}: {pos['qty']} @ ${pos['current_price']:.2f} "
                      f"(P/L: ${pos['unrealized_pl']:.2f}, {pos['unrealized_plpc']*100:.2f}%)")
        
        # Check if we're at max positions
        if len(positions) >= 15:
            print(f"   ⚠️  MAX POSITIONS REACHED ({len(positions)}/15)")
            print("      System won't open new positions until some are closed")
        else:
            print(f"   ✅ Can open {15 - len(positions)} more positions")
    else:
        print("   ❌ Alpaca not available")
except Exception as e:
    print(f"   ⚠️  Could not check positions: {e}")

print()

# Check 4: Possible reasons
print("4. POSSIBLE REASONS FOR NO TRADES")
print("-" * 40)
print("   The system IS running, but may not be finding opportunities because:")
print()
print("   a) AI signals below 45% confidence threshold")
print("      → System only trades when confidence ≥ 45%")
print()
print("   b) Market conditions not meeting criteria")
print("      → AI may be generating HOLD signals instead of BUY/SELL")
print()
print("   c) Rate limiting")
print("      → May have hit 20 trades/hour limit")
print()
print("   d) Max positions reached")
print("      → System won't open new positions if 15 positions already open")
print()
print("   e) Insufficient buying power")
print("      → Need cash available to open new positions")
print()
print("   f) Broker connection issues")
print("      → Alpaca broker may not be properly connected in trading loop")
print()

# Check 5: Recommendations
print("5. RECOMMENDATIONS")
print("-" * 40)
print("   To see what's happening:")
print("   1. Check the latest log file:")
print("      Get-Content prometheus_live_trading_*.log -Tail 100 | Select-String 'Signal|Trade|confidence'")
print()
print("   2. Lower confidence threshold (if too conservative):")
print("      Edit launch_ultimate_prometheus_LIVE_TRADING.py")
print("      Change 'min_confidence': 0.45 to 0.35 or 0.30")
print()
print("   3. Check if system is analyzing symbols:")
print("      Look for 'Analyzing X crypto symbols' in logs")
print()
print("   4. Verify AI signals are being generated:")
print("      Look for 'AI Signal for SYMBOL' in logs")
print()

print("="*80)


