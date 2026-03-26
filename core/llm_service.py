"""
Multi-Provider LLM Service for MASS Framework
Provides unified interface for OpenAI, Anthropic, and local LLMs
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Optional, AsyncIterator, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import tiktoken

# Setup logging first
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced imports with proper AI config loading
try:
    from config.ai_config import ai_config_manager, AIProvider, ModelConfig
    logger.info("[CHECK] AI configuration loaded successfully")

    # Log available providers for debugging
    available_providers = ai_config_manager.get_available_providers()
    if AIProvider.MOCK not in available_providers:
        logger.info(f"🤖 Real AI providers available: {[p.value for p in available_providers]}")
    else:
        logger.warning("[WARNING]️ Only mock AI provider available - check API keys")

except ImportError as e:
    # Create fallback classes if ai_config is missing
    from enum import Enum
    from typing import Dict, Optional

    class AIProvider(Enum):
        OPENAI = "openai"
        ANTHROPIC = "anthropic"
        MOCK = "mock"

    class ModelConfig:
        def __init__(self, name="", provider=AIProvider.MOCK, max_tokens=1000,
                     context_window=1000, cost_per_1k_tokens=0.0, supports_functions=False):
            self.name = name
            self.provider = provider
            self.max_tokens = max_tokens
            self.context_window = context_window
            self.cost_per_1k_tokens = cost_per_1k_tokens
            self.supports_functions = supports_functions

    class AIConfigManager:
        def __init__(self):
            self.config = type('Config', (), {
                'openai_api_key': '',
                'anthropic_api_key': '',
                'chat_model': 'gpt-3.5-turbo',
                'code_generation_model': 'gpt-4',
                'analysis_model': 'gpt-4',
                'models': {}
            })()

        def get_available_providers(self):
            return [AIProvider.MOCK]

        def get_model_config(self, model_name):
            return None

    ai_config_manager = AIConfigManager()
    logger.error(f"[ERROR] AI config import failed: {e}")
    logger.warning("Using fallback configuration - AI intelligence will be limited")

@dataclass
class AIMessage:
    """Standardized AI message format"""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = None

@dataclass
class AIResponse:
    """Standardized AI response format"""
    content: str
    model: str
    provider: str
    tokens_used: int
    cost_estimate: float
    response_time: float
    metadata: Dict[str, Any] = None

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AIResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI API provider with enhanced error handling"""

    def __init__(self):
        api_key = ai_config_manager.config.openai_api_key
        if not api_key or not api_key.startswith("sk-"):
            raise ValueError("Invalid or missing OpenAI API key")

        self.client = AsyncOpenAI(api_key=api_key)
        self.encoding = tiktoken.get_encoding("cl100k_base")
        logger.info(f"[CHECK] OpenAI provider initialized with key: {api_key[:12]}...{api_key[-4:]}")
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.encoding.encode(text))
        except:
            # Fallback estimation
            return len(text.split()) * 1.3
    
    def _messages_to_openai_format(self, messages: List[AIMessage]) -> List[Dict[str, str]]:
        """Convert AIMessage format to OpenAI format"""
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AIResponse:
        """Generate response using OpenAI API"""
        start_time = time.time()
        
        try:
            openai_messages = self._messages_to_openai_format(messages)
            
            response = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000),
                **{k: v for k, v in kwargs.items() 
                   if k in ['top_p', 'frequency_penalty', 'presence_penalty', 'functions', 'function_call']}
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Calculate cost
            model_config = ai_config_manager.get_model_config(model)
            cost_estimate = (tokens_used / 1000) * (model_config.cost_per_1k_tokens if model_config else 0.002)
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=content,
                model=model,
                provider="openai",
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                response_time=response_time,
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    async def generate_stream(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response using OpenAI API"""
        try:
            openai_messages = self._messages_to_openai_format(messages)
            
            stream = await self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 2000),
                stream=True,
                **{k: v for k, v in kwargs.items() 
                   if k in ['top_p', 'frequency_penalty', 'presence_penalty']}
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {str(e)}")
            raise

class AnthropicProvider(LLMProvider):
    """Anthropic API provider"""
    
    def __init__(self):
        try:
            from anthropic import AsyncAnthropic as _AsyncAnthropic
        except ImportError:
            raise ImportError("anthropic package not installed: pip install anthropic")
        self.client = _AsyncAnthropic(
            api_key=ai_config_manager.config.anthropic_api_key
        )
    
    def _count_tokens_estimate(self, text: str) -> int:
        """Estimate token count for Anthropic (rough approximation)"""
        return len(text.split()) * 1.3
    
    def _messages_to_anthropic_format(self, messages: List[AIMessage]) -> tuple:
        """Convert AIMessage format to Anthropic format"""
        system_message = ""
        conversation = []
        
        for msg in messages:
            if msg.role == "system":
                system_message += msg.content + "\n"
            else:
                conversation.append({"role": msg.role, "content": msg.content})
        
        return system_message.strip(), conversation
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AIResponse:
        """Generate response using Anthropic API"""
        start_time = time.time()
        
        try:
            system_message, conversation = self._messages_to_anthropic_format(messages)
            
            request_params = {
                "model": model,
                "messages": conversation,
                "max_tokens": kwargs.get('max_tokens', 2000),
                "temperature": kwargs.get('temperature', 0.7),
            }
            
            if system_message:
                request_params["system"] = system_message
            
            response = await self.client.messages.create(**request_params)
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            # Calculate cost
            model_config = ai_config_manager.get_model_config(model)
            cost_estimate = (tokens_used / 1000) * (model_config.cost_per_1k_tokens if model_config else 0.003)
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=content,
                model=model,
                provider="anthropic",
                tokens_used=tokens_used,
                cost_estimate=cost_estimate,
                response_time=response_time,
                metadata={
                    "stop_reason": response.stop_reason,
                    "response_id": response.id
                }
            )
            
        except Exception as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise
    
    async def generate_stream(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming response using Anthropic API"""
        try:
            system_message, conversation = self._messages_to_anthropic_format(messages)
            
            request_params = {
                "model": model,
                "messages": conversation,
                "max_tokens": kwargs.get('max_tokens', 2000),
                "temperature": kwargs.get('temperature', 0.7),
                "stream": True,
            }
            
            if system_message:
                request_params["system"] = system_message
            
            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {str(e)}")
            raise

class GPTOSSProvider(LLMProvider):
    """GPT-OSS Local AI Provider - PRIORITY PROVIDER"""

    def __init__(self):
        self.endpoint = ai_config_manager.config.gpt_oss_endpoint
        logger.info(f"[CHECK] GPT-OSS provider initialized with endpoint: {self.endpoint}")

    async def generate_response(self, messages: List[AIMessage], model: str = "gpt_oss_20b", **kwargs) -> AIResponse:
        """Generate response using local GPT-OSS models"""
        try:
            import requests

            prompt = self._convert_messages_to_prompt(messages)

            if "120b" in model.lower():
                endpoint = self.endpoint.replace("5000", "5001")
            else:
                endpoint = self.endpoint

            payload = {
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 2000),
                "temperature": kwargs.get("temperature", 0.7),
                "model": model
            }

            start_time = time.time()
            response = requests.post(f"{endpoint}/generate", json=payload, timeout=30)
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                content = data.get("response", data.get("text", ""))

                return AIResponse(
                    content=content,
                    model=model,
                    provider="gpt_oss",
                    tokens_used=len(content.split()),
                    cost_estimate=0.0,
                    response_time=response_time
                )
            else:
                error_msg = f"GPT-OSS API error: {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            error_msg = f"GPT-OSS provider error: {str(e)}"
            logger.error(error_msg)
            raise

    async def generate_stream(self, messages: List[AIMessage], model: str = "gpt_oss_20b", **kwargs) -> AsyncIterator[str]:
        """Generate streaming response from GPT-OSS (falls back to non-streaming)"""
        try:
            response = await self.generate_response(messages, model, **kwargs)
            yield response.content
        except Exception as e:
            logger.error(f"GPT-OSS streaming error: {str(e)}")
            raise

    def _convert_messages_to_prompt(self, messages: List[AIMessage]) -> str:
        """Convert messages to a single prompt for GPT-OSS"""
        prompt_parts = []
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")

        prompt_parts.append("Assistant:")  # Prompt for response
        return "\n\n".join(prompt_parts)

class MockProvider(LLMProvider):
    """Mock provider for testing"""

    def __init__(self):
        self.call_count = 0
    
    async def generate_response(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AIResponse:
        """Generate a mock response"""
        self.call_count += 1
        
        # Check if the request wants JSON (based on message content)
        user_content = ""
        for msg in messages:
            if msg.role == "user":
                user_content = msg.content.lower()
                break
          # Generate appropriate mock response based on request type
        if "json" in user_content and "recommend" in user_content and "agent" in user_content:
            content = """[
    {
        "agent_id": "code_generator",
        "confidence_score": 0.8,
        "reasoning": "Best for code generation tasks",
        "estimated_contribution": "Generate Python code based on requirements"
    },
    {
        "agent_id": "documentation_agent", 
        "confidence_score": 0.6,
        "reasoning": "Helpful for documentation",
        "estimated_contribution": "Create comprehensive documentation"
    },
    {
        "agent_id": "testing_agent",
        "confidence_score": 0.7,
        "reasoning": "Generate unit tests",
        "estimated_contribution": "Create test cases for generated code"
    }
]"""
        elif "json" in user_content and "task" in user_content and "analyze" in user_content:
            content = """{
    "category": "analysis",
    "complexity": "moderate",    "estimated_time_minutes": 30,    "required_agents": ["code_analyzer"],
    "optional_agents": ["documentation_agent"],
    "risk_level": "medium",
    "success_probability": 0.7,
    "reasoning": "Mock task analysis",
    "resource_requirements": {
        "compute_intensive": false,
        "requires_external_apis": false,
        "needs_human_review": true
    }
}"""
        elif "json" in user_content and "workflow" in user_content:
            content = """{
    "workflow": {
        "name": "Development Workflow",
        "description": "Mock workflow for development",
        "steps": [
            {
                "id": "step1",
                "name": "Analysis",
                "agent": "code_analyzer",
                "estimated_time": 10
            },
            {
                "id": "step2", 
                "name": "Implementation",
                "agent": "code_generator",
                "estimated_time": 20
            }
        ]
    }
}"""
        else:
            content = "This is a mock response for testing"
        
        return AIResponse(
            content=content,
            model=model,
            provider="mock",
            tokens_used=10,
            cost_estimate=0.001,
            response_time=0.1,
            metadata={"mock": True, "call_count": self.call_count}
        )
    
    async def generate_stream(
        self, 
        messages: List[AIMessage], 
        model: str,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a mock streaming response"""
        mock_chunks = ["This ", "is ", "a ", "mock ", "streaming ", "response"]
        for chunk in mock_chunks:
            yield chunk

class LLMService:
    """Main LLM service that coordinates multiple providers"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
        self.usage_stats = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "provider_usage": {}        }
    
    def _initialize_providers(self):
        """Initialize available providers based on configuration"""
        available_providers = ai_config_manager.get_available_providers()
        
        # PRIORITY 1: Initialize GPT-OSS provider first
        if AIProvider.GPT_OSS in available_providers:
            try:
                self.providers[AIProvider.GPT_OSS] = GPTOSSProvider()
                logger.info("🚀 GPT-OSS provider initialized (PRIORITY)")
            except Exception as e:
                logger.warning(f"Failed to initialize GPT-OSS provider: {e}")

        if AIProvider.OPENAI in available_providers:
            try:
                self.providers[AIProvider.OPENAI] = OpenAIProvider()
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI provider: {e}")

        if AIProvider.ANTHROPIC in available_providers:
            try:
                self.providers[AIProvider.ANTHROPIC] = AnthropicProvider()
                logger.info("Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic provider: {e}")
        
        # If no providers are available, use mock providers as fallback
        if not self.providers:
            if ai_config_manager.is_real_provider_available():
                logger.error("🚨 CRITICAL: Real AI providers configured but ALL failed to initialize!")
                logger.error("🚨 System is falling back to MockProvider - AI decisions will be TEMPLATE responses!")
                logger.error("🚨 Check: OPENAI_API_KEY, ANTHROPIC_API_KEY in .env file")
            else:
                logger.error("🚨 CRITICAL: No real AI providers configured - ALL AI will be MOCK/FAKE!")
                logger.error("🚨 Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env for real intelligence")
            self.providers[AIProvider.OPENAI] = MockProvider()
            self.providers[AIProvider.ANTHROPIC] = MockProvider()
            self._using_mock = True
        else:
            logger.info(f"✅ Initialized {len(self.providers)} REAL AI provider(s): {list(self.providers.keys())}")
            self._using_mock = False
    
    def _get_provider_for_model(self, model: str) -> LLMProvider:
        """Get the appropriate provider for a model"""
        model_config = ai_config_manager.get_model_config(model)
        if not model_config:
            raise ValueError(f"Model '{model}' not found in configuration")
        
        provider = self.providers.get(model_config.provider)
        if not provider:
            raise ValueError(f"Provider '{model_config.provider}' not available")
        
        return provider
    
    async def generate_response(
        self,
        messages: Union[List[AIMessage], List[Dict[str, str]], str],
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate a response using the specified model"""
        
        # Convert input to standard format
        if isinstance(messages, str):
            messages = [AIMessage(role="user", content=messages)]
        elif isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], dict):
                messages = [AIMessage(role=msg["role"], content=msg["content"]) for msg in messages]
        
        # Use default model if not specified
        if not model:
            model = ai_config_manager.config.code_generation_model
        
        # Get provider and generate response
        provider = self._get_provider_for_model(model)
        response = await provider.generate_response(messages, model, **kwargs)
        
        # Update usage statistics
        self._update_usage_stats(response)
        
        return response
    
    async def generate_stream(
        self,
        messages: Union[List[AIMessage], List[Dict[str, str]], str],
        model: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate a streaming response using the specified model"""
        
        # Convert input to standard format
        if isinstance(messages, str):
            messages = [AIMessage(role="user", content=messages)]
        elif isinstance(messages, list) and len(messages) > 0:
            if isinstance(messages[0], dict):
                messages = [AIMessage(role=msg["role"], content=msg["content"]) for msg in messages]
        
        # Use default model if not specified
        if not model:
            model = ai_config_manager.config.chat_model
        
        # Get provider and generate streaming response
        provider = self._get_provider_for_model(model)
        async for chunk in provider.generate_stream(messages, model, **kwargs):
            yield chunk
    
    def _update_usage_stats(self, response: AIResponse):
        """Update usage statistics"""
        self.usage_stats["total_requests"] += 1
        self.usage_stats["total_tokens"] += response.tokens_used
        self.usage_stats["total_cost"] += response.cost_estimate
        
        if response.provider not in self.usage_stats["provider_usage"]:
            self.usage_stats["provider_usage"][response.provider] = {
                "requests": 0,
                "tokens": 0,
                "cost": 0.0
            }
        
        provider_stats = self.usage_stats["provider_usage"][response.provider]
        provider_stats["requests"] += 1
        provider_stats["tokens"] += response.tokens_used
        provider_stats["cost"] += response.cost_estimate
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats.copy()
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        return list(ai_config_manager.config.models.keys())
    
    def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        model_config = ai_config_manager.get_model_config(model)
        if not model_config:
            return None
        
        return {
            "name": model_config.name,
            "provider": model_config.provider.value,
            "max_tokens": model_config.max_tokens,
            "context_window": model_config.context_window,
            "cost_per_1k_tokens": model_config.cost_per_1k_tokens,
            "supports_functions": model_config.supports_functions
        }
    
    async def chat_completion(self, messages, model=None, **kwargs):
        """Compatibility method for tests and agent mocks. Calls generate_response and returns a simple object with 'content'."""
        response = await self.generate_response(messages, model=model, **kwargs)
        # Return a mock-like object with a 'content' attribute for test compatibility
        class Result:
            def __init__(self, content, usage=None):
                self.content = content
                self.usage = usage if usage is not None else getattr(response, 'usage', None)
        return Result(response.content if hasattr(response, 'content') else str(response), getattr(response, 'usage', None))

    async def _make_openai_request(self, *args, **kwargs):
        """Stub for OpenAI request, for test patching/mocking."""
        return None

# For backwards compatibility with tests that expect to patch OpenAI directly
try:
    from openai import OpenAI, AsyncOpenAI
    # Export these for tests that need to mock them
    __all__ = ['LLMService', 'AIMessage', 'AIResponse', 'OpenAI', 'AsyncOpenAI']
except ImportError:
    __all__ = ['LLMService', 'AIMessage', 'AIResponse']

# Global LLM service instance
llm_service = LLMService()
