# PROMETHEUS Trading Platform — Installation (Windows)

This guide prepares a Windows host for local development or a pilot deployment.

## Prerequisites
- Windows 10/11 (PowerShell 5+ or PowerShell Core)
- Python 3.10+ on PATH
- Node.js 18+ and npm on PATH
- Git (optional)

## Clone / Open Project
- Project root: Desktop\PROMETHEUS-Trading-Platform

## Python Dependencies

If you use a virtual environment (recommended):

```powershell

python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

```

If no requirements.txt exists or packages are missing, install as needed using pip.

## Frontend Dependencies

```powershell

cd frontend
npm install
cd ..

```

## One‑click scripts

All scripts are in `scripts/windows/`:

- `start_all.ps1` — stop → start backend → start frontend → health check
- `stop_all.ps1` — kill Node/Python/cloudflared and free ports 8000/8001/3000/3001/3002
- `start_backend.ps1` — start FastAPI on 127.0.0.1:8000
- `start_frontend.ps1` — start React dev server on port 3000
- `health_check.ps1` — ping /health and /api/system/status and frontend root
- `cloudflare_tunnel.ps1` — start Cloudflare named tunnel for prometheus-trade.com

Run from PowerShell:

```powershell

# From project root

./scripts/windows/start_all.ps1

```

## Cloudflare (Public Access)

You already have config files:

- `cloudflare-tunnel-config.yml` (prometheus-trade.com, api.prometheus-trade.com, ws.prometheus-trade.com)
- `cloudflared.yml` (legacy/prometheus-trader.com)

To start the named tunnel (recommended):

```powershell

./scripts/windows/cloudflare_tunnel.ps1

```
```text
This requires Cloudflare Tunnel credentials to exist at the path referenced inside the config.

If you prefer a quick tunnel (temporary URL):

```powershell

./scripts/windows/cloudflare_tunnel.ps1 -Quick

```

## Verify
- Backend: http://127.0.0.1:8000/health
- API status: http://127.0.0.1:8000/api/system/status
- Frontend: http://127.0.0.1:3000
- Swagger: http://127.0.0.1:8000/docs

## Notes
- Do not run multiple backends on port 8000 simultaneously.
- Use `stop_all.ps1` before switching branches or restarting services.

