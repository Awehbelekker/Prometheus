"""
End-to-end test of the Chart Vision Analyzer.
Fetches real AAPL data, renders a candlestick chart, sends it to llava:7b.
"""
import asyncio
import sys
import time

sys.path.insert(0, ".")


async def main():
    from core.chart_vision_analyzer import ChartVisionAnalyzer

    analyzer = ChartVisionAnalyzer()
    await analyzer.initialize()

    print(f"Connected: {analyzer.is_connected}")
    print(f"Model available: {analyzer._model_available}")
    print(f"Vision model: {analyzer.vision_model}")
    print()

    if not analyzer.is_available():
        print("ERROR: Vision analyzer not available")
        return

    # Test 1: analyze_symbol (fetches its own data via yfinance)
    print("=" * 60)
    print("TEST: Analyzing AAPL chart with llava:7b")
    print("(This may take 30-160s depending on model warm state)")
    print("=" * 60)

    start = time.time()
    result = await analyzer.analyze_symbol("AAPL", period="1mo", interval="1d")
    elapsed = time.time() - start

    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Source: {result.get('source', '?')}")
    print(f"Model: {result.get('model', '?')}")
    print(f"Recommendation: {result.get('recommendation', '?')}")
    print(f"Confidence: {result.get('confidence', '?')}")
    print(f"Trend: {result.get('trend', '?')}")
    print(f"Patterns: {result.get('patterns', [])}")
    print(f"Formations: {result.get('formations', [])}")
    print(f"Support: {result.get('support_level', '?')}")
    print(f"Resistance: {result.get('resistance_level', '?')}")
    print(f"Volume: {result.get('volume_pattern', '?')}")
    print(f"Reasoning: {result.get('reasoning', '?')[:200]}")

    await analyzer.close()
    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
