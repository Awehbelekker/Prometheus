# Enhanced Authentication Security Configuration

import os
import bcrypt
import secrets
from datetime import datetime, timedelta
import jwt

class SecureAuthConfig:
    """Secure authentication configuration."""
    
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
        """Hash password using bcrypt with secure rounds."""
        salt = bcrypt.gensalt(rounds=SecureAuthConfig.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def generate_jwt_token(user_data: dict) -> str:
        """Generate secure JWT token."""
        payload = {
            **user_data,
            'exp': datetime.utcnow() + timedelta(hours=SecureAuthConfig.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        }
        return jwt.encode(payload, SecureAuthConfig.JWT_SECRET_KEY, algorithm=SecureAuthConfig.JWT_ALGORITHM)
    
    @staticmethod
    def verify_jwt_token(token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, SecureAuthConfig.JWT_SECRET_KEY, algorithms=[SecureAuthConfig.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception("Token has expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid token")
