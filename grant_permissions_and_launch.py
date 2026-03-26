#!/usr/bin/env python3
"""
🚀 GRANT PERMISSIONS AND LAUNCH ENHANCED SESSIONS
Grant necessary permissions and launch enhanced risk-managed sessions
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import the existing enhanced systems
from core.enhanced_paper_trading_system import EnhancedPaperTradingSystem, SessionType, SessionStatus
from core.dual_tier_permission_system import dual_tier_system, TradingPermission

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"permissions_and_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def grant_permissions_and_launch():
    """Grant permissions and launch enhanced sessions"""
    logger.info("🔐 GRANTING PERMISSIONS AND LAUNCHING ENHANCED SESSIONS")
    logger.info("=" * 60)
    
    # Grant permissions to system users
    users_to_grant = ["enhanced_24h", "enhanced_48h", "enhanced_week", "system_user"]
    
    for user_id in users_to_grant:
        try:
            # Grant paper trading permission
            dual_tier_system.grant_permission(user_id, TradingPermission.PAPER_TRADING)
            logger.info(f"[CHECK] Granted paper trading permission to {user_id}")
            
            # Grant live trading permission (for future use)
            dual_tier_system.grant_permission(user_id, TradingPermission.LIVE_TRADING)
            logger.info(f"[CHECK] Granted live trading permission to {user_id}")
            
        except Exception as e:
            logger.error(f"[ERROR] Error granting permissions to {user_id}: {e}")
    
    logger.info("=" * 60)
    
    # Initialize the enhanced paper trading system
    paper_trading_system = EnhancedPaperTradingSystem()
    paper_trading_system.start_market_data_feed()
    
    logger.info("🚀 Enhanced Paper Trading System initialized")
    logger.info("[CHECK] Market data feed started")
    logger.info("🛡️ Full risk management active")
    
    active_sessions = []
    
    # Create 24-hour session
    try:
        logger.info("🎯 Creating Enhanced 24-hour session with $10,000.00")
        session_24h = await paper_trading_system.create_paper_session(
            user_id="enhanced_24h",
            session_type=SessionType.QUICK_24H,
            starting_capital=10000.0
        )
        
        if session_24h:
            logger.info(f"[CHECK] 24-hour session created: {session_24h}")
            success = await paper_trading_system.start_session(session_24h)
            if success:
                logger.info("🚀 24-hour session started successfully!")
                active_sessions.append(("24-hour", session_24h))
            else:
                logger.error("[ERROR] Failed to start 24-hour session")
        else:
            logger.error("[ERROR] Failed to create 24-hour session")
    except Exception as e:
        logger.error(f"[ERROR] Error with 24-hour session: {e}")
    
    # Create 48-hour session
    try:
        logger.info("🎯 Creating Enhanced 48-hour session with $10,000.00")
        session_48h = await paper_trading_system.create_paper_session(
            user_id="enhanced_48h",
            session_type=SessionType.EXTENDED_48H,
            starting_capital=10000.0
        )
        
        if session_48h:
            logger.info(f"[CHECK] 48-hour session created: {session_48h}")
            success = await paper_trading_system.start_session(session_48h)
            if success:
                logger.info("🚀 48-hour session started successfully!")
                active_sessions.append(("48-hour", session_48h))
            else:
                logger.error("[ERROR] Failed to start 48-hour session")
        else:
            logger.error("[ERROR] Failed to create 48-hour session")
    except Exception as e:
        logger.error(f"[ERROR] Error with 48-hour session: {e}")
    
    # Create week session
    try:
        logger.info("🎯 Creating Enhanced Week session with $10,000.00")
        session_week = await paper_trading_system.create_paper_session(
            user_id="enhanced_week",
            session_type=SessionType.FULL_WEEK,
            starting_capital=10000.0
        )
        
        if session_week:
            logger.info(f"[CHECK] Week session created: {session_week}")
            success = await paper_trading_system.start_session(session_week)
            if success:
                logger.info("🚀 Week session started successfully!")
                active_sessions.append(("Week", session_week))
            else:
                logger.error("[ERROR] Failed to start week session")
        else:
            logger.error("[ERROR] Failed to create week session")
    except Exception as e:
        logger.error(f"[ERROR] Error with week session: {e}")
    
    if active_sessions:
        logger.info("=" * 60)
        logger.info("[CHECK] ENHANCED SESSIONS LAUNCHED SUCCESSFULLY")
        logger.info("=" * 60)
        for session_type, session_id in active_sessions:
            logger.info(f"🎯 {session_type} Session: {session_id}")
        logger.info("=" * 60)
        logger.info("🛡️ ALL SESSIONS HAVE FULL RISK MANAGEMENT ACTIVE:")
        logger.info("   • Position size limits (5% max per position)")
        logger.info("   • Daily loss limits ($1,000 max)")
        logger.info("   • Stop-loss mechanisms (8% max)")
        logger.info("   • Portfolio risk limits (2% max)")
        logger.info("   • Real-time risk monitoring")
        logger.info("   • AI-powered risk assessment")
        logger.info("   • Enhanced paper trading with real market data")
        logger.info("=" * 60)
        
        # Monitor sessions for a few cycles
        logger.info("📊 Starting session monitoring (5 cycles)...")
        for cycle in range(5):
            logger.info(f"🔄 Monitoring cycle {cycle + 1}/5...")
            
            for session_type, session_id in active_sessions:
                try:
                    session_info = await paper_trading_system.get_session_info(session_id)
                    if session_info:
                        logger.info(f"📊 {session_type} Session {session_id[:8]}...")
                        logger.info(f"   Status: {session_info.get('status', 'Unknown')}")
                        logger.info(f"   Capital: ${session_info.get('current_value', 0):,.2f}")
                        logger.info(f"   P&L: ${session_info.get('profit_loss', 0):,.2f}")
                        logger.info(f"   Trades: {session_info.get('trades_count', 0)}")
                except Exception as e:
                    logger.error(f"Error monitoring {session_type} session: {e}")
            
            if cycle < 4:  # Don't wait after last cycle
                await asyncio.sleep(60)  # Wait 1 minute between cycles
        
        logger.info("=" * 60)
        logger.info("[CHECK] ENHANCED SESSIONS MONITORING COMPLETE")
        logger.info("🎯 Sessions are running with full risk management")
        logger.info("🛡️ Risk controls are active and protecting capital")
        logger.info("=" * 60)
        
    else:
        logger.error("[ERROR] No enhanced sessions created successfully!")

if __name__ == "__main__":
    asyncio.run(grant_permissions_and_launch())
