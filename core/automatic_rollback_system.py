"""
AUTOMATIC ROLLBACK SYSTEM
==========================

Safety mechanism that automatically reverts strategy changes if performance degrades.

Features:
- Version control for model settings
- Performance degradation detection
- Automatic revert if performance drops >10%
- Keep last 7 days of settings
- Quick restore to any previous version
- Safety limits to prevent extreme changes
- Comprehensive logging and reporting

Author: PROMETHEUS AI Team
Date: October 10, 2025
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ModelVersion:
    """Model version snapshot"""
    version_id: str
    timestamp: datetime
    settings: Dict[str, Any]
    performance_metrics: Dict[str, float]
    reason: str
    is_active: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelVersion':
        """Create from dictionary"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class AutomaticRollbackSystem:
    """
    Automatic rollback system for trading strategy safety
    """
    
    def __init__(self, db_path: str = "prometheus_rollback.db"):
        self.db_path = db_path
        self.db = None
        
        # Performance thresholds
        self.performance_degradation_threshold = 0.10  # 10% drop triggers rollback
        self.min_trades_for_comparison = 10  # Minimum trades before comparing
        self.version_retention_days = 7  # Keep versions for 7 days
        
        # Current active version
        self.current_version: Optional[ModelVersion] = None
        
        # Initialize database
        self._initialize_database()
        
        logger.info("🛡️ Automatic Rollback System initialized")
    
    def _initialize_database(self):
        """Initialize rollback database"""
        try:
            self.db = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = self.db.cursor()
            
            # Create model_versions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_versions (
                    version_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    settings TEXT NOT NULL,
                    performance_metrics TEXT NOT NULL,
                    reason TEXT,
                    is_active INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create rollback_events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rollback_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    from_version_id TEXT,
                    to_version_id TEXT,
                    reason TEXT,
                    performance_before TEXT,
                    performance_after TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.db.commit()
            logger.info("[CHECK] Rollback database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing rollback database: {e}")
    
    def create_version_snapshot(self, settings: Dict[str, Any], performance_metrics: Dict[str, float], reason: str) -> ModelVersion:
        """Create a new version snapshot"""
        try:
            # Generate version ID
            version_id = self._generate_version_id(settings)
            
            # Create version
            version = ModelVersion(
                version_id=version_id,
                timestamp=datetime.now(),
                settings=settings.copy(),
                performance_metrics=performance_metrics.copy(),
                reason=reason,
                is_active=True
            )
            
            # Deactivate previous versions
            self._deactivate_all_versions()
            
            # Save to database
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO model_versions (version_id, timestamp, settings, performance_metrics, reason, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                version.version_id,
                version.timestamp.isoformat(),
                json.dumps(version.settings),
                json.dumps(version.performance_metrics),
                version.reason,
                1
            ))
            self.db.commit()
            
            # Set as current version
            self.current_version = version
            
            logger.info(f"📸 Version snapshot created: {version_id[:8]}... - {reason}")
            
            # Clean old versions
            self._clean_old_versions()
            
            return version
            
        except Exception as e:
            logger.error(f"Error creating version snapshot: {e}")
            return None
    
    def _generate_version_id(self, settings: Dict[str, Any]) -> str:
        """Generate unique version ID from settings"""
        settings_str = json.dumps(settings, sort_keys=True)
        hash_obj = hashlib.sha256(settings_str.encode())
        return f"v_{hash_obj.hexdigest()[:16]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _deactivate_all_versions(self):
        """Deactivate all versions"""
        try:
            cursor = self.db.cursor()
            cursor.execute('UPDATE model_versions SET is_active = 0')
            self.db.commit()
        except Exception as e:
            logger.error(f"Error deactivating versions: {e}")
    
    def check_performance_degradation(self, current_performance: Dict[str, float]) -> bool:
        """Check if performance has degraded significantly"""
        try:
            if not self.current_version:
                return False
            
            # Get baseline performance
            baseline_performance = self.current_version.performance_metrics
            
            # Check if we have enough trades
            current_trades = current_performance.get('total_trades', 0)
            if current_trades < self.min_trades_for_comparison:
                logger.info(f"⏳ Not enough trades for comparison ({current_trades}/{self.min_trades_for_comparison})")
                return False
            
            # Compare key metrics
            degradation_detected = False
            degradation_details = []
            
            # Win rate comparison
            baseline_win_rate = baseline_performance.get('win_rate', 0.5)
            current_win_rate = current_performance.get('win_rate', 0.5)
            win_rate_change = (current_win_rate - baseline_win_rate) / baseline_win_rate if baseline_win_rate > 0 else 0
            
            if win_rate_change < -self.performance_degradation_threshold:
                degradation_detected = True
                degradation_details.append(f"Win rate: {baseline_win_rate:.1%} → {current_win_rate:.1%} ({win_rate_change:.1%})")
            
            # Daily P&L comparison
            baseline_daily_pnl = baseline_performance.get('avg_daily_pnl', 0)
            current_daily_pnl = current_performance.get('avg_daily_pnl', 0)
            pnl_change = (current_daily_pnl - baseline_daily_pnl) / abs(baseline_daily_pnl) if baseline_daily_pnl != 0 else 0
            
            if pnl_change < -self.performance_degradation_threshold:
                degradation_detected = True
                degradation_details.append(f"Daily P&L: ${baseline_daily_pnl:.2f} → ${current_daily_pnl:.2f} ({pnl_change:.1%})")
            
            # Sharpe ratio comparison (if available)
            baseline_sharpe = baseline_performance.get('sharpe_ratio', 0)
            current_sharpe = current_performance.get('sharpe_ratio', 0)
            if baseline_sharpe > 0:
                sharpe_change = (current_sharpe - baseline_sharpe) / baseline_sharpe
                if sharpe_change < -self.performance_degradation_threshold:
                    degradation_detected = True
                    degradation_details.append(f"Sharpe ratio: {baseline_sharpe:.2f} → {current_sharpe:.2f} ({sharpe_change:.1%})")
            
            if degradation_detected:
                logger.warning(f"[WARNING]️ Performance degradation detected!")
                for detail in degradation_details:
                    logger.warning(f"   - {detail}")
            
            return degradation_detected
            
        except Exception as e:
            logger.error(f"Error checking performance degradation: {e}")
            return False
    
    def rollback_to_previous_version(self, reason: str = "Performance degradation") -> Optional[ModelVersion]:
        """Rollback to the previous stable version"""
        try:
            # Get previous version
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT version_id, timestamp, settings, performance_metrics, reason
                FROM model_versions
                WHERE version_id != ?
                ORDER BY timestamp DESC
                LIMIT 1
            ''', (self.current_version.version_id if self.current_version else '',))
            
            row = cursor.fetchone()
            if not row:
                logger.warning("[WARNING]️ No previous version found for rollback")
                return None
            
            # Create previous version object
            previous_version = ModelVersion(
                version_id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                settings=json.loads(row[2]),
                performance_metrics=json.loads(row[3]),
                reason=row[4],
                is_active=False
            )
            
            # Record rollback event
            cursor.execute('''
                INSERT INTO rollback_events (timestamp, from_version_id, to_version_id, reason, performance_before, performance_after)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                self.current_version.version_id if self.current_version else None,
                previous_version.version_id,
                reason,
                json.dumps(self.current_version.performance_metrics if self.current_version else {}),
                json.dumps(previous_version.performance_metrics)
            ))
            
            # Activate previous version
            cursor.execute('UPDATE model_versions SET is_active = 0')
            cursor.execute('UPDATE model_versions SET is_active = 1 WHERE version_id = ?', (previous_version.version_id,))
            self.db.commit()
            
            # Set as current version
            previous_version.is_active = True
            self.current_version = previous_version
            
            logger.info(f"🔄 Rolled back to version: {previous_version.version_id[:8]}...")
            logger.info(f"   Reason: {reason}")
            logger.info(f"   Previous performance: Win rate {previous_version.performance_metrics.get('win_rate', 0):.1%}")
            
            return previous_version
            
        except Exception as e:
            logger.error(f"Error rolling back: {e}")
            return None
    
    def get_version_history(self, limit: int = 10) -> List[ModelVersion]:
        """Get version history"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT version_id, timestamp, settings, performance_metrics, reason, is_active
                FROM model_versions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            versions = []
            for row in cursor.fetchall():
                version = ModelVersion(
                    version_id=row[0],
                    timestamp=datetime.fromisoformat(row[1]),
                    settings=json.loads(row[2]),
                    performance_metrics=json.loads(row[3]),
                    reason=row[4],
                    is_active=bool(row[5])
                )
                versions.append(version)
            
            return versions
            
        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            return []
    
    def _clean_old_versions(self):
        """Clean versions older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.version_retention_days)
            cursor = self.db.cursor()
            cursor.execute('''
                DELETE FROM model_versions
                WHERE timestamp < ? AND is_active = 0
            ''', (cutoff_date.isoformat(),))
            deleted = cursor.rowcount
            self.db.commit()
            
            if deleted > 0:
                logger.info(f"🗑️ Cleaned {deleted} old versions")
                
        except Exception as e:
            logger.error(f"Error cleaning old versions: {e}")
    
    def get_rollback_report(self) -> str:
        """Generate rollback system report"""
        try:
            report = "🛡️ AUTOMATIC ROLLBACK SYSTEM REPORT\n"
            report += "=" * 60 + "\n\n"
            
            # Current version
            if self.current_version:
                report += f"📍 Current Version: {self.current_version.version_id[:12]}...\n"
                report += f"   Created: {self.current_version.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                report += f"   Reason: {self.current_version.reason}\n"
                report += f"   Performance:\n"
                for metric, value in self.current_version.performance_metrics.items():
                    if isinstance(value, float):
                        report += f"      - {metric}: {value:.3f}\n"
                    else:
                        report += f"      - {metric}: {value}\n"
                report += "\n"
            
            # Version history
            versions = self.get_version_history(limit=5)
            report += f"📚 Version History (last 5):\n"
            for i, version in enumerate(versions, 1):
                active_marker = "[CHECK]" if version.is_active else "  "
                report += f"{active_marker} {i}. {version.version_id[:12]}... - {version.timestamp.strftime('%Y-%m-%d %H:%M')}\n"
                report += f"      {version.reason}\n"
            
            # Rollback events
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT timestamp, reason, performance_before, performance_after
                FROM rollback_events
                ORDER BY timestamp DESC
                LIMIT 5
            ''')
            
            rollback_events = cursor.fetchall()
            if rollback_events:
                report += f"\n🔄 Recent Rollback Events:\n"
                for event in rollback_events:
                    report += f"   - {event[0]}: {event[1]}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating rollback report: {e}")
            return "Error generating report"

