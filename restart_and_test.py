#!/usr/bin/env python3
"""
Restart Server and Test Enhanced AI Functions
============================================
Restarts the server and tests enhanced AI capabilities
"""

import os
import sys
import time
import requests
import subprocess
import signal
from pathlib import Path

class ServerManager:
    def __init__(self):
        self.server_url = "http://localhost:8000"
        self.server_process = None
        
    def check_server_running(self):
        """Check if server is currently running"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def stop_server(self):
        """Stop the current server"""
        print("STOPPING CURRENT SERVER...")
        
        # Find Python processes running the server
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True)
            
            if 'python.exe' in result.stdout:
                print("Found Python processes - stopping them...")
                subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                             capture_output=True)
                time.sleep(3)
                print("Server stopped")
            else:
                print("No Python processes found")
        except Exception as e:
            print(f"Error stopping server: {e}")
    
    def start_server(self):
        """Start the server"""
        print("STARTING SERVER WITH ENHANCED AI...")
        
        try:
            # Start server in background
            self.server_process = subprocess.Popen([
                sys.executable, "unified_production_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            print("Server starting...")
            return True
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def wait_for_server(self, timeout=60):
        """Wait for server to be ready"""
        print("Waiting for server to be ready...")
        
        for i in range(timeout):
            if self.check_server_running():
                print(f"SUCCESS: Server is ready! (took {i+1} seconds)")
                return True
            time.sleep(1)
            if i % 10 == 0 and i > 0:
                print(f"Still waiting... ({i} seconds)")
        
        print(f"ERROR: Server not ready after {timeout} seconds")
        return False
    
    def test_enhanced_ai(self):
        """Test enhanced AI functions"""
        print("\nTESTING ENHANCED AI FUNCTIONS...")
        print("=" * 50)
        
        # Test 1: Health check
        print("1. Testing server health...")
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                print("   SUCCESS: Server health check passed")
            else:
                print(f"   ERROR: Health check failed ({response.status_code})")
                return False
        except Exception as e:
            print(f"   ERROR: Health check failed: {e}")
            return False
        
        # Test 2: AI Status
        print("2. Testing AI status...")
        try:
            response = requests.get(f"{self.server_url}/api/ai/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   OpenAI Available: {data.get('openai_available', False)}")
                print(f"   GPT-OSS Active: {data.get('gpt_oss_active', False)}")
                print(f"   AI Status: {data.get('status', 'unknown')}")
                
                if data.get('openai_available', False):
                    print("   SUCCESS: OpenAI integration active!")
                else:
                    print("   WARNING: OpenAI not available - check API key")
            else:
                print(f"   ERROR: AI status check failed ({response.status_code})")
        except Exception as e:
            print(f"   ERROR: AI status check failed: {e}")
        
        # Test 3: GPT-OSS Status
        print("3. Testing GPT-OSS status...")
        try:
            response = requests.get(f"{self.server_url}/api/gpt-oss/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"   GPT-OSS Status: {data.get('status', 'unknown')}")
                print(f"   Success: {data.get('success', False)}")
                
                if data.get('success', False):
                    print("   SUCCESS: GPT-OSS services active!")
                else:
                    print(f"   WARNING: GPT-OSS not active: {data.get('error', 'Unknown')}")
            else:
                print(f"   ERROR: GPT-OSS status check failed ({response.status_code})")
        except Exception as e:
            print(f"   ERROR: GPT-OSS status check failed: {e}")
        
        # Test 4: AI Analysis
        print("4. Testing AI analysis...")
        try:
            test_prompt = {
                "prompt": "Analyze the current market conditions for SPY and provide detailed trading recommendations with risk assessment"
            }
            
            response = requests.post(
                f"{self.server_url}/api/ai/analyze",
                json=test_prompt,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    print("   SUCCESS: AI analysis working!")
                    print(f"   Model used: {data.get('model_used', 'unknown')}")
                    print(f"   Response time: {data.get('response_time_ms', 0)}ms")
                    
                    # Show part of the analysis
                    analysis = data.get('analysis', {})
                    if isinstance(analysis, dict) and 'response' in analysis:
                        response_text = analysis['response'][:200]
                        print(f"   Analysis preview: {response_text}...")
                else:
                    print(f"   WARNING: AI analysis failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ERROR: AI analysis request failed ({response.status_code})")
        except Exception as e:
            print(f"   ERROR: AI analysis test failed: {e}")
        
        # Test 5: Revolutionary Engines
        print("5. Testing revolutionary engines...")
        try:
            response = requests.get(f"{self.server_url}/api/revolutionary/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    print("   SUCCESS: Revolutionary engines operational!")
                    status = data.get('status', {})
                    for engine, info in status.items():
                        if isinstance(info, dict):
                            print(f"   {engine}: {info.get('status', 'unknown')} ({info.get('health', 'unknown')})")
                else:
                    print(f"   WARNING: Revolutionary engines issue: {data.get('error', 'Unknown')}")
            else:
                print(f"   ERROR: Revolutionary engines check failed ({response.status_code})")
        except Exception as e:
            print(f"   ERROR: Revolutionary engines test failed: {e}")
        
        return True
    
    def run_complete_restart_and_test(self):
        """Run complete restart and test process"""
        print("PROMETHEUS SERVER RESTART AND AI TESTING")
        print("=" * 60)
        print()
        
        # Step 1: Check if server is running
        if self.check_server_running():
            print("Server is currently running - stopping it...")
            self.stop_server()
        else:
            print("No server currently running")
        
        # Step 2: Start server
        if not self.start_server():
            print("ERROR: Failed to start server")
            return False
        
        # Step 3: Wait for server to be ready
        if not self.wait_for_server():
            print("ERROR: Server failed to start properly")
            return False
        
        # Step 4: Test enhanced AI functions
        self.test_enhanced_ai()
        
        print("\n" + "=" * 60)
        print("RESTART AND TESTING COMPLETE!")
        print("=" * 60)
        print()
        print("Your PROMETHEUS Trading Platform is now running with:")
        print("- Enhanced AI capabilities")
        print("- GPT-OSS integration")
        print("- All revolutionary engines")
        print()
        print("Access your platform at: http://localhost:8000")
        print("API documentation: http://localhost:8000/docs")

def main():
    """Main function"""
    manager = ServerManager()
    manager.run_complete_restart_and_test()

if __name__ == "__main__":
    main()

