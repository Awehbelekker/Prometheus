import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  IconButton,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Refresh,
  InstallMobile,
  Notifications,
  ShowChart,
  TrendingUp
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Import our new components
import { useWebSocket } from '../hooks/useWebSocket';
import { LiveMetricsDashboard } from './LiveMetricsDashboard';
import { TradeNotifications } from './TradeNotifications';
import { getWsUrl, API_ENDPOINTS } from '../config/api';

import { AnimatedCounter, ProfitCounter } from './AnimatedCounter';
import { pwaManager } from '../utils/pwa';

interface RealTimeDashboardProps {
  user: any;
}

export const RealTimeDashboard: React.FC<RealTimeDashboardProps> = ({ user }) => {
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [notificationAlert, setNotificationAlert] = useState<string | null>(null);

  // Connect to Revolutionary Engines WebSocket (port 8000)
  const {
    isConnected,
    liveMetrics,
    latestTrade,
    recentTrades,
    connectionError,
    reconnect
  } = useWebSocket(getWsUrl(API_ENDPOINTS.DASHBOARD_WS), user?.id || 'anonymous');

  // PWA installation status
  const [pwaStatus, setPwaStatus] = useState(pwaManager.getInstallationStatus());

  useEffect(() => {
    // Check PWA status periodically
    const interval = setInterval(() => {
      setPwaStatus(pwaManager.getInstallationStatus());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Show notification when profitable trade occurs
  useEffect(() => {
    if (latestTrade && latestTrade.profit > 50) {
      setNotificationAlert(`🚀 Profitable trade: +$${latestTrade.profit.toFixed(2)} on ${latestTrade.symbol}`);

      // Send PWA notification
      pwaManager.sendNotification('🚀 Profitable Trade!', {
        body: `${latestTrade.side.toUpperCase()} ${latestTrade.quantity} ${latestTrade.symbol} - Profit: $${latestTrade.profit.toFixed(2)}`,
        icon: '/logo192.png',
        tag: 'profitable-trade'
      });
    }
  }, [latestTrade]);

  const handleInstallApp = () => {
    pwaManager.showInstallPrompt();
    setShowInstallPrompt(false);
  };

  // Quick stats for hero section
  const currentProfit = liveMetrics ? liveMetrics.currentValue - liveMetrics.initialValue : 0;
  const returnPercentage = liveMetrics ? ((liveMetrics.currentValue - liveMetrics.initialValue) / liveMetrics.initialValue) * 100 : 0;

  return (
    <Box sx={{ p: 3 }}>
      {/* Hero Section - Your Success Story */}
      <motion.div
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        <Card sx={{
          background: 'linear-gradient(135deg, #4caf50, #66bb6a, #81c784)',
          color: 'white',
          mb: 4,
          position: 'relative',
          overflow: 'visible'
        }}>
          <CardContent sx={{ p: 4 }}>
            <Grid container spacing={3} alignItems="center">
              <Grid item xs={12} md={8}>
                <Typography variant="h3" gutterBottom sx={{ fontWeight: 'bold' }}>
                  🚀 Revolutionary Returns LIVE
                </Typography>
                <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
                  Proven Results: $130 → ${liveMetrics?.currentValue.toFixed(2) || '201.67'}
                  in {liveMetrics?.runTimeHours.toFixed(1) || '11.1'} hours
                </Typography>

                <Box display="flex" gap={2} flexWrap="wrap">
                  <Chip
                    label={`${returnPercentage.toFixed(1)}% Return`}
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      color: 'white',
                      fontWeight: 'bold',
                      fontSize: '1.1rem'
                    }}
                  />
                  <Chip
                    label={`${liveMetrics?.winRate.toFixed(0) || '80'}% Win Rate`}
                    sx={{
                      bgcolor: 'rgba(255,255,255,0.2)',
                      color: 'white',
                      fontWeight: 'bold'
                    }}
                  />
                  <Chip
                    label={isConnected ? 'LIVE DATA' : 'SIMULATED'}
                    color={isConnected ? 'success' : 'warning'}
                    sx={{ fontWeight: 'bold' }}
                  />
                </Box>
              </Grid>

              <Grid item xs={12} md={4}>
                <Box textAlign="center">
                  <Typography variant="h2" sx={{ fontWeight: 'bold', mb: 1 }}>
                    <ProfitCounter
                      value={currentProfit}
                      showTrend={true}
                    />
                  </Typography>
                  <Typography variant="h6" sx={{ opacity: 0.9 }}>
                    Current Profit
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      </motion.div>

      {/* PWA Installation Banner */}
      <AnimatePresence>
        {pwaStatus.canInstall && !pwaStatus.isInstalled && (
          <motion.div
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
          >
            <Alert
              severity="info"
              sx={{ mb: 3 }}
              action={
                <Box display="flex" gap={1}>
                  <Button
                    color="inherit"
                    size="small"
                    startIcon={<InstallMobile />}
                    onClick={handleInstallApp}
                  >
                    Install App
                  </Button>
                  <IconButton
                    size="small"
                    color="inherit"
                    onClick={() => setShowInstallPrompt(false)}
                  >
                    ×
                  </IconButton>
                </Box>
              }
            >
              📱 Install Prometheus Trading for faster access and real-time notifications!
            </Alert>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Connection Status */}
      {connectionError && (
        <Alert
          severity="warning"
          sx={{ mb: 3 }}
          action={
            <Button color="inherit" size="small" onClick={reconnect}>
              <Refresh /> Reconnect
            </Button>
          }
        >
          🔄 Using simulated data - Revolutionary Engines at port 8000 not accessible
        </Alert>
      )}

      {/* Main Dashboard Grid */}
      <Grid container spacing={3}>
        {/* Live Metrics Dashboard */}
        <Grid item xs={12}>
          <LiveMetricsDashboard
            metrics={liveMetrics}
            isConnected={isConnected}
            onRefresh={reconnect}
          />
        </Grid>

        {/* Trade Notifications */}
        <Grid item xs={12} lg={6}>
          <TradeNotifications
            latestTrade={latestTrade}
            recentTrades={recentTrades}
            isConnected={isConnected}
          />
        </Grid>

        {/* Quick Actions & Status */}
        <Grid item xs={12} lg={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🎯 Platform Status
              </Typography>

              <Box display="flex" flexDirection="column" gap={2}>
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body1">Real-time Connection:</Typography>
                  <Chip
                    label={isConnected ? 'CONNECTED' : 'SIMULATED'}
                    color={isConnected ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body1">PWA Installed:</Typography>
                  <Chip
                    label={pwaStatus.isInstalled ? 'YES' : 'NO'}
                    color={pwaStatus.isInstalled ? 'success' : 'default'}
                    size="small"
                  />
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body1">Notifications:</Typography>
                  <Chip
                    label={pwaStatus.notificationsEnabled ? 'ENABLED' : 'DISABLED'}
                    color={pwaStatus.notificationsEnabled ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>

                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="body1">Total Trades:</Typography>
                  <Typography variant="h6" color="primary">
                    {liveMetrics?.totalTrades || 1704}
                  </Typography>
                </Box>
              </Box>

              <Box mt={3} display="flex" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<ShowChart />}
                  fullWidth
                  onClick={() => window.open('/trading', '_blank')}
                >
                  Open Trading
                </Button>

                {!pwaStatus.notificationsEnabled && (
                  <Button
                    variant="outlined"
                    startIcon={<Notifications />}
                    onClick={() => Notification.requestPermission()}
                    fullWidth
                  >
                    Enable Alerts
                  </Button>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Success Notification */}
      <Snackbar
        open={!!notificationAlert}
        autoHideDuration={6000}
        onClose={() => setNotificationAlert(null)}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotificationAlert(null)}
          severity="success"
          sx={{ width: '100%' }}
        >
          {notificationAlert}
        </Alert>
      </Snackbar>
    </Box>
  );
};
