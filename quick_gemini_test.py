#!/usr/bin/env python3
"""Quick test of Claude Vision API"""

import os
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 50)
print("Testing Claude Vision API")
print("=" * 50)

api_key = os.getenv('ANTHROPIC_API_KEY')
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in .env")
    exit(1)

print(f"API Key: {api_key[:15]}...{api_key[-4:]}")

# Get first chart
charts = list(Path('charts').glob('*.png'))
if not charts:
    print("ERROR: No charts found")
    exit(1)

chart = charts[0]
print(f"Test chart: {chart.name}")
print(f"Chart size: {chart.stat().st_size / 1024:.1f} KB")

# Load image
print("\nLoading image...")
with open(chart, 'rb') as f:
    img_data = base64.b64encode(f.read()).decode()

# Call Claude
print("Calling Claude Vision API...")

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01"
}

payload = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 100,
    "messages": [{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": img_data
                }
            },
            {
                "type": "text",
                "text": "Look at this stock chart. Is the overall trend UP, DOWN, or SIDEWAYS? Also identify any chart patterns you see. Be brief."
            }
        ]
    }]
}

try:
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=payload,
        timeout=60
    )

    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        text = result['content'][0]['text']
        print(f"\nClaude says:\n{text.strip()}")
        print("\n" + "=" * 50)
        print("SUCCESS! Claude Vision API is working!")
        print("=" * 50)
        print("\nYou can now run: python CLOUD_VISION_TRAINING.py")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")

