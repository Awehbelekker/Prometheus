# Production reverse proxy setup for /real-data

Goal: keep a single browser base URL (main backend on port 8000) while forwarding Real Data API calls to the Real Data service (port 8002) using the path prefix /real-data/.

Two recommended options

1) App/backend proxy (already implemented)

- unified_production_server.py exposes /real-data/{path} and forwards to REALDATA_API_BASE (default http://localhost:8002)
- Enable via env:
  - ENABLE_REALDATA_PROXY=1
  - REALDATA_API_BASE=http://localhost:8002
- Frontend calls e.g. /real-data/api/admin/dashboard and the backend relays to 8002
- Pros: simplest, no extra infra needed; consistent auth/cookies; single origin; no CORS
- Cons: adds load to backend; large downloads pass through backend unless you opt for edge proxy

2) Edge/web proxy (Nginx, Caddy, or Cloudflare)

- Map /real-data/* to the Real Data service directly at the edge while keeping the same public host. Backend continues to serve everything else.
- Pros: offloads traffic from backend; supports large downloads/streaming directly from 8002; still single origin in the browser
- Cons: needs gateway/reverse proxy configuration

Nginx example

Upstreams and server block for a single host that proxies / to backend:8000 and /real-data/ to realdata:8002.

upstream backend {
  server 127.0.0.1:8000;
}

upstream realdata {
  server 127.0.0.1:8002;
}

server {
  listen 80;
  server_name prometheus-trade.local; # change to your domain
  client_max_body_size 50m;

  # Main backend (serves API and optionally static frontend)
  location / {
    proxy_pass http://backend;
    include proxy_params;               # if available, otherwise set headers below
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_read_timeout 60s;
  }

  # Real Data API via path prefix
  location /real-data/ {
    # Strip prefix when passing to upstream by keeping trailing slash
    proxy_pass http://realdata/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_http_version 1.1;
    proxy_buffering off;                # optional for streaming
    proxy_read_timeout 120s;
  }
}

Caddy example

:80 {
  encode gzip

  handle_path /real-data/* {
    reverse_proxy 127.0.0.1:8002
  }

  handle {
    reverse_proxy 127.0.0.1:8000
  }
}

Cloudflare options

- If you front a single origin (backend on 8000) with Cloudflare, prefer the in-app backend proxy (option 1). It keeps config simple and avoids Worker maintenance.
- If you want to offload large /real-data/ downloads, a Worker can re-route only that path to the Real Data origin. Example Worker (adjust host):

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname.startsWith('/real-data/')) {
      // Forward the same path to the Real Data origin
      // Replace with your internal service DNS/hostname (not localhost)
      url.hostname = 'realdata.internal.example.com';
      url.protocol = 'https:'; // or 'http:' if needed
      // Keep the path and query string as-is
      const init = {
        method: request.method,
        headers: new Headers(request.headers),
        body: request.method === 'GET' || request.method === 'HEAD' ? undefined : await request.clone().arrayBuffer(),
        redirect: 'follow'
      };
      const hop = ['connection','keep-alive','proxy-authenticate','proxy-authorization','te','trailers','transfer-encoding','upgrade'];
      hop.forEach(h => init.headers.delete(h));
      return fetch(url.toString(), init);
    }
    // Default: go to your primary origin
    return fetch(request);
  }
}

Security and ops notes

- Single origin in browser means no CORS issues.
- Validate auth at the backend for /real-data if needed; edge proxy will simply forward.
- Rate-limit /real-data endpoints if they are expensive.
- Set suitable timeouts for streaming or large payloads.
- Keep REALDATA_API_BASE private/non-public where possible; access it via internal network routing.

Frontend usage recap

- Always call the Real Data endpoints via /real-data prefix:
  - GET /real-data/api/admin/dashboard
  - GET /real-data/api/user/sessions
  - POST /real-data/api/paper-trading/create-portfolio
- The app already provides helpers that use the proxy by default.

Docker-compose quickstart (local)

- Requirements: Docker Desktop
- From repo root, run: docker compose -f docker-compose.nginx.yml up --build
- Services:
  - backend: http://localhost:8000 (FastAPI, proxies /real-data/*)
  - realdata: http://localhost:8002 (Real Data API)
  - nginx: http://localhost:8080 (edge proxy: / -> backend, /real-data/ -> realdata)
- Frontend should point to http://localhost:8000 (or to Nginx 8080 if you prefer the edge proxy).

Validation

- With services running (local or docker-compose), run the smoke test:

```
```text
python scripts/smoke_check.py

```

- Success prints "Smoke check passed." and returns exit code 0. Failures list which target failed.
