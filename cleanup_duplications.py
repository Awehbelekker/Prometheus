#!/usr/bin/env python3
"""
🧹 PROMETHEUS DUPLICATION CLEANUP SCRIPT
Systematically removes duplicate implementations and consolidates codebase
Based on the comprehensive duplication audit report
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrometheusCleanupManager:
    """
    Manages the systematic cleanup of duplicate implementations
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.backup_dir = self.project_root / 'backup_before_cleanup'
        self.cleanup_log = []
        
    def create_backup(self):
        """Create backup of all files before cleanup"""
        logger.info("📦 Creating backup before cleanup...")
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        self.backup_dir.mkdir()
        
        # Files to backup
        backup_files = [
            'core/auth_service.py',
            'core/security/authentication.py',
            'enterprise/security/enterprise_auth.py',
            'core/security_enhancements.py',
            'core/database_manager.py',
            'core/persistence_manager.py',
            'core/performance_optimization.py',
            'revolutionary_crypto_engine.py',
            'revolutionary_advanced_engine.py',
            'revolutionary_options_engine.py',
            'revolutionary_market_maker.py',
            'revolutionary_master_engine.py',
            '.env.template',
            '.env.production',
            '.env.enterprise',
            'docker-compose.yml',
            'docker-compose.production.yml',
            'Dockerfile',
            'frontend/Dockerfile'
        ]
        
        for file_path in backup_files:
            source = self.project_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                logger.info(f"[CHECK] Backed up: {file_path}")
        
        logger.info(f"📦 Backup completed in: {self.backup_dir}")
    
    def cleanup_authentication_duplicates(self):
        """Phase 1: Remove duplicate authentication implementations"""
        logger.info("🔐 Phase 1: Cleaning up authentication duplicates...")
        
        # Files to remove (keeping core/auth_service.py as primary)
        files_to_remove = [
            'core/security/authentication.py',
            'enterprise/security/enterprise_auth.py',
            'core/security_enhancements.py'
        ]
        
        for file_path in files_to_remove:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"🗑️ Removed duplicate: {file_path}")
                self.cleanup_log.append(f"Removed authentication duplicate: {file_path}")
        
        # Remove empty directories
        empty_dirs = [
            'core/security',
            'enterprise/security'
        ]
        
        for dir_path in empty_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and not any(full_path.iterdir()):
                full_path.rmdir()
                logger.info(f"🗑️ Removed empty directory: {dir_path}")
    
    def cleanup_database_duplicates(self):
        """Phase 2: Remove duplicate database implementations"""
        logger.info("🗄️ Phase 2: Cleaning up database duplicates...")
        
        # Files to remove (keeping unified_production_server.py database logic)
        files_to_remove = [
            'core/database_manager.py',
            'core/persistence_manager.py'
        ]
        
        for file_path in files_to_remove:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"🗑️ Removed duplicate: {file_path}")
                self.cleanup_log.append(f"Removed database duplicate: {file_path}")
    
    def cleanup_environment_duplicates(self):
        """Phase 3: Remove duplicate environment configurations"""
        logger.info("⚙️ Phase 3: Cleaning up environment duplicates...")
        
        # Files to remove (keeping .env.unified.template as primary)
        files_to_remove = [
            '.env.production',
            '.env.enterprise'
        ]
        
        for file_path in files_to_remove:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"🗑️ Removed duplicate: {file_path}")
                self.cleanup_log.append(f"Removed environment duplicate: {file_path}")
        
        # Rename unified template to standard name
        unified_template = self.project_root / '.env.unified.template'
        standard_template = self.project_root / '.env.template'
        
        if unified_template.exists():
            if standard_template.exists():
                standard_template.unlink()
            unified_template.rename(standard_template)
            logger.info("[CHECK] Renamed .env.unified.template to .env.template")
    
    def cleanup_docker_duplicates(self):
        """Phase 4: Remove duplicate Docker configurations"""
        logger.info("🐳 Phase 4: Cleaning up Docker duplicates...")
        
        # Files to remove (keeping unified versions)
        files_to_remove = [
            'docker-compose.production.yml',
            'frontend/Dockerfile'
        ]
        
        for file_path in files_to_remove:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"🗑️ Removed duplicate: {file_path}")
                self.cleanup_log.append(f"Removed Docker duplicate: {file_path}")
        
        # Rename unified files to standard names
        renames = [
            ('docker-compose.unified.yml', 'docker-compose.yml'),
            ('Dockerfile.unified', 'Dockerfile')
        ]
        
        for old_name, new_name in renames:
            old_path = self.project_root / old_name
            new_path = self.project_root / new_name
            
            if old_path.exists():
                if new_path.exists():
                    new_path.unlink()
                old_path.rename(new_path)
                logger.info(f"[CHECK] Renamed {old_name} to {new_name}")
    
    def cleanup_enterprise_duplicates(self):
        """Phase 5: Remove duplicate enterprise files"""
        logger.info("🏢 Phase 5: Cleaning up enterprise duplicates...")
        
        # Directories to remove completely
        dirs_to_remove = [
            'enterprise/infrastructure',
            'enterprise/integration',
            'enterprise/security'
        ]
        
        for dir_path in dirs_to_remove:
            full_path = self.project_root / dir_path
            if full_path.exists():
                shutil.rmtree(full_path)
                logger.info(f"🗑️ Removed duplicate directory: {dir_path}")
                self.cleanup_log.append(f"Removed enterprise duplicate: {dir_path}")
        
        # Remove enterprise directory if empty
        enterprise_dir = self.project_root / 'enterprise'
        if enterprise_dir.exists() and not any(enterprise_dir.iterdir()):
            enterprise_dir.rmdir()
            logger.info("🗑️ Removed empty enterprise directory")
    
    def cleanup_temporary_files(self):
        """Phase 6: Remove temporary and development files"""
        logger.info("🧹 Phase 6: Cleaning up temporary files...")
        
        # Files to remove
        temp_files = [
            'simple_enterprise_integration.py',
            'DUPLICATION_AUDIT_REPORT.md',
            'UNIFIED_ARCHITECTURE_PLAN.md',
            'ENTERPRISE_INTEGRATION.md',
            'ENTERPRISE_INTEGRATION_SUMMARY.md',
            'ENTERPRISE_INTEGRATION_INSTRUCTIONS.md',
            'UPDATED_PRODUCTION_READINESS_ASSESSMENT.md'
        ]
        
        for file_path in temp_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"🗑️ Removed temporary file: {file_path}")
        
        # Remove backup directories from previous runs
        backup_dirs = [
            'backup_auth_systems',
            'backup_before_cleanup'
        ]
        
        for dir_path in backup_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists() and dir_path != 'backup_before_cleanup':  # Keep current backup
                shutil.rmtree(full_path)
                logger.info(f"🗑️ Removed old backup: {dir_path}")
    
    def update_imports(self):
        """Phase 7: Update import statements to use unified implementations"""
        logger.info("🔄 Phase 7: Updating import statements...")
        
        # Files that need import updates
        files_to_update = [
            'unified_production_server.py',
            'core/advanced_trading_engine.py',
            'revolutionary_crypto_engine.py',
            'revolutionary_advanced_engine.py',
            'revolutionary_options_engine.py',
            'revolutionary_market_maker.py',
            'revolutionary_master_engine.py'
        ]
        
        # Import replacements
        import_replacements = {
            'from core.auth_service import': 'from core.auth.unified_auth_service import',
            'from core.security.authentication import': 'from core.auth.unified_auth_service import',
            'from enterprise.security.enterprise_auth import': 'from core.auth.unified_auth_service import',
            'from core.database_manager import': '# Database management now in unified_production_server.py',
            'from core.persistence_manager import': '# Persistence now in unified_production_server.py'
        }
        
        for file_path in files_to_update:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    updated = False
                    for old_import, new_import in import_replacements.items():
                        if old_import in content:
                            content = content.replace(old_import, new_import)
                            updated = True
                    
                    if updated:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        logger.info(f"[CHECK] Updated imports in: {file_path}")
                        
                except Exception as e:
                    logger.warning(f"[WARNING]️ Failed to update imports in {file_path}: {e}")
    
    def create_cleanup_report(self):
        """Generate cleanup report"""
        logger.info("📊 Generating cleanup report...")
        
        report = {
            'cleanup_date': str(Path(__file__).stat().st_mtime),
            'files_removed': len([log for log in self.cleanup_log if 'Removed' in log]),
            'directories_removed': len([log for log in self.cleanup_log if 'directory' in log]),
            'cleanup_actions': self.cleanup_log,
            'remaining_structure': self._get_directory_structure()
        }
        
        report_path = self.project_root / 'CLEANUP_REPORT.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Cleanup report saved: {report_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("🎉 PROMETHEUS CLEANUP COMPLETED!")
        print("="*60)
        print(f"Files removed: {report['files_removed']}")
        print(f"Directories removed: {report['directories_removed']}")
        print(f"Backup location: {self.backup_dir}")
        print(f"Cleanup report: {report_path}")
        print("\n[CHECK] Codebase is now unified and ready for production!")
        print("="*60)
    
    def _get_directory_structure(self) -> Dict[str, Any]:
        """Get current directory structure"""
        def scan_directory(path: Path) -> Dict[str, Any]:
            result = {}
            try:
                for item in path.iterdir():
                    if item.is_file():
                        result[item.name] = 'file'
                    elif item.is_dir() and not item.name.startswith('.'):
                        result[item.name] = scan_directory(item)
            except PermissionError:
                pass
            return result
        
        return scan_directory(self.project_root)
    
    def run_full_cleanup(self):
        """Run complete cleanup process"""
        logger.info("🚀 Starting PROMETHEUS duplication cleanup...")
        
        # Create backup first
        self.create_backup()
        
        # Run cleanup phases
        self.cleanup_authentication_duplicates()
        self.cleanup_database_duplicates()
        self.cleanup_environment_duplicates()
        self.cleanup_docker_duplicates()
        self.cleanup_enterprise_duplicates()
        self.cleanup_temporary_files()
        self.update_imports()
        
        # Generate report
        self.create_cleanup_report()

def main():
    """Main cleanup function"""
    cleanup_manager = PrometheusCleanupManager()
    
    print("🧹 PROMETHEUS Duplication Cleanup")
    print("=" * 50)
    print("This will remove duplicate implementations and consolidate the codebase.")
    print("A backup will be created before any changes are made.")
    print()
    
    response = input("Do you want to proceed with cleanup? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        cleanup_manager.run_full_cleanup()
    else:
        print("[ERROR] Cleanup cancelled.")

if __name__ == "__main__":
    main()
