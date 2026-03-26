"""
PROMETHEUS Trading Platform - Revolutionary Engines Unit Tests
Comprehensive tests for revolutionary trading engines
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from decimal import Decimal
from datetime import datetime, timedelta

# Import revolutionary engines
from revolutionary_crypto_engine import RevolutionaryCryptoEngine
from revolutionary_options_engine import RevolutionaryOptionsEngine
from revolutionary_advanced_engine import RevolutionaryAdvancedEngine
from revolutionary_market_maker import RevolutionaryMarketMaker


class TestRevolutionaryCryptoEngine:
    """Test suite for Revolutionary Crypto Engine."""
    
    @pytest.fixture
    def crypto_engine(self, temp_db):
        """Create crypto engine instance for testing."""
        return RevolutionaryCryptoEngine(database_path=temp_db)
    
    @pytest.mark.unit
    def test_crypto_engine_initialization(self, crypto_engine):
        """Test crypto engine initializes correctly."""
        assert crypto_engine is not None
        assert crypto_engine.is_24_7_enabled == True
        assert hasattr(crypto_engine, 'supported_pairs')
    
    @pytest.mark.unit
    async def test_crypto_pair_validation(self, crypto_engine):
        """Test cryptocurrency pair validation."""
        # Test valid pairs
        assert crypto_engine.validate_crypto_pair("BTC/USD") == True
        assert crypto_engine.validate_crypto_pair("ETH/USD") == True
        
        # Test invalid pairs
        assert crypto_engine.validate_crypto_pair("INVALID/PAIR") == False
    
    @pytest.mark.unit
    async def test_24_7_trading_capability(self, crypto_engine):
        """Test 24/7 trading capability."""
        # Mock weekend/holiday trading
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 6, 15, 0)  # Saturday
            mock_datetime.weekday.return_value = 5  # Saturday
            
            can_trade = crypto_engine.can_trade_now()
            assert can_trade == True  # Should trade on weekends for crypto
    
    @pytest.mark.unit
    async def test_crypto_order_execution(self, crypto_engine):
        """Test crypto order execution."""
        with patch('core.market_data_service.get_crypto_price', return_value=50000.0):
            result = await crypto_engine.execute_crypto_order(
                pair="BTC/USD",
                quantity=0.1,
                order_type="buy",
                price=50000.0
            )
            
            assert result["status"] == "success"
            assert result["order"]["pair"] == "BTC/USD"
            assert result["order"]["quantity"] == 0.1
    
    @pytest.mark.unit
    async def test_crypto_volatility_handling(self, crypto_engine):
        """Test crypto volatility handling."""
        # Simulate high volatility scenario
        volatile_prices = [50000, 48000, 52000, 47000, 53000]
        
        with patch('core.market_data_service.get_crypto_price', side_effect=volatile_prices):
            volatility_score = await crypto_engine.calculate_volatility("BTC/USD")
            
            assert volatility_score > 0
            assert isinstance(volatility_score, float)


class TestRevolutionaryOptionsEngine:
    """Test suite for Revolutionary Options Engine."""
    
    @pytest.fixture
    def options_engine(self, temp_db):
        """Create options engine instance for testing."""
        return RevolutionaryOptionsEngine(database_path=temp_db)
    
    @pytest.mark.unit
    def test_options_engine_initialization(self, options_engine):
        """Test options engine initializes correctly."""
        assert options_engine is not None
        assert hasattr(options_engine, 'supported_strategies')
        assert len(options_engine.supported_strategies) > 0
    
    @pytest.mark.unit
    async def test_options_chain_analysis(self, options_engine):
        """Test options chain analysis."""
        mock_options_chain = {
            "calls": [
                {"strike": 150, "premium": 5.0, "delta": 0.5, "gamma": 0.1},
                {"strike": 155, "premium": 3.0, "delta": 0.3, "gamma": 0.08}
            ],
            "puts": [
                {"strike": 145, "premium": 4.0, "delta": -0.4, "gamma": 0.09},
                {"strike": 140, "premium": 2.5, "delta": -0.2, "gamma": 0.06}
            ]
        }
        
        with patch('core.options_data_service.get_options_chain', return_value=mock_options_chain):
            analysis = await options_engine.analyze_options_chain("AAPL", "2024-12-20")
            
            assert analysis is not None
            assert "best_call" in analysis
            assert "best_put" in analysis
            assert "implied_volatility" in analysis
    
    @pytest.mark.unit
    async def test_multi_leg_strategy(self, options_engine):
        """Test multi-leg options strategy execution."""
        strategy = {
            "type": "iron_condor",
            "legs": [
                {"action": "sell", "type": "call", "strike": 155, "quantity": 1},
                {"action": "buy", "type": "call", "strike": 160, "quantity": 1},
                {"action": "sell", "type": "put", "strike": 145, "quantity": 1},
                {"action": "buy", "type": "put", "strike": 140, "quantity": 1}
            ]
        }
        
        with patch('core.options_broker.execute_multi_leg_order') as mock_execute:
            mock_execute.return_value = {"status": "success", "order_id": "test_123"}
            
            result = await options_engine.execute_multi_leg_strategy("AAPL", strategy)
            
            assert result["status"] == "success"
            assert "order_id" in result
    
    @pytest.mark.unit
    async def test_greeks_calculation(self, options_engine):
        """Test options Greeks calculation."""
        option_data = {
            "underlying_price": 150.0,
            "strike_price": 155.0,
            "time_to_expiry": 30,
            "volatility": 0.25,
            "risk_free_rate": 0.05
        }
        
        greeks = await options_engine.calculate_greeks(option_data)
        
        assert "delta" in greeks
        assert "gamma" in greeks
        assert "theta" in greeks
        assert "vega" in greeks
        assert "rho" in greeks


class TestRevolutionaryAdvancedEngine:
    """Test suite for Revolutionary Advanced Engine."""
    
    @pytest.fixture
    def advanced_engine(self, temp_db):
        """Create advanced engine instance for testing."""
        return RevolutionaryAdvancedEngine(database_path=temp_db)
    
    @pytest.mark.unit
    def test_advanced_engine_initialization(self, advanced_engine):
        """Test advanced engine initializes correctly."""
        assert advanced_engine is not None
        assert hasattr(advanced_engine, 'dma_enabled')
        assert hasattr(advanced_engine, 'vwap_enabled')
        assert hasattr(advanced_engine, 'twap_enabled')
    
    @pytest.mark.unit
    async def test_dma_order_execution(self, advanced_engine):
        """Test Direct Market Access (DMA) order execution."""
        dma_order = {
            "symbol": "AAPL",
            "quantity": 1000,
            "order_type": "limit",
            "price": 150.0,
            "execution_style": "DMA"
        }
        
        with patch('core.dma_broker.execute_dma_order') as mock_dma:
            mock_dma.return_value = {"status": "success", "execution_time": 0.05}
            
            result = await advanced_engine.execute_dma_order(dma_order)
            
            assert result["status"] == "success"
            assert result["execution_time"] < 0.1  # Fast execution
    
    @pytest.mark.unit
    async def test_vwap_strategy(self, advanced_engine):
        """Test Volume Weighted Average Price (VWAP) strategy."""
        vwap_params = {
            "symbol": "AAPL",
            "target_quantity": 10000,
            "time_horizon": 60,  # minutes
            "participation_rate": 0.1
        }
        
        with patch('core.market_data_service.get_volume_profile') as mock_volume:
            mock_volume.return_value = {"average_volume": 1000000, "volume_curve": []}
            
            strategy = await advanced_engine.create_vwap_strategy(vwap_params)
            
            assert strategy is not None
            assert strategy["total_quantity"] == 10000
            assert len(strategy["execution_schedule"]) > 0
    
    @pytest.mark.unit
    async def test_twap_strategy(self, advanced_engine):
        """Test Time Weighted Average Price (TWAP) strategy."""
        twap_params = {
            "symbol": "MSFT",
            "target_quantity": 5000,
            "time_horizon": 120,  # minutes
            "interval": 10  # minutes
        }
        
        strategy = await advanced_engine.create_twap_strategy(twap_params)
        
        assert strategy is not None
        assert strategy["total_quantity"] == 5000
        assert len(strategy["execution_schedule"]) == 12  # 120/10 intervals


class TestRevolutionaryMarketMaker:
    """Test suite for Revolutionary Market Maker."""
    
    @pytest.fixture
    def market_maker(self, temp_db):
        """Create market maker instance for testing."""
        return RevolutionaryMarketMaker(database_path=temp_db)
    
    @pytest.mark.unit
    def test_market_maker_initialization(self, market_maker):
        """Test market maker initializes correctly."""
        assert market_maker is not None
        assert hasattr(market_maker, 'bid_ask_spread')
        assert hasattr(market_maker, 'inventory_limits')
    
    @pytest.mark.unit
    async def test_bid_ask_spread_calculation(self, market_maker):
        """Test bid-ask spread calculation."""
        market_data = {
            "symbol": "AAPL",
            "last_price": 150.0,
            "volume": 1000000,
            "volatility": 0.25
        }
        
        spread = await market_maker.calculate_optimal_spread(market_data)
        
        assert spread["bid"] < market_data["last_price"]
        assert spread["ask"] > market_data["last_price"]
        assert spread["spread_percentage"] > 0
    
    @pytest.mark.unit
    async def test_inventory_management(self, market_maker):
        """Test inventory management system."""
        current_inventory = {
            "AAPL": {"quantity": 500, "average_price": 148.0},
            "MSFT": {"quantity": -200, "average_price": 302.0}
        }
        
        market_maker.update_inventory(current_inventory)
        
        # Test inventory limits
        can_buy_more = market_maker.can_increase_position("AAPL", 100)
        can_sell_more = market_maker.can_increase_position("MSFT", -50)
        
        assert isinstance(can_buy_more, bool)
        assert isinstance(can_sell_more, bool)
    
    @pytest.mark.unit
    async def test_liquidity_provision(self, market_maker):
        """Test liquidity provision functionality."""
        market_conditions = {
            "symbol": "GOOGL",
            "bid": 2495.0,
            "ask": 2505.0,
            "volume": 500000,
            "spread": 10.0
        }
        
        liquidity_orders = await market_maker.provide_liquidity(market_conditions)
        
        assert len(liquidity_orders) >= 2  # At least bid and ask
        assert any(order["side"] == "buy" for order in liquidity_orders)
        assert any(order["side"] == "sell" for order in liquidity_orders)
