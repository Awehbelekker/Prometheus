"""
PROMETHEUS Trading Platform - API Endpoints Integration Tests
Comprehensive tests for API endpoint integration
"""

import pytest
import asyncio
import httpx
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Import the main server
from unified_production_server import app


class TestAPIEndpoints:
    """Test suite for API endpoint integration."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self, client):
        """Create authentication headers for testing."""
        # Mock login to get auth token
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        with patch('core.auth.unified_auth_service.UnifiedAuthService.authenticate_user') as mock_auth:
            mock_auth.return_value = {
                "status": "success",
                "access_token": "test_token_123",
                "user": {"username": "testuser", "role": "trader"}
            }
            
            response = client.post("/api/auth/login", json=login_data)
            token = response.json().get("access_token", "test_token_123")
            
            return {"Authorization": f"Bearer {token}"}
    
    @pytest.mark.integration
    def test_health_check_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()
    
    @pytest.mark.integration
    def test_system_status_endpoint(self, client, auth_headers):
        """Test system status endpoint."""
        response = client.get("/api/system/status", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "trading_engines" in data
        assert "database_status" in data
        assert "market_data_status" in data
    
    @pytest.mark.integration
    def test_user_authentication_flow(self, client):
        """Test complete user authentication flow."""
        # Test registration
        register_data = {
            "username": "integrationtest",
            "email": "integration@test.com",
            "password": "SecurePassword123!",
            "role": "trader"
        }
        
        with patch('core.auth.unified_auth_service.UnifiedAuthService.register_user') as mock_register:
            mock_register.return_value = {
                "status": "success",
                "user_id": "test_user_123"
            }
            
            response = client.post("/api/auth/register", json=register_data)
            assert response.status_code == 201
            assert response.json()["status"] == "success"
        
        # Test login
        login_data = {
            "username": "integrationtest",
            "password": "SecurePassword123!"
        }
        
        with patch('core.auth.unified_auth_service.UnifiedAuthService.authenticate_user') as mock_login:
            mock_login.return_value = {
                "status": "success",
                "access_token": "integration_token_123",
                "user": {"username": "integrationtest", "role": "trader"}
            }
            
            response = client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            assert "access_token" in response.json()
    
    @pytest.mark.integration
    def test_paper_trading_endpoints(self, client, auth_headers):
        """Test paper trading API endpoints."""
        # Test get portfolio
        with patch('core.internal_paper_trading.InternalPaperTradingEngine.get_portfolio') as mock_portfolio:
            mock_portfolio.return_value = {
                "total_value": 10000.0,
                "cash": 5000.0,
                "positions": {"AAPL": {"quantity": 10, "value": 1500.0}}
            }
            
            response = client.get("/api/paper-trading/portfolio", headers=auth_headers)
            assert response.status_code == 200
            assert "total_value" in response.json()
        
        # Test place order
        order_data = {
            "symbol": "AAPL",
            "quantity": 10,
            "order_type": "buy",
            "price": 150.0
        }
        
        with patch('core.internal_paper_trading.InternalPaperTradingEngine.place_order') as mock_order:
            mock_order.return_value = {
                "status": "success",
                "order": {"id": "order_123", "symbol": "AAPL", "quantity": 10}
            }
            
            response = client.post("/api/paper-trading/orders", json=order_data, headers=auth_headers)
            assert response.status_code == 201
            assert response.json()["status"] == "success"
    
    @pytest.mark.integration
    def test_market_data_endpoints(self, client, auth_headers):
        """Test market data API endpoints."""
        # Test real-time price
        with patch('core.market_data_service.get_real_time_price') as mock_price:
            mock_price.return_value = 150.25
            
            response = client.get("/api/market-data/price/AAPL", headers=auth_headers)
            assert response.status_code == 200
            assert response.json()["price"] == 150.25
        
        # Test market data feed
        with patch('core.market_data_service.get_market_data') as mock_data:
            mock_data.return_value = {
                "symbol": "AAPL",
                "price": 150.25,
                "volume": 1000000,
                "change": 2.5,
                "change_percent": 1.69
            }
            
            response = client.get("/api/market-data/AAPL", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "AAPL"
            assert "price" in data
            assert "volume" in data
    
    @pytest.mark.integration
    def test_ai_trading_endpoints(self, client, auth_headers):
        """Test AI trading intelligence endpoints."""
        # Test market sentiment analysis
        with patch('core.ai_trading_intelligence.AITradingIntelligence.analyze_market_sentiment') as mock_sentiment:
            mock_sentiment.return_value = {
                "sentiment_score": 0.75,
                "sentiment_label": "BULLISH",
                "confidence": 0.85
            }
            
            response = client.get("/api/ai/sentiment/AAPL", headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert "sentiment_score" in data
            assert "sentiment_label" in data
        
        # Test trading signal generation
        with patch('core.ai_trading_intelligence.AITradingIntelligence.generate_trading_signal') as mock_signal:
            mock_signal.return_value = {
                "action": "buy",
                "confidence": 0.9,
                "target_price": 155.0,
                "stop_loss": 145.0
            }
            
            response = client.post("/api/ai/signal", json={"symbol": "AAPL"}, headers=auth_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["action"] in ["buy", "sell", "hold"]
            assert "confidence" in data
    
    @pytest.mark.integration
    def test_revolutionary_engines_endpoints(self, client, auth_headers):
        """Test revolutionary trading engines endpoints."""
        # Test crypto engine status
        response = client.get("/api/revolutionary/crypto/status", headers=auth_headers)
        assert response.status_code == 200
        assert "is_active" in response.json()
        
        # Test options engine capabilities
        response = client.get("/api/revolutionary/options/strategies", headers=auth_headers)
        assert response.status_code == 200
        assert "supported_strategies" in response.json()
        
        # Test advanced engine features
        response = client.get("/api/revolutionary/advanced/features", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "dma_enabled" in data
        assert "vwap_enabled" in data
        assert "twap_enabled" in data
    
    @pytest.mark.integration
    def test_admin_endpoints(self, client):
        """Test admin-specific endpoints."""
        # Create admin auth headers
        admin_headers = {"Authorization": "Bearer admin_token_123"}
        
        with patch('core.auth.unified_auth_service.UnifiedAuthService.validate_jwt_token') as mock_validate:
            mock_validate.return_value = {
                "user_id": "admin_123",
                "username": "admin",
                "role": "admin"
            }
            
            # Test user management
            response = client.get("/api/admin/users", headers=admin_headers)
            assert response.status_code == 200
            
            # Test system metrics
            response = client.get("/api/admin/metrics", headers=admin_headers)
            assert response.status_code == 200
            
            # Test fund allocation
            allocation_data = {
                "user_id": "trader_123",
                "amount": 50000.0,
                "approved": True
            }
            
            response = client.post("/api/admin/fund-allocation", json=allocation_data, headers=admin_headers)
            assert response.status_code == 201
    
    @pytest.mark.integration
    def test_error_handling(self, client, auth_headers):
        """Test API error handling."""
        # Test invalid endpoint
        response = client.get("/api/nonexistent/endpoint", headers=auth_headers)
        assert response.status_code == 404
        
        # Test invalid data
        invalid_order = {
            "symbol": "",  # Invalid empty symbol
            "quantity": -10,  # Invalid negative quantity
            "order_type": "invalid_type"
        }
        
        response = client.post("/api/paper-trading/orders", json=invalid_order, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # Test unauthorized access
        response = client.get("/api/admin/users")  # No auth headers
        assert response.status_code == 401
    
    @pytest.mark.integration
    def test_rate_limiting(self, client, auth_headers):
        """Test API rate limiting."""
        # Make multiple rapid requests
        responses = []
        for i in range(10):
            response = client.get("/api/market-data/price/AAPL", headers=auth_headers)
            responses.append(response.status_code)
        
        # Should have some successful requests
        assert 200 in responses
        
        # Rate limiting implementation would return 429 for excessive requests
        # This test validates the endpoint can handle rapid requests
    
    @pytest.mark.integration
    async def test_websocket_connections(self, client):
        """Test WebSocket connections for real-time data."""
        # This would test WebSocket endpoints if implemented
        # For now, we'll test the HTTP equivalent
        
        with patch('core.market_data_service.get_real_time_feed') as mock_feed:
            mock_feed.return_value = {
                "symbol": "AAPL",
                "price": 150.25,
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            # Test real-time data endpoint
            response = client.get("/api/market-data/realtime/AAPL")
            assert response.status_code == 200
            assert "price" in response.json()
    
    @pytest.mark.integration
    def test_database_integration(self, client, auth_headers):
        """Test database integration through API endpoints."""
        # Test data persistence through API calls
        order_data = {
            "symbol": "MSFT",
            "quantity": 5,
            "order_type": "buy",
            "price": 300.0
        }
        
        with patch('core.internal_paper_trading.InternalPaperTradingEngine.place_order') as mock_order:
            mock_order.return_value = {
                "status": "success",
                "order": {"id": "order_456", "symbol": "MSFT", "quantity": 5}
            }
            
            # Place order
            response = client.post("/api/paper-trading/orders", json=order_data, headers=auth_headers)
            assert response.status_code == 201
            
            # Verify order in history
            with patch('core.internal_paper_trading.InternalPaperTradingEngine.get_order_history') as mock_history:
                mock_history.return_value = [
                    {"id": "order_456", "symbol": "MSFT", "quantity": 5, "status": "filled"}
                ]
                
                response = client.get("/api/paper-trading/orders/history", headers=auth_headers)
                assert response.status_code == 200
                orders = response.json()
                assert len(orders) >= 1
                assert orders[0]["symbol"] == "MSFT"
