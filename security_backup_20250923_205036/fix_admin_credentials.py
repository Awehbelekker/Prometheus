#!/usr/bin/env python3
"""
Update admin credentials to match what the user has always been using
"""

import sys
import os
import sqlite3
import bcrypt
from pathlib import Path

def update_admin_credentials():
    """Update admin credentials to user's expected values"""
    
    # User's expected credentials
    expected_email = "admin@prometheus-trader.com"
    expected_password = "PrometheusAdmin2024!"
    
    print("🔍 UPDATING ADMIN CREDENTIALS...")
    print("=" * 50)
    
    # Check both possible database locations
    db_paths = [
        "prometheus_trading.db",
        "ai_development_mass_framework/mass_framework.db"
    ]
    
    for db_path in db_paths:
        if not Path(db_path).exists():
            print(f"[ERROR] Database not found: {db_path}")
            continue
            
        print(f"\n📁 Checking database: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE role = 'admin'")
            admin_users = cursor.fetchall()
            
            if not admin_users:
                print("[ERROR] No admin users found")
                conn.close()
                continue
                
            for user in admin_users:
                print(f"\n👤 Found admin user:")
                print(f"   ID: {user['id']}")
                print(f"   Username: {user['username']}")
                print(f"   Email: {user['email']}")
                print(f"   Expected Email: {expected_email}")
                
                if user['email'] == expected_email:
                    print("[CHECK] Email already matches!")
                else:
                    # Update email and password
                    print(f"🔄 Updating credentials...")
                    
                    # Hash the expected password
                    salt = bcrypt.gensalt()
                    password_hash = bcrypt.hashpw(expected_password.encode('utf-8'), salt).decode('utf-8')
                    
                    # Update the user
                    cursor.execute("""
                        UPDATE users 
                        SET email = ?, password_hash = ?
                        WHERE id = ?
                    """, (expected_email, password_hash, user['id']))
                    
                    conn.commit()
                    print("[CHECK] Admin credentials updated successfully!")
                    
                    # Verify the update
                    cursor.execute("SELECT email FROM users WHERE id = ?", (user['id'],))
                    updated_user = cursor.fetchone()
                    print(f"[CHECK] Verified - New email: {updated_user['email']}")
            
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error updating {db_path}: {e}")

def check_why_credentials_changed():
    """Investigate why credentials might have changed"""
    
    print("\n🔍 INVESTIGATING CREDENTIAL CHANGES...")
    print("=" * 50)
    
    # Check if there are multiple admin users
    db_paths = [
        "prometheus_trading.db", 
        "ai_development_mass_framework/mass_framework.db"
    ]
    
    for db_path in db_paths:
        if not Path(db_path).exists():
            continue
            
        print(f"\n📁 Analyzing: {db_path}")
        
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all admin users with creation dates
            cursor.execute("""
                SELECT id, username, email, created_at, metadata
                FROM users 
                WHERE role = 'admin'
                ORDER BY created_at
            """)
            
            admins = cursor.fetchall()
            
            print(f"📊 Found {len(admins)} admin user(s):")
            
            for i, admin in enumerate(admins, 1):
                print(f"\n   Admin #{i}:")
                print(f"     ID: {admin['id']}")
                print(f"     Username: {admin['username']}")
                print(f"     Email: {admin['email']}")
                print(f"     Created: {admin['created_at']}")
                print(f"     Metadata: {admin['metadata']}")
                
                # Check if this looks like a system-created admin
                if admin['metadata'] and 'system' in admin['metadata']:
                    print("     🤖 This appears to be SYSTEM-CREATED")
                else:
                    print("     👤 This appears to be USER-CREATED")
            
            conn.close()
            
        except Exception as e:
            print(f"[ERROR] Error analyzing {db_path}: {e}")

def main():
    print("🚀 PROMETHEUS CREDENTIAL INVESTIGATION & FIX")
    print("=" * 60)
    
    # First, investigate why credentials changed
    check_why_credentials_changed()
    
    # Then update to expected credentials
    print("\n" + "=" * 60)
    update_admin_credentials()
    
    print("\n📋 SUMMARY:")
    print("=" * 50)
    print("Your credentials should now be:")
    print("- Email: admin@prometheus-trader.com")
    print("- Password: PrometheusAdmin2024!")
    print("\nReasons credentials may have changed:")
    print("- System auto-created default admin during setup")
    print("- Multiple databases with different admin users")
    print("- Development vs production environment differences")

if __name__ == "__main__":
    main()
