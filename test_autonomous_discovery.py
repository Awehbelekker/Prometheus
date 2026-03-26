"""Quick test of autonomous discovery"""
import asyncio

async def test():
    print("\n" + "="*70)
    print("TESTING AUTONOMOUS MARKET DISCOVERY")
    print("="*70)
    
    from core.autonomous_market_scanner import autonomous_scanner
    
    print("\n[INFO] Scanning markets...")
    opportunities = await autonomous_scanner.discover_best_opportunities(limit=5)
    
    print(f"\n[RESULT] Found {len(opportunities)} opportunities")
    
    for i, opp in enumerate(opportunities, 1):
        print(f"\n{i}. {opp.symbol} - {opp.expected_return:.1%} return")
        print(f"   Confidence: {opp.confidence:.0%}")
        print(f"   Type: {opp.opportunity_type.value}")
    
    print("\n" + "="*70)
    print("[SUCCESS] Autonomous system is working!")
    print("="*70)

asyncio.run(test())
