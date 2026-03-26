"""
Real-Time Risk Dashboard
Interactive web-based dashboard for live risk monitoring
Displays P&L, exposure, VaR, correlations, regime status
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np

# Dashboard framework
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logging.warning("⚠️ FastAPI not available - install with: pip install fastapi uvicorn websockets")

logger = logging.getLogger(__name__)

class RealTimeRiskDashboard:
    """
    Real-time risk monitoring dashboard
    WebSocket-based live updates
    """
    
    def __init__(self, port: int = 8050):
        self.port = port
        self.active_connections: List[WebSocket] = []
        
        if FASTAPI_AVAILABLE:
            self.app = FastAPI(title="PROMETHEUS Risk Dashboard")
            self._setup_routes()
        else:
            self.app = None
            logger.warning("⚠️ Dashboard disabled - FastAPI not available")
        
        # Risk metrics cache
        self.metrics_cache = {
            'pnl': {'current': 0.0, 'history': []},
            'positions': {},
            'risk_metrics': {},
            'regime': {'current': 'NORMAL', 'history': []},
            'alerts': []
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'max_drawdown': -0.10,  # -10%
            'daily_var_breach': 0.95,  # VaR 95%
            'position_concentration': 0.25,  # 25% in single position
            'leverage_limit': 2.0,
            'correlation_spike': 0.90
        }
        
        logger.info(f"✅ Real-Time Risk Dashboard initialized on port {self.port}")
    
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def get_dashboard():
            """Serve dashboard HTML"""
            return self._generate_dashboard_html()
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await websocket.accept()
            self.active_connections.append(websocket)
            
            try:
                while True:
                    # Send updates every second
                    await self._send_update(websocket)
                    await asyncio.sleep(1.0)
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                logger.info("Client disconnected from dashboard")
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current risk metrics"""
            return self.metrics_cache
        
        @self.app.get("/api/positions")
        async def get_positions():
            """Get current positions"""
            return self.metrics_cache['positions']
        
        @self.app.get("/api/alerts")
        async def get_alerts():
            """Get active alerts"""
            return self.metrics_cache['alerts']
    
    async def update_metrics(self, metrics: Dict[str, Any]):
        """
        Update dashboard metrics and broadcast to clients
        
        Args:
            metrics: Updated risk metrics
        """
        try:
            # Update cache
            self.metrics_cache.update(metrics)
            
            # Check for alerts
            alerts = self._check_alerts(metrics)
            if alerts:
                self.metrics_cache['alerts'].extend(alerts)
                logger.warning(f"⚠️ {len(alerts)} new alerts generated")
            
            # Broadcast to all connected clients
            await self._broadcast_update()
            
        except Exception as e:
            logger.error(f"Error updating dashboard metrics: {e}")
    
    async def update_pnl(self, pnl: float, timestamp: datetime = None):
        """Update P&L display"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        self.metrics_cache['pnl']['current'] = pnl
        self.metrics_cache['pnl']['history'].append({
            'timestamp': timestamp.isoformat(),
            'value': pnl
        })
        
        # Keep only last 1000 points
        if len(self.metrics_cache['pnl']['history']) > 1000:
            self.metrics_cache['pnl']['history'] = self.metrics_cache['pnl']['history'][-1000:]
        
        await self._broadcast_update()
    
    async def update_positions(self, positions: Dict[str, Any]):
        """Update positions display"""
        self.metrics_cache['positions'] = positions
        
        # Check concentration risk
        if positions:
            total_value = sum([abs(p.get('value', 0)) for p in positions.values()])
            for symbol, position in positions.items():
                concentration = abs(position.get('value', 0)) / total_value if total_value > 0 else 0
                if concentration > self.alert_thresholds['position_concentration']:
                    await self._add_alert('CONCENTRATION_RISK', 
                                         f"{symbol} position at {concentration:.1%} of portfolio")
        
        await self._broadcast_update()
    
    async def update_regime(self, regime: str, confidence: float):
        """Update market regime indicator"""
        self.metrics_cache['regime']['current'] = regime
        self.metrics_cache['regime']['confidence'] = confidence
        self.metrics_cache['regime']['history'].append({
            'timestamp': datetime.utcnow().isoformat(),
            'regime': regime,
            'confidence': confidence
        })
        
        # Regime change alert
        if len(self.metrics_cache['regime']['history']) > 1:
            previous = self.metrics_cache['regime']['history'][-2]
            if previous['regime'] != regime:
                await self._add_alert('REGIME_CHANGE', 
                                     f"Market regime changed: {previous['regime']} → {regime}")
        
        await self._broadcast_update()
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check metrics for alert conditions"""
        alerts = []
        
        # Drawdown alert
        if 'drawdown' in metrics and metrics['drawdown'] < self.alert_thresholds['max_drawdown']:
            alerts.append({
                'severity': 'HIGH',
                'type': 'DRAWDOWN',
                'message': f"Drawdown exceeded threshold: {metrics['drawdown']:.2%}",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # VaR breach
        if 'var_breach' in metrics and metrics['var_breach']:
            alerts.append({
                'severity': 'MEDIUM',
                'type': 'VAR_BREACH',
                'message': f"VaR threshold breached",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Leverage alert
        if 'leverage' in metrics and metrics['leverage'] > self.alert_thresholds['leverage_limit']:
            alerts.append({
                'severity': 'HIGH',
                'type': 'LEVERAGE',
                'message': f"Leverage at {metrics['leverage']:.2f}x (limit: {self.alert_thresholds['leverage_limit']:.2f}x)",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Correlation spike
        if 'avg_correlation' in metrics and metrics['avg_correlation'] > self.alert_thresholds['correlation_spike']:
            alerts.append({
                'severity': 'MEDIUM',
                'type': 'CORRELATION',
                'message': f"Portfolio correlation spiked to {metrics['avg_correlation']:.2%}",
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return alerts
    
    async def _add_alert(self, alert_type: str, message: str):
        """Add alert to dashboard"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'MEDIUM'
        }
        
        self.metrics_cache['alerts'].append(alert)
        
        # Keep only last 100 alerts
        if len(self.metrics_cache['alerts']) > 100:
            self.metrics_cache['alerts'] = self.metrics_cache['alerts'][-100:]
    
    async def _send_update(self, websocket: WebSocket):
        """Send update to specific websocket"""
        try:
            await websocket.send_json(self.metrics_cache)
        except Exception as e:
            logger.error(f"Error sending update: {e}")
    
    async def _broadcast_update(self):
        """Broadcast update to all connected clients"""
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_json(self.metrics_cache)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>PROMETHEUS Risk Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #0a0e27;
            color: #e0e0e0;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        h1 {
            color: white;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .metric-card {
            background: #1a1f3a;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid #2a3150;
        }
        
        .metric-card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #4ade80;
        }
        
        .metric-value.negative {
            color: #f87171;
        }
        
        .metric-label {
            color: #9ca3af;
            font-size: 0.9em;
            margin-top: 5px;
        }
        
        .positions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        
        .positions-table th {
            background: #2a3150;
            padding: 10px;
            text-align: left;
            color: #667eea;
        }
        
        .positions-table td {
            padding: 10px;
            border-bottom: 1px solid #2a3150;
        }
        
        .alert {
            background: #7f1d1d;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        
        .alert.medium {
            background: #78350f;
            border-left-color: #f59e0b;
        }
        
        .alert.low {
            background: #1e3a8a;
            border-left-color: #3b82f6;
        }
        
        .regime-indicator {
            display: inline-block;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 1.2em;
        }
        
        .regime-BULL {
            background: #22c55e;
            color: white;
        }
        
        .regime-BEAR {
            background: #ef4444;
            color: white;
        }
        
        .regime-NORMAL {
            background: #3b82f6;
            color: white;
        }
        
        .regime-VOLATILE {
            background: #f59e0b;
            color: white;
        }
        
        #chart {
            width: 100%;
            height: 300px;
            background: #0f1729;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-active {
            background: #22c55e;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 PROMETHEUS Real-Time Risk Dashboard</h1>
        <p><span class="status-indicator status-active"></span>Live Updates Active</p>
    </div>
    
    <div class="dashboard-grid">
        <div class="metric-card">
            <h2>📊 P&L</h2>
            <div class="metric-value" id="pnl">$0.00</div>
            <div class="metric-label">Current P&L</div>
        </div>
        
        <div class="metric-card">
            <h2>📈 Daily Return</h2>
            <div class="metric-value" id="daily-return">0.00%</div>
            <div class="metric-label">Today's Performance</div>
        </div>
        
        <div class="metric-card">
            <h2>⚡ Market Regime</h2>
            <div id="regime-indicator">
                <span class="regime-indicator regime-NORMAL">NORMAL</span>
            </div>
            <div class="metric-label">Current Market State</div>
        </div>
        
        <div class="metric-card">
            <h2>🎯 Sharpe Ratio</h2>
            <div class="metric-value" id="sharpe">2.50</div>
            <div class="metric-label">Risk-Adjusted Returns</div>
        </div>
        
        <div class="metric-card">
            <h2>📉 Max Drawdown</h2>
            <div class="metric-value negative" id="drawdown">-5.2%</div>
            <div class="metric-label">Current Drawdown</div>
        </div>
        
        <div class="metric-card">
            <h2>⚖️ Leverage</h2>
            <div class="metric-value" id="leverage">1.2x</div>
            <div class="metric-label">Current Leverage</div>
        </div>
    </div>
    
    <div class="metric-card">
        <h2>📊 Active Positions</h2>
        <table class="positions-table">
            <thead>
                <tr>
                    <th>Symbol</th>
                    <th>Quantity</th>
                    <th>Entry Price</th>
                    <th>Current Price</th>
                    <th>P&L</th>
                </tr>
            </thead>
            <tbody id="positions-body">
                <tr>
                    <td colspan="5" style="text-align: center; color: #9ca3af;">No active positions</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div class="metric-card">
        <h2>🚨 Active Alerts</h2>
        <div id="alerts-container">
            <p style="color: #9ca3af;">No active alerts</p>
        </div>
    </div>
    
    <script>
        const ws = new WebSocket(`ws://${window.location.host}/ws`);
        
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };
        
        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        function updateDashboard(data) {
            // Update P&L
            if (data.pnl && data.pnl.current !== undefined) {
                const pnlElement = document.getElementById('pnl');
                const pnl = data.pnl.current;
                pnlElement.textContent = formatCurrency(pnl);
                pnlElement.className = 'metric-value ' + (pnl >= 0 ? '' : 'negative');
            }
            
            // Update regime
            if (data.regime && data.regime.current) {
                const regimeElement = document.getElementById('regime-indicator');
                const regime = data.regime.current;
                regimeElement.innerHTML = `<span class="regime-indicator regime-${regime}">${regime}</span>`;
            }
            
            // Update positions
            if (data.positions) {
                updatePositionsTable(data.positions);
            }
            
            // Update alerts
            if (data.alerts && data.alerts.length > 0) {
                updateAlerts(data.alerts);
            }
        }
        
        function updatePositionsTable(positions) {
            const tbody = document.getElementById('positions-body');
            
            if (Object.keys(positions).length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #9ca3af;">No active positions</td></tr>';
                return;
            }
            
            let html = '';
            for (const [symbol, position] of Object.entries(positions)) {
                const pnl = position.pnl || 0;
                const pnlClass = pnl >= 0 ? '' : 'negative';
                
                html += `
                    <tr>
                        <td>${symbol}</td>
                        <td>${position.quantity || 0}</td>
                        <td>${formatCurrency(position.entry_price || 0)}</td>
                        <td>${formatCurrency(position.current_price || 0)}</td>
                        <td class="${pnlClass}">${formatCurrency(pnl)}</td>
                    </tr>
                `;
            }
            
            tbody.innerHTML = html;
        }
        
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            
            if (alerts.length === 0) {
                container.innerHTML = '<p style="color: #9ca3af;">No active alerts</p>';
                return;
            }
            
            let html = '';
            // Show last 5 alerts
            const recentAlerts = alerts.slice(-5).reverse();
            
            for (const alert of recentAlerts) {
                const severity = (alert.severity || 'MEDIUM').toLowerCase();
                html += `
                    <div class="alert ${severity}">
                        <strong>${alert.type}</strong>: ${alert.message}
                        <br><small>${new Date(alert.timestamp).toLocaleString()}</small>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(value);
        }
        
        // Initialize
        console.log('PROMETHEUS Risk Dashboard initialized');
    </script>
</body>
</html>
        """
    
    async def start(self):
        """Start dashboard server"""
        if not FASTAPI_AVAILABLE:
            logger.error("Cannot start dashboard - FastAPI not available")
            return
        
        try:
            import uvicorn
            logger.info(f"🚀 Starting Risk Dashboard on http://localhost:{self.port}")
            config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
            
        except ImportError:
            logger.error("uvicorn not available - install with: pip install uvicorn")
        except Exception as e:
            logger.error(f"Error starting dashboard: {e}")


# Global dashboard instance
_dashboard = None

def get_dashboard(port: int = 8050) -> RealTimeRiskDashboard:
    """Get or create global dashboard"""
    global _dashboard
    if _dashboard is None:
        _dashboard = RealTimeRiskDashboard(port=port)
    return _dashboard


async def main():
    """Run dashboard standalone"""
    dashboard = get_dashboard()
    await dashboard.start()


if __name__ == "__main__":
    asyncio.run(main())
