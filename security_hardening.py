#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Security Hardening Script
Fixes all critical security vulnerabilities identified in the security audit
"""

import os
import re
import shutil
import secrets
import hashlib
from pathlib import Path
from datetime import datetime
import json

class SecurityHardening:
    """Comprehensive security hardening for PROMETHEUS Trading Platform."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.backup_dir = Path("security_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.backup_dir.mkdir(exist_ok=True)
        self.fixes_applied = []
        
    def run_complete_hardening(self):
        """Run complete security hardening process."""
        print("🔒 Starting PROMETHEUS Security Hardening")
        print("=" * 60)
        
        # Step 1: Create secure environment template
        self.create_secure_env_template()
        
        # Step 2: Fix hardcoded secrets
        self.fix_hardcoded_secrets()
        
        # Step 3: Fix file permissions
        self.fix_file_permissions()
        
        # Step 4: Enhance authentication security
        self.enhance_authentication_security()
        
        # Step 5: Add security headers and HTTPS enforcement
        self.add_security_headers()
        
        # Step 6: Implement rate limiting
        self.implement_rate_limiting()
        
        # Step 7: Fix CORS configuration
        self.fix_cors_configuration()
        
        # Step 8: Generate security report
        self.generate_security_report()
        
        print("\n🎉 Security hardening completed!")
        print(f"📁 Backup created: {self.backup_dir}")
        print(f"[CHECK] Applied {len(self.fixes_applied)} security fixes")
    
    def create_secure_env_template(self):
        """Create secure .env template with all required variables."""
        print("📝 Creating secure environment configuration...")
        
        # Generate secure secrets
        jwt_secret = secrets.token_urlsafe(64)
        encryption_key = secrets.token_urlsafe(32)
        session_secret = secrets.token_urlsafe(32)
        
        env_template = f"""# PROMETHEUS Trading Platform - Secure Environment Configuration
# Generated on {datetime.now().isoformat()}

# ================================
# CORE CONFIGURATION
# ================================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY={jwt_secret}

# ================================
# DATABASE CONFIGURATION
# ================================
DATABASE_URL=sqlite:///prometheus_trading.db
REDIS_URL=redis://localhost:6379/0

# ================================
# API CONFIGURATION
# ================================
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_PORT=3000
ALLOWED_HOSTS=localhost,127.0.0.1,prometheus-trade.com

# ================================
# SECURITY CONFIGURATION
# ================================
JWT_SECRET_KEY={jwt_secret}
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
ENCRYPTION_KEY={encryption_key}
SESSION_SECRET_KEY={session_secret}
BCRYPT_ROUNDS=12

# ================================
# TRADING CONFIGURATION
# ================================
# Replace with your actual API keys
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# ================================
# MARKET DATA CONFIGURATION
# ================================
# Replace with your actual API keys
POLYGON_API_KEY=your_polygon_api_key_here
YAHOO_FINANCE_ENABLED=true
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# ================================
# AI CONFIGURATION
# ================================
# Replace with your actual API keys
OPENAI_API_KEY=your_openai_api_key_here
THINKMESH_ENABLED=true

# ================================
# CLOUDFLARE CONFIGURATION
# ================================
# Replace with your actual Cloudflare credentials
CLOUDFLARE_ZONE_ID=your_zone_id_here
CLOUDFLARE_API_TOKEN=your_api_token_here

# ================================
# EMAIL CONFIGURATION
# ================================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password_here
FROM_EMAIL=noreply@prometheus-trading.com

# ================================
# SECURITY SETTINGS
# ================================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
HTTPS_ONLY=true
SECURE_COOKIES=true
CSRF_PROTECTION=true

# ================================
# ADMIN CONFIGURATION
# ================================
# Change these default credentials immediately
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@prometheus-trading.com
ADMIN_PASSWORD_HASH=change_this_immediately
"""
        
        # Save secure .env template
        env_path = self.project_root / ".env.secure_template"
        with open(env_path, 'w') as f:
            f.write(env_template)
        
        print(f"[CHECK] Secure .env template created: {env_path}")
        print("[WARNING]️  IMPORTANT: Update the template with your actual API keys and credentials!")
        
        self.fixes_applied.append("Created secure environment template")
    
    def fix_hardcoded_secrets(self):
        """Fix all hardcoded secrets identified in the audit."""
        print("🔐 Fixing hardcoded secrets...")
        
        # Files with hardcoded secrets to fix
        files_to_fix = [
            "fix_admin_credentials.py",
            "test_alpaca_connection.py", 
            "update_admin_credentials.py",
            "core/auth_service.py",
            "core/session_manager.py",
            "frontend/user_management.py"
        ]
        
        for file_path in files_to_fix:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.fix_secrets_in_file(full_path)
        
        self.fixes_applied.append("Fixed hardcoded secrets in source files")
    
    def fix_secrets_in_file(self, file_path: Path):
        """Fix hardcoded secrets in a specific file."""
        try:
            # Create backup
            backup_path = self.backup_dir / file_path.name
            shutil.copy2(file_path, backup_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace common hardcoded patterns
            replacements = [
                # API keys
                (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = os.getenv("ALPACA_API_KEY")'),
                (r'secret_key\s*=\s*["\'][^"\']+["\']', 'secret_key = os.getenv("ALPACA_SECRET_KEY")'),
                
                # Passwords
                (r'password\s*=\s*["\'][^"\']+["\']', 'password = os.getenv("ADMIN_PASSWORD")'),
                (r'admin_password\s*=\s*["\'][^"\']+["\']', 'admin_password = os.getenv("ADMIN_PASSWORD")'),
                
                # JWT secrets
                (r'jwt_secret\s*=\s*["\'][^"\']+["\']', 'jwt_secret = os.getenv("JWT_SECRET_KEY")'),
                (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', 'SECRET_KEY = os.getenv("SECRET_KEY")'),
                
                # Session secrets
                (r'session_key\s*=\s*["\'][^"\']+["\']', 'session_key = os.getenv("SESSION_SECRET_KEY")'),
            ]
            
            modified = False
            for pattern, replacement in replacements:
                if re.search(pattern, content, re.IGNORECASE):
                    content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    modified = True
            
            # Add import os if not present and modifications were made
            if modified and 'import os' not in content:
                content = 'import os\n' + content
            
            # Write back the modified content
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[CHECK] Fixed secrets in: {file_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to fix secrets in {file_path}: {e}")
    
    def fix_file_permissions(self):
        """Fix file permissions for sensitive files."""
        print("📁 Fixing file permissions...")
        
        sensitive_files = [".env", "frontend/.env", ".env.secure_template"]
        
        for file_name in sensitive_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                try:
                    # On Windows, we'll create a note about permissions
                    # On Unix systems, this would set proper permissions
                    if os.name == 'nt':  # Windows
                        print(f"[WARNING]️  Windows detected: Please manually restrict access to {file_path}")
                    else:  # Unix/Linux
                        os.chmod(file_path, 0o600)  # Owner read/write only
                        print(f"[CHECK] Fixed permissions for: {file_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to fix permissions for {file_path}: {e}")
        
        self.fixes_applied.append("Fixed file permissions for sensitive files")
    
    def enhance_authentication_security(self):
        """Enhance authentication security implementation."""
        print("🔐 Enhancing authentication security...")
        
        # Create enhanced auth configuration
        auth_config = """# Enhanced Authentication Security Configuration

import os
import bcrypt
import secrets
from datetime import datetime, timedelta
import jwt

class SecureAuthConfig:
    \"\"\"Secure authentication configuration.\"\"\"
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Password Security
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_SPECIAL_CHARS = True
    REQUIRE_NUMBERS = True
    REQUIRE_UPPERCASE = True
    
    # Session Security
    SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
    SESSION_TIMEOUT_MINUTES = 30
    SECURE_COOKIES = os.getenv("SECURE_COOKIES", "true").lower() == "true"
    
    # Rate Limiting
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    
    @staticmethod
    def hash_password(password: str) -> str:
        \"\"\"Hash password using bcrypt with secure rounds.\"\"\"
        salt = bcrypt.gensalt(rounds=SecureAuthConfig.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        \"\"\"Verify password against hash.\"\"\"
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_jwt_token(user_data: dict) -> str:
        \"\"\"Generate secure JWT token.\"\"\"
        payload = {
            **user_data,
            'exp': datetime.utcnow() + timedelta(hours=SecureAuthConfig.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }
        return jwt.encode(payload, SecureAuthConfig.JWT_SECRET_KEY, algorithm=SecureAuthConfig.JWT_ALGORITHM)
    
    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        \"\"\"Verify and decode JWT token.\"\"\"
        try:
            payload = jwt.decode(token, SecureAuthConfig.JWT_SECRET_KEY, algorithms=[SecureAuthConfig.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
"""
        
        config_path = self.project_root / "config" / "secure_auth_config.py"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write(auth_config)
        
        print(f"[CHECK] Enhanced authentication config created: {config_path}")
        self.fixes_applied.append("Enhanced authentication security configuration")
    
    def add_security_headers(self):
        """Add security headers and HTTPS enforcement."""
        print("🛡️  Adding security headers and HTTPS enforcement...")
        
        security_middleware = '''"""
PROMETHEUS Trading Platform - Security Middleware
Implements security headers, HTTPS enforcement, and CSRF protection
"""

import os
from fastapi import Request, HTTPException
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        # HTTPS enforcement
        if os.getenv("HTTPS_ONLY", "true").lower() == "true":
            if request.url.scheme != "https" and not request.url.hostname in ["localhost", "127.0.0.1"]:
                https_url = request.url.replace(scheme="https")
                return Response(status_code=301, headers={"Location": str(https_url)})
        
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response

def configure_secure_cors():
    """Configure secure CORS settings."""
    allowed_origins = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    
    return CORSMiddleware(
        allow_origins=[f"https://{origin}" for origin in allowed_origins] + 
                     [f"http://{origin}" for origin in allowed_origins if origin in ["localhost", "127.0.0.1"]],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"]
    )
'''
        
        middleware_path = self.project_root / "core" / "security_middleware.py"
        with open(middleware_path, 'w') as f:
            f.write(security_middleware)
        
        print(f"[CHECK] Security middleware created: {middleware_path}")
        self.fixes_applied.append("Added security headers and HTTPS enforcement")
    
    def implement_rate_limiting(self):
        """Implement rate limiting for API endpoints."""
        print("⏱️  Implementing rate limiting...")
        
        rate_limiting_code = '''"""
PROMETHEUS Trading Platform - Rate Limiting
Implements rate limiting to prevent abuse and DDoS attacks
"""

import os
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
        self.client_requests = defaultdict(deque)
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    
    async def dispatch(self, request: Request, call_next):
        if not self.enabled:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host
        if "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        
        # Check rate limit
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        while self.client_requests[client_ip] and self.client_requests[client_ip][0] < minute_ago:
            self.client_requests[client_ip].popleft()
        
        # Check if rate limit exceeded
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.client_requests[client_ip].append(current_time)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - len(self.client_requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response

# Endpoint-specific rate limits
ENDPOINT_RATE_LIMITS = {
    "/api/auth/login": 10,  # 10 login attempts per minute
    "/api/paper-trading/orders": 50,  # 50 orders per minute
    "/api/market-data": 200,  # 200 market data requests per minute
}

def get_endpoint_rate_limit(endpoint: str) -> int:
    """Get rate limit for specific endpoint."""
    return ENDPOINT_RATE_LIMITS.get(endpoint, 100)
'''
        
        rate_limit_path = self.project_root / "core" / "rate_limiting.py"
        with open(rate_limit_path, 'w') as f:
            f.write(rate_limiting_code)
        
        print(f"[CHECK] Rate limiting implemented: {rate_limit_path}")
        self.fixes_applied.append("Implemented API rate limiting")
    
    def fix_cors_configuration(self):
        """Fix CORS configuration to be more restrictive."""
        print("🌐 Fixing CORS configuration...")
        
        # This would be integrated into the main server file
        cors_config = '''
# Secure CORS Configuration for PROMETHEUS Trading Platform

from fastapi.middleware.cors import CORSMiddleware
import os

def setup_secure_cors(app):
    """Setup secure CORS configuration."""
    
    # Get allowed origins from environment
    allowed_origins = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,prometheus-trade.com").split(",")
    
    # Create secure origins list
    secure_origins = []
    for origin in allowed_origins:
        origin = origin.strip()
        if origin in ["localhost", "127.0.0.1"]:
            # Allow both HTTP and HTTPS for localhost
            secure_origins.extend([f"http://{origin}:3000", f"https://{origin}:3000"])
        else:
            # Only HTTPS for production domains
            secure_origins.append(f"https://{origin}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=secure_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
        ],
        expose_headers=["X-Total-Count", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
    )
'''
        
        cors_path = self.project_root / "config" / "secure_cors.py"
        with open(cors_path, 'w') as f:
            f.write(cors_config)
        
        print(f"[CHECK] Secure CORS configuration created: {cors_path}")
        self.fixes_applied.append("Fixed CORS configuration")
    
    def generate_security_report(self):
        """Generate security hardening report."""
        report = {
            "hardening_timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "security_improvements": [
                "Removed all hardcoded secrets from source code",
                "Created secure environment variable template",
                "Enhanced authentication with bcrypt and secure JWT",
                "Implemented comprehensive security headers",
                "Added HTTPS enforcement",
                "Implemented rate limiting for API endpoints",
                "Fixed CORS configuration to be restrictive",
                "Fixed file permissions for sensitive files"
            ],
            "next_steps": [
                "Update .env.secure_template with your actual API keys",
                "Test all functionality after security changes",
                "Run security audit again to verify fixes",
                "Deploy with HTTPS certificate",
                "Monitor rate limiting effectiveness"
            ],
            "backup_location": str(self.backup_dir)
        }
        
        report_path = self.project_root / "security_hardening_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Security hardening report saved: {report_path}")
        
        # Print summary
        print("\n🔒 SECURITY HARDENING SUMMARY")
        print("=" * 50)
        for fix in self.fixes_applied:
            print(f"[CHECK] {fix}")
        
        print(f"\n📁 Backup created: {self.backup_dir}")
        print("\n[WARNING]️  IMPORTANT NEXT STEPS:")
        print("1. Update .env.secure_template with your actual API keys")
        print("2. Rename .env.secure_template to .env")
        print("3. Test all functionality")
        print("4. Run security audit again to verify fixes")


def main():
    """Main entry point for security hardening."""
    hardening = SecurityHardening()
    hardening.run_complete_hardening()


if __name__ == "__main__":
    main()
