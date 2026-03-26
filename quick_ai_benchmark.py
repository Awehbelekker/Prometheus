#!/usr/bin/env python3
"""Quick AI Benchmark for PROMETHEUS"""
import requests
import time
import os
import sys

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

print('=' * 80)
print('  PROMETHEUS AI QUICK BENCHMARK')
print('=' * 80)

# Test 1: Ollama local models
print('\n[1] LOCAL AI MODELS (Ollama)')
print('-' * 40)
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    models = response.json().get('models', [])
    for m in models:
        size_gb = m.get('size', 0) / 1024 / 1024 / 1024
        name = m.get('name', 'unknown')
        print(f'  ✅ {name}: {size_gb:.1f} GB')
    print(f'  Total: {len(models)} models ready')
except Exception as e:
    print(f'  ❌ ERROR: {e}')

# Test 2: DeepSeek inference
print('\n[2] DEEPSEEK-R1 INFERENCE TEST')
print('-' * 40)
try:
    start = time.time()
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'deepseek-r1:8b',
            'prompt': 'AAPL is at 190. RSI is 72. MACD crossed bullish. Quick trading decision: BUY, SELL, or HOLD? Answer in one word.',
            'stream': False,
            'options': {'num_predict': 50}
        },
        timeout=120
    )
    elapsed = time.time() - start
    if response.status_code == 200:
        answer = response.json().get('response', '').strip()[:150]
        print(f'  ✅ Response: {answer}')
        print(f'  ✅ Time: {elapsed:.2f}s')
    else:
        print(f'  ❌ ERROR: HTTP {response.status_code}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')

# Test 3: Qwen inference
print('\n[3] QWEN2.5 INFERENCE TEST')
print('-' * 40)
try:
    start = time.time()
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'qwen2.5:7b',
            'prompt': 'SPY is down 2% today. VIX is at 25. What is the market sentiment? Answer briefly.',
            'stream': False,
            'options': {'num_predict': 50}
        },
        timeout=120
    )
    elapsed = time.time() - start
    if response.status_code == 200:
        answer = response.json().get('response', '').strip()[:150]
        print(f'  ✅ Response: {answer}')
        print(f'  ✅ Time: {elapsed:.2f}s')
    else:
        print(f'  ❌ ERROR: HTTP {response.status_code}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')

# Test 4: Knowledge base
print('\n[4] KNOWLEDGE BASE (ChromaDB)')
print('-' * 40)
try:
    import chromadb
    client = chromadb.PersistentClient(path='./knowledge_vectors')
    collection = client.get_collection('prometheus_knowledge')
    count = collection.count()
    print(f'  ✅ Vectors: {count}')
    
    # Quick query
    results = collection.query(query_texts=['momentum trading signals'], n_results=2)
    if results and results.get('documents'):
        print(f'  ✅ Query test: {len(results["documents"][0])} results returned')
        # Show source
        if results.get('metadatas'):
            sources = [m.get('source', 'unknown') for m in results['metadatas'][0]]
            print(f'  ✅ Sources: {sources}')
except Exception as e:
    print(f'  ❌ ERROR: {e}')

# Test 5: API Keys
print('\n[5] API KEYS STATUS')
print('-' * 40)
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv('OPENAI_API_KEY', '')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
    polygon_key = os.getenv('POLYGON_API_KEY', '')
    alpaca_key = os.getenv('ALPACA_API_KEY', '')
    
    if openai_key and len(openai_key) > 20:
        print(f'  ✅ OpenAI: Configured ({len(openai_key)} chars)')
    else:
        print('  ⚠️  OpenAI: Not configured')
        
    if anthropic_key and len(anthropic_key) > 20:
        print(f'  ✅ Anthropic: Configured ({len(anthropic_key)} chars)')
    else:
        print('  ⚠️  Anthropic: Not configured')
        
    if polygon_key and len(polygon_key) > 5:
        print(f'  ✅ Polygon.io: Configured')
    else:
        print('  ⚠️  Polygon.io: Not configured')
        
    if alpaca_key and len(alpaca_key) > 10:
        print(f'  ✅ Alpaca: Configured')
    else:
        print('  ⚠️  Alpaca: Not configured')
except Exception as e:
    print(f'  ❌ ERROR: {e}')

# Test 6: Broker connectivity
print('\n[6] BROKER CONNECTIVITY')
print('-' * 40)
try:
    from alpaca.trading.client import TradingClient
    from dotenv import load_dotenv
    load_dotenv()
    
    alpaca_key = os.getenv('ALPACA_API_KEY', '')
    alpaca_secret = os.getenv('ALPACA_SECRET_KEY', '')
    
    if alpaca_key and alpaca_secret:
        try:
            # Use paper=False for LIVE trading (paper credentials empty)
            client = TradingClient(alpaca_key, alpaca_secret, paper=False)
            account = client.get_account()
            equity = float(account.equity)
            print(f'  ✅ Alpaca LIVE: ${equity:,.2f} equity')
        except Exception as e:
            print(f'  ⚠️  Alpaca Paper: {str(e)[:50]}')
            
    # Check IB
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    ib_result = sock.connect_ex(('127.0.0.1', 4002))
    sock.close()
    if ib_result == 0:
        print(f'  ✅ Interactive Brokers: Gateway running on port 4002')
    else:
        print(f'  ⚠️  Interactive Brokers: Gateway not detected')
except Exception as e:
    print(f'  ❌ ERROR: {e}')

print('\n' + '=' * 80)
print('  AI BENCHMARK COMPLETE')
print('=' * 80)
