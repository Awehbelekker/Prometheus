import requests

try:
    # Try to get the list of routes from the running server
    # We'll use a custom endpoint to return the routes
    response = requests.get('http://localhost:8000/api/system/health', timeout=5)
    print(f"Server is running: {response.status_code}")
    
    # Now let's try to access the revolutionary/performance endpoint
    print("\nTrying to access /api/revolutionary/performance:")
    try:
        response = requests.get('http://localhost:8000/api/revolutionary/performance', timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Try to access the agents performance history endpoint
    print("\nTrying to access /api/agents/test123/performance-history:")
    try:
        response = requests.get('http://localhost:8000/api/agents/test123/performance-history?time_range=24h', timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Try to access the agents logs endpoint
    print("\nTrying to access /api/agents/test123/logs:")
    try:
        response = requests.get('http://localhost:8000/api/agents/test123/logs?limit=10', timeout=5)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Error: {e}")

except Exception as e:
    print(f"Server is not running or error occurred: {e}")

