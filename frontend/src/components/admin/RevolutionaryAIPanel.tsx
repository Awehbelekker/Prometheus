/**
 * 🚀 REVOLUTIONARY AI SYSTEMS PANEL
 * 
 * Displays real-time status and performance of all 5 revolutionary AI engines:
 * 1. Crypto Trading Engine
 * 2. Options Trading Engine
 * 3. Advanced Pattern Recognition
 * 4. Market Maker Engine
 * 5. Master Coordination Engine
 * 
 * Uses secured admin-only endpoints: /api/revolutionary/*
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Chip,
  LinearProgress,
  CircularProgress,
  Button,
  Alert,
  Tooltip,
  IconButton
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Speed,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Refresh,
  PlayArrow,
  Pause,
  ShowChart,
  AccountBalance,
  AutoAwesome,
  Wifi,
  WifiOff,
  Download,
  FileDownload
} from '@mui/icons-material';
import { getApiUrl } from '../../config/api';
import { getJsonWithRetry } from '../../utils/network';
import { useAdminWebSocket } from '../../hooks/useAdminWebSocket';
import { exportRevolutionaryAI } from '../../utils/exportData';

interface RevolutionaryEngine {
  name: string;
  type: 'crypto' | 'options' | 'advanced' | 'market_maker' | 'master';
  status: 'active' | 'inactive' | 'error' | 'starting';
  performance: {
    accuracy?: number;
    trades: number;
    winRate: number;
    pnl: number;
    avgProfit?: number;
    sharpeRatio?: number;
  };
  capabilities: string[];
  lastUpdate: string;
  uptime?: number;
}

interface RevolutionaryStatus {
  overall_status: string;
  engines: RevolutionaryEngine[];
  total_trades: number;
  total_pnl: number;
  avg_win_rate: number;
  system_uptime: number;
}

const RevolutionaryAIPanel: React.FC = () => {
  const [status, setStatus] = useState<RevolutionaryStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Use WebSocket for real-time updates
  const { data: wsData, isConnected, error: wsError, reconnect } = useAdminWebSocket<RevolutionaryStatus>({
    endpoint: '/ws/revolutionary-ai',
    onData: (data) => {
      setStatus(data);
      setLastUpdate(new Date());
      setLoading(false);
    }
  });

  // Fallback to REST API if WebSocket fails
  useEffect(() => {
    if (wsError && !isConnected) {
      fetchRevolutionaryStatus();
      const interval = setInterval(fetchRevolutionaryStatus, 30000);
      return () => clearInterval(interval);
    }
  }, [wsError, isConnected]);

  const fetchRevolutionaryStatus = async () => {
    try {
      setError(null);
      const data = await getJsonWithRetry(
        getApiUrl('/api/revolutionary/status'),
        {},
        { retries: 3, backoffMs: 500, maxBackoffMs: 4000, timeoutMs: 8000 }
      );

      setStatus(data);
      setLastUpdate(new Date());
      setLoading(false);
    } catch (err: any) {
      console.error('Failed to fetch revolutionary status:', err);
      setError(err.message || 'Failed to load revolutionary AI status');
      setLoading(false);
    }
  };

  const getEngineIcon = (type: string) => {
    switch (type) {
      case 'crypto': return <ShowChart sx={{ fontSize: 32 }} />;
      case 'options': return <AccountBalance sx={{ fontSize: 32 }} />;
      case 'advanced': return <Psychology sx={{ fontSize: 32 }} />;
      case 'market_maker': return <TrendingUp sx={{ fontSize: 32 }} />;
      case 'master': return <AutoAwesome sx={{ fontSize: 32 }} />;
      default: return <Psychology sx={{ fontSize: 32 }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'error': return 'error';
      case 'starting': return 'warning';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle />;
      case 'inactive': return <Pause />;
      case 'error': return <ErrorIcon />;
      case 'starting': return <PlayArrow />;
      default: return <Warning />;
    }
  };

  if (loading && !status) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#00d4ff', mb: 1 }}>
            🚀 Revolutionary AI Systems
          </Typography>
          <Typography variant="body2" sx={{ color: '#ccc' }}>
            Real-time monitoring of all 5 revolutionary trading engines
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          {isConnected ? (
            <Tooltip title="WebSocket Connected - Real-time updates">
              <Chip
                icon={<Wifi />}
                label="Live"
                size="small"
                color="success"
                sx={{ fontWeight: 600 }}
              />
            </Tooltip>
          ) : (
            <Tooltip title="WebSocket Disconnected - Using polling">
              <Chip
                icon={<WifiOff />}
                label="Polling"
                size="small"
                color="warning"
                sx={{ fontWeight: 600 }}
              />
            </Tooltip>
          )}
          <Typography variant="caption" sx={{ color: '#999' }}>
            Last updated: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <Tooltip title="Export as CSV">
            <IconButton
              onClick={() => status && exportRevolutionaryAI(status.engines, 'csv')}
              size="small"
              sx={{ color: '#4caf50' }}
              disabled={!status}
            >
              <FileDownload />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export as JSON">
            <IconButton
              onClick={() => status && exportRevolutionaryAI(status.engines, 'json')}
              size="small"
              sx={{ color: '#00d4ff' }}
              disabled={!status}
            >
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title={isConnected ? "Reconnect WebSocket" : "Refresh Data"}>
            <IconButton onClick={isConnected ? reconnect : fetchRevolutionaryStatus} size="small" sx={{ color: '#00d4ff' }}>
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Overall Status Card */}
      {status && (
        <Card sx={{
          mb: 3,
          background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(255, 107, 53, 0.1))',
          border: '1px solid rgba(0, 212, 255, 0.3)'
        }}>
          <CardContent>
            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Overall Status</Typography>
                <Chip
                  label={status.overall_status?.toUpperCase() || 'UNKNOWN'}
                  color={getStatusColor(status.overall_status)}
                  icon={getStatusIcon(status.overall_status)}
                  sx={{ fontWeight: 700 }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Total Trades</Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#fff' }}>
                  {status.total_trades?.toLocaleString() || 0}
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Avg Win Rate</Typography>
                <Typography variant="h4" sx={{ fontWeight: 700, color: '#4caf50' }}>
                  {status.avg_win_rate?.toFixed(1) || 0}%
                </Typography>
              </Grid>
              <Grid item xs={12} md={3}>
                <Typography variant="subtitle2" sx={{ color: '#999', mb: 1 }}>Total P&L</Typography>
                <Typography
                  variant="h4"
                  sx={{
                    fontWeight: 700,
                    color: (status.total_pnl || 0) >= 0 ? '#4caf50' : '#f44336'
                  }}
                >
                  ${status.total_pnl?.toLocaleString() || 0}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Individual Engine Cards */}
      <Grid container spacing={3}>
        {status?.engines?.map((engine) => (
          <Grid item xs={12} md={6} key={engine.name}>
            <Card sx={{
              background: 'linear-gradient(135deg, rgba(26, 26, 26, 0.95), rgba(42, 42, 42, 0.95))',
              border: `1px solid ${engine.status === 'active' ? 'rgba(76, 175, 80, 0.5)' : 'rgba(255, 255, 255, 0.1)'}`,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: '0 8px 24px rgba(0, 212, 255, 0.2)'
              }
            }}>
              <CardContent>
                {/* Engine Header */}
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ color: '#00d4ff' }}>
                      {getEngineIcon(engine.type)}
                    </Box>
                    <Box>
                      <Typography variant="h6" sx={{ fontWeight: 700, color: '#fff' }}>
                        {engine.name}
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#999' }}>
                        {engine.type.replace('_', ' ').toUpperCase()}
                      </Typography>
                    </Box>
                  </Box>
                  <Chip
                    label={engine.status.toUpperCase()}
                    color={getStatusColor(engine.status) as any}
                    size="small"
                    icon={getStatusIcon(engine.status)}
                  />
                </Box>

                {/* Performance Metrics */}
                <Grid container spacing={2} sx={{ mb: 2 }}>
                  {engine.performance.accuracy !== undefined && (
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: '#999' }}>Accuracy</Typography>
                      <Typography variant="h6" sx={{ color: '#fff' }}>
                        {engine.performance.accuracy.toFixed(1)}%
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={engine.performance.accuracy}
                        sx={{ mt: 1, height: 6, borderRadius: 3 }}
                      />
                    </Grid>
                  )}
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#999' }}>Win Rate</Typography>
                    <Typography variant="h6" sx={{ color: '#4caf50' }}>
                      {engine.performance.winRate.toFixed(1)}%
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={engine.performance.winRate}
                      color="success"
                      sx={{ mt: 1, height: 6, borderRadius: 3 }}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#999' }}>Total Trades</Typography>
                    <Typography variant="h6" sx={{ color: '#fff' }}>
                      {engine.performance.trades.toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="caption" sx={{ color: '#999' }}>P&L</Typography>
                    <Typography
                      variant="h6"
                      sx={{ color: engine.performance.pnl >= 0 ? '#4caf50' : '#f44336' }}
                    >
                      ${engine.performance.pnl.toLocaleString()}
                    </Typography>
                  </Grid>
                </Grid>

                {/* Capabilities */}
                {engine.capabilities && engine.capabilities.length > 0 && (
                  <Box>
                    <Typography variant="caption" sx={{ color: '#999', mb: 1, display: 'block' }}>
                      Capabilities:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {engine.capabilities.map((cap) => (
                        <Chip
                          key={cap}
                          label={cap}
                          size="small"
                          variant="outlined"
                          sx={{ borderColor: 'rgba(0, 212, 255, 0.3)', color: '#00d4ff' }}
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* No Data Message */}
      {!loading && (!status || !status.engines || status.engines.length === 0) && (
        <Alert severity="info" sx={{ mt: 3 }}>
          No revolutionary AI engines found. The system may still be initializing.
        </Alert>
      )}
    </Box>
  );
};

export default RevolutionaryAIPanel;

