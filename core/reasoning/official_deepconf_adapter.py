"""
Official DeepConf Adapter for PROMETHEUS Trading Platform

Integrates the official DeepConf implementation (https://github.com/Awehbelekker/deepconfupdate)
to replace the synthetic DeepConf simulation with proven, research-backed reasoning.

DeepConf Paper: https://arxiv.org/abs/2508.15260
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)

# Try to import official DeepConf
try:
    from deepconf import DeepThinkLLM
    DEEPCONF_AVAILABLE = True
    logger.info("✅ Official DeepConf successfully imported")
except ImportError:
    DEEPCONF_AVAILABLE = False
    # Logged once at module level; per-symbol warnings suppressed below.


class DeepConfMode(Enum):
    """DeepConf reasoning modes"""
    ONLINE = "online"   # Real-time with confidence-based early stopping
    OFFLINE = "offline"  # Batch generation with multiple voting


@dataclass
class DeepConfConfig:
    """Configuration for Official DeepConf reasoning"""
    # Mode selection
    mode: DeepConfMode = DeepConfMode.ONLINE
    
    # Model configuration
    model: str = "deepseek-r1:8b"  # Compatible with Ollama
    endpoint: str = "http://localhost:11434"  # Ollama endpoint
    
    # Online mode parameters
    warmup_traces: int = 8  # Calibration runs for confidence threshold
    total_budget: int = 32  # Maximum traces before stopping
    
    # Offline mode parameters
    offline_budget: int = 16  # Number of traces to generate
    compute_multiple_voting: bool = True  # Enable all voting strategies
    
    # Sampling parameters
    temperature: float = 0.8
    top_p: float = 0.95
    max_tokens: int = 512
    
    # Timeout
    timeout: int = 30  # seconds


@dataclass
class DeepConfResult:
    """Result from official DeepConf reasoning"""
    # Primary answer
    final_answer: str
    voted_answer: Optional[str] = None
    
    # Confidence information
    confidence: float = 0.0
    confidence_threshold: Optional[float] = None
    
    # Voting results (for offline mode)
    voting_results: Optional[Dict[str, Any]] = None
    
    # Traces and reasoning paths
    traces: List[Dict[str, Any]] = None
    warmup_traces: List[Dict[str, Any]] = None
    final_traces: List[Dict[str, Any]] = None
    
    # Statistics
    total_traces_used: int = 0
    tokens_used: int = 0
    latency: float = 0.0
    
    # Mode and metadata
    mode: str = "online"
    timestamp: float = 0.0
    
    # Success/error tracking
    success: bool = True
    error: Optional[str] = None


class OfficialDeepConfAdapter:
    """
    Adapter for official DeepConf implementation
    
    Provides confidence-based reasoning with early stopping (online mode)
    or comprehensive voting strategies (offline mode).
    """
    
    def __init__(self, config: Optional[DeepConfConfig] = None):
        """
        Initialize Official DeepConf adapter
        
        Args:
            config: DeepConf configuration (uses defaults if None)
        """
        self.config = config or DeepConfConfig()
        self.deep_llm = None
        self.enabled = DEEPCONF_AVAILABLE
        
        if not self.enabled:
            # Log only once at DEBUG level to avoid flooding the console every symbol iteration
            logger.debug("DeepConf unavailable — using Ollama fallback reasoning")
            return
        
        try:
            # Initialize DeepThinkLLM
            logger.info(f"Initializing DeepThinkLLM with model: {self.config.model}")
            
            # Note: DeepConf's DeepThinkLLM expects vLLM backend
            # For Ollama compatibility, we need to adapt
            self.deep_llm = DeepThinkLLM(
                model=self.config.model,
                # vLLM parameters (may need adjustment for Ollama)
                enable_prefix_caching=True,
                trust_remote_code=True
            )
            
            logger.info("✅ Official DeepConf initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Official DeepConf: {e}")
            self.enabled = False
    
    async def reason(self, 
                    prompt: str, 
                    context: Optional[Dict[str, Any]] = None) -> DeepConfResult:
        """
        Perform confidence-based reasoning using official DeepConf
        
        Args:
            prompt: The reasoning problem/question
            context: Additional context (market data, etc.)
        
        Returns:
            DeepConfResult with answer, confidence, and metadata
        """
        
        if not self.enabled or self.deep_llm is None:
            return await self._fallback_reasoning(prompt, context)
        
        start_time = time.time()
        
        try:
            # Enhance prompt with context
            enhanced_prompt = self._enhance_prompt(prompt, context)
            
            # Prepare sampling parameters
            from vllm import SamplingParams
            sampling_params = SamplingParams(
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                max_tokens=self.config.max_tokens
            )
            
            # Run DeepConf reasoning based on mode
            if self.config.mode == DeepConfMode.ONLINE:
                result = self.deep_llm.deepthink(
                    prompt=enhanced_prompt,
                    mode="online",
                    warmup_traces=self.config.warmup_traces,
                    total_budget=self.config.total_budget,
                    sampling_params=sampling_params
                )
            else:  # OFFLINE mode
                result = self.deep_llm.deepthink(
                    prompt=enhanced_prompt,
                    mode="offline",
                    budget=self.config.offline_budget,
                    compute_multiple_voting=self.config.compute_multiple_voting,
                    sampling_params=sampling_params
                )
            
            latency = time.time() - start_time
            
            # Convert to our result format
            return DeepConfResult(
                final_answer=result.final_answer,
                voted_answer=result.voted_answer,
                confidence=self._extract_confidence(result),
                confidence_threshold=result.conf_bar if hasattr(result, 'conf_bar') else None,
                voting_results=result.voting_results if hasattr(result, 'voting_results') else None,
                traces=self._process_traces(result.all_traces) if hasattr(result, 'all_traces') else None,
                warmup_traces=self._process_traces(result.warmup_traces) if hasattr(result, 'warmup_traces') else None,
                final_traces=self._process_traces(result.final_traces) if hasattr(result, 'final_traces') else None,
                total_traces_used=result.total_traces_count if hasattr(result, 'total_traces_count') else 0,
                latency=latency,
                mode=self.config.mode.value,
                timestamp=time.time(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ Official DeepConf reasoning failed: {e}")
            latency = time.time() - start_time
            
            return DeepConfResult(
                final_answer="",
                confidence=0.0,
                latency=latency,
                mode=self.config.mode.value,
                timestamp=time.time(),
                success=False,
                error=str(e)
            )
    
    def _enhance_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Enhance prompt with trading context"""
        
        if not context:
            return prompt
        
        enhanced = prompt
        
        # Add market context if available
        if 'market_data' in context:
            market_str = "\n".join([f"{k}: {v}" for k, v in context['market_data'].items()])
            enhanced = f"Market Context:\n{market_str}\n\nQuestion:\n{enhanced}"
        
        # Add risk parameters if available
        if 'risk_parameters' in context:
            risk_str = "\n".join([f"{k}: {v}" for k, v in context['risk_parameters'].items()])
            enhanced = f"Risk Parameters:\n{risk_str}\n\n{enhanced}"
        
        return enhanced
    
    def _extract_confidence(self, result) -> float:
        """Extract confidence score from DeepConf result"""
        
        # Try multiple approaches to get confidence
        if hasattr(result, 'confidence'):
            return float(result.confidence)
        
        if hasattr(result, 'voting_results') and result.voting_results:
            # Use confidence from voting results
            for method, method_result in result.voting_results.items():
                if method_result and 'confidence' in method_result:
                    return float(method_result['confidence'])
        
        # Default to 0.5 if confidence not available
        return 0.5
    
    def _process_traces(self, traces) -> List[Dict[str, Any]]:
        """Process reasoning traces into standardized format"""
        
        if not traces:
            return []
        
        processed = []
        for trace in traces:
            processed.append({
                'text': trace.get('text', ''),
                'confidence': trace.get('min_conf', 0.0),
                'tokens': trace.get('tokens', 0)
            })
        
        return processed
    
    async def _fallback_reasoning(self, 
                                  prompt: str, 
                                  context: Optional[Dict[str, Any]]) -> DeepConfResult:
        """Fallback reasoning via Ollama when DeepConf/vLLM unavailable."""
        import httpx
        start = time.time()
        try:
            payload = {
                "model": self.config.model,
                "prompt": self._enhance_prompt(prompt, context) if context else prompt,
                "stream": False,
                "options": {"temperature": self.config.temperature, "num_predict": self.config.max_tokens},
            }
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                resp = await client.post(f"{self.config.endpoint}/api/generate", json=payload)
                resp.raise_for_status()
                data = resp.json()
            answer = data.get("response", "").strip()
            return DeepConfResult(
                final_answer=answer or "no answer",
                confidence=0.6,
                latency=time.time() - start,
                mode="ollama_fallback",
                timestamp=time.time(),
                success=True,
            )
        except Exception as e:
            logger.debug(f"Ollama fallback also failed: {e}")
            return DeepConfResult(
                final_answer="DeepConf unavailable - basic fallback",
                confidence=0.5,
                latency=time.time() - start,
                mode="fallback",
                timestamp=time.time(),
                success=False,
                error=str(e),
            )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        
        return {
            'enabled': self.enabled,
            'model': self.config.model,
            'mode': self.config.mode.value,
            'warmup_traces': self.config.warmup_traces,
            'total_budget': self.config.total_budget
        }


# Convenience function for trading decisions
async def deepconf_trading_decision(
    question: str,
    market_data: Dict[str, Any],
    risk_params: Optional[Dict[str, float]] = None,
    mode: DeepConfMode = DeepConfMode.ONLINE
) -> DeepConfResult:
    """
    Use Official DeepConf for trading decision with confidence scoring
    
    Args:
        question: Trading decision question
        market_data: Current market context
        risk_params: Risk management parameters
        mode: DeepConf mode (ONLINE for fast, OFFLINE for comprehensive)
    
    Returns:
        DeepConfResult with confident trading decision
    
    Example:
        >>> result = await deepconf_trading_decision(
        ...     "Should I buy AAPL at current price?",
        ...     {"price": 150.00, "volume": 1000000, "trend": "bullish"},
        ...     {"max_position_size": 0.1, "stop_loss": 0.02}
        ... )
        >>> print(f"Decision: {result.final_answer}")
        >>> print(f"Confidence: {result.confidence:.2f}")
    """
    
    config = DeepConfConfig(mode=mode)
    adapter = OfficialDeepConfAdapter(config)
    
    context = {
        'market_data': market_data,
        'risk_parameters': risk_params or {}
    }
    
    return await adapter.reason(question, context)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_official_deepconf():
        """Test official DeepConf integration"""
        
        print("="*80)
        print("TESTING OFFICIAL DEEPCONF")
        print("="*80)
        print()
        
        # Test question
        question = "What is 2^10?"
        
        # Test both modes
        for mode in [DeepConfMode.ONLINE, DeepConfMode.OFFLINE]:
            print(f"\n{'='*80}")
            print(f"Testing {mode.value.upper()} mode")
            print(f"{'='*80}\n")
            
            config = DeepConfConfig(
                mode=mode,
                warmup_traces=4,
                total_budget=16,
                offline_budget=8
            )
            
            adapter = OfficialDeepConfAdapter(config)
            
            result = await adapter.reason(question)
            
            print(f"Question: {question}")
            print(f"Answer: {result.final_answer}")
            print(f"Confidence: {result.confidence:.3f}")
            print(f"Traces Used: {result.total_traces_used}")
            print(f"Latency: {result.latency:.2f}s")
            print(f"Success: {result.success}")
            
            if result.voting_results:
                print("\nVoting Results:")
                for method, method_result in result.voting_results.items():
                    if method_result:
                        print(f"  {method}: {method_result.get('answer', 'N/A')}")
    
    asyncio.run(test_official_deepconf())

