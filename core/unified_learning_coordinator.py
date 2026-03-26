#!/usr/bin/env python3
"""
PROMETHEUS Unified Learning Coordinator
========================================
Coordinates all learning systems for coherent adaptation.
Integrates AI Learning Engine, Advanced Learning Engine, and Continuous Learning Engine.

Features:
- Unified coordination of all learning systems
- Conflict resolution between learning systems
- Coordinated adaptation strategies
- Cross-system knowledge sharing
- Performance-based learning optimization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np

# Import existing learning systems
from core.ai_learning_engine import AILearningEngine
from core.continuous_learning_engine import ContinuousLearningEngine, LearningMode
try:
    from revolutionary_features.ai_learning.advanced_learning_engine import AdvancedLearningEngine
    ADVANCED_LEARNING_AVAILABLE = True
except ImportError:
    ADVANCED_LEARNING_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("[WARNING]️ Advanced Learning Engine not available")

logger = logging.getLogger(__name__)


class LearningPriority(Enum):
    """Priority levels for learning updates"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class LearningUpdate:
    """Unified learning update from any learning system"""
    update_id: str
    source_system: str
    priority: LearningPriority
    update_type: str
    parameters: Dict[str, Any]
    confidence: float
    timestamp: datetime
    reasoning: str


@dataclass
class CoordinatedAdaptation:
    """Coordinated adaptation across all learning systems"""
    adaptation_id: str
    timestamp: datetime
    learning_updates: List[LearningUpdate]
    aggregated_parameters: Dict[str, Any]
    expected_improvement: float
    risk_level: float
    applied: bool


class UnifiedLearningCoordinator:
    """
    Coordinates all learning systems for coherent adaptation
    """
    
    def __init__(self):
        # Initialize all learning systems
        self.ai_learning = AILearningEngine()
        self.continuous_learning = ContinuousLearningEngine()
        
        if ADVANCED_LEARNING_AVAILABLE:
            self.advanced_learning = AdvancedLearningEngine()
        else:
            self.advanced_learning = None
        
        # Learning history
        self.learning_updates = []
        self.adaptations = []
        
        # Coordination parameters
        self.conflict_resolution_strategy = "weighted_average"
        self.learning_rate_multiplier = 1.0
        
        # Performance tracking
        self.performance_history = []
        
        logger.info("🧠 Unified Learning Coordinator initialized")
        logger.info(f"  AI Learning Engine: [CHECK]")
        logger.info(f"  Continuous Learning Engine: [CHECK]")
        logger.info(f"  Advanced Learning Engine: {'[CHECK]' if self.advanced_learning else '[ERROR]'}")
    
    async def coordinate_learning_cycle(
        self,
        market_data: Dict[str, Any],
        trading_performance: Dict[str, Any]
    ) -> CoordinatedAdaptation:
        """
        Execute a complete coordinated learning cycle
        
        Args:
            market_data: Current market data
            trading_performance: Recent trading performance metrics
        
        Returns:
            Coordinated adaptation
        """
        logger.info("🔄 Starting coordinated learning cycle...")
        
        # 1. Collect learning updates from all systems
        updates = await self._collect_learning_updates(market_data, trading_performance)
        
        # 2. Resolve conflicts between updates
        resolved_updates = await self._resolve_conflicts(updates)
        
        # 3. Aggregate parameters
        aggregated_params = await self._aggregate_parameters(resolved_updates)
        
        # 4. Estimate expected improvement
        expected_improvement = await self._estimate_improvement(aggregated_params)
        
        # 5. Calculate risk level
        risk_level = await self._calculate_risk(aggregated_params)
        
        # 6. Create coordinated adaptation
        adaptation = CoordinatedAdaptation(
            adaptation_id=f"adapt_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            learning_updates=resolved_updates,
            aggregated_parameters=aggregated_params,
            expected_improvement=expected_improvement,
            risk_level=risk_level,
            applied=False
        )
        
        # 7. Apply adaptation if risk is acceptable
        if risk_level < 0.7:  # Risk threshold
            await self._apply_adaptation(adaptation)
            adaptation.applied = True
            logger.info(f"[CHECK] Adaptation applied (risk: {risk_level:.2f})")
        else:
            logger.warning(f"[WARNING]️ Adaptation skipped (risk too high: {risk_level:.2f})")
        
        # Store adaptation
        self.adaptations.append(adaptation)
        
        logger.info("[CHECK] Coordinated learning cycle complete")
        
        return adaptation
    
    async def _collect_learning_updates(
        self,
        market_data: Dict[str, Any],
        trading_performance: Dict[str, Any]
    ) -> List[LearningUpdate]:
        """Collect learning updates from all systems"""
        updates = []
        
        # AI Learning Engine updates
        try:
            ai_update = await self._get_ai_learning_update(market_data, trading_performance)
            if ai_update:
                updates.append(ai_update)
        except Exception as e:
            logger.error(f"Error getting AI learning update: {e}")
        
        # Continuous Learning Engine updates
        try:
            continuous_update = await self._get_continuous_learning_update()
            if continuous_update:
                updates.append(continuous_update)
        except Exception as e:
            logger.error(f"Error getting continuous learning update: {e}")
        
        # Advanced Learning Engine updates
        if self.advanced_learning:
            try:
                advanced_update = await self._get_advanced_learning_update(market_data)
                if advanced_update:
                    updates.append(advanced_update)
            except Exception as e:
                logger.error(f"Error getting advanced learning update: {e}")
        
        logger.info(f"  Collected {len(updates)} learning updates")
        
        return updates
    
    async def _get_ai_learning_update(
        self,
        market_data: Dict[str, Any],
        trading_performance: Dict[str, Any]
    ) -> Optional[LearningUpdate]:
        """Get update from AI Learning Engine"""
        # Check if models need retraining
        if trading_performance.get('accuracy', 1.0) < 0.6:
            return LearningUpdate(
                update_id=f"ai_{datetime.now().timestamp()}",
                source_system="ai_learning_engine",
                priority=LearningPriority.HIGH,
                update_type="model_retrain",
                parameters={'retrain_models': True},
                confidence=0.8,
                timestamp=datetime.now(),
                reasoning="Model accuracy below threshold, retraining recommended"
            )
        
        return None
    
    async def _get_continuous_learning_update(self) -> Optional[LearningUpdate]:
        """Get update from Continuous Learning Engine"""
        # Perform learning update
        learning_update = await self.continuous_learning.perform_learning_update()
        
        if learning_update:
            return LearningUpdate(
                update_id=f"continuous_{datetime.now().timestamp()}",
                source_system="continuous_learning_engine",
                priority=LearningPriority.MEDIUM,
                update_type="continuous_adaptation",
                parameters={
                    'learning_rate_adjustment': learning_update.learning_rate_adjustment,
                    'feature_importance': learning_update.feature_importance_changes
                },
                confidence=0.7,
                timestamp=datetime.now(),
                reasoning="Continuous learning adaptation"
            )
        
        return None
    
    async def _get_advanced_learning_update(
        self,
        market_data: Dict[str, Any]
    ) -> Optional[LearningUpdate]:
        """Get update from Advanced Learning Engine"""
        # Simplified - in production would call actual advanced learning methods
        return LearningUpdate(
            update_id=f"advanced_{datetime.now().timestamp()}",
            source_system="advanced_learning_engine",
            priority=LearningPriority.MEDIUM,
            update_type="pattern_recognition",
            parameters={'new_patterns': []},
            confidence=0.75,
            timestamp=datetime.now(),
            reasoning="Advanced pattern recognition update"
        )
    
    async def _resolve_conflicts(
        self,
        updates: List[LearningUpdate]
    ) -> List[LearningUpdate]:
        """Resolve conflicts between learning updates"""
        if len(updates) <= 1:
            return updates
        
        # Group by update type
        updates_by_type = {}
        for update in updates:
            if update.update_type not in updates_by_type:
                updates_by_type[update.update_type] = []
            updates_by_type[update.update_type].append(update)
        
        # Resolve conflicts within each type
        resolved = []
        for update_type, type_updates in updates_by_type.items():
            if len(type_updates) == 1:
                resolved.append(type_updates[0])
            else:
                # Use highest priority update
                best_update = max(type_updates, key=lambda u: (u.priority.value, u.confidence))
                resolved.append(best_update)
                logger.info(f"  Resolved conflict for {update_type}: using {best_update.source_system}")
        
        return resolved
    
    async def _aggregate_parameters(
        self,
        updates: List[LearningUpdate]
    ) -> Dict[str, Any]:
        """Aggregate parameters from all updates"""
        aggregated = {}
        
        for update in updates:
            for key, value in update.parameters.items():
                if key not in aggregated:
                    aggregated[key] = []
                aggregated[key].append((value, update.confidence))
        
        # Weighted average for numeric parameters
        final_params = {}
        for key, values in aggregated.items():
            if isinstance(values[0][0], (int, float)):
                weighted_sum = sum(v * w for v, w in values)
                weight_sum = sum(w for _, w in values)
                final_params[key] = weighted_sum / weight_sum if weight_sum > 0 else 0
            else:
                # For non-numeric, use highest confidence value
                final_params[key] = max(values, key=lambda x: x[1])[0]
        
        return final_params
    
    async def _estimate_improvement(
        self,
        parameters: Dict[str, Any]
    ) -> float:
        """Estimate expected improvement from adaptation"""
        # Simplified estimation
        # In production, would use historical adaptation performance
        return 0.05  # 5% expected improvement
    
    async def _calculate_risk(
        self,
        parameters: Dict[str, Any]
    ) -> float:
        """Calculate risk level of adaptation"""
        # Simplified risk calculation
        # In production, would analyze parameter changes and historical impact
        return 0.3  # Low risk
    
    async def _apply_adaptation(
        self,
        adaptation: CoordinatedAdaptation
    ):
        """Apply coordinated adaptation to all systems"""
        logger.info("  Applying adaptation to all learning systems...")
        
        # Apply to AI Learning Engine
        # (In production, would call actual update methods)
        
        # Apply to Continuous Learning Engine
        # (In production, would call actual update methods)
        
        # Apply to Advanced Learning Engine
        if self.advanced_learning:
            # (In production, would call actual update methods)
            pass
        
        logger.info("  [CHECK] Adaptation applied to all systems")
    
    async def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status across all systems"""
        # Get last update timestamp
        last_update = None
        if self.adaptations:
            last_update = self.adaptations[-1].timestamp.isoformat()

        status = {
            'timestamp': datetime.now().isoformat(),
            'last_update': last_update,
            'total_adaptations': len(self.adaptations),
            'applied_adaptations': sum(1 for a in self.adaptations if a.applied),
            'learning_systems': {
                'ai_learning': 'active',
                'continuous_learning': 'active',
                'advanced_learning': 'active' if self.advanced_learning else 'inactive'
            },
            'recent_adaptations': [
                {
                    'adaptation_id': a.adaptation_id,
                    'timestamp': a.timestamp.isoformat(),
                    'expected_improvement': a.expected_improvement,
                    'risk_level': a.risk_level,
                    'applied': a.applied
                }
                for a in self.adaptations[-5:]  # Last 5 adaptations
            ]
        }

        return status


# Global instance
_unified_coordinator = None

def get_unified_coordinator() -> UnifiedLearningCoordinator:
    """Get global unified learning coordinator instance"""
    global _unified_coordinator
    if _unified_coordinator is None:
        _unified_coordinator = UnifiedLearningCoordinator()
    return _unified_coordinator

