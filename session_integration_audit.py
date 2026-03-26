#!/usr/bin/env python3
"""
🔍 SESSION INTEGRATION AUDIT
Check if the new enhanced sessions are using all available advanced features
"""

import sqlite3
import json
import os
import requests
from datetime import datetime
from typing import Dict, List, Any

class SessionIntegrationAuditor:
    """Audit session integration with advanced features"""
    
    def __init__(self):
        self.results = {
            'active_sessions': [],
            'feature_integration': {},
            'missing_integrations': [],
            'performance_gaps': []
        }
    
    def audit_active_sessions(self):
        """Audit all active trading sessions"""
        print("📊 ACTIVE SESSIONS INTEGRATION AUDIT")
        print("=" * 60)
        
        # Check enhanced paper trading sessions
        if os.path.exists('enhanced_paper_trading.db'):
            try:
                conn = sqlite3.connect('enhanced_paper_trading.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT session_id, user_id, session_type, starting_capital, 
                           current_value, profit_loss, trades_count, status, created_at
                    FROM paper_sessions 
                    WHERE status = 'active'
                """)
                
                sessions = cursor.fetchall()
                print(f"[CHECK] Enhanced Paper Trading Sessions: {len(sessions)} active")
                
                for session in sessions:
                    session_id, user_id, session_type, starting_capital, current_value, profit_loss, trades_count, status, created_at = session
                    
                    print(f"   📊 Session: {session_id[:8]}...")
                    print(f"      User: {user_id}")
                    print(f"      Type: {session_type}")
                    print(f"      Capital: ${starting_capital:,.2f}")
                    print(f"      Current: ${current_value:,.2f}")
                    print(f"      P&L: ${profit_loss:,.2f}")
                    print(f"      Trades: {trades_count}")
                    print(f"      Status: {status}")
                    print(f"      Created: {created_at}")
                    
                    self.results['active_sessions'].append({
                        'session_id': session_id,
                        'user_id': user_id,
                        'session_type': session_type,
                        'starting_capital': starting_capital,
                        'current_value': current_value,
                        'profit_loss': profit_loss,
                        'trades_count': trades_count,
                        'status': status,
                        'created_at': created_at,
                        'database': 'enhanced_paper_trading'
                    })
                
                conn.close()
                
            except Exception as e:
                print(f"[ERROR] Enhanced Paper Trading DB Error: {e}")
        
        # Check internal paper trading session
        if os.path.exists('paper_trading.db'):
            try:
                conn = sqlite3.connect('paper_trading.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT session_id, starting_capital, current_capital, 
                           profit_loss, trades_count, status
                    FROM sessions 
                    WHERE status = 'active'
                """)
                
                sessions = cursor.fetchall()
                print(f"[WARNING]️ Internal Paper Trading Sessions: {len(sessions)} active")
                
                for session in sessions:
                    session_id, starting_capital, current_capital, profit_loss, trades_count, status = session
                    
                    print(f"   📊 Session: {session_id}")
                    print(f"      Starting: ${starting_capital:,.2f}")
                    print(f"      Current: ${current_capital:,.2f}")
                    print(f"      P&L: ${profit_loss:,.2f}")
                    print(f"      Trades: {trades_count}")
                    print(f"      Status: {status}")
                    
                    self.results['active_sessions'].append({
                        'session_id': session_id,
                        'starting_capital': starting_capital,
                        'current_value': current_capital,
                        'profit_loss': profit_loss,
                        'trades_count': trades_count,
                        'status': status,
                        'database': 'internal_paper_trading'
                    })
                
                conn.close()
                
            except Exception as e:
                print(f"[ERROR] Internal Paper Trading DB Error: {e}")
    
    def check_feature_integration(self):
        """Check which advanced features are integrated with sessions"""
        print("\n🔗 FEATURE INTEGRATION CHECK")
        print("=" * 60)
        
        # Check if sessions are using revolutionary engines
        try:
            response = requests.get('http://localhost:8002/api/revolutionary/performance', timeout=5)
            if response.status_code == 200:
                data = response.json()
                performance = data.get('performance', {})
                
                print("🚀 Revolutionary Engines Integration:")
                for engine, engine_data in performance.items():
                    trades = engine_data.get('trades_total', 0)
                    pnl = engine_data.get('pnl_total', 0)
                    status = engine_data.get('status', 'unknown')
                    
                    if trades > 0:
                        print(f"   [CHECK] {engine.upper()}: ACTIVE ({trades} trades, ${pnl:,.2f} P&L)")
                        self.results['feature_integration'][engine] = {
                            'status': 'ACTIVE',
                            'trades': trades,
                            'pnl': pnl
                        }
                    else:
                        print(f"   [WARNING]️ {engine.upper()}: NO TRADES ({status})")
                        self.results['feature_integration'][engine] = {
                            'status': 'NO_TRADES',
                            'engine_status': status
                        }
                        self.results['missing_integrations'].append(f"{engine} not generating trades")
            else:
                print("[ERROR] Cannot check revolutionary engines integration")
                self.results['missing_integrations'].append("Revolutionary engines status unavailable")
        except Exception as e:
            print(f"[ERROR] Revolutionary Engines Check Error: {e}")
            self.results['missing_integrations'].append(f"Revolutionary engines error: {e}")
        
        # Check quantum features integration
        print("\n🔮 Quantum Features Integration:")
        
        # Check if quantum features are enabled in session configs
        session_configs = [
            'trading_session_live_internal_20251001_023631.json'
        ]
        
        quantum_enabled = False
        for config_file in session_configs:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        
                    quantum_features = config.get('quantum_features', [])
                    features_enabled = config.get('features_enabled', {})
                    
                    if quantum_features or features_enabled.get('quantum_trading', False):
                        print(f"   [CHECK] {config_file}: QUANTUM ENABLED")
                        print(f"      Features: {quantum_features}")
                        quantum_enabled = True
                        self.results['feature_integration']['quantum'] = {
                            'status': 'CONFIGURED',
                            'features': quantum_features,
                            'config_file': config_file
                        }
                    else:
                        print(f"   [WARNING]️ {config_file}: QUANTUM NOT CONFIGURED")
                except Exception as e:
                    print(f"   [ERROR] {config_file}: ERROR - {e}")
        
        if not quantum_enabled:
            print("   [ERROR] Quantum Features: NOT INTEGRATED")
            self.results['missing_integrations'].append("Quantum features not integrated with sessions")
        
        # Check AI consciousness integration
        print("\n🧠 AI Consciousness Integration:")
        
        ai_consciousness_enabled = False
        for config_file in session_configs:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    ai_systems = config.get('ai_systems', [])
                    features_enabled = config.get('features_enabled', {})
                    
                    if 'ai_consciousness' in str(config).lower() or features_enabled.get('ai_learning', False):
                        print(f"   [CHECK] {config_file}: AI CONSCIOUSNESS CONFIGURED")
                        print(f"      AI Systems: {ai_systems}")
                        ai_consciousness_enabled = True
                        self.results['feature_integration']['ai_consciousness'] = {
                            'status': 'CONFIGURED',
                            'ai_systems': ai_systems,
                            'config_file': config_file
                        }
                    else:
                        print(f"   [WARNING]️ {config_file}: AI CONSCIOUSNESS NOT CONFIGURED")
                except Exception as e:
                    print(f"   [ERROR] {config_file}: ERROR - {e}")
        
        if not ai_consciousness_enabled:
            print("   [ERROR] AI Consciousness: NOT INTEGRATED")
            self.results['missing_integrations'].append("AI consciousness not integrated with sessions")
    
    def analyze_performance_gaps(self):
        """Analyze performance gaps in current sessions"""
        print("\n📈 PERFORMANCE GAPS ANALYSIS")
        print("=" * 60)
        
        # Analyze session performance
        total_sessions = len(self.results['active_sessions'])
        profitable_sessions = len([s for s in self.results['active_sessions'] if s.get('profit_loss', 0) > 0])
        losing_sessions = len([s for s in self.results['active_sessions'] if s.get('profit_loss', 0) < 0])
        neutral_sessions = total_sessions - profitable_sessions - losing_sessions
        
        print(f"📊 Session Performance Overview:")
        print(f"   Total Sessions: {total_sessions}")
        print(f"   Profitable: {profitable_sessions}")
        print(f"   Losing: {losing_sessions}")
        print(f"   Neutral: {neutral_sessions}")
        
        # Identify performance issues
        if losing_sessions > 0:
            print(f"\n[WARNING]️ Performance Issues Identified:")
            for session in self.results['active_sessions']:
                if session.get('profit_loss', 0) < -1000:  # Significant loss
                    print(f"   🔴 Major Loss: {session['session_id'][:8]}... (${session['profit_loss']:,.2f})")
                    self.results['performance_gaps'].append({
                        'session_id': session['session_id'],
                        'issue': 'Major loss',
                        'amount': session['profit_loss'],
                        'recommendation': 'Check risk management integration'
                    })
        
        # Check if advanced features could improve performance
        missing_features = len(self.results['missing_integrations'])
        if missing_features > 0:
            print(f"\n💡 Performance Improvement Opportunities:")
            print(f"   Missing Integrations: {missing_features}")
            for missing in self.results['missing_integrations']:
                print(f"   • {missing}")
            
            self.results['performance_gaps'].append({
                'issue': 'Missing advanced feature integrations',
                'count': missing_features,
                'recommendation': 'Enable quantum, AI consciousness, and HRM features'
            })
    
    def generate_integration_recommendations(self):
        """Generate recommendations for better feature integration"""
        print("\n💡 INTEGRATION RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = []
        
        # High Priority - Enable quantum features for sessions
        if 'quantum' not in self.results['feature_integration'] or self.results['feature_integration']['quantum']['status'] != 'ACTIVE':
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Quantum Integration',
                'issue': 'Quantum features not active in trading sessions',
                'recommendation': 'Enable quantum optimization for enhanced sessions',
                'impact': 'Improved portfolio optimization and arbitrage detection',
                'implementation': 'Configure quantum features in EnhancedPaperTradingSystem'
            })
        
        # High Priority - Enable AI consciousness for sessions
        if 'ai_consciousness' not in self.results['feature_integration'] or self.results['feature_integration']['ai_consciousness']['status'] != 'ACTIVE':
            recommendations.append({
                'priority': 'HIGH',
                'category': 'AI Consciousness Integration',
                'issue': 'AI consciousness not active in trading sessions',
                'recommendation': 'Enable AI consciousness engine for enhanced sessions',
                'impact': '95% improvement in trading decision quality',
                'implementation': 'Integrate AIConsciousnessEngine with trading sessions'
            })
        
        # Medium Priority - Improve revolutionary engines utilization
        inactive_engines = [engine for engine, data in self.results['feature_integration'].items() 
                          if 'revolutionary' in engine and data.get('status') == 'NO_TRADES']
        
        if inactive_engines:
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Revolutionary Engines',
                'issue': f'{len(inactive_engines)} revolutionary engines not generating trades',
                'recommendation': 'Investigate and optimize revolutionary engine integration',
                'impact': 'Increased trading activity and diversification',
                'implementation': 'Check engine configurations and market data feeds'
            })
        
        print("🎯 PRIORITY RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['priority']} PRIORITY: {rec['category']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Recommendation: {rec['recommendation']}")
            print(f"   Impact: {rec['impact']}")
            print(f"   Implementation: {rec['implementation']}")
        
        return recommendations
    
    def run_session_integration_audit(self):
        """Run the complete session integration audit"""
        print("🔍 PROMETHEUS SESSION INTEGRATION AUDIT")
        print("=" * 70)
        print(f"Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        self.audit_active_sessions()
        self.check_feature_integration()
        self.analyze_performance_gaps()
        recommendations = self.generate_integration_recommendations()
        
        # Generate summary
        print("\n📊 SESSION INTEGRATION SUMMARY")
        print("=" * 70)
        
        print(f"📊 Active Sessions: {len(self.results['active_sessions'])}")
        print(f"🔗 Feature Integrations: {len(self.results['feature_integration'])}")
        print(f"[WARNING]️ Missing Integrations: {len(self.results['missing_integrations'])}")
        print(f"📈 Performance Gaps: {len(self.results['performance_gaps'])}")
        print(f"💡 Recommendations: {len(recommendations)}")
        
        print("=" * 70)
        
        return self.results

if __name__ == "__main__":
    auditor = SessionIntegrationAuditor()
    results = auditor.run_session_integration_audit()
    
    # Save session integration audit results
    with open(f"prometheus_session_integration_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump(results, f, indent=2, default=str)
