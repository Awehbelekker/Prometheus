"""
PROMETHEUS Trading Platform - Test Configuration
Pytest configuration and fixtures for comprehensive testing
"""

import pytest
import asyncio
import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Generator, AsyncGenerator

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///test_prometheus.db"
os.environ["DISABLE_LIVE_TRADING"] = "true"
os.environ["MOCK_MARKET_DATA"] = "true"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Initialize test database
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_trades (
            id INTEGER PRIMARY KEY,
            symbol TEXT,
            quantity INTEGER,
            price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def mock_market_data():
    """Mock market data for testing."""
    return {
        "AAPL": {"price": 150.00, "volume": 1000000, "change": 2.5},
        "MSFT": {"price": 300.00, "volume": 800000, "change": -1.2},
        "GOOGL": {"price": 2500.00, "volume": 500000, "change": 5.8},
        "TSLA": {"price": 800.00, "volume": 2000000, "change": -3.1}
    }

@pytest.fixture
def mock_alpaca_client():
    """Mock Alpaca trading client."""
    mock_client = Mock()
    mock_client.get_account.return_value = Mock(
        buying_power=10000.0,
        cash=5000.0,
        portfolio_value=15000.0
    )
    mock_client.list_positions.return_value = []
    mock_client.submit_order.return_value = Mock(
        id="test_order_123",
        status="accepted",
        symbol="AAPL",
        qty=10,
        side="buy"
    )
    return mock_client

@pytest.fixture
def mock_ai_service():
    """Mock AI trading intelligence service."""
    mock_ai = Mock()
    mock_ai.analyze_market_sentiment.return_value = {
        "sentiment": "bullish",
        "confidence": 0.85,
        "recommendation": "buy"
    }
    mock_ai.generate_trading_signal.return_value = {
        "action": "buy",
        "symbol": "AAPL",
        "quantity": 10,
        "confidence": 0.9
    }
    return mock_ai

@pytest.fixture
async def test_database_manager():
    """Create test database manager."""
    from core.database_manager import DatabaseManager
    
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    db_manager = DatabaseManager(db_path)
    await asyncio.to_thread(db_manager.initialize_all_databases)
    
    yield db_manager
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def test_config():
    """Test configuration settings."""
    return {
        "testing": True,
        "database_url": "sqlite:///test_prometheus.db",
        "api_base_url": "http://localhost:8000",
        "mock_trading": True,
        "log_level": "DEBUG"
    }

# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security
