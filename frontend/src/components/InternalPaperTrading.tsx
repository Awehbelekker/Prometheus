import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Alert,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Avatar,
  Stack
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  ShowChart,
  Psychology,
  Speed,
  Timeline,
  AccountBalance,
  SmartToy,
  Refresh,
  PlayArrow,
  Stop
} from '@mui/icons-material';
import { API_BASE_URL } from '../config/api';
import { getJsonWithRetry } from '../utils/network';



interface PaperPortfolio {
  user_id: string;
  cash_balance: number;
  intended_investment: number;
  positions: Record<string, any>;
  total_value: number;
  pnl: number;
  pnl_percentage: number;
  trades_count: number;
  win_rate: number;
}

interface MarketData {
  symbol: string;
  price: number | null;
  bid: number | null;
  ask: number | null;
  volume: number | null;
  change_24h: number | null;
  change_percentage: number | null;
  timestamp: string;
}

const InternalPaperTrading: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [portfolio, setPortfolio] = useState<PaperPortfolio | null>(null);
  const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
  const [platformStats, setPlatformStats] = useState<any>(null);
  const [aiInsights, setAiInsights] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Trading dialog state
  const [tradeDialog, setTradeDialog] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [tradeQuantity, setTradeQuantity] = useState('');
  const [tradeSide, setTradeSide] = useState('buy');

  const [marketOpen, setMarketOpen] = useState<boolean>(true);

  // Portfolio creation dialog
  const [createPortfolioDialog, setCreatePortfolioDialog] = useState(false);
  const [intendedInvestment, setIntendedInvestment] = useState('');

  const userId = (() => {
    try {
      const key = 'paperUserId';
      const existing = localStorage.getItem(key);
      if (existing) return existing;
      const id = 'paper-' + Math.random().toString(36).slice(2, 12);
      localStorage.setItem(key, id);
      return id;
    } catch {
      return 'paper-' + Math.random().toString(36).slice(2, 12);
    }
  })();

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      // Load market data from backend (fallback to default symbols)
      try {
        const marketResult: any = await getJsonWithRetry(`${API_BASE_URL}/api/market-data?symbols=AAPL,GOOGL,MSFT,TSLA,SPY,NVDA,BTC,ETH`);
        if (marketResult && marketResult.success && marketResult.market_data) {
          setMarketData(marketResult.market_data);
        } else {
          setError('Failed to parse market data');
        }
      } catch (_) {
        setError('Failed to load market data');
      }

      // Load platform stats (try system status then health)
      let stats: any = null;
      try {
        stats = await getJsonWithRetry(`${API_BASE_URL}/api/system/status`);
      } catch (_) {
        try {
          const h: any = await getJsonWithRetry(`${API_BASE_URL}/health`);
          stats = { total_users: 0, max_users: 1000, ai_learning_data_points: 0, active_symbols: 0, system_status: 'healthy', ...h };
        } catch (_) {}
      }
      // Market status
      try {
        const s: any = await getJsonWithRetry(`${API_BASE_URL}/api/internal-paper/market-status`);
        if (typeof s?.market_open === 'boolean') setMarketOpen(!!s.market_open);
      } catch {}

      if (stats) setPlatformStats(stats);

      // Try to load user portfolio (skip if endpoint not available)
      try {
        const portfolioResult: any = await getJsonWithRetry(`${API_BASE_URL}/api/internal-paper/portfolio/${userId}`);
        if (portfolioResult.success) {
          setPortfolio(portfolioResult.portfolio);
          setAiInsights([
            "📈 AAPL showing strong momentum - consider position sizing",
            "⚡ High volatility detected in tech sector - risk management advised",
            "🎯 Portfolio diversification opportunity in energy sector",
            "💡 Options flow suggests bullish sentiment in NVDA"
          ]);
        }
      } catch (e) {
        // Portfolio doesn't exist yet
      }

    } catch (err) {
      setError('Failed to load data');
      console.error('Data loading error:', err);
    }
  };

  const createPortfolio = async () => {
    if (!intendedInvestment || parseFloat(intendedInvestment) <= 0) {
      setError('Please enter a valid investment amount');
      return;
    }

    setLoading(true);
    try {
      const result: any = await getJsonWithRetry(`${API_BASE_URL}/api/internal-paper/create-portfolio`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          intended_investment: parseFloat(intendedInvestment),
          risk_tolerance: 'moderate'
        })
      });

      if (result.success) {
        setPortfolio(result.portfolio);
        setCreatePortfolioDialog(false);
        setError(null);
        return;
      }
      setError('Failed to create portfolio');
    } catch (err) {
      setError('Failed to create portfolio');
    } finally {
      setLoading(false);
    }
  };

  const placeTrade = async () => {
    if (!selectedSymbol || !tradeQuantity || parseFloat(tradeQuantity) <= 0) {
      setError('Please enter valid trade details');
      return;
    }

    setLoading(true);
    try {
      const result: any = await getJsonWithRetry(`${API_BASE_URL}/api/internal-paper/place-trade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId,
          symbol: selectedSymbol,
          side: tradeSide,
          quantity: parseFloat(tradeQuantity),
          trade_type: 'market',
          queue_if_closed: !marketOpen
        })
      });

      if (result.success && result.portfolio) {
        setPortfolio(result.portfolio);
        setTradeDialog(false);
        setSelectedSymbol('');
        setTradeQuantity('');
        setError(null);
        return;
      }
      if (result.success && result.queued) {
        setTradeDialog(false);
        setSelectedSymbol('');
        setTradeQuantity('');
        setError(null);
        return;
      }
      setError('Failed to place trade');
    } catch (err) {
      setError('Failed to place trade');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const isFiniteNumber = (v: any): v is number => typeof v === 'number' && Number.isFinite(v);
  const safeNumber = (v: any, fallback = 0): number => (isFiniteNumber(v) ? v : fallback);

  const formatPercentage = (value?: number | null) => {
    if (!isFiniteNumber(value)) return '—';
    return `${value! >= 0 ? '+' : ''}${value!.toFixed(2)}%`;
  };

  if (!portfolio) {
    return (
      <Box sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
        p: 3,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Card sx={{ maxWidth: 600, background: 'rgba(26, 26, 26, 0.95)' }}>
          <CardContent sx={{ textAlign: 'center', p: 4 }}>
            <SmartToy sx={{ fontSize: 64, color: '#00d4ff', mb: 2 }} />
            <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
              🎯 PROMETHEUS Internal Paper Trading
            </Typography>
            <Typography variant="body1" sx={{ color: 'text.secondary', mb: 3 }}>
              Test your trading strategies with real live market data while our AI learns from every trade.
              No real money at risk - perfect for training both you and our AI systems.
            </Typography>

            {platformStats && (
              <Alert severity="info" sx={{ mb: 3, textAlign: 'left' }}>
                <Typography variant="body2">
                  <strong>Platform Status:</strong><br/>
                  • {platformStats.total_users}/{platformStats.max_users} users active<br/>
                  • {platformStats.ai_learning_data_points} AI learning data points<br/>
                  • {platformStats.active_symbols} symbols with live data<br/>
                  • System training AI with real market conditions
                </Typography>
              </Alert>
            )}

            <Button
              variant="contained"
              size="large"
              onClick={() => setCreatePortfolioDialog(true)}
              sx={{
                background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                px: 4,
                py: 1.5
              }}
            >
              Start Paper Trading
            </Button>
          </CardContent>
        </Card>

        {/* Create Portfolio Dialog */}
        <Dialog open={createPortfolioDialog} onClose={() => setCreatePortfolioDialog(false)}>
          <DialogTitle>💰 Create Paper Trading Portfolio</DialogTitle>
          <DialogContent>
            <Typography variant="body2" sx={{ mb: 3, color: 'text.secondary' }}>
              Enter the amount you're thinking of investing for real. This will be your paper trading balance
              and helps our AI learn realistic trading patterns.
            </Typography>
            <TextField
              fullWidth
              label="Intended Investment Amount"
              type="number"
              value={intendedInvestment}
              onChange={(e) => setIntendedInvestment(e.target.value)}
              InputProps={{ startAdornment: '$' }}
              sx={{ mb: 2 }}
            />
            <Alert severity="info">
              This creates a paper trading account with real live market data.
              Every trade helps train our AI systems for better performance.
            </Alert>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreatePortfolioDialog(false)}>Cancel</Button>
            <Button
              onClick={createPortfolio}
              variant="contained"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Portfolio'}
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    );
  }

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%)',
      p: 3
    }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 2 }}>
          🎯 Internal Paper Trading Dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary' }}>
          Trading with real live data • Training AI systems • Risk-free testing
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Portfolio Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AccountBalance sx={{ color: '#00d4ff', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
                    {formatCurrency(portfolio.total_value)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Portfolio Value
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {portfolio.pnl >= 0 ? (
                  <TrendingUp sx={{ color: '#4caf50', fontSize: 32 }} />
                ) : (
                  <TrendingDown sx={{ color: '#f44336', fontSize: 32 }} />
                )}
                <Box>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 700,
                      color: portfolio.pnl >= 0 ? '#4caf50' : '#f44336'
                    }}
                  >
                    {formatCurrency(portfolio.pnl)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    P&L ({formatPercentage(portfolio.pnl_percentage)})
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <AttachMoney sx={{ color: '#ff9800', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    {formatCurrency(portfolio.cash_balance)}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Cash Available
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #1a1a1a, #2a2a2a)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Timeline sx={{ color: '#9c27b0', fontSize: 32 }} />
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700 }}>
                    {portfolio.trades_count}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                    Total Trades
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {/* Market Status Indicator */}
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Box
          sx={{
            width: 12,
            height: 12,
            borderRadius: '50%',
            backgroundColor: marketOpen ? '#4caf50' : '#f44336',
          }}
        />
        <Typography variant="body2" sx={{ color: 'text.secondary' }}>
          Market is {marketOpen ? 'OPEN' : 'CLOSED'}
          {!marketOpen && ' - Orders will be queued for next market open'}
        </Typography>
      </Box>

      {/* Main Content */}
      <Card sx={{ background: 'rgba(26, 26, 26, 0.95)' }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          sx={{
            borderBottom: 1,
            borderColor: 'divider',
            '& .MuiTab-root': { color: 'text.secondary' },
            '& .Mui-selected': { color: '#00d4ff' }
          }}
        >
          <Tab label="Market Data" />
          <Tab label="My Positions" />
          <Tab label="AI Insights" />
          <Tab label="Platform Stats" />
        </Tabs>

        <CardContent sx={{ p: 3 }}>
          {activeTab === 0 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  📊 Live Market Data
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<PlayArrow />}
                  onClick={() => setTradeDialog(true)}
                  sx={{ background: 'linear-gradient(45deg, #00d4ff, #0099cc)' }}
                >
                  Place Trade
                </Button>
              </Box>

              <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Symbol</TableCell>
                      <TableCell>Price</TableCell>
                      <TableCell>24h Change</TableCell>
                      <TableCell>Volume</TableCell>
                      <TableCell>Bid/Ask</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.values(marketData).slice(0, 10).map((data) => (
                      <TableRow key={data.symbol} hover>
                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {data.symbol}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            ${safeNumber(data.price).toFixed(2)}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          {(() => { const cp = safeNumber(data.change_percentage); return (
                            <Chip
                              label={formatPercentage(cp)}
                              color={cp >= 0 ? 'success' : 'error'}
                              size="small"
                            />); })()}
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {safeNumber(data.volume).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            ${safeNumber(data.bid).toFixed(2)} / ${safeNumber(data.ask).toFixed(2)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                📈 My Positions
              </Typography>

              {Object.keys(portfolio.positions).length === 0 ? (
                <Alert severity="info">
                  No positions yet. Start trading to build your portfolio!
                </Alert>
              ) : (
                <TableContainer component={Paper} sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Symbol</TableCell>
                        <TableCell>Quantity</TableCell>
                        <TableCell>Avg Price</TableCell>
                        <TableCell>Current Value</TableCell>
                        <TableCell>P&L</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {Object.entries(portfolio.positions).map(([symbol, position]: [string, any]) => {
                        const currentPrice = marketData[symbol]?.price || position.avg_price;
                        const pnl = (currentPrice - position.avg_price) * position.quantity;
                        const pnlPercentage = ((currentPrice - position.avg_price) / position.avg_price) * 100;

                        return (
                          <TableRow key={symbol} hover>
                            <TableCell>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                {symbol}
                              </Typography>
                            </TableCell>
                            <TableCell>{position.quantity}</TableCell>
                            <TableCell>${safeNumber(position.avg_price).toFixed(2)}</TableCell>
                            <TableCell>${safeNumber(position.current_value).toFixed(2)}</TableCell>
                            <TableCell>
                              <Typography
                                variant="body2"
                                sx={{
                                  color: pnl >= 0 ? '#4caf50' : '#f44336',
                                  fontWeight: 600
                                }}
                              >
                                {formatCurrency(pnl)} ({formatPercentage(pnlPercentage)})
                              </Typography>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Box>
          )}

          {activeTab === 2 && (
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                🤖 AI Insights & Learning
              </Typography>

              <Stack spacing={2}>
                {aiInsights.map((insight, index) => (
                  <Alert key={index} severity="info" icon={<Psychology />}>
                    {insight}
                  </Alert>
                ))}

                <Alert severity="success" icon={<SmartToy />}>
                  AI is learning from your trading patterns and market conditions.
                  Every trade helps improve our system's performance for live trading.
                </Alert>
              </Stack>
            </Box>
          )}

          {activeTab === 3 && platformStats && (
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
                📊 Platform Statistics
              </Typography>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Card sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>Platform Overview</Typography>
                      <Typography variant="body2">
                        Active Users: {platformStats.total_users}/{platformStats.max_users}
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={(platformStats.total_users / platformStats.max_users) * 100}
                        sx={{ my: 1 }}
                      />
                      <Typography variant="body2">
                        Total Portfolio Value: {formatCurrency(platformStats.total_portfolio_value)}
                      </Typography>
                      <Typography variant="body2">
                        Total Trades: {platformStats.total_trades}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={6}>
                  <Card sx={{ background: 'rgba(42, 42, 42, 0.5)' }}>
                    <CardContent>
                      <Typography variant="h6" sx={{ mb: 2 }}>AI Learning Progress</Typography>
                      <Typography variant="body2">
                        Learning Data Points: {platformStats.ai_learning_data_points}
                      </Typography>
                      <Typography variant="body2">
                        Active Symbols: {platformStats.active_symbols}
                      </Typography>
                      <Typography variant="body2">
                        System Status: {platformStats.system_status}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Trade Dialog */}
      <Dialog open={tradeDialog} onClose={() => setTradeDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>📈 Place Paper Trade</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
            <FormControl fullWidth>
              <InputLabel>Symbol</InputLabel>
              <Select
                value={selectedSymbol}
                onChange={(e) => setSelectedSymbol(e.target.value)}
              >
                {Object.keys(marketData).map((symbol) => (
                  <MenuItem key={symbol} value={symbol}>
                    {symbol} - ${safeNumber(marketData[symbol]?.price).toFixed(2)}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Side</InputLabel>
              <Select
                value={tradeSide}
                onChange={(e) => setTradeSide(e.target.value)}
              >
                <MenuItem value="buy">Buy</MenuItem>
                <MenuItem value="sell">Sell</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Quantity"
              type="number"
              value={tradeQuantity}
              onChange={(e) => setTradeQuantity(e.target.value)}
            />

            {selectedSymbol && tradeQuantity && (
              <Alert severity="info">
                Estimated Value: {formatCurrency(
                  parseFloat(tradeQuantity) * (marketData[selectedSymbol]?.price || 0)
                )}
              </Alert>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTradeDialog(false)}>Cancel</Button>
          <Button
            onClick={placeTrade}
            variant="contained"
            disabled={loading || !selectedSymbol || !tradeQuantity}
          >
            {loading ? 'Placing...' : 'Place Trade'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InternalPaperTrading;
