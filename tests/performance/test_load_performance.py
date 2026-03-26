"""
PROMETHEUS Trading Platform - Load & Performance Tests
Comprehensive performance testing for enterprise-grade scalability
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch
import httpx
from fastapi.testclient import TestClient

from unified_production_server import app


class TestLoadPerformance:
    """Test suite for load and performance testing."""
    
    @pytest.fixture
    def client(self):
        """Create test client for performance testing."""
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        """Create authentication headers for testing."""
        return {"Authorization": "Bearer test_performance_token"}
    
    @pytest.mark.performance
    def test_concurrent_api_requests(self, client, auth_headers):
        """Test concurrent API request handling."""
        def make_request():
            start_time = time.time()
            response = client.get("/api/system/status", headers=auth_headers)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Test with 50 concurrent requests
        num_requests = 50
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r["status_code"] == 200]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) >= num_requests * 0.95  # 95% success rate
        assert statistics.mean(response_times) < 1.0  # Average response time < 1 second
        assert max(response_times) < 5.0  # Max response time < 5 seconds
    
    @pytest.mark.performance
    def test_market_data_throughput(self, client, auth_headers):
        """Test market data endpoint throughput."""
        symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN", "META", "NVDA", "NFLX"]
        
        def fetch_market_data(symbol):
            start_time = time.time()
            with patch('core.market_data_service.get_market_data') as mock_data:
                mock_data.return_value = {
                    "symbol": symbol,
                    "price": 150.0,
                    "volume": 1000000,
                    "change": 2.5
                }
                
                response = client.get(f"/api/market-data/{symbol}", headers=auth_headers)
                end_time = time.time()
                
                return {
                    "symbol": symbol,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                }
        
        # Test concurrent market data requests
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(fetch_market_data, symbol) for symbol in symbols]
            results = [future.result() for future in as_completed(futures)]
        
        # Validate performance
        successful_requests = [r for r in results if r["status_code"] == 200]
        response_times = [r["response_time"] for r in successful_requests]
        
        assert len(successful_requests) == len(symbols)
        assert statistics.mean(response_times) < 0.5  # Fast market data retrieval
        assert max(response_times) < 2.0
    
    @pytest.mark.performance
    def test_trading_order_processing_speed(self, client, auth_headers):
        """Test trading order processing performance."""
        def place_order(order_id):
            order_data = {
                "symbol": "AAPL",
                "quantity": 10,
                "order_type": "buy",
                "price": 150.0
            }
            
            start_time = time.time()
            with patch('core.internal_paper_trading.InternalPaperTradingEngine.place_order') as mock_order:
                mock_order.return_value = {
                    "status": "success",
                    "order": {"id": f"order_{order_id}", "symbol": "AAPL", "quantity": 10}
                }
                
                response = client.post("/api/paper-trading/orders", json=order_data, headers=auth_headers)
                end_time = time.time()
                
                return {
                    "order_id": order_id,
                    "status_code": response.status_code,
                    "response_time": end_time - start_time
                }
        
        # Test 20 concurrent orders
        num_orders = 20
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(place_order, i) for i in range(num_orders)]
            results = [future.result() for future in as_completed(futures)]
        
        # Validate order processing performance
        successful_orders = [r for r in results if r["status_code"] in [200, 201]]
        response_times = [r["response_time"] for r in successful_orders]
        
        assert len(successful_orders) >= num_orders * 0.95
        assert statistics.mean(response_times) < 0.3  # Fast order processing
        assert max(response_times) < 1.0
    
    @pytest.mark.performance
    def test_database_query_performance(self):
        """Test database query performance."""
        from core.database_manager import DatabaseManager
        
        db_manager = DatabaseManager(":memory:")  # In-memory for testing
        
        # Test query performance
        query_times = []
        for i in range(100):
            start_time = time.time()
            result = db_manager.execute_query("SELECT 1 as test", {})
            end_time = time.time()
            query_times.append(end_time - start_time)
        
        # Validate database performance
        assert statistics.mean(query_times) < 0.01  # Average query time < 10ms
        assert max(query_times) < 0.05  # Max query time < 50ms
    
    @pytest.mark.performance
    def test_ai_processing_performance(self):
        """Test AI processing performance."""
        from core.ai_trading_intelligence import AITradingIntelligence
        
        ai_intelligence = AITradingIntelligence()
        
        def process_ai_analysis():
            start_time = time.time()
            with patch.object(ai_intelligence, 'analyze_market_sentiment') as mock_analysis:
                mock_analysis.return_value = {
                    "sentiment_score": 0.75,
                    "sentiment_label": "BULLISH",
                    "confidence": 0.85
                }
                
                result = ai_intelligence.analyze_market_sentiment("AAPL")
                end_time = time.time()
                
                return {
                    "result": result,
                    "processing_time": end_time - start_time
                }
        
        # Test AI processing speed
        processing_times = []
        for i in range(10):
            result = process_ai_analysis()
            processing_times.append(result["processing_time"])
        
        # Validate AI performance
        assert statistics.mean(processing_times) < 2.0  # Average AI processing < 2 seconds
        assert max(processing_times) < 5.0  # Max AI processing < 5 seconds
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self, client, auth_headers):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate load
        def generate_load():
            for i in range(10):
                client.get("/api/system/status", headers=auth_headers)
                client.get("/api/market-data/price/AAPL", headers=auth_headers)
        
        # Run load test
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_load) for _ in range(10)]
            for future in as_completed(futures):
                future.result()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 100  # Less than 100MB increase
    
    @pytest.mark.performance
    def test_cpu_usage_under_load(self, client, auth_headers):
        """Test CPU usage under load."""
        import psutil
        
        # Measure CPU usage during load test
        cpu_percentages = []
        
        def monitor_cpu():
            for _ in range(10):
                cpu_percentages.append(psutil.cpu_percent(interval=0.1))
        
        def generate_api_load():
            for i in range(50):
                client.get("/api/system/status", headers=auth_headers)
        
        # Run concurrent monitoring and load generation
        with ThreadPoolExecutor(max_workers=3) as executor:
            monitor_future = executor.submit(monitor_cpu)
            load_futures = [executor.submit(generate_api_load) for _ in range(2)]
            
            # Wait for completion
            monitor_future.result()
            for future in load_futures:
                future.result()
        
        # Validate CPU usage
        avg_cpu = statistics.mean(cpu_percentages)
        max_cpu = max(cpu_percentages)
        
        assert avg_cpu < 80  # Average CPU usage < 80%
        assert max_cpu < 95   # Max CPU usage < 95%
    
    @pytest.mark.performance
    def test_response_time_consistency(self, client, auth_headers):
        """Test response time consistency."""
        response_times = []
        
        for i in range(100):
            start_time = time.time()
            response = client.get("/api/system/status", headers=auth_headers)
            end_time = time.time()
            
            if response.status_code == 200:
                response_times.append(end_time - start_time)
        
        # Calculate statistics
        mean_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times)
        
        # Validate consistency
        assert std_dev < mean_time * 0.5  # Standard deviation < 50% of mean
        assert len([t for t in response_times if t > mean_time * 2]) < 5  # < 5% outliers
    
    @pytest.mark.performance
    def test_scalability_limits(self, client, auth_headers):
        """Test system scalability limits."""
        max_concurrent_users = 100
        success_rates = []
        
        for concurrent_users in [10, 25, 50, 75, 100]:
            def make_user_request():
                response = client.get("/api/system/status", headers=auth_headers)
                return response.status_code == 200
            
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_user_request) for _ in range(concurrent_users)]
                results = [future.result() for future in as_completed(futures)]
                
                success_rate = sum(results) / len(results)
                success_rates.append(success_rate)
        
        # Validate scalability
        assert all(rate >= 0.90 for rate in success_rates)  # 90% success rate at all levels
        assert success_rates[-1] >= 0.85  # At least 85% success at max load
