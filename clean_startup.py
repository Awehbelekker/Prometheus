#!/usr/bin/env python3
"""
🚀 PROMETHEUS TRADING PLATFORM - CLEAN STARTUP
Comprehensive cleanup and startup script
"""

import subprocess
import time
import os
import sys
import psutil
import webbrowser
from pathlib import Path

from gpu_detector import get_preferred_runtime_python

def print_header():
    """Print startup header"""
    print("🚀 PROMETHEUS TRADING PLATFORM - CLEAN STARTUP")
    print("=" * 60)
    print()

def kill_processes_by_name(process_names):
    """Kill processes by name"""
    killed = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if any(name.lower() in proc.info['name'].lower() for name in process_names):
                proc.kill()
                killed.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return killed

def kill_processes_on_ports(ports):
    """Kill processes using specific ports"""
    killed = []
    for port in ports:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    proc.kill()
                    killed.append(f"Port {port}: {proc.name()} (PID: {conn.pid})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
    return killed

def is_port_free(port):
    """Check if a port is free"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            return False
    return True

def wait_for_port_free(port, timeout=10):
    """Wait for a port to become free"""
    for _ in range(timeout):
        if is_port_free(port):
            return True
        time.sleep(1)
    return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend Server on port 8000...")
    
    project_dir = Path(__file__).parent
    python_executable = get_preferred_runtime_python() or sys.executable
    cmd = [
        python_executable, "-m", "uvicorn", 
        "unified_production_server:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ]
    
    # Start in new window
    if os.name == 'nt':  # Windows
        backend_command = subprocess.list2cmdline(cmd)
        subprocess.Popen(
            f'start "PROMETHEUS Backend" cmd /k "cd /d {project_dir} && {backend_command}"',
            shell=True
        )
    else:  # Unix-like
        subprocess.Popen(cmd, cwd=project_dir)

def start_frontend():
    """Start the frontend server"""
    print("🎯 Starting Frontend Server on port 3000...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Set PORT environment variable to force port 3000
    env = os.environ.copy()
    env['PORT'] = '3000'
    
    if os.name == 'nt':  # Windows
        subprocess.Popen(
            f'start "PROMETHEUS Frontend" cmd /k "cd /d {frontend_dir} && set PORT=3000 && npm start"',
            shell=True,
            env=env
        )
    else:  # Unix-like
        subprocess.Popen(['npm', 'start'], cwd=frontend_dir, env=env)

def main():
    """Main startup function"""
    print_header()
    
    # Step 1: Kill existing processes
    print("🧹 STEP 1: Killing existing processes...")
    print()
    
    # Kill by process name
    process_names = ['python', 'pythonw', 'node', 'uvicorn']
    killed_by_name = kill_processes_by_name(process_names)
    
    if killed_by_name:
        print("Killed processes by name:")
        for proc in killed_by_name:
            print(f"  [CHECK] {proc}")
    
    # Kill by port
    ports = [3000, 3001, 3002, 8000, 8001]
    killed_by_port = kill_processes_on_ports(ports)
    
    if killed_by_port:
        print("Killed processes by port:")
        for proc in killed_by_port:
            print(f"  [CHECK] {proc}")
    
    if not killed_by_name and not killed_by_port:
        print("[CHECK] No processes needed to be killed")
    
    print()
    
    # Step 2: Wait for cleanup
    print("⏳ STEP 2: Waiting for cleanup to complete...")
    time.sleep(3)
    print()
    
    # Step 3: Verify ports are free
    print("🔍 STEP 3: Verifying ports are available...")
    
    if wait_for_port_free(8000, 5):
        print("[CHECK] Port 8000 is available")
    else:
        print("[WARNING]️ Port 8000 still in use, but continuing...")
    
    if wait_for_port_free(3000, 5):
        print("[CHECK] Port 3000 is available")
    else:
        print("[WARNING]️ Port 3000 still in use, but continuing...")
    
    print()
    
    # Step 4: Start backend
    start_backend()
    print("⏳ Waiting 8 seconds for backend to initialize...")
    time.sleep(8)
    
    # Step 5: Start frontend
    start_frontend()
    print("⏳ Waiting 10 seconds for frontend to initialize...")
    time.sleep(10)
    
    # Step 6: Show URLs and open browser
    print()
    print("[CHECK] SERVERS STARTED!")
    print()
    print("📍 PROMETHEUS TRADING PLATFORM URLS:")
    print("🌐 Backend API: http://localhost:8000")
    print("🎯 Frontend: http://localhost:3000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("👑 Admin Panel: http://localhost:3000/admin")
    print("📊 Paper Trading: http://localhost:3000/paper-trading")
    print("💎 Investor Dashboard: http://localhost:3000/investor")
    print()
    
    # Open browser windows
    print("🌐 Opening browser windows...")
    try:
        webbrowser.open("http://localhost:8000/health")
        time.sleep(2)
        webbrowser.open("http://localhost:3000")
    except Exception as e:
        print(f"Could not open browser: {e}")
    
    print()
    print("🎉 PROMETHEUS TRADING PLATFORM IS LIVE!")
    print()
    print("[CHECK] Backend Health Check: http://localhost:8000/health")
    print("[CHECK] Frontend Application: http://localhost:3000")
    print("[CHECK] Admin Panel: http://localhost:3000/admin")
    print()
    print("Press Enter to exit (servers will continue running)...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Startup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Startup failed: {e}")
        sys.exit(1)
