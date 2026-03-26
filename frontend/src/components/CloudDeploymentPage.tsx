import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  LinearProgress,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Switch,
  FormControlLabel,
  Tab,
  Tabs,
  CircularProgress
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Visibility as VisibilityIcon,
  StopCircle as StopIcon,
  ScaleOutlined as ScaleIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Timeline as TimelineIcon,
  Security as SecurityIcon,
  Monitor as MonitorIcon
} from '@mui/icons-material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';

import cloudDeploymentService, { 
  DeploymentConfig, 
  DeploymentStatus, 
  ScalingEvent 
} from '../services/cloudDeploymentService';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`cloud-tabpanel-${index}`}
      aria-labelledby={`cloud-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const CloudDeploymentPage: React.FC = () => {
  const [deployments, setDeployments] = useState<DeploymentStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [deployDialog, setDeployDialog] = useState(false);
  const [scaleDialog, setScaleDialog] = useState(false);
  const [selectedDeployment, setSelectedDeployment] = useState<string | null>(null);
  const [newReplicas, setNewReplicas] = useState(1);
  const [cloudProviders, setCloudProviders] = useState<any[]>([]);
  const [deploymentTemplates, setDeploymentTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [appName, setAppName] = useState('mass-framework-app');
  const [deploymentConfig, setDeploymentConfig] = useState<DeploymentConfig>({
    environment: 'development',
    cloud_provider: 'docker',
    scaling_config: {
      min_replicas: 1,
      max_replicas: 3,
      target_cpu_utilization: 70,
      memory_limit: '512Mi'
    },
    security_config: {
      enable_https: false,
      enable_authentication: true,
      enable_rate_limiting: true,
      api_keys_required: true
    },
    monitoring_config: {
      enable_metrics: true,
      enable_logging: true,
      enable_alerting: false,
      log_level: 'info'
    }
  });
  const [metrics, setMetrics] = useState<any>(null);
  const [scalingHistory, setScalingHistory] = useState<ScalingEvent[]>([]);
  useEffect(() => {
    loadDeployments();
    loadCloudProviders();
    loadDeploymentTemplates();
  }, []);

  const loadDeployments = async () => {
    try {
      setLoading(true);
      // For demo, we'll create some sample deployments
      const sampleDeployments: DeploymentStatus[] = [
        {
          deployment_id: 'demo-deployment-1',
          status: 'deployed',
          created_at: '2025-06-14T18:00:00Z',
          updated_at: '2025-06-14T18:05:00Z',
          endpoints: {
            api_url: 'https://mass-framework-demo.herokuapp.com',
            admin_url: 'https://admin-mass-framework-demo.herokuapp.com',
            monitoring_url: 'https://monitoring-demo.herokuapp.com'
          },
          resources: {
            cpu_usage: 45,
            memory_usage: 62,
            active_requests: 23,
            response_time_avg: 156
          },
          health_checks: {
            api_health: true,
            database_health: true,
            ai_services_health: true
          }
        }
      ];
      
      setDeployments(sampleDeployments);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load deployments');
    } finally {
      setLoading(false);
    }
  };

  const loadCloudProviders = async () => {
    try {
      const response = await cloudDeploymentService.getCloudProviders();
      setCloudProviders(response.providers);
    } catch (err) {
      console.error('Failed to load cloud providers:', err);
    }
  };

  const loadDeploymentTemplates = async () => {
    try {
      const response = await cloudDeploymentService.getDeploymentTemplates();
      setDeploymentTemplates(response.templates);
    } catch (err) {
      console.error('Failed to load deployment templates:', err);
    }
  };
  const handleDeploy = async () => {
    try {
      setLoading(true);
      const deployConfig = { ...deploymentConfig, app_name: appName };
      const result = await cloudDeploymentService.deployToCloud(deployConfig);
      setDeployDialog(false);
      
      // Add the new deployment to the list
      if (result.deployment_id) {
        const newDeployment: DeploymentStatus = {
          deployment_id: result.deployment_id,
          status: 'deploying',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          endpoints: {
            api_url: '',
            admin_url: '',
            monitoring_url: ''
          },
          resources: {
            cpu_usage: 0,
            memory_usage: 0,
            active_requests: 0,
            response_time_avg: 0
          },
          health_checks: {
            api_health: false,
            database_health: false,
            ai_services_health: false
          }
        };
        setDeployments([...deployments, newDeployment]);
      }
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Deployment failed');
    } finally {
      setLoading(false);
    }
  };

  const handleScale = async () => {
    if (!selectedDeployment) return;
    
    try {
      setLoading(true);
      await cloudDeploymentService.scaleDeployment(selectedDeployment, newReplicas, 'Manual scaling via UI');
      setScaleDialog(false);
      await loadDeployments();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scaling failed');
    } finally {
      setLoading(false);
    }
  };

  const handleTerminate = async (deploymentId: string) => {
    if (!window.confirm('Are you sure you want to terminate this deployment?')) return;
    
    try {
      setLoading(true);
      await cloudDeploymentService.terminateDeployment(deploymentId);
      await loadDeployments();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Termination failed');
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async (deploymentId: string) => {
    try {
      const metricsData = await cloudDeploymentService.getMetrics(deploymentId);
      setMetrics(metricsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load metrics');
    }
  };

  const loadScalingHistory = async (deploymentId: string) => {
    try {
      const history = await cloudDeploymentService.getScalingHistory(deploymentId);
      setScalingHistory(history);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scaling history');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed': return 'success';
      case 'deploying': return 'warning';
      case 'failed': return 'error';
      case 'terminated': return 'default';
      default: return 'info';
    }
  };

  const renderDeploymentCard = (deployment: DeploymentStatus) => (
    <Card key={deployment.deployment_id} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography variant="h6" gutterBottom>
              Deployment {deployment.deployment_id.slice(0, 8)}
            </Typography>
            <Chip 
              label={deployment.status} 
              color={getStatusColor(deployment.status) as any}
              size="small"
              sx={{ mb: 1 }}
            />
            <Typography variant="body2" color="textSecondary">
              Created: {new Date(deployment.created_at).toLocaleString()}
            </Typography>
            {deployment.endpoints.api_url && (
              <Typography variant="body2">
                API: <a href={deployment.endpoints.api_url} target="_blank" rel="noopener noreferrer">
                  {deployment.endpoints.api_url}
                </a>
              </Typography>
            )}
          </Box>
          <Box>
            <Tooltip title="View Metrics">
              <IconButton 
                onClick={() => {
                  setSelectedDeployment(deployment.deployment_id);
                  loadMetrics(deployment.deployment_id);
                  setSelectedTab(1);
                }}
              >
                <TimelineIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Scale">
              <IconButton 
                onClick={() => {
                  setSelectedDeployment(deployment.deployment_id);
                  setScaleDialog(true);
                }}
                disabled={deployment.status !== 'deployed'}
              >
                <ScaleIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Terminate">
              <IconButton 
                onClick={() => handleTerminate(deployment.deployment_id)}
                disabled={deployment.status === 'terminated'}
                color="error"
              >
                <StopIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        {deployment.status === 'deployed' && (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={3}>
              <Typography variant="caption" display="block">CPU Usage</Typography>
              <LinearProgress 
                variant="determinate" 
                value={deployment.resources.cpu_usage} 
                sx={{ mb: 0.5 }}
              />
              <Typography variant="caption">{deployment.resources.cpu_usage}%</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="caption" display="block">Memory Usage</Typography>
              <LinearProgress 
                variant="determinate" 
                value={deployment.resources.memory_usage} 
                sx={{ mb: 0.5 }}
              />
              <Typography variant="caption">{deployment.resources.memory_usage}%</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="caption" display="block">Active Requests</Typography>
              <Typography variant="h6">{deployment.resources.active_requests}</Typography>
            </Grid>
            <Grid item xs={3}>
              <Typography variant="caption" display="block">Avg Response Time</Typography>
              <Typography variant="h6">{deployment.resources.response_time_avg}ms</Typography>
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );

  const renderMetricsChart = () => {
    if (!metrics) return <CircularProgress />;

    const chartData = {
      labels: metrics.cpu_metrics.map((m: any) => new Date(m.timestamp).toLocaleTimeString()),
      datasets: [
        {
          label: 'CPU Usage (%)',
          data: metrics.cpu_metrics.map((m: any) => m.value),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
        },
        {
          label: 'Memory Usage (%)',
          data: metrics.memory_metrics.map((m: any) => m.value),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.2)',
        }
      ],
    };

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        title: {
          display: true,
          text: 'Resource Usage Over Time',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
        },
      },
    };

    return <Line data={chartData} options={options} />;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Cloud Deployment Management
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottomWidth: '1px', borderBottomStyle: 'solid', borderBottomColor: 'divider', mb: 3 }}>
        <Tabs value={selectedTab} onChange={(e, v) => setSelectedTab(v)}>
          <Tab label="Deployments" icon={<CloudUploadIcon />} />
          <Tab label="Metrics" icon={<MonitorIcon />} />
          <Tab label="Scaling History" icon={<ScaleIcon />} />
        </Tabs>
      </Box>

      <TabPanel value={selectedTab} index={0}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6">Active Deployments</Typography>
          <Box>
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadDeployments}
              sx={{ mr: 2 }}
              disabled={loading}
            >
              Refresh
            </Button>
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              onClick={() => setDeployDialog(true)}
            >
              New Deployment
            </Button>
          </Box>
        </Box>

        {loading && deployments.length === 0 ? (
          <CircularProgress />
        ) : (
          deployments.map(renderDeploymentCard)
        )}
      </TabPanel>

      <TabPanel value={selectedTab} index={1}>
        {selectedDeployment ? (
          <Box>
            <Typography variant="h6" gutterBottom>
              Metrics for Deployment {selectedDeployment.slice(0, 8)}
            </Typography>
            {renderMetricsChart()}
          </Box>
        ) : (
          <Typography>Select a deployment to view metrics</Typography>
        )}
      </TabPanel>

      <TabPanel value={selectedTab} index={2}>
        {selectedDeployment ? (
          <Box>
            <Typography variant="h6" gutterBottom>
              Scaling History for Deployment {selectedDeployment.slice(0, 8)}
            </Typography>
            <Button 
              onClick={() => loadScalingHistory(selectedDeployment)}
              variant="outlined"
              sx={{ mb: 2 }}
            >
              Load History
            </Button>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Event Type</TableCell>
                    <TableCell>From → To</TableCell>
                    <TableCell>Triggered By</TableCell>
                    <TableCell>Reason</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {scalingHistory.map((event, index) => (
                    <TableRow key={index}>
                      <TableCell>{new Date(event.timestamp).toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip 
                          label={event.event_type} 
                          size="small"
                          color={event.event_type === 'scale_up' ? 'success' : 'warning'}
                        />
                      </TableCell>
                      <TableCell>{event.from_replicas} → {event.to_replicas}</TableCell>
                      <TableCell>{event.triggered_by}</TableCell>
                      <TableCell>{event.reason}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        ) : (
          <Typography>Select a deployment to view scaling history</Typography>
        )}
      </TabPanel>

      {/* Deploy Dialog */}      <Dialog open={deployDialog} onClose={() => setDeployDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Deploy MASS Framework to Cloud</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Application Name"
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                helperText="Unique name for your deployment"
              />
            </Grid>
            
            {deploymentTemplates.length > 0 && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Deployment Template</InputLabel>
                  <Select
                    value={selectedTemplate}
                    onChange={(e) => {
                      setSelectedTemplate(e.target.value);
                      const template = deploymentTemplates.find(t => t.id === e.target.value);
                      if (template) {
                        setDeploymentConfig({
                          ...deploymentConfig,
                          scaling_config: {
                            ...deploymentConfig.scaling_config,
                            ...template.config.scaling
                          }
                        });
                      }
                    }}
                  >
                    <MenuItem value="">Custom Configuration</MenuItem>
                    {deploymentTemplates.map((template) => (
                      <MenuItem key={template.id} value={template.id}>
                        {template.name} - {template.description}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Environment</InputLabel>
                <Select
                  value={deploymentConfig.environment}
                  onChange={(e) => setDeploymentConfig({
                    ...deploymentConfig,
                    environment: e.target.value as any
                  })}
                >
                  <MenuItem value="development">Development</MenuItem>
                  <MenuItem value="staging">Staging</MenuItem>
                  <MenuItem value="production">Production</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Cloud Provider</InputLabel>
                <Select
                  value={deploymentConfig.cloud_provider}
                  onChange={(e) => setDeploymentConfig({
                    ...deploymentConfig,
                    cloud_provider: e.target.value as any
                  })}
                >
                  {cloudProviders.map((provider) => (
                    <MenuItem key={provider.id} value={provider.id}>
                      {provider.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Min Replicas"
                type="number"
                value={deploymentConfig.scaling_config.min_replicas}
                onChange={(e) => setDeploymentConfig({
                  ...deploymentConfig,
                  scaling_config: {
                    ...deploymentConfig.scaling_config,
                    min_replicas: parseInt(e.target.value)
                  }
                })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Max Replicas"
                type="number"
                value={deploymentConfig.scaling_config.max_replicas}
                onChange={(e) => setDeploymentConfig({
                  ...deploymentConfig,
                  scaling_config: {
                    ...deploymentConfig.scaling_config,
                    max_replicas: parseInt(e.target.value)
                  }
                })}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Security Configuration</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={deploymentConfig.security_config.enable_https}
                    onChange={(e) => setDeploymentConfig({
                      ...deploymentConfig,
                      security_config: {
                        ...deploymentConfig.security_config,
                        enable_https: e.target.checked
                      }
                    })}
                  />
                }
                label="Enable HTTPS"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={deploymentConfig.security_config.enable_authentication}
                    onChange={(e) => setDeploymentConfig({
                      ...deploymentConfig,
                      security_config: {
                        ...deploymentConfig.security_config,
                        enable_authentication: e.target.checked
                      }
                    })}
                  />
                }
                label="Enable Authentication"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={deploymentConfig.security_config.enable_rate_limiting}
                    onChange={(e) => setDeploymentConfig({
                      ...deploymentConfig,
                      security_config: {
                        ...deploymentConfig.security_config,
                        enable_rate_limiting: e.target.checked
                      }
                    })}
                  />
                }
                label="Enable Rate Limiting"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeployDialog(false)}>Cancel</Button>
          <Button onClick={handleDeploy} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Deploy'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Scale Dialog */}
      <Dialog open={scaleDialog} onClose={() => setScaleDialog(false)}>
        <DialogTitle>Scale Deployment</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Number of Replicas"
            type="number"
            value={newReplicas}
            onChange={(e) => setNewReplicas(parseInt(e.target.value))}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScaleDialog(false)}>Cancel</Button>
          <Button onClick={handleScale} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Scale'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CloudDeploymentPage;
