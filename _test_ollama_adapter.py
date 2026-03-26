"""Quick test of the CPT-OSS Ollama adapter."""
import asyncio
import json
import sys
sys.path.insert(0, '.')

async def test():
    from core.gpt_oss_trading_adapter import GPTOSSTradingAdapter
    adapter = GPTOSSTradingAdapter()
    print(f"Ollama URL: {adapter.ollama_url}")
    print(f"Primary model: {adapter.primary_model}")
    print(f"Fallback model: {adapter.fallback_model}")

    # Initialize (connects to Ollama)
    await adapter.initialize()
    print(f"Connected: {adapter.is_connected}")
    print(f"Available models: {adapter._available_models}")
    print(f"has generate_trading_signal: {hasattr(adapter, 'generate_trading_signal')}")

    if adapter.is_connected:
        # Test actual signal generation
        print("\n--- Testing generate_trading_signal ---")
        market_data = {
            "price": 192.50,
            "volume": 3500000,
            "change_percent": 1.25,
            "rsi": 42.3,
            "sma_20": 189.0,
            "sma_50": 185.5,
            "macd": 1.2,
        }
        signal = await adapter.generate_trading_signal("AAPL", market_data)
        print(f"Signal: {json.dumps(signal, indent=2)}")
    else:
        print("Ollama not connected - testing heuristic fallback")
        market_data = {"price": 192.50, "volume": 3500000, "change_percent": 1.25, "rsi": 42.3}
        signal = await adapter.generate_trading_signal("AAPL", market_data)
        print(f"Fallback signal: {json.dumps(signal, indent=2)}")

    await adapter.close()
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(test())
