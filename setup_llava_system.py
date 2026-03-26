"""
LLaVA Visual AI Setup Script
Sets up LLaVA in Ollama for chart analysis
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed"""
    print("\n[1/5] Checking Ollama installation...")
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[OK] Ollama installed: {result.stdout.strip()}")
            return True
        return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("[ERROR] Ollama not found!")
        print("\nPlease install Ollama:")
        print("  Windows: https://ollama.ai/download/windows")
        print("  After installation, restart this script")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    print("\n[2/5] Checking if Ollama is running...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            print("[OK] Ollama service is running")
            return True
        return False
    except requests.RequestException:
        print("[ERROR] Ollama service not running!")
        print("\nStart Ollama:")
        print("  Windows: Ollama should auto-start, or run 'ollama serve'")
        return False

def check_llava_model():
    """Check if LLaVA model is already downloaded"""
    print("\n[3/5] Checking for LLaVA model...")
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if 'llava' in model['name'].lower():
                    print(f"[OK] LLaVA model found: {model['name']}")
                    return True, model['name']
        return False, None
    except Exception as e:
        print(f"[ERROR] Could not check models: {e}")
        return False, None

def download_llava():
    """Download LLaVA model"""
    print("\n[4/5] Downloading LLaVA 7B model...")
    print("This will download ~4GB - may take 10-30 minutes depending on connection")
    print("\nStarting download...")
    
    try:
        # Use subprocess to show real-time output
        process = subprocess.Popen(
            ['ollama', 'pull', 'llava:7b'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("\n[OK] LLaVA model downloaded successfully!")
            return True
        else:
            print(f"\n[ERROR] Download failed with code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        return False

def test_llava():
    """Test LLaVA with a simple query"""
    print("\n[5/5] Testing LLaVA...")
    try:
        # Create a simple test (without image for now)
        payload = {
            "model": "llava:7b",
            "prompt": "Hello, are you ready to analyze trading charts?",
            "stream": False
        }
        
        response = requests.post(
            'http://localhost:11434/api/generate',
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("[OK] LLaVA is responding!")
            print(f"Test response: {result.get('response', '')[:100]}...")
            return True
        else:
            print(f"[ERROR] Test failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

def install_chart_libraries():
    """Install required chart generation libraries"""
    print("\n[BONUS] Installing chart generation libraries...")
    libraries = ['matplotlib', 'mplfinance', 'pandas', 'numpy']
    
    try:
        for lib in libraries:
            print(f"Installing {lib}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', lib], 
                         check=True, capture_output=True)
        print("[OK] Chart libraries installed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[WARNING] Some libraries failed to install: {e}")
        return False

def main():
    """Main setup routine"""
    print("="*70)
    print("LLAVA VISUAL AI SETUP FOR PROMETHEUS")
    print("="*70)
    
    # Step 1: Check Ollama
    if not check_ollama_installed():
        print("\n[FAILED] Please install Ollama first")
        input("Press Enter to exit...")
        return False
    
    # Step 2: Check Ollama running
    if not check_ollama_running():
        print("\n[FAILED] Please start Ollama service")
        input("Press Enter to exit...")
        return False
    
    # Step 3: Check if LLaVA already exists
    has_llava, model_name = check_llava_model()
    
    # Step 4: Download if needed
    if not has_llava:
        confirm = input("\nDownload LLaVA 7B model (~4GB)? (y/n): ")
        if confirm.lower() == 'y':
            if not download_llava():
                print("\n[FAILED] Could not download LLaVA")
                input("Press Enter to exit...")
                return False
        else:
            print("\n[SKIPPED] LLaVA download cancelled")
            return False
    
    # Step 5: Test LLaVA
    if not test_llava():
        print("\n[WARNING] LLaVA test failed, but model may still work")
    
    # Bonus: Install chart libraries
    install_chart_libraries()
    
    print("\n" + "="*70)
    print("LLAVA SETUP COMPLETE!")
    print("="*70)
    print("\nLLaVA Visual AI is ready for:")
    print("  - Chart pattern recognition")
    print("  - Support/Resistance detection")
    print("  - Trend analysis")
    print("  - Candlestick patterns")
    print("\nNext steps:")
    print("  1. Generate charts: python generate_historical_charts.py")
    print("  2. Train on history: python train_llava_historical.py")
    print("  3. Test analysis: python test_visual_analysis.py")
    print("="*70)
    
    input("\nPress Enter to exit...")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Setup failed: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
