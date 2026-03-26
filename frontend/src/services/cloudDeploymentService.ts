/**
 * Cloud Deployment Service for MASS Framework
 * Handles cloud deployment, scaling, and monitoring operations
 */

import enhancedApiService from './enhancedApiService';
import { getJsonWithRetry } from '../utils/network';


// Demo mode flag - set to true for demo/development
const DEMO_MODE = true;
const DEMO_API_BASE = DEMO_MODE ? '/api/demo/cloud' : '/api/cloud';

export interface DeploymentConfig {
  environment: 'development' | 'staging' | 'production';
  cloud_provider: 'aws' | 'gcp' | 'azure' | 'docker' | 'kubernetes';
  scaling_config: {
    min_replicas: number;
    max_replicas: number;
    target_cpu_utilization: number;
    memory_limit: string;
  };
  security_config: {
    enable_https: boolean;
    enable_authentication: boolean;
    enable_rate_limiting: boolean;
    api_keys_required: boolean;
  };
  monitoring_config: {
    enable_metrics: boolean;
    enable_logging: boolean;
    enable_alerting: boolean;
    log_level: 'debug' | 'info' | 'warning' | 'error';
  };
}

export interface DeploymentStatus {
  deployment_id: string;
  status: 'pending' | 'deploying' | 'deployed' | 'failed' | 'terminated';
  created_at: string;
  updated_at: string;
  endpoints: {
    api_url: string;
    admin_url?: string;
    monitoring_url?: string;
  };
  resources: {
    cpu_usage: number;
    memory_usage: number;
    active_requests: number;
    response_time_avg: number;
  };
  health_checks: {
    api_health: boolean;
    database_health: boolean;
    ai_services_health: boolean;
  };
}

export interface ScalingEvent {
  timestamp: string;
  event_type: 'scale_up' | 'scale_down' | 'auto_scale';
  from_replicas: number;
  to_replicas: number;
  reason: string;
  triggered_by: 'manual' | 'cpu_threshold' | 'memory_threshold' | 'request_load';
}

class CloudDeploymentService {
  private baseUrl: string;
  private apiKey: string | null = null;

  constructor() {
  // Default to 8000 in dev; can be overridden by REACT_APP_API_URL
  this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    return headers;
  }
  /**
   * Deploy the MASS Framework to cloud
   */
  async deployToCloud(config: DeploymentConfig & { app_name: string }): Promise<{ deployment_id: string; status: string }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/deploy`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(config)
    });
  }
  /**
   * Get deployment status and metrics
   */
  async getDeploymentStatus(deploymentId: string): Promise<DeploymentStatus> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/status/${deploymentId}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * List all active deployments
   */
  async listDeployments(): Promise<DeploymentStatus[]> {
    const data = await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/deployments`, {
      headers: this.getHeaders()
    });
    return data.deployments || [];
  }

  /**
   * Scale deployment replicas
   */
  async scaleDeployment(deploymentId: string, replicas: number, reason?: string): Promise<{ success: boolean }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/deployments/${deploymentId}/scale`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify({
        replicas,
        reason: reason || 'Manual scaling',
        triggered_by: 'manual'
      })
    });
  }

  /**
   * Get scaling history
   */
  async getScalingHistory(deploymentId: string): Promise<ScalingEvent[]> {
    const data = await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/deployments/${deploymentId}/scaling-history`, {
      headers: this.getHeaders()
    });
    return data.events || [];
  }

  /**
   * Terminate deployment
   */
  async terminateDeployment(deploymentId: string): Promise<{ success: boolean }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/deployments/${deploymentId}/terminate`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });
  }

  /**
   * Get real-time metrics
   */
  async getMetrics(deploymentId: string, timeRange: '1h' | '6h' | '24h' | '7d' = '1h'): Promise<{
    cpu_metrics: Array<{ timestamp: string; value: number }>;
    memory_metrics: Array<{ timestamp: string; value: number }>;
    request_metrics: Array<{ timestamp: string; requests_per_second: number; avg_response_time: number }>;
    error_metrics: Array<{ timestamp: string; error_rate: number }>;
  }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/deployments/${deploymentId}/metrics?range=${timeRange}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Get available cloud providers
   */
  async getCloudProviders(): Promise<{ providers: Array<{ id: string; name: string; description: string; supported_services: string[]; status: string }> }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/providers`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Get deployment templates
   */
  async getDeploymentTemplates(): Promise<{ templates: Array<{ id: string; name: string; description: string; cloud_providers: string[]; config: any }> }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/templates`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Get deployment metrics
   */
  async getDeploymentMetrics(deploymentId: string): Promise<{ deployment_id: string; metrics: any[]; summary: any }> {
    return await getJsonWithRetry(`${this.baseUrl}${DEMO_API_BASE}/metrics/${deploymentId}`, {
      headers: this.getHeaders()
    });
  }

  /**
   * Monitor deployment health in real-time
   */
  createHealthMonitor(deploymentId: string, callback: (health: DeploymentStatus['health_checks']) => void): WebSocket | null {
    try {
      const wsUrl = this.baseUrl.replace('http', 'ws') + `${DEMO_API_BASE}/deployments/${deploymentId}/health-monitor`;
      const ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const health = JSON.parse(event.data);
          callback(health);
        } catch (error) {
          console.error('Failed to parse health data:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('Health monitor WebSocket error:', error);
      };

      return ws;
    } catch (error) {
      console.error('Failed to create health monitor:', error);
      return null;
    }
  }
}

export const cloudDeploymentService = new CloudDeploymentService();
export default cloudDeploymentService;
