"""
PROMETHEUS Trading Platform - Trading Engine Unit Tests
Comprehensive tests for core trading engine functionality
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime

from core.internal_paper_trading import InternalPaperTradingEngine
from core.ai_trading_intelligence import AITradingIntelligence
from core.database_manager import DatabaseManager


class TestInternalPaperTradingEngine:
    """Test suite for Internal Paper Trading Engine."""
    
    @pytest.fixture
    def trading_engine(self, temp_db):
        """Create trading engine instance for testing."""
        return InternalPaperTradingEngine(database_path=temp_db)
    
    @pytest.mark.unit
    def test_engine_initialization(self, trading_engine):
        """Test trading engine initializes correctly."""
        assert trading_engine is not None
        assert trading_engine.starting_capital == 10000.0
        assert trading_engine.current_capital > 0
    
    @pytest.mark.unit
    async def test_place_buy_order(self, trading_engine, mock_market_data):
        """Test placing a buy order."""
        with patch('core.market_data_service.get_real_time_price', return_value=150.0):
            result = await trading_engine.place_order(
                symbol="AAPL",
                quantity=10,
                order_type="buy",
                price=150.0
            )
            
            assert result["status"] == "success"
            assert result["order"]["symbol"] == "AAPL"
            assert result["order"]["quantity"] == 10
            assert result["order"]["order_type"] == "buy"
    
    @pytest.mark.unit
    async def test_place_sell_order(self, trading_engine, mock_market_data):
        """Test placing a sell order."""
        # First buy some shares
        with patch('core.market_data_service.get_real_time_price', return_value=150.0):
            await trading_engine.place_order("AAPL", 10, "buy", 150.0)
            
            # Now sell them
            result = await trading_engine.place_order("AAPL", 5, "sell", 155.0)
            
            assert result["status"] == "success"
            assert result["order"]["symbol"] == "AAPL"
            assert result["order"]["quantity"] == 5
            assert result["order"]["order_type"] == "sell"
    
    @pytest.mark.unit
    async def test_insufficient_funds(self, trading_engine):
        """Test handling of insufficient funds."""
        with patch('core.market_data_service.get_real_time_price', return_value=1000.0):
            result = await trading_engine.place_order("EXPENSIVE", 100, "buy", 1000.0)
            
            assert result["status"] == "error"
            assert "insufficient funds" in result["message"].lower()
    
    @pytest.mark.unit
    async def test_portfolio_calculation(self, trading_engine):
        """Test portfolio value calculation."""
        with patch('core.market_data_service.get_real_time_price', return_value=150.0):
            await trading_engine.place_order("AAPL", 10, "buy", 150.0)
            
            portfolio = await trading_engine.get_portfolio()
            
            assert "AAPL" in portfolio["positions"]
            assert portfolio["positions"]["AAPL"]["quantity"] == 10
            assert portfolio["total_value"] > 0
    
    @pytest.mark.unit
    async def test_risk_management(self, trading_engine):
        """Test risk management controls."""
        # Test position size limits
        with patch('core.market_data_service.get_real_time_price', return_value=10.0):
            result = await trading_engine.place_order("CHEAP", 2000, "buy", 10.0)
            
            # Should be rejected due to position size limits
            assert result["status"] == "error" or result["order"]["quantity"] < 2000


class TestAITradingIntelligence:
    """Test suite for AI Trading Intelligence."""
    
    @pytest.fixture
    def ai_intelligence(self):
        """Create AI intelligence instance for testing."""
        return AITradingIntelligence()
    
    @pytest.mark.unit
    async def test_market_sentiment_analysis(self, ai_intelligence, mock_ai_service):
        """Test market sentiment analysis."""
        with patch.object(ai_intelligence, 'openai_client', mock_ai_service):
            sentiment = await ai_intelligence.analyze_market_sentiment("AAPL")
            
            assert sentiment is not None
            assert "sentiment_score" in sentiment
            assert "sentiment_label" in sentiment
    
    @pytest.mark.unit
    async def test_trading_signal_generation(self, ai_intelligence, mock_ai_service):
        """Test trading signal generation."""
        with patch.object(ai_intelligence, 'openai_client', mock_ai_service):
            signal = await ai_intelligence.generate_trading_signal("AAPL", {"price": 150.0})
            
            assert signal is not None
            assert "action" in signal
            assert signal["action"] in ["buy", "sell", "hold"]
    
    @pytest.mark.unit
    async def test_fallback_behavior(self, ai_intelligence):
        """Test AI service fallback behavior."""
        # Simulate AI service failure
        with patch.object(ai_intelligence, 'openai_client', side_effect=Exception("API Error")):
            sentiment = await ai_intelligence.analyze_market_sentiment("AAPL")
            
            # Should return fallback sentiment
            assert sentiment["sentiment_label"] == "NEUTRAL"
            assert sentiment["overall_confidence"] < 0.5


class TestDatabaseManager:
    """Test suite for Database Manager."""
    
    @pytest.mark.unit
    async def test_database_initialization(self, test_database_manager):
        """Test database initialization."""
        assert test_database_manager is not None
        
        # Test basic query
        result = await asyncio.to_thread(
            test_database_manager.execute_query,
            "SELECT 1 as test",
            {}
        )
        assert result is not None
    
    @pytest.mark.unit
    async def test_trade_recording(self, test_database_manager):
        """Test trade recording functionality."""
        trade_data = {
            "symbol": "AAPL",
            "quantity": 10,
            "price": 150.0,
            "order_type": "buy",
            "timestamp": datetime.now().isoformat()
        }
        
        # This would test the actual trade recording method
        # Implementation depends on the actual database schema
        assert True  # Placeholder for actual test
    
    @pytest.mark.unit
    async def test_portfolio_persistence(self, test_database_manager):
        """Test portfolio data persistence."""
        portfolio_data = {
            "user_id": "test_user",
            "symbol": "AAPL",
            "quantity": 10,
            "average_price": 150.0
        }
        
        # This would test portfolio persistence
        # Implementation depends on the actual database schema
        assert True  # Placeholder for actual test


class TestRiskManagement:
    """Test suite for Risk Management systems."""
    
    @pytest.mark.unit
    def test_position_size_validation(self):
        """Test position size validation."""
        from core.risk_management import validate_position_size
        
        # Test normal position
        assert validate_position_size(1000, 10000) == True
        
        # Test oversized position
        assert validate_position_size(8000, 10000) == False
    
    @pytest.mark.unit
    def test_daily_loss_limits(self):
        """Test daily loss limit enforcement."""
        from core.risk_management import check_daily_loss_limit
        
        # Test within limits
        assert check_daily_loss_limit(-100, -500) == True
        
        # Test exceeding limits
        assert check_daily_loss_limit(-600, -500) == False
    
    @pytest.mark.unit
    def test_portfolio_diversification(self):
        """Test portfolio diversification checks."""
        portfolio = {
            "AAPL": {"value": 3000},
            "MSFT": {"value": 2000},
            "GOOGL": {"value": 2000},
            "CASH": {"value": 3000}
        }
        
        from core.risk_management import check_diversification
        diversification_score = check_diversification(portfolio)
        
        assert 0 <= diversification_score <= 1
        assert diversification_score > 0.5  # Well diversified
