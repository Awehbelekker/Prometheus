/**
 * Custom WebSocket Hook for Admin Real-Time Updates
 * 
 * Specialized hook for admin panels (Revolutionary AI, Agents, Market Opportunities)
 * with automatic reconnection, authentication, and error handling.
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { getApiUrl } from '../config/api';

interface UseAdminWebSocketOptions<T> {
  endpoint: string;
  onData?: (data: T) => void;
  enabled?: boolean;
}

interface UseAdminWebSocketReturn<T> {
  data: T | null;
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

export const useAdminWebSocket = <T = any>({
  endpoint,
  onData,
  enabled = true
}: UseAdminWebSocketOptions<T>): UseAdminWebSocketReturn<T> => {
  const [data, setData] = useState<T | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const shouldReconnectRef = useRef(true);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const getWebSocketUrl = useCallback(() => {
    // Get the API URL and convert to WebSocket URL
    const apiUrl = getApiUrl(endpoint);
    const wsUrl = apiUrl.replace(/^http/, 'ws');
    
    // Add authentication token
    const token = localStorage.getItem('token');
    if (token) {
      return `${wsUrl}?token=${encodeURIComponent(token)}`;
    }
    return wsUrl;
  }, [endpoint]);

  const connect = useCallback(() => {
    if (!enabled) return;

    try {
      const wsUrl = getWebSocketUrl();
      console.log(`[AdminWebSocket] Connecting to: ${endpoint}`);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`[AdminWebSocket] Connected to: ${endpoint}`);
        setIsConnected(true);
        setError(null);
        reconnectAttemptsRef.current = 0;

        // Send ping every 30 seconds to keep connection alive
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          // Ignore pong messages
          if (message.type === 'pong') {
            return;
          }

          // Extract data from message
          const messageData = message.data || message;
          setData(messageData);

          if (onData) {
            onData(messageData);
          }
        } catch (err) {
          console.error('[AdminWebSocket] Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error(`[AdminWebSocket] Error on ${endpoint}:`, event);
        setError('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log(`[AdminWebSocket] Disconnected from: ${endpoint}`);
        setIsConnected(false);
        
        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt to reconnect if enabled
        const maxReconnectAttempts = 5;
        if (shouldReconnectRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          console.log(`[AdminWebSocket] Reconnecting (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})...`);
          
          const reconnectDelay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectDelay);
        } else if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
          setError('Max reconnection attempts reached');
        }
      };
    } catch (err: any) {
      console.error('[AdminWebSocket] Connection error:', err);
      setError(err.message || 'Failed to connect');
    }
  }, [endpoint, enabled, getWebSocketUrl, onData]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    reconnectAttemptsRef.current = 0;
    setError(null);
    connect();
  }, [connect, disconnect]);

  useEffect(() => {
    if (enabled) {
      shouldReconnectRef.current = true;
      connect();
    }

    return () => {
      disconnect();
    };
  }, [enabled, connect, disconnect]);

  return {
    data,
    isConnected,
    error,
    reconnect
  };
};

export default useAdminWebSocket;

