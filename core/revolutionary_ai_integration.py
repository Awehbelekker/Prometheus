#!/usr/bin/env python3
"""
PROMETHEUS Revolutionary AI Integration
========================================
Integrates all AI enhancements with the Revolutionary Master Engine.

This module provides a unified interface for:
- Pre-trained AI models
- Market intelligence agents
- Unified learning coordination
- Enhanced knowledge base
- Performance-based agent optimization

Usage in Revolutionary Master Engine:
    from core.revolutionary_ai_integration import get_revolutionary_ai_system
    
    ai_system = await get_revolutionary_ai_system()
    recommendations = await ai_system.get_trading_recommendations(symbols)
    await ai_system.execute_learning_cycle(market_data, performance)
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Phase 1: Historical Data & Pre-Training
from core.historical_data_pipeline import get_historical_pipeline
from core.model_pretraining_system import get_pretraining_system

# Phase 2: Market Intelligence Agents
from core.market_intelligence_agents import (
    get_gap_detection_agent,
    get_opportunity_scanner_agent,
    get_market_research_agent,
    MarketGap,
    TradingOpportunity,
    MarketIntelligence
)
from core.agent_performance_optimizer import get_performance_optimizer
from core.enhanced_agent_integration import get_enhanced_coordinator

# Phase 3: Learning Integration
from core.unified_learning_coordinator import get_unified_coordinator
from core.enhanced_knowledge_base import get_knowledge_base

logger = logging.getLogger(__name__)


@dataclass
class AISystemStatus:
    """Status of the AI enhancement system"""
    pre_trained_models_loaded: bool
    intelligence_agents_active: bool
    learning_coordination_active: bool
    knowledge_base_active: bool
    total_models: int
    total_agents: int
    total_adaptations: int
    last_learning_cycle: Optional[datetime]


class RevolutionaryAISystem:
    """
    Unified AI enhancement system for PROMETHEUS
    Integrates all AI enhancements with the Revolutionary Master Engine
    """
    
    def __init__(self):
        self.initialized = False
        
        # Phase 1: Historical Data & Pre-Training
        self.historical_pipeline = None
        self.pretraining_system = None
        
        # Phase 2: Market Intelligence
        self.gap_agent = None
        self.opportunity_agent = None
        self.research_agent = None
        self.performance_optimizer = None
        self.enhanced_coordinator = None
        
        # Phase 3: Learning Integration
        self.learning_coordinator = None
        self.knowledge_base = None
        
        logger.info("🚀 Revolutionary AI System created")
    
    async def initialize(self):
        """Initialize all AI enhancement components"""
        if self.initialized:
            logger.info("[CHECK] Revolutionary AI System already initialized")
            return
        
        logger.info("🔧 Initializing Revolutionary AI System...")
        
        try:
            # Phase 1: Historical Data & Pre-Training
            self.historical_pipeline = get_historical_pipeline()
            self.pretraining_system = get_pretraining_system()
            logger.info("  [CHECK] Historical data pipeline ready")
            
            # Phase 2: Market Intelligence Agents
            self.gap_agent = get_gap_detection_agent()
            self.opportunity_agent = get_opportunity_scanner_agent()
            self.research_agent = get_market_research_agent()
            self.performance_optimizer = get_performance_optimizer()
            self.enhanced_coordinator = await get_enhanced_coordinator()
            logger.info("  [CHECK] Market intelligence agents ready")
            
            # Phase 3: Learning Integration
            self.learning_coordinator = get_unified_coordinator()
            self.knowledge_base = get_knowledge_base()
            logger.info("  [CHECK] Learning coordination ready")
            
            self.initialized = True
            logger.info("[CHECK] Revolutionary AI System initialized successfully")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Revolutionary AI System: {e}")
            raise
    
    async def get_trading_recommendations(
        self,
        symbols: List[str],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive trading recommendations using all AI systems
        
        Args:
            symbols: List of symbols to analyze
            market_data: Optional market data context
            
        Returns:
            Dictionary with recommendations from all agents
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"🎯 Getting trading recommendations for {len(symbols)} symbols...")
        
        try:
            # Get recommendations from enhanced coordinator
            decisions = await self.enhanced_coordinator.execute_with_intelligence(
                symbols,
                market_data or {}
            )
            
            # Get market intelligence
            intelligence = await self.research_agent.generate_market_intelligence(symbols)
            
            # Get gaps and opportunities
            gaps = await self.gap_agent.scan_for_gaps(symbols)
            opportunities = await self.opportunity_agent.scan_all_opportunities(symbols)
            
            recommendations = {
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols,
                'decisions': decisions,
                'market_intelligence': {
                    'regime': intelligence.market_regime,
                    'sentiment': intelligence.sentiment_score,
                    'volatility': intelligence.volatility_level,
                    'insights': intelligence.actionable_insights
                },
                'gaps': [
                    {
                        'symbol': g.symbol,
                        'gap_percent': g.gap_percent,
                        'direction': g.direction,
                        'opportunity_score': g.opportunity_score
                    }
                    for g in gaps
                ],
                'opportunities': [
                    {
                        'symbol': o.symbol,
                        'type': o.opportunity_type,
                        'confidence': o.confidence,
                        'expected_return': o.expected_return
                    }
                    for o in opportunities
                ]
            }
            
            logger.info(f"[CHECK] Generated recommendations: {len(decisions)} decisions, {len(gaps)} gaps, {len(opportunities)} opportunities")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get trading recommendations: {e}")
            raise
    
    async def execute_learning_cycle(
        self,
        market_data: Dict[str, Any],
        trading_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a complete learning cycle across all AI systems
        
        Args:
            market_data: Current market data and conditions
            trading_performance: Recent trading performance metrics
            
        Returns:
            Dictionary with learning cycle results
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info("🧠 Executing coordinated learning cycle...")
        
        try:
            # Execute unified learning coordination
            adaptation = await self.learning_coordinator.coordinate_learning_cycle(
                market_data,
                trading_performance
            )
            
            # Get learning status
            status = await self.learning_coordinator.get_learning_status()
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'adaptation_id': adaptation.adaptation_id,
                'expected_improvement': adaptation.expected_improvement,
                'risk_level': adaptation.risk_level,
                'applied': adaptation.applied,
                'learning_status': status
            }
            
            logger.info(f"[CHECK] Learning cycle complete: improvement={adaptation.expected_improvement:.2%}, risk={adaptation.risk_level:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to execute learning cycle: {e}")
            raise
    
    async def save_session_knowledge(
        self,
        session_id: str,
        session_data: Dict[str, Any]
    ):
        """
        Save knowledge from completed trading session
        
        Args:
            session_id: Unique session identifier
            session_data: Session performance and learning data
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"💾 Saving session knowledge: {session_id}")
        
        try:
            await self.knowledge_base.save_session_knowledge(session_id, session_data)
            logger.info(f"[CHECK] Session knowledge saved")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save session knowledge: {e}")
            raise
    
    async def load_previous_sessions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Load knowledge from previous trading sessions
        
        Args:
            limit: Number of previous sessions to load
            
        Returns:
            List of previous session data
        """
        if not self.initialized:
            await self.initialize()
        
        logger.info(f"📖 Loading knowledge from {limit} previous sessions...")
        
        try:
            sessions = await self.knowledge_base.load_session_knowledge(limit)
            logger.info(f"[CHECK] Loaded {len(sessions)} previous sessions")
            return sessions
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to load previous sessions: {e}")
            raise
    
    async def get_system_status(self) -> AISystemStatus:
        """
        Get current status of the AI enhancement system
        
        Returns:
            AISystemStatus with current system state
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Check pre-trained models
            import os
            from pathlib import Path
            model_dir = Path("pretrained_models")
            model_count = len(list(model_dir.glob("*.joblib"))) if model_dir.exists() else 0
            
            # Get learning status
            learning_status = await self.learning_coordinator.get_learning_status()
            
            # Count agents
            agent_count = 3  # gap, opportunity, research
            agent_count += 17  # base execution agents
            
            status = AISystemStatus(
                pre_trained_models_loaded=model_count > 0,
                intelligence_agents_active=True,
                learning_coordination_active=True,
                knowledge_base_active=True,
                total_models=model_count,
                total_agents=agent_count,
                total_adaptations=learning_status['total_adaptations'],
                last_learning_cycle=datetime.fromisoformat(learning_status['last_update']) if learning_status['last_update'] else None
            )
            
            logger.info(f"📊 System Status: {model_count} models, {agent_count} agents, {status.total_adaptations} adaptations")
            
            return status
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to get system status: {e}")
            raise


# Global instance
_revolutionary_ai_system = None

async def get_revolutionary_ai_system() -> RevolutionaryAISystem:
    """Get global Revolutionary AI System instance"""
    global _revolutionary_ai_system
    if _revolutionary_ai_system is None:
        _revolutionary_ai_system = RevolutionaryAISystem()
        await _revolutionary_ai_system.initialize()
    return _revolutionary_ai_system

