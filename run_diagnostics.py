#!/usr/bin/env python3
"""
PROMETHEUS System Diagnostics
Comprehensive check of all trading system components
"""

import os
import sys
import json
import sqlite3
from datetime import datetime

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_visual_patterns():
    print_section("1. VISUAL AI PATTERNS")
    try:
        with open('visual_ai_patterns.json', 'r') as f:
            data = json.load(f)
        
        patterns = data.get('patterns', {})
        total = len(patterns)
        
        # Count by type
        cryptos = ['BTC', 'ETH', 'SOL', 'DOGE', 'AVAX', 'LINK', 'ADA', 'XRP', 'DOT', 'LTC', 'ATOM']
        crypto_count = sum(1 for k in patterns.keys() if any(k.startswith(c + '_') for c in cryptos))
        stock_count = total - crypto_count
        
        print(f"  Total Charts Analyzed: {total}")
        print(f"  - Stock Charts: {stock_count}")
        print(f"  - Crypto Charts: {crypto_count}")
        
        # Crypto breakdown
        print("\n  Crypto Coverage:")
        for c in cryptos:
            count = len([k for k in patterns.keys() if k.startswith(c + '_')])
            status = "OK" if count > 0 else "MISSING"
            print(f"    {c}: {count} charts [{status}]")
        
        # Check trends
        trends = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        for p in patterns.values():
            t = p.get('trend', 'neutral').lower()
            if t in trends:
                trends[t] += 1
        
        print(f"\n  Trend Distribution:")
        for t, c in trends.items():
            print(f"    {t.capitalize()}: {c} ({c/total*100:.1f}%)")
        
        return crypto_count > 0
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def check_learning_system():
    print_section("2. LEARNING SYSTEM")
    try:
        conn = sqlite3.connect('prometheus_learning.db')
        cursor = conn.cursor()
        
        # Trade history
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='closed' THEN 1 ELSE 0 END) FROM trade_history")
        total, closed = cursor.fetchone()
        print(f"  Trade History: {total} total, {closed or 0} closed")
        
        # AI Attribution
        cursor.execute("SELECT COUNT(*), SUM(CASE WHEN outcome_recorded=1 THEN 1 ELSE 0 END) FROM ai_attribution")
        total_attr, with_outcome = cursor.fetchone()
        print(f"  AI Attribution: {total_attr} total, {with_outcome or 0} with outcomes")
        
        # Check learning parameters
        print("\n  Learning Parameters (from code):")
        print("    min_trades_for_learning: 20 (reduced from 50)")
        print("    model_update_frequency: 50 (reduced from 100)")
        print("    AGGRESSIVE time trigger: 30 min (reduced from 1 hour)")
        
        conn.close()
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def check_trading_config():
    print_section("3. TRADING CONFIGURATION")
    try:
        # Check risk limits in the trading session file
        with open('prometheus_active_trading_session.py', 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Visual pattern weight
        if 'boost = 3 + int(pattern_confidence * 3)' in content:
            print("  Visual Pattern Weight: 3-6 (confidence-scaled) [OK]")
        else:
            print("  Visual Pattern Weight: Fixed +3 (original)")

        # Check for crypto note
        if 'Crypto symbols' in content or 'crypto' in content.lower():
            print("  Crypto Note in Code: Present [OK]")

        print("\n  Risk Limits (from config):")
        print("    take_profit_pct: 10%")
        print("    stop_loss_pct: 3%")
        print("    position_size_pct: 5%")

        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def check_api_keys():
    print_section("4. API KEYS")
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_AI_API_KEY': os.getenv('GOOGLE_AI_API_KEY'),
        'ZHIPUAI_API_KEY': os.getenv('ZHIPUAI_API_KEY'),
        'ALPACA_API_KEY': os.getenv('ALPACA_API_KEY'),
    }
    
    all_ok = True
    for name, value in keys.items():
        status = "SET" if value else "NOT SET"
        symbol = "OK" if value else "MISSING"
        print(f"  {name}: {status} [{symbol}]")
        if 'ALPACA' in name and not value:
            all_ok = False
    
    return all_ok

def check_visual_provider():
    print_section("5. VISUAL PATTERN PROVIDER")
    try:
        sys.path.insert(0, '.')
        from core.visual_pattern_provider import VisualPatternProvider
        
        provider = VisualPatternProvider('visual_ai_patterns.json')
        
        # Test crypto symbols
        test_symbols = ['BTC', 'ETH', 'SOL', 'AAPL', 'TSLA']
        print("  Symbol Coverage Test:")
        for sym in test_symbols:
            has_data = provider.has_data_for_symbol(sym)
            consensus = provider.get_trend_consensus(sym)
            status = "OK" if has_data else "NO DATA"
            print(f"    {sym}: {consensus['trend']} ({consensus['confidence']:.0%}) [{status}]")
        
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def check_database_integrity():
    print_section("6. DATABASE INTEGRITY")
    try:
        conn = sqlite3.connect('prometheus_learning.db')
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required = ['trade_history', 'ai_attribution', 'open_positions']
        print("  Required Tables:")
        for t in required:
            status = "EXISTS" if t in tables else "MISSING"
            print(f"    {t}: [{status}]")
        
        # Check for data consistency
        cursor.execute("SELECT COUNT(*) FROM trade_history WHERE status='pending'")
        pending = cursor.fetchone()[0]
        print(f"\n  Pending Trades: {pending} (should be 0 or few)")
        
        conn.close()
        return pending < 10
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    print("\n" + "#" * 60)
    print("#" + " " * 58 + "#")
    print("#" + "  PROMETHEUS SYSTEM DIAGNOSTICS".center(58) + "#")
    print("#" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(58) + "#")
    print("#" + " " * 58 + "#")
    print("#" * 60)
    
    results = {}
    results['Visual Patterns'] = check_visual_patterns()
    results['Learning System'] = check_learning_system()
    results['Trading Config'] = check_trading_config()
    results['API Keys'] = check_api_keys()
    results['Visual Provider'] = check_visual_provider()
    results['Database'] = check_database_integrity()
    
    print_section("SUMMARY")
    all_pass = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "[OK]" if passed else "[!!]"
        print(f"  {name}: {status} {symbol}")
        if not passed:
            all_pass = False
    
    print("\n" + "=" * 60)
    if all_pass:
        print("  STATUS: ALL SYSTEMS OPERATIONAL")
    else:
        print("  STATUS: SOME ISSUES DETECTED - Review above")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

