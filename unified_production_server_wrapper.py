#!/usr/bin/env python3
"""
Wrapper for unified_production_server that ensures Revolutionary endpoints are registered
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Set the environment variable to ensure Revolutionary features are enabled
os.environ['ENABLE_REVOLUTIONARY_FEATURES'] = 'true'

print("=" * 80)
print("PROMETHEUS TRADING PLATFORM - WRAPPER STARTUP")
print("=" * 80)
print(f"ENABLE_REVOLUTIONARY_FEATURES = {os.getenv('ENABLE_REVOLUTIONARY_FEATURES')}")
print("=" * 80)

# Import the main server module
print("\n[1] Importing unified_production_server...")
import unified_production_server as ups

# Get the app object
app = ups.app

print(f"\n[2] Checking app object...")
print(f"    App title: {app.title}")
print(f"    App version: {app.version}")

# Count routes
all_routes = [route.path for route in app.routes if hasattr(route, 'path')]
revolutionary_routes = [r for r in all_routes if 'revolutionary' in r.lower()]

print(f"\n[3] Route statistics:")
print(f"    Total routes: {len(all_routes)}")
print(f"    Revolutionary routes: {len(revolutionary_routes)}")

if revolutionary_routes:
    print(f"\n[4] Revolutionary routes found:")
    for route in revolutionary_routes:
        print(f"    [CHECK] {route}")
else:
    print(f"\n[4] [ERROR] NO Revolutionary routes found!")
    print(f"    This indicates a problem with endpoint registration in the main module")

print("\n" + "=" * 80)
print("WRAPPER INITIALIZATION COMPLETE")
print("=" * 80)
print(f"\nServer ready to start with {len(all_routes)} total routes")
print(f"Revolutionary endpoints: {'ENABLED' if revolutionary_routes else 'DISABLED'}")
print("=" * 80)

