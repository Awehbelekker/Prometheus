import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  alpha,
  Chip,
  Tooltip,
  IconButton,
  Paper
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Timeline,
  Speed,
  ShowChart,
  Refresh,
  BarChart
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
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend,
  Filler
);

interface WealthDataPoint {
  timestamp: string;
  value: number;
  change: number;
  changePercent: number;
}

interface RealTimeWealthTrackerProps {
  portfolioValue: number;
  isLiveTrading: boolean;
  refreshInterval?: number;
}

export const RealTimeWealthTracker: React.FC<RealTimeWealthTrackerProps> = ({ 
  portfolioValue, 
  isLiveTrading, 
  refreshInterval = 5000 
}) => {
  const [wealthHistory, setWealthHistory] = useState<WealthDataPoint[]>([]);
  const [currentChange, setCurrentChange] = useState<number>(0);
  const [currentChangePercent, setCurrentChangePercent] = useState<number>(0);
  const [dayStartValue, setDayStartValue] = useState<number>(portfolioValue);
  const [sessionHigh, setSessionHigh] = useState<number>(portfolioValue);
  const [sessionLow, setSessionLow] = useState<number>(portfolioValue);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize day start value
  useEffect(() => {
    const today = new Date().toDateString();
    const savedDayStart = localStorage.getItem(`dayStartValue_${today}_${isLiveTrading ? 'live' : 'paper'}`);
    
    if (savedDayStart) {
      setDayStartValue(parseFloat(savedDayStart));
    } else {
      setDayStartValue(portfolioValue);
      localStorage.setItem(`dayStartValue_${today}_${isLiveTrading ? 'live' : 'paper'}`, portfolioValue.toString());
    }
  }, [isLiveTrading]);

  // Update wealth tracking when portfolio value changes
  useEffect(() => {
    const now = new Date();
    const change = portfolioValue - dayStartValue;
    const changePercent = dayStartValue > 0 ? (change / dayStartValue) * 100 : 0;

    setCurrentChange(change);
    setCurrentChangePercent(changePercent);
    setLastUpdate(now);

    // Update session high/low
    if (portfolioValue > sessionHigh) {
      setSessionHigh(portfolioValue);
    }
    if (portfolioValue < sessionLow) {
      setSessionLow(portfolioValue);
    }

    // Add to wealth history (keep last 50 points for smooth chart)
    const newDataPoint: WealthDataPoint = {
      timestamp: now.toISOString(),
      value: portfolioValue,
      change: change,
      changePercent: changePercent
    };

    setWealthHistory(prev => {
      const updated = [...prev, newDataPoint];
      return updated.slice(-50); // Keep only last 50 points
    });

  }, [portfolioValue, dayStartValue, sessionHigh, sessionLow]);

  // Auto-refresh if live trading
  useEffect(() => {
    if (isLiveTrading && refreshInterval > 0) {
      intervalRef.current = setInterval(() => {
        setLastUpdate(new Date());
      }, refreshInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [isLiveTrading, refreshInterval]);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return '#4caf50';
    if (change < 0) return '#f44336';
    return '#ffb74d';
  };

  const chartData = {
    labels: wealthHistory.map(point => 
      new Date(point.timestamp).toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    ),
    datasets: [
      {
        label: 'Portfolio Value',
        data: wealthHistory.map(point => point.value),
        borderColor: '#00d4ff',
        backgroundColor: alpha('#00d4ff', 0.1),
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: 'rgba(26, 26, 46, 0.95)',
        titleColor: '#00d4ff',
        bodyColor: '#ffffff',
        borderColor: '#00d4ff',
        borderWidth: 1,
        callbacks: {
          label: (context: any) => {
            const point = wealthHistory[context.dataIndex];
            return [
              `Value: ${formatCurrency(point.value)}`,
              `Change: ${formatCurrency(point.change)} (${point.changePercent.toFixed(2)}%)`
            ];
          }
        }
      }
    },
    scales: {
      x: {
        display: true,
        grid: {
          color: alpha('#ffffff', 0.1),
        },
        ticks: {
          color: '#aaa',
          maxTicksLimit: 6
        }
      },
      y: {
        display: true,
        grid: {
          color: alpha('#ffffff', 0.1),
        },
        ticks: {
          color: '#aaa',
          callback: (value: any) => formatCurrency(value)
        }
      },
    },
    interaction: {
      intersect: false,
      mode: 'index' as const,
    },
  };

  return (
    <Paper sx={{
      mb: 4,
      p: 3,
      backgroundColor: 'rgba(26, 26, 46, 0.8)',
      border: `2px solid rgba(${isLiveTrading ? '255, 107, 53' : '0, 212, 255'}, 0.3)`,
      borderRadius: 3
    }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ 
          fontWeight: 700, 
          color: isLiveTrading ? '#ff6b35' : '#00d4ff',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}>
          <AttachMoney />
          Real-Time Wealth Tracker
          {isLiveTrading && (
            <Chip
              label="LIVE"
              size="small"
              sx={{
                backgroundColor: '#ff6b35',
                color: 'white',
                animation: 'pulse 2s infinite'
              }}
            />
          )}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="caption" sx={{ color: '#aaa' }}>
            Last Update: {lastUpdate.toLocaleTimeString()}
          </Typography>
          <IconButton size="small" sx={{ color: '#00d4ff' }}>
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Current Portfolio Value */}
        <Grid item xs={12} md={3}>
          <Card sx={{
            backgroundColor: 'rgba(0, 212, 255, 0.1)',
            border: '1px solid rgba(0, 212, 255, 0.3)'
          }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="h4" sx={{
                fontWeight: 800,
                color: '#00d4ff',
                mb: 1
              }}>
                {formatCurrency(portfolioValue)}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Current Value
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Daily Change */}
        <Grid item xs={12} md={3}>
          <Card sx={{
            backgroundColor: alpha(getChangeColor(currentChange), 0.1),
            border: `1px solid ${alpha(getChangeColor(currentChange), 0.3)}`
          }}>
            <CardContent sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                {currentChange >= 0 ? <TrendingUp /> : <TrendingDown />}
                <Typography variant="h5" sx={{
                  fontWeight: 700,
                  color: getChangeColor(currentChange)
                }}>
                  {currentChange >= 0 ? '+' : ''}{formatCurrency(currentChange)}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ 
                color: getChangeColor(currentChange),
                fontWeight: 600 
              }}>
                {currentChangePercent >= 0 ? '+' : ''}{currentChangePercent.toFixed(2)}% Today
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Session High */}
        <Grid item xs={12} md={3}>
          <Card sx={{
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            border: '1px solid rgba(76, 175, 80, 0.3)'
          }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="h6" sx={{
                fontWeight: 700,
                color: '#4caf50',
                mb: 1
              }}>
                {formatCurrency(sessionHigh)}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Session High
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Session Low */}
        <Grid item xs={12} md={3}>
          <Card sx={{
            backgroundColor: 'rgba(244, 67, 54, 0.1)',
            border: '1px solid rgba(244, 67, 54, 0.3)'
          }}>
            <CardContent sx={{ p: 2 }}>
              <Typography variant="h6" sx={{
                fontWeight: 700,
                color: '#f44336',
                mb: 1
              }}>
                {formatCurrency(sessionLow)}
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Session Low
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Real-Time Chart */}
        <Grid item xs={12}>
          <Card sx={{
            backgroundColor: 'rgba(26, 26, 46, 0.6)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ 
                mb: 2, 
                fontWeight: 700, 
                color: '#00d4ff',
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}>
                <Timeline />
                Wealth Growth Chart ({wealthHistory.length} data points)
              </Typography>
              
              {wealthHistory.length > 1 ? (
                <Box sx={{ height: 300 }}>
                  <Line data={chartData} options={chartOptions} />
                </Box>
              ) : (
                <Box sx={{ 
                  height: 300, 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: '#aaa'
                }}>
                  <Typography>
                    Collecting data... {isLiveTrading ? 'Live tracking active' : 'Paper trading mode'}
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default RealTimeWealthTracker;
