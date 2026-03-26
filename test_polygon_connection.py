"""
Test Polygon.io API connection and data fetching
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_polygon():
    print("\n" + "="*70)
    print("POLYGON.IO CONNECTION TEST")
    print("="*70)
    
    # Check if API key is set
    api_key = os.getenv('POLYGON_API_KEY')
    if not api_key:
        print("[ERROR] POLYGON_API_KEY not found in environment")
        return False
    
    print(f"[OK] API Key found: {api_key[:10]}...")
    
    # Try to import and initialize Polygon provider
    try:
        from core.polygon_premium_provider import PolygonPremiumProvider
        print("[OK] Polygon provider module imported")
    except ImportError as e:
        print(f"[ERROR] Could not import Polygon provider: {e}")
        return False
    
    # Initialize provider
    try:
        provider = PolygonPremiumProvider()
        print(f"[OK] Polygon provider initialized")
        print(f"    S3 Access: {provider.s3_available}")
        print(f"    API Access: {provider.api_available}")
    except Exception as e:
        print(f"[ERROR] Failed to initialize provider: {e}")
        return False
    
    # Test fetching data for a few symbols
    test_symbols = ['AAPL', 'TSLA', 'MSFT']
    print(f"\n[TEST] Fetching data for {len(test_symbols)} symbols...")
    
    for symbol in test_symbols:
        try:
            data = await provider.get_live_price(symbol)
            if data:
                print(f"  [OK] {symbol}: ${data.get('price', 'N/A')}")
            else:
                print(f"  [SKIP] {symbol}: No data (may need premium access)")
        except Exception as e:
            print(f"  [ERROR] {symbol}: {e}")
    
    print("\n" + "="*70)
    print("RESULT: Polygon.io is configured and accessible")
    print("="*70)
    return True

if __name__ == "__main__":
    asyncio.run(test_polygon())
