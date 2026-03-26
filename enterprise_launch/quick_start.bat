@echo off
REM 🚀 PROMETHEUS Trading Platform - Quick Start Script (Windows)
REM This script sets up and launches the complete trading platform

echo 🚀 PROMETHEUS Trading Platform - Enterprise Launch
echo ==================================================

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is required but not installed.
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is required but not installed.
    pause
    exit /b 1
)

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is required but not installed.
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Install backend dependencies
echo 📦 Installing backend dependencies...
pip install -r requirements.txt

REM Install frontend dependencies and build
echo 📦 Installing frontend dependencies...
cd frontend
call npm install
echo 🔨 Building frontend...
call npm run build
cd ..

REM Setup environment
if not exist .env (
    echo ⚙️ Setting up environment configuration...
    copy .env.template .env
    echo ✅ Environment file created (.env)
    echo 💡 You can edit .env to customize settings
)

REM Create launch scripts
echo 📝 Creating launch scripts...

REM Backend launch script
echo @echo off > start_backend.bat
echo echo 🚀 Starting PROMETHEUS Backend Server... >> start_backend.bat
echo python -m uvicorn unified_production_server:app --host 0.0.0.0 --port 8000 --reload >> start_backend.bat
echo pause >> start_backend.bat

REM Frontend launch script
echo @echo off > start_frontend.bat
echo echo 🌐 Starting PROMETHEUS Frontend Server... >> start_frontend.bat
echo cd frontend >> start_frontend.bat
echo npx serve -s build -p 3002 >> start_frontend.bat
echo pause >> start_frontend.bat

echo.
echo 🎉 PROMETHEUS Trading Platform Setup Complete!
echo ==============================================
echo.
echo 🚀 To start the platform:
echo 1. Backend:  start_backend.bat  (or: python -m uvicorn unified_production_server:app --host 0.0.0.0 --port 8000)
echo 2. Frontend: start_frontend.bat (or: cd frontend ^&^& npx serve -s build -p 3002)
echo.
echo 🌐 Access URLs:
echo • Admin Dashboard: http://localhost:3002/admin-dashboard
echo • Live Market:     http://localhost:3002/live-market  
echo • API Docs:        http://localhost:8000/docs
echo • Health Check:    http://localhost:8000/health
echo.
echo 📊 The platform includes:
echo • ✅ Real-time market data from Yahoo Finance
echo • ✅ Internal paper trading engine
echo • ✅ AI-powered trading signals
echo • ✅ Live admin dashboard
echo • ✅ WebSocket real-time updates
echo.
echo 🔧 Configuration:
echo • Edit .env file to customize settings
echo • Add API keys for enhanced features (optional)
echo.
echo 📞 Support:
echo • Check /health endpoint for system status
echo • View /docs for API documentation
echo • Check console logs for troubleshooting
echo.
echo Happy Trading! 📈
pause
