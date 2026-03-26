"""
AI Configuration for Prometheus Trading Platform
Loads real API keys from environment variables and enables full AI intelligence
"""

import os
from enum import Enum
from dotenv import load_dotenv

class AIProvider(Enum):
    GPT_OSS = "gpt_oss"  # Local GPT-OSS models (PRIORITY)
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MOCK = "mock"

class ModelConfig:
    def __init__(self, name, provider, max_tokens, context_window, cost_per_1k_tokens, supports_functions=False):
        self.name = name
        self.provider = provider
        self.max_tokens = max_tokens
        self.context_window = context_window
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.supports_functions = supports_functions

class AIConfig:
    def __init__(self):
        # Load environment variables with proper error handling
        try:
            load_dotenv()
        except Exception as e:
            print(f"Warning: Could not load .env file: {e}")
            print("Continuing with system environment variables...")

        # Load API keys from environment
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")

        # GPT-OSS configuration (local models - PRIORITY)
        self.gpt_oss_enabled = os.getenv("GPT_OSS_ENABLED", "false").lower() == "true"
        self.gpt_oss_endpoint = os.getenv("GPT_OSS_API_ENDPOINT", "http://localhost:5000")
        
        # ThinkMesh configuration
        self.thinkmesh_enabled = os.getenv("THINKMESH_ENABLED", "false").lower() == "true"

        # Model configuration
        self.chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.code_generation_model = "gpt-4"
        self.analysis_model = "gpt-4"
        self.models = self._get_default_models()

    def _get_default_models(self):
        return {
            "gpt-3.5-turbo": ModelConfig(
                name="GPT-3.5 Turbo",
                provider=AIProvider.OPENAI,
                max_tokens=4096,
                context_window=16385,
                cost_per_1k_tokens=0.002,
                supports_functions=True
            ),
            "gpt-4": ModelConfig(
                name="GPT-4",
                provider=AIProvider.OPENAI,
                max_tokens=8192,
                context_window=32768,
                cost_per_1k_tokens=0.03,
                supports_functions=True
            ),
            "gpt-4o-mini": ModelConfig(
                name="GPT-4o Mini",
                provider=AIProvider.OPENAI,
                max_tokens=16384,
                context_window=128000,
                cost_per_1k_tokens=0.00015,
                supports_functions=True
            ),
            "gpt_oss_20b": ModelConfig(
                name="GPT-OSS 20B Local",
                provider=AIProvider.GPT_OSS,
                max_tokens=8192,
                context_window=32768,
                cost_per_1k_tokens=0.0,  # Free local model
                supports_functions=True
            ),
            "gpt_oss_120b": ModelConfig(
                name="GPT-OSS 120B Local",
                provider=AIProvider.GPT_OSS,
                max_tokens=8192,
                context_window=32768,
                cost_per_1k_tokens=0.0,  # Free local model
                supports_functions=True
            )
        }

class AIConfigManager:
    def __init__(self):
        self.config = AIConfig()

    def get_available_providers(self):
        """Dynamically detect ALL available AI providers"""
        providers = []

        # Check for GPT-OSS/Ollama (local models - no API costs)
        if self.config.gpt_oss_enabled:
            try:
                import requests
                ollama_url = self.config.gpt_oss_endpoint.replace('/health', '/api/tags')
                if not ollama_url.endswith('/api/tags'):
                    ollama_url = self.config.gpt_oss_endpoint.rstrip('/') + '/api/tags'

                response = requests.get(ollama_url, timeout=2)
                if response.status_code == 200:
                    providers.append(AIProvider.GPT_OSS)
                else:
                    health_url = self.config.gpt_oss_endpoint.rstrip('/') + '/health'
                    response = requests.get(health_url, timeout=2)
                    if response.status_code == 200:
                        providers.append(AIProvider.GPT_OSS)
            except:
                pass  # Local AI not available

        # Check for OpenAI API key (always check, not only when GPT-OSS unavailable)
        if self.config.openai_api_key and self.config.openai_api_key.strip():
            if self.config.openai_api_key.startswith("sk-"):
                providers.append(AIProvider.OPENAI)

        # Check for Anthropic API key (always check)
        if self.config.anthropic_api_key and self.config.anthropic_api_key.strip():
            if self.config.anthropic_api_key.startswith("sk-"):
                providers.append(AIProvider.ANTHROPIC)

        # Return real providers if available, otherwise fallback to mock
        if not providers:
            print("⚠️  CRITICAL: No real AI providers found! Check .env for OPENAI_API_KEY / ANTHROPIC_API_KEY")
        return providers if providers else [AIProvider.MOCK]

    def get_model_config(self, model_name):
        return self.config.models.get(model_name)

    def is_real_provider_available(self):
        """Check if any real AI provider is available"""
        return len([p for p in self.get_available_providers() if p != AIProvider.MOCK]) > 0

# Global instance
ai_config_manager = AIConfigManager()
