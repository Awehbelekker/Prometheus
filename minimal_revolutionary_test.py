#!/usr/bin/env python3
"""
Minimal test server with ONLY Revolutionary endpoints
"""

from fastapi import FastAPI
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="Minimal Revolutionary Test")

# Check environment variable
ENABLE_REVOLUTIONARY = os.getenv('ENABLE_REVOLUTIONARY_FEATURES', 'false').lower() in ('1','true','yes','on')

print(f"🚀 MINIMAL TEST SERVER STARTING")
print(f"   ENABLE_REVOLUTIONARY_FEATURES = {os.getenv('ENABLE_REVOLUTIONARY_FEATURES', 'NOT SET')}")
print(f"   ENABLE_REVOLUTIONARY (boolean) = {ENABLE_REVOLUTIONARY}")

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/revolutionary/test")
async def revolutionary_test():
    return {
        "success": True,
        "message": "Revolutionary endpoint is working!",
        "enable_revolutionary": ENABLE_REVOLUTIONARY,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/revolutionary/engines/status")
async def get_revolutionary_engines_status():
    return {
        "success": True,
        "message": "Revolutionary engines status endpoint is working!",
        "engines": {
            "crypto": "test",
            "options": "test",
            "advanced": "test",
            "market_maker": "test",
            "master": "test"
        },
        "timestamp": datetime.now().isoformat()
    }

print(f"[CHECK] ALL ENDPOINTS REGISTERED")
print(f"   - /health")
print(f"   - /api/revolutionary/test")
print(f"   - /api/revolutionary/engines/status")

