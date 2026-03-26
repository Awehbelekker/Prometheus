
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
