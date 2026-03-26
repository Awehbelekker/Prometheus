"""
🛡️ FEATURE GATING MIDDLEWARE
Production-ready feature access control and permission enforcement
"""

import logging
from functools import wraps
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from core.user_tier_system import (
    UserTier, FeatureFlag, user_tier_manager, 
    has_feature, can_trade_live, get_trading_limits
)

logger = logging.getLogger(__name__)
security = HTTPBearer()

class FeatureGatingError(Exception):
    """Feature gating specific errors"""
    pass

class PermissionDeniedError(FeatureGatingError):
    """Permission denied error"""
    pass

class TierUpgradeRequiredError(FeatureGatingError):
    """Tier upgrade required error"""
    pass

def require_feature(feature: FeatureFlag, upgrade_message: Optional[str] = None):
    """Decorator to require a specific feature for endpoint access"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request context
            request = None
            current_user = None
            
            # Find request and current_user in kwargs
            for key, value in kwargs.items():
                if key == 'request' and hasattr(value, 'state'):
                    request = value
                elif key == 'current_user' and isinstance(value, dict):
                    current_user = value
            
            if not current_user:
                raise HTTPException(
                    status_code=401, 
                    detail="Authentication required"
                )
            
            user_id = current_user.get('user_id')
            if not user_id:
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid user context"
                )
            
            # Check feature access
            if not has_feature(user_id, feature):
                permissions = user_tier_manager.get_user_permissions(user_id)
                current_tier = permissions.tier.value if permissions else "unknown"
                
                # Find which tier has this feature
                required_tiers = []
                for tier, config in user_tier_manager.tier_configs.items():
                    if feature in config.features:
                        required_tiers.append(tier.value)
                
                error_message = upgrade_message or f"Feature '{feature.value}' requires {' or '.join(required_tiers)} tier. Current tier: {current_tier}"
                
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "feature_access_denied",
                        "message": error_message,
                        "required_feature": feature.value,
                        "current_tier": current_tier,
                        "required_tiers": required_tiers,
                        "upgrade_available": current_tier == "demo"
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_tier(min_tier: UserTier):
    """Decorator to require minimum user tier"""
    tier_hierarchy = {
        UserTier.DEMO: 1,
        UserTier.PREMIUM: 2,
        UserTier.ADMIN: 3
    }
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = current_user.get('user_id')
            permissions = user_tier_manager.get_user_permissions(user_id)
            
            if not permissions or not permissions.is_active:
                raise HTTPException(status_code=403, detail="User permissions not found or inactive")
            
            user_tier_level = tier_hierarchy.get(permissions.tier, 0)
            required_tier_level = tier_hierarchy.get(min_tier, 999)
            
            if user_tier_level < required_tier_level:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "tier_upgrade_required",
                        "message": f"This feature requires {min_tier.value} tier or higher",
                        "current_tier": permissions.tier.value,
                        "required_tier": min_tier.value
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_live_trading():
    """Decorator to require live trading permissions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_id = current_user.get('user_id')
            if not can_trade_live(user_id):
                permissions = user_tier_manager.get_user_permissions(user_id)
                current_tier = permissions.tier.value if permissions else "unknown"
                
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "live_trading_not_permitted",
                        "message": "Live trading requires Premium or Admin tier",
                        "current_tier": current_tier,
                        "required_tiers": ["premium", "admin"],
                        "demo_available": True
                    }
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_trading_limits(order_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """Validate trading order against user limits"""
    limits = get_trading_limits(user_id)
    if not limits:
        raise PermissionDeniedError("No trading limits found for user")
    
    # Check position size limit
    order_value = float(order_data.get('quantity', 0)) * float(order_data.get('price', 0))
    max_position_size = limits.get('max_position_size', 0)
    
    if order_value > max_position_size:
        raise TierUpgradeRequiredError(
            f"Order value ${order_value:,.2f} exceeds limit of ${max_position_size:,.2f}"
        )
    
    # Add risk multiplier based on tier
    permissions = user_tier_manager.get_user_permissions(user_id)
    if permissions:
        if permissions.tier == UserTier.DEMO:
            order_data['risk_multiplier'] = 0.5  # Conservative for demo
        elif permissions.tier == UserTier.PREMIUM:
            order_data['risk_multiplier'] = 1.0  # Standard risk
        elif permissions.tier == UserTier.ADMIN:
            order_data['risk_multiplier'] = 1.5  # Higher risk allowed
    
    return order_data

class FeatureGate:
    """Feature gating utility class"""
    
    @staticmethod
    def check_feature_access(user_id: str, feature: FeatureFlag) -> Dict[str, Any]:
        """Check feature access and return detailed information"""
        has_access = has_feature(user_id, feature)
        permissions = user_tier_manager.get_user_permissions(user_id)
        
        result = {
            "has_access": has_access,
            "feature": feature.value,
            "user_id": user_id
        }
        
        if permissions:
            result.update({
                "current_tier": permissions.tier.value,
                "is_active": permissions.is_active,
                "demo_expires_at": permissions.demo_expires_at.isoformat() if permissions.demo_expires_at else None
            })
        
        if not has_access:
            # Find which tiers have this feature
            available_tiers = []
            for tier, config in user_tier_manager.tier_configs.items():
                if feature in config.features:
                    available_tiers.append(tier.value)
            
            result["available_in_tiers"] = available_tiers
            result["upgrade_required"] = True
        
        return result
    
    @staticmethod
    def get_user_feature_matrix(user_id: str) -> Dict[str, Any]:
        """Get complete feature access matrix for user"""
        permissions = user_tier_manager.get_user_permissions(user_id)
        if not permissions:
            return {"error": "User permissions not found"}
        
        feature_access = {}
        for feature in FeatureFlag:
            feature_access[feature.value] = has_feature(user_id, feature)
        
        return {
            "user_id": user_id,
            "tier": permissions.tier.value,
            "is_active": permissions.is_active,
            "demo_expires_at": permissions.demo_expires_at.isoformat() if permissions.demo_expires_at else None,
            "features": feature_access,
            "trading_limits": get_trading_limits(user_id),
            "can_trade_live": can_trade_live(user_id)
        }

# Middleware for automatic feature gating
async def feature_gating_middleware(request: Request, call_next):
    """Middleware to automatically apply feature gating"""
    try:
        response = await call_next(request)
        return response
    except FeatureGatingError as e:
        logger.warning(f"Feature gating error: {e}")
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in feature gating middleware: {e}")
        raise

# Utility functions for common checks
def ensure_demo_user(user_id: str) -> bool:
    """Ensure user has at least demo access"""
    permissions = user_tier_manager.get_user_permissions(user_id)
    if not permissions:
        # Create demo user automatically
        user_tier_manager.create_user_permissions(user_id, UserTier.DEMO)
        logger.info(f"Auto-created demo user: {user_id}")
        return True
    return permissions.is_active

def get_feature_recommendations(user_id: str) -> List[Dict[str, Any]]:
    """Get feature upgrade recommendations for user"""
    permissions = user_tier_manager.get_user_permissions(user_id)
    if not permissions:
        return []
    
    current_tier = permissions.tier
    recommendations = []
    
    # Recommend Premium features if user is Demo
    if current_tier == UserTier.DEMO:
        premium_features = user_tier_manager.tier_configs[UserTier.PREMIUM].features - permissions.features
        if premium_features:
            recommendations.append({
                "upgrade_to": "premium",
                "new_features": [f.value for f in premium_features],
                "benefits": [
                    "Live trading with real money",
                    "Advanced order types",
                    "Options and crypto trading",
                    "Neural interface access"
                ]
            })
    
    # Recommend Admin features if user is Premium
    if current_tier == UserTier.PREMIUM:
        admin_features = user_tier_manager.tier_configs[UserTier.ADMIN].features - permissions.features
        if admin_features:
            recommendations.append({
                "upgrade_to": "admin",
                "new_features": [f.value for f in admin_features],
                "benefits": [
                    "System administration access",
                    "User management capabilities",
                    "Advanced trading controls",
                    "Unlimited trading limits"
                ]
            })
    
    return recommendations
