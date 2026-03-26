#!/usr/bin/env python3
"""
🔧 CORS FIX - Add explicit OPTIONS handlers for CORS preflight
This script adds OPTIONS handlers to fix CORS preflight issues without disrupting trading
"""

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app for CORS proxy
app = FastAPI(
    title="PROMETHEUS CORS Fix",
    description="CORS preflight handler for frontend integration",
    version="1.0.0"
)

# Add comprehensive CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.options("/api/auth/login")
async def options_auth_login():
    """Handle CORS preflight for login endpoint"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.options("/api/{path:path}")
async def options_catch_all(path: str):
    """Handle CORS preflight for all API endpoints"""
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true"
        }
    )

@app.get("/")
async def root():
    return {
        "message": "🔧 PROMETHEUS CORS Fix Server",
        "status": "running",
        "purpose": "Handle CORS preflight requests"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "CORS-Fix"}

if __name__ == "__main__":
    print("🔧 Starting PROMETHEUS CORS Fix Server on port 8003...")
    print("This server handles CORS preflight requests for frontend integration")
    print("Main backend remains on port 8000")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8003,
        log_level="info"
    )
