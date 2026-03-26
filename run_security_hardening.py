#!/usr/bin/env python3
"""
Quick Security Hardening Script
"""

import os
import secrets
import string
from pathlib import Path

def generate_secure_password(length=16):
    """Generate secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key(length=32):
    """Generate secure API key"""
    return secrets.token_urlsafe(length)

def main():
    print("🔒 PROMETHEUS Security Hardening")
    print("=" * 50)
    
    # Generate secure credentials
    print("🔐 Generating secure credentials...")
    credentials = {
        'admin_password': generate_secure_password(20),
        'jwt_secret_key': generate_api_key(64),
        'encryption_key': secrets.token_urlsafe(32),
        'database_password': generate_secure_password(24),
        'api_secret_key': generate_api_key(48),
        'session_secret': generate_api_key(32)
    }
    
    # Create environment template
    print("📝 Creating secure environment template...")
    env_template = f"""# PROMETHEUS Trading Platform - Production Environment Configuration

# ================================
# SECURITY CONFIGURATION
# ================================
PROMETHEUS_SECRET_KEY={credentials['jwt_secret_key']}
ENCRYPTION_KEY={credentials['encryption_key']}
SESSION_SECRET={credentials['session_secret']}

# ================================
# DATABASE CONFIGURATION
# ================================
DATABASE_URL=postgresql://prometheus_user:{credentials['database_password']}@localhost:5432/prometheus_prod
REDIS_URL=redis://localhost:6379/0

# ================================
# TRADING CONFIGURATION
# ================================
# IMPORTANT: Set these to your actual Alpaca credentials
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Trading Safety Settings
ENABLE_LIVE_ORDER_EXECUTION=false
ALWAYS_LIVE=false
LIVE_TRADING_ENABLED=false

# ================================
# SECURITY SETTINGS
# ================================
SECRETS_BACKEND=local
ADMIN_PASSWORD={credentials['admin_password']}

# ================================
# PRODUCTION SETTINGS
# ================================
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
"""
    
    # Save environment file
    with open('.env.production', 'w') as f:
        f.write(env_template)
    
    # Set restrictive permissions
    os.chmod('.env.production', 0o600)
    
    print("[CHECK] Environment file created: .env.production")
    
    # Create secrets migration script
    print("📝 Creating secrets migration script...")
    migration_script = '''#!/usr/bin/env python3
"""
Migrate secrets to secure storage
"""

import os
import sys
import json
from pathlib import Path

def migrate_secrets():
    """Migrate secrets from environment to secure storage"""
    
    # Create secrets directory
    secrets_dir = Path("enterprise/secrets")
    secrets_dir.mkdir(parents=True, exist_ok=True)
    
    # Load environment variables
    secrets_to_migrate = {}
    
    if os.path.exists('.env.production'):
        with open('.env.production', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if any(keyword in key.lower() for keyword in ['password', 'secret', 'key']):
                        secrets_to_migrate[key.lower()] = value
    
    # Save to secure file
    secrets_file = secrets_dir / "production_secrets.json"
    with open(secrets_file, 'w') as f:
        json.dump(secrets_to_migrate, f, indent=2)
    
    # Set restrictive permissions
    os.chmod(secrets_file, 0o600)
    
    print(f"[CHECK] Secrets migrated to {secrets_file}")
    print("🔒 File permissions set to 600 (owner read/write only)")

if __name__ == "__main__":
    migrate_secrets()
'''
    
    with open('migrate_secrets.py', 'w') as f:
        f.write(migration_script)
    
    os.chmod('migrate_secrets.py', 0o755)
    
    print("[CHECK] Migration script created: migrate_secrets.py")
    
    # Create security checklist
    print("📋 Creating security checklist...")
    checklist = """# 🔒 PROMETHEUS Security Checklist

## [CHECK] COMPLETED
- [x] Generated secure credentials
- [x] Created production environment template
- [x] Set restrictive file permissions
- [x] Created secrets migration script

## 🔄 TODO - CRITICAL
- [ ] Replace all hardcoded credentials in source code
- [ ] Set up HashiCorp Vault or AWS Secrets Manager
- [ ] Enable MFA for all admin accounts
- [ ] Configure SSL/TLS certificates
- [ ] Set up database encryption at rest
- [ ] Implement comprehensive audit logging
- [ ] Configure firewall and network security
- [ ] Set up monitoring and alerting

## 🔄 TODO - HIGH PRIORITY
- [ ] Penetration testing
- [ ] Security code review
- [ ] Implement rate limiting
- [ ] Set up backup encryption
- [ ] Configure intrusion detection
- [ ] Implement security headers
- [ ] Set up log aggregation
- [ ] Create incident response plan

## 📋 NEXT STEPS
1. Run: python migrate_secrets.py
2. Update source code to use environment variables
3. Set up production database with encryption
4. Configure monitoring and alerting
5. Perform security testing
"""
    
    with open('SECURITY_CHECKLIST.md', 'w') as f:
        f.write(checklist)
    
    print("[CHECK] Security checklist created: SECURITY_CHECKLIST.md")
    
    print("\n🎉 Security hardening phase 1 completed!")
    print("\n📋 NEXT STEPS:")
    print("1. Review .env.production file")
    print("2. Run: python migrate_secrets.py")
    print("3. Update source code to use environment variables")
    print("4. Follow SECURITY_CHECKLIST.md")
    
    print(f"\n🔐 Generated Admin Password: {credentials['admin_password']}")
    print("[WARNING]️  IMPORTANT: Store this password securely!")

if __name__ == "__main__":
    main()
