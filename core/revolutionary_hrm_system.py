#!/usr/bin/env python3
"""
Revolutionary HRM System
Combines all enhancements: Multi-agent, Ensemble, Memory, and more
"""

import logging
from typing import Dict, Any, Optional

from core.multi_agent_hrm import MultiAgentHRMOrchestrator
from core.multi_checkpoint_ensemble import MultiCheckpointEnsemble
from core.hierarchical_memory import HierarchicalMemorySystem
from core.hrm_integration import HRMReasoningContext, HRMReasoningLevel

logger = logging.getLogger(__name__)


class RevolutionaryHRMSystem:
    """
    Complete Revolutionary HRM System
    Combines:
    - Multi-agent orchestration (CrewAI)
    - Multi-checkpoint ensemble
    - Hierarchical memory system
    - Market regime detection
    - Adaptive learning
    """
    
    def __init__(self, device='cpu', use_multi_agent=True, use_ensemble=True, use_memory=True):
        self.device = device
        self.use_multi_agent = use_multi_agent
        self.use_ensemble = use_ensemble
        self.use_memory = use_memory
        
        # Initialize components
        self.multi_agent = None
        self.ensemble = None
        self.memory = None
        
        if use_multi_agent:
            try:
                self.multi_agent = MultiAgentHRMOrchestrator(device=device)
                logger.info("✅ Multi-agent HRM system initialized")
            except Exception as e:
                logger.warning(f"Multi-agent system not available: {e}")
                self.use_multi_agent = False
        
        if use_ensemble:
            try:
                self.ensemble = MultiCheckpointEnsemble(device=device)
                logger.info("✅ Multi-checkpoint ensemble initialized")
            except Exception as e:
                logger.warning(f"Ensemble system not available: {e}")
                self.use_ensemble = False
        
        if use_memory:
            try:
                self.memory = HierarchicalMemorySystem()
                logger.info("✅ Hierarchical memory system initialized")
            except Exception as e:
                logger.warning(f"Memory system not available: {e}")
                self.use_memory = False
    
    def make_revolutionary_decision(self, context: HRMReasoningContext) -> Dict[str, Any]:
        """
        Make decision using all revolutionary enhancements
        """
        # Recall relevant memories
        memories = {}
        if self.use_memory and self.memory:
            memories = self.memory.recall_for_context(context.market_data)
            # Enhance context with memories
            context = self._enhance_context_with_memories(context, memories)
        
        # Get decision from multi-agent system
        agent_decision = None
        if self.use_multi_agent and self.multi_agent:
            try:
                agent_decision = self.multi_agent.make_ensemble_decision(context)
            except Exception as e:
                logger.warning(f"Multi-agent decision failed: {e}")
        
        # Get decision from ensemble
        ensemble_decision = None
        if self.use_ensemble and self.ensemble:
            try:
                ensemble_decision = self.ensemble.make_ensemble_decision(context)
            except Exception as e:
                logger.warning(f"Ensemble decision failed: {e}")
        
        # Synthesize final decision
        final_decision = self._synthesize_final_decision(
            agent_decision,
            ensemble_decision,
            memories
        )
        
        # Store in memory for learning
        if self.use_memory and self.memory:
            self.memory.remember_decision(
                context.market_data,
                final_decision,
                outcome=None  # Will be updated when outcome is known
            )
        
        return final_decision
    
    def _enhance_context_with_memories(self, context: HRMReasoningContext, memories: Dict) -> HRMReasoningContext:
        """Enhance context with recalled memories"""
        # Add memory insights to context
        if 'episodic' in memories and memories['episodic']:
            # Learn from similar past episodes
            similar_episodes = memories['episodic']
            if similar_episodes:
                # Extract lessons learned
                context.user_profile = context.user_profile or {}
                context.user_profile['memory_insights'] = {
                    'similar_episodes': len(similar_episodes),
                    'avg_profit': sum(e.get('profit', 0) for e in similar_episodes) / len(similar_episodes) if similar_episodes else 0
                }
        
        if 'semantic' in memories and memories['semantic']:
            # Apply learned patterns
            patterns = memories['semantic']
            if patterns:
                context.user_profile = context.user_profile or {}
                context.user_profile['learned_patterns'] = [
                    {
                        'type': p['pattern_type'],
                        'success_rate': p['success_rate'],
                        'frequency': p['frequency']
                    }
                    for p in patterns[:5]  # Top 5 patterns
                ]
        
        if 'procedural' in memories and memories['procedural']:
            # Apply best strategies
            strategies = memories['procedural']
            if strategies:
                context.user_profile = context.user_profile or {}
                context.user_profile['best_strategies'] = [
                    {
                        'name': s['strategy_name'],
                        'success_rate': s['success_rate'],
                        'avg_profit': s['avg_profit_per_trade']
                    }
                    for s in strategies[:3]  # Top 3 strategies
                ]
        
        return context
    
    def _synthesize_final_decision(self, agent_decision: Optional[Dict], 
                                   ensemble_decision: Optional[Dict],
                                   memories: Dict) -> Dict[str, Any]:
        """Synthesize final decision from all sources"""
        decisions = []
        
        if agent_decision:
            decisions.append(('multi_agent', agent_decision, 0.4))
        
        if ensemble_decision:
            decisions.append(('ensemble', ensemble_decision, 0.4))
        
        # Memory-based decision (if available)
        if memories.get('procedural'):
            best_strategy = memories['procedural'][0] if memories['procedural'] else None
            if best_strategy:
                memory_decision = {
                    'action': best_strategy['strategy_data'].get('action', 'HOLD'),
                    'confidence': best_strategy['success_rate'],
                    'source': 'memory'
                }
                decisions.append(('memory', memory_decision, 0.2))
        
        if not decisions:
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': 'All decision sources failed',
                'revolutionary': True
            }
        
        # Weighted synthesis
        action_scores = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
        total_weight = 0.0
        sources = {}
        
        for source_name, decision, weight in decisions:
            action = decision.get('action', 'HOLD')
            confidence = decision.get('confidence', 0.0)
            
            if action in action_scores:
                action_scores[action] += confidence * weight
            
            total_weight += weight
            sources[source_name] = {
                'action': action,
                'confidence': confidence,
                'weight': weight
            }
        
        # Select best action
        best_action = max(action_scores, key=action_scores.get)
        final_confidence = action_scores[best_action] / max(total_weight, 0.001)
        
        # Calculate position size
        position_size = min(final_confidence * 0.1, 0.1)  # Max 10%
        
        return {
            'action': best_action,
            'confidence': min(final_confidence, 1.0),
            'position_size': position_size,
            'sources': sources,
            'num_sources': len(decisions),
            'revolutionary': True,
            'enhancements': {
                'multi_agent': self.use_multi_agent and agent_decision is not None,
                'ensemble': self.use_ensemble and ensemble_decision is not None,
                'memory': self.use_memory and bool(memories)
            }
        }
    
    def update_with_outcome(self, decision: Dict, outcome: Dict):
        """Update memory with trading outcome"""
        if self.use_memory and self.memory:
            self.memory.remember_decision(
                decision.get('context', {}),
                decision,
                outcome
            )
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of all revolutionary components"""
        return {
            'multi_agent': {
                'enabled': self.use_multi_agent,
                'available': self.multi_agent is not None
            },
            'ensemble': {
                'enabled': self.use_ensemble,
                'available': self.ensemble is not None,
                'metrics': self.ensemble.get_ensemble_metrics() if self.ensemble else None
            },
            'memory': {
                'enabled': self.use_memory,
                'available': self.memory is not None
            }
        }

