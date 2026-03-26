#!/usr/bin/env python3
"""
Enhanced Trading System Demo
Demonstrates the improved error handling, fallback systems, and monitoring
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import enhanced components
from core.error_handling import (
    error_logger, error_recovery_manager, error_database,
    ConnectionError, MarketDataError, TradingError
)
from core.fallback_data_sources import (
    fallback_data_manager, broker_failover_manager,
    get_market_data_with_fallback
)
from core.error_monitoring_dashboard import (
    error_monitoring_dashboard, start_error_monitoring,
    get_error_dashboard_data, export_error_report
)

# Import brokers
from brokers.interactive_brokers_broker import InteractiveBrokersBroker
from brokers.alpaca_broker import AlpacaBroker

class EnhancedTradingSystem:
    """Enhanced trading system with comprehensive error handling"""
    
    def __init__(self):
        self.ib_broker = None
        self.alpaca_broker = None
        self.monitoring_active = False
        
    async def initialize(self):
        """Initialize the enhanced trading system"""
        logger.info("🚀 Initializing Enhanced Trading System")
        
        # Initialize brokers with enhanced error handling
        await self._initialize_brokers()
        
        # Set up broker failover
        if self.ib_broker and self.alpaca_broker:
            broker_failover_manager.set_brokers(self.ib_broker, self.alpaca_broker)
            logger.info("✅ Broker failover system configured")
        
        # Start error monitoring
        await self._start_monitoring()
        
        logger.info("✅ Enhanced Trading System initialized successfully")
    
    async def _initialize_brokers(self):
        """Initialize brokers with proper error handling"""
        # Initialize IB Broker
        try:
            ib_config = {
                'host': '127.0.0.1',
                'port': 7497,  # TWS paper trading
                'client_id': 1,
                'paper_trading': True,
                'account_id': 'U21922116'
            }
            
            self.ib_broker = InteractiveBrokersBroker(ib_config)
            ib_connected = await self.ib_broker.connect()
            
            if ib_connected:
                logger.info("✅ Interactive Brokers connected successfully")
            else:
                logger.warning("⚠️ Interactive Brokers connection failed - will use fallback")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize IB broker: {e}")
            self.ib_broker = None
        
        # Initialize Alpaca Broker
        try:
            alpaca_config = {
                'api_key': os.getenv('ALPACA_PAPER_KEY'),
                'secret_key': os.getenv('ALPACA_PAPER_SECRET'),
                'paper_trading': True
            }
            
            self.alpaca_broker = AlpacaBroker(alpaca_config)
            alpaca_connected = await self.alpaca_broker.connect()
            
            if alpaca_connected:
                logger.info("✅ Alpaca connected successfully")
            else:
                logger.warning("⚠️ Alpaca connection failed - will use fallback")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Alpaca broker: {e}")
            self.alpaca_broker = None
    
    async def _start_monitoring(self):
        """Start error monitoring system"""
        try:
            # Start monitoring in background
            asyncio.create_task(start_error_monitoring())
            self.monitoring_active = True
            logger.info("✅ Error monitoring started")
        except Exception as e:
            logger.error(f"❌ Failed to start monitoring: {e}")
    
    async def get_market_data_demo(self, symbol: str = "AAPL"):
        """Demonstrate enhanced market data retrieval with fallback"""
        logger.info(f"📊 Getting market data for {symbol}")
        
        try:
            # Try with failover system
            if self.ib_broker or self.alpaca_broker:
                data = await get_market_data_with_fallback(
                    symbol, 
                    self.ib_broker, 
                    self.alpaca_broker
                )
            else:
                # Use fallback data sources only
                data = await get_market_data_with_fallback(symbol)
            
            logger.info(f"✅ Market data retrieved: {data}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Failed to get market data for {symbol}: {e}")
            return None
    
    async def demonstrate_error_handling(self):
        """Demonstrate error handling capabilities"""
        logger.info("🔧 Demonstrating error handling capabilities")
        
        # Test with invalid symbol
        try:
            await self.get_market_data_demo("INVALID_SYMBOL_12345")
        except Exception as e:
            logger.info(f"✅ Error handling working: {type(e).__name__}")
        
        # Test with empty symbol
        try:
            await self.get_market_data_demo("")
        except Exception as e:
            logger.info(f"✅ Validation working: {type(e).__name__}")
    
    async def get_system_status(self):
        """Get comprehensive system status"""
        logger.info("📈 Getting system status")
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'brokers': {
                'ib_connected': self.ib_broker.connected if self.ib_broker else False,
                'alpaca_connected': self.alpaca_broker.connected if self.alpaca_broker else False
            },
            'failover_status': broker_failover_manager.get_failover_status(),
            'error_dashboard': get_error_dashboard_data(hours=1),
            'fallback_providers': fallback_data_manager.get_provider_status()
        }
        
        return status
    
    async def run_comprehensive_test(self):
        """Run comprehensive system test"""
        logger.info("🧪 Running comprehensive system test")
        
        test_symbols = ["AAPL", "MSFT", "GOOGL", "TSLA", "INVALID"]
        
        results = {
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_usage': 0,
            'errors': []
        }
        
        for symbol in test_symbols:
            try:
                data = await self.get_market_data_demo(symbol)
                if data:
                    results['successful_requests'] += 1
                    if 'fallback' in data.get('source', ''):
                        results['fallback_usage'] += 1
                else:
                    results['failed_requests'] += 1
            except Exception as e:
                results['failed_requests'] += 1
                results['errors'].append(str(e))
        
        logger.info(f"📊 Test Results: {results}")
        return results
    
    async def generate_error_report(self):
        """Generate comprehensive error report"""
        logger.info("📋 Generating error report")
        
        try:
            # Get dashboard data
            dashboard_data = get_error_dashboard_data(hours=24)
            
            # Export error report
            report = export_error_report(hours=24, format='json')
            
            # Save report to file
            report_file = f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                f.write(report)
            
            logger.info(f"✅ Error report saved to {report_file}")
            
            # Print summary
            if isinstance(dashboard_data, dict) and 'error_summary' in dashboard_data:
                summary = dashboard_data['error_summary']
                logger.info("📊 Error Summary (24h):")
                logger.info(f"   Total Errors: {summary.get('total_errors', 0)}")
                logger.info(f"   Critical Errors: {summary.get('critical_errors', 0)}")
                logger.info(f"   Errors by Broker: {summary.get('error_by_broker', {})}")
            
            return report_file
            
        except Exception as e:
            logger.error(f"❌ Failed to generate error report: {e}")
            return None
    
    async def shutdown(self):
        """Shutdown the system gracefully"""
        logger.info("🛑 Shutting down Enhanced Trading System")
        
        # Stop monitoring
        if self.monitoring_active:
            await error_monitoring_dashboard.stop_monitoring()
        
        # Disconnect brokers
        if self.ib_broker:
            await self.ib_broker.disconnect()
        
        if self.alpaca_broker:
            await self.alpaca_broker.disconnect()
        
        logger.info("✅ System shutdown complete")

async def main():
    """Main demo function"""
    system = EnhancedTradingSystem()
    
    try:
        # Initialize system
        await system.initialize()
        
        # Wait a moment for monitoring to start
        await asyncio.sleep(2)
        
        # Get system status
        status = await system.get_system_status()
        logger.info(f"📊 System Status: {status}")
        
        # Run comprehensive test
        test_results = await system.run_comprehensive_test()
        
        # Demonstrate error handling
        await system.demonstrate_error_handling()
        
        # Get market data for a few symbols
        symbols = ["AAPL", "MSFT", "GOOGL"]
        for symbol in symbols:
            await system.get_market_data_demo(symbol)
            await asyncio.sleep(1)  # Brief pause between requests
        
        # Generate error report
        report_file = await system.generate_error_report()
        
        # Final status check
        final_status = await system.get_system_status()
        logger.info("📊 Final System Status:")
        logger.info(f"   Brokers: {final_status['brokers']}")
        logger.info(f"   Failover Active: {final_status['failover_status']['failover_active']}")
        
        logger.info("✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
    finally:
        # Cleanup
        await system.shutdown()

if __name__ == "__main__":
    print("🚀 Enhanced Trading System Demo")
    print("=" * 50)
    print("This demo showcases:")
    print("✅ Enhanced error handling framework")
    print("✅ Broker connection validation")
    print("✅ Automatic failover systems")
    print("✅ Fallback data sources")
    print("✅ Real-time error monitoring")
    print("✅ Comprehensive error reporting")
    print("=" * 50)
    
    # Run the demo
    asyncio.run(main())
