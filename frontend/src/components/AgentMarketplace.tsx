import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Button,
  Chip,
  Avatar
} from '@mui/material';
import { 
  SmartToy, 
  TrendingUp, 
  Analytics, 
  Security 
} from '@mui/icons-material';

interface Agent {
  id: string;
  name: string;
  description: string;
  category: string;
  rating: number;
  price: number;
  icon: React.ReactNode;
  features: string[];
}

const SAMPLE_AGENTS: Agent[] = [
  {
    id: '1',
    name: 'Neural Trading Bot',
    description: 'Advanced AI trading agent with neural network capabilities',
    category: 'Trading',
    rating: 4.8,
    price: 299,
    icon: <SmartToy sx={{ color: '#00d4ff' }} />,
    features: ['Real-time Analysis', 'Risk Management', 'Auto-trading']
  },
  {
    id: '2',
    name: 'Market Analyzer Pro',
    description: 'Professional market analysis and prediction agent',
    category: 'Analytics',
    rating: 4.6,
    price: 199,
    icon: <Analytics sx={{ color: '#ff6b35' }} />,
    features: ['Market Prediction', 'Trend Analysis', 'Custom Reports']
  },
  {
    id: '3',
    name: 'Risk Guardian',
    description: 'Advanced risk management and portfolio protection',
    category: 'Security',
    rating: 4.9,
    price: 399,
    icon: <Security sx={{ color: '#4caf50' }} />,
    features: ['Portfolio Protection', 'Risk Assessment', 'Alert System']
  },
  {
    id: '4',
    name: 'Trend Spotter',
    description: 'Identifies emerging market trends and opportunities',
    category: 'Analysis',
    rating: 4.7,
    price: 249,
    icon: <TrendingUp sx={{ color: '#9c27b0' }} />,
    features: ['Trend Detection', 'Opportunity Alerts', 'Market Insights']
  }
];

const AgentMarketplace: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, color: '#fff', fontWeight: 600 }}>
        Agent Marketplace
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 4, color: '#888' }}>
        Discover and deploy AI agents to enhance your trading capabilities
      </Typography>

      <Grid container spacing={3}>
        {SAMPLE_AGENTS.map((agent) => (
          <Grid item xs={12} sm={6} md={4} key={agent.id}>
            <Card 
              sx={{ 
                background: 'rgba(26, 26, 26, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: 2,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                '&:hover': {
                  borderColor: 'rgba(0, 212, 255, 0.3)',
                  transform: 'translateY(-2px)',
                  transition: 'all 0.3s ease'
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1, p: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'transparent', mr: 2 }}>
                    {agent.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h6" sx={{ color: '#fff', fontWeight: 600 }}>
                      {agent.name}
                    </Typography>
                    <Chip 
                      label={agent.category} 
                      size="small" 
                      sx={{ 
                        bgcolor: 'rgba(0, 212, 255, 0.2)', 
                        color: '#00d4ff',
                        fontSize: '0.75rem'
                      }} 
                    />
                  </Box>
                </Box>

                <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
                  {agent.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ color: '#fff', mb: 1, fontWeight: 500 }}>
                    Features:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {agent.features.map((feature, index) => (
                      <Chip
                        key={index}
                        label={feature}
                        size="small"
                        variant="outlined"
                        sx={{
                          borderColor: 'rgba(255, 255, 255, 0.2)',
                          color: '#888',
                          fontSize: '0.7rem'
                        }}
                      />
                    ))}
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ color: '#00d4ff', fontWeight: 600 }}>
                    ${agent.price}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="body2" sx={{ color: '#ffd700', mr: 0.5 }}>
                      ★ {agent.rating}
                    </Typography>
                  </Box>
                </Box>

                <Button
                  variant="contained"
                  fullWidth
                  sx={{
                    background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                    color: '#000',
                    fontWeight: 600,
                    '&:hover': {
                      background: 'linear-gradient(45deg, #00b8e6, #0088bb)',
                      transform: 'translateY(-1px)',
                      boxShadow: '0 4px 12px rgba(0, 212, 255, 0.3)'
                    },
                    transition: 'all 0.3s ease'
                  }}
                >
                  Deploy Agent
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="body2" sx={{ color: '#888', mb: 2 }}>
          More agents coming soon! Check back regularly for new AI capabilities.
        </Typography>
        <Button
          variant="outlined"
          sx={{
            borderColor: 'rgba(255, 255, 255, 0.2)',
            color: '#fff',
            '&:hover': {
              borderColor: '#00d4ff',
              backgroundColor: 'rgba(0, 212, 255, 0.1)'
            }
          }}
        >
          Request Custom Agent
        </Button>
      </Box>
    </Box>
  );
};

export default AgentMarketplace;
