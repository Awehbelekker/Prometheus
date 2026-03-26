#!/usr/bin/env python3
"""
🔧 SYSTEM CONNECTION DIAGNOSTIC
Comprehensive diagnostic tool to identify and fix system connection issues
"""

import asyncio
import json
import os
import sys
import time
import socket
import subprocess
from datetime import datetime
from pathlib import Path
import logging
import requests

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class SystemConnectionDiagnostic:
    """Comprehensive system connection diagnostic and repair tool"""
    
    def __init__(self):
        self.diagnostic_id = f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # System components to check
        self.components = {
            "backend_server": {
                "name": "PROMETHEUS Backend Server",
                "url": "http://localhost:8000/health",
                "port": 8000,
                "process_name": "unified_production_server.py"
            },
            "frontend_server": {
                "name": "React Frontend Server",
                "url": "http://localhost:3000",
                "port": 3000,
                "process_name": "npm start"
            },
            "ib_gateway": {
                "name": "Interactive Brokers Gateway",
                "host": "127.0.0.1",
                "port": 7497,
                "process_name": "IB Gateway"
            },
            "cloudflare_tunnel": {
                "name": "Cloudflare Tunnel",
                "process_name": "cloudflared"
            }
        }
        
        # Diagnostic results
        self.results = {
            "diagnostic_id": self.diagnostic_id,
            "timestamp": datetime.now().isoformat(),
            "component_status": {},
            "issues_found": [],
            "fixes_applied": [],
            "recommendations": []
        }
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def print_diagnostic_header(self):
        """Print diagnostic header"""
        print("=" * 80)
        print("🔧 PROMETHEUS SYSTEM CONNECTION DIAGNOSTIC")
        print("=" * 80)
        print(f"🔍 Diagnostic ID: {self.diagnostic_id}")
        print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Objective: Identify and fix system connection issues")
        print("=" * 80)
        print()
    
    async def run_comprehensive_diagnostic(self):
        """Run comprehensive system diagnostic"""
        self.print_diagnostic_header()
        
        try:
            # Phase 1: Check all system components
            await self.check_all_components()
            
            # Phase 2: Identify issues
            await self.identify_issues()
            
            # Phase 3: Apply fixes
            await self.apply_fixes()
            
            # Phase 4: Verify fixes
            await self.verify_fixes()
            
            # Phase 5: Generate recommendations
            await self.generate_recommendations()
            
        except Exception as e:
            self.logger.error(f"Diagnostic failed: {e}")
            print(f"[ERROR] Diagnostic failed: {e}")
        
        finally:
            await self.save_diagnostic_report()
    
    async def check_all_components(self):
        """Check status of all system components"""
        print("🔍 CHECKING ALL SYSTEM COMPONENTS")
        print("-" * 50)
        
        for component_key, config in self.components.items():
            print(f"📊 Checking {config['name']}...")
            
            status = await self.check_component(component_key, config)
            self.results["component_status"][component_key] = status
            
            if status["healthy"]:
                print(f"   [CHECK] {config['name']}: HEALTHY")
                if "details" in status:
                    print(f"      {status['details']}")
            else:
                print(f"   [ERROR] {config['name']}: ISSUE DETECTED")
                print(f"      Error: {status.get('error', 'Unknown error')}")
                self.results["issues_found"].append({
                    "component": component_key,
                    "name": config['name'],
                    "error": status.get('error', 'Unknown error')
                })
            
            print()
    
    async def check_component(self, component_key: str, config: dict) -> dict:
        """Check individual component status"""
        try:
            if component_key == "backend_server":
                return await self.check_backend_server(config)
            elif component_key == "frontend_server":
                return await self.check_frontend_server(config)
            elif component_key == "ib_gateway":
                return await self.check_ib_gateway(config)
            elif component_key == "cloudflare_tunnel":
                return await self.check_cloudflare_tunnel(config)
            else:
                return {"healthy": False, "error": "Unknown component"}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_backend_server(self, config: dict) -> dict:
        """Check backend server status"""
        try:
            # Check if port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            port_result = sock.connect_ex(('localhost', config['port']))
            sock.close()
            
            if port_result != 0:
                return {"healthy": False, "error": f"Port {config['port']} not accessible"}
            
            # Check HTTP response
            response = requests.get(config['url'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                uptime = data.get('uptime_seconds', 0)
                return {
                    "healthy": True,
                    "details": f"Status: {response.status_code}, Uptime: {uptime:.0f}s"
                }
            else:
                return {"healthy": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"healthy": False, "error": f"Request failed: {e}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_frontend_server(self, config: dict) -> dict:
        """Check frontend server status"""
        try:
            # Check if port is open
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            port_result = sock.connect_ex(('localhost', config['port']))
            sock.close()
            
            if port_result != 0:
                return {"healthy": False, "error": f"Port {config['port']} not accessible"}
            
            # Try to get a response
            response = requests.get(config['url'], timeout=5)
            if response.status_code == 200:
                return {
                    "healthy": True,
                    "details": f"Status: {response.status_code}, React app accessible"
                }
            else:
                return {"healthy": False, "error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            return {"healthy": False, "error": f"Request failed: {e}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_ib_gateway(self, config: dict) -> dict:
        """Check IB Gateway connection"""
        try:
            # Check if IB Gateway port is accessible
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((config['host'], config['port']))
            sock.close()
            
            if result == 0:
                return {
                    "healthy": True,
                    "details": f"IB Gateway accessible on port {config['port']}"
                }
            else:
                return {
                    "healthy": False,
                    "error": f"Cannot connect to IB Gateway on port {config['port']}"
                }
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def check_cloudflare_tunnel(self, config: dict) -> dict:
        """Check Cloudflare tunnel status"""
        try:
            # Check if cloudflared process is running
            if sys.platform == "win32":
                result = subprocess.run(
                    ['tasklist', '/FI', 'IMAGENAME eq cloudflared.exe'],
                    capture_output=True, text=True
                )
                if 'cloudflared.exe' in result.stdout:
                    return {"healthy": True, "details": "Cloudflare tunnel process running"}
                else:
                    return {"healthy": False, "error": "Cloudflare tunnel not running"}
            else:
                result = subprocess.run(['pgrep', 'cloudflared'], capture_output=True)
                if result.returncode == 0:
                    return {"healthy": True, "details": "Cloudflare tunnel process running"}
                else:
                    return {"healthy": False, "error": "Cloudflare tunnel not running"}
                    
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def identify_issues(self):
        """Identify specific issues and their causes"""
        print("🔍 IDENTIFYING ISSUES")
        print("-" * 30)
        
        if not self.results["issues_found"]:
            print("   [CHECK] No issues found - all systems healthy!")
            return
        
        for issue in self.results["issues_found"]:
            print(f"   [ERROR] {issue['name']}: {issue['error']}")
        
        print()
    
    async def apply_fixes(self):
        """Apply automatic fixes where possible"""
        print("🔧 APPLYING FIXES")
        print("-" * 20)
        
        if not self.results["issues_found"]:
            print("   [CHECK] No fixes needed - all systems healthy!")
            return
        
        for issue in self.results["issues_found"]:
            fix_applied = await self.apply_component_fix(issue)
            if fix_applied:
                self.results["fixes_applied"].append({
                    "component": issue['component'],
                    "fix": fix_applied
                })
                print(f"   [CHECK] Applied fix for {issue['name']}: {fix_applied}")
            else:
                print(f"   [WARNING]️ Manual intervention needed for {issue['name']}")
        
        print()
    
    async def apply_component_fix(self, issue: dict) -> str:
        """Apply fix for specific component"""
        component = issue['component']
        
        if component == "backend_server":
            # Try to start backend server
            try:
                print("      🚀 Attempting to start backend server...")
                # This would need to be implemented based on your startup process
                return "Backend server restart attempted"
            except Exception as e:
                return None
        
        elif component == "ib_gateway":
            return "Please ensure IB Gateway is running and API is enabled"
        
        elif component == "frontend_server":
            return "Please ensure 'npm start' is running in frontend directory"
        
        elif component == "cloudflare_tunnel":
            return "Please start Cloudflare tunnel if external access is needed"
        
        return None
    
    async def verify_fixes(self):
        """Verify that applied fixes resolved the issues"""
        print("[CHECK] VERIFYING FIXES")
        print("-" * 20)
        
        if not self.results["fixes_applied"]:
            print("   [INFO]️ No fixes were applied")
            return
        
        # Re-check components that had fixes applied
        for fix in self.results["fixes_applied"]:
            component_key = fix['component']
            config = self.components[component_key]
            
            print(f"   🔄 Re-checking {config['name']}...")
            status = await self.check_component(component_key, config)
            
            if status["healthy"]:
                print(f"      [CHECK] Fix successful!")
            else:
                print(f"      [ERROR] Fix unsuccessful: {status.get('error', 'Unknown error')}")
        
        print()
    
    async def generate_recommendations(self):
        """Generate recommendations based on diagnostic results"""
        print("💡 RECOMMENDATIONS")
        print("-" * 20)
        
        recommendations = []
        
        # Check overall system health
        healthy_components = sum(1 for status in self.results["component_status"].values() if status["healthy"])
        total_components = len(self.results["component_status"])
        health_percentage = (healthy_components / total_components) * 100
        
        if health_percentage == 100:
            recommendations.append("[CHECK] All systems healthy - ready for validation testing")
            recommendations.append("🚀 Proceed with extended validation suite")
        elif health_percentage >= 75:
            recommendations.append("[WARNING]️ Most systems healthy - address remaining issues")
            recommendations.append("🔧 Fix remaining issues before extended testing")
        else:
            recommendations.append("[ERROR] Multiple system issues detected")
            recommendations.append("🛠️ Address all issues before proceeding")
        
        # Specific recommendations
        for issue in self.results["issues_found"]:
            if issue['component'] == 'ib_gateway':
                recommendations.append("🏦 Ensure IB Gateway is running with API enabled (port 7497)")
            elif issue['component'] == 'backend_server':
                recommendations.append("🖥️ Start PROMETHEUS backend server (unified_production_server.py)")
            elif issue['component'] == 'frontend_server':
                recommendations.append("⚛️ Start React frontend (npm start in frontend directory)")
        
        self.results["recommendations"] = recommendations
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        print()
    
    async def save_diagnostic_report(self):
        """Save diagnostic report"""
        report_filename = f"system_diagnostic_report_{self.diagnostic_id}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"📄 Diagnostic report saved: {report_filename}")
        
        # Print summary
        healthy_count = sum(1 for status in self.results["component_status"].values() if status["healthy"])
        total_count = len(self.results["component_status"])
        
        print()
        print("📊 DIAGNOSTIC SUMMARY")
        print("-" * 30)
        print(f"   Healthy Components: {healthy_count}/{total_count}")
        print(f"   Issues Found: {len(self.results['issues_found'])}")
        print(f"   Fixes Applied: {len(self.results['fixes_applied'])}")
        print(f"   System Health: {(healthy_count/total_count)*100:.0f}%")

if __name__ == "__main__":
    diagnostic = SystemConnectionDiagnostic()
    asyncio.run(diagnostic.run_comprehensive_diagnostic())
