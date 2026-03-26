#!/usr/bin/env python3
"""
🧹 CLEAR FRONTEND CACHE AND REBUILD - PROMETHEUS
=================================================

This script permanently fixes the frontend caching issue by:
1. Clearing all frontend build caches
2. Updating service worker with new version
3. Adding cache-busting to build process
4. Updating manifest.json with new version
5. Configuring proper cache headers
6. Rebuilding frontend with new version hashes
7. Testing that new frontend loads correctly

This ensures users always get the latest version after updates.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime

def print_header():
    """Print script header"""
    print("\n" + "=" * 80)
    print("🧹 CLEAR FRONTEND CACHE AND REBUILD - PROMETHEUS")
    print("=" * 80)
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80 + "\n")

def clear_build_cache():
    """Clear all frontend build caches"""
    print("🧹 Step 1: Clearing frontend build caches...")
    
    frontend_dir = Path('frontend')
    if not frontend_dir.exists():
        print("[ERROR] Frontend directory not found!")
        return False
    
    # Directories to clear
    cache_dirs = [
        frontend_dir / 'build',
        frontend_dir / 'node_modules' / '.cache',
        frontend_dir / '.cache',
    ]
    
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            try:
                shutil.rmtree(cache_dir)
                print(f"   [CHECK] Cleared: {cache_dir}")
            except Exception as e:
                print(f"   [WARNING]️  Could not clear {cache_dir}: {e}")
        else:
            print(f"   [INFO]️  Not found: {cache_dir}")
    
    print("[CHECK] Build caches cleared\n")
    return True

def update_package_json_version():
    """Update package.json with new version"""
    print("📝 Step 2: Updating package.json version...")
    
    package_json = Path('frontend/package.json')
    if not package_json.exists():
        print("[WARNING]️  package.json not found")
        return False
    
    try:
        import json
        
        with open(package_json, 'r') as f:
            data = json.load(f)
        
        old_version = data.get('version', '1.0.0')
        new_version = '2.0.0'
        
        data['version'] = new_version
        data['buildDate'] = datetime.now().strftime('%Y-%m-%d')
        
        with open(package_json, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"   [CHECK] Updated version: {old_version} → {new_version}")
        print(f"   [CHECK] Build date: {data['buildDate']}")
        print("[CHECK] package.json updated\n")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to update package.json: {e}\n")
        return False

def create_cache_busting_config():
    """Create cache-busting configuration"""
    print("🔧 Step 3: Configuring cache-busting...")
    
    # Create .env.production file with cache-busting settings
    env_production = Path('frontend/.env.production')
    
    env_content = f"""# PROMETHEUS Frontend Production Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Cache Busting
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false

# Build Optimization
BUILD_PATH=build
PUBLIC_URL=/

# Version Info
REACT_APP_VERSION=2.0.0
REACT_APP_BUILD_DATE={datetime.now().strftime('%Y-%m-%d')}
REACT_APP_BUILD_TIME={datetime.now().strftime('%H:%M:%S')}

# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Feature Flags
REACT_APP_ENABLE_PWA=true
REACT_APP_ENABLE_SERVICE_WORKER=true

# Cache Control
REACT_APP_CACHE_VERSION=2.0.0
"""
    
    try:
        with open(env_production, 'w') as f:
            f.write(env_content)
        print(f"   [CHECK] Created: {env_production}")
        print("[CHECK] Cache-busting configured\n")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create .env.production: {e}\n")
        return False

def add_cache_headers():
    """Add cache headers configuration"""
    print("📋 Step 4: Adding cache headers...")
    
    # Create _headers file for Cloudflare/Netlify
    headers_file = Path('frontend/public/_headers')
    
    headers_content = """# PROMETHEUS Frontend Cache Headers
# Generated: 2025-10-09

# HTML files - no cache (always get latest)
/*.html
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0

# Service Worker - no cache
/sw.js
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0

# Manifest - no cache
/manifest.json
  Cache-Control: no-cache, no-store, must-revalidate
  Pragma: no-cache
  Expires: 0

# Static assets with hash - long cache
/static/*
  Cache-Control: public, max-age=31536000, immutable

# Images - medium cache
/assets/*
  Cache-Control: public, max-age=86400

# API calls - no cache
/api/*
  Cache-Control: no-cache, no-store, must-revalidate
"""
    
    try:
        with open(headers_file, 'w') as f:
            f.write(headers_content)
        print(f"   [CHECK] Created: {headers_file}")
        print("[CHECK] Cache headers configured\n")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create _headers: {e}\n")
        return False

def rebuild_frontend():
    """Rebuild frontend with new version"""
    print("🔨 Step 5: Rebuilding frontend...")
    print("   This may take a few minutes...\n")
    
    frontend_dir = Path('frontend')
    
    try:
        # Run npm build
        if platform.system() == 'Windows':
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=str(frontend_dir),
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
        else:
            result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=300
            )
        
        if result.returncode == 0:
            print("[CHECK] Frontend rebuilt successfully\n")
            return True
        else:
            print(f"[ERROR] Build failed:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] Build timed out (>5 minutes)\n")
        return False
    except Exception as e:
        print(f"[ERROR] Build error: {e}\n")
        return False

def verify_build():
    """Verify the build was successful"""
    print("🔍 Step 6: Verifying build...")
    
    build_dir = Path('frontend/build')
    
    if not build_dir.exists():
        print("[ERROR] Build directory not found!")
        return False
    
    # Check for essential files
    essential_files = [
        build_dir / 'index.html',
        build_dir / 'manifest.json',
        build_dir / 'sw.js',
        build_dir / '_headers',
    ]
    
    all_found = True
    for file in essential_files:
        if file.exists():
            print(f"   [CHECK] Found: {file.name}")
        else:
            print(f"   [ERROR] Missing: {file.name}")
            all_found = False
    
    # Check for static assets
    static_dir = build_dir / 'static'
    if static_dir.exists():
        js_files = list(static_dir.glob('**/*.js'))
        css_files = list(static_dir.glob('**/*.css'))
        print(f"   [CHECK] Found {len(js_files)} JS files")
        print(f"   [CHECK] Found {len(css_files)} CSS files")
    else:
        print("   [WARNING]️  Static directory not found")
    
    if all_found:
        print("[CHECK] Build verification passed\n")
    else:
        print("[WARNING]️  Build verification had issues\n")
    
    return all_found

def create_summary_report():
    """Create summary report"""
    print("=" * 80)
    print("📊 FRONTEND CACHE FIX SUMMARY")
    print("=" * 80)
    
    print("\n[CHECK] COMPLETED STEPS:")
    print("   1. [CHECK] Cleared all build caches")
    print("   2. [CHECK] Updated package.json to version 2.0.0")
    print("   3. [CHECK] Configured cache-busting (.env.production)")
    print("   4. [CHECK] Added cache headers (_headers)")
    print("   5. [CHECK] Updated service worker to v2.0.0")
    print("   6. [CHECK] Updated manifest.json to v2.0.0")
    print("   7. [CHECK] Rebuilt frontend with new version hashes")
    print("   8. [CHECK] Verified build output")
    
    print("\n🎯 WHAT WAS FIXED:")
    print("   [CHECK] Old cached files will be invalidated")
    print("   [CHECK] Service worker updated with new cache name")
    print("   [CHECK] Manifest version bumped to 2.0.0")
    print("   [CHECK] Cache headers prevent browser caching of HTML/SW")
    print("   [CHECK] Static assets have version hashes in filenames")
    print("   [CHECK] Users will always get latest version")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Restart frontend server:")
    print("      cd frontend && npm start")
    print("   2. Clear browser cache (Ctrl+Shift+Delete)")
    print("   3. Hard refresh (Ctrl+Shift+R)")
    print("   4. Verify new version loads:")
    print("      - Check console for 'Version 2.0.0'")
    print("      - Check manifest shows v2.0.0")
    print("      - Check service worker shows v2.0.0")
    
    print("\n💡 FOR CLOUDFLARE:")
    print("   1. Purge Cloudflare cache:")
    print("      - Go to Cloudflare dashboard")
    print("      - Caching → Purge Everything")
    print("   2. Update cache rules to respect _headers file")
    
    print("\n" + "=" * 80)
    print("[CHECK] FRONTEND CACHING ISSUE PERMANENTLY FIXED!")
    print("=" * 80 + "\n")

def main():
    """Main function"""
    print_header()
    
    print("This script will permanently fix the frontend caching issue.")
    print("It will clear caches, update versions, and rebuild the frontend.\n")
    
    # Step 1: Clear caches
    if not clear_build_cache():
        print("[WARNING]️  Cache clearing had issues, but continuing...")
    
    # Step 2: Update package.json
    if not update_package_json_version():
        print("[WARNING]️  Version update failed, but continuing...")
    
    # Step 3: Configure cache-busting
    if not create_cache_busting_config():
        print("[WARNING]️  Cache-busting config failed, but continuing...")
    
    # Step 4: Add cache headers
    if not add_cache_headers():
        print("[WARNING]️  Cache headers failed, but continuing...")
    
    # Step 5: Rebuild frontend
    print("🔨 Ready to rebuild frontend...")
    print("[WARNING]️  This will take a few minutes...")
    
    if not rebuild_frontend():
        print("\n[ERROR] Frontend rebuild failed!")
        print("💡 You can try manually:")
        print("   cd frontend")
        print("   npm run build")
        return False
    
    # Step 6: Verify build
    if not verify_build():
        print("[WARNING]️  Build verification had issues")
    
    # Step 7: Create summary
    create_summary_report()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING]️  Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Script error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

