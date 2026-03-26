import json
d = json.load(open('visual_ai_patterns.json'))
btc = {k:v for k,v in d['patterns'].items() if k.startswith('BTC_')}
print('BTC Chart Analysis:')
for k,v in list(btc.items())[:3]:
    print(f"  {k}:")
    print(f"    Trend: {v.get('trend', 'N/A')}")
    patterns = v.get('patterns_detected', [])
    print(f"    Patterns: {len(patterns)} found")
    for p in patterns[:2]:
        print(f"      - {p.get('name', p)} ({p.get('confidence', 'N/A')})")

