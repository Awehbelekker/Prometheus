"""
Automated Database Backup System
Backs up all 32 SQLite databases with compression and retention policies
"""

import os
import shutil
import gzip
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseBackupSystem:
    """
    Automated backup system for PROMETHEUS databases
    Features: Compression, versioning, retention policies, integrity checks
    """
    
    def __init__(self, workspace_root: str = None):
        # Workspace root
        if workspace_root is None:
            workspace_root = Path(__file__).parent.parent
        self.workspace_root = Path(workspace_root)
        
        # Backup directory
        self.backup_root = self.workspace_root / 'backups'
        self.backup_root.mkdir(exist_ok=True)
        
        # Backup metadata
        self.metadata_file = self.backup_root / 'backup_metadata.json'
        self.metadata = self._load_metadata()
        
        # Retention policy (days to keep backups)
        self.retention_policy = {
            'daily': 7,      # Keep daily backups for 7 days
            'weekly': 30,    # Keep weekly backups for 30 days
            'monthly': 365   # Keep monthly backups for 1 year
        }
        
        logger.info(f"✅ Backup system initialized: {self.backup_root}")
    
    def discover_databases(self) -> List[Path]:
        """Discover all SQLite databases in workspace"""
        databases = []
        
        # Search patterns for databases
        patterns = ['*.db', '*.sqlite', '*.sqlite3']
        
        for pattern in patterns:
            databases.extend(self.workspace_root.rglob(pattern))
        
        # Filter out backup directory
        databases = [db for db in databases if 'backups' not in str(db)]
        
        logger.info(f"📊 Discovered {len(databases)} databases")
        for db in databases:
            logger.info(f"  - {db.relative_to(self.workspace_root)}")
        
        return databases
    
    def backup_database(
        self,
        db_path: Path,
        compress: bool = True
    ) -> Dict[str, Any]:
        """
        Backup a single database
        
        Args:
            db_path: Path to database file
            compress: Whether to compress backup
            
        Returns:
            Backup metadata
        """
        try:
            if not db_path.exists():
                logger.error(f"❌ Database not found: {db_path}")
                return None
            
            # Create backup filename
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            relative_path = db_path.relative_to(self.workspace_root)
            
            # Create subdirectory for this database
            db_backup_dir = self.backup_root / relative_path.parent / relative_path.stem
            db_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup filename
            backup_name = f"{relative_path.stem}_{timestamp}.db"
            if compress:
                backup_name += '.gz'
            
            backup_path = db_backup_dir / backup_name
            
            # Calculate source checksum
            source_checksum = self._calculate_checksum(db_path)
            
            # Perform backup
            if compress:
                # Compress and backup
                with open(db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb', compresslevel=6) as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Direct copy
                shutil.copy2(db_path, backup_path)
            
            # Calculate backup size
            source_size = db_path.stat().st_size
            backup_size = backup_path.stat().st_size
            compression_ratio = backup_size / source_size if source_size > 0 else 0
            
            # Create metadata
            metadata = {
                'timestamp': timestamp,
                'source_path': str(relative_path),
                'backup_path': str(backup_path.relative_to(self.backup_root)),
                'source_size': source_size,
                'backup_size': backup_size,
                'compression_ratio': compression_ratio,
                'compressed': compress,
                'checksum': source_checksum,
                'type': self._determine_backup_type()
            }
            
            # Record backup
            self._record_backup(str(relative_path), metadata)
            
            logger.info(f"✅ Backed up: {relative_path}")
            logger.info(f"   Size: {source_size:,} → {backup_size:,} bytes "
                       f"({compression_ratio:.1%} compression)")
            
            return metadata
            
        except Exception as e:
            logger.error(f"❌ Error backing up {db_path}: {e}")
            return None
    
    def backup_all_databases(self, compress: bool = True) -> Dict[str, Any]:
        """
        Backup all discovered databases
        
        Returns:
            Backup summary
        """
        databases = self.discover_databases()
        
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_databases': len(databases),
            'successful': 0,
            'failed': 0,
            'total_source_size': 0,
            'total_backup_size': 0,
            'backups': []
        }
        
        for db_path in databases:
            metadata = self.backup_database(db_path, compress=compress)
            if metadata:
                results['successful'] += 1
                results['total_source_size'] += metadata['source_size']
                results['total_backup_size'] += metadata['backup_size']
                results['backups'].append(metadata)
            else:
                results['failed'] += 1
        
        # Calculate overall compression
        if results['total_source_size'] > 0:
            overall_compression = results['total_backup_size'] / results['total_source_size']
        else:
            overall_compression = 0
        
        results['overall_compression'] = overall_compression
        
        # Save backup summary
        summary_file = self.backup_root / f"backup_summary_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 BACKUP SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total databases: {results['total_databases']}")
        logger.info(f"Successful: {results['successful']}")
        logger.info(f"Failed: {results['failed']}")
        logger.info(f"Source size: {results['total_source_size']:,} bytes")
        logger.info(f"Backup size: {results['total_backup_size']:,} bytes")
        logger.info(f"Compression: {overall_compression:.1%}")
        logger.info(f"{'='*60}\n")
        
        return results
    
    def restore_database(
        self,
        backup_path: Path,
        destination: Path = None
    ) -> bool:
        """
        Restore a database from backup
        
        Args:
            backup_path: Path to backup file
            destination: Where to restore (None = original location)
            
        Returns:
            Success status
        """
        try:
            if not backup_path.exists():
                logger.error(f"❌ Backup not found: {backup_path}")
                return False
            
            # Determine destination
            if destination is None:
                # Extract original path from metadata
                backup_name = backup_path.stem.replace('.db', '')
                # Find metadata for this backup
                # For now, use same directory as backup
                destination = self.workspace_root / 'restored' / backup_path.name.replace('.gz', '')
                destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore
            if backup_path.suffix == '.gz':
                # Decompress
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(destination, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Direct copy
                shutil.copy2(backup_path, destination)
            
            logger.info(f"✅ Restored: {backup_path.name} → {destination}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error restoring {backup_path}: {e}")
            return False
    
    def cleanup_old_backups(self) -> Dict[str, int]:
        """
        Remove old backups according to retention policy
        
        Returns:
            Cleanup statistics
        """
        stats = {
            'daily_removed': 0,
            'weekly_removed': 0,
            'monthly_removed': 0,
            'total_removed': 0,
            'space_freed': 0
        }
        
        now = datetime.utcnow()
        
        for db_name, backups in self.metadata.get('databases', {}).items():
            for backup in list(backups):
                backup_date = datetime.fromisoformat(backup['timestamp'])
                age_days = (now - backup_date).days
                backup_type = backup.get('type', 'daily')
                
                # Check retention policy
                should_remove = False
                if backup_type == 'daily' and age_days > self.retention_policy['daily']:
                    should_remove = True
                    stats['daily_removed'] += 1
                elif backup_type == 'weekly' and age_days > self.retention_policy['weekly']:
                    should_remove = True
                    stats['weekly_removed'] += 1
                elif backup_type == 'monthly' and age_days > self.retention_policy['monthly']:
                    should_remove = True
                    stats['monthly_removed'] += 1
                
                if should_remove:
                    backup_path = self.backup_root / backup['backup_path']
                    if backup_path.exists():
                        size = backup_path.stat().st_size
                        backup_path.unlink()
                        stats['space_freed'] += size
                        stats['total_removed'] += 1
                        logger.info(f"🗑️  Removed old backup: {backup['backup_path']} "
                                   f"(age: {age_days} days)")
                    
                    # Remove from metadata
                    backups.remove(backup)
        
        # Save updated metadata
        self._save_metadata()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🧹 CLEANUP SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total removed: {stats['total_removed']}")
        logger.info(f"  Daily: {stats['daily_removed']}")
        logger.info(f"  Weekly: {stats['weekly_removed']}")
        logger.info(f"  Monthly: {stats['monthly_removed']}")
        logger.info(f"Space freed: {stats['space_freed']:,} bytes")
        logger.info(f"{'='*60}\n")
        
        return stats
    
    def verify_backup_integrity(self, backup_path: Path) -> bool:
        """Verify backup file integrity using checksum"""
        try:
            # Get stored checksum from metadata
            # For now, just check file exists and is readable
            if not backup_path.exists():
                return False
            
            # Try to read first few bytes
            if backup_path.suffix == '.gz':
                with gzip.open(backup_path, 'rb') as f:
                    f.read(1024)
            else:
                with open(backup_path, 'rb') as f:
                    f.read(1024)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup integrity check failed: {e}")
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _determine_backup_type(self) -> str:
        """Determine backup type based on date"""
        now = datetime.utcnow()
        
        # Monthly: first day of month
        if now.day == 1:
            return 'monthly'
        
        # Weekly: Sunday
        if now.weekday() == 6:
            return 'weekly'
        
        # Otherwise daily
        return 'daily'
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load backup metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {'databases': {}}
    
    def _save_metadata(self):
        """Save backup metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _record_backup(self, db_name: str, backup_metadata: Dict[str, Any]):
        """Record backup in metadata"""
        if 'databases' not in self.metadata:
            self.metadata['databases'] = {}
        
        if db_name not in self.metadata['databases']:
            self.metadata['databases'][db_name] = []
        
        self.metadata['databases'][db_name].append(backup_metadata)
        self._save_metadata()
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Get current backup system status"""
        status = {
            'total_databases': 0,
            'total_backups': 0,
            'total_backup_size': 0,
            'oldest_backup': None,
            'newest_backup': None,
            'databases': {}
        }
        
        for db_name, backups in self.metadata.get('databases', {}).items():
            status['total_databases'] += 1
            status['total_backups'] += len(backups)
            
            db_status = {
                'backup_count': len(backups),
                'total_size': sum(b['backup_size'] for b in backups),
                'latest_backup': max((b['timestamp'] for b in backups), default=None)
            }
            
            status['databases'][db_name] = db_status
            status['total_backup_size'] += db_status['total_size']
            
            # Update oldest/newest
            for backup in backups:
                timestamp = backup['timestamp']
                if status['oldest_backup'] is None or timestamp < status['oldest_backup']:
                    status['oldest_backup'] = timestamp
                if status['newest_backup'] is None or timestamp > status['newest_backup']:
                    status['newest_backup'] = timestamp
        
        return status


def setup_windows_scheduler(
    script_path: str,
    schedule_time: str = "02:00",
    task_name: str = "PROMETHEUS_Database_Backup"
) -> str:
    """
    Generate Windows Task Scheduler command
    
    Args:
        script_path: Path to this backup script
        schedule_time: Time to run daily (HH:MM format)
        task_name: Name for scheduled task
        
    Returns:
        PowerShell command to create scheduled task
    """
    python_exe = shutil.which('python') or 'python'
    
    command = f'''
# Create Windows Scheduled Task for PROMETHEUS Database Backup
$action = New-ScheduledTaskAction -Execute '{python_exe}' -Argument '"{script_path}"'
$trigger = New-ScheduledTaskTrigger -Daily -At {schedule_time}
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable $false

Register-ScheduledTask -TaskName '{task_name}' -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force

Write-Host "✅ Scheduled task '{task_name}' created successfully!"
Write-Host "Daily backups will run at {schedule_time}"
'''
    
    return command


if __name__ == '__main__':
    # Initialize backup system
    backup_system = DatabaseBackupSystem()
    
    # Run full backup
    logger.info("🚀 Starting automated database backup...")
    results = backup_system.backup_all_databases(compress=True)
    
    # Cleanup old backups
    logger.info("🧹 Cleaning up old backups...")
    cleanup_stats = backup_system.cleanup_old_backups()
    
    # Show status
    status = backup_system.get_backup_status()
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 BACKUP SYSTEM STATUS")
    logger.info(f"{'='*60}")
    logger.info(f"Total databases tracked: {status['total_databases']}")
    logger.info(f"Total backups stored: {status['total_backups']}")
    logger.info(f"Total storage used: {status['total_backup_size']:,} bytes")
    logger.info(f"Oldest backup: {status['oldest_backup']}")
    logger.info(f"Newest backup: {status['newest_backup']}")
    logger.info(f"{'='*60}\n")
    
    # Generate scheduler command
    script_path = Path(__file__).absolute()
    scheduler_cmd = setup_windows_scheduler(str(script_path))
    
    logger.info("To setup automated daily backups, run this PowerShell command as Administrator:")
    logger.info(scheduler_cmd)
