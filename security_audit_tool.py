#!/usr/bin/env python3
"""
PROMETHEUS Trading Platform - Security Audit & Penetration Testing Tool
Enterprise-grade security validation for financial trading platform
"""

import os
import re
import json
import hashlib
import secrets
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
import ast
import tempfile

class SecurityAuditTool:
    """Comprehensive security audit tool for PROMETHEUS Trading Platform."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.audit_results = {
            "timestamp": datetime.now().isoformat(),
            "security_score": 0,
            "vulnerabilities": [],
            "recommendations": [],
            "compliance_checks": {},
            "file_analysis": {},
            "database_security": {},
            "authentication_security": {},
            "api_security": {}
        }
    
    def scan_for_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Scan for hardcoded secrets and sensitive information."""
        print("🔍 Scanning for hardcoded secrets...")
        
        vulnerabilities = []
        
        # Patterns for common secrets
        secret_patterns = {
            "api_key": r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]([a-zA-Z0-9_-]{20,})['\"]",
            "password": r"(?i)(password|pwd|pass)\s*[=:]\s*['\"]([^'\"]{8,})['\"]",
            "secret_key": r"(?i)(secret[_-]?key|secretkey)\s*[=:]\s*['\"]([a-zA-Z0-9_-]{20,})['\"]",
            "private_key": r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
            "aws_access": r"(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*['\"]([A-Z0-9]{20})['\"]",
            "database_url": r"(?i)(database[_-]?url|db[_-]?url)\s*[=:]\s*['\"]([^'\"]+://[^'\"]+)['\"]",
            "jwt_secret": r"(?i)(jwt[_-]?secret|token[_-]?secret)\s*[=:]\s*['\"]([a-zA-Z0-9_-]{20,})['\"]"
        }
        
        # File extensions to scan
        extensions = ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.env', '.config']
        
        for ext in extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if any(skip in str(file_path) for skip in ['node_modules', '__pycache__', '.git', 'venv']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for secret_type, pattern in secret_patterns.items():
                            matches = re.finditer(pattern, content, re.MULTILINE)
                            for match in matches:
                                vulnerabilities.append({
                                    "type": "hardcoded_secret",
                                    "severity": "HIGH",
                                    "file": str(file_path.relative_to(self.project_root)),
                                    "line": content[:match.start()].count('\n') + 1,
                                    "secret_type": secret_type,
                                    "description": f"Potential {secret_type} found in source code",
                                    "recommendation": f"Move {secret_type} to environment variables or secure configuration"
                                })
                
                except Exception as e:
                    continue
        
        return vulnerabilities
    
    def analyze_authentication_security(self) -> Dict[str, Any]:
        """Analyze authentication and authorization security."""
        print("🔐 Analyzing authentication security...")
        
        auth_analysis = {
            "jwt_security": {"score": 0, "issues": []},
            "password_security": {"score": 0, "issues": []},
            "session_security": {"score": 0, "issues": []},
            "overall_score": 0
        }
        
        # Check JWT implementation
        jwt_files = list(self.project_root.rglob("*auth*.py"))
        for file_path in jwt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for secure JWT practices
                    if "HS256" in content:
                        auth_analysis["jwt_security"]["score"] += 20
                    else:
                        auth_analysis["jwt_security"]["issues"].append("JWT algorithm not specified or insecure")
                    
                    if "exp" in content or "expiry" in content:
                        auth_analysis["jwt_security"]["score"] += 30
                    else:
                        auth_analysis["jwt_security"]["issues"].append("JWT tokens may not have expiration")
                    
                    if "secrets.token_urlsafe" in content or "os.urandom" in content:
                        auth_analysis["jwt_security"]["score"] += 25
                    else:
                        auth_analysis["jwt_security"]["issues"].append("JWT secret may not be cryptographically secure")
                    
                    if "bcrypt" in content or "scrypt" in content or "pbkdf2" in content:
                        auth_analysis["password_security"]["score"] += 40
                    else:
                        auth_analysis["password_security"]["issues"].append("Password hashing may not use secure algorithms")
                    
                    if "salt" in content:
                        auth_analysis["password_security"]["score"] += 30
                    else:
                        auth_analysis["password_security"]["issues"].append("Password hashing may not use salt")
            
            except Exception as e:
                continue
        
        # Calculate overall authentication score
        scores = [auth_analysis[key]["score"] for key in ["jwt_security", "password_security", "session_security"]]
        auth_analysis["overall_score"] = sum(scores) / len(scores) if scores else 0
        
        return auth_analysis
    
    def check_database_security(self) -> Dict[str, Any]:
        """Check database security configurations."""
        print("💾 Checking database security...")
        
        db_security = {
            "sql_injection_protection": {"score": 0, "issues": []},
            "connection_security": {"score": 0, "issues": []},
            "data_encryption": {"score": 0, "issues": []},
            "overall_score": 0
        }
        
        # Check for SQL injection vulnerabilities
        python_files = list(self.project_root.rglob("*.py"))
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for parameterized queries
                    if re.search(r'execute\([^,]+,\s*\([^)]+\)', content):
                        db_security["sql_injection_protection"]["score"] += 10
                    
                    # Check for dangerous string formatting in SQL
                    dangerous_patterns = [
                        r'execute\([^)]*%[^)]*\)',
                        r'execute\([^)]*\.format\([^)]*\)',
                        r'execute\([^)]*\+[^)]*\)'
                    ]
                    
                    for pattern in dangerous_patterns:
                        if re.search(pattern, content):
                            db_security["sql_injection_protection"]["issues"].append(
                                f"Potential SQL injection in {file_path.name}"
                            )
                    
                    # Check for database connection security
                    if "ssl" in content.lower() or "tls" in content.lower():
                        db_security["connection_security"]["score"] += 20
                    
                    if "encrypt" in content.lower():
                        db_security["data_encryption"]["score"] += 15
            
            except Exception as e:
                continue
        
        # Normalize scores
        for category in ["sql_injection_protection", "connection_security", "data_encryption"]:
            db_security[category]["score"] = min(100, db_security[category]["score"])
        
        scores = [db_security[key]["score"] for key in ["sql_injection_protection", "connection_security", "data_encryption"]]
        db_security["overall_score"] = sum(scores) / len(scores) if scores else 0
        
        return db_security
    
    def analyze_api_security(self) -> Dict[str, Any]:
        """Analyze API security measures."""
        print("🌐 Analyzing API security...")
        
        api_security = {
            "input_validation": {"score": 0, "issues": []},
            "rate_limiting": {"score": 0, "issues": []},
            "cors_security": {"score": 0, "issues": []},
            "https_enforcement": {"score": 0, "issues": []},
            "overall_score": 0
        }
        
        # Check API files
        api_files = list(self.project_root.rglob("*api*.py")) + list(self.project_root.rglob("*server*.py"))
        
        for file_path in api_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Check for input validation
                    if "pydantic" in content or "marshmallow" in content or "validate" in content:
                        api_security["input_validation"]["score"] += 25
                    
                    # Check for rate limiting
                    if "rate_limit" in content or "throttle" in content:
                        api_security["rate_limiting"]["score"] += 30
                    else:
                        api_security["rate_limiting"]["issues"].append("No rate limiting detected")
                    
                    # Check CORS configuration
                    if "CORS" in content:
                        if "allow_origins" in content and "*" not in content:
                            api_security["cors_security"]["score"] += 25
                        else:
                            api_security["cors_security"]["issues"].append("CORS may be too permissive")
                    
                    # Check HTTPS enforcement
                    if "https_only" in content or "ssl_redirect" in content:
                        api_security["https_enforcement"]["score"] += 30
                    else:
                        api_security["https_enforcement"]["issues"].append("HTTPS enforcement not detected")
            
            except Exception as e:
                continue
        
        # Normalize scores
        for category in api_security:
            if category != "overall_score":
                api_security[category]["score"] = min(100, api_security[category]["score"])
        
        scores = [api_security[key]["score"] for key in api_security if key != "overall_score"]
        api_security["overall_score"] = sum(scores) / len(scores) if scores else 0
        
        return api_security
    
    def check_file_permissions(self) -> List[Dict[str, Any]]:
        """Check file permissions for security issues."""
        print("📁 Checking file permissions...")
        
        permission_issues = []
        
        # Check for overly permissive files
        sensitive_files = [
            "*.key", "*.pem", "*.p12", "*.pfx", 
            "*.env", "config.py", "settings.py"
        ]
        
        for pattern in sensitive_files:
            for file_path in self.project_root.rglob(pattern):
                try:
                    stat_info = file_path.stat()
                    mode = oct(stat_info.st_mode)[-3:]
                    
                    # Check if file is world-readable or world-writable
                    if mode[-1] in ['4', '5', '6', '7']:  # World-readable
                        permission_issues.append({
                            "type": "file_permission",
                            "severity": "MEDIUM",
                            "file": str(file_path.relative_to(self.project_root)),
                            "issue": "File is world-readable",
                            "current_permissions": mode,
                            "recommendation": "Restrict file permissions to owner only"
                        })
                    
                    if mode[-1] in ['2', '3', '6', '7']:  # World-writable
                        permission_issues.append({
                            "type": "file_permission",
                            "severity": "HIGH",
                            "file": str(file_path.relative_to(self.project_root)),
                            "issue": "File is world-writable",
                            "current_permissions": mode,
                            "recommendation": "Remove world-write permissions immediately"
                        })
                
                except Exception as e:
                    continue
        
        return permission_issues
    
    def generate_security_recommendations(self) -> List[str]:
        """Generate security recommendations based on audit results."""
        recommendations = []
        
        # General security recommendations
        recommendations.extend([
            "Implement comprehensive input validation for all API endpoints",
            "Use environment variables for all sensitive configuration",
            "Enable HTTPS/TLS for all communications",
            "Implement proper session management with secure cookies",
            "Use parameterized queries to prevent SQL injection",
            "Implement rate limiting on all public endpoints",
            "Regular security updates for all dependencies",
            "Implement proper logging and monitoring for security events",
            "Use strong, unique passwords and multi-factor authentication",
            "Regular security audits and penetration testing"
        ])
        
        # Add specific recommendations based on vulnerabilities found
        if any(v["type"] == "hardcoded_secret" for v in self.audit_results["vulnerabilities"]):
            recommendations.append("CRITICAL: Remove all hardcoded secrets from source code immediately")
        
        return recommendations
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit."""
        print("🔒 Starting PROMETHEUS Security Audit")
        print("=" * 60)
        
        # Run all security checks
        self.audit_results["vulnerabilities"].extend(self.scan_for_hardcoded_secrets())
        self.audit_results["vulnerabilities"].extend(self.check_file_permissions())
        
        self.audit_results["authentication_security"] = self.analyze_authentication_security()
        self.audit_results["database_security"] = self.check_database_security()
        self.audit_results["api_security"] = self.analyze_api_security()
        
        self.audit_results["recommendations"] = self.generate_security_recommendations()
        
        # Calculate overall security score
        security_scores = [
            self.audit_results["authentication_security"]["overall_score"],
            self.audit_results["database_security"]["overall_score"],
            self.audit_results["api_security"]["overall_score"]
        ]
        
        # Deduct points for vulnerabilities
        vulnerability_penalty = len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "HIGH"]) * 10
        vulnerability_penalty += len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "MEDIUM"]) * 5
        
        base_score = sum(security_scores) / len(security_scores) if security_scores else 0
        self.audit_results["security_score"] = max(0, base_score - vulnerability_penalty)
        
        # Generate report
        self.generate_security_report()
        
        return self.audit_results
    
    def generate_security_report(self):
        """Generate comprehensive security audit report."""
        print("\n" + "=" * 60)
        print("🔒 PROMETHEUS SECURITY AUDIT REPORT")
        print("=" * 60)
        
        print(f"Audit Timestamp: {self.audit_results['timestamp']}")
        print(f"Overall Security Score: {self.audit_results['security_score']:.1f}/100")
        
        # Security score assessment
        score = self.audit_results['security_score']
        if score >= 90:
            print("🟢 EXCELLENT - Enterprise-grade security")
        elif score >= 80:
            print("🟡 GOOD - Minor security improvements needed")
        elif score >= 70:
            print("🟠 FAIR - Several security issues to address")
        else:
            print("🔴 POOR - Critical security issues require immediate attention")
        
        # Vulnerabilities summary
        high_vulns = len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "HIGH"])
        medium_vulns = len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "MEDIUM"])
        low_vulns = len([v for v in self.audit_results["vulnerabilities"] if v.get("severity") == "LOW"])
        
        print(f"\n📊 Vulnerability Summary:")
        print(f"  High Severity: {high_vulns}")
        print(f"  Medium Severity: {medium_vulns}")
        print(f"  Low Severity: {low_vulns}")
        
        # Security category scores
        print(f"\n🔍 Security Category Scores:")
        print(f"  Authentication Security: {self.audit_results['authentication_security']['overall_score']:.1f}/100")
        print(f"  Database Security: {self.audit_results['database_security']['overall_score']:.1f}/100")
        print(f"  API Security: {self.audit_results['api_security']['overall_score']:.1f}/100")
        
        # Top vulnerabilities
        if self.audit_results["vulnerabilities"]:
            print(f"\n[WARNING]️  Top Security Issues:")
            for i, vuln in enumerate(self.audit_results["vulnerabilities"][:5], 1):
                print(f"  {i}. {vuln.get('description', 'Security issue')} ({vuln.get('severity', 'UNKNOWN')})")
        
        # Top recommendations
        print(f"\n💡 Top Security Recommendations:")
        for i, rec in enumerate(self.audit_results["recommendations"][:5], 1):
            print(f"  {i}. {rec}")
        
        # Save detailed report
        report_filename = f"security_audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(self.audit_results, f, indent=2)
        
        print(f"\n📁 Detailed security report saved: {report_filename}")
        print("=" * 60)


def main():
    """Main entry point for security audit."""
    auditor = SecurityAuditTool()
    results = auditor.run_comprehensive_audit()
    
    # Return appropriate exit code
    if results["security_score"] >= 80:
        return 0  # Success
    else:
        return 1  # Security issues found


if __name__ == "__main__":
    exit(main())
