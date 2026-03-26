import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent,
  IconButton,
  Tooltip,
  Chip,
  LinearProgress,
  Fade,
  useTheme
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Speed,
  Memory,
  Storage,
  NetworkCheck,
  Timeline,
  Assessment,
  Refresh
} from '@mui/icons-material';
import ModernCard from './ModernCard';

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor: string;
    borderColor: string;
    borderWidth: number;
  }[];
}

interface PerformanceMetric {
  name: string;
  value: number;
  maxValue: number;
  color: string;
  icon: React.ReactNode;
  trend: 'up' | 'down' | 'stable';
  trendValue: number;
}

interface TimeSeriesData {
  timestamp: string;
  value: number;
  category: string;
}

const DataVisualization: React.FC = () => {
  const theme = useTheme();
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetric[]>([
    {
      name: 'CPU Usage',
      value: 65,
      maxValue: 100,
      color: theme.palette.primary.main,
      icon: <Speed />,
      trend: 'up',
      trendValue: 5.2
    },
    {
      name: 'Memory Usage',
      value: 78,
      maxValue: 100,
      color: theme.palette.secondary.main,
      icon: <Memory />,
      trend: 'up',
      trendValue: 2.1
    },
    {
      name: 'Disk Usage',
      value: 45,
      maxValue: 100,
      color: theme.palette.warning.main,
      icon: <Storage />,
      trend: 'stable',
      trendValue: 0
    },
    {
      name: 'Network',
      value: 92,
      maxValue: 100,
      color: theme.palette.info.main,
      icon: <NetworkCheck />,
      trend: 'down',
      trendValue: -1.5
    }
  ]);

  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([
    { timestamp: '00:00', value: 45, category: 'CPU' },
    { timestamp: '02:00', value: 52, category: 'CPU' },
    { timestamp: '04:00', value: 48, category: 'CPU' },
    { timestamp: '06:00', value: 61, category: 'CPU' },
    { timestamp: '08:00', value: 68, category: 'CPU' },
    { timestamp: '10:00', value: 72, category: 'CPU' },
    { timestamp: '12:00', value: 65, category: 'CPU' },
    { timestamp: '14:00', value: 58, category: 'CPU' },
    { timestamp: '16:00', value: 63, category: 'CPU' },
    { timestamp: '18:00', value: 70, category: 'CPU' },
    { timestamp: '20:00', value: 75, category: 'CPU' },
    { timestamp: '22:00', value: 62, category: 'CPU' }
  ]);

  const [agentPerformance, setAgentPerformance] = useState([
    { name: 'Data Analyzer', efficiency: 85, tasks: 12, status: 'active' },
    { name: 'Predictive Agent', efficiency: 92, tasks: 8, status: 'active' },
    { name: 'Optimization Agent', efficiency: 78, tasks: 15, status: 'busy' },
    { name: 'Anomaly Detector', efficiency: 88, tasks: 6, status: 'active' }
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setPerformanceMetrics(prev => prev.map(metric => ({
        ...metric,
        value: Math.max(0, Math.min(100, metric.value + (Math.random() - 0.5) * 2))
      })));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const renderPerformanceChart = () => {
    const maxValue = Math.max(...timeSeriesData.map(d => d.value));
    const minValue = Math.min(...timeSeriesData.map(d => d.value));
    const range = maxValue - minValue;

    return (
      <Box sx={{ position: 'relative', height: 200 }}>
        <svg width="100%" height="100%" viewBox="0 0 400 200">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={theme.palette.primary.main} stopOpacity={0.8} />
              <stop offset="100%" stopColor={theme.palette.primary.main} stopOpacity={0.2} />
            </linearGradient>
          </defs>
          
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map((y, i) => (
            <line
              key={i}
              x1="0"
              y1={200 - (y / 100) * 200}
              x2="400"
              y2={200 - (y / 100) * 200}
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="1"
            />
          ))}

          {/* Data line */}
          <path
            d={timeSeriesData.map((point, i) => {
              const x = (i / (timeSeriesData.length - 1)) * 400;
              const y = 200 - ((point.value - minValue) / range) * 180;
              return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
            }).join(' ')}
            stroke={theme.palette.primary.main}
            strokeWidth="3"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
          />

          {/* Area fill */}
          <path
            d={`M 0 200 ${timeSeriesData.map((point, i) => {
              const x = (i / (timeSeriesData.length - 1)) * 400;
              const y = 200 - ((point.value - minValue) / range) * 180;
              return `L ${x} ${y}`;
            }).join(' ')} L 400 200 Z`}
            fill="url(#chartGradient)"
          />

          {/* Data points */}
          {timeSeriesData.map((point, i) => {
            const x = (i / (timeSeriesData.length - 1)) * 400;
            const y = 200 - ((point.value - minValue) / range) * 180;
            return (
              <circle
                key={i}
                cx={x}
                cy={y}
                r="4"
                fill={theme.palette.primary.main}
                stroke="white"
                strokeWidth="2"
              />
            );
          })}
        </svg>
      </Box>
    );
  };

  const renderGaugeChart = (value: number, maxValue: number, color: string, label: string) => {
    const percentage = (value / maxValue) * 100;
    const radius = 40;
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = (percentage / 100) * circumference;

    return (
      <Box sx={{ textAlign: 'center', p: 2 }}>
        <Box sx={{ position: 'relative', display: 'inline-block' }}>
          <svg width="120" height="120" viewBox="0 0 120 120">
            {/* Background circle */}
            <circle
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="8"
            />
            {/* Progress circle */}
            <circle
              cx="60"
              cy="60"
              r={radius}
              fill="none"
              stroke={color}
              strokeWidth="8"
              strokeDasharray={strokeDasharray}
              strokeDashoffset={circumference - strokeDasharray}
              strokeLinecap="round"
              transform="rotate(-90 60 60)"
            />
          </svg>
          <Box sx={{ 
            position: 'absolute', 
            top: '50%', 
            left: '50%', 
            transform: 'translate(-50%, -50%)',
            textAlign: 'center'
          }}>
            <Typography variant="h6" sx={{ fontWeight: 700, color }}>
              {Math.round(percentage)}%
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {label}
            </Typography>
          </Box>
        </Box>
      </Box>
    );
  };

  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ p: { xs: 2, md: 3 } }}>
        <Typography 
          variant="h4" 
          sx={{ 
            mb: 4, 
            fontWeight: 700,
            background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Data Visualization
        </Typography>

        {/* Performance Metrics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {performanceMetrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <ModernCard
                title={metric.name}
                content={
                  <Box>
                    {renderGaugeChart(metric.value, metric.maxValue, metric.color, metric.name)}
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                      {metric.trend === 'up' ? (
                        <TrendingUp sx={{ color: 'success.main', fontSize: 16 }} />
                      ) : metric.trend === 'down' ? (
                        <TrendingDown sx={{ color: 'error.main', fontSize: 16 }} />
                      ) : (
                        <Box sx={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: 'grey.500' }} />
                      )}
                      <Typography variant="caption" color="text.secondary">
                        {metric.trendValue > 0 ? '+' : ''}{metric.trendValue.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Box>
                }
                icon={metric.icon}
                status={metric.trend === 'up' ? 'success' : metric.trend === 'down' ? 'error' : 'info'}
              />
            </Grid>
          ))}
        </Grid>

        {/* Time Series Chart */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <ModernCard
              title="Performance Over Time"
              subtitle="CPU usage in the last 24 hours"
              content={
                <Box>
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="h6" sx={{ mb: 1 }}>
                      CPU Usage Trend
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Average: {Math.round(timeSeriesData.reduce((sum, d) => sum + d.value, 0) / timeSeriesData.length)}%
                    </Typography>
                  </Box>
                  {renderPerformanceChart()}
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                    <Typography variant="caption" color="text.secondary">
                      {timeSeriesData[0].timestamp}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {timeSeriesData[timeSeriesData.length - 1].timestamp}
                    </Typography>
                  </Box>
                </Box>
              }
              icon={<Timeline />}
              status="info"
            />
          </Grid>

          <Grid item xs={12} md={4}>
            <ModernCard
              title="Agent Performance"
              subtitle="Efficiency metrics"
              content={
                <Box>
                  {agentPerformance.map((agent, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, borderRadius: 2, backgroundColor: 'rgba(255,255,255,0.02)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {agent.name}
                        </Typography>
                        <Chip 
                          label={agent.status} 
                          size="small" 
                          color={agent.status === 'active' ? 'success' : 'warning'}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
                        <Box sx={{ flex: 1 }}>
                          <LinearProgress
                            variant="determinate"
                            value={agent.efficiency}
                            sx={{
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: 'rgba(255,255,255,0.1)',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: theme.palette.primary.main,
                                borderRadius: 3
                              }
                            }}
                          />
                        </Box>
                        <Typography variant="body2" fontWeight={600}>
                          {agent.efficiency}%
                        </Typography>
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {agent.tasks} tasks completed
                      </Typography>
                    </Box>
                  ))}
                </Box>
              }
              icon={<Assessment />}
              status="info"
            />
          </Grid>
        </Grid>

        {/* Real-time Metrics */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <ModernCard
              title="System Health"
              subtitle="Real-time monitoring"
              content={
                <Box>
                  {[
                    { label: 'Response Time', value: 120, unit: 'ms', color: 'success.main' },
                    { label: 'Error Rate', value: 0.5, unit: '%', color: 'warning.main' },
                    { label: 'Throughput', value: 1500, unit: 'req/s', color: 'info.main' },
                    { label: 'Active Sessions', value: 25, unit: '', color: 'primary.main' }
                  ].map((metric, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          {metric.label}
                        </Typography>
                        <Typography variant="body2" fontWeight={600} sx={{ color: metric.color }}>
                          {metric.value}{metric.unit}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(100, (metric.value / (metric.label === 'Response Time' ? 200 : metric.label === 'Error Rate' ? 5 : metric.label === 'Throughput' ? 2000 : 50)) * 100)}
                        sx={{
                          height: 4,
                          borderRadius: 2,
                          backgroundColor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: metric.color,
                            borderRadius: 2
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              }
              icon={<Speed />}
              status="success"
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <ModernCard
              title="Resource Distribution"
              subtitle="Current allocation"
              content={
                <Box>
                  {[
                    { label: 'CPU Cores', used: 6, total: 8, color: 'primary.main' },
                    { label: 'Memory', used: 12, total: 16, color: 'secondary.main' },
                    { label: 'Storage', used: 500, total: 1000, color: 'warning.main' },
                    { label: 'Network', used: 80, total: 100, color: 'info.main' }
                  ].map((resource, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          {resource.label}
                        </Typography>
                        <Typography variant="body2" fontWeight={600}>
                          {resource.used}/{resource.total} {resource.label === 'Storage' ? 'GB' : resource.label === 'Network' ? 'Mbps' : ''}
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={(resource.used / resource.total) * 100}
                        sx={{
                          height: 6,
                          borderRadius: 3,
                          backgroundColor: 'rgba(255,255,255,0.1)',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: resource.color,
                            borderRadius: 3
                          }
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              }
              icon={<Memory />}
              status="info"
            />
          </Grid>
        </Grid>
      </Box>
    </Fade>
  );
};

export default DataVisualization; 