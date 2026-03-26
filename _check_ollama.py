import urllib.request, json

# Check loaded models
r = urllib.request.urlopen('http://localhost:11434/api/ps', timeout=30)
d = json.loads(r.read())
models = d.get('models', [])
print(f"{len(models)} models loaded in RAM:")
for m in models:
    name = m.get('name', '?')
    size_gb = round(m.get('size', 0) / 1e9, 1)
    expires = m.get('expires_at', '?')
    print(f"  {name} - {size_gb} GB RAM - expires: {expires}")

if not models:
    print("  (none currently loaded - models load on demand)")
