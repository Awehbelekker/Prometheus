"""
🎯 USER TIER SYSTEM - DEMO/PREMIUM/ADMIN ACCESS CONTROL
Production-ready tiered access control with feature gating
"""

import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User access tiers"""
    DEMO = "demo"
    PREMIUM = "premium" 
    ADMIN = "admin"

class FeatureFlag(Enum):
    """Available feature flags"""
    # Trading Features
    LIVE_TRADING = "live_trading"
    PAPER_TRADING = "paper_trading"
    ADVANCED_ORDERS = "advanced_orders"
    OPTIONS_TRADING = "options_trading"
    CRYPTO_TRADING = "crypto_trading"
    
    # AI Features
    AI_TRADING_AGENTS = "ai_trading_agents"
    QUANTUM_OPTIMIZATION = "quantum_optimization"
    NEURAL_INTERFACE = "neural_interface"
    HOLOGRAPHIC_UI = "holographic_ui"
    
    # Analytics Features
    ADVANCED_ANALYTICS = "advanced_analytics"
    REAL_TIME_DATA = "real_time_data"
    MARKET_ORACLE = "market_oracle"
    RISK_MANAGEMENT = "risk_management"
    
    # Social Features
    SOCIAL_TRADING = "social_trading"
    COMMUNITY_FEATURES = "community_features"
    LEADERBOARDS = "leaderboards"
    
    # Admin Features
    USER_MANAGEMENT = "user_management"
    SYSTEM_MONITORING = "system_monitoring"
    TRADING_CONTROLS = "trading_controls"

@dataclass
class TierConfiguration:
    """Configuration for each user tier"""
    tier: UserTier
    display_name: str
    description: str
    features: Set[FeatureFlag]
    trading_limits: Dict[str, Any]
    demo_duration_hours: Optional[int] = None
    max_positions: int = 10
    max_daily_trades: int = 100
    max_position_size: float = 10000.0
    api_rate_limit: int = 1000  # requests per hour

# Tier Configurations
TIER_CONFIGS = {
    UserTier.DEMO: TierConfiguration(
        tier=UserTier.DEMO,
        display_name="Demo Trader",
        description="48-hour live trading demo with full feature access",
        features={
            FeatureFlag.PAPER_TRADING,
            FeatureFlag.AI_TRADING_AGENTS,
            FeatureFlag.QUANTUM_OPTIMIZATION,
            FeatureFlag.ADVANCED_ANALYTICS,
            FeatureFlag.REAL_TIME_DATA,
            FeatureFlag.MARKET_ORACLE,
            FeatureFlag.RISK_MANAGEMENT,
            FeatureFlag.SOCIAL_TRADING,
            FeatureFlag.COMMUNITY_FEATURES
        },
        trading_limits={
            "virtual_capital": 100000.0,
            "max_trade_size": 5000.0,
            "demo_mode_only": True
        },
        demo_duration_hours=48,
        max_positions=5,
        max_daily_trades=50,
        max_position_size=5000.0,
        api_rate_limit=500
    ),
    
    UserTier.PREMIUM: TierConfiguration(
        tier=UserTier.PREMIUM,
        display_name="Premium Trader",
        description="Full trading access with advanced AI features",
        features={
            FeatureFlag.LIVE_TRADING,
            FeatureFlag.PAPER_TRADING,
            FeatureFlag.ADVANCED_ORDERS,
            FeatureFlag.OPTIONS_TRADING,
            FeatureFlag.CRYPTO_TRADING,
            FeatureFlag.AI_TRADING_AGENTS,
            FeatureFlag.QUANTUM_OPTIMIZATION,
            FeatureFlag.NEURAL_INTERFACE,
            FeatureFlag.HOLOGRAPHIC_UI,
            FeatureFlag.ADVANCED_ANALYTICS,
            FeatureFlag.REAL_TIME_DATA,
            FeatureFlag.MARKET_ORACLE,
            FeatureFlag.RISK_MANAGEMENT,
            FeatureFlag.SOCIAL_TRADING,
            FeatureFlag.COMMUNITY_FEATURES,
            FeatureFlag.LEADERBOARDS
        },
        trading_limits={
            "max_account_value": 1000000.0,
            "max_trade_size": 50000.0,
            "live_trading_enabled": True
        },
        max_positions=20,
        max_daily_trades=200,
        max_position_size=50000.0,
        api_rate_limit=2000
    ),
    
    UserTier.ADMIN: TierConfiguration(
        tier=UserTier.ADMIN,
        display_name="System Administrator",
        description="Full system access with administrative controls",
        features=set(FeatureFlag),  # All features
        trading_limits={
            "unlimited_access": True,
            "live_trading_enabled": True,
            "admin_controls": True
        },
        max_positions=100,
        max_daily_trades=1000,
        max_position_size=1000000.0,
        api_rate_limit=10000
    )
}

@dataclass
class UserPermissions:
    """User permissions and access control"""
    user_id: str
    tier: UserTier
    features: Set[FeatureFlag]
    trading_limits: Dict[str, Any]
    demo_expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    is_active: bool = True

class UserTierManager:
    """Manages user tiers and permissions"""
    
    def __init__(self):
        self.user_permissions: Dict[str, UserPermissions] = {}
        self.tier_configs = TIER_CONFIGS
        
    def create_user_permissions(self, user_id: str, tier: UserTier) -> UserPermissions:
        """Create permissions for a new user"""
        config = self.tier_configs[tier]
        
        # Set demo expiration for demo users
        demo_expires_at = None
        if tier == UserTier.DEMO and config.demo_duration_hours:
            demo_expires_at = datetime.now() + timedelta(hours=config.demo_duration_hours)
        
        permissions = UserPermissions(
            user_id=user_id,
            tier=tier,
            features=config.features.copy(),
            trading_limits=config.trading_limits.copy(),
            demo_expires_at=demo_expires_at
        )
        
        self.user_permissions[user_id] = permissions
        logger.info(f"Created {tier.value} permissions for user {user_id}")
        
        return permissions
    
    def get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions"""
        permissions = self.user_permissions.get(user_id)
        
        # Check if demo has expired
        if permissions and permissions.tier == UserTier.DEMO:
            if permissions.demo_expires_at and datetime.now() > permissions.demo_expires_at:
                logger.info(f"Demo expired for user {user_id}")
                permissions.is_active = False
                
        return permissions
    
    def has_feature(self, user_id: str, feature: FeatureFlag) -> bool:
        """Check if user has access to a feature"""
        permissions = self.get_user_permissions(user_id)
        if not permissions or not permissions.is_active:
            return False
        
        return feature in permissions.features
    
    def can_trade_live(self, user_id: str) -> bool:
        """Check if user can trade with real money"""
        permissions = self.get_user_permissions(user_id)
        if not permissions or not permissions.is_active:
            return False
        
        # Only Premium and Admin can trade live
        return permissions.tier in [UserTier.PREMIUM, UserTier.ADMIN]
    
    def get_trading_limits(self, user_id: str) -> Dict[str, Any]:
        """Get user's trading limits"""
        permissions = self.get_user_permissions(user_id)
        if not permissions:
            return {}
        
        config = self.tier_configs[permissions.tier]
        return {
            **permissions.trading_limits,
            "max_positions": config.max_positions,
            "max_daily_trades": config.max_daily_trades,
            "max_position_size": config.max_position_size,
            "api_rate_limit": config.api_rate_limit
        }
    
    def upgrade_user_tier(self, user_id: str, new_tier: UserTier) -> bool:
        """Upgrade user to a higher tier"""
        permissions = self.get_user_permissions(user_id)
        if not permissions:
            return False
        
        # Create new permissions with upgraded tier
        new_permissions = self.create_user_permissions(user_id, new_tier)
        logger.info(f"Upgraded user {user_id} from {permissions.tier.value} to {new_tier.value}")
        
        return True
    
    def get_tier_info(self, tier: UserTier) -> Dict[str, Any]:
        """Get information about a tier"""
        config = self.tier_configs[tier]
        return {
            "tier": tier.value,
            "display_name": config.display_name,
            "description": config.description,
            "features": [f.value for f in config.features],
            "trading_limits": config.trading_limits,
            "demo_duration_hours": config.demo_duration_hours,
            "max_positions": config.max_positions,
            "max_daily_trades": config.max_daily_trades,
            "max_position_size": config.max_position_size
        }
    
    def get_all_tiers_info(self) -> List[Dict[str, Any]]:
        """Get information about all tiers"""
        return [self.get_tier_info(tier) for tier in UserTier]

# Global instance
user_tier_manager = UserTierManager()

# Convenience functions
def has_feature(user_id: str, feature: FeatureFlag) -> bool:
    """Check if user has access to a feature"""
    return user_tier_manager.has_feature(user_id, feature)

def can_trade_live(user_id: str) -> bool:
    """Check if user can trade with real money"""
    return user_tier_manager.can_trade_live(user_id)

def get_trading_limits(user_id: str) -> Dict[str, Any]:
    """Get user's trading limits"""
    return user_tier_manager.get_trading_limits(user_id)

def create_demo_user(user_id: str) -> UserPermissions:
    """Create a demo user with 48-hour access"""
    return user_tier_manager.create_user_permissions(user_id, UserTier.DEMO)

def create_premium_user(user_id: str) -> UserPermissions:
    """Create a premium user with full access"""
    return user_tier_manager.create_user_permissions(user_id, UserTier.PREMIUM)

def create_admin_user(user_id: str) -> UserPermissions:
    """Create an admin user with system access"""
    return user_tier_manager.create_user_permissions(user_id, UserTier.ADMIN)
