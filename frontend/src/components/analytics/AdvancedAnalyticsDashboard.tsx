/**
 * AdvancedAnalyticsDashboard Component
 * Comprehensive analytics with charts, insights, and data export
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Tabs,
  Tab,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  Download,
  Refresh,
  DateRange,
  ShowChart,
  PieChart,
  BarChart as BarChartIcon
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { apiService } from '../../services/api';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface AdvancedAnalyticsDashboardProps {
  userId: string;
}

type TimeRange = '1D' | '1W' | '1M' | '3M' | '1Y' | 'ALL';
type AnalyticsTab = 'performance' | 'trades' | 'risk' | 'insights';

const AdvancedAnalyticsDashboard: React.FC<AdvancedAnalyticsDashboardProps> = ({ userId }) => {
  const [activeTab, setActiveTab] = useState<AnalyticsTab>('performance');
  const [timeRange, setTimeRange] = useState<TimeRange>('1M');

  const { data: analyticsData, isLoading, refetch } = useQuery({
    queryKey: ['advanced-analytics', userId, timeRange],
    queryFn: async () => {
      // Mock data for now - replace with actual API call when endpoint is ready
      return {
        performance: { totalReturn: 15.5, winRate: 68, sharpeRatio: 1.8 },
        trades: { total: 150, profitable: 102, avgProfit: 250 },
        risk: { maxDrawdown: 8.5, volatility: 12.3, beta: 0.95 },
        performanceData: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          values: [10000, 10500, 11200, 10800, 11500, 12000],
          benchmark: [10000, 10200, 10400, 10600, 10800, 11000]
        },
        tradeDistribution: [102, 38, 10],
        sectorAllocation: {
          labels: ['Technology', 'Finance', 'Healthcare', 'Energy'],
          values: [40, 30, 20, 10]
        },
        riskMetrics: {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
          values: [8.5, 7.2, 9.1, 6.8, 7.5, 8.0]
        }
      };
    }
  });

  const handleExport = (format: 'csv' | 'pdf' | 'json') => {
    // Export analytics data
    const dataStr = format === 'json' 
      ? JSON.stringify(analyticsData, null, 2)
      : convertToCSV(analyticsData);
    
    const blob = new Blob([dataStr], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `analytics-${userId}-${timeRange}.${format}`;
    link.click();
  };

  const convertToCSV = (data: any) => {
    // Simple CSV conversion
    return 'Date,Value,Type\n' + 
      (data?.trades || []).map((t: any) => `${t.date},${t.value},${t.type}`).join('\n');
  };

  // Chart configurations
  const performanceChartData = {
    labels: analyticsData?.performanceData?.labels || [],
    datasets: [
      {
        label: 'Portfolio Value',
        data: analyticsData?.performanceData?.values || [],
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0, 212, 255, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Benchmark',
        data: analyticsData?.performanceData?.benchmark || [],
        borderColor: '#888',
        backgroundColor: 'transparent',
        borderDash: [5, 5],
        tension: 0.4
      }
    ]
  };

  const tradeDistributionData = {
    labels: ['Winning Trades', 'Losing Trades', 'Break-even'],
    datasets: [
      {
        data: analyticsData?.tradeDistribution || [60, 30, 10],
        backgroundColor: ['#4caf50', '#f44336', '#ff9800'],
        borderWidth: 0
      }
    ]
  };

  const sectorAllocationData = {
    labels: analyticsData?.sectorAllocation?.labels || ['Technology', 'Finance', 'Healthcare', 'Energy'],
    datasets: [
      {
        data: analyticsData?.sectorAllocation?.values || [40, 30, 20, 10],
        backgroundColor: ['#00d4ff', '#ff6b35', '#4caf50', '#ff9800'],
        borderWidth: 0
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#fff'
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: '#fff',
        bodyColor: '#fff'
      }
    },
    scales: {
      x: {
        ticks: { color: '#888' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      y: {
        ticks: { color: '#888' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    }
  };

  return (
    <Box>
      {/* Header */}
      <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(0, 212, 255, 0.3)', mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Assessment sx={{ color: '#00d4ff', fontSize: 32 }} />
              <Typography variant="h5" sx={{ color: '#fff', fontWeight: 700 }}>
                Advanced Analytics
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <FormControl size="small" sx={{ minWidth: 120 }}>
                <Select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value as TimeRange)}
                  sx={{ color: '#fff', '& .MuiOutlinedInput-notchedOutline': { borderColor: '#00d4ff' } }}
                >
                  <MenuItem value="1D">1 Day</MenuItem>
                  <MenuItem value="1W">1 Week</MenuItem>
                  <MenuItem value="1M">1 Month</MenuItem>
                  <MenuItem value="3M">3 Months</MenuItem>
                  <MenuItem value="1Y">1 Year</MenuItem>
                  <MenuItem value="ALL">All Time</MenuItem>
                </Select>
              </FormControl>
              <IconButton onClick={() => refetch()} sx={{ color: '#00d4ff' }}>
                <Refresh />
              </IconButton>
              <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={() => handleExport('csv')}
                sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}
              >
                Export
              </Button>
            </Box>
          </Box>

          {/* Tabs */}
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{
              '& .MuiTab-root': { color: '#888', '&.Mui-selected': { color: '#00d4ff' } },
              '& .MuiTabs-indicator': { backgroundColor: '#00d4ff' }
            }}
          >
            <Tab label="Performance" value="performance" icon={<TrendingUp />} iconPosition="start" />
            <Tab label="Trades" value="trades" icon={<ShowChart />} iconPosition="start" />
            <Tab label="Risk Analysis" value="risk" icon={<BarChartIcon />} iconPosition="start" />
            <Tab label="AI Insights" value="insights" icon={<Assessment />} iconPosition="start" />
          </Tabs>
        </CardContent>
      </Card>

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ color: '#fff', mb: 2 }}>
                  Portfolio Performance
                </Typography>
                <Box sx={{ height: 400 }}>
                  <Line data={performanceChartData} options={chartOptions} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ color: '#fff', mb: 2 }}>
                  Trade Distribution
                </Typography>
                <Box sx={{ height: 300 }}>
                  <Doughnut data={tradeDistributionData} options={{ ...chartOptions, scales: undefined }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card sx={{ background: 'rgba(26, 26, 26, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography variant="h6" sx={{ color: '#fff', mb: 2 }}>
                  Sector Allocation
                </Typography>
                <Box sx={{ height: 300 }}>
                  <Pie data={sectorAllocationData} options={{ ...chartOptions, scales: undefined }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Other tabs content would go here */}
    </Box>
  );
};

export default AdvancedAnalyticsDashboard;

