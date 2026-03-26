import json
d = json.load(open('visual_ai_patterns.json'))
cryptos = ['BTC', 'ETH', 'SOL', 'DOGE', 'AVAX', 'LINK', 'ADA', 'XRP', 'DOT', 'LTC', 'ATOM']
print("Crypto Pattern Coverage:")
total = 0
for c in cryptos:
    count = len([k for k in d['patterns'].keys() if k.startswith(c + '_')])
    print(f"  {c}: {count} charts")
    total += count
print(f"\nTotal crypto charts trained: {total}")
print(f"Total patterns in DB: {len(d['patterns'])}")

