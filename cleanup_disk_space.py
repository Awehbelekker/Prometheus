"""Disk Cleanup for Prometheus Trading Platform"""
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def get_size_mb(path):
    """Get size of file or folder in MB"""
    if os.path.isfile(path):
        return os.path.getsize(path) / (1024 * 1024)
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except:
                pass
    return total / (1024 * 1024)

def cleanup_prometheus():
    """Clean up unnecessary files from Prometheus platform"""
    
    print("=" * 60)
    print("  PROMETHEUS DISK CLEANUP")
    print("=" * 60)
    
    base_path = Path(r"C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform")
    total_freed = 0
    
    # 1. Clean old log files (keep last 7 days)
    print("\n📁 Cleaning old log files...")
    logs_path = base_path / "logs"
    if logs_path.exists():
        cutoff = datetime.now() - timedelta(days=7)
        log_freed = 0
        for log_file in logs_path.glob("*.log"):
            try:
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if mtime < cutoff:
                    size = log_file.stat().st_size / (1024 * 1024)
                    log_file.unlink()
                    log_freed += size
                    print(f"   Deleted: {log_file.name} ({size:.1f} MB)")
            except Exception as e:
                pass
        total_freed += log_freed
        print(f"   Freed: {log_freed:.1f} MB from logs")
    
    # 2. Clean __pycache__ directories
    print("\n📁 Cleaning Python cache...")
    cache_freed = 0
    for cache_dir in base_path.rglob("__pycache__"):
        try:
            size = get_size_mb(cache_dir)
            shutil.rmtree(cache_dir)
            cache_freed += size
        except:
            pass
    total_freed += cache_freed
    print(f"   Freed: {cache_freed:.1f} MB from __pycache__")
    
    # 3. Clean .pyc files
    print("\n📁 Cleaning .pyc files...")
    pyc_freed = 0
    for pyc_file in base_path.rglob("*.pyc"):
        try:
            size = pyc_file.stat().st_size / (1024 * 1024)
            pyc_file.unlink()
            pyc_freed += size
        except:
            pass
    total_freed += pyc_freed
    print(f"   Freed: {pyc_freed:.1f} MB from .pyc files")
    
    # 4. Find large files that might be candidates for cleanup
    print("\n📊 Large files in workspace:")
    large_files = []
    for f in base_path.rglob("*"):
        if f.is_file():
            try:
                size = f.stat().st_size / (1024 * 1024)
                if size > 50:  # Files > 50MB
                    large_files.append((f, size))
            except:
                pass
    
    large_files.sort(key=lambda x: x[1], reverse=True)
    for f, size in large_files[:10]:
        rel_path = f.relative_to(base_path)
        print(f"   {size:>8.1f} MB: {rel_path}")
    
    # 5. Clean old backup files
    print("\n📁 Checking backup/archive folders...")
    archive_size = 0
    archive_path = base_path / "ARCHIVE_2025_10_20"
    if archive_path.exists():
        archive_size = get_size_mb(archive_path)
        print(f"   Archive folder: {archive_size:.1f} MB")
        print(f"   (Run with --delete-archive to remove)")
    
    # 6. Clean temp files
    print("\n📁 Cleaning temp files...")
    temp_patterns = ["*.tmp", "*.temp", "*~", "*.bak"]
    temp_freed = 0
    for pattern in temp_patterns:
        for f in base_path.rglob(pattern):
            try:
                size = f.stat().st_size / (1024 * 1024)
                f.unlink()
                temp_freed += size
            except:
                pass
    total_freed += temp_freed
    print(f"   Freed: {temp_freed:.1f} MB from temp files")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"  TOTAL FREED: {total_freed:.1f} MB")
    print("=" * 60)
    
    # System-wide suggestions
    print("\n💡 ADDITIONAL CLEANUP SUGGESTIONS:")
    print("   1. Run Windows Disk Cleanup: cleanmgr")
    print("   2. Clear Windows temp: %TEMP%")
    print("   3. Clear Ollama cache if not using models")
    print("   4. Uninstall unused programs")
    
    return total_freed

if __name__ == "__main__":
    import sys
    
    # Check disk before
    import psutil
    disk_before = psutil.disk_usage('C:\\')
    print(f"\n💾 Disk BEFORE: {disk_before.percent:.1f}% used ({disk_before.free / (1024**3):.1f} GB free)")
    
    freed = cleanup_prometheus()
    
    # Check disk after
    disk_after = psutil.disk_usage('C:\\')
    print(f"\n💾 Disk AFTER: {disk_after.percent:.1f}% used ({disk_after.free / (1024**3):.1f} GB free)")
    
    # Delete archive if requested
    if "--delete-archive" in sys.argv:
        archive_path = Path(r"C:\Users\Judy\Desktop\PROMETHEUS-Trading-Platform\ARCHIVE_2025_10_20")
        if archive_path.exists():
            print(f"\n⚠️ Deleting archive folder...")
            shutil.rmtree(archive_path)
            print("✅ Archive deleted!")
