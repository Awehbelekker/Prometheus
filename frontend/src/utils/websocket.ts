import { API_ENDPOINTS, getAuthedWsUrl } from '../config/api';

export class OrchestrationWebSocket {
  private ws: WebSocket | null = null;
  private listeners: ((data: any) => void)[] = [];

  connect(clientId: string) {
    // Build WS URL using centralized config so we always target the backend
    const token = (() => {
      try { return localStorage.getItem('authToken') || undefined; } catch { return undefined; }
    })();
    const baseUrl = getAuthedWsUrl(API_ENDPOINTS.DASHBOARD_WS, token);
    const sep = baseUrl.includes('?') ? '&' : '?';
    const wsUrl = `${baseUrl}${sep}clientId=${encodeURIComponent(clientId)}`;

    this.ws = new WebSocket(wsUrl);
    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach((cb) => cb(data));
      } catch (e) {
        // ignore malformed frames
      }
    };
  }

  onMessage(cb: (data: any) => void) {
    this.listeners.push(cb);
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  close() {
    if (this.ws) this.ws.close();
  }
}
