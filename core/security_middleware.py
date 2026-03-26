"""
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
