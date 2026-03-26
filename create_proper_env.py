#!/usr/bin/env python3
"""
Create Proper .env File
Create a clean .env file with proper UTF-8 encoding
"""

def create_proper_env():
    """Create a proper .env file with correct encoding"""
    env_content = """# PROMETHEUS Trading Platform Environment Configuration
# Generated with proper UTF-8 encoding

# OpenAI Configuration
OPENAI_API_KEY=test_key
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000

# ThinkMesh Enhanced Reasoning
THINKMESH_ENABLED=true

# Alpaca Trading Configuration
ALPACA_API_KEY=test_alpaca_key
ALPACA_SECRET_KEY=test_alpaca_secret
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Interactive Brokers Configuration
IB_HOST=127.0.0.1
IB_PORT=7497
IB_CLIENT_ID=1

# Database Configuration
DATABASE_URL=sqlite:///prometheus_trading.db

# Security Configuration
SECRET_KEY=test_secret_key
JWT_SECRET=test_jwt_secret

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=prometheus_trading.log

# GPT-OSS Configuration
GPT_OSS_ENABLED=true
GPT_OSS_API_ENDPOINT=http://localhost:5000
"""

    try:
        # Write with explicit UTF-8 encoding
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("[OK] .env file created successfully with proper UTF-8 encoding")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create .env file: {e}")
        return False

if __name__ == "__main__":
    success = create_proper_env()
    if success:
        print("[SUCCESS] Environment configuration ready!")
    else:
        print("[FAILED] Environment configuration failed!")
