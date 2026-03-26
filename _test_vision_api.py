"""Quick test of Ollama vision API with llava:7b."""
import base64, json, urllib.request, io, time
from PIL import Image

img = Image.new('RGB', (10, 10), 'white')
buf = io.BytesIO()
img.save(buf, format='PNG')
b64 = base64.b64encode(buf.getvalue()).decode()

payload = json.dumps({
    'model': 'llava:7b',
    'prompt': 'What do you see in this image?',
    'images': [b64],
    'stream': False,
    'options': {'num_predict': 30}
}).encode()

req = urllib.request.Request(
    'http://localhost:11434/api/generate',
    data=payload,
    headers={'Content-Type': 'application/json'}
)

print('Sending test image to llava:7b (cold start may take 60-120s)...')
t = time.time()
resp = urllib.request.urlopen(req, timeout=180)
data = json.loads(resp.read().decode())
elapsed = time.time() - t
print(f"Response in {elapsed:.1f}s:")
print(data.get("response", "NONE")[:300])
