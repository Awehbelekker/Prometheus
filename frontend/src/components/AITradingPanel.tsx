import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Stack,
  Grid,
  LinearProgress,
  alpha,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Fade,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Assessment,
  Security,
  Refresh,
  AutoAwesome,
  SmartToy,
  Timeline,
  Speed,
  CheckCircle,
  Warning,
  Error as ErrorIcon
} from '@mui/icons-material';
import { aiTradingService, useAITrading } from '../services/AITradingService';

interface AITradingPanelProps {
  defaultSymbol?: string;
  onAnalysisUpdate?: (analysis: any) => void;
}

const AITradingPanel: React.FC<AITradingPanelProps> = ({ 
  defaultSymbol = 'AAPL', 
  onAnalysisUpdate 
}) => {
  const [selectedSymbol, setSelectedSymbol] = useState(defaultSymbol);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [serviceHealth, setServiceHealth] = useState<any>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const { analyzeSymbol, generateTradingStrategy, isLoading, error, isServiceAvailable } = useAITrading();

  // Popular symbols for quick selection
  const popularSymbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'BTC-USD', 'ETH-USD', 'SPY'];

  useEffect(() => {
    // Check service health on mount
    checkServiceHealth();
    // Auto-analyze default symbol
    if (isServiceAvailable) {
      handleAnalyzeSymbol();
    }
  }, []);

  const checkServiceHealth = async () => {
    const health = await aiTradingService.getServiceHealth();
    setServiceHealth(health);
  };

  const handleAnalyzeSymbol = async () => {
    if (!selectedSymbol) return;

    const result = await analyzeSymbol(selectedSymbol);
    if (result) {
      setAiAnalysis(result);
      setLastUpdate(new Date());
      onAnalysisUpdate?.(result);
    }
  };

  const handleGenerateStrategy = async () => {
    if (!selectedSymbol) return;

    const mockMarketData = {
      current_price: 150.0 + Math.random() * 100,
      volume: 1000000 + Math.random() * 500000,
      change_percent: (Math.random() - 0.5) * 10,
      volatility: 0.15 + Math.random() * 0.2,
      market_cap: 1000000000 + Math.random() * 1000000000
    };

    const strategy = await generateTradingStrategy(selectedSymbol, mockMarketData);
    if (strategy) {
      setAiAnalysis((prev: any) => ({ ...prev, strategy }));
      setLastUpdate(new Date());
    }
  };

  const getServiceStatusColor = () => {
    if (!serviceHealth) return '#666';
    if (serviceHealth.ai_trading_service === 'healthy') return '#4caf50';
    if (serviceHealth.ai_trading_service === 'degraded') return '#ff9800';
    return '#f44336';
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment?.toLowerCase()) {
      case 'bullish': return '#4caf50';
      case 'bearish': return '#f44336';
      case 'neutral': return '#ff9800';
      default: return '#666';
    }
  };

  return (
    <Paper sx={{
      p: 3,
      background: 'linear-gradient(135deg, rgba(138, 43, 226, 0.1) 0%, rgba(75, 0, 130, 0.05) 100%)',
      border: '2px solid rgba(138, 43, 226, 0.3)',
      borderRadius: 4,
      boxShadow: '0 8px 32px rgba(138, 43, 226, 0.2)',
      position: 'relative',
      overflow: 'hidden',
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: 'linear-gradient(90deg, #8a2be2, #4b0082, #9400d3, #8a2be2)',
        backgroundSize: '200% 100%',
        animation: 'gradientShift 3s ease-in-out infinite'
      }
    }}>
      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 3 }}>
        <SmartToy sx={{ color: '#8a2be2', fontSize: 32 }} />
        <Typography variant="h4" sx={{
          fontWeight: 800,
          background: 'linear-gradient(45deg, #8a2be2, #9400d3)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '0.5px'
        }}>
          🤖 AI TRADING ANALYSIS
        </Typography>
        
        {/* Service Status */}
        <Chip
          icon={serviceHealth?.ai_trading_service === 'healthy' ? <CheckCircle /> : <Warning />}
          label={serviceHealth?.ai_trading_service === 'healthy' ? 'AI ONLINE' : 'AI OFFLINE'}
          sx={{
            backgroundColor: getServiceStatusColor(),
            color: 'white',
            fontWeight: 700,
            animation: serviceHealth?.ai_trading_service === 'healthy' ? 'pulse 2s infinite' : 'none'
          }}
        />
      </Stack>

      {/* Symbol Selection */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <FormControl fullWidth>
            <InputLabel>Select Symbol</InputLabel>
            <Select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              label="Select Symbol"
              sx={{
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#8a2be2'
                }
              }}
            >
              {popularSymbols.map(symbol => (
                <MenuItem key={symbol} value={symbol}>{symbol}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Stack direction="row" spacing={2} sx={{ height: '100%', alignItems: 'center' }}>
            <Button
              variant="contained"
              onClick={handleAnalyzeSymbol}
              disabled={isLoading || !isServiceAvailable}
              startIcon={isLoading ? <CircularProgress size={20} /> : <Psychology />}
              sx={{
                background: 'linear-gradient(45deg, #8a2be2, #9400d3)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #9400d3, #8a2be2)'
                }
              }}
            >
              Analyze
            </Button>
            
            <Button
              variant="outlined"
              onClick={handleGenerateStrategy}
              disabled={isLoading || !isServiceAvailable}
              startIcon={<AutoAwesome />}
              sx={{
                borderColor: '#8a2be2',
                color: '#8a2be2',
                '&:hover': {
                  borderColor: '#9400d3',
                  backgroundColor: alpha('#8a2be2', 0.1)
                }
              }}
            >
              Strategy
            </Button>
            
            <IconButton
              onClick={checkServiceHealth}
              sx={{ color: '#8a2be2' }}
            >
              <Refresh />
            </IconButton>
          </Stack>
        </Grid>
      </Grid>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          AI Analysis Error: {error}
        </Alert>
      )}

      {/* Loading State */}
      {isLoading && (
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <CircularProgress sx={{ color: '#8a2be2', mb: 2 }} />
          <Typography variant="body2" sx={{ color: '#8a2be2' }}>
            AI is analyzing {selectedSymbol}...
          </Typography>
        </Box>
      )}

      {/* AI Analysis Results */}
      {aiAnalysis && (
        <Fade in={!!aiAnalysis}>
          <Grid container spacing={3}>
            {/* Sentiment Analysis */}
            {aiAnalysis.sentiment && (
              <Grid item xs={12} md={6}>
                <Card sx={{
                  background: `linear-gradient(135deg, ${alpha(getSentimentColor(aiAnalysis.sentiment.data.sentiment), 0.1)} 0%, ${alpha(getSentimentColor(aiAnalysis.sentiment.data.sentiment), 0.05)} 100%)`,
                  border: `1px solid ${alpha(getSentimentColor(aiAnalysis.sentiment.data.sentiment), 0.3)}`
                }}>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <Psychology sx={{ color: getSentimentColor(aiAnalysis.sentiment.data.sentiment) }} />
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        Market Sentiment
                      </Typography>
                      <Chip
                        label={aiAnalysis.sentiment.data.sentiment?.toUpperCase()}
                        sx={{
                          backgroundColor: getSentimentColor(aiAnalysis.sentiment.data.sentiment),
                          color: 'white',
                          fontWeight: 700
                        }}
                      />
                    </Stack>
                    
                    <Typography variant="body2" sx={{ mb: 2, color: '#aaa' }}>
                      {aiAnalysis.sentiment.data.reasoning}
                    </Typography>
                    
                    <LinearProgress
                      variant="determinate"
                      value={aiAnalysis.sentiment.data.confidence * 100}
                      sx={{
                        height: 8,
                        borderRadius: 4,
                        backgroundColor: alpha('#333', 0.3),
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: getSentimentColor(aiAnalysis.sentiment.data.sentiment),
                          borderRadius: 4
                        }
                      }}
                    />
                    <Typography variant="caption" sx={{ color: '#aaa', mt: 1, display: 'block' }}>
                      Confidence: {(aiAnalysis.sentiment.data.confidence * 100).toFixed(1)}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Model Status */}
            {aiAnalysis.modelStatus && (
              <Grid item xs={12} md={6}>
                <Card sx={{
                  background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 212, 255, 0.05) 100%)',
                  border: '1px solid rgba(0, 212, 255, 0.3)'
                }}>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <Speed sx={{ color: '#00d4ff' }} />
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        AI Models Status
                      </Typography>
                    </Stack>
                    
                    {aiAnalysis.modelStatus.models && Object.entries(aiAnalysis.modelStatus.models).map(([model, info]: [string, any]) => (
                      <Stack key={model} direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                        <Typography variant="body2">
                          {model.toUpperCase()}
                        </Typography>
                        <Chip
                          size="small"
                          label={info.available ? 'READY' : 'OFFLINE'}
                          sx={{
                            backgroundColor: info.available ? '#4caf50' : '#f44336',
                            color: 'white',
                            fontSize: '0.7rem'
                          }}
                        />
                      </Stack>
                    ))}
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Trading Strategy */}
            {aiAnalysis.strategy && (
              <Grid item xs={12}>
                <Card sx={{
                  background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%)',
                  border: '1px solid rgba(255, 152, 0, 0.3)'
                }}>
                  <CardContent>
                    <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2 }}>
                      <Timeline sx={{ color: '#ff9800' }} />
                      <Typography variant="h6" sx={{ fontWeight: 700 }}>
                        AI Trading Strategy
                      </Typography>
                      <Chip
                        label={aiAnalysis.strategy.data.action}
                        sx={{
                          backgroundColor: aiAnalysis.strategy.data.action === 'BUY' ? '#4caf50' :
                                          aiAnalysis.strategy.data.action === 'SELL' ? '#f44336' : '#ff9800',
                          color: 'white',
                          fontWeight: 700
                        }}
                      />
                    </Stack>
                    
                    <Typography variant="body2" sx={{ mb: 2, color: '#aaa' }}>
                      {aiAnalysis.strategy.data.reasoning}
                    </Typography>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: '#aaa' }}>Risk Assessment</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700 }}>
                          {aiAnalysis.strategy.data.risk_assessment}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" sx={{ color: '#aaa' }}>Time Horizon</Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700 }}>
                          {aiAnalysis.strategy.data.time_horizon}
                        </Typography>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </Fade>
      )}

      {/* Last Update */}
      {lastUpdate && (
        <Typography variant="caption" sx={{ 
          color: '#aaa', 
          mt: 2, 
          display: 'block', 
          textAlign: 'center' 
        }}>
          Last updated: {lastUpdate.toLocaleTimeString()}
        </Typography>
      )}

      {/* CSS Animations */}
      <style>{`
        @keyframes gradientShift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </Paper>
  );
};

export default AITradingPanel;
