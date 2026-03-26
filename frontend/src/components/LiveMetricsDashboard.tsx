import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { Refresh, ShowChart, TrendingUp, Schedule, AccountBalance } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { LiveMetrics } from '../hooks/useWebSocket';
import { AnimatedCounter, ProfitCounter, PercentageCounter, NumberCounter } from './AnimatedCounter';

interface LiveMetricsDashboardProps {
  metrics: LiveMetrics | null;
  isConnected: boolean;
  onRefresh: () => void;
}

export const LiveMetricsDashboard: React.FC<LiveMetricsDashboardProps> = ({
  metrics,
  isConnected,
  onRefresh
}) => {
  const [previousMetrics, setPreviousMetrics] = useState<LiveMetrics | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  useEffect(() => {
    if (metrics && JSON.stringify(metrics) !== JSON.stringify(previousMetrics)) {
      setPreviousMetrics(metrics);
      setLastUpdate(new Date());
    }
  }, [metrics, previousMetrics]);

  if (!metrics) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" height={200}>
            <Typography variant="h6" color="textSecondary">
              Connecting to Revolutionary Engines...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const currentProfit = metrics.currentValue - metrics.initialValue;
  const returnPercentage = ((metrics.currentValue - metrics.initialValue) / metrics.initialValue) * 100;
  const timeRemaining = 48 - metrics.runTimeHours;
  const progressPercentage = (metrics.runTimeHours / 48) * 100;

  const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" sx={{ 
          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🚀 Revolutionary Engines LIVE
        </Typography>
        
        <Box display="flex" alignItems="center" gap={2}>
          <Chip
            label={isConnected ? 'REAL-TIME' : 'SIMULATED'}
            color={isConnected ? 'success' : 'warning'}
            icon={isConnected ? <ShowChart /> : <Schedule />}
          />
          
          <Tooltip title="Refresh Data">
            <IconButton onClick={onRefresh} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Typography variant="caption" color="textSecondary">
            Last Update: {lastUpdate.toLocaleTimeString()}
          </Typography>
        </Box>
      </Box>

      {/* Main Performance Cards */}
      <Grid container spacing={3} mb={3}>
        {/* Current Investment Value */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.5 }}
          >
            <Card sx={{ 
              background: 'linear-gradient(135deg, #4caf50, #66bb6a)',
              color: 'white',
              height: '100%'
            }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <AccountBalance sx={{ mr: 1 }} />
                  <Typography variant="h6">Current Value</Typography>
                </Box>
                <AnimatedCounter
                  value={metrics.currentValue}
                  prefix="$"
                  variant="h3"
                  decimals={2}
                  color="white"
                  showTrend={true}
                  previousValue={previousMetrics?.currentValue}
                />
                <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
                  Started with ${metrics.initialValue}
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Profit/Loss */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card sx={{ 
              background: currentProfit >= 0 
                ? 'linear-gradient(135deg, #4caf50, #66bb6a)' 
                : 'linear-gradient(135deg, #f44336, #ef5350)',
              color: 'white',
              height: '100%'
            }}>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <TrendingUp sx={{ mr: 1 }} />
                  <Typography variant="h6">Profit/Loss</Typography>
                </Box>
                <ProfitCounter
                  value={currentProfit}
                  previousValue={previousMetrics ? (previousMetrics.currentValue - previousMetrics.initialValue) : undefined}
                  showTrend={true}
                />
                <Box display="flex" alignItems="center" mt={1}>
                  <PercentageCounter
                    value={returnPercentage}
                    previousValue={previousMetrics ? ((previousMetrics.currentValue - previousMetrics.initialValue) / previousMetrics.initialValue) * 100 : undefined}
                    showTrend={false}
                  />
                  <Typography variant="body2" sx={{ opacity: 0.8, ml: 1 }}>
                    return
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Win Rate */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ 
              background: 'linear-gradient(135deg, #00d4ff, #0099cc)',
              color: 'white',
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" mb={2}>Win Rate</Typography>
                <PercentageCounter
                  value={metrics.winRate}
                  previousValue={previousMetrics?.winRate}
                  showTrend={true}
                />
                <LinearProgress
                  variant="determinate"
                  value={metrics.winRate}
                  sx={{
                    mt: 2,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: 'rgba(255,255,255,0.3)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: 'white'
                    }
                  }}
                />
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Total Trades */}
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card sx={{ 
              background: 'linear-gradient(135deg, #ff6b35, #ff8a65)',
              color: 'white',
              height: '100%'
            }}>
              <CardContent>
                <Typography variant="h6" mb={2}>Total Trades</Typography>
                <NumberCounter
                  value={metrics.totalTrades}
                  previousValue={previousMetrics?.totalTrades}
                  showTrend={true}
                />
                <Typography variant="body2" sx={{ opacity: 0.8, mt: 1 }}>
                  in {metrics.runTimeHours.toFixed(1)} hours
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Secondary Metrics */}
      <Grid container spacing={3}>
        {/* Demo Progress */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                48-Hour Demo Progress
              </Typography>
              
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2">
                  Runtime: {metrics.runTimeHours.toFixed(1)} hours
                </Typography>
                <Typography variant="body2">
                  Remaining: {timeRemaining.toFixed(1)} hours
                </Typography>
              </Box>
              
              <LinearProgress
                variant="determinate"
                value={progressPercentage}
                sx={{
                  height: 12,
                  borderRadius: 6,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
                    borderRadius: 6
                  }
                }}
              />
              
              <Typography variant="caption" color="textSecondary" mt={1} display="block">
                {progressPercentage.toFixed(1)}% Complete
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Hourly Performance */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" mb={2}>
                Performance Rate
              </Typography>
              
              <Box textAlign="center">
                <PercentageCounter
                  value={metrics.hourlyReturn}
                  previousValue={previousMetrics?.hourlyReturn}
                  showTrend={true}
                />
                <Typography variant="body2" color="textSecondary">
                  per hour
                </Typography>
                
                <Typography variant="h6" mt={2} color="primary">
                  ${(metrics.totalPnL || 0).toLocaleString()}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Total System P&L
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
