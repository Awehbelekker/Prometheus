#!/usr/bin/env python3
"""Check market conditions and AI decision logs"""

import requests
import json
from datetime import datetime

print('🌍 MARKET CONDITIONS & AI ANALYSIS')
print('=' * 60)
print(f'⏰ Current Time: {datetime.now().strftime("%H:%M:%S")}')
print('=' * 60)

# Check market data endpoints
market_endpoints = [
    ('/api/market-data', '📊 Market Data'),
    ('/api/revolutionary/status', '🤖 Revolutionary Status'),
    ('/api/ai/status', '🧠 AI Status'),
    ('/health', '💚 System Health'),
]

print('🌍 MARKET CONDITIONS:')
print('-' * 40)

for endpoint, name in market_endpoints:
    try:
        response = requests.get(f'http://localhost:8000{endpoint}')
        if response.status_code == 200:
            data = response.json()
            print(f'{name}: [CHECK]')
            
            # Extract relevant data
            if 'market-data' in endpoint:
                if isinstance(data, dict):
                    if 'symbols' in data:
                        print(f'   Active Symbols: {len(data.get("symbols", []))}')
                    if 'status' in data:
                        print(f'   Status: {data.get("status", "unknown")}')
                    if 'last_update' in data:
                        print(f'   Last Update: {data.get("last_update", "unknown")}')
                else:
                    print(f'   Response: {str(data)[:100]}...')
                    
            elif 'revolutionary' in endpoint:
                print(f'   Status: {data.get("status", "unknown")}')
                engines = data.get("engines", {})
                active_engines = sum(1 for status in engines.values() if status)
                print(f'   Active Engines: {active_engines}/{len(engines)}')
                
            elif 'ai/status' in endpoint:
                print(f'   AI Available: {data.get("ai_available", False)}')
                print(f'   Trading Intelligence: {data.get("trading_intelligence", "unknown")}')
                
            elif 'health' in endpoint:
                print(f'   Status: {data.get("status", "unknown")}')
                
        else:
            print(f'{name}: [ERROR] {response.status_code}')
            
    except Exception as e:
        print(f'{name}: [ERROR] {str(e)[:40]}...')
    print()

print('🕐 MARKET TIMING ANALYSIS:')
print('-' * 40)
now = datetime.now()
hour = now.hour
minute = now.minute

print(f'Current Time: {hour:02d}:{minute:02d}')

if hour < 4:
    print('🌙 PRE-MARKET: Very low activity expected')
    print('   - Most markets closed')
    print('   - Limited trading opportunities')
elif 4 <= hour < 9:
    print('🌅 PRE-MARKET: Early trading hours')
    print('   - Some pre-market activity')
    print('   - Conservative AI approach expected')
elif 9 <= hour < 16:
    print('📈 MARKET HOURS: Peak trading time')
    print('   - Full market activity')
    print('   - AI should be most active')
elif 16 <= hour < 20:
    print('🌆 AFTER-HOURS: Extended trading')
    print('   - Reduced liquidity')
    print('   - More selective trading')
else:
    print('🌃 OVERNIGHT: Minimal activity')
    print('   - Crypto may be active')
    print('   - Very conservative approach')

print()
print('🤖 AI DECISION FACTORS:')
print('-' * 40)
print('Possible reasons for low activity:')
print('1. 🕐 Market timing (current hour)')
print('2. 📊 Conservative risk settings (1% max position)')
print('3. 🎯 High AI standards for trade entry')
print('4. 🔗 IB connection intermittency')
print('5. 📈 Market conditions not meeting criteria')
print('6. 🧠 AI in learning/analysis phase')

print()
print('🚨 LIVE TRADING STATUS: ACTIVE')
print('   Session: session_1759597921')
print('   Capital: $250.00 USD')
print('   Account: U21922116')
