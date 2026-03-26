"""
🎯 DUAL-TIER TRADING PERMISSION SYSTEM
Complete user permission management with paper-only defaults and admin-controlled live trading
"""

import sqlite3
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)

class UserTier(Enum):
    """User access tiers"""
    PAPER_ONLY = "paper_only"
    LIVE_APPROVED = "live_approved"
    ADMIN = "admin"

class TradingPermission(Enum):
    """Trading permission types"""
    PAPER_TRADING = "paper_trading"
    LIVE_TRADING = "live_trading"
    FUND_ALLOCATION = "fund_allocation"
    USER_MANAGEMENT = "user_management"
    SYSTEM_ADMIN = "system_admin"

@dataclass
class UserPermissions:
    """User permission data structure"""
    user_id: str
    tier: UserTier
    paper_trading_enabled: bool = True
    live_trading_enabled: bool = False
    allocated_funds: float = 0.0
    max_allocation: float = 0.0
    live_trading_activated_by: Optional[str] = None
    live_trading_activated_at: Optional[datetime] = None
    permissions: List[TradingPermission] = None
    session_limits: Dict[str, Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = [TradingPermission.PAPER_TRADING]
        if self.session_limits is None:
            self.session_limits = {
                "max_session_hours": 168,  # 1 week max
                "concurrent_sessions": 1,
                "daily_trades": 100
            }
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class FundAllocation:
    """Fund allocation record"""
    allocation_id: str
    user_id: str
    admin_id: str
    amount: float
    allocation_type: str  # 'initial', 'additional', 'withdrawal'
    reason: str
    allocated_at: datetime
    status: str  # 'pending', 'active', 'revoked'
    audit_trail: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.audit_trail is None:
            self.audit_trail = []

class DualTierPermissionSystem:
    """
    🎯 DUAL-TIER PERMISSION SYSTEM
    Manages user permissions with paper-only defaults and admin-controlled live trading
    """
    
    def __init__(self, db_path: str = "dual_tier_permissions.db"):
        self.db_path = db_path
        self.admin_users = set()  # Cache of admin user IDs
        self._init_database()
        self._create_default_admin()
        logger.info("🎯 Dual-Tier Permission System initialized")

    def _init_database(self):
        """Initialize permission database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_permissions (
                    user_id TEXT PRIMARY KEY,
                    tier TEXT NOT NULL,
                    paper_trading_enabled BOOLEAN DEFAULT TRUE,
                    live_trading_enabled BOOLEAN DEFAULT FALSE,
                    allocated_funds REAL DEFAULT 0.0,
                    max_allocation REAL DEFAULT 0.0,
                    live_trading_activated_by TEXT,
                    live_trading_activated_at TIMESTAMP,
                    permissions TEXT,  -- JSON array
                    session_limits TEXT,  -- JSON object
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fund_allocations (
                    allocation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    admin_id TEXT NOT NULL,
                    amount REAL NOT NULL,
                    allocation_type TEXT NOT NULL,
                    reason TEXT,
                    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'active',
                    audit_trail TEXT,  -- JSON array
                    FOREIGN KEY (user_id) REFERENCES user_permissions (user_id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS permission_audit_log (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    admin_id TEXT,
                    action TEXT NOT NULL,
                    details TEXT,  -- JSON object
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            """)
            
            conn.commit()
            logger.info("[CHECK] Permission database initialized")

    def _create_default_admin(self):
        """Create default admin user if none exists"""
        try:
            admin_id = "admin_prometheus_001"
            existing = self.get_user_permissions(admin_id)
            
            if not existing:
                admin_permissions = UserPermissions(
                    user_id=admin_id,
                    tier=UserTier.ADMIN,
                    paper_trading_enabled=True,
                    live_trading_enabled=True,
                    allocated_funds=1000000.0,  # $1M for admin testing
                    max_allocation=10000000.0,  # $10M max
                    permissions=[
                        TradingPermission.PAPER_TRADING,
                        TradingPermission.LIVE_TRADING,
                        TradingPermission.FUND_ALLOCATION,
                        TradingPermission.USER_MANAGEMENT,
                        TradingPermission.SYSTEM_ADMIN
                    ],
                    session_limits={
                        "max_session_hours": 720,  # 30 days for admin
                        "concurrent_sessions": 10,
                        "daily_trades": 10000
                    }
                )
                
                self.create_user_permissions(admin_permissions)
                self.admin_users.add(admin_id)
                logger.info(f"[CHECK] Default admin user created: {admin_id}")
                
        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")

    def create_user_permissions(self, permissions: UserPermissions) -> bool:
        """Create new user permissions (defaults to paper-only)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO user_permissions (
                        user_id, tier, paper_trading_enabled, live_trading_enabled,
                        allocated_funds, max_allocation, live_trading_activated_by,
                        live_trading_activated_at, permissions, session_limits
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    permissions.user_id,
                    permissions.tier.value,
                    permissions.paper_trading_enabled,
                    permissions.live_trading_enabled,
                    permissions.allocated_funds,
                    permissions.max_allocation,
                    permissions.live_trading_activated_by,
                    permissions.live_trading_activated_at,
                    json.dumps([p.value for p in permissions.permissions]),
                    json.dumps(permissions.session_limits)
                ))
                conn.commit()
                
                # Log the creation
                self._log_permission_action(
                    permissions.user_id,
                    None,
                    "user_created",
                    {"tier": permissions.tier.value, "permissions": [p.value for p in permissions.permissions]}
                )
                
                logger.info(f"[CHECK] User permissions created: {permissions.user_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to create user permissions: {e}")
            return False

    def get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM user_permissions WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                permissions_list = [TradingPermission(p) for p in json.loads(row['permissions'])]
                session_limits = json.loads(row['session_limits'])
                
                return UserPermissions(
                    user_id=row['user_id'],
                    tier=UserTier(row['tier']),
                    paper_trading_enabled=bool(row['paper_trading_enabled']),
                    live_trading_enabled=bool(row['live_trading_enabled']),
                    allocated_funds=float(row['allocated_funds']),
                    max_allocation=float(row['max_allocation']),
                    live_trading_activated_by=row['live_trading_activated_by'],
                    live_trading_activated_at=datetime.fromisoformat(row['live_trading_activated_at']) if row['live_trading_activated_at'] else None,
                    permissions=permissions_list,
                    session_limits=session_limits,
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at'])
                )
                
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return None

    def create_paper_only_user(self, user_id: str) -> bool:
        """Create a new paper-only user (default tier)"""
        paper_user = UserPermissions(
            user_id=user_id,
            tier=UserTier.PAPER_ONLY,
            paper_trading_enabled=True,
            live_trading_enabled=False,
            allocated_funds=0.0,
            max_allocation=0.0,
            permissions=[TradingPermission.PAPER_TRADING]
        )
        return self.create_user_permissions(paper_user)

    def has_permission(self, user_id: str, permission: TradingPermission) -> bool:
        """Check if user has specific permission"""
        user_perms = self.get_user_permissions(user_id)
        if not user_perms:
            return False
        return permission in user_perms.permissions

    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin"""
        user_perms = self.get_user_permissions(user_id)
        return user_perms and user_perms.tier == UserTier.ADMIN

    def can_access_live_trading(self, user_id: str) -> bool:
        """Check if user can access live trading"""
        user_perms = self.get_user_permissions(user_id)
        return (user_perms and
                user_perms.live_trading_enabled and
                user_perms.allocated_funds > 0 and
                TradingPermission.LIVE_TRADING in user_perms.permissions)

    def allocate_funds(self, user_id: str, admin_id: str, amount: float, reason: str = "") -> bool:
        """Allocate funds to user (admin only)"""
        try:
            # Verify admin permissions
            if not self.is_admin(admin_id):
                logger.warning(f"Non-admin {admin_id} attempted fund allocation")
                return False

            user_perms = self.get_user_permissions(user_id)
            if not user_perms:
                logger.warning(f"User {user_id} not found for fund allocation")
                return False

            # Create allocation record
            allocation = FundAllocation(
                allocation_id=str(uuid.uuid4()),
                user_id=user_id,
                admin_id=admin_id,
                amount=amount,
                allocation_type="additional" if user_perms.allocated_funds > 0 else "initial",
                reason=reason,
                allocated_at=datetime.now(),
                status="active"
            )

            # Update user funds
            new_funds = user_perms.allocated_funds + amount
            with sqlite3.connect(self.db_path) as conn:
                # Insert allocation record
                conn.execute("""
                    INSERT INTO fund_allocations (
                        allocation_id, user_id, admin_id, amount, allocation_type,
                        reason, status, audit_trail
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    allocation.allocation_id,
                    allocation.user_id,
                    allocation.admin_id,
                    allocation.amount,
                    allocation.allocation_type,
                    allocation.reason,
                    allocation.status,
                    json.dumps(allocation.audit_trail)
                ))

                # Update user permissions
                conn.execute("""
                    UPDATE user_permissions
                    SET allocated_funds = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (new_funds, user_id))

                conn.commit()

            # Log the allocation
            self._log_permission_action(
                user_id,
                admin_id,
                "funds_allocated",
                {
                    "amount": amount,
                    "new_total": new_funds,
                    "allocation_id": allocation.allocation_id,
                    "reason": reason
                }
            )

            logger.info(f"[CHECK] Funds allocated: ${amount:,.2f} to {user_id} by {admin_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to allocate funds: {e}")
            return False

    def activate_live_trading(self, user_id: str, admin_id: str) -> bool:
        """Activate live trading for user (admin only)"""
        try:
            # Verify admin permissions
            if not self.is_admin(admin_id):
                logger.warning(f"Non-admin {admin_id} attempted live trading activation")
                return False

            user_perms = self.get_user_permissions(user_id)
            if not user_perms:
                logger.warning(f"User {user_id} not found for live trading activation")
                return False

            # Check if user has allocated funds
            if user_perms.allocated_funds <= 0:
                logger.warning(f"Cannot activate live trading for {user_id} - no allocated funds")
                return False

            # Update user permissions
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE user_permissions
                    SET live_trading_enabled = TRUE,
                        tier = ?,
                        live_trading_activated_by = ?,
                        live_trading_activated_at = CURRENT_TIMESTAMP,
                        permissions = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (
                    UserTier.LIVE_APPROVED.value,
                    admin_id,
                    json.dumps([TradingPermission.PAPER_TRADING.value, TradingPermission.LIVE_TRADING.value]),
                    user_id
                ))
                conn.commit()

            # Log the activation
            self._log_permission_action(
                user_id,
                admin_id,
                "live_trading_activated",
                {
                    "allocated_funds": user_perms.allocated_funds,
                    "activation_time": datetime.now().isoformat()
                }
            )

            logger.info(f"[CHECK] Live trading activated for {user_id} by {admin_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to activate live trading: {e}")
            return False

    def _log_permission_action(self, user_id: str, admin_id: Optional[str], action: str, details: Dict[str, Any]):
        """Log permission-related actions for audit"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO permission_audit_log (
                        log_id, user_id, admin_id, action, details
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    user_id,
                    admin_id,
                    action,
                    json.dumps(details)
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log permission action: {e}")

    def get_user_allocations(self, user_id: str) -> List[FundAllocation]:
        """Get all fund allocations for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT * FROM fund_allocations
                    WHERE user_id = ?
                    ORDER BY allocated_at DESC
                """, (user_id,))

                allocations = []
                for row in cursor.fetchall():
                    allocation = FundAllocation(
                        allocation_id=row['allocation_id'],
                        user_id=row['user_id'],
                        admin_id=row['admin_id'],
                        amount=float(row['amount']),
                        allocation_type=row['allocation_type'],
                        reason=row['reason'],
                        allocated_at=datetime.fromisoformat(row['allocated_at']),
                        status=row['status'],
                        audit_trail=json.loads(row['audit_trail']) if row['audit_trail'] else []
                    )
                    allocations.append(allocation)

                return allocations

        except Exception as e:
            logger.error(f"Failed to get user allocations: {e}")
            return []

# Global instance
dual_tier_system = DualTierPermissionSystem()
