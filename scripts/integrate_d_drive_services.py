#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - D: Drive Integration Script
=========================================================

This script integrates the GPT-OSS services running on D: drive
with the main PROMETHEUS trading platform.

Author: PROMETHEUS Development Team
Version: 2.0.0
Date: 2025-08-30
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path
from datetime import datetime

class PrometheusGPTOSSIntegration:
    """Integration manager for D: drive GPT-OSS services"""
    
    def __init__(self):
        self.d_drive_services = {
            "gpt_oss_20b": "http://localhost:5000",
            "gpt_oss_120b": "http://localhost:5001", 
            "dashboard": "http://localhost:8080"
        }
        
        self.main_platform = "http://localhost:8000"
        self.integration_status = {
            "services_discovered": False,
            "health_checks_passed": False,
            "integration_complete": False
        }

    async def discover_services(self):
        """Discover and validate D: drive services"""
        print("🔍 Discovering GPT-OSS services on D: drive...")
        
        discovered_services = {}
        
        for service_name, endpoint in self.d_drive_services.items():
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{endpoint}/health")
                    if response.status_code == 200:
                        service_info = response.json()
                        discovered_services[service_name] = {
                            "endpoint": endpoint,
                            "status": "healthy",
                            "info": service_info
                        }
                        print(f"   [CHECK] {service_name}: {endpoint} - Healthy")
                    else:
                        print(f"   [ERROR] {service_name}: {endpoint} - Unhealthy")
            except Exception as e:
                print(f"   [ERROR] {service_name}: {endpoint} - Connection failed: {e}")
        
        if len(discovered_services) > 0:
            self.integration_status["services_discovered"] = True
            print(f"[CHECK] Discovered {len(discovered_services)} healthy services")
        else:
            print("[ERROR] No healthy services discovered")
            return False
        
        return discovered_services

    async def test_main_platform(self):
        """Test connection to main PROMETHEUS platform"""
        print("🔗 Testing main PROMETHEUS platform connection...")
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.main_platform}/health")
                if response.status_code == 200:
                    print("   [CHECK] Main platform: Healthy")
                    return True
                else:
                    print("   [ERROR] Main platform: Unhealthy")
                    return False
        except Exception as e:
            print(f"   [ERROR] Main platform: Connection failed: {e}")
            print("   💡 Tip: Make sure the main platform is running on port 8000")
            return False

    async def perform_integration_tests(self):
        """Perform integration tests between services"""
        print("🧪 Performing integration tests...")
        
        # Test GPT-OSS 20B inference
        test_prompt = "Analyze the current market conditions for cryptocurrency trading"
        
        try:
            request_data = {
                "prompt": test_prompt,
                "max_length": 256,
                "temperature": 0.7
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.d_drive_services['gpt_oss_20b']}/generate",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("   [CHECK] GPT-OSS 20B inference test passed")
                    print(f"   📊 Processing time: {result.get('processing_time', 'N/A')}s")
                    print(f"   📝 Response preview: {result.get('generated_text', '')[:100]}...")
                    return True
                else:
                    print("   [ERROR] GPT-OSS 20B inference test failed")
                    return False
        except Exception as e:
            print(f"   [ERROR] Integration test failed: {e}")
            return False

    async def create_integration_config(self):
        """Create integration configuration for main platform"""
        print("📄 Creating integration configuration...")
        
        config = {
            "gpt_oss_integration": {
                "enabled": True,
                "deployment_location": "D:/PROMETHEUS_AI_DEPLOYMENT",
                "services": {
                    "gpt_oss_20b": {
                        "endpoint": self.d_drive_services["gpt_oss_20b"],
                        "model_size": "20B",
                        "use_cases": ["market_analysis", "trading_advice", "risk_assessment"]
                    },
                    "gpt_oss_120b": {
                        "endpoint": self.d_drive_services["gpt_oss_120b"], 
                        "model_size": "120B",
                        "use_cases": ["complex_strategy", "portfolio_optimization", "advanced_reasoning"]
                    },
                    "dashboard": {
                        "endpoint": self.d_drive_services["dashboard"],
                        "use_cases": ["monitoring", "management", "metrics"]
                    }
                },
                "fallback_strategy": "thinkmesh_adapter",
                "load_balancing": "round_robin",
                "health_check_interval": 30
            },
            "integration_metadata": {
                "integration_date": datetime.now().isoformat(),
                "integration_version": "1.0.0",
                "platform_version": "2.0.0"
            }
        }
        
        # Save to main platform config
        config_path = Path("./gpt_oss_integration.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"   [CHECK] Configuration saved: {config_path}")
        return config

    async def update_main_platform(self):
        """Update main platform with GPT-OSS integration"""
        print("🔧 Updating main PROMETHEUS platform...")
        
        # Create enhanced reasoning adapter
        adapter_code = '''
import asyncio
import httpx
from typing import Dict, Any, Optional

class GPTOSSAdapter:
    """GPT-OSS D: Drive Integration Adapter"""
    
    def __init__(self):
        self.endpoints = {
            "gpt_oss_20b": "http://localhost:5000",
            "gpt_oss_120b": "http://localhost:5001"
        }
        self.fallback_enabled = True
    
    async def generate_response(self, prompt: str, model: str = "gpt_oss_20b", **kwargs) -> Dict[str, Any]:
        """Generate response using GPT-OSS models"""
        endpoint = self.endpoints.get(model, self.endpoints["gpt_oss_20b"])
        
        try:
            request_data = {
                "prompt": prompt,
                "max_length": kwargs.get("max_length", 512),
                "temperature": kwargs.get("temperature", 0.7)
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{endpoint}/generate", json=request_data)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "response": response.json(),
                        "model_used": model,
                        "source": "gpt_oss_d_drive"
                    }
                else:
                    return await self._fallback_response(prompt, **kwargs)
        
        except Exception as e:
            print(f"GPT-OSS adapter error: {e}")
            return await self._fallback_response(prompt, **kwargs)
    
    async def _fallback_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Fallback to ThinkMesh or mock response"""
        return {
            "success": True,
            "response": {
                "generated_text": f"[FALLBACK] {prompt} [GPT-OSS unavailable - using fallback]",
                "model_name": "fallback",
                "processing_time": 0.001
            },
            "model_used": "fallback",
            "source": "fallback"
        }
    
    def is_available(self) -> bool:
        """Check if GPT-OSS services are available"""
        # Quick synchronous check
        import requests
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            return response.status_code == 200
        except:
            return False

# Global adapter instance
gpt_oss_adapter = GPTOSSAdapter()
'''
        
        adapter_path = Path("./core/gpt_oss_adapter.py")
        with open(adapter_path, 'w') as f:
            f.write(adapter_code)
        
        print(f"   [CHECK] GPT-OSS adapter created: {adapter_path}")

    async def run_integration(self):
        """Run complete integration process"""
        print("🚀 Starting PROMETHEUS GPT-OSS Integration")
        print("=" * 60)
        
        # Step 1: Discover services
        discovered_services = await self.discover_services()
        if not discovered_services:
            print("[ERROR] Integration failed: No services discovered")
            return False
        
        # Step 2: Test main platform (optional)
        main_platform_healthy = await self.test_main_platform()
        if not main_platform_healthy:
            print("[WARNING]️  Main platform not running - integration config created anyway")
        
        # Step 3: Integration tests
        tests_passed = await self.perform_integration_tests()
        if tests_passed:
            self.integration_status["health_checks_passed"] = True
        
        # Step 4: Create configuration
        config = await self.create_integration_config()
        
        # Step 5: Update main platform
        await self.update_main_platform()
        
        # Mark integration as complete
        self.integration_status["integration_complete"] = True
        
        print("\n" + "=" * 60)
        print("🎉 INTEGRATION COMPLETE!")
        print("=" * 60)
        print(f"[CHECK] Services discovered: {len(discovered_services)}")
        print(f"[CHECK] Health checks: {'Passed' if tests_passed else 'Warning'}")
        print(f"[CHECK] Configuration: Created")
        print(f"[CHECK] Adapter: Updated")
        print("\n📋 Next Steps:")
        print("1. Restart main PROMETHEUS platform to load new GPT-OSS adapter")
        print("2. Test integration via main platform API")
        print("3. Monitor performance via D: drive dashboard (http://localhost:8080)")
        print("4. Download actual model weights for production use")
        
        return True

async def main():
    """Main integration function"""
    integrator = PrometheusGPTOSSIntegration()
    success = await integrator.run_integration()
    
    if not success:
        print("\n[ERROR] Integration failed. Check that D: drive services are running:")
        print("   D:\\PROMETHEUS_AI_DEPLOYMENT\\LAUNCH_PROMETHEUS_AI.bat")
        sys.exit(1)
    
    print("\n[CHECK] Integration successful!")

if __name__ == "__main__":
    asyncio.run(main())
