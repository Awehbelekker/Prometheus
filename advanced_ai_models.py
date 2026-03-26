#!/usr/bin/env python3
"""
================================================================================
PROMETHEUS ADVANCED AI MODEL INTEGRATIONS
================================================================================

Integrates cutting-edge AI models for enhanced reasoning:
- Falcon H1R-7B (256K context window - ideal for documents)
- DeepSeek-R1 (latest version with chain-of-thought)
- Local Ollama models
- Cloud API fallbacks

================================================================================
"""

import os
import sys
import json
import requests
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    name: str
    provider: str  # ollama, openai, anthropic, huggingface
    model_id: str
    context_length: int
    supports_vision: bool = False
    supports_reasoning: bool = False
    endpoint: str = None
    api_key_env: str = None


class AdvancedAIModels:
    """
    Manages advanced AI models for PROMETHEUS.
    
    Features:
    - Auto-detection of available models
    - Dynamic model selection based on task
    - Context length optimization
    - Fallback chains
    """
    
    # Model registry with capabilities
    MODELS = {
        # Ollama Local Models
        "deepseek-r1:8b": ModelConfig(
            name="DeepSeek-R1 8B",
            provider="ollama",
            model_id="deepseek-r1:8b",
            context_length=32768,
            supports_reasoning=True
        ),
        "deepseek-r1:14b": ModelConfig(
            name="DeepSeek-R1 14B",
            provider="ollama",
            model_id="deepseek-r1:14b",
            context_length=65536,
            supports_reasoning=True
        ),
        "deepseek-r1:32b": ModelConfig(
            name="DeepSeek-R1 32B",
            provider="ollama",
            model_id="deepseek-r1:32b",
            context_length=65536,
            supports_reasoning=True
        ),
        "deepseek-r1:70b": ModelConfig(
            name="DeepSeek-R1 70B",
            provider="ollama",
            model_id="deepseek-r1:70b",
            context_length=65536,
            supports_reasoning=True
        ),
        "falcon-h1r:7b": ModelConfig(
            name="Falcon H1R 7B (256K)",
            provider="ollama",
            model_id="falcon-h1r:7b",
            context_length=262144,  # 256K context!
            supports_reasoning=True
        ),
        "qwen2.5:7b": ModelConfig(
            name="Qwen 2.5 7B",
            provider="ollama",
            model_id="qwen2.5:7b",
            context_length=32768,
            supports_reasoning=True
        ),
        "qwen2.5:14b": ModelConfig(
            name="Qwen 2.5 14B",
            provider="ollama",
            model_id="qwen2.5:14b",
            context_length=32768,
            supports_reasoning=True
        ),
        "llava:7b": ModelConfig(
            name="LLaVA 7B (Vision)",
            provider="ollama",
            model_id="llava:7b",
            context_length=4096,
            supports_vision=True
        ),
        "llava:13b": ModelConfig(
            name="LLaVA 13B (Vision)",
            provider="ollama",
            model_id="llava:13b",
            context_length=4096,
            supports_vision=True
        ),
        "minicpm-v:8b": ModelConfig(
            name="MiniCPM-V 8B (Vision)",
            provider="ollama",
            model_id="minicpm-v:8b",
            context_length=8192,
            supports_vision=True
        ),
        
        # GLM-4 Series (Finance-Optimized)
        "glm4:9b": ModelConfig(
            name="GLM-4 9B (Finance)",
            provider="ollama",
            model_id="glm4:9b",
            context_length=131072,  # 128K context
            supports_reasoning=True
        ),
        "glm4:latest": ModelConfig(
            name="GLM-4 Latest",
            provider="ollama",
            model_id="glm4:latest",
            context_length=131072,
            supports_reasoning=True
        ),
        "chatglm3:6b": ModelConfig(
            name="ChatGLM3 6B (Lightweight)",
            provider="ollama",
            model_id="chatglm3:6b",
            context_length=32768,
            supports_reasoning=True
        ),
        
        # Cloud Models
        "gpt-4o": ModelConfig(
            name="GPT-4o",
            provider="openai",
            model_id="gpt-4o",
            context_length=128000,
            supports_vision=True,
            supports_reasoning=True,
            api_key_env="OPENAI_API_KEY"
        ),
        "claude-3-opus": ModelConfig(
            name="Claude 3 Opus",
            provider="anthropic",
            model_id="claude-3-opus-20240229",
            context_length=200000,
            supports_vision=True,
            supports_reasoning=True,
            api_key_env="ANTHROPIC_API_KEY"
        ),
        "claude-3.5-sonnet": ModelConfig(
            name="Claude 3.5 Sonnet",
            provider="anthropic",
            model_id="claude-3-5-sonnet-20241022",
            context_length=200000,
            supports_vision=True,
            supports_reasoning=True,
            api_key_env="ANTHROPIC_API_KEY"
        ),
        "gemini-2.0-flash": ModelConfig(
            name="Gemini 2.0 Flash",
            provider="google",
            model_id="gemini-2.0-flash-exp",
            context_length=1000000,
            supports_vision=True,
            supports_reasoning=True,
            api_key_env="GEMINI_API_KEY"
        ),
        
        # GLM-4 Cloud (Zhipu AI - Finance Specialist)
        "glm-4-plus": ModelConfig(
            name="GLM-4-Plus (API)",
            provider="zhipu",
            model_id="glm-4-plus",
            context_length=131072,
            supports_vision=False,
            supports_reasoning=True,
            api_key_env="ZHIPUAI_API_KEY"
        ),
        "glm-4v-plus": ModelConfig(
            name="GLM-4V-Plus (Vision)",
            provider="zhipu",
            model_id="glm-4v-plus",
            context_length=8192,
            supports_vision=True,
            supports_reasoning=True,
            api_key_env="ZHIPUAI_API_KEY"
        ),
    }
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.available_models: Dict[str, ModelConfig] = {}
        self._detect_available_models()
    
    def _detect_available_models(self):
        """Detect all available models"""
        logger.info("Detecting available AI models...")
        
        # Check Ollama models
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_models = response.json().get('models', [])
                for model in ollama_models:
                    model_name = model['name']
                    # Match with our registry
                    for key, config in self.MODELS.items():
                        if config.provider == "ollama" and config.model_id in model_name:
                            self.available_models[key] = config
                            logger.info(f"  ✓ Ollama: {config.name}")
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
        
        # Check cloud APIs
        from dotenv import load_dotenv
        load_dotenv()
        
        for key, config in self.MODELS.items():
            if config.provider in ["openai", "anthropic", "google"]:
                if config.api_key_env and os.getenv(config.api_key_env):
                    self.available_models[key] = config
                    logger.info(f"  ✓ Cloud: {config.name}")
        
        logger.info(f"Total available models: {len(self.available_models)}")
    
    def get_best_model(self, task: str = "reasoning", 
                       min_context: int = 4096) -> Optional[ModelConfig]:
        """Get the best available model for a task"""
        
        candidates = []
        for key, config in self.available_models.items():
            if config.context_length >= min_context:
                if task == "vision" and config.supports_vision:
                    candidates.append(config)
                elif task == "reasoning" and config.supports_reasoning:
                    candidates.append(config)
                elif task == "long_context":
                    candidates.append(config)
                elif task == "general":
                    candidates.append(config)
        
        if not candidates:
            return None
        
        # Sort by capability
        if task == "long_context":
            candidates.sort(key=lambda x: x.context_length, reverse=True)
        else:
            # Prefer local models for cost
            candidates.sort(key=lambda x: (x.provider != "ollama", -x.context_length))
        
        return candidates[0]
    
    def call_model(self, model_key: str, prompt: str, 
                   system_prompt: str = None, images: List[str] = None,
                   max_tokens: int = 4096, temperature: float = 0.7) -> str:
        """Call a specific model"""
        
        if model_key not in self.available_models:
            raise ValueError(f"Model not available: {model_key}")
        
        config = self.available_models[model_key]
        
        if config.provider == "ollama":
            return self._call_ollama(config, prompt, system_prompt, images, max_tokens, temperature)
        elif config.provider == "openai":
            return self._call_openai(config, prompt, system_prompt, images, max_tokens, temperature)
        elif config.provider == "anthropic":
            return self._call_anthropic(config, prompt, system_prompt, images, max_tokens, temperature)
        elif config.provider == "google":
            return self._call_google(config, prompt, system_prompt, images, max_tokens, temperature)
        else:
            raise ValueError(f"Unknown provider: {config.provider}")
    
    def _call_ollama(self, config: ModelConfig, prompt: str,
                     system_prompt: str, images: List[str],
                     max_tokens: int, temperature: float) -> str:
        """Call Ollama model"""
        
        payload = {
            "model": config.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if images and config.supports_vision:
            payload["images"] = images
        
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"Ollama error: {response.text}")
    
    def _call_openai(self, config: ModelConfig, prompt: str,
                     system_prompt: str, images: List[str],
                     max_tokens: int, temperature: float) -> str:
        """Call OpenAI model"""
        import openai
        
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if images and config.supports_vision:
            content = [{"type": "text", "text": prompt}]
            for img in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img}"}
                })
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=config.model_id,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    def _call_anthropic(self, config: ModelConfig, prompt: str,
                        system_prompt: str, images: List[str],
                        max_tokens: int, temperature: float) -> str:
        """Call Anthropic model"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        content = []
        if images and config.supports_vision:
            for img in images:
                content.append({
                    "type": "image",
                    "source": {"type": "base64", "media_type": "image/png", "data": img}
                })
        content.append({"type": "text", "text": prompt})
        
        response = client.messages.create(
            model=config.model_id,
            max_tokens=max_tokens,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role": "user", "content": content}]
        )
        
        return response.content[0].text
    
    def _call_google(self, config: ModelConfig, prompt: str,
                     system_prompt: str, images: List[str],
                     max_tokens: int, temperature: float) -> str:
        """Call Google Gemini model"""
        import google.generativeai as genai
        
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(config.model_id)
        
        if system_prompt:
            prompt = f"{system_prompt}\n\n{prompt}"
        
        response = model.generate_content(prompt)
        return response.text
    
    def smart_call(self, prompt: str, task: str = "reasoning",
                   system_prompt: str = None, images: List[str] = None,
                   min_context: int = 4096) -> Optional[str]:
        """Automatically select best model and call it"""
        
        model = self.get_best_model(task, min_context)
        if not model:
            logger.error(f"No suitable model available for task: {task}")
            return None
        
        logger.info(f"Using model: {model.name} for {task}")
        
        try:
            return self.call_model(
                [k for k, v in self.available_models.items() if v == model][0],
                prompt, system_prompt, images
            )
        except Exception as e:
            logger.error(f"Model call failed: {e}")
            return None


class DeepSeekR1Reasoner:
    """
    Specialized reasoner using DeepSeek-R1's chain-of-thought capabilities.
    
    DeepSeek-R1 excels at:
    - Multi-step reasoning
    - Mathematical analysis
    - Code generation
    - Complex trading decisions
    """
    
    def __init__(self, models: AdvancedAIModels):
        self.models = models
        
        # Find best DeepSeek model
        self.model_key = None
        for key in ["deepseek-r1:70b", "deepseek-r1:32b", "deepseek-r1:14b", "deepseek-r1:8b"]:
            if key in models.available_models:
                self.model_key = key
                break
        
        if self.model_key:
            logger.info(f"DeepSeek Reasoner using: {self.model_key}")
        else:
            logger.warning("No DeepSeek-R1 model available")
    
    def analyze_trade(self, symbol: str, market_data: Dict[str, Any],
                      signals: Dict[str, Any]) -> Dict[str, Any]:
        """Deep analysis of a trading opportunity"""
        
        if not self.model_key:
            return {"error": "DeepSeek-R1 not available"}
        
        prompt = f"""Analyze this trading opportunity using step-by-step reasoning:

Symbol: {symbol}

Market Data:
- Price: ${market_data.get('price', 'N/A')}
- Change: {market_data.get('change_pct', 'N/A')}%
- Volume: {market_data.get('volume', 'N/A')}
- 20-day MA: ${market_data.get('ma_20', 'N/A')}
- 50-day MA: ${market_data.get('ma_50', 'N/A')}
- RSI: {market_data.get('rsi', 'N/A')}
- MACD: {market_data.get('macd', 'N/A')}

Current Signals:
{json.dumps(signals, indent=2)}

Please provide:
1. <thinking>Your step-by-step analysis</thinking>
2. Trade recommendation (BUY/SELL/HOLD)
3. Confidence level (0-100%)
4. Entry price suggestion
5. Stop loss level
6. Target price
7. Risk/reward ratio
8. Key risks to monitor
"""
        
        system = """You are an expert quantitative trader with deep knowledge of technical analysis, 
market microstructure, and risk management. Use chain-of-thought reasoning to analyze trades.
Always wrap your thinking process in <thinking></thinking> tags."""
        
        try:
            response = self.models.call_model(
                self.model_key, prompt, system,
                max_tokens=4096, temperature=0.3
            )
            
            # Parse response
            return {
                "symbol": symbol,
                "analysis": response,
                "model": self.model_key,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trade analysis failed: {e}")
            return {"error": str(e)}


class FalconLongContextAnalyzer:
    """
    Analyzer using Falcon H1R's massive 256K context window.
    
    Ideal for:
    - Processing entire trading books
    - Analyzing long market histories
    - Multi-document synthesis
    """
    
    def __init__(self, models: AdvancedAIModels):
        self.models = models
        
        # Check for Falcon or long-context alternatives
        self.model_key = None
        for key in ["falcon-h1r:7b", "gemini-2.0-flash", "claude-3-opus"]:
            if key in models.available_models:
                self.model_key = key
                break
        
        if self.model_key:
            config = models.available_models[self.model_key]
            logger.info(f"Long Context Analyzer using: {config.name} ({config.context_length:,} tokens)")
        else:
            logger.warning("No long-context model available")
    
    def analyze_document(self, document: str, query: str) -> str:
        """Analyze a long document with a query"""
        
        if not self.model_key:
            return "No long-context model available"
        
        prompt = f"""Analyze the following document and answer the query.

DOCUMENT:
{document}

QUERY: {query}

Provide a comprehensive answer based on the document content."""
        
        system = "You are an expert analyst. Extract and synthesize information from documents."
        
        try:
            return self.models.call_model(
                self.model_key, prompt, system,
                max_tokens=4096, temperature=0.3
            )
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return f"Error: {e}"
    
    def synthesize_knowledge(self, documents: List[Dict[str, str]], 
                             topic: str) -> str:
        """Synthesize knowledge from multiple documents"""
        
        if not self.model_key:
            return "No long-context model available"
        
        # Combine documents
        combined = ""
        for i, doc in enumerate(documents):
            combined += f"\n\n=== DOCUMENT {i+1}: {doc.get('title', 'Untitled')} ===\n"
            combined += doc.get('content', '')[:50000]  # Limit per doc
        
        prompt = f"""Synthesize knowledge from these documents about: {topic}

{combined}

Provide:
1. Key concepts and principles
2. Practical applications for trading
3. Connections between different sources
4. Actionable insights"""
        
        try:
            return self.models.call_model(
                self.model_key, prompt,
                system_prompt="You are a knowledge synthesizer for trading strategies.",
                max_tokens=8192, temperature=0.3
            )
        except Exception as e:
            return f"Error: {e}"


def pull_new_models():
    """Pull new AI models via Ollama"""
    
    models_to_pull = [
        "deepseek-r1:8b",      # Latest DeepSeek-R1 (INSTALLED)
        "qwen2.5:7b",          # Qwen 2.5 (INSTALLED)
        "llava:7b",            # Vision model (INSTALLED)
        "falcon3:7b",          # Falcon 3 (optional)
        "minicpm-v:8b",        # Better vision model (optional)
    ]
    
    print("\nPulling new AI models...")
    print("This may take a while depending on your internet speed.\n")
    
    for model in models_to_pull:
        print(f"Pulling {model}...")
        try:
            response = requests.post(
                "http://localhost:11434/api/pull",
                json={"name": model},
                stream=True,
                timeout=3600  # 1 hour timeout
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        status = data.get('status', '')
                        if 'pulling' in status or 'downloading' in status:
                            completed = data.get('completed', 0)
                            total = data.get('total', 0)
                            if total > 0:
                                pct = (completed / total) * 100
                                print(f"\r  {status}: {pct:.1f}%", end='', flush=True)
                        elif status == 'success':
                            print(f"\n  ✓ {model} pulled successfully")
                            break
            else:
                print(f"  ✗ Failed to pull {model}: {response.text}")
                
        except Exception as e:
            print(f"  ✗ Error pulling {model}: {e}")
    
    print("\nModel pull complete!")


def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("PROMETHEUS ADVANCED AI MODELS")
    print("="*70)
    
    # Initialize models
    models = AdvancedAIModels()
    
    print("\n[1] Available Models:")
    for key, config in models.available_models.items():
        print(f"    • {config.name}")
        print(f"      Context: {config.context_length:,} tokens")
        print(f"      Vision: {config.supports_vision}, Reasoning: {config.supports_reasoning}")
    
    # Show best models for each task
    print("\n[2] Best Models by Task:")
    tasks = ["reasoning", "vision", "long_context"]
    for task in tasks:
        best = models.get_best_model(task)
        if best:
            print(f"    {task}: {best.name} ({best.context_length:,} context)")
        else:
            print(f"    {task}: No suitable model available")
    
    # Initialize specialized analyzers
    print("\n[3] Specialized Analyzers:")
    
    deepseek_reasoner = DeepSeekR1Reasoner(models)
    if deepseek_reasoner.model_key:
        print(f"    ✓ DeepSeek-R1 Reasoner: {deepseek_reasoner.model_key}")
    
    falcon_analyzer = FalconLongContextAnalyzer(models)
    if falcon_analyzer.model_key:
        config = models.available_models[falcon_analyzer.model_key]
        print(f"    ✓ Long Context Analyzer: {config.name}")
    
    # Test a simple call
    print("\n[4] Testing Model Call...")
    best_model = models.get_best_model("reasoning")
    if best_model:
        try:
            response = models.smart_call(
                "What are the key principles of trend following in trading? Be brief.",
                task="reasoning"
            )
            if response:
                print(f"    Response preview: {response[:200]}...")
        except Exception as e:
            print(f"    Test failed: {e}")
    
    print("\n" + "="*70)
    print("AI MODELS READY")
    print("="*70)
    print("\nTo pull additional models, run:")
    print("  python advanced_ai_models.py --pull")
    print("\nUsage in code:")
    print("  models = AdvancedAIModels()")
    print("  response = models.smart_call('Your prompt', task='reasoning')")
    print("="*70)


if __name__ == "__main__":
    import sys
    if "--pull" in sys.argv:
        pull_new_models()
    else:
        main()
