#!/bin/bash
echo "🚀 Starting PROMETHEUS Trading Platform..."

# Start Backend Server
echo "📡 Starting Backend (Port 8001)..."
cd PROMETHEUS-Trading-Platform
python -m uvicorn unified_production_server:app --host 0.0.0.0 --port 8001 &

# Start Frontend
echo "🌐 Starting Frontend (Port 3000)..."
cd frontend
npm install
npm start &

echo "✅ PROMETHEUS Trading Platform is starting..."
echo "🔗 Backend: http://localhost:8001"
echo "🔗 Frontend: http://localhost:3000"
echo "🔑 Login: admin / admin123"
