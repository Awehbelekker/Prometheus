#!/usr/bin/env python3
"""
Set Up Log Rotation for Prometheus
Prevents log files from growing too large
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_log_rotation():
    """Set up log rotation for all loggers"""
    print("=" * 80)
    print("SETTING UP LOG ROTATION")
    print("=" * 80)
    print()
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger with rotation
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create rotating file handler
    log_file = logs_dir / "prometheus.log"
    handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    
    # Set format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    print(f"[OK] Log rotation configured")
    print(f"     Log file: {log_file}")
    print(f"     Max size: 10 MB per file")
    print(f"     Backups: 5 files")
    print(f"     Total max: 50 MB")
    print()
    
    # Create example configuration file
    config_content = """# Log Rotation Configuration
# This file documents the log rotation settings

LOG_FILE=logs/prometheus.log
MAX_BYTES=10485760  # 10 MB
BACKUP_COUNT=5
LOG_LEVEL=INFO

# Log files will rotate when they reach 10 MB
# Old logs are kept as: prometheus.log.1, prometheus.log.2, etc.
# Only the 5 most recent backups are kept
"""
    
    config_file = Path("log_rotation_config.txt")
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"[OK] Configuration file created: {config_file}")
    print()
    print("=" * 80)
    print("Log rotation setup complete!")
    print("=" * 80)

if __name__ == "__main__":
    setup_log_rotation()

