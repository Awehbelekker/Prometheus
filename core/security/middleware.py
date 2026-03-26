"""
Security Middleware for Prometheus Trading App
Implements comprehensive security measures including rate limiting, input validation, and security headers
"""

import time
import json
import re
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from .database_security import sql_protector
import logging

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware"""
    
    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.config = config or {}
        self.rate_limiter = RateLimiter()
        self.input_validator = InputValidator()
        
        # Security configuration
        self.enable_rate_limiting = self.config.get('enable_rate_limiting', True)
        self.enable_input_validation = self.config.get('enable_input_validation', True)
        self.enable_security_headers = self.config.get('enable_security_headers', True)
        
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware"""
        start_time = time.time()
        
        try:
            # 1. Rate limiting
            if self.enable_rate_limiting:
                await self._check_rate_limit(request)
            
            # 2. Input validation
            if self.enable_input_validation:
                await self._validate_input(request)
            
            # 3. Process request
            response = await call_next(request)
            
            # 4. Add security headers
            if self.enable_security_headers:
                self._add_security_headers(response)

            # 5. Add rate limit headers
            if self.enable_rate_limiting:
                self._add_rate_limit_headers(request, response)
            
            # 5. Log request
            process_time = time.time() - start_time
            await self._log_request(request, response, process_time)
            
            return response
            
        except HTTPException as e:
            # Return proper error response
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "timestamp": time.time()}
            )
        except Exception as e:
            # Broaden JWT-related error handling: some jwt libs expose different exception names
            name = type(e).__name__
            msg = str(e)
            if 'JWTError' in name or 'InvalidToken' in name or 'DecodeError' in name:
                logger.warning(f"Auth token error intercepted ({name}): {msg}")
                return JSONResponse(status_code=401, content={"error":"Unauthorized", "timestamp": time.time()})
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "timestamp": time.time()}
            )
    
    async def _check_rate_limit(self, request: Request):
        """Check rate limiting"""
        client_ip = self._get_client_ip(request)
        endpoint = request.url.path
        
        # Different limits for different endpoints
        if endpoint.startswith('/api/auth/'):
            limit = 5  # 5 requests per minute for auth endpoints
        elif endpoint.startswith('/api/trading/'):
            limit = 60  # 60 requests per minute for trading
        else:
            limit = 100  # 100 requests per minute for general API
        
        if not self.rate_limiter.is_allowed(client_ip, endpoint, limit):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    async def _validate_input(self, request: Request):
        """Validate request input for security threats"""
        # Check URL for suspicious patterns
        url_path = str(request.url.path)
        if sql_protector.is_sql_injection_attempt(url_path):
            logger.warning(f"SQL injection attempt detected in URL: {url_path}")
            raise HTTPException(status_code=400, detail="Invalid request")

        if self.input_validator.contains_xss(url_path):
            logger.warning(f"XSS attempt detected in URL: {url_path}")
            raise HTTPException(status_code=400, detail="Invalid request")

        # Check query parameters
        for key, value in request.query_params.items():
            if sql_protector.is_sql_injection_attempt(value):
                logger.warning(f"SQL injection attempt in query param {key}: {value}")
                raise HTTPException(status_code=400, detail="Invalid query parameter")

            if self.input_validator.contains_xss(value):
                logger.warning(f"XSS attempt in query param {key}: {value}")
                raise HTTPException(status_code=400, detail="Invalid query parameter")
        
        # Check request body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')

                    if sql_protector.is_sql_injection_attempt(body_str):
                        logger.warning(f"SQL injection attempt in request body")
                        raise HTTPException(status_code=400, detail="Invalid request body")

                    if self.input_validator.contains_xss(body_str):
                        logger.warning(f"XSS attempt in request body")
                        raise HTTPException(status_code=400, detail="Invalid request body")
                    
                    # Validate JSON structure if content-type is JSON
                    content_type = request.headers.get('content-type', '')
                    if 'application/json' in content_type:
                        try:
                            json.loads(body_str)
                        except json.JSONDecodeError:
                            raise HTTPException(status_code=400, detail="Invalid JSON format")
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Invalid request encoding")
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers to response"""
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS protection (deprecated but still useful for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS (HTTP Strict Transport Security) - Force HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # Content Security Policy - Comprehensive protection
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts for React
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' wss: https: ws:",
            "media-src 'self'",
            "object-src 'none'",
            "frame-src 'none'",
            "base-uri 'self'",
            "form-action 'self'",
            "frame-ancestors 'none'",
            "upgrade-insecure-requests"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Referrer Policy - Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        permissions_directives = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "accelerometer=()",
            "gyroscope=()",
            "fullscreen=(self)"
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions_directives)

        # Cross-Origin Embedder Policy
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

        # Cross-Origin Opener Policy
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin Resource Policy
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Expect-CT (Certificate Transparency)
        response.headers["Expect-CT"] = "max-age=86400, enforce"

        # X-Permitted-Cross-Domain-Policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Clear-Site-Data (for logout endpoints)
        if hasattr(response, 'url') and '/logout' in str(response.url):
            response.headers["Clear-Site-Data"] = '"cache", "cookies", "storage"'

        # Remove/mask server information
        response.headers["Server"] = "Prometheus Trading Server"

        # Add custom security headers
        response.headers["X-Content-Security-Policy"] = response.headers["Content-Security-Policy"]
        response.headers["X-WebKit-CSP"] = response.headers["Content-Security-Policy"]

        # Cache control for sensitive endpoints
        if hasattr(response, 'url') and any(path in str(response.url) for path in ['/api/', '/admin/', '/auth/']):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

    def _add_rate_limit_headers(self, request: Request, response: Response):
        """Add rate limiting headers to response"""
        try:
            client_ip = self._get_client_ip(request)
            endpoint = request.url.path

            # Get rate limit info
            rate_info = self.rate_limiter.get_rate_limit_info(client_ip, endpoint)

            # Add standard rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_info['limit'])
            response.headers["X-RateLimit-Remaining"] = str(rate_info['remaining'])
            response.headers["X-RateLimit-Reset"] = str(rate_info['reset_time'])
            response.headers["X-RateLimit-Window"] = str(rate_info['window_seconds'])
            response.headers["X-RateLimit-Category"] = rate_info['category']

            # Add Retry-After header if rate limited
            if rate_info['remaining'] == 0:
                response.headers["Retry-After"] = str(rate_info['window_seconds'])

        except Exception as e:
            logger.error(f"Error adding rate limit headers: {e}")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _log_request(self, request: Request, response: Response, process_time: float):
        """Log request for security monitoring"""
        client_ip = self._get_client_ip(request)
        
        log_data = {
            "timestamp": time.time(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "user_agent": request.headers.get('User-Agent', ''),
            "referer": request.headers.get('Referer', '')
        }
        
        # Log suspicious activity
        if response.status_code in [400, 401, 403, 429]:
            logger.warning(f"Security event: {log_data}")
        else:
            logger.info(f"Request: {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

class RateLimiter:
    """Enhanced rate limiter with multiple algorithms"""

    def __init__(self):
        self.requests = {}  # In production, use Redis
        self.window_size = 60  # 1 minute window
        self.burst_window = 10  # 10 second burst window
        self.blocked_ips = {}  # Temporarily blocked IPs

        # Rate limit configurations
        self.limits = {
            'auth': {'requests': 5, 'window': 900},      # 5 requests per 15 minutes
            'trading': {'requests': 60, 'window': 60},    # 60 requests per minute
            'api': {'requests': 100, 'window': 60},       # 100 requests per minute
            'search': {'requests': 20, 'window': 60},     # 20 requests per minute
            'admin': {'requests': 200, 'window': 60},     # 200 requests per minute
            'default': {'requests': 50, 'window': 60}     # 50 requests per minute
        }

    def is_allowed(self, identifier: str, endpoint: str, limit: int) -> bool:
        """Check if request is allowed under rate limit"""
        # Check if IP is temporarily blocked
        if self._is_ip_blocked(identifier):
            return False

        # Determine rate limit category
        category = self._get_endpoint_category(endpoint)
        config = self.limits.get(category, self.limits['default'])

        # Use configured limits instead of passed limit
        limit = config['requests']
        window = config['window']

        key = f"{identifier}:{category}"
        now = time.time()

        # Clean old entries
        if key in self.requests:
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if now - timestamp < window
            ]
        else:
            self.requests[key] = []

        # Check for burst protection (too many requests in short time)
        recent_requests = [
            timestamp for timestamp in self.requests[key]
            if now - timestamp < self.burst_window
        ]

        if len(recent_requests) > limit // 6:  # Max 1/6 of limit in burst window
            self._block_ip_temporarily(identifier, 300)  # Block for 5 minutes
            return False

        # Check main limit
        if len(self.requests[key]) >= limit:
            # Progressive blocking for repeated violations
            violation_count = self._get_violation_count(identifier)
            if violation_count > 3:
                self._block_ip_temporarily(identifier, 600)  # Block for 10 minutes
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def _get_endpoint_category(self, endpoint: str) -> str:
        """Determine rate limit category for endpoint"""
        if '/auth/' in endpoint or '/login' in endpoint:
            return 'auth'
        elif '/trading/' in endpoint:
            return 'trading'
        elif '/search' in endpoint:
            return 'search'
        elif '/admin/' in endpoint:
            return 'admin'
        elif '/api/' in endpoint:
            return 'api'
        else:
            return 'default'

    def _is_ip_blocked(self, identifier: str) -> bool:
        """Check if IP is temporarily blocked"""
        if identifier in self.blocked_ips:
            if time.time() < self.blocked_ips[identifier]['until']:
                return True
            else:
                del self.blocked_ips[identifier]
        return False

    def _block_ip_temporarily(self, identifier: str, duration: int):
        """Temporarily block an IP"""
        self.blocked_ips[identifier] = {
            'until': time.time() + duration,
            'reason': 'rate_limit_violation',
            'blocked_at': time.time()
        }
        logger.warning(f"IP {identifier} temporarily blocked for {duration} seconds")

    def _get_violation_count(self, identifier: str) -> int:
        """Get number of recent violations for an IP"""
        # Simple implementation - count violations in last hour
        violation_key = f"violations:{identifier}"
        now = time.time()

        if violation_key in self.requests:
            violations = [
                timestamp for timestamp in self.requests[violation_key]
                if now - timestamp < 3600  # 1 hour
            ]
            return len(violations)
        return 0

    def get_rate_limit_info(self, identifier: str, endpoint: str) -> Dict[str, Any]:
        """Get rate limit information for an identifier"""
        category = self._get_endpoint_category(endpoint)
        config = self.limits.get(category, self.limits['default'])
        key = f"{identifier}:{category}"

        now = time.time()
        window = config['window']

        if key in self.requests:
            current_requests = [
                timestamp for timestamp in self.requests[key]
                if now - timestamp < window
            ]
            remaining = max(0, config['requests'] - len(current_requests))
        else:
            remaining = config['requests']

        return {
            'limit': config['requests'],
            'remaining': remaining,
            'reset_time': int(now + window),
            'window_seconds': window,
            'category': category
        }

class InputValidator:
    """Input validation for security threats"""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",
            r"(--|#|/\*|\*/)",
            r"(\bUNION\b.*\bSELECT\b)",
            r"(\b(EXEC|EXECUTE)\b)",
            r"(\bxp_\w+)",
            r"(\bsp_\w+)",
            r"(\b(WAITFOR|DELAY)\b)",
            r"(\b(CAST|CONVERT)\b.*\b(CHAR|VARCHAR)\b)"
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"expression\s*\(",
            r"url\s*\(",
            r"@import"
        ]
        
        # Compile patterns for better performance
        self.compiled_sql_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_patterns]
        self.compiled_xss_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
    
    def contains_sql_injection(self, text: str) -> bool:
        """Check if text contains SQL injection patterns"""
        if not text:
            return False
        
        for pattern in self.compiled_sql_patterns:
            if pattern.search(text):
                return True
        return False
    
    def contains_xss(self, text: str) -> bool:
        """Check if text contains XSS patterns"""
        if not text:
            return False
        
        for pattern in self.compiled_xss_patterns:
            if pattern.search(text):
                return True
        return False
    
    def sanitize_input(self, text: str) -> str:
        """Sanitize input by removing dangerous characters"""
        if not text:
            return text
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newline and tab
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Limit length
        if len(text) > 10000:  # 10KB limit
            text = text[:10000]
        
        return text

def create_security_middleware(config: Optional[Dict[str, Any]] = None):
    """Factory function to create security middleware"""
    return SecurityMiddleware(None, config)
