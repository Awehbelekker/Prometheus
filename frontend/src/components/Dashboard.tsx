import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  Badge,
  IconButton,
  Tooltip,
  LinearProgress,
  Fade,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Speed,
  Memory,
  Storage,
  NetworkCheck,
  PlayArrow,
  Pause,
  Refresh,
  Settings,
  Notifications,
  Timeline,
  Assessment,
  Build,
  Cloud
} from '@mui/icons-material';
import { useWebSocket } from '../hooks/useWebSocket';
import ModernCard from './ModernCard';
import LoadingSpinner from './LoadingSpinner';
import Logo from './Logo';
import { getApiUrl, getWsUrl, API_ENDPOINTS } from '../config/api';
import UnifiedSidebar from './navigation/UnifiedSidebar';
import MainContent from './MainContent';
import FeatureBadges from './FeatureBadges';

import { apiCall } from '../config/api';

import { getJsonWithRetry } from '../utils/network';

interface SystemStatus {
  system: string;
  version: string;
  agents_available: number;
  active_workflows: number;
  active_connections: number;
  cpu_usage?: number;
  memory_usage?: number;
  disk_usage?: number;
}

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'busy';
  last_activity?: string;
  description?: string;
  capabilities?: string[];
  performance?: number;
}

interface MetricCard {
  title: string;
  value: string | number;
  subtitle: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'stable';
  trendValue?: string;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
}

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface DashboardProps {
  user?: any;
  onLogout?: () => void;
}

// Add state for sidebar
const DashboardWithSidebar: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [selectedItem, setSelectedItem] = useState('dashboard');

  // Ensure user has admin access for testing
  const adminUser = user || {
    id: 'admin-1',
    name: 'Admin User',
    email: 'admin@prometheus.com',
    role: 'admin',
    permissions: ['admin', 'trader', 'user']
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <UnifiedSidebar selected={selectedItem} onSelect={setSelectedItem} />
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <MainContent selectedItem={selectedItem} currentUser={adminUser} />
      </Box>
    </Box>
  );
};

const DashboardContent: React.FC<DashboardProps> = ({ user, onLogout }) => {
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [recentActivities, setRecentActivities] = useState<string[]>([]);
  const [performanceData, setPerformanceData] = useState({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0
  });

  const [liveMetrics, setLiveMetrics] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalTrades: 0,
    totalPnL: 0,
    winRate: 0,
    portfolioValue: 0,
    lastUpdated: ''
  });

  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // WebSocket connection for real-time updates
  const { isConnected, lastMessage, sendMessage, connectionStatus } = useWebSocket(
    getWsUrl(API_ENDPOINTS.DASHBOARD_WS),
    'dashboard-client'
  );

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;
    try {
      const data: WebSocketMessage = lastMessage;
      switch (data.type) {
        case 'status_update': {
          if (typeof data.data === 'object' && data.data !== null) {
            setSystemStatus(prev => {
              const base = prev ?? {
                system: '',
                version: '',
                agents_available: 0,
                active_workflows: 0,
                active_connections: 0,
                cpu_usage: 0,
                memory_usage: 0,
                disk_usage: 0
              };
              return {
                ...base,
                ...(data.data as Partial<SystemStatus>)
              };
            });
          }
          break;
        }
        case 'performance_update': {
          if (
            typeof data.data === 'object' && data.data !== null &&
            'cpu' in data.data && 'memory' in data.data && 'disk' in data.data && 'network' in data.data
          ) {
            setPerformanceData({
              cpu: data.data.cpu,
              memory: data.data.memory,
              disk: data.data.disk,
              network: data.data.network
            });
          }
          break;
        }
        case 'agent_update': {
          if (
            typeof data.data === 'object' && data.data !== null &&
            'agent_id' in data.data && 'message' in data.data
          ) {
            setRecentActivities(prev => [
              `Agent ${data.data.agent_id}: ${data.data.message}`,
              ...prev.slice(0, 4)
            ]);
          }
          break;
        }
        default:
          break;
      }
    } catch (error) {
      console.error('Error handling WebSocket message:', error);
    }
  }, [lastMessage]);

  useEffect(() => {
    fetchSystemStatus();
    fetchAgents();
    fetchPerformanceData();
    fetchLiveMetrics();

    // Set up live data updates
    const interval = setInterval(() => {
      fetchLiveMetrics();
    }, 10000); // Update every 10 seconds

    return () => clearInterval(interval);
  }, []);

  const fetchLiveMetrics = async () => {
    try {
      // Get live trading metrics
      const url = getApiUrl('/api/system/status');
      const data = await getJsonWithRetry(url, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('authToken')}` }
      }, { retries: 4, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 });
        setLiveMetrics({
          totalUsers: data.users || 0,
          activeUsers: data.active_users || 0,
          totalTrades: data.trades || 0,
          totalPnL: data.pnl || 0,
          winRate: data.win_rate || 0,
          portfolioValue: data.portfolio_value || 0,
          lastUpdated: new Date().toLocaleTimeString()
        });
    } catch (error) {
      console.error('Failed to load live metrics:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const data = await getJsonWithRetry(getApiUrl(API_ENDPOINTS.STATUS), {}, { retries: 4, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 });
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const fetchAgents = async () => {
    try {
      const data = await getJsonWithRetry(getApiUrl(API_ENDPOINTS.AGENTS), {}, { retries: 4, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 });
      // Ensure data is an array
      const agentsArray = Array.isArray(data) ? data : (data?.agents && Array.isArray(data.agents) ? data.agents : []);
      setAgents(agentsArray);
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      setAgents([]); // Set to empty array on error
    } finally {
      setLoading(false);
    }
  };

  const fetchPerformanceData = async () => {
    try {
      const data = await getJsonWithRetry(getApiUrl(API_ENDPOINTS.SYSTEM_PERFORMANCE), {}, { retries: 4, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 });
      setPerformanceData({
        cpu: data.cpu_usage || 0,
        memory: data.memory_usage || 0,
        disk: 75, // Mock data
        network: data.throughput || 0
      });
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    }
  };

  const activateAgent = async (agentId: string) => {
    try {
      await apiCall(API_ENDPOINTS.AGENT_ACTIVATE(agentId), { method: 'POST' });
      fetchAgents();
    } catch (error) {
      console.error('Failed to activate agent:', error);
    }
  };

  const getMetricCards = (): MetricCard[] => [
    {
      title: 'System Status',
      value: systemStatus?.system === 'online' ? 'Online' : 'Offline',
      subtitle: `Version ${systemStatus?.version || '3.0.0'}`,
      icon: <Speed />,
      trend: 'up',
      trendValue: '+2.5%',
      color: systemStatus?.system === 'online' ? 'success' : 'error'
    },
    {
      title: 'Available Agents',
      value: systemStatus?.agents_available || 0,
      subtitle: `${Array.isArray(agents) ? agents.filter(a => a.status === 'active').length : 0} active`,
      icon: <Build />,
      trend: 'up',
      trendValue: '+1',
      color: 'primary'
    },
    {
      title: 'Active Workflows',
      value: systemStatus?.active_workflows || 0,
      subtitle: 'Processing tasks',
      icon: <Timeline />,
      trend: 'stable',
      color: 'info'
    },
    {
      title: 'Active Connections',
      value: systemStatus?.active_connections || 0,
      subtitle: 'Real-time connections',
      icon: <NetworkCheck />,
      trend: 'up',
      trendValue: '+3',
      color: 'secondary'
    }
  ];

  if (loading) {
    return <LoadingSpinner message="Loading dashboard..." size="large" />;
  }

  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ p: { xs: 2, md: 3 }, minHeight: '100vh' }}>
        {/* Header Section */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Logo size="medium" theme="dark" />
              <Box>
                <Typography
                  variant="h3"
                  sx={{
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #00d4ff 0%, #ff6b35 50%, #9c27b0 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontSize: { xs: '2rem', md: '2.5rem' }
                  }}
                >
                  PROMETHEUS Dashboard
                </Typography>
                <Typography variant="subtitle1" sx={{ color: 'text.secondary', fontWeight: 500 }}>
                  NeuroForge™ Trading Platform
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Refresh Data">
                <IconButton
                  onClick={() => { fetchSystemStatus(); fetchAgents(); }}
                  sx={{
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    '&:hover': { backgroundColor: 'rgba(99, 102, 241, 0.2)' }
                  }}
                >
                  <Refresh />
                </IconButton>
              </Tooltip>
              <Tooltip title="Settings">
                <IconButton
                  sx={{
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    '&:hover': { backgroundColor: 'rgba(16, 185, 129, 0.2)' }
                  }}
                >
                  <Settings />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          {/* Connection Status */}
          <Alert
            severity={isConnected ? 'success' : connectionStatus === 'error' ? 'error' : 'warning'}
            sx={{
              mb: 2,
              '& .MuiAlert-icon': {
                color: isConnected ? 'success.main' : connectionStatus === 'error' ? 'error.main' : 'warning.main'
              }
            }}
          >
            {isConnected
              ? 'Real-time updates connected'
              : connectionStatus === 'error'
              ? 'Real-time updates unavailable - using fallback data'
              : 'Connecting to real-time updates...'
            }
          </Alert>
          <FeatureBadges />
        </Box>

        {/* Metric Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {getMetricCards().map((card, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <ModernCard
                title={card.title}
                content={
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="h4" sx={{ fontWeight: 700, color: `${card.color}.main` }}>
                        {card.value}
                      </Typography>
                      <Box sx={{
                        p: 1,
                        borderRadius: 2,
                        backgroundColor: `${card.color}.main`,
                        color: 'white',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        {card.icon}
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {card.subtitle}
                    </Typography>
                    {card.trend && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        {card.trend === 'up' ? (
                          <TrendingUp sx={{ color: 'success.main', fontSize: 16 }} />
                        ) : card.trend === 'down' ? (
                          <TrendingDown sx={{ color: 'error.main', fontSize: 16 }} />
                        ) : (
                          <Box sx={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: 'grey.500' }} />
                        )}
                        <Typography variant="caption" color="text.secondary">
                          {card.trendValue || 'Stable'}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                }
                status={card.color === 'primary' || card.color === 'secondary' ? 'info' : card.color}
                elevation={2}
              />
            </Grid>
          ))}
        </Grid>

        {/* Performance Metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <ModernCard
              title="System Performance"
              subtitle="Real-time resource usage"
              content={
                <Box>
                  {[
                    { label: 'CPU Usage', value: performanceData.cpu, color: 'primary.main' },
                    { label: 'Memory Usage', value: performanceData.memory, color: 'secondary.main' },
                    { label: 'Disk Usage', value: performanceData.disk, color: 'warning.main' },
                    { label: 'Network', value: performanceData.network, color: 'info.main' }
                  ].map((metric, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          {metric.label}
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {metric.value}%
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={metric.value}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: metric.color,
                            borderRadius: 4
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              }
              icon={<Assessment />}
              status="info"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <ModernCard
              title="Recent Activities"
              subtitle="Latest system events"
              content={
                <Box>
                  {recentActivities.length === 0 ? (
                    <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>
                      No recent activities
                    </Typography>
                  ) : (
                    <List sx={{ p: 0 }}>
                      {recentActivities.map((activity, index) => (
                        <ListItem key={index} sx={{ px: 0, py: 1 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <Box sx={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              backgroundColor: 'primary.main'
                            }} />
                          </ListItemIcon>
                          <ListItemText
                            primary={activity}
                            primaryTypographyProps={{
                              variant: 'body2',
                              sx: { fontWeight: 500 }
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </Box>
              }
              icon={<Notifications />}
              status="info"
            />
          </Grid>
        </Grid>

        {/* Agents Section */}
        <ModernCard
          title="Available Agents"
          subtitle={`${Array.isArray(agents) ? agents.length : 0} agents configured`}
          content={
            <Box>
              {!Array.isArray(agents) || agents.length === 0 ? (
                <Typography color="text.secondary" sx={{ fontStyle: 'italic' }}>
                  No agents available. Check your agents directory.
                </Typography>
              ) : (
                <Grid container spacing={2}>
                  {agents.map((agent) => (
                    <Grid item xs={12} sm={6} md={4} key={agent.id}>
                      <Box
                        sx={{
                          p: 2,
                          borderRadius: 2,
                          border: '1px solid rgba(255,255,255,0.1)',
                          backgroundColor: 'rgba(255,255,255,0.02)',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            backgroundColor: 'rgba(255,255,255,0.05)',
                            borderColor: 'rgba(255,255,255,0.2)',
                            transform: 'translateY(-2px)'
                          }
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle1" fontWeight={600}>
                            {agent.name}
                          </Typography>
                          <Chip
                            label={agent.status}
                            size="small"
                            color={agent.status === 'active' ? 'success' : agent.status === 'busy' ? 'warning' : 'default'}
                            sx={{ fontWeight: 500 }}
                          />
                        </Box>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          {agent.description || 'No description available'}
                        </Typography>
                        {agent.capabilities && agent.capabilities.length > 0 && (
                          <Box sx={{ mb: 2 }}>
                            {agent.capabilities.slice(0, 2).map((capability, index) => (
                              <Chip
                                key={index}
                                label={capability}
                                size="small"
                                variant="outlined"
                                sx={{ mr: 0.5, mb: 0.5, fontSize: '0.75rem' }}
                              />
                            ))}
                            {agent.capabilities.length > 2 && (
                              <Chip
                                label={`+${agent.capabilities.length - 2} more`}
                                size="small"
                                variant="outlined"
                                sx={{ fontSize: '0.75rem' }}
                              />
                            )}
                          </Box>
                        )}
                        <Button
                          variant="contained"
                          size="small"
                          startIcon={agent.status === 'active' ? <Pause /> : <PlayArrow />}
                          onClick={() => activateAgent(agent.id)}
                          disabled={agent.status === 'busy'}
                          sx={{
                            width: '100%',
                            '&:hover': {
                              transform: 'translateY(-1px)'
                            }
                          }}
                        >
                          {agent.status === 'active' ? 'Deactivate' : 'Activate'}
                        </Button>
                      </Box>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          }
          icon={<Build />}
          status="info"
        />

        {/* Quick Actions */}
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
            Quick Actions
          </Typography>
          <Grid container spacing={2}>
            {[
              { label: 'Import Project', icon: <Cloud />, color: 'primary' },
              { label: 'Create Workflow', icon: <Timeline />, color: 'secondary' },
              { label: 'View Logs', icon: <Assessment />, color: 'info' },
              { label: 'System Settings', icon: <Settings />, color: 'warning' }
            ].map((action, index) => (
              <Grid item xs={12} sm={6} md={3} key={index}>
                <Button
                  variant="outlined"
                  startIcon={action.icon}
                  fullWidth
                  sx={{
                    py: 2,
                    borderColor: `${action.color}.main`,
                    color: `${action.color}.main`,
                    '&:hover': {
                      backgroundColor: `${action.color}.main`,
                      color: 'white',
                      transform: 'translateY(-2px)',
                      boxShadow: `0 4px 12px ${(theme.palette[action.color as keyof typeof theme.palette] as any)?.main || '#6366f1'}40`
                    },
                    transition: 'all 0.2s ease'
                  }}
                >
                  {action.label}
                </Button>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Box>
    </Fade>
  );
};

export default DashboardWithSidebar;
export { DashboardContent };
