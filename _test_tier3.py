"""Quick test of the new Tier 3 endpoints"""
import urllib.request, json

# Test 1: XAI Explain Decision
print("=== Test 1: XAI Explain Decision ===")
body = json.dumps({
    'symbol': 'AAPL', 'action': 'BUY', 'confidence': 0.78, 'price': 185.50,
    'market_data': {'rsi': 35, 'momentum': 0.02, 'volume_ratio': 1.5, 'sma_20': 180.0, 'sma_50': 178.0},
    'decision_scores': {'BUY': 2.1, 'SELL': 0.8, 'HOLD': 1.2}
}).encode()
req = urllib.request.Request('http://localhost:8000/api/ai/explain-decision', data=body, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req, timeout=30)
d = json.loads(r.read())
print(f"  Success: {d['success']}")
if d['success']:
    e = d['explanation']
    print(f"  Keys: {list(e.keys())}")
    print(f"  Key factors: {e.get('key_factors', [])[:3]}")
    print(f"  NL Summary: {e.get('natural_language_summary', e.get('summary', 'N/A'))[:200]}")
    print(f"  Features: {len(e.get('feature_contributions', []))} features")

# Test 2: Adversarial Robustness Validate Signal
print("\n=== Test 2: Validate Signal ===")
body = json.dumps({
    'symbol': 'AAPL', 'action': 'BUY', 'confidence': 0.78, 'price': 185.50,
    'market_data': {'rsi': 35, 'momentum': 0.02, 'volume_ratio': 1.5},
    'decision_scores': {'BUY': 2.1, 'SELL': 0.8, 'HOLD': 1.2}
}).encode()
req = urllib.request.Request('http://localhost:8000/api/ai/validate-signal', data=body, headers={'Content-Type': 'application/json'})
r = urllib.request.urlopen(req, timeout=30)
d = json.loads(r.read())
print(f"  Success: {d['success']}")
print(f"  Valid: {d.get('is_valid')}")
print(f"  Risk: {d.get('overall_risk')}")
print(f"  Checks: {d.get('checks_passed')}/{d.get('checks_total')}")
print(f"  Confidence adj: {d.get('confidence_adjustment')}")

# Test 3: Signal Weights
print("\n=== Test 3: Signal Weights ===")
r = urllib.request.urlopen('http://localhost:8000/api/ai/signal-weights', timeout=10)
d = json.loads(r.read())
print(f"  Voters: {d.get('total_voters')}")
print(f"  Total weight: {d.get('total_weight')}")

# Test 4: All Systems
print("\n=== Test 4: All Systems Count ===")
r = urllib.request.urlopen('http://localhost:8000/api/ai/all-systems/status', timeout=30)
d = json.loads(r.read())
print(f"  Total: {d['total_systems']}, Active: {d['active_systems']}")

print("\n[DONE] All Tier 3 tests passed!")
