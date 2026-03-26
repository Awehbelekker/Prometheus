"""
PROMETHEUS - Reconnect Interactive Brokers to Running System

This script reconnects Interactive Brokers to the already-running PROMETHEUS system
without disrupting the live trading session.

Usage: python reconnect_ib_to_running_system.py
"""

import asyncio
import logging
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from brokers.interactive_brokers_broker import InteractiveBrokersBroker
    IB_AVAILABLE = True
except ImportError as e:
    logger.error(f"Interactive Brokers broker not available: {e}")
    IB_AVAILABLE = False

async def reconnect_ib():
    """Reconnect Interactive Brokers to the running system"""
    
    if not IB_AVAILABLE:
        logger.error("[ERROR] Interactive Brokers broker module not available!")
        logger.error("Install with: pip install ibapi")
        return False
    
    logger.info("=" * 80)
    logger.info("🔄 RECONNECTING INTERACTIVE BROKERS TO RUNNING PROMETHEUS")
    logger.info("=" * 80)
    
    # IB Configuration (matching the main launcher)
    ib_config = {
        'host': '127.0.0.1',
        'port': 7496,  # LIVE port (7497 is paper)
        'client_id': 2,  # Use different client ID to avoid conflicts
        'paper_trading': False  # LIVE trading
    }
    
    logger.info(f"Connecting to IB TWS/Gateway at {ib_config['host']}:{ib_config['port']}")
    logger.info(f"Client ID: {ib_config['client_id']}")
    logger.info(f"Mode: LIVE TRADING")
    
    try:
        # Create IB broker instance
        ib_broker = InteractiveBrokersBroker(config=ib_config)
        
        # Attempt connection
        logger.info("Attempting connection...")
        connected = await ib_broker.connect()
        
        if connected:
            logger.info("=" * 80)
            logger.info("[CHECK] SUCCESS! INTERACTIVE BROKERS CONNECTED!")
            logger.info("=" * 80)
            
            # Get account info to verify
            try:
                account = await ib_broker.get_account()
                logger.info(f"📊 Account: {account.account_id}")
                logger.info(f"💰 Buying Power: ${account.buying_power:,.2f}")
                logger.info(f"💵 Cash: ${account.cash:,.2f}")
                logger.info(f"📈 Portfolio Value: ${account.portfolio_value:,.2f}")
                logger.info("=" * 80)
            except Exception as e:
                logger.warning(f"Could not fetch account details: {e}")
            
            logger.info("🎉 IB is now connected and ready for stock trading!")
            logger.info("📝 NOTE: The main PROMETHEUS system is still running in Terminal 27")
            logger.info("📝 IB will be available for stock trades during market hours")
            logger.info("📝 Keep this terminal open to maintain the IB connection")
            logger.info("=" * 80)
            
            # Keep connection alive
            logger.info("Keeping connection alive... Press Ctrl+C to disconnect")
            try:
                while True:
                    await asyncio.sleep(60)
                    # Periodic health check
                    if ib_broker.connected:
                        logger.info("[CHECK] IB connection healthy")
                    else:
                        logger.warning("[WARNING]️ IB connection lost - attempting reconnect...")
                        connected = await ib_broker.connect()
                        if connected:
                            logger.info("[CHECK] Reconnected successfully!")
                        else:
                            logger.error("[ERROR] Reconnection failed")
                            break
            except KeyboardInterrupt:
                logger.info("\n🛑 Disconnecting IB...")
                await ib_broker.disconnect()
                logger.info("[CHECK] IB disconnected cleanly")
            
            return True
        else:
            logger.error("=" * 80)
            logger.error("[ERROR] FAILED TO CONNECT TO INTERACTIVE BROKERS")
            logger.error("=" * 80)
            logger.error("Possible reasons:")
            logger.error("1. TWS or IB Gateway is not running")
            logger.error("2. TWS/Gateway is not configured for API connections")
            logger.error("3. Port 7496 is not open or is blocked")
            logger.error("4. API settings in TWS need to be enabled")
            logger.error("")
            logger.error("To fix:")
            logger.error("1. Open TWS or IB Gateway")
            logger.error("2. Go to File > Global Configuration > API > Settings")
            logger.error("3. Enable 'Enable ActiveX and Socket Clients'")
            logger.error("4. Set Socket port to 7496")
            logger.error("5. Add 127.0.0.1 to 'Trusted IP Addresses'")
            logger.error("6. Restart TWS/Gateway and try again")
            logger.error("=" * 80)
            return False
            
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"[ERROR] ERROR CONNECTING TO IB: {e}")
        logger.error("=" * 80)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                             ║")
    print("║         PROMETHEUS - IB RECONNECTION UTILITY                ║")
    print("║                                                             ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("\n")
    
    asyncio.run(reconnect_ib())

