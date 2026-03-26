import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Grid,
  Button,
  Alert,
  CircularProgress
} from '@mui/material';
import { apiService, AlpacaAccountStatus } from '../services/api';

interface AlpacaStatusCardProps {
  onStartDemo?: () => void;
}

const AlpacaStatusCard: React.FC<AlpacaStatusCardProps> = ({ onStartDemo }) => {
  const [status, setStatus] = useState<AlpacaAccountStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAlpacaStatus();
  }, []);

  const loadAlpacaStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      const alpacaStatus = await apiService.getAlpacaStatus();
      setStatus(alpacaStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load Alpaca status');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: string | undefined) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(parseFloat(value));
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="center" p={2}>
            <CircularProgress />
            <Typography variant="body1" sx={{ ml: 2 }}>
              Loading Alpaca Status...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error" action={
            <Button color="inherit" size="small" onClick={loadAlpacaStatus}>
              Retry
            </Button>
          }>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return null;
  }

  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Typography variant="h6" component="h2">
            Alpaca Trading Account
          </Typography>
          <Chip
            label={status.mode.toUpperCase()}
            color={status.mode === 'paper' ? 'info' : 'warning'}
            variant="outlined"
          />
        </Box>

        {!status.configured && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            {status.note || 'Alpaca API keys not configured'}
          </Alert>
        )}

        {status.error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            Connection Error: {status.error}
          </Alert>
        )}

        {status.configured && status.account && (
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Account Number
              </Typography>
              <Typography variant="body1" fontFamily="monospace">
                {status.account.account_number}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Status
              </Typography>
              <Chip
                label={status.account.status}
                color={status.account.status === 'ACTIVE' ? 'success' : 'default'}
                size="small"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Cash
              </Typography>
              <Typography variant="h6" color="primary">
                {formatCurrency(status.account.cash)}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Buying Power
              </Typography>
              <Typography variant="h6" color="secondary">
                {formatCurrency(status.account.buying_power)}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Portfolio Value
              </Typography>
              <Typography variant="h6">
                {formatCurrency(status.account.portfolio_value)}
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <Typography variant="body2" color="text.secondary">
                Trading Status
              </Typography>
              <Chip
                label={status.account.trading_blocked ? 'BLOCKED' : 'ENABLED'}
                color={status.account.trading_blocked ? 'error' : 'success'}
                size="small"
              />
            </Grid>

            {status.account.pattern_day_trader && (
              <Grid item xs={12}>
                <Alert severity="info" variant="outlined">
                  Pattern Day Trader restrictions apply
                </Alert>
              </Grid>
            )}
          </Grid>
        )}

        <Box mt={2} display="flex" gap={1}>
          <Button variant="outlined" onClick={loadAlpacaStatus} size="small">
            Refresh
          </Button>
          {status.configured && onStartDemo && (
            <Button variant="contained" onClick={onStartDemo} size="small">
              Start 48h Demo
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default AlpacaStatusCard;
