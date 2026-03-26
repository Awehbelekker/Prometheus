#!/usr/bin/env python3
"""
Start Prometheus Backend/API Server
Starts the unified production server on port 8000
"""

import os
import sys
import subprocess
from pathlib import Path

def start_backend_server():
    """Start the unified production server"""
    print("=" * 80)
    print("STARTING PROMETHEUS BACKEND SERVER")
    print("=" * 80)
    print()
    
    server_file = Path("unified_production_server.py")
    if not server_file.exists():
        print("[ERROR] unified_production_server.py not found")
        return False
    
    print(f"[OK] Found server file: {server_file}")
    print()
    print("Starting server on port 8000...")
    print("API will be available at: http://localhost:8000")
    print("API Docs will be at: http://localhost:8000/docs")
    print()
    print("Starting in external terminal window...")
    print()
    
    # Start in external terminal
    try:
        if sys.platform == "win32":
            # Windows: Start in new cmd window
            subprocess.Popen(
                ["cmd", "/k", "python", str(server_file)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            print("[OK] Backend server starting in new terminal window")
            print()
            print("Check the new terminal window for server status")
            print("Server will be available at: http://localhost:8000")
            return True
        else:
            # Linux/Mac: Start in background
            subprocess.Popen(
                [sys.executable, str(server_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[OK] Backend server started in background")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False

if __name__ == "__main__":
    start_backend_server()

