"""
Query the running server to see what routes are actually registered
"""
import requests
import json

print("="*80)
print("  QUERYING RUNNING SERVER FOR REGISTERED ROUTES")
print("="*80)

try:
    # Get the OpenAPI schema from the running server
    response = requests.get("http://localhost:8000/openapi.json", timeout=10)
    
    if response.status_code == 200:
        schema = response.json()
        paths = schema.get('paths', {})
        
        print(f"\nTotal routes in running server: {len(paths)}")
        
        # Check for Revolutionary routes
        revolutionary_routes = [p for p in paths.keys() if 'revolutionary' in p.lower()]
        
        print(f"Revolutionary routes found: {len(revolutionary_routes)}")
        
        if revolutionary_routes:
            print("\nRevolutionary Routes in RUNNING server:")
            for path in sorted(revolutionary_routes):
                methods = list(paths[path].keys())
                print(f"  {', '.join(m.upper() for m in methods if m != 'parameters')}: {path}")
        else:
            print("\nWARNING: NO Revolutionary routes found in running server!")
            print("This confirms the routes are NOT being registered at runtime.")
            
            # Show some sample routes to confirm we're getting valid data
            print("\nSample routes from running server:")
            for path in sorted(paths.keys())[:20]:
                print(f"  {path}")
    else:
        print(f"ERROR: Server returned status {response.status_code}")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)

