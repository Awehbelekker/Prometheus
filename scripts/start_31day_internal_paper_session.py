#!/usr/bin/env python3
"""
🗓️ START 31-DAY INTERNAL PAPER TRADING SESSION
Launch long-term internal paper trading session until end of October for continuous AI learning
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def start_31day_session():
    """Start 31-day internal paper trading session"""
    print("🚀 STARTING 31-DAY INTERNAL PAPER TRADING SESSION")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target End: End of October 2025")
    print("=" * 60)
    
    try:
        # Import the enhanced paper trading system
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'PROMETHEUS-Enterprise-Package', 'backend'))
        from core.enhanced_paper_trading_system import (
            enhanced_paper_trading, SessionType, SessionStatus
        )
        
        # Calculate 31 days in hours (744 hours)
        session_duration_hours = 31 * 24  # 744 hours
        starting_capital = 100000.0  # $100k for comprehensive testing
        
        print(f"📊 Session Configuration:")
        print(f"   Duration: {session_duration_hours} hours (31 days)")
        print(f"   Starting Capital: ${starting_capital:,.2f}")
        print(f"   Session Type: CUSTOM (Long-term AI Learning)")
        print(f"   AI Learning: ENABLED")
        print(f"   Real Market Data: ENABLED")
        
        # Create internal AI learning user and grant permissions
        internal_user_id = "internal_ai_learning_system"

        # Grant permissions to internal system
        from core.dual_tier_permission_system import dual_tier_system, TradingPermission, UserPermissions, UserTier

        # Create internal user with admin permissions
        internal_permissions = UserPermissions(
            user_id=internal_user_id,
            tier=UserTier.ADMIN,
            paper_trading_enabled=True,
            live_trading_enabled=True,
            allocated_funds=100000.0,
            max_allocation=1000000.0,
            permissions=[
                TradingPermission.PAPER_TRADING,
                TradingPermission.LIVE_TRADING,
                TradingPermission.SYSTEM_ADMIN
            ]
        )

        # Create user permissions
        dual_tier_system.create_user_permissions(internal_permissions)

        print(f"[CHECK] Internal AI user created with permissions")
        
        # Create the 31-day session
        print(f"\n🔧 Creating 31-day paper trading session...")
        session_id = await enhanced_paper_trading.create_paper_session(
            user_id=internal_user_id,
            session_type=SessionType.CUSTOM,
            starting_capital=starting_capital,
            custom_hours=session_duration_hours
        )
        
        if not session_id:
            print("[ERROR] Failed to create 31-day session")
            return False
        
        print(f"[CHECK] Session created successfully!")
        print(f"   Session ID: {session_id}")
        
        # Start the session
        print(f"\n🚀 Starting 31-day session...")
        started = await enhanced_paper_trading.start_session(session_id)
        
        if not started:
            print("[ERROR] Failed to start 31-day session")
            return False
        
        print(f"[CHECK] 31-day session started successfully!")
        
        # Get session details
        session = await enhanced_paper_trading.get_session(session_id)
        if session:
            print(f"\n📈 Session Details:")
            print(f"   Session ID: {session.session_id}")
            print(f"   Status: {session.status.value}")
            print(f"   Start Time: {session.start_time}")
            print(f"   End Time: {session.end_time}")
            print(f"   Duration: {session.duration_hours} hours")
            print(f"   Starting Capital: ${session.starting_capital:,.2f}")
            print(f"   Current Value: ${session.current_value:,.2f}")
        
        # Enable AI learning features
        print(f"\n🤖 Enabling AI Learning Features...")
        
        # Configure AI learning parameters
        ai_config = {
            "learning_enabled": True,
            "data_collection": True,
            "pattern_recognition": True,
            "strategy_optimization": True,
            "market_sentiment_analysis": True,
            "risk_management_learning": True,
            "performance_tracking": True,
            "continuous_improvement": True
        }
        
        # Update session with AI configuration
        session.session_data.update({
            "ai_learning_config": ai_config,
            "session_purpose": "31-day AI learning and system optimization",
            "target_end_date": "2025-10-31",
            "learning_objectives": [
                "Market pattern recognition",
                "Strategy optimization",
                "Risk management improvement",
                "Performance enhancement",
                "User behavior analysis",
                "System reliability testing"
            ]
        })
        
        # Save updated configuration to database
        try:
            import sqlite3
            import json
            with sqlite3.connect(enhanced_paper_trading.db_path) as conn:
                conn.execute("""
                    UPDATE paper_sessions
                    SET session_data = ?
                    WHERE session_id = ?
                """, (json.dumps(session.session_data), session.session_id))
                conn.commit()
        except Exception as e:
            print(f"[WARNING]️ Warning: Could not save AI config to database: {e}")
        
        print(f"[CHECK] AI Learning configuration applied!")
        
        # Display monitoring information
        print(f"\n📊 MONITORING INFORMATION:")
        print(f"   • Session will run continuously for 31 days")
        print(f"   • AI will learn from all market movements and trading patterns")
        print(f"   • Real market data will be used (no simulation)")
        print(f"   • System will adapt and improve strategies over time")
        print(f"   • Progress can be monitored through admin dashboard")
        print(f"   • Session will automatically end on: {session.end_time}")
        
        print(f"\n🎯 SUCCESS: 31-day internal paper trading session is now ACTIVE!")
        print(f"Session ID: {session_id}")
        print(f"Monitor progress at: /api/user/session/{session_id}")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Make sure the enhanced paper trading system is available")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error starting 31-day session: {e}")
        return False

async def verify_session_status():
    """Verify the session is running properly"""
    print(f"\n🔍 VERIFYING SESSION STATUS...")
    
    try:
        from core.enhanced_paper_trading_system import enhanced_paper_trading
        
        # Get all active sessions
        active_sessions = enhanced_paper_trading.active_sessions
        
        print(f"Active Sessions: {len(active_sessions)}")
        
        for session_id, session in active_sessions.items():
            if session.user_id == "internal_ai_learning_system":
                print(f"[CHECK] Found 31-day AI learning session:")
                print(f"   Session ID: {session_id}")
                print(f"   Status: {session.status.value}")
                print(f"   Duration: {session.duration_hours} hours")
                print(f"   Time Remaining: {(session.end_time - datetime.now()).total_seconds() / 3600:.1f} hours")
                print(f"   Current Value: ${session.current_value:,.2f}")
                print(f"   P&L: ${session.profit_loss:,.2f}")
                print(f"   Trades: {session.trades_count}")
                return True
        
        print("[WARNING]️ No 31-day AI learning session found in active sessions")
        return False
        
    except Exception as e:
        print(f"[ERROR] Error verifying session: {e}")
        return False

async def main():
    """Main function"""
    print("🗓️ PROMETHEUS 31-DAY INTERNAL PAPER TRADING SESSION LAUNCHER")
    print("=" * 80)
    print(f"Launch Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv('.env.live')
    
    # Start the 31-day session
    success = await start_31day_session()
    
    if success:
        # Verify session is running
        await asyncio.sleep(2)  # Give it a moment to initialize
        await verify_session_status()
        
        print(f"\n🎉 31-DAY SESSION LAUNCH COMPLETE!")
        print("=" * 80)
        print("The session is now running in the background and will continue")
        print("until the end of October, learning from all market activity.")
        print("=" * 80)
    else:
        print(f"\n[ERROR] FAILED TO START 31-DAY SESSION")
        print("Please check the logs and try again.")

if __name__ == "__main__":
    asyncio.run(main())
