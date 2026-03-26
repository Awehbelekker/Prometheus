#!/usr/bin/env python3
"""
🔮 RAGFlow Setup Script for PROMETHEUS Trading Platform
Sets up and configures RAGFlow knowledge retrieval system for Market Oracle Engine.

Prerequisites:
1. Docker must be running
2. Port 9380 must be available

Usage:
    python setup_ragflow.py --start     # Start RAGFlow container
    python setup_ragflow.py --stop      # Stop RAGFlow container
    python setup_ragflow.py --status    # Check RAGFlow status
    python setup_ragflow.py --populate  # Populate knowledge base
"""

import subprocess
import sys
import time
import argparse
import os
from pathlib import Path

RAGFLOW_CONTAINER_NAME = "prometheus_ragflow"
RAGFLOW_IMAGE = "infiniflow/ragflow:latest"
RAGFLOW_PORT = 9380

def check_docker_running() -> bool:
    """Check if Docker daemon is running"""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False

def start_ragflow():
    """Start RAGFlow Docker container"""
    print("🔮 Starting RAGFlow Knowledge Retrieval System...")
    
    if not check_docker_running():
        print("❌ Docker is not running. Please start Docker Desktop first.")
        return False
    
    # Check if container already exists
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={RAGFLOW_CONTAINER_NAME}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    
    if RAGFLOW_CONTAINER_NAME in result.stdout:
        # Container exists, start it
        print(f"   Starting existing container: {RAGFLOW_CONTAINER_NAME}")
        subprocess.run(["docker", "start", RAGFLOW_CONTAINER_NAME])
    else:
        # Create new container
        print(f"   Creating new RAGFlow container...")
        subprocess.run([
            "docker", "run", "-d",
            "--name", RAGFLOW_CONTAINER_NAME,
            "-p", f"{RAGFLOW_PORT}:9380",
            "-v", "ragflow_data:/ragflow/data",
            RAGFLOW_IMAGE
        ])
    
    # Wait for startup
    print("   Waiting for RAGFlow to be ready...")
    for i in range(30):
        if check_ragflow_status():
            print(f"✅ RAGFlow is ready at http://localhost:{RAGFLOW_PORT}")
            update_env_file()
            return True
        time.sleep(2)
        print(f"   Waiting... ({i+1}/30)")
    
    print("❌ RAGFlow failed to start within timeout")
    return False

def stop_ragflow():
    """Stop RAGFlow Docker container"""
    print("🛑 Stopping RAGFlow...")
    subprocess.run(["docker", "stop", RAGFLOW_CONTAINER_NAME])
    print("✅ RAGFlow stopped")

def check_ragflow_status() -> bool:
    """Check if RAGFlow is running and responsive"""
    try:
        import requests
        response = requests.get(f"http://localhost:{RAGFLOW_PORT}/api/v1/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False

def get_status():
    """Get RAGFlow status"""
    if not check_docker_running():
        print("❌ Docker is not running")
        return
    
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={RAGFLOW_CONTAINER_NAME}", "--format", "{{.Status}}"],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip():
        print(f"✅ RAGFlow container status: {result.stdout.strip()}")
        if check_ragflow_status():
            print(f"✅ RAGFlow API is responsive at http://localhost:{RAGFLOW_PORT}")
        else:
            print("⚠️ RAGFlow container running but API not responsive")
    else:
        print("❌ RAGFlow container is not running")

def update_env_file():
    """Update .env file with RAGFlow configuration"""
    env_path = Path(".env")
    if env_path.exists():
        content = env_path.read_text()
        if "RAGFLOW_ENABLED=true" not in content:
            # Update existing RAGFLOW entries or add new ones
            lines = content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("RAGFLOW_ENABLED="):
                    lines[i] = "RAGFLOW_ENABLED=true"
                    updated = True
            if not updated:
                lines.append("RAGFLOW_ENABLED=true")
            env_path.write_text('\n'.join(lines))
            print("✅ Updated .env with RAGFlow configuration")

def populate_knowledge_base():
    """Populate RAGFlow with market knowledge"""
    print("📚 Populating RAGFlow knowledge base...")
    
    if not check_ragflow_status():
        print("❌ RAGFlow is not running. Start it first with: python setup_ragflow.py --start")
        return
    
    # This would normally populate the knowledge base
    print("✅ Knowledge base populated (placeholder - actual implementation in Market Oracle Engine)")

def main():
    parser = argparse.ArgumentParser(description="RAGFlow Setup for PROMETHEUS")
    parser.add_argument("--start", action="store_true", help="Start RAGFlow")
    parser.add_argument("--stop", action="store_true", help="Stop RAGFlow")
    parser.add_argument("--status", action="store_true", help="Check status")
    parser.add_argument("--populate", action="store_true", help="Populate knowledge base")
    
    args = parser.parse_args()
    
    if args.start:
        start_ragflow()
    elif args.stop:
        stop_ragflow()
    elif args.status:
        get_status()
    elif args.populate:
        populate_knowledge_base()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

