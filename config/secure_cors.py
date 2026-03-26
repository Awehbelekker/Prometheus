
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
