#!/usr/bin/env python3
"""
Configure RAGFlow for Market Oracle Engine
Sets up RAGFlow integration for enhanced knowledge retrieval
"""

import os
import sys
from pathlib import Path

def check_ragflow_installation():
    """Check if RAGFlow is installed"""
    try:
        import ragflow
        return True, ragflow.__version__ if hasattr(ragflow, '__version__') else "installed"
    except ImportError:
        return False, None

def install_ragflow():
    """Install RAGFlow"""
    print("Installing RAGFlow...")
    import subprocess
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "ragflow"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[OK] RAGFlow installed successfully")
            return True
        else:
            print(f"[ERROR] Installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Installation error: {e}")
        return False

def configure_ragflow_env():
    """Configure RAGFlow environment variables"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("[WARNING] .env file not found")
        return False
    
    # Read current .env
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Check if RAGFlow config exists
    ragflow_vars = {
        'RAGFLOW_API_URL': 'http://localhost:9380',
        'RAGFLOW_API_KEY': '',
        'RAGFLOW_ENABLED': 'true'
    }
    
    updated = False
    existing_vars = {line.split('=')[0].strip(): line for line in lines if '=' in line}
    
    # Add missing variables
    new_lines = []
    for line in lines:
        new_lines.append(line)
        # Add RAGFlow vars after last env var
        if '=' in line and line.strip() and not line.strip().startswith('#'):
            var_name = line.split('=')[0].strip()
            if var_name in existing_vars and var_name not in ragflow_vars:
                # Add RAGFlow vars after this line
                for rf_var, rf_value in ragflow_vars.items():
                    if rf_var not in existing_vars:
                        new_lines.append(f"{rf_var}={rf_value}\n")
                        updated = True
                        print(f"[OK] Added {rf_var} to .env")
                break
    
    if updated:
        with open(env_file, 'w') as f:
            f.writelines(new_lines)
        print("[OK] RAGFlow configuration added to .env")
        return True
    else:
        print("[INFO] RAGFlow variables already configured")
        return False

def main():
    """Main configuration"""
    print("=" * 80)
    print("CONFIGURING RAGFLOW FOR MARKET ORACLE")
    print("=" * 80)
    print()
    
    # Check installation
    print("Step 1: Checking RAGFlow installation...")
    installed, version = check_ragflow_installation()
    
    if installed:
        print(f"[OK] RAGFlow is installed (version: {version})")
    else:
        print("[WARNING] RAGFlow is not installed")
        print("[INFO] Attempting to install RAGFlow...")
        if not install_ragflow():
            print("[WARNING] Failed to install RAGFlow automatically")
            print("You can install manually with: pip install ragflow")
            print("Note: Market Oracle will work without RAGFlow but with limited functionality")
            print("      The system will use enhanced oracle without knowledge retrieval")
            # Continue anyway - system works without RAGFlow
    
    print()
    
    # Configure environment
    print("Step 2: Configuring environment variables...")
    configure_ragflow_env()
    
    print()
    print("=" * 80)
    print("RAGFLOW CONFIGURATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Set RAGFLOW_API_KEY in .env if using cloud RAGFlow")
    print("2. Or start local RAGFlow server: ragflow start")
    print("3. Update RAGFLOW_API_URL if using different endpoint")
    print()

if __name__ == "__main__":
    main()

