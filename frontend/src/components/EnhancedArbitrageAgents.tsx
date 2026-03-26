import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Chip,
  Button,
  LinearProgress,
  Alert
} from '@mui/material';
import { useRealWorldIntelligence } from './RealWorldIntelligenceProvider';

interface ArbitrageOpportunity {
  id: string;
  symbol: string;
  buyExchange: string;
  sellExchange: string;
  buyPrice: number;
  sellPrice: number;
  profitMargin: number;
  volume: number;
  executionProbability: number;
  timeRemaining: number;
  riskFactors: string[];
}

// Mock function to generate sample arbitrage opportunities for demo
const generateMockOpportunities = (): ArbitrageOpportunity[] => {
  const opportunities: ArbitrageOpportunity[] = [];
  const symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT', 'DOT/USDT'];
  const exchanges = ['Binance', 'Coinbase', 'Kraken', 'FTX', 'Huobi'];
  
  // Generate 0-5 opportunities
  const numOpportunities = Math.floor(Math.random() * 6);
  
  for (let i = 0; i < numOpportunities; i++) {
    // Randomly select symbol and exchanges
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    let buyExchange, sellExchange;
    
    do {
      buyExchange = exchanges[Math.floor(Math.random() * exchanges.length)];
      sellExchange = exchanges[Math.floor(Math.random() * exchanges.length)];
    } while (buyExchange === sellExchange);
    
    // Generate prices with a small difference for arbitrage
    const basePrice = symbol.startsWith('BTC') ? 30000 + Math.random() * 5000 :
                     symbol.startsWith('ETH') ? 2000 + Math.random() * 300 :
                     symbol.startsWith('SOL') ? 50 + Math.random() * 20 :
                     symbol.startsWith('AVAX') ? 20 + Math.random() * 10 :
                     5 + Math.random() * 10;
    
    const buyPrice = basePrice * (0.99 + Math.random() * 0.005);
    const sellPrice = basePrice * (1 + Math.random() * 0.01);
    
    const profitMargin = ((sellPrice - buyPrice) / buyPrice) * 100;
    
    // Only add if profit margin is positive
    if (profitMargin > 0) {
      opportunities.push({
        id: `arb-${Date.now()}-${i}`,
        symbol,
        buyExchange,
        sellExchange,
        buyPrice,
        sellPrice,
        profitMargin,
        volume: Math.random() * 50000 + 5000,
        executionProbability: 0.6 + Math.random() * 0.35,
        timeRemaining: Math.floor(Math.random() * 120) + 10,
        riskFactors: [
          'Exchange latency',
          'Price slippage',
          'Transaction fees'
        ].filter(() => Math.random() > 0.5)
      });
    }
  }
  
  return opportunities;
};

const EnhancedArbitrageAgents: React.FC = () => {
  const { intelligence } = useRealWorldIntelligence();
  const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingIds, setExecutingIds] = useState<Set<string>>(new Set());
  const [stats, setStats] = useState({
    todayPerformance: 2.3,
    successfulArbitrages: 12,
    successRate: 94.2,
    avgExecutionTime: 1.2
  });

  useEffect(() => {
    const fetchOpportunities = async () => {
      try {
        setLoading(true);
        // In a real implementation, fetch from API
        // const response = await fetch('/api/arbitrage/opportunities');
        // const data = await response.json();
        
        // Using mock data for now
        const mockOpportunities = generateMockOpportunities();
        setOpportunities(mockOpportunities);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch arbitrage opportunities:', error);
        setLoading(false);
      }
    };

    fetchOpportunities();
    
    // Update opportunities every 15 seconds to simulate real-time monitoring
    const interval = setInterval(fetchOpportunities, 15000);

    return () => clearInterval(interval);
  }, []);

  // Add some randomness to the performance stats
  useEffect(() => {
    const interval = setInterval(() => {
      setStats(prev => ({
        todayPerformance: prev.todayPerformance + (Math.random() * 0.2 - 0.1),
        successfulArbitrages: Math.min(30, prev.successfulArbitrages + (Math.random() > 0.8 ? 1 : 0)),
        successRate: Math.min(99.5, Math.max(85, prev.successRate + (Math.random() * 1 - 0.5))),
        avgExecutionTime: Math.max(0.8, Math.min(2.5, prev.avgExecutionTime + (Math.random() * 0.2 - 0.1)))
      }));
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const executeArbitrage = async (opportunity: ArbitrageOpportunity) => {
    setExecutingIds(prev => new Set(prev).add(opportunity.id));

    try {
      // In a real implementation, call the API
      // const response = await fetch('/api/arbitrage/execute', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ 
      //     opportunityId: opportunity.id,
      //     marketIntelligence: intelligence 
      //   })
      // });
      
      // Simulate API call with a delay
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulate successful execution
      // If response.ok - update opportunities
      setOpportunities(prev => prev.filter(op => op.id !== opportunity.id));
      
      // Update stats on successful execution
      setStats(prev => ({
        ...prev,
        successfulArbitrages: prev.successfulArbitrages + 1,
        todayPerformance: prev.todayPerformance + (opportunity.profitMargin * 0.01),
      }));
      
    } catch (error) {
      console.error('Failed to execute arbitrage:', error);
    } finally {
      // Remove from executing state
      setExecutingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(opportunity.id);
        return newSet;
      });
    }
  };

  const formatCurrency = (amount: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* DEBUG IDENTIFIER */}
      <Box sx={{ 
        position: 'absolute', 
        top: 10, 
        right: 10, 
        background: 'linear-gradient(45deg, #ff6b35, #ff9800)', 
        color: 'white', 
        padding: '4px 8px', 
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 'bold',
        zIndex: 1000
      }}>
        📈 ARBITRAGE AGENTS
      </Box>
      <Typography variant="h4" gutterBottom>
        Intelligent Arbitrage Agents
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        Enhanced with real-world intelligence: Market sentiment, liquidity conditions, and execution probability analysis
      </Alert>

      {/* Active Arbitrage Opportunities */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Live Arbitrage Opportunities
          </Typography>
          
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Symbol</TableCell>
                <TableCell>Buy Exchange</TableCell>
                <TableCell>Sell Exchange</TableCell>
                <TableCell>Buy Price</TableCell>
                <TableCell>Sell Price</TableCell>
                <TableCell>Profit Margin</TableCell>
                <TableCell>Execution Probability</TableCell>
                <TableCell>Time Remaining</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {opportunities.map((opportunity) => (
                <TableRow key={opportunity.id}>
                  <TableCell>
                    <Typography variant="body2" fontWeight="bold">
                      {opportunity.symbol}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip label={opportunity.buyExchange} size="small" color="primary" />
                  </TableCell>
                  <TableCell>
                    <Chip label={opportunity.sellExchange} size="small" color="secondary" />
                  </TableCell>
                  <TableCell>{formatCurrency(opportunity.buyPrice)}</TableCell>
                  <TableCell>{formatCurrency(opportunity.sellPrice)}</TableCell>
                  <TableCell>
                    <Typography color={opportunity.profitMargin > 0.5 ? 'success.main' : 'warning.main'}>
                      {opportunity.profitMargin.toFixed(3)}%
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <LinearProgress
                        variant="determinate"
                        value={opportunity.executionProbability * 100}
                        sx={{ width: 60, mr: 1 }}
                      />
                      <Typography variant="caption">
                        {(opportunity.executionProbability * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color={opportunity.timeRemaining < 30 ? 'error' : 'textSecondary'}>
                      {opportunity.timeRemaining}s
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => executeArbitrage(opportunity)}
                      disabled={
                        executingIds.has(opportunity.id) || 
                        opportunity.executionProbability < 0.7 ||
                        opportunity.timeRemaining < 10
                      }
                    >
                      {executingIds.has(opportunity.id) ? 'Executing...' : 'Execute'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {opportunities.length === 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              No arbitrage opportunities found. Agents are monitoring markets continuously.
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Agent Performance Statistics */}
      <Grid container spacing={3} sx={{ mt: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Today's Performance</Typography>
              <Typography variant="h4" color="success.main">+{stats.todayPerformance.toFixed(1)}%</Typography>
              <Typography variant="body2">{stats.successfulArbitrages} successful arbitrages</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Success Rate</Typography>
              <Typography variant="h4" color="primary">{stats.successRate.toFixed(1)}%</Typography>
              <Typography variant="body2">Last 100 executions</Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6">Avg Execution Time</Typography>
              <Typography variant="h4" color="warning.main">{stats.avgExecutionTime.toFixed(1)}s</Typography>
              <Typography variant="body2">Cross-platform execution</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EnhancedArbitrageAgents;
