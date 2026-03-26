#!/usr/bin/env python3
"""
Update Polygon.io credentials in .env file
"""
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

def update_polygon_credentials(access_key_id, secret_access_key, s3_endpoint, bucket, env_file='.env'):
    """Update Polygon credentials in .env file"""
    env_path = Path(env_file)
    
    if not env_path.exists():
        print(f"❌ .env file not found at {env_path.absolute()}")
        return False
    
    try:
        # Read current .env file
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove old Polygon entries
        patterns_to_remove = [
            r'^POLYGON_API_KEY=.*$',
            r'^POLYGON_ACCESS_KEY_ID=.*$',
            r'^POLYGON_SECRET_ACCESS_KEY=.*$',
            r'^POLYGON_S3_ENDPOINT=.*$',
            r'^POLYGON_S3_BUCKET=.*$',
            r'^# POLYGON.*$'
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Add new Polygon credentials
        polygon_section = f"""
# POLYGON.IO (Premium Market Data - S3 Access)
POLYGON_ACCESS_KEY_ID={access_key_id}
POLYGON_SECRET_ACCESS_KEY={secret_access_key}
POLYGON_S3_ENDPOINT={s3_endpoint}
POLYGON_S3_BUCKET={bucket}
# Note: POLYGON_API_KEY can be added separately for REST API access
"""
        
        # Find where to add (after Alpaca section or at end)
        if '# POLYGON' in content or 'POLYGON_API_KEY' in content:
            # Replace existing Polygon section
            content = re.sub(
                r'# POLYGON.*?(?=\n\n|\n# |$)',
                polygon_section.strip(),
                content,
                flags=re.DOTALL
            )
        else:
            # Add at end
            content += polygon_section
        
        # Clean up multiple blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Write back to file
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated .env file with Polygon credentials")
        print(f"   Access Key ID: {access_key_id[:15]}...{access_key_id[-4:]}")
        print(f"   Secret Access Key: {secret_access_key[:10]}...{secret_access_key[-4:]}")
        print(f"   S3 Endpoint: {s3_endpoint}")
        print(f"   Bucket: {bucket}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("UPDATE POLYGON.IO CREDENTIALS")
    print("="*80)
    print()
    
    # Credentials from user
    access_key_id = "17b081b1-55a8-412b-81d6-87e0b2bd41d9"
    secret_access_key = "QGKb6mcqdd9yvJ6kxDA69qRPvBNCCzzU"
    s3_endpoint = "https://files.massive.com"
    bucket = "flatfiles"
    
    print(f"Updating Polygon credentials:")
    print(f"  Access Key ID: {access_key_id[:15]}...{access_key_id[-4:]}")
    print(f"  S3 Endpoint: {s3_endpoint}")
    print(f"  Bucket: {bucket}")
    print()
    
    # Update .env file
    success = update_polygon_credentials(access_key_id, secret_access_key, s3_endpoint, bucket)
    
    if success:
        print()
        print("="*80)
        print("UPDATE COMPLETE")
        print("="*80)
        print()
        print("✅ Polygon credentials have been added to .env file")
        print()
        print("💡 Next steps:")
        print("   1. Restart the trading system to load the new credentials")
        print("   2. The Polygon warning should disappear on next startup")
        print()
        print("📋 To verify:")
        print("   python -c \"from dotenv import load_dotenv; import os; load_dotenv(); print('Access Key:', os.getenv('POLYGON_ACCESS_KEY_ID', 'NOT SET')[:15])\"")
        print("="*80)
    else:
        print()
        print("="*80)
        print("UPDATE FAILED")
        print("="*80)
        sys.exit(1)


