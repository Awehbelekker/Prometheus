#!/usr/bin/env python3
"""
Diagnostic script to find exactly where server startup is failing
"""

import sys
import time
import traceback

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("PROMETHEUS SERVER STARTUP DIAGNOSTIC")
print("=" * 80)

# Step 1: Test basic imports
print("\n[STEP 1] Testing basic imports...")
try:
    import os
    print("  [OK] os")
    import asyncio
    print("  [OK] asyncio")
    import logging
    print("  [OK] logging")
    from datetime import datetime
    print("  [OK] datetime")
except Exception as e:
    print(f"  [ERROR] Basic imports failed: {e}")
    sys.exit(1)

# Step 2: Test FastAPI import
print("\n[STEP 2] Testing FastAPI import...")
try:
    from fastapi import FastAPI
    print("  [OK] FastAPI")
    from fastapi.middleware.cors import CORSMiddleware
    print("  [OK] CORSMiddleware")
except Exception as e:
    print(f"  [ERROR] FastAPI import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Step 3: Test uvicorn import
print("\n[STEP 3] Testing uvicorn import...")
try:
    import uvicorn
    print("  [OK] uvicorn")
except Exception as e:
    print(f"  [ERROR] uvicorn import failed: {e}")
    sys.exit(1)

# Step 4: Test importing unified_production_server (this is where it likely fails)
print("\n[STEP 4] Testing unified_production_server import...")
print("  This may take 30-60 seconds due to heavy dependencies...")
start_time = time.time()

try:
    print("  [4.1] Starting import...")
    import unified_production_server
    elapsed = time.time() - start_time
    print(f"  [OK] unified_production_server imported in {elapsed:.1f} seconds")
    
    # Check if app exists
    if hasattr(unified_production_server, 'app'):
        print("  [OK] app object exists")
        app = unified_production_server.app
        print(f"  [OK] app type: {type(app)}")
    else:
        print("  [ERROR] app object NOT found")
        sys.exit(1)
        
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  [ERROR] Import failed after {elapsed:.1f} seconds")
    print(f"  Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

# Step 5: Try to start the server
print("\n[STEP 5] Attempting to start server...")
print("  Starting uvicorn on port 8000...")
print("  Press CTRL+C to stop")
print("=" * 80)

try:
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
except KeyboardInterrupt:
    print("\n\n[CHECK] Server stopped by user")
    sys.exit(0)
except Exception as e:
    print(f"\n\n[ERROR] Server startup failed: {e}")
    traceback.print_exc()
    sys.exit(1)

