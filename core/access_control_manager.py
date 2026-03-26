"""
🔐 PROMETHEUS Access Control Manager
Role-based permissions system for trading access control
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    DEMO_USER = "demo_user"

class PermissionType(Enum):
    LIVE_TRADING = "live_trading"
    PAPER_TRADING = "paper_trading"
    VIEW_PORTFOLIOS = "view_portfolios"
    MANAGE_USERS = "manage_users"
    SYSTEM_ADMIN = "system_admin"
    ALLOCATE_FUNDS = "allocate_funds"

@dataclass
class UserPermissions:
    user_id: str
    role: UserRole
    permissions: Set[PermissionType]
    live_trading_approved: bool
    max_allocation: float
    current_allocation: float
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    restrictions: Dict[str, Any]
    is_active: bool

@dataclass
class AllocationRequest:
    request_id: str
    user_id: str
    requested_amount: float
    justification: str
    status: str  # 'pending', 'approved', 'rejected'
    requested_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    admin_notes: Optional[str] = None

class AccessControlManager:
    """
    Manages user roles, permissions, and trading access control
    """
    
    def __init__(self, db_path: str = "access_control.db"):
        self.db_path = db_path
        self._init_database()
        self._create_default_admin()

    def _init_database(self):
        """Initialize access control database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User roles and permissions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_permissions (
                    user_id TEXT PRIMARY KEY,
                    role TEXT NOT NULL DEFAULT 'demo_user',
                    permissions TEXT NOT NULL DEFAULT '[]',
                    live_trading_approved BOOLEAN DEFAULT 0,
                    max_allocation REAL DEFAULT 0,
                    current_allocation REAL DEFAULT 0,
                    approved_by TEXT,
                    approved_at TIMESTAMP,
                    restrictions TEXT DEFAULT '{}',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Allocation requests
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS allocation_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    requested_amount REAL NOT NULL,
                    justification TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by TEXT,
                    reviewed_at TIMESTAMP,
                    admin_notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_permissions (user_id)
                )
            """)
            
            # Permission audit log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permission_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    old_permissions TEXT,
                    new_permissions TEXT,
                    changed_by TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reason TEXT
                )
            """)
            
            # Admin actions log
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    target_user_id TEXT,
                    action_details TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                )
            """)
            
            conn.commit()
            logger.info("Access control database initialized")

    @contextmanager
    def get_db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _create_default_admin(self):
        """Create default admin user if none exists"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM user_permissions WHERE role = 'admin'")
            admin_count = cursor.fetchone()['count']
            
            if admin_count == 0:
                admin_id = "admin_default"
                admin_permissions = [
                    PermissionType.LIVE_TRADING,
                    PermissionType.PAPER_TRADING,
                    PermissionType.VIEW_PORTFOLIOS,
                    PermissionType.MANAGE_USERS,
                    PermissionType.SYSTEM_ADMIN,
                    PermissionType.ALLOCATE_FUNDS
                ]
                
                cursor.execute("""
                    INSERT INTO user_permissions 
                    (user_id, role, permissions, live_trading_approved, max_allocation, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    admin_id,
                    UserRole.ADMIN.value,
                    json.dumps([p.value for p in admin_permissions]),
                    True,
                    1000000.0,  # $1M default admin allocation
                    True
                ))
                conn.commit()
                logger.info("Created default admin user")

    def create_user_permissions(self, user_id: str, role: UserRole = UserRole.DEMO_USER) -> bool:
        """Create initial permissions for a new user"""
        try:
            # Define default permissions by role
            role_permissions = {
                UserRole.ADMIN: [
                    PermissionType.LIVE_TRADING,
                    PermissionType.PAPER_TRADING,
                    PermissionType.VIEW_PORTFOLIOS,
                    PermissionType.MANAGE_USERS,
                    PermissionType.SYSTEM_ADMIN,
                    PermissionType.ALLOCATE_FUNDS
                ],
                UserRole.TRADER: [
                    PermissionType.PAPER_TRADING,
                    PermissionType.VIEW_PORTFOLIOS
                ],
                UserRole.VIEWER: [
                    PermissionType.VIEW_PORTFOLIOS
                ],
                UserRole.DEMO_USER: [
                    PermissionType.PAPER_TRADING
                ]
            }
            
            permissions = role_permissions.get(role, [PermissionType.PAPER_TRADING])
            
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO user_permissions
                    (user_id, role, permissions, live_trading_approved, max_allocation, current_allocation)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    role.value,
                    json.dumps([p.value for p in permissions]),
                    role == UserRole.ADMIN,
                    1000000.0 if role == UserRole.ADMIN else 0.0,
                    0.0
                ))
                conn.commit()
            
            logger.info(f"Created permissions for user {user_id} with role {role.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create user permissions: {e}")
            return False

    def get_user_permissions(self, user_id: str) -> Optional[UserPermissions]:
        """Get user permissions and role"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_permissions WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            permissions_list = json.loads(row['permissions'])
            permissions_set = {PermissionType(p) for p in permissions_list}
            
            return UserPermissions(
                user_id=row['user_id'],
                role=UserRole(row['role']),
                permissions=permissions_set,
                live_trading_approved=bool(row['live_trading_approved']),
                max_allocation=row['max_allocation'],
                current_allocation=row['current_allocation'],
                approved_by=row['approved_by'],
                approved_at=datetime.fromisoformat(row['approved_at']) if row['approved_at'] else None,
                restrictions=json.loads(row['restrictions']),
                is_active=bool(row['is_active'])
            )

    def has_permission(self, user_id: str, permission: PermissionType) -> bool:
        """Check if user has specific permission"""
        user_perms = self.get_user_permissions(user_id)
        if not user_perms or not user_perms.is_active:
            return False
        
        return permission in user_perms.permissions

    def approve_live_trading(self, user_id: str, admin_id: str, max_allocation: float, 
                           reason: str = "") -> bool:
        """Approve user for live trading"""
        try:
            # Check if admin has permission
            if not self.has_permission(admin_id, PermissionType.MANAGE_USERS):
                logger.warning(f"Admin {admin_id} lacks permission to approve live trading")
                return False
            
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Update user permissions
                cursor.execute("""
                    UPDATE user_permissions 
                    SET live_trading_approved = 1, max_allocation = ?, approved_by = ?, 
                        approved_at = ?, updated_at = ?
                    WHERE user_id = ?
                """, (max_allocation, admin_id, datetime.now().isoformat(), 
                      datetime.now().isoformat(), user_id))
                
                # Add live trading permission if not already present
                cursor.execute("SELECT permissions FROM user_permissions WHERE user_id = ?", (user_id,))
                current_perms = json.loads(cursor.fetchone()['permissions'])
                
                if PermissionType.LIVE_TRADING.value not in current_perms:
                    current_perms.append(PermissionType.LIVE_TRADING.value)
                    cursor.execute("""
                        UPDATE user_permissions SET permissions = ? WHERE user_id = ?
                    """, (json.dumps(current_perms), user_id))
                
                # Log admin action
                cursor.execute("""
                    INSERT INTO admin_actions
                    (admin_id, action_type, target_user_id, action_details)
                    VALUES (?, ?, ?, ?)
                """, (admin_id, "approve_live_trading", user_id, 
                      f"Approved live trading with ${max_allocation:,.2f} allocation. Reason: {reason}"))
                
                conn.commit()
            
            logger.info(f"Approved live trading for user {user_id} by admin {admin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to approve live trading: {e}")
            return False

    def revoke_live_trading(self, user_id: str, admin_id: str, reason: str = "") -> bool:
        """Revoke live trading access"""
        try:
            if not self.has_permission(admin_id, PermissionType.MANAGE_USERS):
                return False
            
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Update permissions
                cursor.execute("""
                    UPDATE user_permissions 
                    SET live_trading_approved = 0, updated_at = ?
                    WHERE user_id = ?
                """, (datetime.now().isoformat(), user_id))
                
                # Remove live trading permission
                cursor.execute("SELECT permissions FROM user_permissions WHERE user_id = ?", (user_id,))
                current_perms = json.loads(cursor.fetchone()['permissions'])
                
                if PermissionType.LIVE_TRADING.value in current_perms:
                    current_perms.remove(PermissionType.LIVE_TRADING.value)
                    cursor.execute("""
                        UPDATE user_permissions SET permissions = ? WHERE user_id = ?
                    """, (json.dumps(current_perms), user_id))
                
                # Log admin action
                cursor.execute("""
                    INSERT INTO admin_actions
                    (admin_id, action_type, target_user_id, action_details)
                    VALUES (?, ?, ?, ?)
                """, (admin_id, "revoke_live_trading", user_id, f"Revoked live trading. Reason: {reason}"))
                
                conn.commit()
            
            logger.info(f"Revoked live trading for user {user_id} by admin {admin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke live trading: {e}")
            return False

    def allocate_funds(self, user_id: str, admin_id: str, amount: float, reason: str = "") -> bool:
        """Allocate funds to a user's live trading account"""
        try:
            if not self.has_permission(admin_id, PermissionType.ALLOCATE_FUNDS):
                return False
            
            user_perms = self.get_user_permissions(user_id)
            if not user_perms or not user_perms.live_trading_approved:
                logger.warning(f"Cannot allocate funds to user {user_id} - not approved for live trading")
                return False
            
            new_allocation = user_perms.current_allocation + amount
            if new_allocation > user_perms.max_allocation:
                logger.warning(f"Allocation ${new_allocation:,.2f} exceeds max ${user_perms.max_allocation:,.2f}")
                return False
            
            with self.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE user_permissions 
                    SET current_allocation = ?, updated_at = ?
                    WHERE user_id = ?
                """, (new_allocation, datetime.now().isoformat(), user_id))
                
                # Log allocation
                cursor.execute("""
                    INSERT INTO admin_actions
                    (admin_id, action_type, target_user_id, action_details)
                    VALUES (?, ?, ?, ?)
                """, (admin_id, "allocate_funds", user_id, 
                      f"Allocated ${amount:,.2f}. New total: ${new_allocation:,.2f}. Reason: {reason}"))
                
                conn.commit()
            
            logger.info(f"Allocated ${amount:,.2f} to user {user_id} by admin {admin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to allocate funds: {e}")
            return False

    def request_allocation(self, user_id: str, amount: float, justification: str) -> str:
        """Submit allocation request"""
        request_id = str(uuid.uuid4())
        
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO allocation_requests
                (request_id, user_id, requested_amount, justification)
                VALUES (?, ?, ?, ?)
            """, (request_id, user_id, amount, justification))
            conn.commit()
        
        logger.info(f"User {user_id} requested ${amount:,.2f} allocation")
        return request_id

    def get_pending_requests(self) -> List[Dict]:
        """Get all pending allocation requests"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM allocation_requests 
                WHERE status = 'pending'
                ORDER BY requested_at ASC
            """)
            
            requests = []
            for row in cursor.fetchall():
                requests.append({
                    'request_id': row['request_id'],
                    'user_id': row['user_id'],
                    'requested_amount': row['requested_amount'],
                    'justification': row['justification'],
                    'requested_at': row['requested_at']
                })
            
            return requests

    def get_all_users_permissions(self) -> List[Dict]:
        """Get permissions for all users (admin only)"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, role, live_trading_approved, max_allocation, 
                       current_allocation, is_active, created_at
                FROM user_permissions
                ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append({
                    'user_id': row['user_id'],
                    'role': row['role'],
                    'live_trading_approved': bool(row['live_trading_approved']),
                    'max_allocation': row['max_allocation'],
                    'current_allocation': row['current_allocation'],
                    'is_active': bool(row['is_active']),
                    'created_at': row['created_at']
                })
            
            return users

# Global instance
access_control_manager = AccessControlManager()
