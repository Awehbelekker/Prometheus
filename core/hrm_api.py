#!/usr/bin/env python3
"""
HRM API Endpoints for Prometheus Trading App

This module provides FastAPI endpoints for HRM (Hierarchical Reasoning Model)
integration, allowing the frontend to access enhanced AI reasoning capabilities.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from pydantic import BaseModel

from .hrm_integration import HRMTradingEngine, HRMReasoningContext, HRMReasoningLevel
from .hrm_enhanced_personas import HRMPersonaManager, HRMPersonaType

logger = logging.getLogger(__name__)

# Create API router
hrm_router = APIRouter(prefix="/api/hrm", tags=["HRM"])

# Pydantic models for API requests/responses
class MarketDataRequest(BaseModel):
    """Market data for HRM analysis"""
    prices: List[float]
    volumes: List[float]
    indicators: Dict[str, float]
    sentiment: Dict[str, float]
    timestamp: datetime

class UserContextRequest(BaseModel):
    """User context for HRM analysis"""
    profile: Dict[str, Any]
    trading_history: List[Dict[str, Any]]
    portfolio: Dict[str, Any]
    risk_preferences: Dict[str, float]

class HRMAnalysisRequest(BaseModel):
    """Request for HRM analysis"""
    market_data: MarketDataRequest
    user_context: UserContextRequest
    persona_type: str = "balanced_hrm"
    reasoning_level: str = "arc_level"

class HRMPersonaRequest(BaseModel):
    """Request for specific persona analysis"""
    market_data: MarketDataRequest
    user_context: UserContextRequest
    persona_type: str

# Initialize HRM components
hrm_engine = HRMTradingEngine()
hrm_persona_manager = HRMPersonaManager(hrm_engine)

@hrm_router.get("/status")
async def get_hrm_status():
    """Get CogniFlow™ system status"""
    try:
        metrics = hrm_engine.get_performance_metrics()
        persona_metrics = hrm_persona_manager.get_persona_performance()
        
        return {
            "status": "operational",
            "hrm_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "engine_metrics": metrics,
            "persona_metrics": persona_metrics,
            "available_personas": [p.value for p in HRMPersonaType],
            "reasoning_levels": [r.value for r in HRMReasoningLevel]
        }
    except Exception as e:
        logger.error(f"Error getting CogniFlow™ status: {e}")
        raise HTTPException(status_code=500, detail=f"CogniFlow™ status error: {str(e)}")

@hrm_router.post("/analyze")
async def analyze_market_with_hrm(request: HRMAnalysisRequest):
    """Analyze market using CogniFlow™ hierarchical reasoning"""
    try:
        # Convert request to HRM context
        context = HRMReasoningContext(
            market_data=request.market_data.dict(),
            user_profile=request.user_context.profile,
            trading_history=request.user_context.trading_history,
            current_portfolio=request.user_context.portfolio,
            risk_preferences=request.user_context.risk_preferences,
            reasoning_level=HRMReasoningLevel(request.reasoning_level)
        )
        
        # Get HRM decision
        decision = hrm_engine.make_hierarchical_decision(context)
        
        return {
            "success": True,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
            "hrm_version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Error in HRM analysis: {e}")
        raise HTTPException(status_code=500, detail=f"HRM analysis error: {str(e)}")

@hrm_router.post("/persona/analyze")
async def analyze_with_persona(request: HRMPersonaRequest):
    """Analyze market with specific HRM persona"""
    try:
        # Get persona type
        persona_type = HRMPersonaType(request.persona_type)
        
        # Analyze with persona
        result = hrm_persona_manager.analyze_with_persona(
            persona_type=persona_type,
            market_data=request.market_data.dict(),
            user_context=request.user_context.dict()
        )
        
        return {
            "success": True,
            "persona_type": request.persona_type,
            "decision": result,
            "timestamp": datetime.now().isoformat(),
            "hrm_version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Error in persona analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Persona analysis error: {str(e)}")

@hrm_router.get("/personas")
async def get_all_personas():
    """Get all available HRM personas"""
    try:
        personas = {}
        for persona_type in HRMPersonaType:
            persona = hrm_persona_manager.get_persona(persona_type)
            if persona:
                personas[persona_type.value] = {
                    "type": persona_type.value,
                    "risk_tolerance": persona.profile.risk_tolerance,
                    "reasoning_style": persona.profile.reasoning_style,
                    "preferred_assets": persona.profile.preferred_assets,
                    "max_position_size": persona.profile.max_position_size,
                    "stop_loss_percentage": persona.profile.stop_loss_percentage,
                    "take_profit_percentage": persona.profile.take_profit_percentage,
                    "trading_frequency": persona.profile.trading_frequency,
                    "hrm_weights": persona.profile.hrm_weights,
                    "performance": persona.get_performance_metrics()
                }
        
        return {
            "success": True,
            "personas": personas,
            "total_personas": len(personas),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting personas: {e}")
        raise HTTPException(status_code=500, detail=f"Personas error: {str(e)}")

@hrm_router.get("/personas/{persona_type}")
async def get_persona_details(persona_type: str):
    """Get details for specific HRM persona"""
    try:
        # Get persona type
        try:
            persona_enum = HRMPersonaType(persona_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid persona type: {persona_type}")
        
        # Get persona
        persona = hrm_persona_manager.get_persona(persona_enum)
        if not persona:
            raise HTTPException(status_code=404, detail=f"Persona not found: {persona_type}")
        
        return {
            "success": True,
            "persona": {
                "type": persona.profile.persona_type.value,
                "risk_tolerance": persona.profile.risk_tolerance,
                "reasoning_style": persona.profile.reasoning_style,
                "preferred_assets": persona.profile.preferred_assets,
                "max_position_size": persona.profile.max_position_size,
                "stop_loss_percentage": persona.profile.stop_loss_percentage,
                "take_profit_percentage": persona.profile.take_profit_percentage,
                "trading_frequency": persona.profile.trading_frequency,
                "hrm_weights": persona.profile.hrm_weights,
                "performance": persona.get_performance_metrics()
            },
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting persona details: {e}")
        raise HTTPException(status_code=500, detail=f"Persona details error: {str(e)}")

@hrm_router.get("/performance")
async def get_hrm_performance():
    """Get HRM performance metrics"""
    try:
        # Get engine performance
        engine_metrics = hrm_engine.get_performance_metrics()
        
        # Get persona performance
        persona_metrics = hrm_persona_manager.get_persona_performance()
        
        # Calculate overall performance
        total_decisions = engine_metrics.get('total_decisions', 0)
        avg_confidence = engine_metrics.get('average_confidence', 0.0)
        
        # Calculate persona success rates
        persona_success_rates = {}
        for persona_type, metrics in persona_metrics.items():
            persona_success_rates[persona_type] = metrics.get('success_rate', 0.0)
        
        return {
            "success": True,
            "engine_performance": engine_metrics,
            "persona_performance": persona_metrics,
            "overall_metrics": {
                "total_decisions": total_decisions,
                "average_confidence": avg_confidence,
                "best_performing_persona": max(persona_success_rates.items(), key=lambda x: x[1])[0] if persona_success_rates else None,
                "persona_success_rates": persona_success_rates
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting HRM performance: {e}")
        raise HTTPException(status_code=500, detail=f"Performance error: {str(e)}")

@hrm_router.post("/reasoning-levels")
async def get_reasoning_levels():
    """Get available HRM reasoning levels"""
    try:
        reasoning_levels = {}
        for level in HRMReasoningLevel:
            reasoning_levels[level.value] = {
                "name": level.value,
                "description": _get_reasoning_level_description(level),
                "capabilities": _get_reasoning_level_capabilities(level)
            }
        
        return {
            "success": True,
            "reasoning_levels": reasoning_levels,
            "total_levels": len(reasoning_levels),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting reasoning levels: {e}")
        raise HTTPException(status_code=500, detail=f"Reasoning levels error: {str(e)}")

def _get_reasoning_level_description(level: HRMReasoningLevel) -> str:
    """Get description for reasoning level"""
    descriptions = {
        HRMReasoningLevel.HIGH_LEVEL: "Abstract strategy planning - slow, high-level reasoning like human brain",
        HRMReasoningLevel.LOW_LEVEL: "Detailed trade execution - rapid, detailed computations",
        HRMReasoningLevel.ARC_LEVEL: "General reasoning - ARC benchmark level intelligence",
        HRMReasoningLevel.SUDOKU_LEVEL: "Pattern recognition - complex pattern solving capabilities",
        HRMReasoningLevel.MAZE_LEVEL: "Path finding - optimal route discovery and navigation"
    }
    return descriptions.get(level, "Unknown reasoning level")

def _get_reasoning_level_capabilities(level: HRMReasoningLevel) -> List[str]:
    """Get capabilities for reasoning level"""
    capabilities = {
        HRMReasoningLevel.HIGH_LEVEL: [
            "Abstract market analysis",
            "Portfolio strategy planning",
            "Risk assessment",
            "Long-term trend analysis"
        ],
        HRMReasoningLevel.LOW_LEVEL: [
            "Detailed trade execution",
            "Position sizing",
            "Entry/exit timing",
            "Real-time decision making"
        ],
        HRMReasoningLevel.ARC_LEVEL: [
            "General market intelligence",
            "Context understanding",
            "Adaptive reasoning",
            "Complex problem solving"
        ],
        HRMReasoningLevel.SUDOKU_LEVEL: [
            "Pattern recognition",
            "Market structure analysis",
            "Technical pattern identification",
            "Complex puzzle solving"
        ],
        HRMReasoningLevel.MAZE_LEVEL: [
            "Optimal path finding",
            "Arbitrage detection",
            "Route optimization",
            "Navigation through complex scenarios"
        ]
    }
    return capabilities.get(level, [])

@hrm_router.post("/demo")
async def run_hrm_demo():
    """Run HRM demo with sample data"""
    try:
        # Sample market data
        sample_market_data = {
            "prices": [100.0, 101.5, 99.8, 102.3, 103.1],
            "volumes": [1000000, 1200000, 800000, 1500000, 1100000],
            "indicators": {
                "rsi": 65.5,
                "macd": 0.8,
                "bollinger_upper": 105.0,
                "bollinger_lower": 98.0
            },
            "sentiment": {
                "positive": 0.6,
                "negative": 0.2,
                "neutral": 0.2
            }
        }
        
        # Sample user context
        sample_user_context = {
            "profile": {
                "risk_tolerance": 0.5,
                "investment_goal": "growth",
                "time_horizon": "medium"
            },
            "trading_history": [
                {"action": "BUY", "symbol": "AAPL", "amount": 1000, "timestamp": "2024-01-01T10:00:00Z"},
                {"action": "SELL", "symbol": "GOOGL", "amount": 500, "timestamp": "2024-01-02T14:30:00Z"}
            ],
            "portfolio": {
                "total_value": 50000,
                "cash": 10000,
                "positions": {"AAPL": 1000, "GOOGL": 500}
            },
            "risk_preferences": {
                "max_drawdown": 0.1,
                "target_return": 0.15,
                "volatility_tolerance": 0.2
            }
        }
        
        # Test with balanced persona
        result = hrm_persona_manager.analyze_with_persona(
            persona_type=HRMPersonaType.BALANCED_HRM,
            market_data=sample_market_data,
            user_context=sample_user_context
        )
        
        return {
            "success": True,
            "demo_result": result,
            "sample_data": {
                "market_data": sample_market_data,
                "user_context": sample_user_context
            },
            "timestamp": datetime.now().isoformat(),
            "message": "HRM demo completed successfully"
        }
    except Exception as e:
        logger.error(f"Error in HRM demo: {e}")
        raise HTTPException(status_code=500, detail=f"Demo error: {str(e)}")

# Health check endpoint
@hrm_router.get("/health")
async def hrm_health_check():
    """CogniFlow™ health check"""
    try:
        # Test basic functionality
        test_context = HRMReasoningContext(
            market_data={"prices": [100.0], "volumes": [1000000]},
            user_profile={},
            trading_history=[],
            current_portfolio={},
            risk_preferences={},
            reasoning_level=HRMReasoningLevel.ARC_LEVEL
        )
        
        # Try to make a decision
        decision = hrm_engine.make_hierarchical_decision(test_context)
        
        return {
            "status": "healthy",
            "hrm_version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "test_decision": decision,
            "personas_available": len(hrm_persona_manager.get_all_personas())
        }
    except Exception as e:
        logger.error(f"HRM health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 