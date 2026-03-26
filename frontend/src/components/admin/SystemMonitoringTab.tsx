import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  MonitorHeart,
  Storage,
  Speed,
  Memory,
  NetworkCheck,
  BugReport,
  Analytics,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh,
  Settings,
  RestartAlt,
  CloudDownload,
  Security,
  Timeline,
  ExpandMore,
  Computer,
  Dataset,
  Api,
  Schedule
} from '@mui/icons-material';

interface SystemHealth {
  overall_status: 'healthy' | 'degraded' | 'critical';
  uptime: number;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  background_tasks: number;
  database_status: string;
  api_response_time: number;
  error_rate: number;
  last_backup: string;
}

interface SystemMetric {
  metric_name: string;
  current_value: number;
  previous_value: number;
  change_percent: number;
  status: 'healthy' | 'warning' | 'critical';
  last_updated: string;
  threshold_warning: number;
  threshold_critical: number;
}

interface SystemMonitoringTabProps {
  systemHealth: SystemHealth | null;
  systemMetrics: SystemMetric[];
  performanceData: any[];
  onSystemAction: (action: string, params?: any) => void;
  loading: boolean;
  formatDate: (date: string) => string;
  showAlert: (type: 'success' | 'error' | 'info' | 'warning', message: string) => void;
}

const SystemMonitoringTab: React.FC<SystemMonitoringTabProps> = ({
  systemHealth,
  systemMetrics,
  performanceData,
  onSystemAction,
  loading,
  formatDate,
  showAlert
}) => {
  const [expandedAccordion, setExpandedAccordion] = useState<string | false>('overview');
  const [actionDialog, setActionDialog] = useState(false);
  const [selectedAction, setSelectedAction] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        // Trigger refresh of monitoring data
        onSystemAction('refresh_metrics');
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh, onSystemAction]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return '#4caf50';
      case 'warning': case 'degraded': return '#ff9800';
      case 'critical': case 'error': return '#f44336';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return <CheckCircle sx={{ color: '#4caf50' }} />;
      case 'warning': case 'degraded': return <Warning sx={{ color: '#ff9800' }} />;
      case 'critical': case 'error': return <Error sx={{ color: '#f44336' }} />;
      default: return <Info sx={{ color: '#757575' }} />;
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const formatBytes = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleSystemAction = (action: string) => {
    setSelectedAction(action);
    setActionDialog(true);
  };

  const confirmSystemAction = () => {
    onSystemAction(selectedAction);
    setActionDialog(false);
    showAlert('info', `System action '${selectedAction}' initiated`);
  };

  if (!systemHealth) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
        <Typography variant="h6" sx={{ ml: 2, color: '#aaa' }}>
          Loading system health data...
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header with Controls */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
          System Health Monitoring
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Chip
            label={`Auto-refresh: ${autoRefresh ? 'ON' : 'OFF'}`}
            onClick={() => setAutoRefresh(!autoRefresh)}
            color={autoRefresh ? 'success' : 'default'}
            size="small"
          />
          
          <Tooltip title="Refresh Now">
            <IconButton
              onClick={() => onSystemAction('refresh_metrics')}
              sx={{ color: '#00d4ff' }}
            >
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="System Settings">
            <IconButton
              onClick={() => handleSystemAction('open_settings')}
              sx={{ color: '#00d4ff' }}
            >
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Overall System Status */}
      <Card sx={{ 
        backgroundColor: 'rgba(26, 26, 46, 0.8)', 
        border: `2px solid ${getStatusColor(systemHealth.overall_status)}`,
        mb: 3
      }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {getStatusIcon(systemHealth.overall_status)}
              <Box>
                <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
                  System Status: {systemHealth.overall_status.toUpperCase()}
                </Typography>
                <Typography variant="body2" sx={{ color: '#aaa' }}>
                  Uptime: {formatUptime(systemHealth.uptime)} | Last updated: {formatDate(new Date().toISOString())}
                </Typography>
              </Box>
            </Box>
            
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button
                variant="outlined"
                startIcon={<RestartAlt />}
                onClick={() => handleSystemAction('restart_services')}
                sx={{ borderColor: '#ff9800', color: '#ff9800' }}
              >
                Restart Services
              </Button>
              <Button
                variant="outlined"
                startIcon={<CloudDownload />}
                onClick={() => handleSystemAction('backup_system')}
                sx={{ borderColor: '#4caf50', color: '#4caf50' }}
              >
                Backup Now
              </Button>
            </Box>
          </Box>
        </CardContent>
      </Card>

      {/* Key Metrics Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'rgba(26, 26, 46, 0.8)', 
            border: '1px solid rgba(76, 175, 80, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#4caf50' }}>CPU Usage</Typography>
                <Speed sx={{ color: '#4caf50' }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', mb: 1 }}>
                {systemHealth.cpu_usage.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={systemHealth.cpu_usage}
                sx={{
                  height: 8,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: systemHealth.cpu_usage > 80 ? '#f44336' : systemHealth.cpu_usage > 60 ? '#ff9800' : '#4caf50'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'rgba(26, 26, 46, 0.8)', 
            border: '1px solid rgba(33, 150, 243, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#2196f3' }}>Memory Usage</Typography>
                <Memory sx={{ color: '#2196f3' }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', mb: 1 }}>
                {systemHealth.memory_usage.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={systemHealth.memory_usage}
                sx={{
                  height: 8,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: systemHealth.memory_usage > 85 ? '#f44336' : systemHealth.memory_usage > 70 ? '#ff9800' : '#2196f3'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'rgba(26, 26, 46, 0.8)', 
            border: '1px solid rgba(255, 152, 0, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#ff9800' }}>Disk Usage</Typography>
                <Storage sx={{ color: '#ff9800' }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', mb: 1 }}>
                {systemHealth.disk_usage.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={systemHealth.disk_usage}
                sx={{
                  height: 8,
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: systemHealth.disk_usage > 90 ? '#f44336' : systemHealth.disk_usage > 75 ? '#ff9800' : '#ff9800'
                  }
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ 
            backgroundColor: 'rgba(26, 26, 46, 0.8)', 
            border: '1px solid rgba(156, 39, 176, 0.3)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                <Typography variant="h6" sx={{ color: '#9c27b0' }}>Active Connections</Typography>
                <NetworkCheck sx={{ color: '#9c27b0' }} />
              </Box>
              <Typography variant="h4" sx={{ fontWeight: 700, color: 'white', mb: 1 }}>
                {systemHealth.active_connections}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Background tasks: {systemHealth.background_tasks}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Metrics */}
      <Accordion 
        expanded={expandedAccordion === 'metrics'} 
        onChange={(_, isExpanded) => setExpandedAccordion(isExpanded ? 'metrics' : false)}
        sx={{ 
          backgroundColor: 'rgba(26, 26, 46, 0.8)', 
          border: '1px solid rgba(0, 212, 255, 0.3)',
          mb: 2,
          '&:before': { display: 'none' }
        }}
      >
        <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#00d4ff' }} />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Analytics sx={{ color: '#00d4ff' }} />
            <Typography variant="h6" sx={{ color: '#00d4ff' }}>
              Detailed System Metrics
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ color: '#aaa' }}>Metric</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Current Value</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Previous Value</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Change</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Status</TableCell>
                  <TableCell sx={{ color: '#aaa' }}>Last Updated</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {systemMetrics.map((metric) => (
                  <TableRow key={metric.metric_name}>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: 'white', fontWeight: 600 }}>
                        {metric.metric_name.replace('_', ' ').toUpperCase()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: 'white' }}>
                        {metric.current_value.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ color: '#aaa' }}>
                        {metric.previous_value.toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: metric.change_percent >= 0 ? '#4caf50' : '#f44336',
                          fontWeight: 600
                        }}
                      >
                        {metric.change_percent >= 0 ? '+' : ''}{metric.change_percent.toFixed(2)}%
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {getStatusIcon(metric.status)}
                    </TableCell>
                    <TableCell>
                      <Typography variant="caption" sx={{ color: '#aaa' }}>
                        {formatDate(metric.last_updated)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* System Services Status */}
      <Accordion 
        expanded={expandedAccordion === 'services'} 
        onChange={(_, isExpanded) => setExpandedAccordion(isExpanded ? 'services' : false)}
        sx={{ 
          backgroundColor: 'rgba(26, 26, 46, 0.8)', 
          border: '1px solid rgba(76, 175, 80, 0.3)',
          mb: 2,
          '&:before': { display: 'none' }
        }}
      >
        <AccordionSummary expandIcon={<ExpandMore sx={{ color: '#4caf50' }} />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Computer sx={{ color: '#4caf50' }} />
            <Typography variant="h6" sx={{ color: '#4caf50' }}>
              System Services Status
            </Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Dataset sx={{ color: '#4caf50' }} />
                    <Typography variant="h6" sx={{ color: 'white' }}>Database</Typography>
                    <Chip label={systemHealth.database_status} color="success" size="small" />
                  </Box>
                  <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
                    Last Backup: {formatDate(systemHealth.last_backup)}
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleSystemAction('backup_database')}
                    sx={{ borderColor: '#4caf50', color: '#4caf50' }}
                  >
                    Backup Now
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Api sx={{ color: '#2196f3' }} />
                    <Typography variant="h6" sx={{ color: 'white' }}>API Server</Typography>
                    <Chip label="Running" color="primary" size="small" />
                  </Box>
                  <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
                    Response Time: {systemHealth.api_response_time}ms
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleSystemAction('restart_api')}
                    sx={{ borderColor: '#2196f3', color: '#2196f3' }}
                  >
                    Restart API
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card sx={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <Security sx={{ color: '#ff9800' }} />
                    <Typography variant="h6" sx={{ color: 'white' }}>Security</Typography>
                    <Chip 
                      label={systemHealth.error_rate < 1 ? "Secure" : "Alert"} 
                      color={systemHealth.error_rate < 1 ? "success" : "warning"} 
                      size="small" 
                    />
                  </Box>
                  <Typography variant="body2" sx={{ color: '#aaa', mb: 1 }}>
                    Error Rate: {systemHealth.error_rate.toFixed(2)}%
                  </Typography>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={() => handleSystemAction('security_scan')}
                    sx={{ borderColor: '#ff9800', color: '#ff9800' }}
                  >
                    Run Scan
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* System Action Confirmation Dialog */}
      <Dialog open={actionDialog} onClose={() => setActionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          Confirm System Action
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#1a1a2e', color: 'white' }}>
          <Alert severity="warning" sx={{ mb: 2 }}>
            You are about to perform: <strong>{selectedAction.replace('_', ' ').toUpperCase()}</strong>
          </Alert>
          <Typography variant="body1">
            This action may temporarily affect system performance. Are you sure you want to continue?
          </Typography>
        </DialogContent>
        <DialogActions sx={{ bgcolor: '#1a1a2e' }}>
          <Button onClick={() => setActionDialog(false)}>Cancel</Button>
          <Button onClick={confirmSystemAction} variant="contained" color="warning">
            Confirm Action
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SystemMonitoringTab;
