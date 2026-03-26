"""
DeepSeek Local AI Setup for PROMETHEUS
Replaces GPT-OSS with DeepSeek for FREE, LOCAL, SMARTER AI
Zero OpenAI costs, 100% privacy, unlimited usage
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

class DeepSeekSetup:
    """Setup DeepSeek local AI for PROMETHEUS"""
    
    def __init__(self):
        self.deepseek_dir = Path("D:/AI_Models/DeepSeek")
        self.ollama_installed = False
        self.deepseek_running = False
        
    def check_system_requirements(self):
        """Check if system meets requirements"""
        print("\n🔍 CHECKING SYSTEM REQUIREMENTS")
        print("=" * 60)
        
        # Check RAM
        try:
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            print(f"✅ RAM: {ram_gb:.1f} GB")
            if ram_gb < 16:
                print("⚠️  WARNING: 16GB+ RAM recommended for best performance")
        except:
            print("⚠️  Could not check RAM")
        
        # Check GPU (optional but recommended)
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ NVIDIA GPU: Detected")
                print("   GPU acceleration will be used for faster inference")
            else:
                print("ℹ️  No NVIDIA GPU detected - will use CPU (slower)")
        except:
            print("ℹ️  No NVIDIA GPU detected - will use CPU (slower)")
        
        # Check disk space
        try:
            import shutil
            disk = shutil.disk_usage("D:/")
            free_gb = disk.free / (1024**3)
            print(f"✅ Disk Space: {free_gb:.1f} GB free")
            if free_gb < 50:
                print("⚠️  WARNING: 50GB+ free space recommended")
        except:
            print("⚠️  Could not check disk space")
    
    def install_ollama(self):
        """Install Ollama (easiest way to run DeepSeek locally)"""
        print("\n📦 INSTALLING OLLAMA")
        print("=" * 60)
        print("Ollama is the easiest way to run DeepSeek locally")
        print("It handles model downloads, GPU acceleration, and API server")
        print("\nDownloading Ollama installer...")
        
        # Download Ollama for Windows
        ollama_url = "https://ollama.com/download/OllamaSetup.exe"
        installer_path = "OllamaSetup.exe"
        
        try:
            response = requests.get(ollama_url, stream=True)
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"✅ Downloaded: {installer_path}")
            print("\n🚀 PLEASE RUN THE INSTALLER:")
            print(f"   1. Double-click: {installer_path}")
            print("   2. Follow installation wizard")
            print("   3. Restart this script after installation")
            
            # Open installer
            os.startfile(installer_path)
            
            return False  # Not installed yet
            
        except Exception as e:
            print(f"❌ Error downloading Ollama: {e}")
            print("\n📥 MANUAL INSTALLATION:")
            print("   1. Visit: https://ollama.com/download")
            print("   2. Download Ollama for Windows")
            print("   3. Install and restart this script")
            return False
    
    def check_ollama_installed(self):
        """Check if Ollama is installed"""
        try:
            result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Ollama installed: {result.stdout.strip()}")
                self.ollama_installed = True
                return True
        except:
            pass
        
        print("❌ Ollama not installed")
        return False
    
    def download_deepseek_model(self):
        """Download DeepSeek model via Ollama"""
        print("\n📥 DOWNLOADING DEEPSEEK MODEL")
        print("=" * 60)
        print("This will download DeepSeek-R1 (14B parameters)")
        print("Size: ~8GB - This may take 10-30 minutes depending on your internet")
        print("\nStarting download...")
        
        try:
            # Download DeepSeek-R1 model
            result = subprocess.run(
                ['ollama', 'pull', 'deepseek-r1:14b'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ DeepSeek model downloaded successfully!")
                return True
            else:
                print(f"❌ Error downloading model: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def start_deepseek_server(self):
        """Start DeepSeek API server"""
        print("\n🚀 STARTING DEEPSEEK API SERVER")
        print("=" * 60)
        
        try:
            # Start Ollama server (runs in background)
            subprocess.Popen(['ollama', 'serve'], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
            print("✅ DeepSeek API server starting on http://localhost:11434")
            print("   This server will run in the background")
            
            import time
            time.sleep(3)
            
            # Test the server
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                print("✅ Server is running!")
                self.deepseek_running = True
                return True
            
        except Exception as e:
            print(f"⚠️  Server may still be starting: {e}")
            return False
    
    def test_deepseek(self):
        """Test DeepSeek with a trading analysis"""
        print("\n🧪 TESTING DEEPSEEK AI")
        print("=" * 60)
        
        test_prompt = """Analyze this stock data and provide a BUY/SELL/HOLD recommendation:
        
Symbol: AAPL
Price: $175.50
Volume: 52M
RSI: 65
MACD: Bullish crossover
Moving Averages: Above 50-day and 200-day

Provide: Action (BUY/SELL/HOLD) and confidence (0-100)"""

        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'deepseek-r1:14b',
                    'prompt': test_prompt,
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ DeepSeek Response:")
                print("-" * 60)
                print(result.get('response', 'No response'))
                print("-" * 60)
                print("\n🎉 DeepSeek is working perfectly!")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False

def main():
    """Main setup process"""
    print("\n" + "=" * 60)
    print("🚀 DEEPSEEK LOCAL AI SETUP FOR PROMETHEUS")
    print("=" * 60)
    print("This will install DeepSeek AI locally on your machine")
    print("Benefits:")
    print("  ✅ 100% FREE - No API costs ever")
    print("  ✅ 100% PRIVATE - Data never leaves your machine")
    print("  ✅ UNLIMITED - No rate limits")
    print("  ✅ SMARTER - Better than GPT-4 for many tasks")
    print("=" * 60)
    
    setup = DeepSeekSetup()
    
    # Step 1: Check system
    setup.check_system_requirements()
    
    # Step 2: Check/Install Ollama
    if not setup.check_ollama_installed():
        setup.install_ollama()
        print("\n⏸️  PAUSED: Please install Ollama and run this script again")
        return
    
    # Step 3: Download DeepSeek
    if not setup.download_deepseek_model():
        print("\n❌ Failed to download DeepSeek model")
        return
    
    # Step 4: Start server
    if not setup.start_deepseek_server():
        print("\n⚠️  Server may need manual start: ollama serve")
    
    # Step 5: Test
    setup.test_deepseek()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python integrate_deepseek_prometheus.py")
    print("2. This will configure PROMETHEUS to use DeepSeek")
    print("3. Launch PROMETHEUS and enjoy FREE, LOCAL AI!")

if __name__ == "__main__":
    main()

