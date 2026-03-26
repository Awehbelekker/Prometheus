# PROMETHEUS Operations Guide (Windows)

## Start/Stop
- Start everything:

  ```powershell

  ./scripts/windows/start_all.ps1

  ```
```text

- Stop everything and free ports:

  ```powershell

  ./scripts/windows/stop_all.ps1

  ```

## Health Checks
- Local health summary:

  ```powershell

  ./scripts/windows/health_check.ps1

  ```
```text

- Direct:
  - Backend health: http://127.0.0.1:8000/health
  - System status: http://127.0.0.1:8000/api/system/status
  - Frontend: http://127.0.0.1:3000

## Cloudflare Tunnel
- Named tunnel for prometheus-trade.com:

  ```powershell

  ./scripts/windows/cloudflare_tunnel.ps1

  ```
```python
  Expected routes (from cloudflare-tunnel-config.yml):

  - https://prometheus-trade.com → http://localhost:3000
  - https://api.prometheus-trade.com → http://localhost:8000
  - wss://ws.prometheus-trade.com → ws://localhost:8000

- Quick tunnel (temporary URL):

  ```powershell

  ./scripts/windows/cloudflare_tunnel.ps1 -Quick

  ```

## Logs and Monitoring
- Backend (uvicorn) runs hidden; bring to foreground by launching manually:

  ```powershell

  python -m uvicorn unified_production_server:app --host 127.0.0.1 --port 8000 --log-level info

  ```
```text

- Frontend logs appear in the terminal started by `npm start`.
- Cloudflare tunnel logs appear in its terminal if launched interactively.

## Backup and Recovery (local)
- Database: ensure snapshots of your SQLite/DB files before upgrading.
- Configs: back up `.env` files and `cloudflare-*.yml` configs.

## Maintenance
- Apply updates when services are stopped (`stop_all.ps1`).
- Validate with `health_check.ps1` before exposing via Cloudflare.

## Troubleshooting
- Port in use (WinError 10048): run `stop_all.ps1` to free ports.
- 502/host not reachable via Cloudflare: verify local health, then DNS and tunnel status.
- Admin endpoints require header `X-Admin-ID: admin_prometheus_001` for privileged routes.

