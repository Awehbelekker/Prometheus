#!/usr/bin/env python3
"""
Update Polygon.io API key in .env file
"""
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def update_polygon_key(api_key: str, env_file: str = '.env'):
    """Update or add Polygon API key to .env file"""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path.absolute()}")
        return False
    
    try:
        # Read current .env file
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if POLYGON_API_KEY exists
        pattern = r'^POLYGON_API_KEY=.*$'
        if re.search(pattern, content, re.MULTILINE):
            # Update existing key
            content = re.sub(
                pattern,
                f'POLYGON_API_KEY={api_key}',
                content,
                flags=re.MULTILINE
            )
            print(f"✅ Updated POLYGON_API_KEY in .env file")
        else:
            # Add new key
            content += f'\n# Polygon.io API Key\nPOLYGON_API_KEY={api_key}\n'
            print(f"✅ Added POLYGON_API_KEY to .env file")
        
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ Successfully updated .env file with Polygon API key")
        print(f"   Key: {api_key[:15]}...{api_key[-4:] if len(api_key) > 15 else ''}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("UPDATE POLYGON.IO API KEY")
    print("="*80)
    print()
    
    # Get API key from user
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your Polygon.io API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        sys.exit(1)
    
    print()
    print(f"Updating Polygon API key: {api_key[:15]}...{api_key[-4:] if len(api_key) > 15 else ''}")
    print()
    
    # Update .env file
    success = update_polygon_key(api_key)
    
    if success:
        print()
        print("="*80)
        print("UPDATE COMPLETE")
        print("="*80)
        print()
        print("✅ Polygon API key has been added to .env file")
        print()
        print("💡 Next steps:")
        print("   1. Restart the trading system to load the new key")
        print("   2. The warning should disappear on next startup")
        print()
        print("📋 To verify:")
        print("   python -c \"from dotenv import load_dotenv; import os; load_dotenv(); print('Key:', os.getenv('POLYGON_API_KEY', 'NOT SET')[:15])\"")
        print("="*80)
    else:
        print()
        print("="*80)
        print("UPDATE FAILED")
        print("="*80)
        sys.exit(1)


