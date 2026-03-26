import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  AppBar,
  Toolbar,
  Button,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Divider,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Psychology,
  TrendingUp,
  Assessment,
  AutoAwesome,
  ExitToApp,
  School,
  Insights,
  Timeline,
  SmartToy,
  CheckCircle,
  Warning,
  Info
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Logo from './common/Logo';

interface AILearningDashboardProps {
  user: any;
  onLogout: () => void;
}

interface LearningMetric {
  name: string;
  value: number;
  trend: 'up' | 'down' | 'stable';
  description: string;
}

interface AIInsight {
  id: string;
  type: 'pattern' | 'recommendation' | 'warning' | 'achievement';
  title: string;
  description: string;
  confidence: number;
  timestamp: string;
}

const AILearningDashboard: React.FC<AILearningDashboardProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const [learningProgress, setLearningProgress] = useState<number>(67);
  const [aiConfidence, setAiConfidence] = useState<number>(84);
  const [tradingPatterns, setTradingPatterns] = useState<any>({});
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [metrics, setMetrics] = useState<LearningMetric[]>([]);

  useEffect(() => {
    // Simulate AI learning data
    const mockMetrics: LearningMetric[] = [
      {
        name: 'Pattern Recognition',
        value: 89,
        trend: 'up',
        description: 'AI ability to identify your trading patterns'
      },
      {
        name: 'Risk Assessment',
        value: 76,
        trend: 'up',
        description: 'Understanding of your risk tolerance'
      },
      {
        name: 'Market Timing',
        value: 82,
        trend: 'stable',
        description: 'Learning your preferred trading times'
      },
      {
        name: 'Sector Preference',
        value: 94,
        trend: 'up',
        description: 'Knowledge of your sector preferences'
      }
    ];
    setMetrics(mockMetrics);

    const mockInsights: AIInsight[] = [
      {
        id: '1',
        type: 'pattern',
        title: 'Morning Trading Pattern Detected',
        description: 'You tend to make your most profitable trades between 9:30-11:00 AM EST. Consider focusing your active trading during this window.',
        confidence: 92,
        timestamp: new Date().toISOString()
      },
      {
        id: '2',
        type: 'recommendation',
        title: 'Technology Sector Affinity',
        description: 'Your highest win rate (78%) comes from technology stocks. The AI recommends increasing allocation to FAANG+ stocks.',
        confidence: 85,
        timestamp: new Date().toISOString()
      },
      {
        id: '3',
        type: 'warning',
        title: 'Risk Tolerance Analysis',
        description: 'Recent trades show higher risk exposure than your historical comfort level. Consider position sizing adjustments.',
        confidence: 71,
        timestamp: new Date().toISOString()
      },
      {
        id: '4',
        type: 'achievement',
        title: 'Learning Milestone Reached',
        description: 'AI confidence in predicting your trading preferences has exceeded 80%. Recommendations will become more personalized.',
        confidence: 95,
        timestamp: new Date().toISOString()
      }
    ];
    setInsights(mockInsights);

    // Simulate trading patterns
    setTradingPatterns({
      preferredTradingTime: 'Market Open (9:30-11:00 AM)',
      averageHoldTime: '3.2 days',
      riskTolerance: 'Moderate-High',
      successfulSectors: ['Technology', 'Healthcare', 'Finance'],
      tradingStyle: 'Momentum Following',
      winRate: '68%',
      averageReturn: '2.3%',
      sharpeRatio: '1.42'
    });
  }, []);

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'pattern':
        return <Timeline color="primary" />;
      case 'recommendation':
        return <AutoAwesome color="secondary" />;
      case 'warning':
        return <Warning color="warning" />;
      case 'achievement':
        return <CheckCircle color="success" />;
      default:
        return <Info color="info" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'pattern':
        return 'primary';
      case 'recommendation':
        return 'secondary';
      case 'warning':
        return 'warning';
      case 'achievement':
        return 'success';
      default:
        return 'info';
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      {/* Navigation */}
      <AppBar position="sticky" sx={{ mb: 3 }}>
        <Toolbar>
          <Logo size="small" />
          <Typography variant="h6" sx={{ flexGrow: 1, ml: 2 }}>
            AI Learning Dashboard
          </Typography>
          <Button color="inherit" onClick={() => navigate('/dashboard')}>
            Dashboard
          </Button>
          <Button color="inherit" onClick={() => navigate('/trading')}>
            Trading
          </Button>
          <IconButton color="inherit" onClick={onLogout}>
            <ExitToApp />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl">
        {/* AI Learning Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Psychology sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>AI Learning Progress</Typography>
                <Typography variant="h3" color="primary" gutterBottom>
                  {learningProgress}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={learningProgress} 
                  sx={{ mb: 2, height: 8, borderRadius: 4 }}
                />
                <Typography variant="body2" color="text.secondary">
                  The AI has analyzed {Math.floor(learningProgress * 0.5)} of your trades
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <SmartToy sx={{ fontSize: 48, color: 'secondary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>AI Confidence</Typography>
                <Typography variant="h3" color="secondary" gutterBottom>
                  {aiConfidence}%
                </Typography>
                <LinearProgress 
                  variant="determinate" 
                  value={aiConfidence} 
                  color="secondary"
                  sx={{ mb: 2, height: 8, borderRadius: 4 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Confidence in personalized recommendations
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent sx={{ textAlign: 'center' }}>
                <Insights sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>Active Insights</Typography>
                <Typography variant="h3" color="success.main" gutterBottom>
                  {insights.length}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 3 }}>
                  New insights generated from your trading patterns
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Learning Metrics */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Assessment sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Learning Metrics
                </Typography>
                
                {metrics.map((metric, index) => (
                  <Box key={index} sx={{ mb: 3 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography variant="body1">{metric.name}</Typography>
                      <Typography variant="body1" color="primary">
                        {metric.value}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={metric.value} 
                      sx={{ mb: 1, height: 6, borderRadius: 3 }}
                    />
                    <Typography variant="caption" color="text.secondary">
                      {metric.description}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          </Grid>

          {/* Trading Patterns Learned */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Timeline sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Learned Trading Patterns
                </Typography>
                
                <List>
                  <ListItem>
                    <ListItemText 
                      primary="Preferred Trading Time"
                      secondary={tradingPatterns.preferredTradingTime}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Average Hold Time"
                      secondary={tradingPatterns.averageHoldTime}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Risk Tolerance"
                      secondary={tradingPatterns.riskTolerance}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Trading Style"
                      secondary={tradingPatterns.tradingStyle}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Win Rate"
                      secondary={tradingPatterns.winRate}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText 
                      primary="Average Return"
                      secondary={tradingPatterns.averageReturn}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Grid>

          {/* AI Insights */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <AutoAwesome sx={{ mr: 1, verticalAlign: 'middle' }} />
                  AI-Generated Insights
                </Typography>
                
                <Grid container spacing={2}>
                  {insights.map((insight) => (
                    <Grid item xs={12} md={6} key={insight.id}>
                      <Paper 
                        sx={{ 
                          p: 3, 
                          border: 1, 
                          borderColor: `${getInsightColor(insight.type)}.main`,
                          borderRadius: 2
                        }}
                      >
                        <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                          {getInsightIcon(insight.type)}
                          <Box sx={{ ml: 2, flexGrow: 1 }}>
                            <Typography variant="h6" gutterBottom>
                              {insight.title}
                            </Typography>
                            <Chip 
                              label={`${insight.confidence}% confidence`}
                              color={getInsightColor(insight.type) as any}
                              size="small"
                              sx={{ mb: 1 }}
                            />
                          </Box>
                        </Box>
                        <Typography variant="body2" color="text.secondary">
                          {insight.description}
                        </Typography>
                      </Paper>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Learning Progress Timeline */}
          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <School sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Learning Timeline
                </Typography>
                
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Learning Event</TableCell>
                        <TableCell>Confidence Impact</TableCell>
                        <TableCell>Status</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Today</TableCell>
                        <TableCell>Pattern recognition improvement</TableCell>
                        <TableCell>+3%</TableCell>
                        <TableCell>
                          <Chip label="Active" color="success" size="small" />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Yesterday</TableCell>
                        <TableCell>Risk tolerance analysis completed</TableCell>
                        <TableCell>+5%</TableCell>
                        <TableCell>
                          <Chip label="Completed" color="info" size="small" />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>2 days ago</TableCell>
                        <TableCell>Sector preference learning</TableCell>
                        <TableCell>+7%</TableCell>
                        <TableCell>
                          <Chip label="Completed" color="info" size="small" />
                        </TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>3 days ago</TableCell>
                        <TableCell>Initial trading pattern analysis</TableCell>
                        <TableCell>+15%</TableCell>
                        <TableCell>
                          <Chip label="Milestone" color="secondary" size="small" />
                        </TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default AILearningDashboard;
