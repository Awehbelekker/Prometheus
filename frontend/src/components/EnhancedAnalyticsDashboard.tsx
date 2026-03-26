import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  LinearProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area
} from 'recharts';
import { TrendingUp, TrendingDown, Assessment } from '@mui/icons-material';
import { apiCall, API_ENDPOINTS } from '../config/api';


interface PerformanceData {
  profit_over_time: Array<{
    timestamp: string;
    cumulative_profit: number;
    hourly_profit: number;
  }>;
  success_rate_over_time: Array<{
    timestamp: string;
    success_rate: number;
    total_trades: number;
  }>;
  agent_performance: Array<{
    agent_id: string;
    profit_24h: number;
    trades_24h: number;
    success_rate: number;
    avg_execution_time_ms: number;
  }>;
  system_load: Array<{
    timestamp: string;
    cpu_usage: number;
    memory_usage: number;
    active_agents: number;
  }>;
}

interface TradingMetrics {
  total_trades: number;
  successful_trades: number;
  total_profit: number;
  win_rate: number;
  avg_profit_per_trade: number;
  best_performing_agent: string;
  worst_performing_agent: string;
  total_volume_traded: number;
}

const EnhancedAnalyticsDashboard: React.FC = () => {
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [tradingMetrics, setTradingMetrics] = useState<TradingMetrics | null>(null);
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedAgent, setSelectedAgent] = useState('all');
  const [loading, setLoading] = useState(true);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);

      // Fetch performance metrics via centralized API helper
      const metricsData = await apiCall(API_ENDPOINTS.PERFORMANCE_METRICS);
      setPerformanceData(metricsData);

      // Generate mock trading metrics
      const mockTradingMetrics: TradingMetrics = {
        total_trades: Math.floor(Math.random() * 500) + 200,
        successful_trades: Math.floor(Math.random() * 400) + 180,
        total_profit: Math.random() * 5000 + 1000,
        win_rate: Math.random() * 20 + 80, // 80-100%
        avg_profit_per_trade: Math.random() * 50 + 10,
        best_performing_agent: 'arbitrage-agent-1',
        worst_performing_agent: 'sync-agent-1',
        total_volume_traded: Math.random() * 1000000 + 500000
      };
      setTradingMetrics(mockTradingMetrics);

      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
    const interval = setInterval(fetchAnalyticsData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [timeRange, selectedAgent]);

  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const formatPercentage = (value: number) => `${value.toFixed(1)}%`;

  const formatTime = (timestamp: string) =>
    new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  // Safe defaults to prevent runtime errors when data is missing or partially defined
  const safePerf: PerformanceData = {
    profit_over_time: performanceData?.profit_over_time ?? [],
    success_rate_over_time: performanceData?.success_rate_over_time ?? [],
    agent_performance: performanceData?.agent_performance ?? [],
    system_load: performanceData?.system_load ?? []
  };

  if (loading) {
    return <LinearProgress />;
  }

  const agentPieData = safePerf.agent_performance.map((agent, index) => ({
    name: agent.agent_id.replace('-', ' ').toUpperCase(),
    value: agent.profit_24h,
    color: COLORS[index % COLORS.length]
  })) || [];

  return (
    <Box sx={{
      p: 3,
      minHeight: '100vh',
      backgroundColor: '#0a0a0a',
      color: 'white'
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" sx={{
          fontWeight: 700,
          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          📊 Enhanced Trading Analytics
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              label="Time Range"
            >
              <MenuItem value="1h">Last Hour</MenuItem>
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Agent</InputLabel>
            <Select
              value={selectedAgent}
              onChange={(e) => setSelectedAgent(e.target.value)}
              label="Agent"
            >
              <MenuItem value="all">All Agents</MenuItem>
              <MenuItem value="arbitrage-agent-1">Arbitrage Agent</MenuItem>
              <MenuItem value="trading-agent-1">Trading Agent</MenuItem>
              <MenuItem value="sync-agent-1">Sync Agent</MenuItem>
            </Select>
          </FormControl>
          <Button variant="outlined" onClick={fetchAnalyticsData}>
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Key Performance Indicators */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Profit (24h)
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {formatCurrency(tradingMetrics?.total_profit || 0)}
                  </Typography>
                </Box>
                <TrendingUp color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Win Rate
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {formatPercentage(tradingMetrics?.win_rate || 0)}
                  </Typography>
                </Box>
                <Assessment color="primary" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Total Trades
                  </Typography>
                  <Typography variant="h4">
                    {tradingMetrics?.total_trades?.toLocaleString()}
                  </Typography>
                </Box>
                <TrendingUp color="info" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Avg Profit/Trade
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {formatCurrency(tradingMetrics?.avg_profit_per_trade || 0)}
                  </Typography>
                </Box>
                <TrendingUp color="success" sx={{ fontSize: 40 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Charts Grid */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Profit Over Time Chart */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Cumulative Profit Over Time
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={safePerf.profit_over_time}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis tickFormatter={(value) => `$${value}`} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any) => [formatCurrency(value), 'Cumulative Profit']}
                  />
                  <Area
                    type="monotone"
                    dataKey="cumulative_profit"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Agent Profit Distribution */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Agent Profit Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
        <PieChart>
                  <Pie
          data={agentPieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {agentPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* Success Rate Trend */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Success Rate Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={safePerf.success_rate_over_time}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis domain={[80, 100]} tickFormatter={formatPercentage} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any) => [formatPercentage(value), 'Success Rate']}
                  />
                  <Line
                    type="monotone"
                    dataKey="success_rate"
                    stroke="#82ca9d"
                    strokeWidth={3}
                    dot={{ fill: '#82ca9d', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        {/* System Load Chart */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Resource Usage
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={safePerf.system_load}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tickFormatter={formatTime}
                  />
                  <YAxis domain={[0, 100]} tickFormatter={(value) => `${value}%`} />
                  <Tooltip
                    labelFormatter={(value) => new Date(value).toLocaleString()}
                    formatter={(value: any, name: string) => [
                      `${value}%`,
                      name === 'cpu_usage' ? 'CPU Usage' : 'Memory Usage'
                    ]}
                  />
                  <Line
                    type="monotone"
                    dataKey="cpu_usage"
                    stroke="#ff7300"
                    strokeWidth={2}
                    name="CPU Usage"
                  />
                  <Line
                    type="monotone"
                    dataKey="memory_usage"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Memory Usage"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Agent Performance Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Detailed Agent Performance (24h)
          </Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Agent</TableCell>
                <TableCell align="right">Profit (24h)</TableCell>
                <TableCell align="right">Trades</TableCell>
                <TableCell align="right">Success Rate</TableCell>
                <TableCell align="right">Avg Execution Time</TableCell>
                <TableCell align="center">Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {safePerf.agent_performance.map((agent) => (
                <TableRow key={agent.agent_id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {agent.agent_id.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography
                      color={agent.profit_24h >= 0 ? 'success.main' : 'error.main'}
                      fontWeight="medium"
                    >
                      {formatCurrency(agent.profit_24h)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{agent.trades_24h}</TableCell>
                  <TableCell align="right">
                    <Typography
                      color={agent.success_rate >= 90 ? 'success.main' : 'warning.main'}
                    >
                      {formatPercentage(agent.success_rate)}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">{agent.avg_execution_time_ms}ms</TableCell>
                  <TableCell align="center">
                    <Chip
                      label={agent.success_rate >= 90 ? 'Excellent' : agent.success_rate >= 80 ? 'Good' : 'Needs Attention'}
                      color={agent.success_rate >= 90 ? 'success' : agent.success_rate >= 80 ? 'warning' : 'error'}
                      size="small"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </Box>
  );
};

export default EnhancedAnalyticsDashboard;
