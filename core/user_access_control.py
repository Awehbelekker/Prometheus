#!/usr/bin/env python3
"""
🔐 USER ACCESS CONTROL SYSTEM
Prometheus Trading App - NeuroForge™ Revolutionary Trading Platform
Comprehensive user permission and feature gating system
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

class UserTier(str, Enum):
    """User access tiers"""
    DEMO = "demo"
    PREMIUM = "premium"
    ADMIN = "admin"

class FeatureCategory(str, Enum):
    """Feature categories for organization"""
    BASIC_TRADING = "basic_trading"
    AI_FEATURES = "ai_features"
    REVOLUTIONARY = "revolutionary"
    ADMIN = "admin"

@dataclass
class Feature:
    """Feature definition with access control"""
    name: str
    category: FeatureCategory
    description: str
    required_tier: UserTier
    is_revolutionary: bool = False
    beta_feature: bool = False
    
class UserAccessManager:
    """Comprehensive user access control manager"""
    
    def __init__(self, db_path: str = "prometheus_trading.db"):
        self.db_path = db_path
        self.features = self._initialize_features()
        self.invitation_codes = self._initialize_invitation_codes()
        self._setup_database()
    
    def _initialize_features(self) -> Dict[str, Feature]:
        """Initialize all system features with access controls"""
        features = {
            # Basic Trading Features (Demo Tier)
            "portfolio_tracking": Feature(
                "portfolio_tracking", FeatureCategory.BASIC_TRADING,
                "Real-time portfolio tracking and basic analytics",
                UserTier.DEMO
            ),
            "basic_trading": Feature(
                "basic_trading", FeatureCategory.BASIC_TRADING,
                "Basic buy/sell trading operations",
                UserTier.DEMO
            ),
            "48_hour_demo": Feature(
                "48_hour_demo", FeatureCategory.BASIC_TRADING,
                "48-hour live trading demonstration with AI learning",
                UserTier.DEMO
            ),
            "market_data_basic": Feature(
                "market_data_basic", FeatureCategory.BASIC_TRADING,
                "Basic market data and price feeds",
                UserTier.DEMO
            ),
            
            # AI Features (Premium Tier)
            "ai_insights_advanced": Feature(
                "ai_insights_advanced", FeatureCategory.AI_FEATURES,
                "Advanced AI-powered trading insights and recommendations",
                UserTier.PREMIUM
            ),
            "ai_learning_system": Feature(
                "ai_learning_system", FeatureCategory.AI_FEATURES,
                "Personalized AI learning from trading patterns",
                UserTier.PREMIUM
            ),
            "quantum_trading": Feature(
                "quantum_trading", FeatureCategory.REVOLUTIONARY,
                "Quantum-powered trading algorithms (1000x faster)",
                UserTier.PREMIUM, is_revolutionary=True
            ),
            "blockchain_trading": Feature(
                "blockchain_trading", FeatureCategory.REVOLUTIONARY,
                "Blockchain-based transparent trading",
                UserTier.PREMIUM, is_revolutionary=True
            ),
            "holographic_ui": Feature(
                "holographic_ui", FeatureCategory.REVOLUTIONARY,
                "3D holographic market visualization",
                UserTier.PREMIUM, is_revolutionary=True
            ),
            
            # Revolutionary Features (Admin Tier)
            "ai_consciousness": Feature(
                "ai_consciousness", FeatureCategory.REVOLUTIONARY,
                "Self-aware AI consciousness engine",
                UserTier.ADMIN, is_revolutionary=True
            ),
            "neural_interface": Feature(
                "neural_interface", FeatureCategory.REVOLUTIONARY,
                "Brain-computer interface for thought-based trading",
                UserTier.ADMIN, is_revolutionary=True
            ),
            "temporal_trading": Feature(
                "temporal_trading", FeatureCategory.REVOLUTIONARY,
                "Time-based predictive trading algorithms",
                UserTier.ADMIN, is_revolutionary=True
            ),
            "multidimensional_analysis": Feature(
                "multidimensional_analysis", FeatureCategory.REVOLUTIONARY,
                "Cross-dimensional market analysis",
                UserTier.ADMIN, is_revolutionary=True
            ),
            
            # Admin Features
            "admin_panel": Feature(
                "admin_panel", FeatureCategory.ADMIN,
                "System administration and user management",
                UserTier.ADMIN
            ),
            "system_monitoring": Feature(
                "system_monitoring", FeatureCategory.ADMIN,
                "Real-time system performance monitoring",
                UserTier.ADMIN
            ),
            "user_management": Feature(
                "user_management", FeatureCategory.ADMIN,
                "User account and permission management",
                UserTier.ADMIN
            )
        }
        
        return features
    
    def _initialize_invitation_codes(self) -> Dict[str, Dict[str, Any]]:
        """Initialize invitation codes for premium access"""
        return {
            # Demo Tier Codes
            "BR123456": {
                "tier": UserTier.DEMO,
                "demo_tier": "bronze",
                "features": ["basic_trading", "portfolio_tracking", "48_hour_demo"],
                "investment_amount": 500,
                "expected_return": "8%"
            },
            
            # Premium Tier Codes
            "SI123456": {
                "tier": UserTier.PREMIUM,
                "demo_tier": "silver",
                "features": ["ai_insights_advanced", "quantum_trading", "blockchain_trading"],
                "investment_amount": 1000,
                "expected_return": "12%"
            },
            "GO123456": {
                "tier": UserTier.PREMIUM,
                "demo_tier": "gold",
                "features": ["ai_insights_advanced", "quantum_trading", "holographic_ui"],
                "investment_amount": 2500,
                "expected_return": "15%"
            },
            "EL123456": {
                "tier": UserTier.PREMIUM,
                "demo_tier": "elite",
                "features": ["ai_insights_advanced", "quantum_trading", "blockchain_trading", "holographic_ui"],
                "investment_amount": 5000,
                "expected_return": "20%"
            },
            
            # Admin Tier Codes
            "ADMIN2024": {
                "tier": UserTier.ADMIN,
                "demo_tier": "admin",
                "features": ["all_features"],
                "investment_amount": 10000,
                "expected_return": "25%"
            },
            "NEUROFORGE_ADMIN": {
                "tier": UserTier.ADMIN,
                "demo_tier": "admin",
                "features": ["all_revolutionary_features"],
                "investment_amount": 25000,
                "expected_return": "30%"
            }
        }
    
    def _setup_database(self):
        """Setup database tables for user access control"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # User access table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_access (
                        user_id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        tier TEXT NOT NULL,
                        demo_tier TEXT,
                        invitation_code TEXT,
                        features_enabled TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        demo_48h_active BOOLEAN DEFAULT TRUE,
                        demo_48h_start TIMESTAMP,
                        subscription_expires TIMESTAMP
                    )
                """)
                
                # Feature usage tracking
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS feature_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        feature_name TEXT,
                        access_granted BOOLEAN,
                        access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tier_at_access TEXT,
                        FOREIGN KEY (user_id) REFERENCES user_access (user_id)
                    )
                """)
                
                conn.commit()
                logger.info("[CHECK] User access control database initialized")
                
        except Exception as e:
            logger.error(f"[ERROR] Database setup failed: {e}")
            raise
    
    def validate_invitation_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Validate invitation code and return access details"""
        return self.invitation_codes.get(code)
    
    def create_user_access(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user access record with proper tier assignment"""
        try:
            # Determine user tier
            invitation_code = user_data.get('invitation_code')
            tier = UserTier.DEMO
            demo_tier = "bronze"
            features_enabled = []
            
            if invitation_code:
                invite_data = self.validate_invitation_code(invitation_code)
                if invite_data:
                    tier = invite_data['tier']
                    demo_tier = invite_data['demo_tier']
                    features_enabled = invite_data['features']
            
            # Get available features for tier
            available_features = self.get_features_for_tier(tier)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                user_access_data = {
                    'user_id': user_data['user_id'],
                    'email': user_data['email'],
                    'tier': tier,
                    'demo_tier': demo_tier,
                    'invitation_code': invitation_code,
                    'features_enabled': json.dumps(features_enabled),
                    'demo_48h_start': datetime.utcnow().isoformat()
                }
                
                cursor.execute("""
                    INSERT OR REPLACE INTO user_access 
                    (user_id, email, tier, demo_tier, invitation_code, features_enabled, demo_48h_start)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_access_data['user_id'],
                    user_access_data['email'],
                    user_access_data['tier'],
                    user_access_data['demo_tier'],
                    user_access_data['invitation_code'],
                    user_access_data['features_enabled'],
                    user_access_data['demo_48h_start']
                ))
                
                conn.commit()
                
            return {
                'user_access': user_access_data,
                'available_features': available_features,
                'tier': tier,
                'demo_tier': demo_tier,
                '48_hour_demo_active': True
            }
            
        except Exception as e:
            logger.error(f"[ERROR] User access creation failed: {e}")
            raise
    
    def get_features_for_tier(self, tier: UserTier) -> List[Dict[str, Any]]:
        """Get all features available for a specific tier"""
        available_features = []
        
        for feature_name, feature in self.features.items():
            # Check if user tier meets or exceeds required tier
            tier_hierarchy = [UserTier.DEMO, UserTier.PREMIUM, UserTier.ADMIN]
            user_tier_level = tier_hierarchy.index(tier)
            required_tier_level = tier_hierarchy.index(feature.required_tier)
            
            if user_tier_level >= required_tier_level:
                available_features.append({
                    'name': feature.name,
                    'category': feature.category,
                    'description': feature.description,
                    'is_revolutionary': feature.is_revolutionary,
                    'beta_feature': feature.beta_feature
                })
        
        return available_features
    
    def check_feature_access(self, user_id: str, feature_name: str) -> Dict[str, Any]:
        """Check if user has access to specific feature"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT tier, demo_tier, features_enabled, demo_48h_active, demo_48h_start
                    FROM user_access WHERE user_id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    # Default to demo access for unknown users
                    user_tier = UserTier.DEMO
                    demo_active = True
                else:
                    user_tier, demo_tier, features_enabled, demo_active, demo_start = result
                    user_tier = UserTier(user_tier)
                
                # Check feature access
                feature = self.features.get(feature_name)
                if not feature:
                    return {
                        'access_granted': False,
                        'reason': 'Feature not found',
                        'feature_name': feature_name
                    }
                
                # Check tier requirements
                tier_hierarchy = [UserTier.DEMO, UserTier.PREMIUM, UserTier.ADMIN]
                user_tier_level = tier_hierarchy.index(user_tier)
                required_tier_level = tier_hierarchy.index(feature.required_tier)
                
                access_granted = user_tier_level >= required_tier_level
                
                # Special case: 48-hour demo available to all tiers
                if feature_name == "48_hour_demo":
                    access_granted = True
                
                # Log feature access attempt
                cursor.execute("""
                    INSERT INTO feature_usage (user_id, feature_name, access_granted, tier_at_access)
                    VALUES (?, ?, ?, ?)
                """, (user_id, feature_name, access_granted, user_tier))
                
                conn.commit()
                
                return {
                    'access_granted': access_granted,
                    'user_tier': user_tier,
                    'required_tier': feature.required_tier,
                    'feature_name': feature_name,
                    'feature_description': feature.description,
                    'is_revolutionary': feature.is_revolutionary,
                    'upgrade_message': None if access_granted else f"Upgrade to {feature.required_tier} to access {feature_name}"
                }
                
        except Exception as e:
            logger.error(f"[ERROR] Feature access check failed: {e}")
            return {
                'access_granted': False,
                'reason': f'Access check failed: {str(e)}',
                'feature_name': feature_name
            }
    
    def get_user_access_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user access summary"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM user_access WHERE user_id = ?
                """, (user_id,))
                
                result = cursor.fetchone()
                
                if not result:
                    return {
                        'user_id': user_id,
                        'tier': UserTier.DEMO,
                        'available_features': self.get_features_for_tier(UserTier.DEMO),
                        '48_hour_demo_active': True
                    }
                
                columns = [desc[0] for desc in cursor.description]
                user_data = dict(zip(columns, result))
                
                user_tier = UserTier(user_data['tier'])
                available_features = self.get_features_for_tier(user_tier)
                
                # Check 48-hour demo status
                demo_start = user_data.get('demo_48h_start')
                demo_active = True
                if demo_start:
                    start_time = datetime.fromisoformat(demo_start)
                    demo_active = datetime.utcnow() - start_time < timedelta(hours=48)
                
                return {
                    'user_data': user_data,
                    'tier': user_tier,
                    'available_features': available_features,
                    'revolutionary_features': [f for f in available_features if f['is_revolutionary']],
                    '48_hour_demo_active': demo_active,
                    'total_features': len(available_features)
                }
                
        except Exception as e:
            logger.error(f"[ERROR] User access summary failed: {e}")
            return {
                'error': str(e),
                'user_id': user_id
            }
    
    def upgrade_user_tier(self, user_id: str, new_tier: UserTier, subscription_duration_days: int = 30) -> Dict[str, Any]:
        """Upgrade user to higher tier"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                subscription_expires = datetime.utcnow() + timedelta(days=subscription_duration_days)
                
                cursor.execute("""
                    UPDATE user_access 
                    SET tier = ?, subscription_expires = ?
                    WHERE user_id = ?
                """, (new_tier, subscription_expires.isoformat(), user_id))
                
                conn.commit()
                
                return {
                    'success': True,
                    'user_id': user_id,
                    'new_tier': new_tier,
                    'subscription_expires': subscription_expires.isoformat(),
                    'new_features': self.get_features_for_tier(new_tier)
                }
                
        except Exception as e:
            logger.error(f"[ERROR] User tier upgrade failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global access manager instance
access_manager = UserAccessManager()

def get_access_manager() -> UserAccessManager:
    """Get global access manager instance"""
    return access_manager
