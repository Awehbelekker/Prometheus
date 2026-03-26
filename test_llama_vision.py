"""Test llama3.2-vision model for faster visual analysis"""

import time
import requests
import base64
from pathlib import Path

def test_vision():
    # Use llama3.2-vision instead of llava
    model = 'llama3.2-vision:latest'
    print(f'Using model: {model}')
    
    # Load image
    chart = list(Path('charts').glob('*.png'))[0]
    print(f'Chart: {chart.name}')
    
    with open(chart, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    # Simple prompt
    prompt = 'Analyze this stock chart. What patterns do you see? Is the trend bullish or bearish?'
    
    print(f'Calling {model}...')
    start = time.time()
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': model,
                'prompt': prompt,
                'images': [img_b64],
                'stream': False
            },
            timeout=120
        )
        elapsed = time.time() - start
        
        if response.ok:
            result = response.json()
            print('')
            print(f'Time: {elapsed:.1f} seconds')
            resp_text = result.get('response', 'No response')
            print(f'Response: {resp_text[:500]}...' if len(resp_text) > 500 else f'Response: {resp_text}')
        else:
            print(f'Error: {response.status_code}')
    except requests.exceptions.Timeout:
        print(f'Timeout after 120s')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_vision()
