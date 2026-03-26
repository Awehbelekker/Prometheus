#!/usr/bin/env python3
"""
Start Backend Server - Windows Optimized
Uses single worker mode for Windows compatibility
"""

import os
import sys
import subprocess
from pathlib import Path

def start_backend_windows():
    """Start backend server optimized for Windows"""
    print("=" * 80)
    print("STARTING PROMETHEUS BACKEND SERVER (Windows Optimized)")
    print("=" * 80)
    print()
    
    server_file = Path("unified_production_server.py")
    if not server_file.exists():
        print("[ERROR] unified_production_server.py not found")
        return False
    
    # Set Windows-friendly environment variables
    os.environ['WORKERS'] = '1'  # Single worker for Windows
    os.environ['RELOAD'] = 'false'
    os.environ['HOST'] = '0.0.0.0'
    os.environ['PORT'] = '8000'
    
    print("Configuration:")
    print("  Workers: 1 (Windows-compatible)")
    print("  Port: 8000")
    print("  Host: 0.0.0.0")
    print()
    print("Starting server...")
    print()
    
    # Start in external terminal
    try:
        if sys.platform == "win32":
            # Use uvicorn directly with single worker
            cmd = [
                "cmd", "/k",
                "python", "-m", "uvicorn",
                "unified_production_server:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--workers", "1",  # Single worker for Windows
                "--log-level", "info"
            ]
            
            subprocess.Popen(
                cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print("[OK] Backend server starting in new terminal window")
            print()
            print("Server will be available at:")
            print("  API: http://localhost:8000")
            print("  Docs: http://localhost:8000/docs")
            print()
            print("NOTE: Using single worker mode for Windows compatibility")
            print("      This is normal and works perfectly fine")
            return True
        else:
            # Linux/Mac
            subprocess.Popen(
                [sys.executable, "-m", "uvicorn",
                 "unified_production_server:app",
                 "--host", "0.0.0.0",
                 "--port", "8000",
                 "--workers", "1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("[OK] Backend server started")
            return True
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return False

if __name__ == "__main__":
    start_backend_windows()

