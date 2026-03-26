"""Example unit tests for PROMETHEUS"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class TestSystemImports:
    """Test that core systems can be imported"""
    
    def test_import_trading_engine(self):
        """Test trading engine import"""
        from core.advanced_trading_engine import AdvancedTradingEngine
        assert AdvancedTradingEngine is not None
    
    def test_import_market_data(self):
        """Test market data import"""
        from core.real_time_market_data import RealTimeMarketDataOrchestrator
        assert RealTimeMarketDataOrchestrator is not None
    
    def test_import_brokers(self):
        """Test broker imports"""
        from brokers.alpaca_broker import AlpacaBroker
        from brokers.interactive_brokers_broker import InteractiveBrokersBroker
        assert AlpacaBroker is not None
        assert InteractiveBrokersBroker is not None

class TestRiskManagement:
    """Test risk management functionality"""
    
    def test_risk_limits_exist(self):
        """Test that risk limits are defined"""
        from core.advanced_trading_engine import AdvancedTradingEngine
        engine = AdvancedTradingEngine()
        
        assert hasattr(engine, 'risk_limits')
        assert 'max_position_size' in engine.risk_limits
        assert 'max_daily_risk' in engine.risk_limits
    
    def test_risk_limits_values(self):
        """Test risk limit values are reasonable"""
        from core.advanced_trading_engine import AdvancedTradingEngine
        engine = AdvancedTradingEngine()
        
        assert 0 < engine.risk_limits['max_position_size'] <= 1.0
        assert 0 < engine.risk_limits['max_daily_risk'] <= 1.0

@pytest.mark.asyncio
class TestAsyncFunctions:
    """Test async functionality"""
    
    async def test_async_example(self):
        """Example async test"""
        import asyncio
        await asyncio.sleep(0.1)
        assert True
