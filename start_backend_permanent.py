#!/usr/bin/env python3
"""
PROMETHEUS Backend Server - Permanent Startup Script
This script ensures the backend server starts correctly
"""

import os
import sys
import time
import subprocess
import socket
import requests
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def kill_process_on_port(port):
    """Kill process using specified port"""
    import psutil
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"Killing process on port {port}: PID {proc.info['pid']}")
                    proc.kill()
                    proc.wait(timeout=5)
                    time.sleep(2)
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def check_port_free(port):
    """Check if port is free"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def main():
    print("="*60)
    print("PROMETHEUS Backend Server Startup")
    print("="*60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Kill existing processes on port 8000
    if not check_port_free(8000):
        print("Killing existing process on port 8000...")
        kill_process_on_port(8000)
        time.sleep(3)
    
    # Start backend server
    print("Starting backend server on port 8000...")
    if os.name == 'nt':  # Windows
        proc = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'unified_production_server:app',
             '--host', '0.0.0.0', '--port', '8000', '--workers', '1'],
            cwd=os.getcwd(),
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:  # Unix
        proc = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'unified_production_server:app',
             '--host', '0.0.0.0', '--port', '8000', '--workers', '1'],
            cwd=os.getcwd()
        )
    
    print(f"Backend server started (PID: {proc.pid})")
    print("Waiting for server to initialize...")
    
    # Wait and check health
    max_attempts = 20
    healthy = False
    
    for attempt in range(max_attempts):
        time.sleep(2)
        try:
            response = requests.get('http://127.0.0.1:8000/health', timeout=3)
            if response.status_code == 200:
                print("✅ Backend server is healthy and responding!")
                healthy = True
                break
        except:
            print(f"Attempt {attempt + 1}/{max_attempts} - Waiting for server...")
    
    if not healthy:
        print("⚠️ Backend server started but health check failed. Check logs for errors.")
    
    print("="*60)
    print("Backend server startup complete")
    print("="*60)
    
    # Keep process running
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    main()
