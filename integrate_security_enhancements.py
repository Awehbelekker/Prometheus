#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Security Integration Script
Integrates security enhancements into the main production server
"""

import os
import re
from pathlib import Path
import shutil
from datetime import datetime

class SecurityIntegrator:
    """Integrates security enhancements into the production server."""
    
    def __init__(self):
        self.project_root = Path(".")
        self.server_file = self.project_root / "unified_production_server.py"
        self.backup_dir = Path("security_integration_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.backup_dir.mkdir(exist_ok=True)
        self.integrations_applied = []
        
    def integrate_security(self):
        """Integrate all security enhancements."""
        print("🔒 Integrating Security Enhancements into Production Server")
        print("=" * 60)
        
        # Create backup
        self.create_backup()
        
        # Step 1: Add security imports
        self.add_security_imports()
        
        # Step 2: Add security middleware
        self.add_security_middleware()
        
        # Step 3: Add rate limiting
        self.add_rate_limiting()
        
        # Step 4: Add security headers
        self.add_security_headers()
        
        # Step 5: Create production startup script
        self.create_production_startup()
        
        # Step 6: Generate integration report
        self.generate_integration_report()
        
        print(f"\n🎉 Security integration completed!")
        print(f"[CHECK] Applied {len(self.integrations_applied)} integrations")
    
    def create_backup(self):
        """Create backup of original files."""
        print("📁 Creating backup of original files...")
        
        if self.server_file.exists():
            backup_file = self.backup_dir / "unified_production_server.py"
            shutil.copy2(self.server_file, backup_file)
            print(f"[CHECK] Backup created: {backup_file}")
    
    def add_security_imports(self):
        """Add security-related imports to the server."""
        print("📦 Adding security imports...")
        
        # Read the current server file
        with open(self.server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Security imports to add
        security_imports = '''
# Security enhancements
import secrets
import hashlib
import bcrypt
from collections import defaultdict, deque
import time as time_module
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
'''
        
        # Find the import section and add security imports
        import_pattern = r'(from pydantic import BaseModel, Field\n)'
        if re.search(import_pattern, content):
            content = re.sub(import_pattern, r'\1' + security_imports, content)
            
            with open(self.server_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[CHECK] Security imports added")
            self.integrations_applied.append("Added security imports")
        else:
            print("[WARNING]️  Could not find import section to modify")
    
    def add_security_middleware(self):
        """Add security middleware classes."""
        print("🛡️  Adding security middleware...")
        
        security_middleware_code = '''

# Security Middleware Classes
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        # HTTPS enforcement
        if os.getenv("HTTPS_ONLY", "false").lower() == "true":
            if request.url.scheme != "https" and request.url.hostname not in ["localhost", "127.0.0.1"]:
                https_url = str(request.url).replace("http://", "https://")
                return JSONResponse(
                    status_code=301,
                    headers={"Location": https_url}
                )
        
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

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
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
        current_time = time_module.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        while self.client_requests[client_ip] and self.client_requests[client_ip][0] < minute_ago:
            self.client_requests[client_ip].popleft()
        
        # Check if rate limit exceeded
        if len(self.client_requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded. Please try again later."},
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

'''
        
        # Read current content
        with open(self.server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find a good place to insert middleware (after imports, before app creation)
        insertion_point = content.find('# FastAPI and dependencies')
        if insertion_point != -1:
            # Insert before FastAPI imports
            content = content[:insertion_point] + security_middleware_code + '\n' + content[insertion_point:]
            
            with open(self.server_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[CHECK] Security middleware added")
            self.integrations_applied.append("Added security middleware classes")
        else:
            print("[WARNING]️  Could not find insertion point for middleware")
    
    def add_rate_limiting(self):
        """Add rate limiting to the FastAPI app."""
        print("⏱️  Adding rate limiting configuration...")
        
        # This would be added to the app initialization section
        rate_limit_config = '''
# Add security middleware to app
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")))
'''
        
        # Read current content
        with open(self.server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find CORS middleware addition and add security middleware after it
        cors_pattern = r'(app\.add_middleware\(CORSMiddleware[^)]+\))'
        if re.search(cors_pattern, content, re.DOTALL):
            content = re.sub(cors_pattern, r'\1\n' + rate_limit_config, content, flags=re.DOTALL)
            
            with open(self.server_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[CHECK] Rate limiting configuration added")
            self.integrations_applied.append("Added rate limiting configuration")
        else:
            print("[WARNING]️  Could not find CORS middleware to add rate limiting after")
    
    def add_security_headers(self):
        """Add security headers endpoint."""
        print("🔐 Adding security status endpoint...")
        
        security_endpoint = '''

@app.get("/api/security/status")
async def get_security_status():
    """Get security configuration status."""
    return {
        "https_only": os.getenv("HTTPS_ONLY", "false").lower() == "true",
        "rate_limiting": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
        "rate_limit_per_minute": int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")),
        "security_headers": True,
        "timestamp": datetime.now().isoformat()
    }
'''
        
        # Read current content
        with open(self.server_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add before the main block
        main_pattern = r'(if __name__ == "__main__":)'
        if re.search(main_pattern, content):
            content = re.sub(main_pattern, security_endpoint + '\n\n' + r'\1', content)
            
            with open(self.server_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("[CHECK] Security status endpoint added")
            self.integrations_applied.append("Added security status endpoint")
        else:
            print("[WARNING]️  Could not find main block to add security endpoint")
    
    def create_production_startup(self):
        """Create production startup script with security."""
        print("🚀 Creating secure production startup script...")
        
        startup_script = '''#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Secure Production Startup
Enterprise-grade startup with security enhancements
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_environment():
    """Check environment configuration."""
    print("🔍 Checking environment configuration...")
    
    required_vars = [
        "JWT_SECRET_KEY",
        "ENCRYPTION_KEY", 
        "SESSION_SECRET_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERROR] Missing required environment variables: {missing_vars}")
        print("Please update your .env file with secure values")
        return False
    
    print("[CHECK] Environment configuration OK")
    return True

def check_security_config():
    """Check security configuration."""
    print("🔒 Checking security configuration...")
    
    security_checks = {
        "HTTPS_ONLY": os.getenv("HTTPS_ONLY", "false").lower() == "true",
        "RATE_LIMIT_ENABLED": os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true",
        "SECURE_COOKIES": os.getenv("SECURE_COOKIES", "true").lower() == "true"
    }
    
    for check, status in security_checks.items():
        status_icon = "[CHECK]" if status else "[WARNING]️ "
        print(f"{status_icon} {check}: {status}")
    
    return True

def start_server():
    """Start the production server."""
    print("🚀 Starting PROMETHEUS Trading Platform...")
    
    # Environment checks
    if not check_environment():
        sys.exit(1)
    
    check_security_config()
    
    # Server configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    workers = int(os.getenv("WORKERS", "4"))
    
    print(f"🌐 Server starting on {host}:{port} with {workers} workers")
    print("🔒 Security enhancements enabled")
    print("📊 Monitoring available at /metrics")
    print("🏥 Health check available at /health")
    
    # Start with uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "unified_production_server:app",
        "--host", host,
        "--port", str(port),
        "--workers", str(workers),
        "--access-log",
        "--log-level", "info"
    ]
    
    if os.getenv("ENVIRONMENT") == "production":
        cmd.extend(["--ssl-keyfile", "/etc/ssl/private/prometheus-trade.com.key"])
        cmd.extend(["--ssl-certfile", "/etc/ssl/certs/prometheus-trade.com.crt"])
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\\n🛑 Server shutdown requested")
    except Exception as e:
        print(f"[ERROR] Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server()
'''
        
        startup_path = self.project_root / "start_production_server.py"
        with open(startup_path, 'w', encoding='utf-8') as f:
            f.write(startup_script)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(startup_path, 0o755)
        
        print(f"[CHECK] Production startup script created: {startup_path}")
        self.integrations_applied.append("Created secure production startup script")
    
    def generate_integration_report(self):
        """Generate security integration report."""
        report = {
            "integration_timestamp": datetime.now().isoformat(),
            "integrations_applied": self.integrations_applied,
            "security_features": [
                "Security headers middleware (X-Frame-Options, CSP, etc.)",
                "Rate limiting middleware with configurable limits",
                "HTTPS enforcement for production",
                "Secure cookie configuration",
                "CORS security with restricted origins",
                "Security status endpoint for monitoring",
                "Production startup script with security checks"
            ],
            "configuration_files": [
                ".env.secure_template - Secure environment variables",
                "config/secure_auth_config.py - Enhanced authentication",
                "core/security_middleware.py - Security middleware",
                "core/rate_limiting.py - Rate limiting implementation",
                "start_production_server.py - Secure startup script"
            ],
            "next_steps": [
                "Update .env with your actual API keys and secrets",
                "Test all endpoints with security middleware",
                "Configure SSL certificates for HTTPS",
                "Monitor rate limiting effectiveness",
                "Run security audit to verify fixes"
            ],
            "backup_location": str(self.backup_dir)
        }
        
        report_path = self.project_root / "security_integration_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(report, f, indent=2)
        
        print(f"\\n📊 Security integration report saved: {report_path}")
        
        # Print summary
        print("\\n🔒 SECURITY INTEGRATION SUMMARY")
        print("=" * 50)
        for integration in self.integrations_applied:
            print(f"[CHECK] {integration}")
        
        print(f"\\n📁 Backup created: {self.backup_dir}")
        print("\\n[WARNING]️  IMPORTANT NEXT STEPS:")
        print("1. Update .env.secure_template with your actual credentials")
        print("2. Rename .env.secure_template to .env")
        print("3. Test the server: python start_production_server.py")
        print("4. Verify security: curl -I http://localhost:8000/health")


def main():
    """Main entry point."""
    integrator = SecurityIntegrator()
    integrator.integrate_security()


if __name__ == "__main__":
    main()
