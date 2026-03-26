"""Quick test of pattern matching"""
import logging
logging.basicConfig(level=logging.DEBUG)

from core.pattern_integration import PatternIntegration
pi = PatternIntegration()

print(f"\n=== Pattern Integration Test ===")
print(f"Loaded {len(pi.patterns)} pattern categories")
for cat, pats in pi.patterns.items():
    print(f"  {cat}: {len(pats) if isinstance(pats, dict) else 'N/A'} pattern sets")

# Test matching for AAPL with uptrend
market_data = {
    'symbol': 'AAPL',
    'trend': 'up',
    'volatility': 0.0021,
    'volume_ratio': 15.15
}

print(f"\n=== Testing AAPL with trend=up ===")
matches = pi.match_patterns(market_data, 'sideways', 'AAPL')
print(f"\nMatches found: {len(matches)}")
for m in matches[:5]:
    print(f"  {m['pattern_key']}: similarity={m['similarity']:.3f}")

# Test with MSFT
market_data2 = {
    'symbol': 'MSFT',
    'trend': 'up',
    'volatility': 0.0022,
    'volume_ratio': 5.59
}
print(f"\n=== Testing MSFT with trend=up ===")
matches2 = pi.match_patterns(market_data2, 'sideways', 'MSFT')
print(f"\nMatches found: {len(matches2)}")
for m in matches2[:5]:
    print(f"  {m['pattern_key']}: similarity={m['similarity']:.3f}")
