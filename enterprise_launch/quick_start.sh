#!/bin/bash
# 🚀 PROMETHEUS Trading Platform - Quick Start Script
# This script sets up and launches the complete trading platform

set -e

echo "🚀 PROMETHEUS Trading Platform - Enterprise Launch"
echo "=================================================="

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

# Check pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies and build
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
echo "🔨 Building frontend..."
npm run build
cd ..

# Setup environment
if [ ! -f .env ]; then
    echo "⚙️ Setting up environment configuration..."
    cp .env.template .env
    echo "✅ Environment file created (.env)"
    echo "💡 You can edit .env to customize settings"
fi

# Create launch scripts
echo "📝 Creating launch scripts..."

# Backend launch script
cat > start_backend.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting PROMETHEUS Backend Server..."
python -m uvicorn unified_production_server:app --host 0.0.0.0 --port 8000 --reload
EOF

# Frontend launch script  
cat > start_frontend.sh << 'EOF'
#!/bin/bash
echo "🌐 Starting PROMETHEUS Frontend Server..."
cd frontend
npx serve -s build -p 3002
EOF

# Make scripts executable
chmod +x start_backend.sh
chmod +x start_frontend.sh

echo ""
echo "🎉 PROMETHEUS Trading Platform Setup Complete!"
echo "=============================================="
echo ""
echo "🚀 To start the platform:"
echo "1. Backend:  ./start_backend.sh  (or: python -m uvicorn unified_production_server:app --host 0.0.0.0 --port 8000)"
echo "2. Frontend: ./start_frontend.sh (or: cd frontend && npx serve -s build -p 3002)"
echo ""
echo "🌐 Access URLs:"
echo "• Admin Dashboard: http://localhost:3002/admin-dashboard"
echo "• Live Market:     http://localhost:3002/live-market"
echo "• API Docs:        http://localhost:8000/docs"
echo "• Health Check:    http://localhost:8000/health"
echo ""
echo "📊 The platform includes:"
echo "• ✅ Real-time market data from Yahoo Finance"
echo "• ✅ Internal paper trading engine"
echo "• ✅ AI-powered trading signals"
echo "• ✅ Live admin dashboard"
echo "• ✅ WebSocket real-time updates"
echo ""
echo "🔧 Configuration:"
echo "• Edit .env file to customize settings"
echo "• Add API keys for enhanced features (optional)"
echo ""
echo "📞 Support:"
echo "• Check /health endpoint for system status"
echo "• View /docs for API documentation"
echo "• Check console logs for troubleshooting"
echo ""
echo "Happy Trading! 📈"
