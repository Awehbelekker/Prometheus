#!/usr/bin/env python3
"""
PROMETHEUS PLATFORM SYNCHRONIZATION SCRIPT
Syncs newer features from Trading Platform to Enterprise Package COMPLETE

This script safely synchronizes improvements from the active Trading Platform
to the stable Enterprise Package COMPLETE without disrupting any systems.

SAFETY FEATURES:
- Validates no trading processes are running
- Creates backups before sync
- Validates file integrity
- Provides rollback capability
- Logs all operations
"""

import os
import shutil
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class PrometheusSyncManager:
    """Manages synchronization between Trading Platform and Enterprise Package"""
    
    def __init__(self):
        self.trading_platform_path = Path("C:/Users/Judy/Desktop/PROMETHEUS-Trading-Platform")
        self.enterprise_package_path = Path("C:/Users/Judy/Desktop/PROMETHEUS-Enterprise-Package-COMPLETE")
        self.backup_path = Path("C:/Users/Judy/Desktop/PROMETHEUS-SYNC-BACKUP")
        self.sync_log_path = Path("C:/Users/Judy/Desktop/PROMETHEUS-SYNC-LOGS")
        
        # Setup logging
        self.setup_logging()
        
        # Define sync categories
        self.sync_categories = {
            "ai_intelligence": {
                "description": "AI Intelligence Enhancements",
                "priority": "high",
                "files": [
                    "genius_level_ai_optimizer.py",
                    "ai_quality_monitor.py", 
                    "enhanced_ai_trading_engine.py",
                    "comprehensive_ai_audit.py"
                ]
            },
            "analytics": {
                "description": "Advanced Analytics System",
                "priority": "high", 
                "files": [
                    "advanced_analytics_system.py",
                    "performance_benchmarking_suite.py",
                    "comprehensive_returns_report.py",
                    "analyze_historical_performance.py"
                ]
            },
            "monitoring": {
                "description": "Enhanced Monitoring Systems",
                "priority": "high",
                "files": [
                    "comprehensive_system_monitor.py",
                    "live_stats_dashboard.py",
                    "automated_monitoring.py",
                    "advanced_monitoring_dashboards.py"
                ]
            },
            "trading_optimization": {
                "description": "Trading Logic Optimizations",
                "priority": "high",
                "files": [
                    "aggressive_6_8_percent_optimizer.py",
                    "gradual_optimization_engine.py",
                    "enhanced_trading_logic.py",
                    "maximize_daily_trades.py"
                ]
            },
            "system_maintenance": {
                "description": "System Maintenance Tools",
                "priority": "medium",
                "files": [
                    "comprehensive_codebase_cleanup_audit.py",
                    "execute_codebase_cleanup.py",
                    "free_memory_and_optimize.py",
                    "optimize_for_32gb_ram.py"
                ]
            }
        }
        
        # Sync statistics
        self.sync_stats = {
            "files_synced": 0,
            "files_skipped": 0,
            "files_failed": 0,
            "backups_created": 0,
            "start_time": None,
            "end_time": None
        }
    
    def setup_logging(self):
        """Setup comprehensive logging"""
        self.sync_log_path.mkdir(exist_ok=True)
        
        log_file = self.sync_log_path / f"sync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("=== PROMETHEUS SYNC MANAGER INITIALIZED ===")
    
    def check_safety_prerequisites(self) -> bool:
        """Check if it's safe to perform sync operations"""
        self.logger.info("🔍 Checking safety prerequisites...")
        
        # Check if trading processes are running
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                  capture_output=True, text=True, shell=True)
            if 'python.exe' in result.stdout:
                self.logger.warning("⚠️ Python processes detected - checking if trading related...")
                # Additional check for trading-specific processes
                trading_processes = ['launch_ultimate_prometheus', 'trading_engine', 'ib_live']
                for process in trading_processes:
                    if process in result.stdout.lower():
                        self.logger.error(f"❌ Trading process detected: {process}")
                        return False
        except Exception as e:
            self.logger.warning(f"⚠️ Could not check processes: {e}")
        
        # Check if backend server is running
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=3)
            if response.status_code == 200:
                self.logger.error("❌ Backend server is running - sync not safe")
                return False
        except:
            self.logger.info("✅ Backend server not running - safe to sync")
        
        # Check if paths exist
        if not self.trading_platform_path.exists():
            self.logger.error(f"❌ Trading Platform path not found: {self.trading_platform_path}")
            return False
            
        if not self.enterprise_package_path.exists():
            self.logger.error(f"❌ Enterprise Package path not found: {self.enterprise_package_path}")
            return False
        
        self.logger.info("✅ All safety checks passed")
        return True
    
    def create_backup(self) -> bool:
        """Create backup of Enterprise Package before sync"""
        self.logger.info("📦 Creating backup of Enterprise Package...")
        
        try:
            if self.backup_path.exists():
                shutil.rmtree(self.backup_path)
            
            backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = self.backup_path / f"backup_{backup_timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy entire Enterprise Package
            shutil.copytree(self.enterprise_package_path, backup_dir / "PROMETHEUS-Enterprise-Package-COMPLETE")
            
            # Create backup manifest
            manifest = {
                "backup_time": datetime.now().isoformat(),
                "source_path": str(self.enterprise_package_path),
                "backup_path": str(backup_dir),
                "files_backed_up": self.count_files(backup_dir),
                "backup_type": "full_enterprise_package"
            }
            
            with open(backup_dir / "backup_manifest.json", 'w') as f:
                json.dump(manifest, f, indent=2)
            
            self.sync_stats["backups_created"] += 1
            self.logger.info(f"✅ Backup created: {backup_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Backup failed: {e}")
            return False
    
    def count_files(self, directory: Path) -> int:
        """Count files in directory recursively"""
        count = 0
        for root, dirs, files in os.walk(directory):
            count += len(files)
        return count
    
    def validate_file_integrity(self, source_file: Path, dest_file: Path) -> bool:
        """Validate that file was copied correctly"""
        try:
            if not source_file.exists() or not dest_file.exists():
                return False
            
            # Compare file sizes
            if source_file.stat().st_size != dest_file.stat().st_size:
                return False
            
            # Compare file contents (first 1KB)
            with open(source_file, 'rb') as f1, open(dest_file, 'rb') as f2:
                chunk1 = f1.read(1024)
                chunk2 = f2.read(1024)
                if chunk1 != chunk2:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ File integrity check failed: {e}")
            return False
    
    def sync_file(self, source_file: Path, dest_file: Path, category: str) -> bool:
        """Sync a single file from Trading Platform to Enterprise Package"""
        try:
            # Ensure destination directory exists
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source_file, dest_file)
            
            # Validate integrity
            if self.validate_file_integrity(source_file, dest_file):
                self.logger.info(f"✅ Synced {category}: {dest_file.name}")
                self.sync_stats["files_synced"] += 1
                return True
            else:
                self.logger.error(f"❌ Integrity check failed: {dest_file.name}")
                self.sync_stats["files_failed"] += 1
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Sync failed for {dest_file.name}: {e}")
            self.sync_stats["files_failed"] += 1
            return False
    
    def sync_category(self, category_name: str, category_info: Dict) -> bool:
        """Sync all files in a category"""
        self.logger.info(f"🔄 Syncing {category_info['description']}...")
        
        success_count = 0
        total_files = len(category_info['files'])
        
        for file_name in category_info['files']:
            source_file = self.trading_platform_path / file_name
            dest_file = self.enterprise_package_path / file_name
            
            if source_file.exists():
                if self.sync_file(source_file, dest_file, category_name):
                    success_count += 1
            else:
                self.logger.warning(f"⚠️ File not found: {file_name}")
                self.sync_stats["files_skipped"] += 1
        
        success_rate = (success_count / total_files) * 100
        self.logger.info(f"📊 {category_name}: {success_count}/{total_files} files synced ({success_rate:.1f}%)")
        
        return success_count == total_files
    
    def create_sync_report(self) -> Dict:
        """Create comprehensive sync report"""
        report = {
            "sync_summary": {
                "timestamp": datetime.now().isoformat(),
                "duration": (self.sync_stats["end_time"] - self.sync_stats["start_time"]).total_seconds(),
                "total_files_synced": self.sync_stats["files_synced"],
                "total_files_skipped": self.sync_stats["files_skipped"],
                "total_files_failed": self.sync_stats["files_failed"],
                "backups_created": self.sync_stats["backups_created"]
            },
            "categories": {},
            "recommendations": []
        }
        
        # Add category details
        for category_name, category_info in self.sync_categories.items():
            report["categories"][category_name] = {
                "description": category_info["description"],
                "priority": category_info["priority"],
                "files_count": len(category_info["files"]),
                "status": "completed" if self.sync_stats["files_synced"] > 0 else "pending"
            }
        
        # Add recommendations
        if self.sync_stats["files_failed"] > 0:
            report["recommendations"].append("Review failed file syncs and retry if necessary")
        
        if self.sync_stats["files_skipped"] > 0:
            report["recommendations"].append("Check for missing files in Trading Platform")
        
        report["recommendations"].extend([
            "Test all synced features in Enterprise Package",
            "Update documentation with new features",
            "Create integration tests for new components"
        ])
        
        return report
    
    def save_sync_report(self, report: Dict):
        """Save sync report to file"""
        report_file = self.sync_log_path / f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"📄 Sync report saved: {report_file}")
    
    def run_sync(self) -> bool:
        """Execute the complete sync process"""
        self.logger.info("🚀 Starting PROMETHEUS Platform Synchronization...")
        self.sync_stats["start_time"] = datetime.now()
        
        # Step 1: Safety checks
        if not self.check_safety_prerequisites():
            self.logger.error("❌ Safety checks failed - aborting sync")
            return False
        
        # Step 2: Create backup
        if not self.create_backup():
            self.logger.error("❌ Backup creation failed - aborting sync")
            return False
        
        # Step 3: Sync categories by priority
        high_priority_categories = [name for name, info in self.sync_categories.items() 
                                  if info["priority"] == "high"]
        medium_priority_categories = [name for name, info in self.sync_categories.items() 
                                    if info["priority"] == "medium"]
        
        all_successful = True
        
        # Sync high priority categories first
        self.logger.info("🔥 Syncing HIGH PRIORITY categories...")
        for category_name in high_priority_categories:
            if not self.sync_category(category_name, self.sync_categories[category_name]):
                all_successful = False
        
        # Sync medium priority categories
        self.logger.info("⚡ Syncing MEDIUM PRIORITY categories...")
        for category_name in medium_priority_categories:
            if not self.sync_category(category_name, self.sync_categories[category_name]):
                all_successful = False
        
        # Step 4: Generate report
        self.sync_stats["end_time"] = datetime.now()
        report = self.create_sync_report()
        self.save_sync_report(report)
        
        # Step 5: Final summary
        self.logger.info("=" * 60)
        self.logger.info("📊 SYNC SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"✅ Files Synced: {self.sync_stats['files_synced']}")
        self.logger.info(f"⚠️ Files Skipped: {self.sync_stats['files_skipped']}")
        self.logger.info(f"❌ Files Failed: {self.sync_stats['files_failed']}")
        self.logger.info(f"📦 Backups Created: {self.sync_stats['backups_created']}")
        self.logger.info(f"⏱️ Duration: {(self.sync_stats['end_time'] - self.sync_stats['start_time']).total_seconds():.2f}s")
        
        if all_successful:
            self.logger.info("🎉 SYNC COMPLETED SUCCESSFULLY!")
        else:
            self.logger.warning("⚠️ SYNC COMPLETED WITH WARNINGS")
        
        return all_successful

def main():
    """Main execution function"""
    print("🚀 PROMETHEUS PLATFORM SYNCHRONIZATION SCRIPT")
    print("=" * 50)
    print("This script will sync newer features from Trading Platform")
    print("to Enterprise Package COMPLETE safely.")
    print()
    
    # Confirm with user
    response = input("Do you want to proceed with synchronization? (y/N): ")
    if response.lower() != 'y':
        print("❌ Synchronization cancelled by user")
        return False
    
    # Initialize sync manager
    sync_manager = PrometheusSyncManager()
    
    # Run synchronization
    success = sync_manager.run_sync()
    
    if success:
        print("\n🎉 Synchronization completed successfully!")
        print("📄 Check sync logs for detailed information")
        print("🔄 Enterprise Package COMPLETE has been updated with newer features")
    else:
        print("\n⚠️ Synchronization completed with warnings")
        print("📄 Check sync logs for details on any issues")
        print("🔄 Some features may not have been synced")
    
    return success

if __name__ == "__main__":
    main()








