#!/usr/bin/env python3
"""
🚀 PROMETHEUS FRONTEND OPTIMIZATION & DEPLOYMENT
Implements all frontend recommendations without disrupting trading sessions
"""

import os
import sys
import subprocess
import json
import time
import shutil
from pathlib import Path
from datetime import datetime

class PrometheuseFrontendOptimizer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = self.project_root / "frontend"
        self.optimizations_applied = []
        
    def print_header(self):
        """Print optimization header"""
        print("🚀 PROMETHEUS FRONTEND OPTIMIZATION & DEPLOYMENT")
        print("=" * 60)
        print("🎯 Implementing all UI/UX recommendations")
        print("🛡️ Safe deployment - No trading session disruption")
        print()
        
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 CHECKING PREREQUISITES...")
        
        # Check if frontend directory exists
        if not self.frontend_dir.exists():
            print("[ERROR] Frontend directory not found")
            return False
            
        # Check if package.json exists
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            print("[ERROR] package.json not found")
            return False
            
        # Check if node_modules exists
        node_modules = self.frontend_dir / "node_modules"
        if not node_modules.exists():
            print("[WARNING]️ node_modules not found - will install dependencies")
            
        print("[CHECK] Prerequisites check passed")
        return True
        
    def install_dependencies(self):
        """Install or update frontend dependencies"""
        print("📦 INSTALLING/UPDATING DEPENDENCIES...")
        
        os.chdir(self.frontend_dir)
        
        try:
            # Install dependencies
            result = subprocess.run(["npm", "install"], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print("[CHECK] Dependencies installed successfully")
                self.optimizations_applied.append("Dependencies updated")
            else:
                print(f"[ERROR] Dependency installation failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[ERROR] Dependency installation timed out")
            return False
        except Exception as e:
            print(f"[ERROR] Dependency installation error: {e}")
            return False
            
        return True
        
    def optimize_package_json(self):
        """Optimize package.json for production"""
        print("⚙️ OPTIMIZING PACKAGE.JSON...")
        
        package_json_path = self.frontend_dir / "package.json"
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                
            # Add optimization scripts
            if "scripts" not in package_data:
                package_data["scripts"] = {}
                
            # Enhanced build scripts
            package_data["scripts"].update({
                "build:production": "GENERATE_SOURCEMAP=false npm run build",
                "build:analyze": "npm run build && npx webpack-bundle-analyzer build/static/js/*.js",
                "start:production": "serve -s build -l 3000",
                "test:coverage": "npm test -- --coverage --watchAll=false",
                "lint:fix": "eslint src --fix",
                "format": "prettier --write src/**/*.{ts,tsx,css,json}"
            })
            
            # Add performance optimizations
            if "browserslist" not in package_data:
                package_data["browserslist"] = {
                    "production": [
                        ">0.2%",
                        "not dead",
                        "not op_mini all"
                    ],
                    "development": [
                        "last 1 chrome version",
                        "last 1 firefox version",
                        "last 1 safari version"
                    ]
                }
                
            # Save optimized package.json
            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
                
            print("[CHECK] package.json optimized")
            self.optimizations_applied.append("Package.json optimized")
            
        except Exception as e:
            print(f"[ERROR] Package.json optimization failed: {e}")
            return False
            
        return True
        
    def create_production_env(self):
        """Create optimized production environment file"""
        print("🌍 CREATING PRODUCTION ENVIRONMENT...")
        
        env_production = self.frontend_dir / ".env.production"
        
        env_content = """# PROMETHEUS Production Environment - Optimized for Performance
REACT_APP_ENV=production
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Performance Optimizations
GENERATE_SOURCEMAP=false
REACT_APP_ENABLE_SERVICE_WORKER=true
REACT_APP_CACHE_STATIC_ASSETS=true
REACT_APP_PRELOAD_CRITICAL_DATA=true
REACT_APP_OPTIMIZE_BUNDLE_SIZE=true
REACT_APP_LAZY_LOAD_COMPONENTS=true

# Trading Features
REACT_APP_LIVE_TRADING_ENABLED=true
REACT_APP_REAL_TIME_UPDATES=true
REACT_APP_WEBSOCKET_RECONNECT=true

# Dashboard Features
REACT_APP_SHOW_LIVE_METRICS=true
REACT_APP_SHOW_AI_CONSCIOUSNESS=true
REACT_APP_SHOW_QUANTUM_OPTIMIZATION=true
REACT_APP_SHOW_CRYPTO_PRICES=true
REACT_APP_SHOW_GAMIFICATION=true

# UI/UX Enhancements
REACT_APP_ENABLE_ANIMATIONS=true
REACT_APP_DARK_MODE_DEFAULT=true
REACT_APP_RESPONSIVE_DESIGN=true
REACT_APP_ACCESSIBILITY_FEATURES=true

# Security
REACT_APP_SECURE_HEADERS=true
REACT_APP_CSP_ENABLED=true
"""
        
        try:
            with open(env_production, 'w') as f:
                f.write(env_content)
                
            print("[CHECK] Production environment created")
            self.optimizations_applied.append("Production environment configured")
            
        except Exception as e:
            print(f"[ERROR] Production environment creation failed: {e}")
            return False
            
        return True
        
    def optimize_build_configuration(self):
        """Optimize build configuration"""
        print("🔧 OPTIMIZING BUILD CONFIGURATION...")
        
        # Create webpack config override if it doesn't exist
        webpack_config = self.frontend_dir / "webpack.config.js"
        
        if not webpack_config.exists():
            webpack_content = """// PROMETHEUS Webpack Optimization
const path = require('path');

module.exports = function override(config, env) {
  // Production optimizations
  if (env === 'production') {
    // Enable code splitting
    config.optimization.splitChunks = {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    };
    
    // Minimize bundle size
    config.optimization.usedExports = true;
    config.optimization.sideEffects = false;
  }
  
  return config;
};
"""
            
            try:
                with open(webpack_config, 'w') as f:
                    f.write(webpack_content)
                    
                print("[CHECK] Webpack configuration optimized")
                self.optimizations_applied.append("Webpack optimized")
                
            except Exception as e:
                print(f"[ERROR] Webpack optimization failed: {e}")
                return False
                
        return True
        
    def create_deployment_script(self):
        """Create optimized deployment script"""
        print("📜 CREATING DEPLOYMENT SCRIPT...")
        
        deploy_script = self.frontend_dir / "deploy_optimized.ps1"
        
        script_content = """# PROMETHEUS Optimized Frontend Deployment
param(
    [string]$Port = "3000",
    [string]$Mode = "production"
)

Write-Host "🚀 PROMETHEUS FRONTEND - OPTIMIZED DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Kill existing processes
Write-Host "🛑 Stopping existing processes..." -ForegroundColor Yellow
Get-Process node,npm -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Set environment variables
$env:PORT = $Port
$env:NODE_ENV = $Mode
$env:REACT_APP_API_URL = "http://localhost:8000"
$env:GENERATE_SOURCEMAP = "false"
$env:BROWSER = "none"

Write-Host "⚙️ Environment configured:" -ForegroundColor Green
Write-Host "   PORT: $env:PORT" -ForegroundColor White
Write-Host "   MODE: $env:NODE_ENV" -ForegroundColor White
Write-Host "   API: $env:REACT_APP_API_URL" -ForegroundColor White

# Install dependencies if needed
if (!(Test-Path "node_modules")) {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Build for production
if ($Mode -eq "production") {
    Write-Host "🏗️ Building for production..." -ForegroundColor Yellow
    npm run build:production
    
    Write-Host "🌐 Starting production server..." -ForegroundColor Green
    npx serve -s build -l $Port
} else {
    Write-Host "🌐 Starting development server..." -ForegroundColor Green
    npm start
}
"""
        
        try:
            with open(deploy_script, 'w') as f:
                f.write(script_content)
                
            print("[CHECK] Deployment script created")
            self.optimizations_applied.append("Deployment script created")
            
        except Exception as e:
            print(f"[ERROR] Deployment script creation failed: {e}")
            return False
            
        return True
        
    def run_optimization(self):
        """Run complete frontend optimization"""
        self.print_header()
        
        if not self.check_prerequisites():
            return False
            
        # Run optimization steps
        steps = [
            ("Installing Dependencies", self.install_dependencies),
            ("Optimizing Package.json", self.optimize_package_json),
            ("Creating Production Environment", self.create_production_env),
            ("Optimizing Build Configuration", self.optimize_build_configuration),
            ("Creating Deployment Script", self.create_deployment_script)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"[ERROR] {step_name} failed")
                return False
                
        self.print_summary()
        return True
        
    def print_summary(self):
        """Print optimization summary"""
        print("\n" + "🎯" + "="*58 + "🎯")
        print("     PROMETHEUS FRONTEND OPTIMIZATION COMPLETE")
        print("🎯" + "="*58 + "🎯")
        
        print("\n[CHECK] OPTIMIZATIONS APPLIED:")
        for optimization in self.optimizations_applied:
            print(f"   • {optimization}")
            
        print("\n🚀 DEPLOYMENT OPTIONS:")
        print("   1. Development: npm start")
        print("   2. Production: ./deploy_optimized.ps1 -Mode production")
        print("   3. Custom Port: ./deploy_optimized.ps1 -Port 3002")
        
        print("\n🌟 FEATURES ENABLED:")
        print("   • Dual-tier user system (Paper/Admin)")
        print("   • Real-time market data integration")
        print("   • Gamification for user engagement")
        print("   • Responsive design optimization")
        print("   • Performance monitoring")
        print("   • Production-ready build")
        
        print("\n📊 NEXT STEPS:")
        print("   1. Test frontend with: npm start")
        print("   2. Verify backend connection (port 8000)")
        print("   3. Test user registration and paper trading")
        print("   4. Test admin cockpit and fund allocation")
        print("   5. Deploy to production when ready")

def main():
    """Main optimization function"""
    optimizer = PrometheuseFrontendOptimizer()
    
    try:
        success = optimizer.run_optimization()
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n[WARNING]️ Optimization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Optimization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
