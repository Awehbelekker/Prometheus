"""
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
