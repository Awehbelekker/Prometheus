#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Deployment Package Creator
Creates a complete, portable installation package
"""

import os
import sys
import zipfile
import shutil
import json
from pathlib import Path
from datetime import datetime

def create_deployment_package():
    """Create complete deployment package"""
    
    print("📦 Creating PROMETHEUS Trading Platform Deployment Package")
    print("=" * 65)
    print()
    
    # Define source and target
    source_dir = Path.cwd()
    package_name = f"PROMETHEUS-Trading-Platform-v2.0-{datetime.now().strftime('%Y%m%d')}"
    package_dir = Path.cwd().parent / package_name
    zip_file = Path.cwd().parent / f"{package_name}.zip"
    
    # Clean up previous package
    if package_dir.exists():
        shutil.rmtree(package_dir)
    if zip_file.exists():
        zip_file.unlink()
    
    print(f"📁 Creating package directory: {package_dir}")
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Core files to include
    core_files = [
        "prometheus_universal_installer.py",
        "unified_production_server.py", 
        "requirements.txt",
        ".env.template",
        "README.md",
        "INSTALLATION.md",
        "VERSION",
        "prometheus_config.json",
        "GPT_OSS_INTEGRATION_STATUS.md",
        "ADVANCED_FEATURES_COMPLETE.md"
    ]
    
    # Core directories to include
    core_dirs = [
        "core",
        "frontend", 
        "revolutionary_features",
        "scripts",
        "docs",
        "config"
    ]
    
    # Copy core files
    print("📄 Copying core files...")
    for file_name in core_files:
        src_file = source_dir / file_name
        if src_file.exists():
            shutil.copy2(src_file, package_dir / file_name)
            print(f"[CHECK] {file_name}")
        else:
            print(f"[WARNING]️  {file_name} - not found")
    
    # Copy core directories
    print("\n📁 Copying core directories...")
    for dir_name in core_dirs:
        src_dir = source_dir / dir_name
        if src_dir.exists():
            shutil.copytree(src_dir, package_dir / dir_name, 
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'node_modules'))
            print(f"[CHECK] {dir_name}/")
        else:
            print(f"[WARNING]️  {dir_name}/ - not found")
    
    # Create startup scripts for different platforms
    print("\n🚀 Creating platform-specific startup scripts...")
    
    # Windows batch file
    windows_startup = f'''@echo off
title PROMETHEUS Trading Platform v2.0
echo ========================================
echo PROMETHEUS Trading Platform v2.0
echo Enterprise Trading System
echo ========================================
echo.

echo Installing PROMETHEUS Trading Platform...
python prometheus_universal_installer.py

echo.
echo Installation complete!
echo.
echo To start PROMETHEUS:
echo   cd PROMETHEUS-Trading-Platform
echo   start_prometheus.bat
echo.
pause
'''
    
    with open(package_dir / "INSTALL_WINDOWS.bat", "w", encoding='utf-8') as f:
        f.write(windows_startup)
    
    # Linux/macOS shell script
    unix_startup = f'''#!/bin/bash
echo "========================================"
echo "PROMETHEUS Trading Platform v2.0"
echo "Enterprise Trading System"
echo "========================================"
echo ""

echo "Installing PROMETHEUS Trading Platform..."
python3 prometheus_universal_installer.py

echo ""
echo "Installation complete!"
echo ""
echo "To start PROMETHEUS:"
echo "  cd PROMETHEUS-Trading-Platform"
echo "  ./start_prometheus.sh"
echo ""
read -p "Press Enter to continue..."
'''
    
    unix_script = package_dir / "INSTALL_UNIX.sh"
    with open(unix_script, "w", encoding='utf-8') as f:
        f.write(unix_startup)
    os.chmod(unix_script, 0o755)
    
    # PowerShell script
    powershell_startup = f'''# PROMETHEUS Trading Platform v2.0 - PowerShell Installer
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PROMETHEUS Trading Platform v2.0" -ForegroundColor Yellow
Write-Host "Enterprise Trading System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installing PROMETHEUS Trading Platform..." -ForegroundColor Green
python prometheus_universal_installer.py

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start PROMETHEUS:" -ForegroundColor Yellow
Write-Host "  cd PROMETHEUS-Trading-Platform"
Write-Host "  .\\start_prometheus.bat"
Write-Host ""
Read-Host "Press Enter to continue"
'''
    
    with open(package_dir / "INSTALL_POWERSHELL.ps1", "w", encoding='utf-8') as f:
        f.write(powershell_startup)
    
    print("[CHECK] INSTALL_WINDOWS.bat")
    print("[CHECK] INSTALL_UNIX.sh") 
    print("[CHECK] INSTALL_POWERSHELL.ps1")
    
    # Create deployment info
    deployment_info = {
        "package_name": package_name,
        "version": "2.0.0",
        "created_date": datetime.now().isoformat(),
        "platform": "Universal (Windows/Linux/macOS)",
        "python_requirement": "3.8+",
        "features": [
            "Quantum Trading Engine (50 qubits)",
            "Advanced AI Reasoning System", 
            "GPT-OSS Integration (20B/120B models)",
            "Revolutionary Trading Features",
            "Enterprise Security Framework",
            "Real-time Portfolio Optimization",
            "Multi-strategy Market Analysis"
        ],
        "installation_methods": [
            "INSTALL_WINDOWS.bat - Windows Batch",
            "INSTALL_UNIX.sh - Linux/macOS Shell", 
            "INSTALL_POWERSHELL.ps1 - PowerShell",
            "python prometheus_universal_installer.py - Direct"
        ],
        "quick_start": [
            "1. Extract package to desired location",
            "2. Run appropriate installer for your platform",
            "3. Navigate to PROMETHEUS-Trading-Platform directory",
            "4. Run startup script (start_prometheus.bat/sh)",
            "5. Access http://localhost:8000 for backend",
            "6. Access http://localhost:3000 for frontend"
        ]
    }
    
    with open(package_dir / "DEPLOYMENT_INFO.json", "w", encoding='utf-8') as f:
        json.dump(deployment_info, f, indent=2)
    
    # Create quick README for the package
    package_readme = f'''# PROMETHEUS Trading Platform v2.0 - Deployment Package

## Universal Installation Package

This package contains everything needed to install and run the complete PROMETHEUS Trading Platform on any system.

### Quick Installation

**Windows:**
```batch
INSTALL_WINDOWS.bat
```

**Linux/macOS:**
```bash
chmod +x INSTALL_UNIX.sh
./INSTALL_UNIX.sh
```

**PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\\INSTALL_POWERSHELL.ps1
```

**Manual Installation:**
```bash
python prometheus_universal_installer.py
```

### What's Included

- Complete PROMETHEUS Trading Platform v2.0
- Quantum Trading Engine (50 qubits)
- Advanced AI Reasoning System
- GPT-OSS Integration Framework
- Revolutionary Trading Features  
- Enterprise Security & Authentication
- React Frontend Interface
- FastAPI Backend Server
- SQLite Database with Mass Framework
- Complete Documentation

### System Requirements

- **Python**: 3.8+ (3.11+ recommended)
- **RAM**: 8GB minimum (32GB for GPT-OSS)
- **Storage**: 10GB minimum (50GB for GPT-OSS)
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+

### After Installation

1. Navigate to `PROMETHEUS-Trading-Platform` directory
2. Run the startup script:
   - Windows: `start_prometheus.bat`
   - Linux/macOS: `./start_prometheus.sh`
3. Access the platform:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

### Documentation

- `README.md` - Complete feature overview
- `INSTALLATION.md` - Detailed setup guide
- `GPT_OSS_INTEGRATION_STATUS.md` - AI integration status
- `DEPLOYMENT_INFO.json` - Package information

### Enterprise Features

- Multi-strategy AI market analysis
- Quantum-enhanced portfolio optimization
- Real-time trading signals
- Advanced risk management
- JWT authentication
- Audit logging
- Role-based access control

---

**Package Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**  
**Version: 2.0.0**  
**The future of trading is in this package!**
'''
    
    with open(package_dir / "PACKAGE_README.md", "w", encoding='utf-8') as f:
        f.write(package_readme)
    
    print("\n📝 Creating package documentation...")
    print("[CHECK] DEPLOYMENT_INFO.json")
    print("[CHECK] PACKAGE_README.md")
    
    # Create the ZIP package
    print(f"\n📦 Creating ZIP package: {zip_file}")
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            # Skip __pycache__ and other unwanted directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
            
            for file in files:
                if not file.endswith(('.pyc', '.pyo', '.log')):
                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(package_dir.parent)
                    zipf.write(file_path, arc_name)
    
    # Get package size
    zip_size = zip_file.stat().st_size / (1024 * 1024)  # MB
    
    print(f"[CHECK] ZIP package created: {zip_size:.1f} MB")
    
    # Cleanup temporary directory
    print(f"\n🧹 Cleaning up temporary files...")
    shutil.rmtree(package_dir)
    print("[CHECK] Cleanup complete")
    
    # Final summary
    print("\n" + "=" * 65)
    print("🎉 DEPLOYMENT PACKAGE CREATED SUCCESSFULLY!")
    print("=" * 65)
    print(f"📦 Package Name: {package_name}")
    print(f"📁 Package File: {zip_file}")
    print(f"📊 Package Size: {zip_size:.1f} MB")
    print(f"🗓️  Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("🚀 Distribution Instructions:")
    print("1. Share the ZIP file with target systems")
    print("2. Extract ZIP to desired location") 
    print("3. Run appropriate installer:")
    print("   • Windows: INSTALL_WINDOWS.bat")
    print("   • Linux/macOS: INSTALL_UNIX.sh")
    print("   • PowerShell: INSTALL_POWERSHELL.ps1")
    print("4. Follow installation prompts")
    print("5. Access platform at http://localhost:8000")
    print()
    print("✨ This package contains the complete PROMETHEUS Trading Platform")
    print("   with all enterprise features and AI capabilities!")
    print("=" * 65)
    
    return zip_file

if __name__ == "__main__":
    try:
        package_file = create_deployment_package()
        print(f"\n🎯 Ready for deployment: {package_file}")
    except Exception as e:
        print(f"\n[ERROR] Package creation failed: {e}")
        sys.exit(1)
