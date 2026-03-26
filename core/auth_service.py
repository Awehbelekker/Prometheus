"""
Authentication Service for MASS Framework
Handles JWT-based authentication, user management, and security
"""

import jwt
try:
    # Prefer python-jose for encoding to avoid environment-specific PyJWT TypeErrors
    from jose import jwt as jose_jwt  # type: ignore
except Exception:
    jose_jwt = None  # type: ignore
import bcrypt
import secrets
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
import os
import traceback
from core.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class UserRole(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    ANALYST = "analyst"
    TRADER = "trader"
    VIEWER = "viewer"

class Permission(Enum):
    # AI Agent Permissions
    USE_AI_AGENTS = "use_ai_agents"
    MANAGE_AI_AGENTS = "manage_ai_agents"
    
    # Collaboration Permissions
    CREATE_COLLABORATIONS = "create_collaborations"
    MANAGE_COLLABORATIONS = "manage_collaborations"
    VIEW_COLLABORATIONS = "view_collaborations"
    
    # Project Permissions
    ANALYZE_PROJECTS = "analyze_projects"
    MANAGE_PROJECTS = "manage_projects"
    VIEW_PROJECTS = "view_projects"
    
    # System Permissions
    ADMIN_SYSTEM = "admin_system"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_USERS = "manage_users"
    
    # API Permissions
    API_ACCESS = "api_access"
    ADMIN_API = "admin_api"
    # Trading Advanced (sensitive capabilities)
    QUANTUM_TRADING = "quantum_trading"
    AI_CONSCIOUSNESS_ACCESS = "ai_consciousness_access"

@dataclass
class User:
    """User model"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    tenant_id: str
    is_active: bool = True
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
    
@dataclass
class LoginCredentials:
    """Login credentials model"""
    username: str
    password: str
    tenant_id: Optional[str] = None

class AuthenticationService:
    """JWT-based authentication service"""
    
    def __init__(self, secret_key: Optional[str] = None, token_expiry_hours: int = 24, db_manager: Optional[DatabaseManager] = None):
        # Always coerce secret to str to satisfy PyJWT key handling
        env_secret = os.getenv("JWT_SECRET_KEY")
        derived_secret = secret_key if isinstance(secret_key, (str, bytes)) else env_secret
        if not derived_secret:
            derived_secret = secrets.token_urlsafe(32)
        # If bytes provided, decode to utf-8; else cast to str
        if isinstance(derived_secret, (bytes, bytearray)):
            try:
                self.secret_key = derived_secret.decode("utf-8")
            except Exception:
                # last resort: use repr
                self.secret_key = str(derived_secret)
        else:
            self.secret_key = str(derived_secret)
        self.token_expiry_hours = token_expiry_hours
        self.algorithm = "HS256"
        self.db_manager = db_manager or DatabaseManager()
        self.role_permissions = self._define_role_permissions()
        # Help diagnose which JWT implementation is active in this environment
        try:
            logger.info(
                f"JWT module in use: path={getattr(jwt, '__file__', 'unknown')}, version={getattr(jwt, '__version__', 'n/a')}"
            )
        except Exception:
            pass
        
        # Initialize database tables
        self._init_auth_tables()
    
    def _define_role_permissions(self) -> Dict[UserRole, List[Permission]]:
        """Define permissions for each role"""
        return {
            UserRole.ADMIN: [
                Permission.USE_AI_AGENTS,
                Permission.MANAGE_AI_AGENTS,
                Permission.CREATE_COLLABORATIONS,
                Permission.MANAGE_COLLABORATIONS,
                Permission.VIEW_COLLABORATIONS,
                Permission.ANALYZE_PROJECTS,
                Permission.MANAGE_PROJECTS,
                Permission.VIEW_PROJECTS,
                Permission.ADMIN_SYSTEM,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_USERS,
                Permission.API_ACCESS,
                Permission.ADMIN_API,
                Permission.QUANTUM_TRADING,
                Permission.AI_CONSCIOUSNESS_ACCESS
            ],
            UserRole.DEVELOPER: [
                Permission.USE_AI_AGENTS,
                Permission.CREATE_COLLABORATIONS,
                Permission.VIEW_COLLABORATIONS,
                Permission.ANALYZE_PROJECTS,
                Permission.VIEW_PROJECTS,
                Permission.API_ACCESS,
                Permission.QUANTUM_TRADING
            ],
            UserRole.ANALYST: [
                Permission.USE_AI_AGENTS,
                Permission.VIEW_COLLABORATIONS,
                Permission.ANALYZE_PROJECTS,
                Permission.VIEW_PROJECTS,
                Permission.VIEW_ANALYTICS,
                Permission.API_ACCESS
            ],
            UserRole.TRADER: [
                Permission.USE_AI_AGENTS,
                Permission.VIEW_COLLABORATIONS,
                Permission.ANALYZE_PROJECTS,
                Permission.VIEW_PROJECTS,
                Permission.API_ACCESS,
                Permission.QUANTUM_TRADING
            ],
            UserRole.VIEWER: [
                Permission.VIEW_COLLABORATIONS,
                Permission.VIEW_PROJECTS,
                Permission.API_ACCESS
            ]
        }
    
    def _init_auth_tables(self):
        """Initialize authentication database tables"""
        try:
            # Users table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    tenant_id TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Sessions table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # API Keys table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    permissions TEXT,
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Audit log table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS auth_audit_log (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Broker Credentials table
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS broker_credentials (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    broker TEXT NOT NULL,
                    api_key TEXT NOT NULL,
                    api_secret TEXT NOT NULL,
                    account_name TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            logger.info("Authentication tables initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize auth tables: {str(e)}")
            raise
    
    def hash_password(self, password: str | bytes) -> str:
        """Hash a password using bcrypt; always return str."""
        salt = bcrypt.gensalt()
        pwd_bytes = password if isinstance(password, (bytes, bytearray)) else str(password).encode('utf-8')
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        return hashed.decode('utf-8') if isinstance(hashed, (bytes, bytearray)) else str(hashed)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification failed: {str(e)}")
            return False
    
    def create_user(
        self, 
        username: str, 
        email: str, 
        password: str, 
        role: UserRole,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> User:
        print(f"DEBUG: create_user received metadata: {metadata} (type: {type(metadata)})")
        import traceback
        traceback.print_stack()
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
        try:
            # Always serialize metadata to JSON string for DB
            metadata_json = json.dumps(user.metadata or {})
            print(f"DEBUG: Final metadata_json before insert: {metadata_json} (type: {type(metadata_json)})")
            created_at_str = user.created_at.isoformat()
            print(f"DEBUG: INSERT PARAMS: id={user.id}, username={user.username}, email={user.email}, password_hash={user.password_hash}, role={user.role.value}, tenant_id={user.tenant_id}, created_at={created_at_str}, metadata_json={metadata_json} (type: {type(metadata_json)})")
            self.db_manager.execute_query(
                """INSERT INTO users 
                   (id, username, email, password_hash, role, tenant_id, created_at, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (user.id, user.username, user.email, user.password_hash, 
                 user.role.value, user.tenant_id, created_at_str, metadata_json)
            )
            self._log_auth_event(user.id, "USER_CREATED", f"User {username} created")
            logger.info(f"User created successfully: {username}")
            return user
        except Exception as e:
            import traceback
            print(f"[DEBUG] create_user exception: {e}")
            print(f"[DEBUG] create_user params: id={user.id}, username={user.username}, email={user.email}, password_hash={user.password_hash}, role={user.role.value}, tenant_id={user.tenant_id}, created_at={user.created_at}, metadata_json={metadata_json}")
            traceback.print_exc()
            logger.error(f"Failed to create user {username}: {str(e)}")
            raise
    
    def authenticate_user(self, credentials: LoginCredentials) -> Optional[User]:
        """Authenticate user with username/password (accepts username or email)"""
        import sys
        print(f"[DEBUG] authenticate_user called. id(self)={id(self)} db_manager={self.db_manager}", file=sys.stderr)
        print(f"[DEBUG] authenticate_user: credentials={credentials}", file=sys.stderr)
        try:
            # Query user from database - check both username and email
            result = self.db_manager.fetch_one(
                "SELECT * FROM users WHERE (username = ? OR email = ?) AND is_active = 1",
                (credentials.username, credentials.username)
            )
            print(f"[DEBUG] authenticate_user: DB result for username={credentials.username}: {result}", file=sys.stderr)
            if not result:
                self._log_auth_event(None, "LOGIN_FAILED", f"User not found: {credentials.username}")
                return None
              # Convert result to User object
            user = User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                password_hash=result['password_hash'],
                role=UserRole(result['role']),
                tenant_id=result['tenant_id'],
                is_active=bool(result['is_active']),
                created_at=result['created_at'],
                last_login=result['last_login'],
                metadata=json.loads(result['metadata']) if result['metadata'] else {}
            )
            print(f"[DEBUG] authenticate_user: User object created: {user}", file=sys.stderr)
            # Verify password
            if not self.verify_password(credentials.password, user.password_hash):
                self._log_auth_event(user.id, "LOGIN_FAILED", "Invalid password")
                print(f"[DEBUG] authenticate_user: Invalid password for user {user.username}", file=sys.stderr)
                return None
            
            # Check tenant if specified
            if credentials.tenant_id and user.tenant_id != credentials.tenant_id:
                self._log_auth_event(user.id, "LOGIN_FAILED", "Invalid tenant")
                print(f"[DEBUG] authenticate_user: Invalid tenant for user {user.username}", file=sys.stderr)
                return None
            
            print(f"[DEBUG] authenticate_user: Authentication successful for user {user.username}", file=sys.stderr)
            return user
        except Exception as e:
            print(f"[DEBUG] authenticate_user: Exception: {e}\n{traceback.format_exc()}", file=sys.stderr)
            logger.error(f"Failed to authenticate user {credentials.username}: {str(e)}")
            raise
    
    def generate_token(self, user: User) -> AuthToken:
        """Generate JWT token for authenticated user"""
        now_dt = datetime.now(timezone.utc)
        expires_at = now_dt + timedelta(hours=self.token_expiry_hours)
        # Use epoch seconds for JWT standard compliance and portability
        exp_epoch = int(expires_at.timestamp())
        iat_epoch = int(now_dt.timestamp())

        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'tenant_id': user.tenant_id,
            'exp': exp_epoch,
            'iat': iat_epoch,
            'jti': secrets.token_urlsafe(16)  # JWT ID
        }

        # Defensive: ensure secret key is a plain string to avoid TypeError from PyJWT
        key_for_jwt = self.secret_key
        # Prefer python-jose path first; fall back to PyJWT with rich diagnostics
        token = None  # type: ignore
        if jose_jwt is not None:
            try:
                if not isinstance(key_for_jwt, (str, bytes, bytearray)):
                    key_for_jwt = str(key_for_jwt)
                # jose expects str key; ensure string
                token = jose_jwt.encode(payload, str(key_for_jwt), algorithm=str(self.algorithm))
            except Exception as je:
                print(f"[DEBUG] jose_jwt.encode failed: {je}", flush=True)
        if token is None:
            try:
                if not isinstance(key_for_jwt, (str, bytes, bytearray)):
                    key_for_jwt = str(key_for_jwt)
                token = jwt.encode(payload, key_for_jwt, algorithm=str(self.algorithm))
            except TypeError as te:
                # Provide rich diagnostics to locate non-string culprit
                dbg = {
                    'error': str(te),
                    'secret_type': str(type(self.secret_key)),
                    'algorithm_type': str(type(self.algorithm)),
                    'payload_types': {k: str(type(v)) for k, v in payload.items()},
                    'jwt_module': getattr(jwt, '__file__', 'unknown'),
                }
                print(f"[DEBUG] jwt.encode TypeError (pyjwt): {dbg}", flush=True)
                # Retry coercing key to str explicitly
                try:
                    token = jwt.encode(payload, str(self.secret_key), algorithm=str(self.algorithm))
                except Exception as te2:
                    print(f"[DEBUG] jwt.encode retry failed (pyjwt): {te2}", flush=True)
                    if jose_jwt is not None:
                        try:
                            print("[DEBUG] Falling back to python-jose for JWT encode", flush=True)
                            token = jose_jwt.encode(payload, str(self.secret_key), algorithm=str(self.algorithm))
                        except Exception as je:
                            print(f"[DEBUG] python-jose encode failed: {je}", flush=True)
                            raise te2
                    else:
                        raise te2
            except Exception as e:
                print(f"[DEBUG] jwt.encode error (non-TypeError): {e}", flush=True)
                if jose_jwt is not None:
                    try:
                        print("[DEBUG] Using python-jose for JWT encode due to unexpected error", flush=True)
                        token = jose_jwt.encode(payload, str(self.secret_key), algorithm=str(self.algorithm))
                    except Exception as je:
                        print(f"[DEBUG] python-jose encode also failed: {je}", flush=True)
                        raise
        # PyJWT <2 returns bytes; normalize to str
        if isinstance(token, (bytes, bytearray)):
            token = token.decode('utf-8')

        # Store session in database (persist ISO string to avoid driver datetime binding issues)
        session_id = str(secrets.token_urlsafe(16))
        token_hash = str(self.hash_password(token))
        # Persist as ISO string; prefer naive UTC to avoid driver timezone binding issues
        try:
            expires_at_iso = expires_at.replace(tzinfo=None).isoformat()
        except Exception:
            expires_at_iso = expires_at.isoformat()
        # Debug trace for parameter types
        try:
            print(f"DEBUG generate_token: session_id={session_id} ({type(session_id)}), user_id={user.id} ({type(user.id)}), token_hash={type(token_hash)}, expires_at_iso={expires_at_iso} ({type(expires_at_iso)})", flush=True)
        except Exception:
            pass
        # Insert session; ensure all params are strings to placate sqlite binding
        try:
            sid = str(session_id)
            uid = str(user.id)
            thash = str(token_hash)
            eiso = str(expires_at_iso)
            print(f"DEBUG generate_token insert params types: {[type(x) for x in [sid, uid, thash, eiso]]}")
            self.db_manager.execute_query(
                """INSERT INTO user_sessions (id, user_id, token_hash, expires_at)
                   VALUES (?, ?, ?, ?)""",
                (sid, uid, thash, eiso)
            )
        except Exception as ie:
            import traceback
            print(f"[DEBUG] user_sessions insert failed: {ie}\n{traceback.format_exc()}")
            raise

        auth_token = AuthToken(
            token=token,
            user_id=user.id,
            expires_at=expires_at
        )

        self._log_auth_event(user.id, "TOKEN_GENERATED", "JWT token generated")
        return auth_token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            # Try PyJWT first
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check if session exists and is active. We store expires_at as ISO string.
            # Compare naive UTC ISO string to match storage format
            now_iso = datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
            session = self.db_manager.fetch_one(
                """SELECT * FROM user_sessions 
                   WHERE user_id = ? AND expires_at > ? AND is_active = 1""",
                (payload['user_id'], now_iso)
            )
            
            if not session:
                self._log_auth_event(payload.get('user_id'), "TOKEN_INVALID", "Session not found or expired")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self._log_auth_event(None, "TOKEN_EXPIRED", "JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            # Attempt decode via python-jose if available
            try:
                if jose_jwt is not None:
                    payload = jose_jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                else:
                    raise e
            except Exception:
                self._log_auth_event(None, "TOKEN_INVALID", f"Invalid JWT token: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a JWT token by deactivating the session"""
        try:
            # Try PyJWT first; fall back to jose
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Deactivate session
            self.db_manager.execute_query(
                "UPDATE user_sessions SET is_active = 0 WHERE user_id = ?",
                (payload['user_id'],)
            )
            
            self._log_auth_event(payload['user_id'], "TOKEN_REVOKED", "JWT token revoked")
            return True
            
        except Exception as e:
            # Fallback: try decoding with jose then proceed to revoke
            try:
                if jose_jwt is not None:
                    payload = jose_jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
                    self.db_manager.execute_query(
                        "UPDATE user_sessions SET is_active = 0 WHERE user_id = ?",
                        (payload['user_id'],)
                    )
                    self._log_auth_event(payload['user_id'], "TOKEN_REVOKED", "JWT token revoked (jose)")
                    return True
            except Exception:
                pass
            logger.error(f"Token revocation failed: {str(e)}")
            return False
    
    def get_user_permissions(self, user: User) -> List[Permission]:
        """Get permissions for a user based on their role"""
        return self.role_permissions.get(user.role, [])
    
    def has_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has a specific permission"""
        user_permissions = self.get_user_permissions(user)
        return permission in user_permissions
    
    def require_permission(self, user: User, permission: Permission) -> bool:
        """Require user to have a specific permission, raise exception if not"""
        if not self.has_permission(user, permission):
            self._log_auth_event(user.id, "PERMISSION_DENIED", f"Permission denied: {permission.value}")
            raise PermissionError(f"User does not have permission: {permission.value}")
        return True
    
    def create_api_key(
        self, 
        user: User, 
        name: str, 
        permissions: List[Permission] = None,
        expires_at: datetime = None
    ) -> str:
        """Create an API key for a user"""
        api_key = f"mass_{secrets.token_urlsafe(32)}"
        key_hash = self.hash_password(api_key)
        key_id = secrets.token_urlsafe(16)
        
        # Default to user's permissions if not specified
        if permissions is None:
            permissions = self.get_user_permissions(user)
        
        try:
            self.db_manager.execute_query(
                """INSERT INTO api_keys (id, user_id, key_hash, name, permissions, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (key_id, user.id, key_hash, name, 
                 ','.join([p.value for p in permissions]), expires_at)
            )
            
            self._log_auth_event(user.id, "API_KEY_CREATED", f"API key created: {name}")
            return api_key
            
        except Exception as e:
            logger.error(f"Failed to create API key: {str(e)}")
            raise
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Verify an API key and return user info"""
        try:
            # Find all active API keys
            results = self.db_manager.fetch_all(
                """SELECT ak.*, u.username, u.role, u.tenant_id 
                   FROM api_keys ak
                   JOIN users u ON ak.user_id = u.id
                   WHERE ak.is_active = 1 
                   AND (ak.expires_at IS NULL OR ak.expires_at > ?)""",
                (datetime.now(timezone.utc),)
            )
            if not results:
                return None
            for result in results:
                key_hash = result['key_hash']
                if self.verify_password(api_key, key_hash):
                    return {
                        'user_id': result['user_id'],
                        'username': result['username'],
                        'role': result['role'],
                        'tenant_id': result['tenant_id'],
                        'permissions': result['permissions'].split(',') if result['permissions'] else [],
                        'api_key_name': result['name']
                    }
            return None
        except Exception as e:
            logger.error(f"API key verification failed: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            result = self.db_manager.fetch_one(
                "SELECT * FROM users WHERE id = ? AND is_active = 1",
                (user_id,)
            )
            
            if not result:
                return None
            
            # Parse created_at and last_login as datetime if needed
            created_at = result['created_at']
            if isinstance(created_at, str):
                from datetime import datetime
                created_at = datetime.fromisoformat(created_at)
            last_login = result['last_login']
            if last_login and isinstance(last_login, str):
                from datetime import datetime
                last_login = datetime.fromisoformat(last_login)
            
            return User(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                password_hash=result['password_hash'],
                role=UserRole(result['role']),
                tenant_id=result['tenant_id'],
                is_active=bool(result['is_active']),
                created_at=created_at,
                last_login=last_login,
                metadata=json.loads(result['metadata']) if result['metadata'] else {}
            )
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {str(e)}")
            return None
    
    def update_user_role(self, user_id: str, new_role: UserRole, admin_user: User) -> bool:
        """Update user role (admin only)"""
        try:
            # Check admin permissions
            self.require_permission(admin_user, Permission.MANAGE_USERS)
            
            self.db_manager.execute_query(
                "UPDATE users SET role = ? WHERE id = ?",
                (new_role.value, user_id)
            )
            
            self._log_auth_event(
                admin_user.id, 
                "USER_ROLE_UPDATED", 
                f"User {user_id} role updated to {new_role.value}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update user role: {str(e)}")
            return False
    
    def deactivate_user(self, user_id: str, admin_user: User) -> bool:
        """Deactivate a user account (admin only)"""
        try:
            # Check admin permissions
            self.require_permission(admin_user, Permission.MANAGE_USERS)
            
            # Deactivate user
            self.db_manager.execute_query(
                "UPDATE users SET is_active = 0 WHERE id = ?",
                (user_id,)
            )
            
            # Deactivate all sessions
            self.db_manager.execute_query(
                "UPDATE user_sessions SET is_active = 0 WHERE user_id = ?",
                (user_id,)
            )
            
            # Deactivate all API keys
            self.db_manager.execute_query(
                "UPDATE api_keys SET is_active = 0 WHERE user_id = ?",
                (user_id,)
            )
            
            # Deactivate all broker credentials
            self.db_manager.execute_query(
                "UPDATE broker_credentials SET status = 'inactive' WHERE user_id = ?",
                (user_id,)
            )
            
            self._log_auth_event(admin_user.id, "USER_DEACTIVATED", f"User {user_id} deactivated")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate user: {str(e)}")
            return False
    
    def get_auth_stats(self, admin_user: User) -> Dict[str, Any]:
        """Get authentication statistics (admin only)"""
        try:
            print(f"[DEBUG] get_auth_stats: id(self)={id(self)} id(self.db_manager)={id(self.db_manager)} id(self.db_manager._external_connection)={id(self.db_manager._external_connection) if hasattr(self.db_manager, '_external_connection') else None}", flush=True)
            self.require_permission(admin_user, Permission.VIEW_ANALYTICS)
            # Get user counts by role
            role_counts = {}
            for role in UserRole:
                count_row = self.db_manager.fetch_one(
                    "SELECT COUNT(*) FROM users WHERE role = ? AND is_active = 1",
                    (role.value,)
                )
                count = count_row[0] if count_row else 0
                role_counts[role.value] = count
            # Get active sessions count
            session_row = self.db_manager.fetch_one(
                "SELECT COUNT(*) FROM user_sessions WHERE expires_at > ? AND is_active = 1",
                (datetime.now(timezone.utc),)
            )
            active_sessions = session_row[0] if session_row else 0
            # Get recent login activity
            recent_logins = self.db_manager.fetch_all(
                """SELECT action, COUNT(*) as count 
                   FROM auth_audit_log 
                   WHERE action IN ('LOGIN_SUCCESS', 'LOGIN_FAILED') 
                   AND timestamp > ? 
                   GROUP BY action""",
                (datetime.now(timezone.utc) - timedelta(days=7),)
            )
            recent_activity = {row[0]: row[1] for row in recent_logins} if recent_logins else {}
            return {
                'role_counts': role_counts,
                'active_sessions': active_sessions,
                'recent_activity': recent_activity,
                'total_users': sum(role_counts.values())
            }
        except Exception as e:
            logger.error(f"Failed to get auth stats: {str(e)}")
            return {                'role_counts': {},
                'active_sessions': 0,
                'recent_activity': {},
                'total_users': 0
            }
    
    def _log_auth_event(
        self, 
        user_id: Optional[str], 
        action: str, 
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True
    ):
        """Log authentication events for audit purposes"""
        try:
            event_id = secrets.token_urlsafe(16)
            
            self.db_manager.execute_query(
                """INSERT INTO auth_audit_log 
                   (id, user_id, action, details, ip_address, user_agent, success)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (event_id, user_id, action, details, ip_address, user_agent, success)
            )
            
        except Exception as e:
            logger.error(f"Failed to log auth event: {str(e)}")

# Global authentication service instance
# Allow resetting for test isolation
def set_global_auth_service(new_auth_service: AuthenticationService) -> None:
    global auth_service
    auth_service = new_auth_service

# Default instance
auth_service = AuthenticationService()

# Helper functions for common operations
def create_default_admin(auth_service_instance: Optional[AuthenticationService] = None) -> Optional[User]:
    print(f"DEBUG: create_default_admin called with auth_service_instance: {auth_service_instance}")
    """Create default admin user if none exists"""
    auth_service_to_use = auth_service_instance or auth_service
    try:
        # Check if any admin users exist
        result = auth_service_to_use.db_manager.fetch_one(
            "SELECT COUNT(*) as admin_count FROM users WHERE role = 'admin' AND is_active = 1"
        )
        print(f"DEBUG: create_default_admin admin_count result: {result}")
        if result and result.get('admin_count', 0) == 0:
            # Create default admin
            admin_metadata = {"created_by": "system", "is_default": True}
            print(f"DEBUG: create_default_admin metadata: {admin_metadata} (type: {type(admin_metadata)})")
            admin_user = auth_service_to_use.create_user(
                username="admin",
                email="admin@mass-framework.com",
                password = os.getenv("ADMIN_PASSWORD"),  # Should be changed immediately
                role=UserRole.ADMIN,
                tenant_id="default",
                metadata=admin_metadata
            )
            logger.info("Default admin user created successfully")
            logger.warning("Default admin password is 'admin123' - CHANGE IMMEDIATELY!")
            return admin_user
        else:
            logger.info("Admin users already exist, skipping default creation")
            return None
    except Exception as e:
        import traceback
        print(f"[DEBUG] create_default_admin exception: {e}")
        traceback.print_exc()
        logger.error(f"Failed to create default admin: {str(e)}")
        return None

def login(username: str, password: str, tenant_id: Optional[str] = None) -> Optional[AuthToken]:
    """Convenience function for user login"""
    credentials = LoginCredentials(username=username, password=password, tenant_id=tenant_id)
    user = auth_service.authenticate_user(credentials)
    
    if user:
        return auth_service.generate_token(user)
    return None

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Convenience function for token verification"""
    return auth_service.verify_token(token)
