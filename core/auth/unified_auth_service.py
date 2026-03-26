#!/usr/bin/env python3
"""
🔐 UNIFIED AUTHENTICATION SERVICE
Consolidates all authentication functionality from:
- core/auth_service.py (PRIMARY - most complete)
- core/security/authentication.py (JWT enhancements)
- enterprise/security/enterprise_auth.py (MFA features)
- core/security_enhancements.py (Security validation)

Single source of truth for all authentication needs
"""

import os
import jwt
import bcrypt
import secrets
import pyotp
import qrcode
from io import BytesIO
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from fastapi import HTTPException, Request

# Try to import jose as fallback
try:
    from jose import jwt as jose_jwt
except ImportError:
    jose_jwt = None

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS AND DATA MODELS
# =============================================================================

class UserRole(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    TRADER = "trader"
    VIEWER = "viewer"

class Permission(Enum):
    """System permissions"""
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    READ_TRADING = "read_trading"
    WRITE_TRADING = "write_trading"
    EXECUTE_TRADES = "execute_trades"
    READ_ANALYTICS = "read_analytics"
    WRITE_ANALYTICS = "write_analytics"
    ADMIN_ACCESS = "admin_access"
    API_ACCESS = "api_access"

@dataclass
class SecurityConfig:
    """Unified security configuration"""
    # JWT Settings
    jwt_secret_key: str = field(default_factory=lambda: os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32)))
    jwt_expiration_hours: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    jwt_algorithm: str = "HS256"
    
    # Password Security
    password_min_length: int = int(os.getenv('PASSWORD_MIN_LENGTH', '8'))
    password_require_uppercase: bool = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'true').lower() == 'true'
    password_require_numbers: bool = os.getenv('PASSWORD_REQUIRE_NUMBERS', 'true').lower() == 'true'
    password_require_special: bool = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'false').lower() == 'true'
    
    # Session Management
    session_timeout_minutes: int = int(os.getenv('SESSION_TIMEOUT_MINUTES', '30'))
    max_login_attempts: int = int(os.getenv('MAX_LOGIN_ATTEMPTS', '5'))
    lockout_duration_minutes: int = int(os.getenv('LOCKOUT_DURATION_MINUTES', '15'))
    concurrent_sessions_limit: int = int(os.getenv('CONCURRENT_SESSIONS_LIMIT', '3'))
    
    # MFA Settings
    mfa_enabled: bool = os.getenv('MFA_ENABLED', 'false').lower() == 'true'
    mfa_required_for_admin: bool = os.getenv('MFA_REQUIRED_FOR_ADMIN', 'true').lower() == 'true'
    mfa_issuer: str = os.getenv('MFA_ISSUER', 'PROMETHEUS Trading')
    
    # Enterprise Features
    enterprise_mode: bool = os.getenv('ENTERPRISE_MODE', 'false').lower() == 'true'
    risk_assessment_enabled: bool = os.getenv('RISK_ASSESSMENT_ENABLED', 'false').lower() == 'true'
    audit_logging_enabled: bool = os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'

@dataclass
class User:
    """Unified user model"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    tenant_id: str
    is_active: bool = True
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class AuthToken:
    """Authentication token model"""
    token: str
    user_id: str
    expires_at: datetime
    token_type: str = "access"
    session_id: Optional[str] = None

@dataclass
class AuthenticationResult:
    """Authentication result with enterprise features"""
    success: bool
    user_id: Optional[str] = None
    token: Optional[str] = None
    requires_mfa: bool = False
    mfa_methods: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    risk_score: float = 0.0
    session_id: Optional[str] = None

# =============================================================================
# UNIFIED AUTHENTICATION SERVICE
# =============================================================================

class UnifiedAuthenticationService:
    """
    Unified authentication service consolidating all implementations
    Features from all existing auth systems with no duplication
    """
    
    def __init__(self, config: SecurityConfig = None, db_manager=None):
        self.config = config or SecurityConfig()
        self.db_manager = db_manager
        
        # Role-based permissions (FROM: core/auth_service.py)
        self.role_permissions = {
            UserRole.ADMIN: [p for p in Permission],
            UserRole.DEVELOPER: [Permission.READ_USERS, Permission.READ_TRADING, Permission.WRITE_TRADING, 
                                Permission.READ_ANALYTICS, Permission.WRITE_ANALYTICS, Permission.API_ACCESS],
            UserRole.ANALYST: [Permission.READ_TRADING, Permission.READ_ANALYTICS, Permission.WRITE_ANALYTICS],
            UserRole.TRADER: [Permission.READ_TRADING, Permission.WRITE_TRADING, Permission.EXECUTE_TRADES],
            UserRole.VIEWER: [Permission.READ_TRADING, Permission.READ_ANALYTICS]
        }
        
        # Session and security tracking
        self.active_sessions: Dict[str, Dict] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.audit_events: List[Dict[str, Any]] = []
        
        logger.info("🔐 Unified Authentication Service initialized")
    
    # =============================================================================
    # PASSWORD MANAGEMENT (FROM: core/auth_service.py + security_enhancements.py)
    # =============================================================================
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with enterprise-grade settings"""
        # Validate password strength first
        if not self._validate_password_strength(password):
            raise ValueError("Password does not meet security requirements")
        
        # Use cost factor 12 for enterprise security
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < self.config.password_min_length:
            return False
        
        if self.config.password_require_uppercase and not any(c.isupper() for c in password):
            return False
        
        if self.config.password_require_numbers and not any(c.isdigit() for c in password):
            return False
        
        if self.config.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False
        
        # Check against common passwords
        common_passwords = ['password', '123456', 'admin', 'prometheus', 'trading']
        if password.lower() in common_passwords:
            return False
        
        return True
    
    # =============================================================================
    # JWT TOKEN MANAGEMENT (FROM: core/auth_service.py + security/authentication.py)
    # =============================================================================
    
    def generate_token(self, user: User) -> AuthToken:
        """Generate JWT token with enhanced security"""
        now_dt = datetime.now(timezone.utc)
        expires_at = now_dt + timedelta(hours=self.config.jwt_expiration_hours)
        session_id = secrets.token_urlsafe(32)
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'tenant_id': user.tenant_id,
            'session_id': session_id,
            'exp': int(expires_at.timestamp()),
            'iat': int(now_dt.timestamp()),
            'jti': secrets.token_urlsafe(16)  # JWT ID
        }
        
        # Try jose first, fallback to PyJWT
        token = None
        if jose_jwt is not None:
            try:
                token = jose_jwt.encode(payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
            except Exception as e:
                logger.debug(f"jose_jwt.encode failed: {e}")
        
        if token is None:
            try:
                token = jwt.encode(payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm)
            except Exception as e:
                logger.error(f"JWT encoding failed: {e}")
                raise
        
        # Store session
        self.active_sessions[session_id] = {
            'user_id': user.id,
            'created_at': now_dt,
            'expires_at': expires_at,
            'is_active': True
        }
        
        return AuthToken(
            token=token,
            user_id=user.id,
            expires_at=expires_at,
            session_id=session_id
        )
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            # Try PyJWT first
            payload = jwt.decode(token, self.config.jwt_secret_key, algorithms=[self.config.jwt_algorithm])
            
            # Check session validity
            session_id = payload.get('session_id')
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if session['is_active'] and datetime.now(timezone.utc) < session['expires_at']:
                    return payload
            
            return None
            
        except jwt.ExpiredSignatureError:
            logger.debug("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid token: {e}")
            return None
        except Exception as e:
            # Try jose fallback
            if jose_jwt is not None:
                try:
                    payload = jose_jwt.decode(token, self.config.jwt_secret_key, algorithms=[self.config.jwt_algorithm])
                    return payload
                except Exception:
                    pass
            logger.error(f"Token verification failed: {e}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a JWT token by deactivating the session"""
        try:
            payload = self.verify_token(token)
            if payload and payload.get('session_id'):
                session_id = payload['session_id']
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]['is_active'] = False
                    self._log_auth_event(payload['user_id'], "TOKEN_REVOKED", "JWT token revoked")
                    return True
            return False
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    # =============================================================================
    # USER MANAGEMENT (FROM: core/auth_service.py)
    # =============================================================================
    
    def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        role: UserRole,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> User:
        """Create a new user with validation"""
        user_id = secrets.token_urlsafe(16)
        password_hash = self.hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            tenant_id=tenant_id,
            created_at=datetime.now(timezone.utc),
            metadata=metadata or {}
        )
        
        # Store user (would integrate with database)
        if self.db_manager:
            try:
                self.db_manager.execute_query(
                    """INSERT INTO users (id, username, email, password_hash, role, tenant_id, created_at, metadata)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (user.id, user.username, user.email, user.password_hash, 
                     user.role.value, user.tenant_id, user.created_at, json.dumps(user.metadata))
                )
            except Exception as e:
                logger.error(f"Failed to create user in database: {e}")
                raise
        
        self._log_auth_event(user.id, "USER_CREATED", f"User created: {username}")
        return user
    
    def authenticate_user(self, username: str, password: str, request: Optional[Request] = None) -> AuthenticationResult:
        """Authenticate user with enhanced security"""
        # Check rate limiting
        client_ip = self._get_client_ip(request) if request else "unknown"
        if not self._check_rate_limit(f"auth:{client_ip}"):
            return AuthenticationResult(
                success=False,
                error_message="Too many authentication attempts. Please try again later.",
                risk_score=1.0
            )
        
        # Get user (would query database)
        user = self._get_user_by_username(username)
        if not user:
            self._log_auth_event("unknown", "LOGIN_FAILED", f"User not found: {username}")
            return AuthenticationResult(
                success=False,
                error_message="Invalid credentials",
                risk_score=0.8
            )
        
        # Check if account is locked
        if user.locked_until and datetime.now(timezone.utc) < user.locked_until:
            return AuthenticationResult(
                success=False,
                error_message="Account is temporarily locked",
                risk_score=1.0
            )
        
        # Verify password
        if not self.verify_password(password, user.password_hash):
            self._handle_failed_authentication(user)
            return AuthenticationResult(
                success=False,
                error_message="Invalid credentials",
                risk_score=0.9
            )
        
        # Check if MFA is required
        mfa_required = (
            user.mfa_enabled or 
            (self.config.mfa_required_for_admin and user.role == UserRole.ADMIN) or
            self.config.enterprise_mode
        )
        
        if mfa_required and not user.mfa_secret:
            return AuthenticationResult(
                success=False,
                requires_mfa=True,
                mfa_methods=["setup_required"],
                error_message="MFA setup required",
                user_id=user.id
            )
        
        # Reset failed attempts on successful authentication
        user.failed_attempts = 0
        user.locked_until = None
        user.last_login = datetime.now(timezone.utc)
        
        # Generate token
        auth_token = self.generate_token(user)
        
        self._log_auth_event(user.id, "LOGIN_SUCCESS", f"User authenticated: {username}")
        
        return AuthenticationResult(
            success=True,
            user_id=user.id,
            token=auth_token.token,
            session_id=auth_token.session_id,
            requires_mfa=mfa_required and user.mfa_secret is not None
        )
    
    # =============================================================================
    # MFA MANAGEMENT (FROM: enterprise/security/enterprise_auth.py)
    # =============================================================================
    
    def setup_mfa(self, user_id: str) -> Dict[str, Any]:
        """Setup MFA for user"""
        secret = pyotp.random_base32()
        
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_id,
            issuer_name=self.config.mfa_issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        return {
            'secret': secret,
            'qr_code': qr_code_base64,
            'backup_codes': backup_codes,
            'totp_uri': totp_uri
        }
    
    def verify_mfa_token(self, user_id: str, token: str) -> bool:
        """Verify MFA token"""
        user = self._get_user_by_id(user_id)
        if not user or not user.mfa_secret:
            return False
        
        totp = pyotp.TOTP(user.mfa_secret)
        return totp.verify(token, valid_window=1)  # Allow 30-second window
    
    # =============================================================================
    # API KEY MANAGEMENT (FROM: core/auth_service.py)
    # =============================================================================
    
    def create_api_key(
        self, 
        user: User, 
        name: str, 
        permissions: List[Permission] = None,
        expires_at: datetime = None
    ) -> str:
        """Create an API key for a user"""
        api_key = f"prometheus_{secrets.token_urlsafe(32)}"
        key_hash = self.hash_password(api_key)
        key_id = secrets.token_urlsafe(16)
        
        # Default to user's permissions if not specified
        if permissions is None:
            permissions = self.get_user_permissions(user)
        
        # Store API key (would integrate with database)
        self._log_auth_event(user.id, "API_KEY_CREATED", f"API key created: {name}")
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify an API key and return user info"""
        # This would query the database for active API keys
        # For now, return None (not implemented in database layer)
        return None
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def get_user_permissions(self, user: User) -> List[Permission]:
        """Get permissions for a user based on their role"""
        return self.role_permissions.get(user.role, [])
    
    def _get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (would query database)"""
        # This would integrate with the database
        return None
    
    def _get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID (would query database)"""
        # This would integrate with the database
        return None
    
    def _handle_failed_authentication(self, user: User):
        """Handle failed authentication attempt"""
        user.failed_attempts += 1
        
        if user.failed_attempts >= self.config.max_login_attempts:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=self.config.lockout_duration_minutes)
            self._log_auth_event(user.id, "ACCOUNT_LOCKED", f"Account locked after {user.failed_attempts} failed attempts")
    
    def _check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now(timezone.utc)
        
        # Clean old attempts
        if identifier in self.failed_attempts:
            self.failed_attempts[identifier] = [
                attempt for attempt in self.failed_attempts[identifier]
                if now - attempt < timedelta(minutes=1)
            ]
        
        # Check current rate
        current_attempts = len(self.failed_attempts.get(identifier, []))
        
        if current_attempts >= 10:  # 10 attempts per minute
            return False
        
        # Record attempt
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = []
        self.failed_attempts[identifier].append(now)
        
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else 'unknown'
    
    def _log_auth_event(self, user_id: str, event_type: str, details: str):
        """Log authentication event for audit trail"""
        if self.config.audit_logging_enabled:
            event = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'user_id': user_id,
                'event_type': event_type,
                'details': details
            }
            self.audit_events.append(event)
            logger.info(f"🔐 Auth Event: {event_type} - {details}")

# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Global unified authentication service instance
unified_auth = UnifiedAuthenticationService()
