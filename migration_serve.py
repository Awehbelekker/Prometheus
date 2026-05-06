"""
PROMETHEUS Migration Server
Run this on the OLD machine to serve files to the new server over the home network.

Usage:
  python migration_serve.py

Then on the NEW server run:
  python migration_receive.py --host 192.168.0.100
"""

import os
import json
import socket
import hashlib
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote

ROOT = Path(__file__).parent
PORT = 9999

# Files and directories to serve for migration
MIGRATION_MANIFEST = [
    # HRM trained model (critical — 85 epochs)
    "hrm_checkpoints/market_finetuned/checkpoint.pt",
    "hrm_checkpoints/market_finetuned/head_only.pt",
    "hrm_checkpoints/market_finetuned/all_config.yaml",
    "hrm_checkpoints/market_finetuned/finetune_meta.json",
    "hrm_checkpoints/market_finetuned/checkpoint",
    "hrm_checkpoints/market_finetuned/PROMOTION_COMPLETE.txt",
    # Databases
    "prometheus_learning.db",
    "performance_metrics.db",
    "portfolio_persistence.db",
    "paper_trading.db",
    # Signal weights and cache
    "ai_signal_weights_config.json",
    "prometheus_real_hrm_signal_cache.npz",
]

# Also include any .db files in databases/ subdirectory
for db in ROOT.glob("databases/*.db"):
    rel = str(db.relative_to(ROOT)).replace("\\", "/")
    if rel not in MIGRATION_MANIFEST:
        MIGRATION_MANIFEST.append(rel)


def build_manifest():
    """Build manifest of files that actually exist with sizes and checksums."""
    manifest = []
    total_bytes = 0
    for rel_path in MIGRATION_MANIFEST:
        p = ROOT / rel_path
        if p.exists() and p.is_file():
            size = p.stat().st_size
            total_bytes += size
            manifest.append({
                "path": rel_path.replace("\\", "/"),
                "size": size,
                "size_mb": round(size / 1024 / 1024, 1),
            })
        else:
            print(f"  [SKIP] Not found: {rel_path}")
    return manifest, total_bytes


class MigrationHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Only log file downloads, not manifest requests
        if "/file/" in self.path:
            mb = ""
            print(f"  -> {unquote(self.path.replace('/file/', ''))} {args[1]}")

    def do_GET(self):
        path = unquote(self.path)

        if path == "/manifest":
            manifest, total = build_manifest()
            body = json.dumps({
                "files": manifest,
                "total_mb": round(total / 1024 / 1024, 1),
                "total_gb": round(total / 1024 / 1024 / 1024, 2),
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)

        elif path.startswith("/file/"):
            rel = path[6:]  # strip /file/
            file_path = ROOT / rel
            if not file_path.exists() or not file_path.is_file():
                self.send_response(404)
                self.end_headers()
                return
            # Security: ensure path is inside ROOT
            try:
                file_path.resolve().relative_to(ROOT.resolve())
            except ValueError:
                self.send_response(403)
                self.end_headers()
                return

            size = file_path.stat().st_size
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", size)
            self.end_headers()
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 1024):  # 1MB chunks
                    self.wfile.write(chunk)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    # Get local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    manifest, total_bytes = build_manifest()

    print("=" * 60)
    print("  PROMETHEUS Migration Server")
    print("=" * 60)
    print(f"\n  Serving {len(manifest)} files  ({total_bytes/1024/1024:.0f} MB total)\n")
    for f in manifest:
        print(f"    {f['size_mb']:6.1f}MB  {f['path']}")
    print()
    print(f"  Server ready at: http://{local_ip}:{PORT}")
    print()
    print("  On the NEW server, run:")
    print(f"    python migration_receive.py --host {local_ip}")
    print()
    print("  Press Ctrl+C to stop after transfer completes.")
    print("=" * 60)

    server = HTTPServer(("0.0.0.0", PORT), MigrationHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
