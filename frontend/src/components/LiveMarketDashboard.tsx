import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  TextField,
  Button,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import { Refresh, TrendingUp, TrendingDown } from '@mui/icons-material';

import { getApiUrl } from '../config/api';
import { getJsonWithRetry } from '../utils/network';

// Minimal shape of market data returned by /api/market-data
interface Quote {
  symbol: string;
  price: number;
  change_percent?: number;
  change?: number;
  volume?: number;
  timestamp?: string;
  source?: string;
}

const DEFAULT_SYMBOLS = ['AAPL','SPY','QQQ','TSLA','NVDA','AMD','GOOGL','MSFT'];

const LiveMarketDashboard: React.FC = () => {
  const [symbolsText, setSymbolsText] = useState(DEFAULT_SYMBOLS.join(','));
  const symbols = useMemo(() => symbolsText.split(',').map(s => s.trim().toUpperCase()).filter(Boolean), [symbolsText]);

  const [quotes, setQuotes] = useState<Record<string, Quote | null>>({});
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const timerRef = useRef<number | null>(null);

  const fetchQuotes = async () => {
    try {
      setLoading(true);
      const params = encodeURIComponent(symbols.join(','));
      const url = getApiUrl(`/api/market-data?symbols=${params}`);
      const data = await getJsonWithRetry(url, { method: 'GET' }, { retries: 4, backoffMs: 500, maxBackoffMs: 6000, timeoutMs: 8000 });
      setQuotes(data || {});
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (e) {
      console.error('Live quotes fetch failed:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchQuotes();
    // Auto refresh every 5s
    timerRef.current = window.setInterval(fetchQuotes, 5000);
    return () => { if (timerRef.current) window.clearInterval(timerRef.current); };

  }, [symbolsText]);

  const rows = symbols.map((sym) => ({ sym, q: quotes[sym] || null }));

  const renderChange = (q: Quote | null) => {
    if (!q) return '-';
    const pct = q.change_percent ?? 0;
    const color = pct >= 0 ? '#4caf50' : '#f44336';
    const Icon = pct >= 0 ? TrendingUp : TrendingDown;
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color }}>
        <Icon fontSize="small" />
        <span>{pct >= 0 ? '+' : ''}{pct.toFixed(2)}%</span>
      </Box>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
            Live Market Dashboard
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            Real-time quotes from orchestrated providers
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Tooltip title="Refresh now">
            <span>
              <IconButton color="primary" disabled={loading} onClick={fetchQuotes}>
                <Refresh />
              </IconButton>
            </span>
          </Tooltip>
          <Chip label={lastUpdated ? `Updated ${lastUpdated}` : 'Connecting...'} size="small" />
        </Box>
      </Box>

      {/* Controls */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={8}>
              <TextField
                fullWidth
                label="Symbols (comma-separated)"
                value={symbolsText}
                onChange={(e) => setSymbolsText(e.target.value)}
                placeholder="AAPL,SPY,QQQ,TSLA,NVDA,AMD,GOOGL,MSFT"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button variant="contained" fullWidth onClick={fetchQuotes} disabled={loading}>
                {loading ? 'Refreshing…' : 'Refresh Now'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {loading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
        </Box>
      )}

      {/* Quotes table */}
      <Card>
        <CardContent>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Symbol</TableCell>
                  <TableCell align="right">Price</TableCell>
                  <TableCell align="right">Change</TableCell>
                  <TableCell align="right">Volume</TableCell>
                  <TableCell align="right">Source</TableCell>
                  <TableCell align="right">Time</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map(({ sym, q }) => (
                  <TableRow key={sym} hover>
                    <TableCell sx={{ fontWeight: 700 }}>{sym}</TableCell>
                    <TableCell align="right">
                      {q ? q.price?.toFixed(2) : '-'}
                    </TableCell>
                    <TableCell align="right">{renderChange(q)}</TableCell>
                    <TableCell align="right">{q?.volume ? q.volume.toLocaleString() : '-'}</TableCell>
                    <TableCell align="right">{q?.source || '-'}</TableCell>
                    <TableCell align="right">{q?.timestamp ? new Date(q.timestamp).toLocaleTimeString() : '-'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LiveMarketDashboard;

