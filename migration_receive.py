"""
PROMETHEUS Migration Receiver
Run this on the NEW server to pull everything from the old machine over the home network.

Usage:
  python migration_receive.py --host 192.168.0.100

The old machine must be running:
  python migration_serve.py
"""

import os
import sys
import json
import time
import argparse
import urllib.request
from pathlib import Path

PORT = 9999
ROOT = Path(__file__).parent


def fetch_manifest(host):
    url = f"http://{host}:{PORT}/manifest"
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read())


def download_file(host, rel_path, dest_path, size_bytes):
    url = f"http://{host}:{PORT}/file/{rel_path}"
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists() and dest_path.stat().st_size == size_bytes:
        print(f"  [SKIP] Already complete: {rel_path}")
        return True

    start = time.time()
    downloaded = 0
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=300) as r, \
             open(dest_path, "wb") as f:
            while True:
                chunk = r.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)
                pct = downloaded / size_bytes * 100 if size_bytes else 0
                mb_s = downloaded / 1024 / 1024 / max(time.time() - start, 0.1)
                print(f"\r  {pct:5.1f}%  {downloaded/1024/1024:.0f}/{size_bytes/1024/1024:.0f}MB"
                      f"  {mb_s:.1f}MB/s  {rel_path}", end="", flush=True)
        print()
        elapsed = time.time() - start
        print(f"  [OK]  {size_bytes/1024/1024:.1f}MB in {elapsed:.0f}s"
              f"  ({size_bytes/1024/1024/elapsed:.1f}MB/s)")
        return True
    except Exception as e:
        print(f"\n  [ERR] {rel_path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True,
                        help="IP of the old machine running migration_serve.py")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    host = args.host
    global PORT
    PORT = args.port

    print("=" * 60)
    print("  PROMETHEUS Migration Receiver")
    print(f"  Connecting to http://{host}:{PORT}")
    print("=" * 60)

    # Fetch manifest
    print("\n  Fetching file manifest...")
    try:
        manifest = fetch_manifest(host)
    except Exception as e:
        print(f"\n  [ERR] Cannot reach {host}:{PORT} — {e}")
        print("  Make sure migration_serve.py is running on the old machine.")
        sys.exit(1)

    files = manifest["files"]
    total_mb = manifest["total_mb"]
    print(f"  {len(files)} files  ({total_mb:.0f}MB total)\n")

    for f in files:
        print(f"    {f['size_mb']:6.1f}MB  {f['path']}")

    print(f"\n  Starting download to: {ROOT}")
    print("  (Existing complete files will be skipped)\n")

    # Download each file
    ok = 0
    failed = []
    total_start = time.time()

    for f in files:
        dest = ROOT / f["path"]
        print(f"  Downloading: {f['path']}")
        success = download_file(host, f["path"], dest, f["size"])
        if success:
            ok += 1
        else:
            failed.append(f["path"])

    elapsed = time.time() - total_start
    total_received = sum(
        (ROOT / f["path"]).stat().st_size
        for f in files
        if (ROOT / f["path"]).exists()
    )

    print()
    print("=" * 60)
    print(f"  Transfer complete: {ok}/{len(files)} files")
    print(f"  Total received: {total_received/1024/1024:.0f}MB"
          f" in {elapsed/60:.1f}min"
          f" ({total_received/1024/1024/elapsed:.1f}MB/s avg)")

    if failed:
        print(f"\n  FAILED ({len(failed)}):")
        for f in failed:
            print(f"    {f}")
        print("\n  Re-run to retry failed files.")
    else:
        print("\n  All files transferred successfully!")
        print("\n  Next steps on this machine:")
        print("    1. pip install -r requirements.txt")
        print("    2. python download_knowledge_books.py")
        print("    3. python prometheus_knowledge_autodiscovery.py --now")
        print("    4. python prometheus_watchdog.py")

    print("=" * 60)


if __name__ == "__main__":
    main()
