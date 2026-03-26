/**
 * 📈 AGENT PERFORMANCE CHART
 * 
 * Displays historical performance metrics for hierarchical agents:
 * - P&L over time
 * - Win rate trends
 * - Trade volume
 * - Performance comparison
 * 
 * Uses recharts for beautiful, responsive charts
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Grid,
  Chip,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { TrendingUp, TrendingDown, ShowChart } from '@mui/icons-material';
import { getApiUrl } from '../../config/api';
import { getJsonWithRetry } from '../../utils/network';

interface PerformanceDataPoint {
  timestamp: string;
  pnl: number;
  winRate: number;
  trades: number;
  cumulativePnl: number;
}

interface AgentPerformanceChartProps {
  agentId: string;
  agentName: string;
}

const AgentPerformanceChart: React.FC<AgentPerformanceChartProps> = ({ agentId, agentName }) => {
  const [chartType, setChartType] = useState<'pnl' | 'winrate' | 'trades'>('pnl');
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [data, setData] = useState<PerformanceDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPerformanceData();
  }, [agentId, timeRange]);

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);

      // Fetch real performance data from backend
      const response = await getJsonWithRetry<{
        success: boolean;
        agent_id: string;
        time_range: string;
        data_points: Array<{
          timestamp: string;
          pnl: number;
          cumulative_pnl: number;
          win_rate: number;
          trades: number;
        }>;
        summary?: {
          total_pnl: number;
          avg_win_rate: number;
          total_trades: number;
          best_trade: number;
          worst_trade: number;
        };
        note?: string;
      }>(
        getApiUrl(`/api/agents/${agentId}/performance-history?timeRange=${timeRange}`),
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        },
        { retries: 3, backoffMs: 500, maxBackoffMs: 4000, timeoutMs: 8000 }
      );

      // Transform backend data to frontend format
      const transformedData: PerformanceDataPoint[] = response.data_points.map(point => {
        const date = new Date(point.timestamp);
        return {
          timestamp: date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            ...(timeRange === '7d' || timeRange === '30d' ? { month: 'short', day: 'numeric' } : {})
          }),
          pnl: point.pnl,
          winRate: point.win_rate,
          trades: point.trades,
          cumulativePnl: point.cumulative_pnl
        };
      });

      setData(transformedData);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch performance data:', err);
      setLoading(false);
    }
  };

  const handleChartTypeChange = (_event: React.MouseEvent<HTMLElement>, newType: 'pnl' | 'winrate' | 'trades' | null) => {
    if (newType !== null) {
      setChartType(newType);
    }
  };

  const handleTimeRangeChange = (_event: React.MouseEvent<HTMLElement>, newRange: '1h' | '24h' | '7d' | '30d' | null) => {
    if (newRange !== null) {
      setTimeRange(newRange);
    }
  };

  const getTotalPnl = () => {
    return data.length > 0 ? data[data.length - 1].cumulativePnl : 0;
  };

  const getAvgWinRate = () => {
    if (data.length === 0) return 0;
    const sum = data.reduce((acc, d) => acc + d.winRate, 0);
    return (sum / data.length).toFixed(1);
  };

  const getTotalTrades = () => {
    return data.reduce((acc, d) => acc + d.trades, 0);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Card sx={{ 
      background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
      border: '1px solid rgba(0, 212, 255, 0.2)',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)'
    }}>
      <CardContent>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h6" sx={{ fontWeight: 700, color: '#00d4ff', mb: 0.5 }}>
              📈 {agentName} Performance
            </Typography>
            <Typography variant="caption" sx={{ color: '#999' }}>
              Historical performance metrics
            </Typography>
          </Box>
          
          {/* Time Range Selector */}
          <ToggleButtonGroup
            value={timeRange}
            exclusive
            onChange={handleTimeRangeChange}
            size="small"
            sx={{
              '& .MuiToggleButton-root': {
                color: '#999',
                borderColor: 'rgba(0, 212, 255, 0.3)',
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0, 212, 255, 0.2)',
                  color: '#00d4ff',
                  borderColor: '#00d4ff'
                }
              }
            }}
          >
            <ToggleButton value="1h">1H</ToggleButton>
            <ToggleButton value="24h">24H</ToggleButton>
            <ToggleButton value="7d">7D</ToggleButton>
            <ToggleButton value="30d">30D</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Summary Stats */}
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(0, 212, 255, 0.1)', borderRadius: 2 }}>
              <Typography variant="caption" sx={{ color: '#999', display: 'block', mb: 0.5 }}>
                Total P&L
              </Typography>
              <Typography variant="h6" sx={{ 
                color: getTotalPnl() >= 0 ? '#4caf50' : '#f44336',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: 0.5
              }}>
                {getTotalPnl() >= 0 ? <TrendingUp fontSize="small" /> : <TrendingDown fontSize="small" />}
                ${getTotalPnl().toLocaleString()}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(76, 175, 80, 0.1)', borderRadius: 2 }}>
              <Typography variant="caption" sx={{ color: '#999', display: 'block', mb: 0.5 }}>
                Avg Win Rate
              </Typography>
              <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 700 }}>
                {getAvgWinRate()}%
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={4}>
            <Box sx={{ textAlign: 'center', p: 2, backgroundColor: 'rgba(156, 39, 176, 0.1)', borderRadius: 2 }}>
              <Typography variant="caption" sx={{ color: '#999', display: 'block', mb: 0.5 }}>
                Total Trades
              </Typography>
              <Typography variant="h6" sx={{ color: '#9c27b0', fontWeight: 700 }}>
                {getTotalTrades()}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Chart Type Selector */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
          <ToggleButtonGroup
            value={chartType}
            exclusive
            onChange={handleChartTypeChange}
            size="small"
            sx={{
              '& .MuiToggleButton-root': {
                color: '#999',
                borderColor: 'rgba(0, 212, 255, 0.3)',
                '&.Mui-selected': {
                  backgroundColor: 'rgba(0, 212, 255, 0.2)',
                  color: '#00d4ff',
                  borderColor: '#00d4ff'
                }
              }
            }}
          >
            <ToggleButton value="pnl">P&L</ToggleButton>
            <ToggleButton value="winrate">Win Rate</ToggleButton>
            <ToggleButton value="trades">Trades</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Chart */}
        {chartType === 'pnl' && (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#00d4ff" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#00d4ff" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="timestamp" stroke="#999" style={{ fontSize: '12px' }} />
              <YAxis stroke="#999" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a2e',
                  border: '1px solid #00d4ff',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#00d4ff' }}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="cumulativePnl"
                stroke="#00d4ff"
                fillOpacity={1}
                fill="url(#colorPnl)"
                name="Cumulative P&L ($)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}

        {chartType === 'winrate' && (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="timestamp" stroke="#999" style={{ fontSize: '12px' }} />
              <YAxis stroke="#999" style={{ fontSize: '12px' }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a2e',
                  border: '1px solid #4caf50',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#4caf50' }}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="winRate"
                stroke="#4caf50"
                strokeWidth={2}
                dot={{ fill: '#4caf50', r: 3 }}
                name="Win Rate (%)"
              />
            </LineChart>
          </ResponsiveContainer>
        )}

        {chartType === 'trades' && (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="timestamp" stroke="#999" style={{ fontSize: '12px' }} />
              <YAxis stroke="#999" style={{ fontSize: '12px' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1a1a2e',
                  border: '1px solid #9c27b0',
                  borderRadius: '8px'
                }}
                labelStyle={{ color: '#9c27b0' }}
              />
              <Legend />
              <Bar
                dataKey="trades"
                fill="#9c27b0"
                name="Trades"
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
};

export default AgentPerformanceChart;

