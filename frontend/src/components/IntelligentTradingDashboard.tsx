import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Chip, 
  LinearProgress,
  Alert,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow
} from '@mui/material';
import { useRealWorldIntelligence } from './RealWorldIntelligenceProvider';

interface TradingOpportunity {
  id: string;
  type: 'arbitrage' | 'trend' | 'sentiment' | 'event-driven';
  symbol: string;
  confidence: number;
  expectedReturn: number;
  riskLevel: 'low' | 'medium' | 'high';
  timeframe: string;
  description: string;
  reasoning: string[];
  platforms: string[];
}

interface PredictiveSignal {
  symbol: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  strength: number;
  timeframe: '5m' | '15m' | '1h' | '4h' | '1d';
  confidence: number;
  factors: string[];
}

// Helper function to generate mock opportunities
const generateMockOpportunities = (): TradingOpportunity[] => {
  const opportunities: TradingOpportunity[] = [];
  const symbols = ['BTC/USD', 'ETH/USD', 'AAPL', 'MSFT', 'TSLA', 'AMZN', 'SPY'];
  const types: TradingOpportunity['type'][] = ['arbitrage', 'trend', 'sentiment', 'event-driven'];
  const riskLevels: TradingOpportunity['riskLevel'][] = ['low', 'medium', 'high'];
  const timeframes = ['1h', '4h', '1d', '1w'];
  const platforms = ['Crypto Exchange', 'Stock Exchange', 'Both'];
  
  // Generate 1-5 opportunities
  const count = 1 + Math.floor(Math.random() * 5);
  
  for (let i = 0; i < count; i++) {
    const type = types[Math.floor(Math.random() * types.length)];
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const risk = riskLevels[Math.floor(Math.random() * riskLevels.length)];
    
    // Generate reasonable values based on type
    let confidence, expectedReturn, description, reasoning;
    
    switch (type) {
      case 'arbitrage':
        confidence = 0.7 + Math.random() * 0.25; // Higher confidence for arbitrage
        expectedReturn = (0.5 + Math.random() * 1.5) / 100; // 0.5%-2% returns
        description = `Price difference opportunity between exchanges for ${symbol}`;
        reasoning = ['Exchange price difference', 'Sufficient liquidity on both sides', 'Low transfer fee impact'];
        break;
      case 'trend':
        confidence = 0.6 + Math.random() * 0.3;
        expectedReturn = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 8) / 100; // 2%-10% returns
        description = `Strong ${expectedReturn > 0 ? 'upward' : 'downward'} trend detected in ${symbol}`;
        reasoning = ['Price action confirmation', 'Volume analysis', 'Technical indicator alignment'];
        break;
      case 'sentiment':
        confidence = 0.5 + Math.random() * 0.35;
        expectedReturn = (Math.random() > 0.4 ? 1 : -1) * (3 + Math.random() * 7) / 100; // 3%-10% returns
        description = `${expectedReturn > 0 ? 'Positive' : 'Negative'} sentiment shift detected for ${symbol}`;
        reasoning = ['Social media sentiment analysis', 'News coverage sentiment', 'Trading community interest'];
        break;
      case 'event-driven':
        confidence = 0.55 + Math.random() * 0.25;
        expectedReturn = (Math.random() > 0.5 ? 1 : -1) * (4 + Math.random() * 10) / 100; // 4%-14% returns
        description = `${symbol} ${expectedReturn > 0 ? 'favorable' : 'unfavorable'} reaction expected to upcoming event`;
        reasoning = ['Historical event response pattern', 'Pre-event positioning', 'Similar asset class reactions'];
        break;
      default:
        confidence = 0.6;
        expectedReturn = 0.05;
        description = `Trading opportunity in ${symbol}`;
        reasoning = ['Market analysis'];
    }
    
    opportunities.push({
      id: `opp-${Date.now()}-${i}`,
      type,
      symbol,
      confidence,
      expectedReturn,
      riskLevel: risk,
      timeframe: timeframes[Math.floor(Math.random() * timeframes.length)],
      description,
      reasoning,
      platforms: [platforms[Math.floor(Math.random() * platforms.length)]]
    });
  }
  
  return opportunities;
};

// Helper function to generate mock predictive signals
const generateMockSignals = (): PredictiveSignal[] => {
  const signals: PredictiveSignal[] = [];
  const symbols = ['BTC/USD', 'ETH/USD', 'SOL/USD', 'AAPL', 'MSFT', 'TSLA', 'NVDA', 'SPY', 'QQQ'];
  const directions: PredictiveSignal['direction'][] = ['bullish', 'bearish', 'neutral'];
  const timeframes: PredictiveSignal['timeframe'][] = ['5m', '15m', '1h', '4h', '1d'];
  
  // Generate 4-8 signals
  const count = 4 + Math.floor(Math.random() * 5);
  
  for (let i = 0; i < count; i++) {
    // Pick random values
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    const direction = directions[Math.floor(Math.random() * directions.length)];
    const timeframe = timeframes[Math.floor(Math.random() * timeframes.length)];
    
    // Generate appropriate factor list based on direction
    let factors: string[] = [];
    if (direction === 'bullish') {
      factors = [
        'Increasing volume',
        'Support level held',
        'Positive RSI divergence',
        'Golden cross formation',
        'Institutional buying'
      ].filter(() => Math.random() > 0.5);
    } else if (direction === 'bearish') {
      factors = [
        'Decreasing volume',
        'Resistance rejection',
        'Negative RSI divergence',
        'Death cross formation',
        'Institutional selling'
      ].filter(() => Math.random() > 0.5);
    } else {
      factors = [
        'Consolidation phase',
        'Low volatility',
        'Range-bound trading',
        'Balanced order book',
        'Neutral volume profile'
      ].filter(() => Math.random() > 0.5);
    }
    
    // Ensure there are at least 2 factors
    while (factors.length < 2) {
      factors.push('Technical analysis');
    }
    
    signals.push({
      symbol,
      direction,
      strength: 0.5 + Math.random() * 0.5, // 0.5-1.0
      timeframe,
      confidence: 0.6 + Math.random() * 0.35, // 0.6-0.95
      factors
    });
  }
  
  return signals;
};

const IntelligentTradingDashboard: React.FC = () => {
  const { intelligence, isLoading } = useRealWorldIntelligence();
  const [opportunities, setOpportunities] = useState<TradingOpportunity[]>([]);
  const [predictiveSignals, setPredictiveSignals] = useState<PredictiveSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingOpportunity, setExecutingOpportunity] = useState<string | null>(null);

  useEffect(() => {
    const generateIntelligentOpportunities = async () => {
      if (!intelligence) return;

      try {
        setLoading(true);
        
        // In a real implementation, call the API
        // const response = await fetch('/api/trading/intelligent-opportunities', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ intelligence })
        // });
        // const data = await response.json();
        
        // For now, generate mock data
        // Add a small delay to simulate API call
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const mockOpportunities = generateMockOpportunities();
        const mockSignals = generateMockSignals();
        
        setOpportunities(mockOpportunities);
        setPredictiveSignals(mockSignals);
        setLoading(false);
      } catch (error) {
        console.error('Failed to generate intelligent opportunities:', error);
        setLoading(false);
        
        // Use mock data as fallback
        setOpportunities(generateMockOpportunities());
        setPredictiveSignals(generateMockSignals());
      }
    };

    generateIntelligentOpportunities();
    
    // Refresh data every minute
    const interval = setInterval(generateIntelligentOpportunities, 60000);
    return () => clearInterval(interval);
  }, [intelligence]);

  const executeOpportunity = async (opportunity: TradingOpportunity) => {
    setExecutingOpportunity(opportunity.id);
    
    try {
      // In a real implementation, call the API
      // const response = await fetch('/api/trading/execute-opportunity', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ opportunityId: opportunity.id })
      // });

      // Simulate API call with delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // If successful, remove from opportunities list
      setOpportunities(prev => prev.filter(op => op.id !== opportunity.id));
    } catch (error) {
      console.error('Failed to execute opportunity:', error);
    } finally {
      setExecutingOpportunity(null);
    }
  };

  if (isLoading || loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Intelligent Trading Dashboard
      </Typography>

      {/* Market Intelligence Summary */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Market Sentiment</Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Typography variant="h4" color={
                  (intelligence?.sentiment?.overall || 0) > 0.2 ? 'success.main' :
                  (intelligence?.sentiment?.overall || 0) < -0.2 ? 'error.main' : 'warning.main'
                }>
                  {intelligence?.sentiment?.overall ? intelligence.sentiment.overall.toFixed(2) : '0.00'}
                </Typography>
                <Typography variant="body2" sx={{ ml: 1 }}>
                  {(intelligence?.sentiment?.overall || 0) > 0.2 ? 'Bullish' :
                   (intelligence?.sentiment?.overall || 0) < -0.2 ? 'Bearish' : 'Neutral'}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>              <Typography variant="h6">Fear & Greed</Typography>
              <Typography variant="h4" color={
                (intelligence?.crypto?.fearGreedIndex || 50) > 70 ? 'error.main' :
                (intelligence?.crypto?.fearGreedIndex || 50) < 30 ? 'success.main' : 'warning.main'
              }>
                {intelligence?.crypto?.fearGreedIndex || 50}
              </Typography>
              <Typography variant="body2">
                {(intelligence?.crypto?.fearGreedIndex || 50) > 70 ? 'Extreme Greed' :
                 (intelligence?.crypto?.fearGreedIndex || 50) < 30 ? 'Extreme Fear' : 'Neutral'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6">Active Opportunities</Typography>
              <Typography variant="h4" color="primary">
                {opportunities.length}
              </Typography>
              <Typography variant="body2">
                High-confidence trades
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>              <Typography variant="h6">Whale Activity</Typography>
              <Typography variant="h4" color={
                (intelligence?.crypto?.whaleMovements?.length || 0) > 5 ? 'warning.main' : 'success.main'
              }>
                {intelligence?.crypto?.whaleMovements?.length || 0}
              </Typography>
              <Typography variant="body2">
                Large movements detected
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Intelligent Trading Opportunities */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            AI-Generated Trading Opportunities
          </Typography>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Expected Return</TableCell>
                <TableCell>Confidence</TableCell>
                <TableCell>Risk</TableCell>
                <TableCell>Reasoning</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {opportunities.map((opportunity) => (
                <TableRow key={opportunity.id}>
                  <TableCell>{opportunity.symbol}</TableCell>
                  <TableCell>
                    <Chip label={opportunity.type} size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography color={opportunity.expectedReturn > 0 ? 'success.main' : 'error.main'}>
                      {(opportunity.expectedReturn * 100).toFixed(2)}%
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LinearProgress 
                        variant="determinate" 
                        value={opportunity.confidence * 100}
                        sx={{ width: 60, mr: 1 }}
                      />
                      <Typography variant="caption">
                        {(opportunity.confidence * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Chip 
                      label={opportunity.riskLevel} 
                      color={
                        opportunity.riskLevel === 'low' ? 'success' :
                        opportunity.riskLevel === 'medium' ? 'warning' : 'error'
                      }
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 200 }}>
                      {opportunity.description}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => executeOpportunity(opportunity)}
                      disabled={opportunity.confidence < 0.7 || executingOpportunity === opportunity.id}
                    >
                      {executingOpportunity === opportunity.id ? 'Executing...' : 'Execute'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {opportunities.length === 0 && (
                <TableRow>
                  <TableCell colSpan={7}>
                    <Alert severity="info" sx={{ m: 2 }}>
                      No trading opportunities found at this time. The system continuously evaluates market conditions.
                    </Alert>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Predictive Signals */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Predictive Market Signals
          </Typography>
          <Grid container spacing={2}>
            {predictiveSignals.map((signal, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Box sx={{ 
                  p: 2, 
                  border: 1, 
                  borderColor: 'divider', 
                  borderRadius: 1,
                  backgroundColor: signal.direction === 'bullish' ? '#e8f5e9' :
                                   signal.direction === 'bearish' ? '#ffebee' : '#f5f5f5'
                }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="h6">{signal.symbol}</Typography>
                    <Chip 
                      label={signal.direction}
                      color={
                        signal.direction === 'bullish' ? 'success' :
                        signal.direction === 'bearish' ? 'error' : 'default'
                      }
                    />
                  </Box>
                  <Typography variant="body2">
                    Strength: {(signal.strength * 100).toFixed(0)}% | 
                    Confidence: {(signal.confidence * 100).toFixed(0)}% | 
                    Timeframe: {signal.timeframe}
                  </Typography>
                  <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                    Factors: {signal.factors.join(', ')}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default IntelligentTradingDashboard;
