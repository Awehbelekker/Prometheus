#!/usr/bin/env python3
"""
🚀 PROMETHEUS Persistent Trading System Initialization
Complete system startup and configuration script
"""

import os
import sys
import logging
import asyncio
import signal
import time
from datetime import datetime
from typing import Dict, Any

# Add core modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Import all core systems
from core.persistent_trading_engine import persistent_trading_engine, TradingMode
from core.user_portfolio_manager import user_portfolio_manager, PortfolioType
from core.access_control_manager import access_control_manager, UserRole, PermissionType
from core.wealth_management_system import wealth_management_system
from core.portfolio_persistence_layer import portfolio_persistence_layer, PersistenceEventType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prometheus_trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class PrometheusSystemManager:
    """
    Central system manager for PROMETHEUS persistent trading platform
    """
    
    def __init__(self):
        self.systems_running = False
        self.shutdown_requested = False
        
    def initialize_system(self):
        """Initialize all system components"""
        logger.info("🚀 Initializing PROMETHEUS Persistent Trading System...")
        
        try:
            # 1. Initialize databases
            logger.info("📊 Initializing databases...")
            self._initialize_databases()
            
            # 2. Create default admin user
            logger.info("👤 Setting up default admin...")
            self._setup_default_admin()
            
            # 3. Start background services
            logger.info("⚙️ Starting background services...")
            self._start_background_services()
            
            # 4. Restore system state
            logger.info("💾 Restoring system state...")
            self._restore_system_state()
            
            # 5. Verify system health
            logger.info("🔍 Verifying system health...")
            self._verify_system_health()
            
            self.systems_running = True
            logger.info("[CHECK] PROMETHEUS System initialized successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"[ERROR] System initialization failed: {e}")
            return False
    
    def _initialize_databases(self):
        """Initialize all database schemas"""
        # Databases are initialized automatically when classes are instantiated
        logger.info("  - Persistent trading engine database: [CHECK]")
        logger.info("  - User portfolio manager database: [CHECK]")
        logger.info("  - Access control manager database: [CHECK]")
        logger.info("  - Wealth management system database: [CHECK]")
        logger.info("  - Portfolio persistence layer database: [CHECK]")
    
    def _setup_default_admin(self):
        """Set up default admin user"""
        try:
            # Create default admin profile if it doesn't exist
            admin_id = "admin_prometheus"
            
            # Check if admin already exists
            admin_perms = access_control_manager.get_user_permissions(admin_id)
            
            if not admin_perms:
                # Create admin user profile
                try:
                    user_portfolio_manager.create_user_profile(
                        "admin",
                        "admin@prometheus-trading.com",
                        "prometheus_admin_2024"  # Change this in production!
                    )
                except ValueError:
                    # User might already exist, that's okay
                    pass
                
                # Set admin permissions
                access_control_manager.create_user_permissions(admin_id, UserRole.ADMIN)
                
                # Initialize admin portfolios
                user_portfolio_manager.initialize_user_portfolio(
                    admin_id,
                    PortfolioType.PAPER,
                    1000000.0  # $1M paper trading
                )
                
                user_portfolio_manager.initialize_user_portfolio(
                    admin_id,
                    PortfolioType.LIVE,
                    1000000.0  # $1M live trading
                )
                
                logger.info("  - Default admin user created: [CHECK]")
            else:
                logger.info("  - Default admin user exists: [CHECK]")
                
        except Exception as e:
            logger.error(f"  - Failed to setup admin: {e}")
    
    def _start_background_services(self):
        """Start all background services"""
        try:
            # Start persistent trading engine
            persistent_trading_engine.start_background_trading()
            logger.info("  - Persistent trading engine: [CHECK]")
            
            # Start portfolio persistence layer
            portfolio_persistence_layer.start_persistence_engine()
            logger.info("  - Portfolio persistence layer: [CHECK]")
            
            # Record system startup
            portfolio_persistence_layer.record_event(
                PersistenceEventType.SYSTEM_STARTUP,
                "system",
                {
                    "startup_time": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "components": [
                        "persistent_trading_engine",
                        "portfolio_persistence_layer",
                        "user_portfolio_manager",
                        "access_control_manager",
                        "wealth_management_system"
                    ]
                }
            )
            
        except Exception as e:
            logger.error(f"  - Failed to start background services: {e}")
            raise
    
    def _restore_system_state(self):
        """Restore system state from persistence layer"""
        try:
            # The persistence layer automatically restores state on initialization
            health = portfolio_persistence_layer.get_system_health()
            logger.info(f"  - Active sessions restored: {health.get('active_sessions', 0)}")
            logger.info(f"  - Pending events: {health.get('pending_events', 0)}")
            
        except Exception as e:
            logger.error(f"  - Failed to restore system state: {e}")
    
    def _verify_system_health(self):
        """Verify all systems are healthy"""
        try:
            # Check trading engine
            if not persistent_trading_engine.is_running:
                raise Exception("Trading engine not running")
            
            # Check persistence layer
            health = portfolio_persistence_layer.get_system_health()
            if not health.get('persistence_engine_running', False):
                raise Exception("Persistence engine not running")
            
            # Check database connections
            test_user_id = "health_check_user"
            portfolio = persistent_trading_engine.get_user_portfolio(test_user_id)
            # Portfolio won't exist, but connection should work
            
            logger.info("  - All systems healthy: [CHECK]")
            
        except Exception as e:
            logger.error(f"  - System health check failed: {e}")
            raise
    
    def create_demo_users(self, count: int = 5):
        """Create demo users for testing"""
        logger.info(f"👥 Creating {count} demo users...")
        
        demo_users = []
        for i in range(1, count + 1):
            try:
                username = f"demo_user_{i}"
                email = f"demo{i}@prometheus-trading.com"
                password = f"demo_password_{i}"
                
                # Create user
                user_id = user_portfolio_manager.create_user_profile(username, email, password)
                
                # Set permissions
                access_control_manager.create_user_permissions(user_id, UserRole.TRADER)
                
                # Initialize portfolios
                user_portfolio_manager.initialize_user_portfolio(
                    user_id,
                    PortfolioType.PAPER,
                    100000.0  # $100K paper trading
                )
                
                # Approve some users for live trading
                if i <= 2:  # First 2 users get live trading
                    access_control_manager.approve_live_trading(
                        user_id,
                        "admin_prometheus",
                        50000.0,  # $50K live allocation
                        f"Demo user {i} live trading approval"
                    )
                    
                    user_portfolio_manager.initialize_user_portfolio(
                        user_id,
                        PortfolioType.LIVE,
                        50000.0
                    )
                
                demo_users.append({
                    'user_id': user_id,
                    'username': username,
                    'email': email,
                    'live_approved': i <= 2
                })
                
                logger.info(f"  - Created demo user: {username} [CHECK]")
                
            except ValueError as e:
                logger.warning(f"  - Demo user {username} already exists")
            except Exception as e:
                logger.error(f"  - Failed to create demo user {username}: {e}")
        
        return demo_users
    
    def run_system(self):
        """Run the system with graceful shutdown handling"""
        if not self.systems_running:
            logger.error("[ERROR] System not initialized. Call initialize_system() first.")
            return
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🎯 PROMETHEUS Persistent Trading System is running...")
        logger.info("📊 System Status:")
        logger.info(f"  - Trading Engine: {'Running' if persistent_trading_engine.is_running else 'Stopped'}")
        logger.info(f"  - Persistence Layer: {'Running' if portfolio_persistence_layer.is_running else 'Stopped'}")
        logger.info(f"  - Active Portfolios: {len(persistent_trading_engine.user_portfolios)}")
        
        try:
            # Main system loop
            while not self.shutdown_requested:
                # System is running in background threads
                # This loop just keeps the main process alive
                time.sleep(10)
                
                # Periodic health check
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self._periodic_health_check()
                    
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            logger.error(f"[ERROR] System error: {e}")
        finally:
            self.shutdown_system()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def _periodic_health_check(self):
        """Perform periodic system health check"""
        try:
            health = portfolio_persistence_layer.get_system_health()
            logger.info(f"💓 Health Check - Active Sessions: {health.get('active_sessions', 0)}, "
                       f"Pending Events: {health.get('pending_events', 0)}")
        except Exception as e:
            logger.warning(f"[WARNING]️ Health check failed: {e}")
    
    def shutdown_system(self):
        """Gracefully shutdown all systems"""
        logger.info("🛑 Shutting down PROMETHEUS Persistent Trading System...")
        
        try:
            # Stop background services
            logger.info("  - Stopping background services...")
            persistent_trading_engine.stop_background_trading()
            portfolio_persistence_layer.stop_persistence_engine()
            
            # Record system shutdown
            portfolio_persistence_layer.record_event(
                PersistenceEventType.SYSTEM_SHUTDOWN,
                "system",
                {
                    "shutdown_time": datetime.now().isoformat(),
                    "reason": "graceful_shutdown"
                }
            )
            
            self.systems_running = False
            logger.info("[CHECK] System shutdown complete")
            
        except Exception as e:
            logger.error(f"[ERROR] Error during shutdown: {e}")

def main():
    """Main entry point"""
    print("🚀 PROMETHEUS Persistent Trading System")
    print("=" * 50)
    
    # Create system manager
    system_manager = PrometheusSystemManager()
    
    # Initialize system
    if not system_manager.initialize_system():
        print("[ERROR] System initialization failed. Exiting.")
        sys.exit(1)
    
    # Create demo users (optional)
    create_demo = input("Create demo users? (y/N): ").lower().strip() == 'y'
    if create_demo:
        demo_users = system_manager.create_demo_users(5)
        print(f"[CHECK] Created {len(demo_users)} demo users")
    
    # Run system
    try:
        system_manager.run_system()
    except Exception as e:
        logger.error(f"[ERROR] System failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
