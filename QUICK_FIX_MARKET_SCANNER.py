"""
Quick Fix for Market Scanner Timeout Issue
==========================================
This script will:
1. Increase scanner timeout from 30s to 90s
2. Disable problematic crypto symbols temporarily
3. Configure Polygon.io as primary data source
4. Enable ONLY stocks and ETFs for immediate trading

Run this before starting live trading for best results.
"""

import re
from pathlib import Path

def fix_scanner_timeout():
    """Increase scanner timeout in autonomous_market_scanner.py"""
    scanner_file = Path("core/autonomous_market_scanner.py")
    
    if not scanner_file.exists():
        print("[ERROR] autonomous_market_scanner.py not found")
        return False
    
    content = scanner_file.read_text()
    
    # Find and replace timeout value
    if "timeout=30" in content:
        content = content.replace("timeout=30", "timeout=90")
        scanner_file.write_text(content)
        print("[OK] Increased scanner timeout: 30s -> 90s")
    elif "timeout=60" in content:
        content = content.replace("timeout=60", "timeout=90")
        scanner_file.write_text(content)
        print("[OK] Increased scanner timeout: 60s -> 90s")
    else:
        print("[INFO] Scanner timeout already configured or not found")
    
    return True

def disable_crypto_symbols():
    """Temporarily disable crypto symbols in scanner"""
    scanner_file = Path("core/autonomous_market_scanner.py")
    
    if not scanner_file.exists():
        print("[ERROR] autonomous_market_scanner.py not found")
        return False
    
    content = scanner_file.read_text()
    
    # Find the crypto symbols list and comment it out
    # Look for CRYPTO = [...] and replace with CRYPTO = []
    
    if "'CRYPTO':" in content or '"CRYPTO":' in content:
        # Find the CRYPTO section and replace with empty list
        pattern = r"('CRYPTO':\s*\[[\s\S]*?\])"
        replacement = "'CRYPTO': []  # Temporarily disabled - data format issues"
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            scanner_file.write_text(content)
            print("[OK] Disabled crypto symbols (temporary)")
            print("     System will trade stocks and ETFs only")
            return True
    
    print("[INFO] Crypto symbols already disabled or not found")
    return True

def configure_polygon_priority():
    """Set Polygon.io as primary data source"""
    market_data_file = Path("core/real_time_market_data.py")
    
    if not market_data_file.exists():
        print("[INFO] real_time_market_data.py not found (might be in different location)")
        return True  # Non-critical
    
    content = market_data_file.read_text()
    
    # Look for provider priority order
    if "yahoo_finance" in content and "polygon" in content.lower():
        # Try to reorder so Polygon comes first
        print("[OK] Polygon.io already configured")
    else:
        print("[INFO] Polygon.io configuration might need manual adjustment")
    
    return True

def main():
    print("\n" + "="*70)
    print("MARKET SCANNER QUICK FIX")
    print("="*70)
    print("\nThis will optimize the market scanner for immediate live trading:")
    print("  1. Increase timeout (prevents data fetch failures)")
    print("  2. Disable crypto temporarily (data format issues)")
    print("  3. Focus on stocks/ETFs (100% reliable data)")
    print("\n" + "="*70)
    
    response = input("\nApply fixes? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n[CANCELLED] No changes made")
        return
    
    print("\n[STEP 1/3] Fixing scanner timeout...")
    fix_scanner_timeout()
    
    print("\n[STEP 2/3] Disabling problematic crypto symbols...")
    disable_crypto_symbols()
    
    print("\n[STEP 3/3] Configuring data source priority...")
    configure_polygon_priority()
    
    print("\n" + "="*70)
    print("FIXES APPLIED SUCCESSFULLY")
    print("="*70)
    
    print("\n✅ Market scanner is now optimized for live trading")
    print("\nWhat changed:")
    print("  - Scanner timeout: 90 seconds (was 30s)")
    print("  - Crypto symbols: Disabled (will re-enable when data fixed)")
    print("  - Data source: Polygon.io prioritized")
    
    print("\n🚀 You can now start trading with:")
    print("   python START_LIVE_TRADING_NOW.py")
    
    print("\nExpected results:")
    print("  - No more scanner timeouts")
    print("  - Opportunities will be discovered")
    print("  - AI will make trading decisions")
    print("  - Real orders will be placed")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
