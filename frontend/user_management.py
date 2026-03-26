import os
"""
User Management System for MASS Framework

Comprehensive user management with multi-tenant support:
- Registration and authentication
- Role-based access control
- Organization management
- Subscription and billing integration
- Social media authentication
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import secrets
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt
from passlib.context import CryptContext


class UserRole(Enum):
    """User roles with hierarchical permissions"""
    MASTER_ADMIN = "master_admin"      # Full system access
    ORG_ADMIN = "org_admin"           # Organization admin
    PROJECT_MANAGER = "project_manager" # Project management
    DEVELOPER = "developer"            # Development access
    USER = "user"                     # Basic access
    VIEWER = "viewer"                 # Read-only access


class SubscriptionTier(Enum):
    """Subscription tiers with different features"""
    FREE = "free"                     # Free tier - limited features
    STARTER = "starter"               # $29/month - basic features
    PROFESSIONAL = "professional"     # $99/month - advanced features
    ENTERPRISE = "enterprise"         # $299/month - full features
    MASTER = "master"                 # Free for master admin


@dataclass
class Organization:
    """Organization/tenant structure"""
    org_id: str
    name: str
    domain: Optional[str] = None
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    created_at: datetime = field(default_factory=datetime.utcnow)
    max_users: int = 5
    max_projects: int = 3
    max_agents: int = 10
    is_active: bool = True
    billing_email: Optional[str] = None
    custom_branding: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'org_id': self.org_id,
            'name': self.name,
            'domain': self.domain,
            'subscription_tier': self.subscription_tier.value,
            'created_at': self.created_at.isoformat(),
            'max_users': self.max_users,
            'max_projects': self.max_projects,
            'max_agents': self.max_agents,
            'is_active': self.is_active,
            'billing_email': self.billing_email,
            'custom_branding': self.custom_branding
        }


@dataclass
class User:
    """User model with organization association"""
    user_id: str
    email: str
    username: str
    password_hash: str
    full_name: str
    role: UserRole
    org_id: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    profile_image: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'username': self.username,
            'full_name': self.full_name,
            'role': self.role.value,
            'org_id': self.org_id,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'profile_image': self.profile_image,
            'preferences': self.preferences
        }


@dataclass
class SocialAccount:
    """Social media account linked to user"""
    provider: str
    provider_id: str
    provider_username: Optional[str] = None
    provider_avatar: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    linked_at: datetime = field(default_factory=datetime.utcnow)


# Pydantic models for API
class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str
    org_name: Optional[str] = None
    org_domain: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class OrganizationCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    billing_email: Optional[EmailStr] = None


class UserManagementSystem:
    """Complete user management system"""
    
    def __init__(self, jwt_secret: str = None):
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.users: Dict[str, User] = {}
        self.organizations: Dict[str, Organization] = {}
        self.social_accounts: Dict[str, List[SocialAccount]] = {}  # user_id -> [social_accounts]
        self.email_to_user: Dict[str, str] = {}  # email -> user_id
        self.social_to_user: Dict[str, str] = {}  # provider:provider_id -> user_id
        
        # Initialize master admin
        self._create_master_admin()
    
    def _create_master_admin(self):
        """Create the master admin user"""
        master_admin_id = str(uuid.uuid4())
        master_org_id = str(uuid.uuid4())
        
        # Create master organization
        master_org = Organization(
            org_id=master_org_id,
            name="MASS Framework Administration",
            subscription_tier=SubscriptionTier.MASTER,
            max_users=1000,
            max_projects=1000,
            max_agents=1000,
            custom_branding=True
        )
        self.organizations[master_org_id] = master_org
        
        # Create master admin user
        master_admin = User(
            user_id=master_admin_id,
            email="admin@mass-framework.com",
            username="master_admin",
            password_hash=self.pwd_context.hash("MasterAdmin2025!"),
            full_name="Master Administrator",
            role=UserRole.MASTER_ADMIN,
            org_id=master_org_id,
            is_active=True,
            is_verified=True
        )
        
        self.users[master_admin_id] = master_admin
        self.email_to_user["admin@mass-framework.com"] = master_admin_id
    
    async def register_user(self, registration: UserRegistration) -> Dict[str, Any]:
        """Register a new user and optionally create organization"""
        # Check if email already exists
        if registration.email in self.email_to_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user_id = str(uuid.uuid4())
        org_id = None
        
        # Create organization if provided
        if registration.org_name:
            org_id = await self._create_organization(
                registration.org_name,
                registration.org_domain,
                registration.email
            )
            role = UserRole.ORG_ADMIN
        else:
            role = UserRole.USER
        
        # Hash password
        password_hash = self.pwd_context.hash(registration.password)
        
        # Create user
        user = User(
            user_id=user_id,
            email=registration.email,
            username=registration.username,
            password_hash=password_hash,
            full_name=registration.full_name,
            role=role,
            org_id=org_id
        )
        
        # Store user
        self.users[user_id] = user
        self.email_to_user[registration.email] = user_id
        
        # Generate verification token (in production, send email)
        verification_token = self._generate_jwt_token(user, expires_delta=timedelta(days=7))
        
        return {
            "user": user.to_dict(),
            "verification_token": verification_token,
            "message": "Registration successful. Please verify your email."
        }
    
    async def login_user(self, login: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        user_id = self.email_to_user.get(login.email)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = self.users[user_id]
        
        # Verify password
        if not self.pwd_context.verify(login.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account is deactivated")
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Generate tokens
        access_token = self._generate_jwt_token(user, expires_delta=timedelta(hours=24))
        refresh_token = self._generate_jwt_token(user, expires_delta=timedelta(days=30))
        
        # Get organization info
        org_info = None
        if user.org_id:
            org_info = self.organizations[user.org_id].to_dict()
        
        return {
            "user": user.to_dict(),
            "organization": org_info,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            if user_id and user_id in self.users:
                user = self.users[user_id]
                if user.is_active:
                    return user
            
            return None
            
        except jwt.InvalidTokenError:
            return None
    
    async def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for resource and action"""
        # Master admin has all permissions
        if user.role == UserRole.MASTER_ADMIN:
            return True
        
        # Role-based permissions
        permissions = {
            UserRole.ORG_ADMIN: {
                "users": ["create", "read", "update", "delete"],
                "projects": ["create", "read", "update", "delete"],
                "agents": ["create", "read", "update", "delete"],
                "billing": ["read", "update"],
                "organization": ["read", "update"]
            },
            UserRole.PROJECT_MANAGER: {
                "projects": ["create", "read", "update"],
                "agents": ["create", "read", "update"],
                "users": ["read"]
            },
            UserRole.DEVELOPER: {
                "projects": ["read", "update"],
                "agents": ["create", "read", "update"],
                "code": ["create", "read", "update"]
            },
            UserRole.USER: {
                "projects": ["read"],
                "agents": ["read"],
                "profile": ["read", "update"]
            },
            UserRole.VIEWER: {
                "projects": ["read"],
                "agents": ["read"]
            }
        }
        
        user_permissions = permissions.get(user.role, {})
        resource_permissions = user_permissions.get(resource, [])
        
        return action in resource_permissions
    
    async def get_organization_users(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all users in an organization"""
        org_users = []
        for user in self.users.values():
            if user.org_id == org_id:
                org_users.append(user.to_dict())
        
        return org_users
    
    async def update_subscription(self, org_id: str, new_tier: SubscriptionTier) -> Dict[str, Any]:
        """Update organization subscription tier"""
        if org_id not in self.organizations:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        org = self.organizations[org_id]
        old_tier = org.subscription_tier
        org.subscription_tier = new_tier
        
        # Update limits based on tier
        tier_limits = {
            SubscriptionTier.FREE: {"users": 5, "projects": 3, "agents": 10},
            SubscriptionTier.STARTER: {"users": 25, "projects": 10, "agents": 50},
            SubscriptionTier.PROFESSIONAL: {"users": 100, "projects": 50, "agents": 200},
            SubscriptionTier.ENTERPRISE: {"users": 500, "projects": 200, "agents": 1000},
            SubscriptionTier.MASTER: {"users": 1000, "projects": 1000, "agents": 1000}
        }
        
        limits = tier_limits.get(new_tier, tier_limits[SubscriptionTier.FREE])
        org.max_users = limits["users"]
        org.max_projects = limits["projects"]
        org.max_agents = limits["agents"]
        
        # Enable custom branding for paid tiers
        org.custom_branding = new_tier != SubscriptionTier.FREE
        
        return {
            "organization": org.to_dict(),
            "previous_tier": old_tier.value,
            "new_tier": new_tier.value,
            "message": f"Subscription updated to {new_tier.value}"
        }
    
    async def get_user_dashboard_data(self, user: User) -> Dict[str, Any]:
        """Get dashboard data for user"""
        dashboard_data = {
            "user": user.to_dict(),
            "permissions": {},
            "organization": None,
            "stats": {
                "projects": 0,
                "agents": 0,
                "team_members": 0
            }
        }
        
        # Get organization info
        if user.org_id:
            org = self.organizations.get(user.org_id)
            if org:
                dashboard_data["organization"] = org.to_dict()
                
                # Get org stats
                org_users = await self.get_organization_users(user.org_id)
                dashboard_data["stats"]["team_members"] = len(org_users)
        
        # Get user permissions
        resources = ["users", "projects", "agents", "billing", "organization"]
        actions = ["create", "read", "update", "delete"]
        
        for resource in resources:
            dashboard_data["permissions"][resource] = {}
            for action in actions:
                dashboard_data["permissions"][resource][action] = await self.check_permission(
                    user, resource, action
                )
        
        return dashboard_data
    
    async def _create_organization(self, name: str, domain: str = None, 
                                 billing_email: str = None) -> str:
        """Create a new organization"""
        org_id = str(uuid.uuid4())
        
        org = Organization(
            org_id=org_id,
            name=name,
            domain=domain,
            billing_email=billing_email
        )
        
        self.organizations[org_id] = org
        return org_id
    
    def _generate_jwt_token(self, user: User, expires_delta: timedelta = None) -> str:
        """Generate JWT token for user"""
        if expires_delta is None:
            expires_delta = timedelta(hours=24)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "org_id": user.org_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")
    
    # Social Authentication Methods
    async def get_user_by_social_id(self, provider: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get user by social media provider ID"""
        social_key = f"{provider}:{provider_id}"
        user_id = self.social_to_user.get(social_key)
        if user_id and user_id in self.users:
            return self.users[user_id].to_dict()
        return None
    
    async def create_user_from_social(self, social_user) -> Dict[str, Any]:
        """Create a new user from social media data"""
        user_id = str(uuid.uuid4())
        
        # Generate username if not provided
        username = social_user.username or social_user.email.split('@')[0] if social_user.email else f"user_{user_id[:8]}"
        
        # Ensure unique username
        counter = 1
        original_username = username
        while any(u.username == username for u in self.users.values()):
            username = f"{original_username}_{counter}"
            counter += 1
        
        # Create user with minimal password (since they'll login via social)
        temp_password = secrets.token_urlsafe(32)
        
        user = User(
            user_id=user_id,
            email=social_user.email or f"noemail_{user_id}@example.com",
            username=username,
            password_hash=self.pwd_context.hash(temp_password),
            full_name=social_user.name or username,
            role=UserRole.USER,
            is_verified=True,  # Social accounts are pre-verified
            profile_image=social_user.avatar_url
        )
        
        self.users[user_id] = user
        if social_user.email:
            self.email_to_user[social_user.email] = user_id
        
        # Link social account
        await self.link_social_account(user_id, social_user)
        
        return user.to_dict()
    
    async def link_social_account(self, user_id: str, social_user) -> None:
        """Link a social media account to an existing user"""
        if user_id not in self.users:
            raise ValueError("User not found")
        
        social_account = SocialAccount(
            provider=social_user.provider,
            provider_id=social_user.provider_id,
            provider_username=social_user.username,
            provider_avatar=social_user.avatar_url,
            access_token=social_user.access_token,
            refresh_token=social_user.refresh_token,
            token_expires_at=social_user.token_expires_at
        )
        
        if user_id not in self.social_accounts:
            self.social_accounts[user_id] = []
        
        # Remove existing account for same provider
        self.social_accounts[user_id] = [
            acc for acc in self.social_accounts[user_id] 
            if acc.provider != social_user.provider
        ]
        
        # Add new account
        self.social_accounts[user_id].append(social_account)
        
        # Update social-to-user mapping
        social_key = f"{social_user.provider}:{social_user.provider_id}"
        self.social_to_user[social_key] = user_id
    
    async def unlink_social_account(self, user_id: str, provider: str) -> None:
        """Unlink a social media account from a user"""
        if user_id not in self.social_accounts:
            return
        
        # Find and remove the account
        old_accounts = self.social_accounts[user_id]
        self.social_accounts[user_id] = [
            acc for acc in old_accounts if acc.provider != provider
        ]
        
        # Remove from social-to-user mapping
        removed_account = next((acc for acc in old_accounts if acc.provider == provider), None)
        if removed_account:
            social_key = f"{provider}:{removed_account.provider_id}"
            self.social_to_user.pop(social_key, None)
    
    async def update_social_data(self, user_id: str, social_user) -> None:
        """Update user's social media data"""
        if user_id not in self.users:
            return
        
        user = self.users[user_id]
        
        # Update profile image if not set
        if not user.profile_image and social_user.avatar_url:
            user.profile_image = social_user.avatar_url
        
        # Update social account data
        if user_id in self.social_accounts:
            for account in self.social_accounts[user_id]:
                if account.provider == social_user.provider:
                    account.access_token = social_user.access_token
                    account.refresh_token = social_user.refresh_token
                    account.token_expires_at = social_user.token_expires_at
                    account.provider_avatar = social_user.avatar_url
                    break
    
    async def get_user_social_accounts(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all social accounts linked to a user"""
        if user_id not in self.social_accounts:
            return []
        
        accounts = []
        for account in self.social_accounts[user_id]:
            accounts.append({
                "provider": account.provider,
                "provider_username": account.provider_username,
                "provider_avatar": account.provider_avatar,
                "linked_at": account.linked_at.isoformat(),
                "is_token_valid": account.token_expires_at is None or account.token_expires_at > datetime.utcnow()
            })
        
        return accounts
    
    async def generate_jwt_token(self, user: Dict[str, Any]) -> str:
        """Generate JWT token for a user (wrapper for compatibility)"""
        user_obj = User(
            user_id=user["user_id"],
            email=user["email"],
            username=user["username"],
            password_hash="",  # Not needed for token generation
            full_name=user["full_name"],
            role=UserRole(user["role"]),
            org_id=user.get("org_id")
        )
        return self._generate_jwt_token(user_obj)
    
    # Continue with existing methods...


# FastAPI security
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                          user_system: UserManagementSystem = None) -> User:
    """Get current authenticated user"""
    if not user_system:
        raise HTTPException(status_code=500, detail="User system not initialized")
    
    token = credentials.credentials
    user = await user_system.verify_token(token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user


# Demo function
async def demo_user_management():
    """Demonstrate user management system"""
    print("=== User Management System Demo ===")
    
    # Initialize system
    user_system = UserManagementSystem()
    
    # Register a new user with organization
    registration = UserRegistration(
        email="john.doe@example.com",
        username="johndoe",
        full_name="John Doe",
        password = os.getenv("ADMIN_PASSWORD"),
        org_name="Acme Corporation",
        org_domain="acme.com"
    )
    
    try:
        result = await user_system.register_user(registration)
        print(f"✓ User registered: {result['user']['email']}")
        print(f"✓ Organization created: {result['user']['org_id']}")
        
        # Login user
        login = UserLogin(email="john.doe@example.com", password = os.getenv("ADMIN_PASSWORD"))
        login_result = await user_system.login_user(login)
        print(f"✓ User logged in: {login_result['user']['username']}")
        
        # Get dashboard data
        user = user_system.users[login_result['user']['user_id']]
        dashboard = await user_system.get_user_dashboard_data(user)
        print(f"✓ Dashboard data retrieved for: {dashboard['user']['full_name']}")
        
        # Check permissions
        can_create_users = await user_system.check_permission(user, "users", "create")
        print(f"✓ Can create users: {can_create_users}")
        
        # Get pricing
        pricing = user_system.get_subscription_pricing()
        print(f"✓ Pricing tiers available: {len(pricing['tiers'])}")
        
        print(f"\n✓ User management system working perfectly!")
        
    except Exception as e:
        print(f"Error in demo: {e}")


if __name__ == "__main__":
    asyncio.run(demo_user_management())
