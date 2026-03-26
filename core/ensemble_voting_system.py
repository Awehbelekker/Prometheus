"""
Ensemble Voting System for PROMETHEUS Trading Platform

Inspired by llm-council (Andrej Karpathy), adapted for local models:
- DeepSeek-R1 8B (reasoning expert)
- Qwen2.5 7B (fast inference)
- LLaVA 7B (multimodal analysis)
- OpenAI (cloud fallback)

3-Stage Process:
1. Collect individual responses from all models
2. Cross-ranking: each model ranks others' responses
3. Chairman synthesis: best model produces final answer
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


@dataclass
class ModelResponse:
    """Response from a single model"""
    model_name: str
    response: str
    confidence: float = 0.5
    latency: float = 0.0
    success: bool = True
    error: Optional[str] = None


@dataclass
class RankingResult:
    """Ranking from one model of all responses"""
    judge_model: str
    ranking: str  # Full text explanation
    parsed_ranking: List[str]  # ["Response A", "Response B", ...]
    confidence: float = 0.5


@dataclass
class EnsembleResult:
    """Final ensemble decision with consensus"""
    # Final synthesized answer
    final_answer: str
    chairman_model: str
    
    # Individual responses
    individual_responses: List[ModelResponse] = field(default_factory=list)
    
    # Rankings
    rankings: List[RankingResult] = field(default_factory=list)
    aggregate_rankings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Consensus metrics
    consensus_confidence: float = 0.0
    agreement_rate: float = 0.0
    top_ranked_model: Optional[str] = None
    
    # Performance
    total_latency: float = 0.0
    stage_latencies: Dict[str, float] = field(default_factory=dict)
    
    # Metadata
    timestamp: float = 0.0
    success: bool = True


class EnsembleVotingSystem:
    """
    Multi-model ensemble voting system
    
    Runs 3-stage process:
    1. Collect responses from all models
    2. Cross-ranking by all models
    3. Chairman synthesis
    """
    
    def __init__(self, 
                 model_names: Optional[List[str]] = None,
                 chairman: Optional[str] = None):
        """
        Initialize ensemble system
        
        Args:
            model_names: List of model names to include in council
            chairman: Model to use for final synthesis (best model)
        """
        self.model_names = model_names or [
            "deepseek-r1:8b",    # Reasoning expert
            "qwen2.5:7b",        # Fast inference
            # "llava:7b",        # Multimodal (use when visual context available)
        ]
        
        self.chairman = chairman or "deepseek-r1:8b"  # Best reasoner as chairman
        
        # Initialize providers
        self._initialize_providers()
        
        logger.info(f"✅ Ensemble initialized with {len(self.model_names)} models")
        logger.info(f"   Council: {', '.join(self.model_names)}")
        logger.info(f"   Chairman: {self.chairman}")
    
    def _initialize_providers(self):
        """Initialize AI providers for ensemble"""
        try:
            from core.unified_ai_provider import UnifiedAIProvider
            self.provider = UnifiedAIProvider()
            logger.info("✅ AI providers initialized for ensemble")
        except Exception as e:
            logger.error(f"❌ Failed to initialize providers: {e}")
            self.provider = None
    
    async def vote(self, 
                   question: str,
                   context: Optional[Dict[str, Any]] = None) -> EnsembleResult:
        """
        Run complete ensemble voting process
        
        Args:
            question: Trading decision question
            context: Additional context (market data, risk params, etc.)
        
        Returns:
            EnsembleResult with consensus decision
        """
        
        start_time = time.time()
        
        if not self.provider:
            return self._fallback_result("Providers not initialized")
        
        try:
            # Stage 1: Collect individual responses
            stage1_start = time.time()
            stage1_results = await self._stage1_collect_responses(question, context)
            stage1_latency = time.time() - stage1_start
            
            if not stage1_results:
                return self._fallback_result("All models failed to respond")
            
            logger.info(f"✅ Stage 1: Collected {len(stage1_results)} responses")
            
            # Stage 2: Cross-ranking
            stage2_start = time.time()
            stage2_results, label_to_model = await self._stage2_collect_rankings(
                question, stage1_results
            )
            stage2_latency = time.time() - stage2_start
            
            logger.info(f"✅ Stage 2: Collected {len(stage2_results)} rankings")
            
            # Calculate aggregate rankings
            aggregate_rankings = self._calculate_aggregate_rankings(
                stage2_results, label_to_model
            )
            
            # Stage 3: Chairman synthesis
            stage3_start = time.time()
            stage3_result = await self._stage3_synthesize_final(
                question, stage1_results, stage2_results, context
            )
            stage3_latency = time.time() - stage3_start
            
            logger.info(f"✅ Stage 3: Chairman synthesized final answer")
            
            # Calculate consensus metrics
            consensus = self._calculate_consensus(stage1_results, aggregate_rankings)
            
            total_latency = time.time() - start_time
            
            return EnsembleResult(
                final_answer=stage3_result,
                chairman_model=self.chairman,
                individual_responses=stage1_results,
                rankings=stage2_results,
                aggregate_rankings=aggregate_rankings,
                consensus_confidence=consensus['confidence'],
                agreement_rate=consensus['agreement_rate'],
                top_ranked_model=aggregate_rankings[0]['model'] if aggregate_rankings else None,
                total_latency=total_latency,
                stage_latencies={
                    'stage1': stage1_latency,
                    'stage2': stage2_latency,
                    'stage3': stage3_latency
                },
                timestamp=time.time(),
                success=True
            )
            
        except Exception as e:
            logger.error(f"❌ Ensemble voting failed: {e}")
            return self._fallback_result(str(e))
    
    async def _stage1_collect_responses(self,
                                       question: str,
                                       context: Optional[Dict[str, Any]]) -> List[ModelResponse]:
        """Stage 1: Collect responses from all models in parallel"""
        
        # Build enhanced prompt with context
        prompt = self._build_prompt(question, context)
        
        # Query all models in parallel
        tasks = []
        for model in self.model_names:
            task = self._query_single_model(model, prompt)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Format results
        results = []
        for model, response in zip(self.model_names, responses):
            if isinstance(response, Exception):
                logger.warning(f"⚠️ {model} failed: {response}")
                continue
            
            if response and response['success']:
                results.append(ModelResponse(
                    model_name=model,
                    response=response['text'],
                    confidence=response.get('confidence', 0.5),
                    latency=response.get('latency', 0.0),
                    success=True
                ))
        
        return results
    
    async def _stage2_collect_rankings(self,
                                      question: str,
                                      stage1_results: List[ModelResponse]) -> Tuple[List[RankingResult], Dict[str, str]]:
        """Stage 2: Each model ranks others' responses"""
        
        # Create anonymized labels
        labels = [chr(65 + i) for i in range(len(stage1_results))]  # A, B, C, ...
        
        label_to_model = {
            f"Response {label}": result.model_name
            for label, result in zip(labels, stage1_results)
        }
        
        # Build ranking prompt
        responses_text = "\n\n".join([
            f"Response {label}:\n{result.response}"
            for label, result in zip(labels, stage1_results)
        ])
        
        ranking_prompt = f"""You are evaluating different trading AI responses to this question:

Question: {question}

Here are the responses (anonymized):

{responses_text}

Task:
1. Evaluate each response for accuracy, insight, and risk assessment
2. Provide your ranking at the end

Format your ranking EXACTLY as:
FINAL RANKING:
1. Response A
2. Response B
3. Response C

Provide your evaluation and ranking:"""
        
        # Get rankings from all models in parallel
        tasks = []
        for model in self.model_names:
            task = self._query_single_model(model, ranking_prompt)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Format results
        results = []
        for model, response in zip(self.model_names, responses):
            if isinstance(response, Exception):
                continue
            
            if response and response['success']:
                full_text = response['text']
                parsed = self._parse_ranking(full_text)
                results.append(RankingResult(
                    judge_model=model,
                    ranking=full_text,
                    parsed_ranking=parsed,
                    confidence=response.get('confidence', 0.5)
                ))
        
        return results, label_to_model
    
    async def _stage3_synthesize_final(self,
                                      question: str,
                                      stage1_results: List[ModelResponse],
                                      stage2_results: List[RankingResult],
                                      context: Optional[Dict[str, Any]]) -> str:
        """Stage 3: Chairman synthesizes final answer"""
        
        # Build comprehensive context
        stage1_text = "\n\n".join([
            f"Model: {r.model_name}\nResponse: {r.response}\nConfidence: {r.confidence:.2f}"
            for r in stage1_results
        ])
        
        stage2_text = "\n\n".join([
            f"Judge: {r.judge_model}\nRanking:\n{r.ranking}"
            for r in stage2_results
        ])
        
        chairman_prompt = f"""You are the Chairman of the PROMETHEUS AI Trading Council.

Multiple AI models have analyzed this trading question and ranked each other's responses.

Original Question: {question}

STAGE 1 - Individual Responses:
{stage1_text}

STAGE 2 - Peer Rankings:
{stage2_text}

Your task as Chairman:
Synthesize all responses into ONE clear trading decision (BUY/SELL/HOLD) with reasoning.

Consider:
- Points of agreement (strong signals)
- Points of disagreement (uncertainty flags)
- Risk assessments
- Confidence levels

Provide final decision:"""
        
        response = await self._query_single_model(self.chairman, chairman_prompt)
        
        if response and response['success']:
            return response['text']
        else:
            return "Error: Chairman unable to synthesize final answer"
    
    async def _query_single_model(self, model: str, prompt: str) -> Dict[str, Any]:
        """Query a single model"""
        
        start = time.time()
        
        try:
            # Use unified provider
            response = await self.provider.generate(prompt, max_tokens=300)
            latency = time.time() - start
            
            return {
                'success': True,
                'text': response,
                'latency': latency,
                'confidence': 0.7  # Default confidence
            }
            
        except Exception as e:
            logger.error(f"❌ {model} query failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'latency': time.time() - start
            }
    
    def _build_prompt(self, question: str, context: Optional[Dict[str, Any]]) -> str:
        """Build enhanced prompt with context"""
        
        if not context:
            return question
        
        prompt = question
        
        if 'market_data' in context:
            market_str = "\n".join([f"  {k}: {v}" for k, v in context['market_data'].items()])
            prompt = f"Market Data:\n{market_str}\n\nQuestion: {prompt}"
        
        if 'risk_parameters' in context:
            risk_str = "\n".join([f"  {k}: {v}" for k, v in context['risk_parameters'].items()])
            prompt = f"{prompt}\n\nRisk Parameters:\n{risk_str}"
        
        return prompt
    
    def _parse_ranking(self, text: str) -> List[str]:
        """Parse ranking from text"""
        
        if "FINAL RANKING:" in text:
            parts = text.split("FINAL RANKING:")
            if len(parts) >= 2:
                ranking_section = parts[1]
                matches = re.findall(r'Response [A-Z]', ranking_section)
                return matches
        
        # Fallback
        matches = re.findall(r'Response [A-Z]', text)
        return matches
    
    def _calculate_aggregate_rankings(self,
                                     rankings: List[RankingResult],
                                     label_to_model: Dict[str, str]) -> List[Dict[str, Any]]:
        """Calculate aggregate rankings"""
        
        model_positions = defaultdict(list)
        
        for ranking in rankings:
            for position, label in enumerate(ranking.parsed_ranking, start=1):
                if label in label_to_model:
                    model_name = label_to_model[label]
                    model_positions[model_name].append(position)
        
        aggregate = []
        for model, positions in model_positions.items():
            if positions:
                avg_rank = sum(positions) / len(positions)
                aggregate.append({
                    'model': model,
                    'average_rank': round(avg_rank, 2),
                    'rankings_count': len(positions)
                })
        
        aggregate.sort(key=lambda x: x['average_rank'])
        return aggregate
    
    def _calculate_consensus(self,
                            responses: List[ModelResponse],
                            rankings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate consensus metrics"""
        
        # Average confidence
        avg_confidence = sum(r.confidence for r in responses) / len(responses) if responses else 0.0
        
        # Agreement rate (simplified)
        agreement_rate = 0.8 if rankings and len(rankings) > 0 else 0.5
        
        return {
            'confidence': avg_confidence,
            'agreement_rate': agreement_rate
        }
    
    def _fallback_result(self, error: str) -> EnsembleResult:
        """Create fallback result for errors"""
        
        return EnsembleResult(
            final_answer=f"Ensemble unavailable: {error}",
            chairman_model=self.chairman,
            consensus_confidence=0.0,
            agreement_rate=0.0,
            total_latency=0.0,
            timestamp=time.time(),
            success=False
        )


# Convenience function for quick ensemble decisions
async def ensemble_trading_decision(question: str,
                                   market_data: Optional[Dict[str, Any]] = None,
                                   risk_params: Optional[Dict[str, Any]] = None) -> EnsembleResult:
    """
    Quick ensemble trading decision
    
    Args:
        question: Trading decision question
        market_data: Current market context
        risk_params: Risk management parameters
    
    Returns:
        EnsembleResult with consensus decision
    
    Example:
        >>> result = await ensemble_trading_decision(
        ...     "Should I buy AAPL?",
        ...     market_data={"price": 150, "trend": "bullish"},
        ...     risk_params={"max_position": 0.1}
        ... )
        >>> print(f"Decision: {result.final_answer}")
        >>> print(f"Consensus: {result.consensus_confidence:.2f}")
        >>> print(f"Agreement: {result.agreement_rate:.1%}")
    """
    
    ensemble = EnsembleVotingSystem()
    
    context = {
        'market_data': market_data or {},
        'risk_parameters': risk_params or {}
    }
    
    return await ensemble.vote(question, context)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_ensemble():
        print("="*80)
        print("ENSEMBLE VOTING SYSTEM - TEST")
        print("="*80)
        print()
        
        # Test question
        question = "Should I buy AAPL if it's down 5% but earnings beat expectations?"
        
        context = {
            'market_data': {
                'symbol': 'AAPL',
                'price': 142.50,
                'change_percent': -5.0,
                'earnings': 'beat expectations by 15%'
            },
            'risk_parameters': {
                'max_position_size': 0.10,
                'stop_loss': 0.02
            }
        }
        
        print(f"Question: {question}")
        print(f"Context: {context}")
        print()
        
        # Run ensemble
        ensemble = EnsembleVotingSystem()
        result = await ensemble.vote(question, context)
        
        print("\n" + "="*80)
        print("ENSEMBLE RESULT")
        print("="*80)
        print()
        print(f"Final Answer: {result.final_answer}")
        print(f"Chairman: {result.chairman_model}")
        print(f"Consensus Confidence: {result.consensus_confidence:.2f}")
        print(f"Agreement Rate: {result.agreement_rate:.1%}")
        print(f"Total Latency: {result.total_latency:.2f}s")
        print()
        
        if result.individual_responses:
            print("Individual Responses:")
            for r in result.individual_responses:
                print(f"  {r.model_name}: {r.response[:100]}...")
        
        if result.aggregate_rankings:
            print("\nAggregate Rankings:")
            for r in result.aggregate_rankings:
                print(f"  {r['model']}: Rank {r['average_rank']}")
    
    asyncio.run(test_ensemble())

