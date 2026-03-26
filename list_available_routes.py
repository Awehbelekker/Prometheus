"""
List all available routes from the running server
"""
import requests

def main():
    print("="*80)
    print("  CHECKING AVAILABLE API ROUTES")
    print("="*80)
    
    # Try to get the OpenAPI schema
    try:
        response = requests.get("http://localhost:8000/openapi.json", timeout=10)
        if response.status_code == 200:
            data = response.json()
            paths = data.get('paths', {})
            
            print(f"\nFound {len(paths)} API endpoints:\n")
            
            # Group by prefix
            groups = {}
            for path in sorted(paths.keys()):
                parts = path.split('/')
                if len(parts) > 2:
                    prefix = f"/{parts[1]}"
                else:
                    prefix = "/"
                
                if prefix not in groups:
                    groups[prefix] = []
                groups[prefix].append(path)
            
            for prefix in sorted(groups.keys()):
                print(f"\n{prefix} ({len(groups[prefix])} endpoints):")
                for path in groups[prefix][:20]:  # Show first 20
                    methods = list(paths[path].keys())
                    print(f"  {', '.join(m.upper() for m in methods if m != 'parameters')}: {path}")
                if len(groups[prefix]) > 20:
                    print(f"  ... and {len(groups[prefix]) - 20} more")
            
            # Check for Revolutionary endpoints
            revolutionary_paths = [p for p in paths.keys() if 'revolutionary' in p.lower()]
            print(f"\n{'='*80}")
            print(f"Revolutionary Endpoints Found: {len(revolutionary_paths)}")
            print(f"{'='*80}")
            if revolutionary_paths:
                for path in revolutionary_paths:
                    print(f"  {path}")
            else:
                print("  [WARNING]️  No Revolutionary endpoints found in OpenAPI schema!")
                print("  This suggests the endpoints may not be registered.")
            
            # Check for broker endpoints
            broker_paths = [p for p in paths.keys() if 'broker' in p.lower() or 'alpaca' in p.lower() or 'ib' in p.lower()]
            print(f"\n{'='*80}")
            print(f"Broker Endpoints Found: {len(broker_paths)}")
            print(f"{'='*80}")
            if broker_paths:
                for path in broker_paths:
                    print(f"  {path}")
            else:
                print("  [WARNING]️  No Broker endpoints found in OpenAPI schema!")
        else:
            print(f"[ERROR] OpenAPI endpoint returned status {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Failed to get OpenAPI schema: {e}")
    
    # Try some known endpoints
    print(f"\n{'='*80}")
    print("Testing Known Endpoints:")
    print(f"{'='*80}")
    
    test_endpoints = [
        "/health",
        "/",
        "/api/health",
        "/docs",
        "/redoc",
    ]
    
    for endpoint in test_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            status = "[CHECK]" if response.status_code == 200 else f"[ERROR] {response.status_code}"
            print(f"  {status} {endpoint}")
        except Exception as e:
            print(f"  [ERROR] {endpoint} - {e}")

if __name__ == "__main__":
    main()

