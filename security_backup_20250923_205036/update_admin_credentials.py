#!/usr/bin/env python3
"""
Update admin credentials for PROMETHEUS Trading Platform
Sets the correct admin email and password as specified by the user
"""

import sys
import os
from pathlib import Path

def update_admin_credentials():
    """Update admin credentials to the correct ones"""
    print("🔐 UPDATING ADMIN CREDENTIALS...")
    print("=" * 50)
    
    try:
        # Import after setting up path
        from core.auth_service import auth_service, UserRole
        from core.database_manager import DatabaseManager
        import bcrypt
        
        # New credentials as specified by user
        new_email = "admin@prometheus-trader.com"
        new_password = "PrometheusAdmin2024!"
        
        print(f"Setting admin credentials:")
        print(f"  Email: {new_email}")
        print(f"  Password: {new_password}")
        print()
        
        # Hash the new password
        password_hash = auth_service.hash_password(new_password)
        
        # Update existing admin user or create new one
        db = auth_service.db_manager
        
        # Check if admin user exists
        existing_admin = db.fetch_one(
            "SELECT * FROM users WHERE role = 'admin' AND is_active = 1"
        )
        
        if existing_admin:
            print(f"📝 Updating existing admin user: {existing_admin['username']}")
            # Update existing admin
            db.execute_query(
                "UPDATE users SET email = ?, password_hash = ? WHERE id = ?",
                (new_email, password_hash, existing_admin['id'])
            )
            print("[CHECK] Admin credentials updated successfully!")
        else:
            print("📝 Creating new admin user...")
            # Create new admin user
            admin_user = auth_service.create_user(
                username="admin",
                email=new_email,
                password=new_password,
                role=UserRole.ADMIN,
                tenant_id="default",
                metadata={"created_by": "credential_update", "is_default": True}
            )
            print("[CHECK] New admin user created successfully!")
        
        # Verify the new credentials work
        print("\n🔍 VERIFYING NEW CREDENTIALS...")
        from core.auth_service import LoginCredentials
        
        test_credentials = [
            ("admin", new_password),
            (new_email, new_password)
        ]
        
        for username, password in test_credentials:
            print(f"Testing: {username} / {password}")
            try:
                creds = LoginCredentials(username=username, password=password)
                user = auth_service.authenticate_user(creds)
                
                if user:
                    print(f"  [CHECK] SUCCESS - User: {user.username} ({user.email}) - Role: {user.role.value}")
                else:
                    print(f"  [ERROR] FAILED - Invalid credentials")
                    
            except Exception as e:
                print(f"  [ERROR] ERROR: {e}")
            print()
        
        print("🎉 ADMIN CREDENTIALS UPDATE COMPLETE!")
        print("=" * 50)
        print("[CHECK] New Admin Credentials:")
        print(f"   Email: {new_email}")
        print(f"   Password: {new_password}")
        print("   Alternative Username: admin")
        print()
        print("🚀 You can now login to the PROMETHEUS platform with these credentials.")
        
    except Exception as e:
        print(f"[ERROR] Error updating credentials: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 PROMETHEUS TRADING PLATFORM - CREDENTIAL UPDATER")
    print("=" * 60)
    success = update_admin_credentials()
    
    if success:
        print("\n📋 SUMMARY:")
        print("[CHECK] Admin credentials have been updated successfully")
        print("[CHECK] You can now login with:")
        print("   - Email: admin@prometheus-trader.com")
        print("   - Password: PrometheusAdmin2024!")
        print("   - Alternative: username 'admin' with the same password")
    else:
        print("\n[ERROR] Failed to update credentials. Please check the error messages above.")
    
    sys.exit(0 if success else 1)
