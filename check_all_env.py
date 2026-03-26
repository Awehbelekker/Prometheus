#!/usr/bin/env python3
"""
Check all Alpaca environment variables and configuration files
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

def check_env_vars():
    """Check all environment variables"""
    print("="*80)
    print("ENVIRONMENT VARIABLES CHECK")
    print("="*80)
    
    # Check all possible Alpaca env var names
    alpaca_vars = [
        'ALPACA_PAPER_KEY',
        'ALPACA_PAPER_SECRET',
        'ALPACA_LIVE_KEY',
        'ALPACA_LIVE_SECRET',
        'ALPACA_API_KEY',
        'ALPACA_SECRET_KEY',
        'ALPACA_PAPER_API_KEY',
        'ALPACA_PAPER_API_SECRET',
        'ALPACA_LIVE_API_KEY',
        'ALPACA_LIVE_API_SECRET',
        'APCA_API_KEY_ID',
        'APCA_API_SECRET_KEY',
        'APCA_API_BASE_URL',
        'ALPACA_BASE_URL',
        'ALPACA_PAPER_BASE_URL',
        'ALPACA_LIVE_BASE_URL'
    ]
    
    found_vars = {}
    for var in alpaca_vars:
        value = os.getenv(var)
        if value:
            # Show first 10 and last 4 chars for security
            masked = value[:10] + '...' + value[-4:] if len(value) > 14 else value
            found_vars[var] = masked
            print(f"✅ {var}: {masked}")
        else:
            print(f"❌ {var}: NOT SET")
    
    print(f"\n📊 Summary: {len(found_vars)}/{len(alpaca_vars)} variables set")
    return found_vars


def check_env_files():
    """Check .env files"""
    print("\n" + "="*80)
    print("ENVIRONMENT FILES CHECK")
    print("="*80)
    
    env_files = [
        '.env',
        'hrm_config.env',
        'optimal_dual_broker.env',
        'ARCHIVE_2025_10_20/PROMETHEUS-Enterprise-Package/scripts/advanced_features.env'
    ]
    
    found_creds = {}
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"\n📄 Found: {env_file}")
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            if any(keyword in line.upper() for keyword in ['ALPACA', 'APCA']):
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                if value and value.lower() not in ['your_key', 'your_secret', 'not_set', '']:
                                    masked = value[:10] + '...' + value[-4:] if len(value) > 14 else value
                                    print(f"   ✅ {key}: {masked}")
                                    found_creds[key] = value
                                else:
                                    print(f"   ⚠️  {key}: (placeholder/empty)")
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"❌ {env_file}: NOT FOUND")
    
    return found_creds


def check_daily_trading_report():
    """Check daily_trading_report.py for credentials"""
    print("\n" + "="*80)
    print("DAILY TRADING REPORT CHECK")
    print("="*80)
    
    report_file = 'daily_trading_report.py'
    found_creds = {}
    
    if os.path.exists(report_file):
        print(f"📄 Found: {report_file}")
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            import re
            patterns = [
                (r"os\.environ\['ALPACA_PAPER_KEY'\]\s*=\s*['\"]([^'\"]+)['\"]", 'ALPACA_PAPER_KEY'),
                (r"os\.environ\['ALPACA_PAPER_SECRET'\]\s*=\s*['\"]([^'\"]+)['\"]", 'ALPACA_PAPER_SECRET'),
                (r"os\.environ\['ALPACA_LIVE_KEY'\]\s*=\s*['\"]([^'\"]+)['\"]", 'ALPACA_LIVE_KEY'),
                (r"os\.environ\['ALPACA_LIVE_SECRET'\]\s*=\s*['\"]([^'\"]+)['\"]", 'ALPACA_LIVE_SECRET'),
            ]
            
            for pattern, key in patterns:
                match = re.search(pattern, content)
                if match:
                    value = match.group(1)
                    masked = value[:10] + '...' + value[-4:] if len(value) > 14 else value
                    print(f"   ✅ {key}: {masked}")
                    found_creds[key] = value
                else:
                    print(f"   ❌ {key}: NOT FOUND")
                    
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    else:
        print(f"❌ {report_file}: NOT FOUND")
    
    return found_creds


def check_config_files():
    """Check other config files"""
    print("\n" + "="*80)
    print("OTHER CONFIG FILES CHECK")
    print("="*80)
    
    config_files = [
        'core/alpaca_trading_service.py',
        'launch_ultimate_prometheus_LIVE_TRADING.py',
        'unified_production_server.py'
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"\n📄 Checking: {config_file}")
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for hardcoded credentials (not recommended but checking)
                import re
                # Look for patterns like 'AK...' or 'PK...' (Alpaca key prefixes)
                key_pattern = r"['\"]([AP]K[A-Z0-9]{20,})['\"]"
                matches = re.findall(key_pattern, content)
                if matches:
                    print(f"   ⚠️  Found potential API keys in code (not recommended):")
                    for match in matches[:3]:  # Show first 3
                        masked = match[:10] + '...' + match[-4:]
                        print(f"      {masked}")
            except Exception as e:
                print(f"   ❌ Error reading: {e}")


def main():
    """Main check function"""
    print("\n" + "="*80)
    print("COMPREHENSIVE ALPACA ENVIRONMENT CHECK")
    print("="*80)
    print(f"Current Directory: {os.getcwd()}")
    print(f"Python Version: {sys.version}")
    print()
    
    # Check environment variables
    env_vars = check_env_vars()
    
    # Check .env files
    env_file_creds = check_env_files()
    
    # Check daily_trading_report.py
    report_creds = check_daily_trading_report()
    
    # Check other config files
    check_config_files()
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    all_creds = {**env_vars, **env_file_creds, **report_creds}
    
    print(f"\n📊 Total credentials found: {len(all_creds)}")
    
    if all_creds:
        print("\n✅ Credentials found in:")
        if env_vars:
            print("   - Environment variables")
        if env_file_creds:
            print("   - .env files")
        if report_creds:
            print("   - daily_trading_report.py")
    else:
        print("\n❌ No Alpaca credentials found anywhere!")
        print("\n💡 To set credentials:")
        print("   1. Set environment variables, OR")
        print("   2. Add to .env file, OR")
        print("   3. Update daily_trading_report.py")
    
    # Check which credentials are actually being used
    print("\n" + "="*80)
    print("CREDENTIALS USAGE")
    print("="*80)
    
    # Test what the Alpaca service would use
    try:
        from core.alpaca_trading_service import get_alpaca_service
        
        # Check paper trading
        paper_key = os.getenv('ALPACA_PAPER_KEY') or os.getenv('APCA_API_KEY_ID') or os.getenv('ALPACA_API_KEY', '')
        paper_secret = os.getenv('ALPACA_PAPER_SECRET') or os.getenv('APCA_API_SECRET_KEY') or os.getenv('ALPACA_SECRET_KEY', '')
        
        print(f"\n📊 Paper Trading would use:")
        print(f"   Key: {'SET (' + paper_key[:10] + '...)' if paper_key else 'NOT SET'}")
        print(f"   Secret: {'SET' if paper_secret else 'NOT SET'}")
        
        # Check live trading
        live_key = os.getenv('ALPACA_LIVE_KEY') or os.getenv('ALPACA_LIVE_API_KEY') or os.getenv('ALPACA_API_KEY', '')
        live_secret = os.getenv('ALPACA_LIVE_SECRET') or os.getenv('ALPACA_LIVE_API_SECRET') or os.getenv('ALPACA_SECRET_KEY', '')
        
        print(f"\n📊 Live Trading would use:")
        print(f"   Key: {'SET (' + live_key[:10] + '...)' if live_key else 'NOT SET'}")
        print(f"   Secret: {'SET' if live_secret else 'NOT SET'}")
        
    except Exception as e:
        print(f"   ⚠️  Could not check service: {e}")


if __name__ == "__main__":
    main()



