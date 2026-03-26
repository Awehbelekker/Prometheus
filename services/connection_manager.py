"""
🌐 CONNECTION MANAGER
Robust connection handling with auto-reconnect capabilities
"""

import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import os
import time

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    🔄 ROBUST CONNECTION MANAGEMENT
    
    Features:
    - Automatic reconnection on network failure
    - Connection health monitoring  
    - Bandwidth optimization
    - Multiple backup connections
    - Sleep/wake detection
    - Exponential backoff retry
    """
    
    def __init__(self):
        self.connections = {}
        self.health_status = {}
        self.backup_connections = {}
        self.session = None
        self.last_check = None
        self.connection_timeout = 30
        self.retry_delays = [1, 2, 5, 10, 30, 60]  # Exponential backoff
        self.max_retries = len(self.retry_delays)
        
        # Connection monitoring
        self.connection_failures = {}
        self.last_successful_ping = {}
        
        # System state
        self.system_sleeping = False
        self.last_wake_time = None
        
    async def initialize(self):
        """Initialize connection manager with persistent session"""
        
        try:
            # Create optimized HTTP session
            timeout = aiohttp.ClientTimeout(
                total=self.connection_timeout,
                connect=10,
                sock_read=20
            )
            
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
                use_dns_cache=True,
                ttl_dns_cache=300,
                family=0  # Allow both IPv4 and IPv6
            )
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    'User-Agent': 'Prometheus-Trading-App/1.0',
                    'Accept': 'application/json',
                    'Connection': 'keep-alive'
                }
            )
            
            # Initialize connection tracking
            self.last_check = datetime.utcnow()
            
            logger.info("[CHECK] Connection Manager initialized with optimized session")
            
        except Exception as e:
            logger.error(f"[ERROR] Connection Manager initialization failed: {str(e)}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all connections"""
        
        health_results = {}
        
        try:
            # Check internet connectivity
            health_results['internet'] = await self._check_internet_connection()
            
            # Check broker connectivity  
            health_results['broker'] = await self._check_broker_connection()
            
            # Check data feed connections
            health_results['data_feeds'] = await self._check_data_feeds()
            
            # Check API endpoints
            health_results['api_endpoints'] = await self._check_api_endpoints()
            
            # Overall health calculation
            connection_scores = [
                health_results['internet'],
                health_results['broker'],
                health_results['data_feeds'],
                health_results['api_endpoints']
            ]
            
            overall_health = sum(score for score in connection_scores if isinstance(score, (int, float))) / len(connection_scores)
            
            health_results['overall_score'] = overall_health
            health_results['status'] = 'healthy' if overall_health >= 0.8 else 'degraded' if overall_health >= 0.5 else 'unhealthy'
            health_results['timestamp'] = datetime.utcnow().isoformat()
            
            # Update internal state
            self.health_status = health_results
            self.last_check = datetime.utcnow()
            
            return health_results
            
        except Exception as e:
            logger.error(f"[ERROR] Health check failed: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_internet_connection(self) -> float:
        """Check basic internet connectivity with multiple endpoints"""
        
        test_endpoints = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://1.1.1.1',
            'https://8.8.8.8'
        ]
        
        successful_connections = 0
        
        for endpoint in test_endpoints:
            try:
                start_time = time.time()
                async with self.session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200 and response_time < 3.0:
                        successful_connections += 1
                        self.last_successful_ping[endpoint] = datetime.utcnow()
                    
            except Exception as e:
                self.connection_failures[endpoint] = str(e)
                logger.debug(f"Connection test failed for {endpoint}: {str(e)}")
        
        return successful_connections / len(test_endpoints)
    
    async def _check_broker_connection(self) -> float:
        """Check broker API connectivity"""
        
        broker_endpoints = [
            'https://paper-api.alpaca.markets/v2/account',
            'https://api.alpaca.markets/v2/account'
        ]
        
        successful_connections = 0
        
        for endpoint in broker_endpoints:
            try:
                async with self.session.get(endpoint, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    # 401 is expected without auth, but means API is working
                    if response.status in [200, 401]:
                        successful_connections += 1
                        self.last_successful_ping[endpoint] = datetime.utcnow()
                    
            except Exception as e:
                self.connection_failures[endpoint] = str(e)
                logger.debug(f"Broker connectivity test failed for {endpoint}: {str(e)}")
        
        return successful_connections / len(broker_endpoints) if broker_endpoints else 0
    
    async def _check_data_feeds(self) -> float:
        """Check data feed connections"""
        
        data_feed_endpoints = [
            'https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT',
            'https://api.coinbase.com/v2/exchange-rates',
            'https://api.polygon.io/v2/aggs/ticker/AAPL/prev',
            'https://finnhub.io/api/v1/quote?symbol=AAPL'
        ]
        
        successful_connections = 0
        
        for endpoint in data_feed_endpoints:
            try:
                headers = {}
                if 'polygon.io' in endpoint:
                    headers['Authorization'] = f"Bearer {os.getenv('POLYGON_API_KEY', '')}"
                elif 'finnhub.io' in endpoint:
                    endpoint += f"&token={os.getenv('FINNHUB_API_KEY', 'demo')}"
                
                async with self.session.get(endpoint, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data:  # Ensure we got actual data
                            successful_connections += 1
                            self.last_successful_ping[endpoint] = datetime.utcnow()
                    
            except Exception as e:
                self.connection_failures[endpoint] = str(e)
                logger.debug(f"Data feed test failed for {endpoint}: {str(e)}")
        
        return successful_connections / len(data_feed_endpoints)
    
    async def _check_api_endpoints(self) -> float:
        """Check critical API endpoints"""
        
        api_endpoints = [
            'https://api.github.com/zen',
            'https://httpbin.org/status/200',
            'https://jsonplaceholder.typicode.com/posts/1'
        ]
        
        successful_connections = 0
        
        for endpoint in api_endpoints:
            try:
                async with self.session.get(endpoint, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        successful_connections += 1
                        self.last_successful_ping[endpoint] = datetime.utcnow()
                    
            except Exception as e:
                self.connection_failures[endpoint] = str(e)
                logger.debug(f"API endpoint test failed for {endpoint}: {str(e)}")
        
        return successful_connections / len(api_endpoints)
    
    async def wait_for_connection(self, timeout: int = 300) -> bool:
        """Wait for internet connection to be restored"""
        
        logger.info("🔄 Waiting for connection to be restored...")
        
        start_time = time.time()
        retry_count = 0
        
        while time.time() - start_time < timeout:
            try:
                # Test basic connectivity
                async with self.session.get('https://www.google.com', timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        logger.info("[CHECK] Connection restored!")
                        await self._handle_connection_restored()
                        return True
                
            except Exception as e:
                retry_count += 1
                delay = self.retry_delays[min(retry_count - 1, len(self.retry_delays) - 1)]
                
                logger.debug(f"Connection attempt {retry_count} failed: {str(e)}")
                logger.info(f"⏳ Retrying in {delay} seconds...")
                
                await asyncio.sleep(delay)
        
        logger.error(f"[ERROR] Connection not restored within {timeout} seconds")
        return False
    
    async def _handle_connection_restored(self):
        """Handle connection restoration"""
        
        try:
            # Clear failure tracking
            self.connection_failures.clear()
            
            # Update last wake time if this was after system sleep
            if self.system_sleeping:
                self.last_wake_time = datetime.utcnow()
                self.system_sleeping = False
                logger.info("🌅 System wake detected - connections restored")
            
            # Run full health check
            await self.health_check()
            
        except Exception as e:
            logger.error(f"[ERROR] Connection restoration handling failed: {str(e)}")
    
    async def handle_system_sleep(self):
        """Handle system going to sleep"""
        
        logger.info("💤 System sleep detected")
        
        try:
            # Mark system as sleeping
            self.system_sleeping = True
            
            # Close current session to prevent connection issues
            if self.session:
                await self.session.close()
                self.session = None
            
            # Save current state
            sleep_state = {
                'sleep_time': datetime.utcnow().isoformat(),
                'health_status': self.health_status,
                'last_check': self.last_check.isoformat() if self.last_check else None
            }
            
            with open('sleep_state.json', 'w') as f:
                json.dump(sleep_state, f, indent=2)
            
        except Exception as e:
            logger.error(f"[ERROR] Sleep handling failed: {str(e)}")
    
    async def handle_system_wake(self):
        """Handle system waking up"""
        
        logger.info("🌅 System wake detected")
        
        try:
            # Re-initialize session
            await self.initialize()
            
            # Wait for connections to stabilize
            await asyncio.sleep(5)
            
            # Wait for connection restoration
            connection_restored = await self.wait_for_connection(timeout=60)
            
            if connection_restored:
                logger.info("[CHECK] All connections restored after wake")
            else:
                logger.warning("[WARNING]️ Some connections may still be unstable after wake")
            
            # Load previous state if available
            try:
                if os.path.exists('sleep_state.json'):
                    with open('sleep_state.json', 'r') as f:
                        sleep_state = json.load(f)
                    
                    sleep_time = datetime.fromisoformat(sleep_state['sleep_time'])
                    sleep_duration = datetime.utcnow() - sleep_time
                    
                    logger.info(f"📊 System was asleep for {sleep_duration}")
                    
                    # Clean up sleep state file
                    os.remove('sleep_state.json')
                    
            except Exception as e:
                logger.debug(f"Sleep state recovery failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"[ERROR] Wake handling failed: {str(e)}")
    
    async def send_heartbeat(self, data: Dict[str, Any]):
        """Send heartbeat to monitoring systems"""
        
        try:
            # Add connection health to heartbeat
            heartbeat_data = {
                **data,
                'connection_health': self.health_status,
                'last_connection_check': self.last_check.isoformat() if self.last_check else None,
                'system_sleeping': self.system_sleeping,
                'last_wake_time': self.last_wake_time.isoformat() if self.last_wake_time else None
            }
            
            # Save heartbeat locally
            with open('heartbeat.json', 'w') as f:
                json.dump(heartbeat_data, f, indent=2)
            
            # Try to send to external monitoring (if configured)
            monitoring_endpoint = os.getenv('MONITORING_ENDPOINT')
            if monitoring_endpoint and self.session:
                try:
                    async with self.session.post(monitoring_endpoint, json=heartbeat_data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                        if response.status == 200:
                            logger.debug("[CHECK] Heartbeat sent to external monitoring")
                        else:
                            logger.debug(f"[WARNING]️ Heartbeat response: {response.status}")
                except Exception as e:
                    logger.debug(f"External heartbeat failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"[ERROR] Heartbeat failed: {str(e)}")
    
    async def test_specific_connection(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Test a specific connection endpoint"""
        
        try:
            start_time = time.time()
            
            async with self.session.get(url, headers=headers or {}, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time = time.time() - start_time
                
                return {
                    'url': url,
                    'status': response.status,
                    'response_time': response_time,
                    'success': response.status == 200,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'url': url,
                'status': None,
                'response_time': None,
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get detailed connection statistics"""
        
        return {
            'health_status': self.health_status,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'connection_failures': dict(self.connection_failures),
            'last_successful_pings': {
                endpoint: timestamp.isoformat() 
                for endpoint, timestamp in self.last_successful_ping.items()
            },
            'system_sleeping': self.system_sleeping,
            'last_wake_time': self.last_wake_time.isoformat() if self.last_wake_time else None,
            'session_active': self.session is not None and not self.session.closed
        }
    
    async def cleanup(self):
        """Cleanup connection manager resources"""
        
        try:
            if self.session and not self.session.closed:
                await self.session.close()
                
            logger.info("[CHECK] Connection Manager cleaned up")
            
        except Exception as e:
            logger.error(f"[ERROR] Connection cleanup failed: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, 'session') and self.session and not self.session.closed:
                # Schedule cleanup in event loop if available
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.session.close())
        except:
            pass
