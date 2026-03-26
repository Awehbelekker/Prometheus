"""
DeepSeek AI Adapter for PROMETHEUS
Supports both LOCAL (Ollama) and CLOUD (DeepSeek API) inference

Cloud API: Fast, cheap ($0.14-0.42/M tokens), reliable
Local: Free but slow on CPU (15-35s per request)
"""

import os
import requests
import logging
import re
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class DeepSeekAdapter:
    """Adapter for DeepSeek AI with support for both local Ollama and cloud API"""

    def __init__(self, endpoint="http://localhost:11434", model="phi"):
        # Check if we should use DeepSeek Cloud API
        self.use_cloud_api = os.getenv('USE_DEEPSEEK_API', 'false').lower() == 'true'
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.cloud_endpoint = os.getenv('DEEPSEEK_API_ENDPOINT', 'https://api.deepseek.com')

        # Local Ollama settings
        self.local_endpoint = endpoint
        self.model = model

        # Stats tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.total_cost = 0.0
        self.timeout = 30 if self.use_cloud_api else 60  # Cloud is faster

        # Determine mode
        if self.use_cloud_api and self.api_key:
            self.mode = 'cloud'
            self.cloud_model = os.getenv('DEEPSEEK_MODEL', 'deepseek-reasoner')
            logger.info(f"🚀 DeepSeek Cloud API initialized: {self.cloud_model}")
            logger.info(f"   Endpoint: {self.cloud_endpoint}")
        else:
            self.mode = 'local'
            logger.info(f"🏠 DeepSeek Local (Ollama) initialized: {model}")
            logger.info(f"   Endpoint: {endpoint}")

    def _is_valid_response(self, text: str) -> bool:
        """Check if response is valid (not garbled)."""
        if not text or len(text) < 2:
            return False
        
        # DeepSeek-R1 specific: Extract final answer from thinking process
        if 'deepseek-r1' in self.model.lower():
            # DeepSeek-R1 format: <think>...</think> Final answer
            # Or: Thinking... ...done thinking. Final answer
            if '...done thinking.' in text:
                # Extract text after thinking phase
                parts = text.split('...done thinking.')
                if len(parts) > 1:
                    text = parts[-1].strip()
            elif '</think>' in text:
                parts = text.split('</think>')
                if len(parts) > 1:
                    text = parts[-1].strip()
        
        # Check for excessive special characters (garbled output)
        # Allow more special chars for short responses
        special_chars = re.findall(r'[^a-zA-Z0-9\s.,!?\'"=+\-*/():%]', text)
        special_ratio = len(special_chars) / max(len(text), 1)
        if special_ratio > 0.5:  # More than 50% unusual chars = garbled (increased tolerance)
            return False
        # Check for at least some readable content (words OR numbers)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        numbers = re.findall(r'\b\d+\b', text)
        # Valid if has at least 1 word OR has numbers (like "2 + 2 = 4")
        return len(words) >= 1 or len(numbers) >= 1

    def _clean_thinking_response(self, text: str) -> str:
        """Clean up DeepSeek-R1 thinking format from response."""
        if not text:
            return text

        # Remove thinking annotations - DeepSeek-R1 format
        if '...done thinking.' in text:
            parts = text.split('...done thinking.')
            text = parts[-1].strip() if len(parts) > 1 else text
        elif '</think>' in text:
            parts = text.split('</think>')
            text = parts[-1].strip() if len(parts) > 1 else text

        # Remove "Thinking..." prefix if present
        if text.startswith('Thinking...'):
            text = text.replace('Thinking...', '', 1).strip()

        # Remove <think> tags if present (without closing tag)
        if '<think>' in text and '</think>' not in text:
            text = re.sub(r'<think>.*', '', text, flags=re.DOTALL).strip()

        return text

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using DeepSeek (cloud API or local Ollama)."""
        if self.mode == 'cloud':
            return self._generate_cloud(prompt, max_tokens, temperature)
        else:
            return self._generate_local(prompt, max_tokens, temperature)

    def _generate_cloud(self, prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate response using DeepSeek Cloud API (OpenAI-compatible)."""
        try:
            self.total_requests += 1

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                'model': self.cloud_model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': max_tokens,
                'temperature': temperature,
                'stream': False
            }

            response = requests.post(
                f"{self.cloud_endpoint}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content']

                # Extract reasoning tokens cost
                usage = result.get('usage', {})
                input_tokens = usage.get('prompt_tokens', 0)
                output_tokens = usage.get('completion_tokens', 0)
                reasoning_tokens = usage.get('completion_tokens_details', {}).get('reasoning_tokens', 0)

                # Calculate cost: $0.14/M input (cache), $0.28/M input (miss), $0.42/M output
                # Using cache miss rate for conservative estimate
                cost = (input_tokens * 0.28 + output_tokens * 0.42) / 1_000_000
                self.total_cost += cost

                # Clean up DeepSeek-R1 thinking format if present
                response_text = self._clean_thinking_response(response_text)

                # Validate response
                if not self._is_valid_response(response_text):
                    logger.warning("DeepSeek API returned invalid response")
                    return {'success': False, 'error': 'Invalid response', 'needs_fallback': True}

                self.successful_requests += 1
                return {
                    'success': True,
                    'response': response_text,
                    'model': self.cloud_model,
                    'cost': cost,
                    'source': 'DeepSeek-R1 (Cloud API)',
                    'tokens_used': input_tokens + output_tokens,
                    'reasoning_tokens': reasoning_tokens
                }
            else:
                error_msg = response.json().get('error', {}).get('message', f'HTTP {response.status_code}')
                logger.error(f"DeepSeek API error: {error_msg}")
                return {'success': False, 'error': error_msg, 'needs_fallback': True}

        except requests.exceptions.Timeout:
            logger.warning(f"DeepSeek API timeout after {self.timeout}s")
            return {'success': False, 'error': 'Timeout', 'needs_fallback': True}
        except Exception as e:
            logger.error(f"DeepSeek API exception: {e}")
            return {'success': False, 'error': str(e), 'needs_fallback': True}

    def _generate_local(self, prompt: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Generate response using local Ollama."""
        try:
            self.total_requests += 1

            response = requests.post(
                f"{self.local_endpoint}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': temperature,
                        'num_predict': max_tokens
                    }
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                response_text = self._clean_thinking_response(response_text)

                if not self._is_valid_response(response_text):
                    logger.warning("DeepSeek local returned garbled response")
                    return {'success': False, 'error': 'Garbled response', 'needs_fallback': True}

                self.successful_requests += 1
                return {
                    'success': True,
                    'response': response_text,
                    'model': self.model,
                    'cost': 0.0,
                    'source': 'DeepSeek (Local Ollama)',
                    'tokens_used': result.get('eval_count', 0)
                }
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return {'success': False, 'error': f"HTTP {response.status_code}", 'needs_fallback': True}

        except requests.exceptions.Timeout:
            logger.warning(f"Ollama timeout after {self.timeout}s")
            return {'success': False, 'error': 'Timeout', 'needs_fallback': True}
        except Exception as e:
            logger.error(f"Ollama exception: {e}")
            return {'success': False, 'error': str(e), 'needs_fallback': True}

    def analyze_market(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and provide trading signal"""
        prompt = f"""Analyze this market data and provide a trading recommendation:

Symbol: {market_data.get('symbol', 'UNKNOWN')}
Price: ${market_data.get('price', 0):.2f}
Volume: {market_data.get('volume', 0):,}
RSI: {market_data.get('rsi', 50):.1f}
MACD: {market_data.get('macd', 'neutral')}
Trend: {market_data.get('trend', 'sideways')}

Provide:
1. Action: BUY, SELL, or HOLD
2. Confidence: 0-100
3. Reasoning: Brief explanation

Format: ACTION|CONFIDENCE|REASONING"""

        result = self.generate(prompt, max_tokens=200, temperature=0.3)

        if result['success']:
            # Parse response
            response_text = result['response']
            source = result.get('source', f'DeepSeek ({self.mode})')
            cost = result.get('cost', 0.0)

            try:
                parts = response_text.split('|')
                if len(parts) >= 3:
                    return {
                        'action': parts[0].strip().upper(),
                        'confidence': int(parts[1].strip()),
                        'reasoning': parts[2].strip(),
                        'cost': cost,
                        'source': source
                    }
            except:
                pass

            # Fallback: return raw response
            return {
                'action': 'HOLD',
                'confidence': 50,
                'reasoning': response_text,
                'cost': cost,
                'source': source
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': 0,
                'reasoning': 'DeepSeek unavailable',
                'error': result.get('error'),
                'needs_fallback': result.get('needs_fallback', True)
            }

    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        success_rate = (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0

        stats = {
            'mode': self.mode,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'success_rate': f"{success_rate:.1f}%",
            'timeout': self.timeout
        }

        if self.mode == 'cloud':
            stats.update({
                'model': self.cloud_model,
                'endpoint': self.cloud_endpoint,
                'total_cost': f"${self.total_cost:.4f}",
                'avg_cost_per_request': f"${self.total_cost / max(self.total_requests, 1):.6f}"
            })
        else:
            stats.update({
                'model': self.model,
                'endpoint': self.local_endpoint,
                'total_cost': '$0.00 (FREE)',
                'savings': f"${self.total_requests * 0.002:.2f} saved vs OpenAI"
            })

        return stats

    def is_healthy(self) -> bool:
        """Quick health check - verify API/Ollama is responding."""
        try:
            if self.mode == 'cloud':
                # Check DeepSeek API with a minimal request
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                response = requests.get(
                    f"{self.cloud_endpoint}/v1/models",
                    headers=headers,
                    timeout=5
                )
                return response.status_code in [200, 401]  # 401 = key works but may be rate limited
            else:
                # Check Ollama
                response = requests.get(f"{self.local_endpoint}/api/tags", timeout=5)
                return response.status_code == 200
        except:
            return False
