"""
🤖 AI-Enhanced Trading Endpoints with GPT-OSS Integration
Advanced trading API with AI-powered market analysis, strategy generation, and risk assessment
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import asyncio
import json

from core.gpt_oss_trading_adapter import (
    get_gpt_oss_adapter,
    GPTOSSTradingAdapter,
    TradingPrompt,
    AITradingInsight,
    ModelSize
)

logger = logging.getLogger(__name__)

# Pydantic models for request/response
class MarketSentimentRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g., AAPL)")
    include_news: bool = Field(default=True, description="Include news sentiment analysis")
    model_size: str = Field(default="20b", description="Model size: 20b or 120b")

class TradingStrategyRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    market_data: Dict[str, Any] = Field(..., description="Current market data")
    strategy_context: str = Field(..., description="Trading strategy context")
    analysis_type: str = Field(default="technical", description="Analysis type")
    time_horizon: str = Field(default="intraday", description="Time horizon")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance")
    model_size: str = Field(default="120b", description="Model size for strategy generation")

class TechnicalAnalysisRequest(BaseModel):
    symbol: str = Field(..., description="Trading symbol")
    price_data: List[Dict[str, float]] = Field(..., description="OHLCV price data")
    indicators: Optional[Dict[str, float]] = Field(default=None, description="Technical indicators")
    model_size: str = Field(default="20b", description="Model size")

class RiskAssessmentRequest(BaseModel):
    portfolio: Dict[str, Any] = Field(..., description="Current portfolio")
    market_conditions: Dict[str, Any] = Field(..., description="Market conditions")
    model_size: str = Field(default="120b", description="Model size")

class AITradingResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    ai_analysis: Optional[Dict[str, Any]] = None
    processing_time: float
    model_used: str
    confidence: float

# Initialize router
router = APIRouter(prefix="/ai-trading", tags=["AI Trading"])

@router.get("/health")
async def ai_trading_health():
    """Check AI trading services health"""
    try:
        adapter = await get_gpt_oss_adapter()
        
        health_status = {
            "ai_trading_service": "healthy",
            "gpt_oss_20b": adapter.is_available(ModelSize.SMALL),
            "gpt_oss_120b": adapter.is_available(ModelSize.LARGE),
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "sentiment_analysis": adapter.is_available(ModelSize.SMALL),
                "strategy_generation": adapter.is_available(ModelSize.LARGE),
                "technical_analysis": adapter.is_available(ModelSize.SMALL),
                "risk_assessment": adapter.is_available(ModelSize.LARGE)
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"AI trading health check failed: {e}")
        return {
            "ai_trading_service": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.post("/sentiment-analysis", response_model=AITradingResponse)
async def analyze_market_sentiment(request: MarketSentimentRequest):
    """
    🎯 Advanced Market Sentiment Analysis
    
    Analyzes market sentiment using GPT-OSS models, incorporating:
    - Price action analysis
    - Volume patterns
    - News sentiment (if enabled)
    - Social media trends
    """
    start_time = datetime.utcnow()
    
    try:
        adapter = await get_gpt_oss_adapter()
        model_size = ModelSize.LARGE if request.model_size == "120b" else ModelSize.SMALL
        
        # Get current market data for the symbol
        market_data = await _get_market_data(request.symbol)
        
        # Get news headlines if requested
        news_headlines = []
        if request.include_news:
            news_headlines = await _get_news_headlines(request.symbol)
        
        # Perform sentiment analysis
        sentiment_result = await adapter.analyze_market_sentiment(
            market_data=market_data,
            news_headlines=news_headlines,
            model_size=model_size
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=True,
            data={
                "symbol": request.symbol,
                "sentiment": sentiment_result["sentiment"],
                "confidence": sentiment_result["confidence"],
                "reasoning": sentiment_result["reasoning"],
                "bullish_factors": sentiment_result.get("bullish_factors", []),
                "bearish_factors": sentiment_result.get("bearish_factors", []),
                "market_data": market_data,
                "news_count": len(news_headlines)
            },
            ai_analysis=sentiment_result,
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=sentiment_result["confidence"]
        )
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed for {request.symbol}: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=False,
            data={"error": str(e), "symbol": request.symbol},
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=0.0
        )

@router.post("/trading-strategy", response_model=AITradingResponse)
async def generate_trading_strategy(request: TradingStrategyRequest):
    """
    📈 AI-Powered Trading Strategy Generation
    
    Generates comprehensive trading strategies using GPT-OSS 120B model:
    - Technical analysis integration
    - Fundamental analysis
    - Risk-adjusted recommendations
    - Entry/exit points
    - Position sizing suggestions
    """
    start_time = datetime.utcnow()
    
    try:
        adapter = await get_gpt_oss_adapter()
        model_size = ModelSize.LARGE if request.model_size == "120b" else ModelSize.SMALL
        
        # Create trading prompt
        trading_prompt = TradingPrompt(
            market_data=request.market_data,
            strategy_context=request.strategy_context,
            analysis_type=request.analysis_type,
            time_horizon=request.time_horizon,
            risk_tolerance=request.risk_tolerance
        )
        
        # Generate trading strategy
        strategy_insight = await adapter.generate_trading_strategy(
            prompt=trading_prompt,
            model_size=model_size
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=True,
            data={
                "symbol": strategy_insight.symbol,
                "action": strategy_insight.action,
                "confidence": strategy_insight.confidence,
                "reasoning": strategy_insight.reasoning,
                "price_target": strategy_insight.price_target,
                "stop_loss": strategy_insight.stop_loss,
                "time_horizon": strategy_insight.time_horizon,
                "risk_assessment": strategy_insight.risk_assessment,
                "market_sentiment": strategy_insight.market_sentiment,
                "strategy_context": request.strategy_context
            },
            ai_analysis={
                "full_insight": strategy_insight.__dict__,
                "prompt_used": trading_prompt.__dict__
            },
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=strategy_insight.confidence
        )
        
    except Exception as e:
        logger.error(f"Strategy generation failed for {request.symbol}: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=False,
            data={"error": str(e), "symbol": request.symbol},
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=0.0
        )

@router.post("/technical-analysis", response_model=AITradingResponse)
async def analyze_technical_patterns(request: TechnicalAnalysisRequest):
    """
    📊 Advanced Technical Pattern Recognition
    
    AI-powered technical analysis using GPT-OSS:
    - Chart pattern recognition
    - Support/resistance levels
    - Trend analysis
    - Technical indicator interpretation
    - Entry/exit signal generation
    """
    start_time = datetime.utcnow()
    
    try:
        adapter = await get_gpt_oss_adapter()
        model_size = ModelSize.LARGE if request.model_size == "120b" else ModelSize.SMALL
        
        # Perform technical analysis
        technical_result = await adapter.analyze_technical_patterns(
            symbol=request.symbol,
            price_data=request.price_data,
            indicators=request.indicators,
            model_size=model_size
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=True,
            data={
                "symbol": request.symbol,
                "patterns": technical_result.get("patterns", []),
                "signals": technical_result.get("signals", []),
                "strength": technical_result.get("strength", "weak"),
                "recommendation": technical_result.get("recommendation", "HOLD"),
                "data_points_analyzed": len(request.price_data),
                "indicators_used": list(request.indicators.keys()) if request.indicators else []
            },
            ai_analysis=technical_result,
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=technical_result.get("confidence", 0.5)
        )
        
    except Exception as e:
        logger.error(f"Technical analysis failed for {request.symbol}: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=False,
            data={"error": str(e), "symbol": request.symbol},
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=0.0
        )

@router.post("/risk-assessment", response_model=AITradingResponse)
async def assess_portfolio_risk(request: RiskAssessmentRequest):
    """
    [WARNING]️ Comprehensive Portfolio Risk Assessment
    
    AI-powered risk analysis using GPT-OSS 120B:
    - Portfolio diversification analysis
    - Correlation risk assessment
    - Market risk evaluation
    - Volatility analysis
    - Risk mitigation recommendations
    """
    start_time = datetime.utcnow()
    
    try:
        adapter = await get_gpt_oss_adapter()
        model_size = ModelSize.LARGE if request.model_size == "120b" else ModelSize.SMALL
        
        # Perform risk assessment
        risk_result = await adapter.assess_risk_exposure(
            portfolio=request.portfolio,
            market_conditions=request.market_conditions,
            model_size=model_size
        )
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=True,
            data={
                "risk_level": risk_result.get("risk_level", "medium"),
                "risk_score": risk_result.get("risk_score", 5.0),
                "risk_factors": risk_result.get("risk_factors", []),
                "recommendations": risk_result.get("recommendations", []),
                "portfolio_positions": len(request.portfolio.get("positions", [])),
                "market_condition": request.market_conditions.get("condition", "unknown")
            },
            ai_analysis=risk_result,
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=risk_result.get("confidence", 0.5)
        )
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return AITradingResponse(
            success=False,
            data={"error": str(e)},
            processing_time=processing_time,
            model_used=f"gpt-oss-{request.model_size}",
            confidence=0.0
        )

@router.get("/models/status")
async def get_models_status():
    """Get detailed status of all GPT-OSS models"""
    try:
        adapter = await get_gpt_oss_adapter()
        
        return {
            "models": {
                "gpt-oss-20b": {
                    "available": adapter.is_available(ModelSize.SMALL),
                    "url": "http://localhost:5000",
                    "recommended_for": ["sentiment_analysis", "technical_analysis", "quick_insights"],
                    "response_time": "fast"
                },
                "gpt-oss-120b": {
                    "available": adapter.is_available(ModelSize.LARGE),
                    "url": "http://localhost:5001", 
                    "recommended_for": ["strategy_generation", "risk_assessment", "deep_analysis"],
                    "response_time": "slower_but_comprehensive"
                }
            },
            "capabilities": {
                "sentiment_analysis": True,
                "strategy_generation": True,
                "technical_analysis": True,
                "risk_assessment": True,
                "news_integration": True,
                "real_time_analysis": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model status check failed: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

@router.post("/batch-analysis")
async def run_batch_analysis(
    symbols: List[str],
    analysis_types: List[str] = ["sentiment", "technical"],
    background_tasks: BackgroundTasks = None
):
    """
    🚀 Batch Analysis for Multiple Symbols
    
    Run comprehensive AI analysis on multiple symbols:
    - Concurrent processing for speed
    - Multiple analysis types
    - Consolidated reporting
    """
    start_time = datetime.utcnow()
    
    try:
        adapter = await get_gpt_oss_adapter()
        
        # Limit batch size for performance
        if len(symbols) > 20:
            symbols = symbols[:20]
            
        results = {}
        
        # Process symbols concurrently
        tasks = []
        for symbol in symbols:
            if "sentiment" in analysis_types:
                tasks.append(_analyze_symbol_sentiment(adapter, symbol))
            if "technical" in analysis_types:
                tasks.append(_analyze_symbol_technical(adapter, symbol))
                
        # Execute all tasks concurrently
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organize results by symbol
        for i, symbol in enumerate(symbols):
            results[symbol] = {
                "sentiment": None,
                "technical": None,
                "processed": True
            }
            
            # Parse task results (simplified for example)
            if i < len(task_results) and not isinstance(task_results[i], Exception):
                if "sentiment" in analysis_types:
                    results[symbol]["sentiment"] = task_results[i]
                    
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "success": True,
            "batch_id": f"batch_{int(start_time.timestamp())}",
            "symbols_processed": len(symbols),
            "analysis_types": analysis_types,
            "results": results,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            "success": False,
            "error": str(e),
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }

# Helper functions
async def _get_market_data(symbol: str) -> Dict[str, Any]:
    """Get current market data for a symbol"""
    # This would integrate with your market data provider
    # For now, return mock data
    return {
        "symbol": symbol,
        "price": 150.00,
        "volume": 1000000,
        "change_percent": 2.5,
        "market_cap": 2500000000,
        "timestamp": datetime.utcnow().isoformat()
    }

async def _get_news_headlines(symbol: str) -> List[str]:
    """Get recent news headlines for a symbol"""
    # This would integrate with your news data provider
    # For now, return mock headlines
    return [
        f"{symbol} reports strong quarterly earnings",
        f"Analysts upgrade {symbol} price target",
        f"{symbol} announces new product launch",
        f"Market volatility affects {symbol} trading"
    ]

async def _analyze_symbol_sentiment(adapter: GPTOSSTradingAdapter, symbol: str):
    """Helper for batch sentiment analysis"""
    market_data = await _get_market_data(symbol)
    return await adapter.analyze_market_sentiment(market_data, model_size=ModelSize.SMALL)

async def _analyze_symbol_technical(adapter: GPTOSSTradingAdapter, symbol: str):
    """Helper for batch technical analysis"""
    # Mock price data for technical analysis
    price_data = [
        {"open": 148.0, "high": 151.0, "low": 147.0, "close": 150.0, "volume": 1000000}
    ]
    return await adapter.analyze_technical_patterns(symbol, price_data, model_size=ModelSize.SMALL)
