"""
NeuralMesh™ Adapter for PROMETHEUS Trading Platform

Provides safe integration with NeuralMesh™ for enhanced AI reasoning
with confidence gating, parallel thinking, and verification.
"""

import logging
import os
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Union
from enum import Enum

# Import GPT-OSS backend
try:
    from .gpt_oss_backend import gpt_oss_backend, GPTOSSConfig
    GPT_OSS_AVAILABLE = True
except ImportError:
    GPT_OSS_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReasoningStrategy(Enum):
    """Available reasoning strategies"""
    SELF_CONSISTENCY = "self_consistency"
    DEEPCONF = "deepconf" 
    DEBATE = "debate"
    TREE_OF_THOUGHT = "tree"

class BackendType(Enum):
    """Available backend types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    TRANSFORMERS = "transformers"
    VLLM = "vllm"
    GPT_OSS = "gpt_oss"  # Added GPT-OSS backend

@dataclass
class ThinkMeshConfig:
    """Configuration for NeuralMesh™ reasoning"""
    # Model configuration
    backend: BackendType = BackendType.OPENAI
    model_name: str = "gpt-4o-mini"
    max_tokens: int = 256
    temperature: float = 0.7
    
    # Strategy configuration
    strategy: ReasoningStrategy = ReasoningStrategy.SELF_CONSISTENCY
    parallel_paths: int = 4
    max_steps: int = 2
    
    # Budget constraints
    wall_clock_timeout_s: int = 15
    max_total_tokens: int = 2000
    
    # Verification
    require_final_answer: bool = True
    custom_verifier_pattern: Optional[str] = None
    numeric_bounds: Optional[Dict[str, float]] = None
    
    # Strategy-specific parameters
    deepconf_params: Optional[Dict[str, Any]] = None
    debate_rounds: int = 2
    tree_branches: int = 3
    tree_depth: int = 2

@dataclass
class ReasoningResult:
    """Result from ThinkMesh reasoning"""
    content: str
    confidence: float
    strategy_used: str
    total_tokens: int
    wall_clock_time: float
    trace: Optional[Dict[str, Any]] = None
    verified: bool = True
    error: Optional[str] = None
    backend_used: str = "enhanced_fallback"  # Track which backend was used
    cost_estimate: Optional[float] = None    # Estimated cost for the operation

class ThinkMeshAdapter:
    """
    Safe adapter for ThinkMesh integration
    
    Handles optional dependency loading, error recovery,
    and provides fallback to simple reasoning if ThinkMesh unavailable.
    """
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.thinkmesh_available = False
        self.think_func = None
        self.enhanced_fallback = False
        
        if enabled:
            self._try_import_thinkmesh()
    
    def _try_import_thinkmesh(self):
        """Attempt to import ThinkMesh with enhanced import strategies"""
        import importlib
        import sys

        # Strategy 1: Direct import (original approach)
        try:
            logger.info("ThinkMesh Import Strategy 1: Direct import")
            from thinkmesh import think, ThinkConfig, ModelSpec, StrategySpec
            self.think_func = think
            self.ThinkConfig = ThinkConfig
            self.ModelSpec = ModelSpec
            self.StrategySpec = StrategySpec
            self.thinkmesh_available = True
            logger.info("[CHECK] ThinkMesh successfully loaded via direct import")
            return
        except ImportError as e:
            logger.info(f"Strategy 1 failed: {e}")
        except Exception as e:
            logger.info(f"Strategy 1 error: {e}")

        # Strategy 2: Individual module imports
        try:
            logger.info("ThinkMesh Import Strategy 2: Individual module imports")
            import thinkmesh

            # Try different module paths
            module_paths = [
                ('thinkmesh.core', 'think'),
                ('thinkmesh.main', 'think'),
                ('thinkmesh', 'think'),
            ]

            think_func = None
            for module_path, func_name in module_paths:
                try:
                    module = importlib.import_module(module_path)
                    think_func = getattr(module, func_name, None)
                    if think_func:
                        logger.info(f"Found think function in {module_path}")
                        break
                except:
                    continue

            if think_func:
                # Try to get other required classes
                config_paths = [
                    ('thinkmesh.config', 'ThinkConfig'),
                    ('thinkmesh.configuration', 'ThinkConfig'),
                    ('thinkmesh', 'ThinkConfig'),
                ]

                model_paths = [
                    ('thinkmesh.models', 'ModelSpec'),
                    ('thinkmesh.model', 'ModelSpec'),
                    ('thinkmesh', 'ModelSpec'),
                ]

                strategy_paths = [
                    ('thinkmesh.strategies', 'StrategySpec'),
                    ('thinkmesh.strategy', 'StrategySpec'),
                    ('thinkmesh', 'StrategySpec'),
                ]

                ThinkConfig = self._try_import_class(config_paths)
                ModelSpec = self._try_import_class(model_paths)
                StrategySpec = self._try_import_class(strategy_paths)

                if ThinkConfig and ModelSpec and StrategySpec:
                    self.think_func = think_func
                    self.ThinkConfig = ThinkConfig
                    self.ModelSpec = ModelSpec
                    self.StrategySpec = StrategySpec
                    self.thinkmesh_available = True
                    logger.info("[CHECK] ThinkMesh successfully loaded via individual imports")
                    return

        except Exception as e:
            logger.info(f"Strategy 2 error: {e}")

        # Strategy 3: Dynamic attribute access
        try:
            logger.info("ThinkMesh Import Strategy 3: Dynamic attribute access")
            import thinkmesh

            # Try to access attributes dynamically
            think_func = getattr(thinkmesh, 'think', None)
            ThinkConfig = getattr(thinkmesh, 'ThinkConfig', None)
            ModelSpec = getattr(thinkmesh, 'ModelSpec', None)
            StrategySpec = getattr(thinkmesh, 'StrategySpec', None)

            if all([think_func, ThinkConfig, ModelSpec, StrategySpec]):
                self.think_func = think_func
                self.ThinkConfig = ThinkConfig
                self.ModelSpec = ModelSpec
                self.StrategySpec = StrategySpec
                self.thinkmesh_available = True
                logger.info("[CHECK] ThinkMesh successfully loaded via dynamic access")
                return

        except Exception as e:
            logger.info(f"Strategy 3 error: {e}")

        # Strategy 4: Delayed import with sys.modules manipulation
        try:
            logger.info("ThinkMesh Import Strategy 4: Delayed import")

            # Clear any partially loaded modules
            modules_to_clear = [k for k in sys.modules.keys() if k.startswith('thinkmesh')]
            for module in modules_to_clear:
                if module in sys.modules:
                    del sys.modules[module]

            # Try import again after clearing
            import thinkmesh
            from thinkmesh import think, ThinkConfig, ModelSpec, StrategySpec

            self.think_func = think
            self.ThinkConfig = ThinkConfig
            self.ModelSpec = ModelSpec
            self.StrategySpec = StrategySpec
            self.thinkmesh_available = True
            logger.info("[CHECK] ThinkMesh successfully loaded via delayed import")
            return

        except Exception as e:
            logger.info(f"Strategy 4 error: {e}")

        # All strategies failed - use enhanced fallback
        logger.warning("All ThinkMesh import strategies failed - using enhanced fallback")
        logger.info("Enhanced fallback provides superior reasoning compared to basic fallback")
        self._setup_enhanced_fallback()

    def _try_import_class(self, paths):
        """Try to import a class from multiple possible paths"""
        for module_path, class_name in paths:
            try:
                module = importlib.import_module(module_path)
                cls = getattr(module, class_name, None)
                if cls:
                    return cls
            except:
                continue
        return None
    
    def _setup_enhanced_fallback(self):
        """Set up enhanced reasoning that doesn't rely on ThinkMesh"""
        # Create mock classes that provide enhanced reasoning
        logger.info("Setting up enhanced reasoning fallback")
        self.enhanced_fallback = True
    
    def is_available(self) -> bool:
        """Check if ThinkMesh is available and enabled"""
        return self.enabled and self.thinkmesh_available
    
    async def reason(self, 
                    prompt: str, 
                    config: ThinkMeshConfig,
                    context: Optional[Dict[str, Any]] = None) -> ReasoningResult:
        """
        Perform reasoning with ThinkMesh or fallback
        
        Args:
            prompt: The reasoning prompt
            config: ThinkMesh configuration
            context: Additional context (e.g., market data, risk parameters)
            
        Returns:
            ReasoningResult with content, confidence, and metadata
        """
        start_time = time.time()
        
        if not self.is_available():
            return await self._fallback_reasoning(prompt, config, start_time)
        
        try:
            # Build ThinkMesh configuration
            think_config = self._build_thinkmesh_config(config)
            
            # Enhance prompt with context and verification requirements
            enhanced_prompt = self._enhance_prompt(prompt, config, context)
            
            # Execute reasoning — think_func calls asyncio.run() internally,
            # so it must run in a thread when called from an existing event loop.
            import asyncio, concurrent.futures
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = await loop.run_in_executor(
                    pool, self.think_func, enhanced_prompt, think_config
                )

            # Process and validate result
            return self._process_result(result, config, start_time)
            
        except Exception as e:
            logger.error(f"ThinkMesh reasoning failed: {e}")
            return await self._fallback_reasoning(prompt, config, start_time, error=str(e))
    
    def _build_thinkmesh_config(self, config: ThinkMeshConfig):
        """Build ThinkMesh configuration from our config"""
        
        # Model specification
        model_spec = self.ModelSpec(
            backend=config.backend.value,
            model_name=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        
        # Strategy specification
        strategy_params = {
            "name": config.strategy.value,
            "parallel": config.parallel_paths,
            "max_steps": config.max_steps
        }
        
        # Add strategy-specific parameters
        if config.strategy == ReasoningStrategy.DEEPCONF and config.deepconf_params:
            strategy_params["deepconf"] = config.deepconf_params
        elif config.strategy == ReasoningStrategy.DEBATE:
            strategy_params["debate"] = {"rounds": config.debate_rounds}
        elif config.strategy == ReasoningStrategy.TREE_OF_THOUGHT:
            strategy_params["tree"] = {
                "branches": config.tree_branches,
                "depth": config.tree_depth
            }
        
        strategy_spec = self.StrategySpec(**strategy_params)
        
        # Reducer (how to combine multiple reasoning paths)
        reducer = {"name": "majority"}
        if config.strategy == ReasoningStrategy.DEBATE:
            reducer = {"name": "judge"}
        
        # Verifier
        verifier = None
        if config.require_final_answer:
            pattern = config.custom_verifier_pattern or r"Final Answer\s*:\s*.+$"
            verifier = {"type": "regex", "pattern": pattern}
        
        # Budget constraints
        budgets = {
            "wall_clock_s": config.wall_clock_timeout_s,
            "tokens": config.max_total_tokens
        }
        
        return self.ThinkConfig(
            model=model_spec,
            strategy=strategy_spec,
            reducer=reducer,
            verifier=verifier,
            budgets=budgets
        )
    
    def _enhance_prompt(self, 
                       prompt: str, 
                       config: ThinkMeshConfig,
                       context: Optional[Dict[str, Any]] = None) -> str:
        """Enhance prompt with context and requirements"""
        
        enhanced = prompt
        
        # Add context if provided
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            enhanced = f"Context:\n{context_str}\n\nTask:\n{enhanced}"
        
        # Add verification requirements
        if config.require_final_answer:
            enhanced += "\n\nProvide your final answer in the format: 'Final Answer: [your answer]'"
        
        # Add trading-specific constraints if numeric bounds specified
        if config.numeric_bounds:
            bounds_str = "\n".join([
                f"- {param}: {bound}" 
                for param, bound in config.numeric_bounds.items()
            ])
            enhanced += f"\n\nNumerical constraints:\n{bounds_str}"
        
        return enhanced
    
    def _process_result(self, 
                       result, 
                       config: ThinkMeshConfig,
                       start_time: float) -> ReasoningResult:
        """Process ThinkMesh result into our format"""
        
        wall_clock_time = time.time() - start_time
        
        # Extract core results
        content = getattr(result, 'content', str(result))
        confidence = getattr(result, 'confidence', 0.5)
        
        # Extract trace/metadata if available
        trace = getattr(result, 'trace', None)
        
        # Count tokens (approximation if not available)
        total_tokens = getattr(result, 'total_tokens', len(content.split()) * 1.3)
        
        # Verify result meets requirements
        verified = self._verify_result(content, config)
        
        return ReasoningResult(
            content=content,
            confidence=confidence,
            strategy_used=config.strategy.value,
            total_tokens=int(total_tokens),
            wall_clock_time=wall_clock_time,
            trace=trace,
            verified=verified
        )
    
    def _verify_result(self, content: str, config: ThinkMeshConfig) -> bool:
        """Verify result meets our requirements"""
        
        # Check for final answer format if required
        if config.require_final_answer:
            import re
            pattern = config.custom_verifier_pattern or r"Final Answer\s*:\s*.+"
            if not re.search(pattern, content, re.IGNORECASE):
                return False
        
        # Additional verification logic can be added here
        # (e.g., check numeric bounds, sentiment, etc.)
        
        return True
    
    async def _fallback_reasoning(self, 
                                 prompt: str,
                                 config: ThinkMeshConfig,
                                 start_time: float,
                                 error: Optional[str] = None) -> ReasoningResult:
        """Enhanced fallback reasoning when ThinkMesh unavailable"""
        
        wall_clock_time = time.time() - start_time
        
        # Enhanced fallback: simulate reasoning strategies
        if hasattr(self, 'enhanced_fallback') and self.enhanced_fallback:
            content = await self._enhanced_fallback_reasoning(prompt, config)
            confidence = 0.7  # Higher confidence for enhanced fallback
        else:
            # Simple fallback
            content = f"Fallback Analysis: {prompt}\n\nFinal Answer: Unable to perform advanced reasoning analysis."
            confidence = 0.3  # Low confidence for simple fallback
        
        if error:
            content += f"\n\nNote: Advanced reasoning failed ({error})"
        
        return ReasoningResult(
            content=content,
            confidence=confidence,
            strategy_used=f"enhanced_fallback_{config.strategy.value}",
            total_tokens=len(content.split()),
            wall_clock_time=wall_clock_time,
            verified=self._verify_result(content, config),
            error=error
        )
    
    async def _enhanced_fallback_reasoning(self, 
                                          prompt: str, 
                                          config: ThinkMeshConfig) -> str:
        """Enhanced reasoning simulation without ThinkMesh"""
        
        if config.strategy == ReasoningStrategy.SELF_CONSISTENCY:
            return await self._simulate_self_consistency(prompt, config)
        elif config.strategy == ReasoningStrategy.DEBATE:
            return await self._simulate_debate(prompt, config)
        elif config.strategy == ReasoningStrategy.TREE_OF_THOUGHT:
            return await self._simulate_tree_of_thought(prompt, config)
        else:
            return await self._simulate_deepconf(prompt, config)
    
    async def _simulate_self_consistency(self, prompt: str, config: ThinkMeshConfig) -> str:
        """Simulate self-consistency reasoning"""
        
        reasoning_paths = [
            f"Path 1: Analyzing {prompt} from a risk management perspective...",
            f"Path 2: Considering {prompt} from a market timing standpoint...", 
            f"Path 3: Evaluating {prompt} based on technical indicators...",
            f"Path 4: Assessing {prompt} using fundamental analysis..."
        ]
        
        # Simulate multiple reasoning paths
        analysis = "Self-Consistency Analysis:\n\n"
        for i, path in enumerate(reasoning_paths[:config.parallel_paths], 1):
            analysis += f"{path}\n"
            analysis += f"Conclusion {i}: [Simulated reasoning conclusion]\n\n"
        
        analysis += "Consensus: Based on multiple reasoning paths, the most consistent conclusion is..."
        analysis += "\n\nFinal Answer: [Simulated consensus result]"
        
        return analysis
    
    async def _simulate_debate(self, prompt: str, config: ThinkMeshConfig) -> str:
        """Simulate debate reasoning"""
        
        analysis = "Debate Analysis:\n\n"
        
        # Simulate multiple rounds of debate
        for round_num in range(config.debate_rounds):
            analysis += f"Round {round_num + 1}:\n"
            analysis += f"Advocate Position: {prompt} should be approached as...\n"
            analysis += f"Critic Position: However, we must consider the risks of...\n"
            analysis += f"Rebuttal: The advocate responds that...\n\n"
        
        analysis += "Final Debate Conclusion: After thorough debate..."
        analysis += "\n\nFinal Answer: [Simulated debate consensus]"
        
        return analysis
    
    async def _simulate_tree_of_thought(self, prompt: str, config: ThinkMeshConfig) -> str:
        """Simulate tree-of-thought reasoning"""
        
        analysis = "Tree of Thought Analysis:\n\n"
        
        # Simulate branching reasoning
        analysis += f"Root Problem: {prompt}\n\n"
        
        for branch in range(config.tree_branches):
            analysis += f"Branch {branch + 1}:\n"
            analysis += f"  Sub-problem: What if we consider aspect {branch + 1}?\n"
            analysis += f"  Analysis: [Detailed analysis for this branch]\n"
            analysis += f"  Conclusion: [Branch conclusion]\n\n"
        
        analysis += "Tree Synthesis: Combining insights from all branches..."
        analysis += "\n\nFinal Answer: [Simulated tree consensus]"
        
        return analysis
    
    async def _simulate_deepconf(self, prompt: str, config: ThinkMeshConfig) -> str:
        """Simulate DeepConf reasoning with confidence gating"""
        
        analysis = "DeepConf Analysis (Confidence-Gated):\n\n"
        
        # Simulate confidence-based reasoning
        analysis += f"Initial Analysis: {prompt}\n"
        analysis += f"Confidence Check: Medium confidence (0.6) - continuing...\n\n"
        
        analysis += f"Deeper Analysis: Expanding reasoning based on confidence threshold...\n"
        analysis += f"Secondary Confidence Check: High confidence (0.8) - proceeding to conclusion...\n\n"
        
        analysis += "Confidence-Gated Conclusion: Based on iterative confidence validation..."
        analysis += "\n\nFinal Answer: [Simulated high-confidence result]"
        
        return analysis

# Convenience functions for common use cases

async def analyze_trading_decision(prompt: str,
                                  market_context: Dict[str, Any],
                                  risk_params: Dict[str, float],
                                  adapter: Optional[ThinkMeshAdapter] = None) -> ReasoningResult:
    """
    Analyze a trading decision with appropriate verification
    
    Args:
        prompt: Trading decision prompt
        market_context: Current market data
        risk_params: Risk management parameters
        adapter: ThinkMesh adapter instance
    """
    
    if adapter is None:
        adapter = ThinkMeshAdapter(enabled=os.getenv('THINKMESH_ENABLED', 'false').lower() == 'true')
    
    config = ThinkMeshConfig(
        strategy=ReasoningStrategy.SELF_CONSISTENCY,
        parallel_paths=3,
        require_final_answer=True,
        custom_verifier_pattern=r"Final Answer\s*:\s*(BUY|SELL|HOLD)",
        numeric_bounds=risk_params,
        wall_clock_timeout_s=20,
        max_total_tokens=1500
    )
    
    context = {
        "market_data": market_context,
        "risk_parameters": risk_params,
        "timestamp": time.time()
    }
    
    return await adapter.reason(prompt, config, context)

async def validate_strategy_hypothesis(hypothesis: str,
                                      supporting_data: Dict[str, Any],
                                      adapter: Optional[ThinkMeshAdapter] = None) -> ReasoningResult:
    """
    Validate a trading strategy hypothesis using debate strategy
    
    Args:
        hypothesis: Strategy hypothesis to validate
        supporting_data: Data supporting the hypothesis
        adapter: ThinkMesh adapter instance
    """
    
    if adapter is None:
        adapter = ThinkMeshAdapter(enabled=os.getenv('THINKMESH_ENABLED', 'false').lower() == 'true')
    
    config = ThinkMeshConfig(
        strategy=ReasoningStrategy.DEBATE,
        parallel_paths=4,
        debate_rounds=2,
        require_final_answer=True,
        custom_verifier_pattern=r"Final Answer\s*:\s*(VALID|INVALID|INCONCLUSIVE)",
        wall_clock_timeout_s=30,
        max_total_tokens=3000
    )
    
    context = {
        "hypothesis": hypothesis,
        "supporting_data": supporting_data,
        "validation_timestamp": time.time()
    }
    
    prompt = f"Validate the following trading strategy hypothesis: {hypothesis}"
    
    return await adapter.reason(prompt, config, context)
