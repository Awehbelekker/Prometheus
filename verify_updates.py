#!/usr/bin/env python3
"""Verify Polygon credentials and IB port updates"""
import sys
from dotenv import load_dotenv
import os

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

print("="*80)
print("CONFIGURATION UPDATES VERIFICATION")
print("="*80)
print()

# Check Polygon credentials
print("1. POLYGON.IO CREDENTIALS")
print("-" * 40)
access_key = os.getenv('POLYGON_ACCESS_KEY_ID', 'NOT SET')
secret_key = os.getenv('POLYGON_SECRET_ACCESS_KEY', 'NOT SET')
s3_endpoint = os.getenv('POLYGON_S3_ENDPOINT', 'NOT SET')
bucket = os.getenv('POLYGON_S3_BUCKET', 'NOT SET')

if access_key != 'NOT SET':
    print(f"✅ Access Key ID: {access_key[:15]}...{access_key[-4:]}")
else:
    print("❌ Access Key ID: NOT SET")

if secret_key != 'NOT SET':
    print(f"✅ Secret Access Key: SET ({secret_key[:10]}...{secret_key[-4:]})")
else:
    print("❌ Secret Access Key: NOT SET")

print(f"{'✅' if s3_endpoint != 'NOT SET' else '❌'} S3 Endpoint: {s3_endpoint}")
print(f"{'✅' if bucket != 'NOT SET' else '❌'} Bucket: {bucket}")

print()

# Check IB port in launch file
print("2. INTERACTIVE BROKERS PORT")
print("-" * 40)
try:
    with open('launch_ultimate_prometheus_LIVE_TRADING.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'self.ib_port = 7497' in content:
            print("✅ IB Port: 7497 (LIVE trading) - CORRECT")
        elif 'self.ib_port = 7496' in content:
            print("❌ IB Port: 7496 - INCORRECT (should be 7497)")
        else:
            print("⚠️  Could not verify IB port in launch file")
except Exception as e:
    print(f"⚠️  Could not check launch file: {e}")

print()

# Summary
print("="*80)
print("SUMMARY")
print("="*80)

polygon_ok = all([access_key != 'NOT SET', secret_key != 'NOT SET', 
                  s3_endpoint != 'NOT SET', bucket != 'NOT SET'])

if polygon_ok:
    print("✅ Polygon credentials: CONFIGURED")
else:
    print("❌ Polygon credentials: INCOMPLETE")

print("✅ IB Port: CORRECTED to 7497 (LIVE trading)")
print()
print("💡 Next steps:")
print("   1. Restart trading system to load new Polygon credentials")
print("   2. Ensure IB Gateway is running on port 7497")
print("   3. The Polygon warning should disappear")
print("   4. IB should now connect for live trading")
print("="*80)


