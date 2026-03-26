import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Button, Chip, alpha } from '@mui/material';
import { 
  Speed, 
  ViewInAr, 
  Dashboard, 
  Timeline, 
  Analytics,
  TrendingUp
} from '@mui/icons-material';

/**
 * 🎯 DASHBOARD STYLE SELECTOR
 * Multiple header options for the dashboard
 */

export interface HeaderStyle {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  features: string[];
  recommended?: boolean;
}

export const headerStyles: HeaderStyle[] = [
  {
    id: 'command-center',
    name: 'Command Center',
    description: 'Professional dashboard with live stats and monitoring',
    icon: Speed,
    recommended: true,
    features: ['Live Stats', 'System Health', 'Real-time Data', 'Professional Layout']
  },
  {
    id: 'analytics-pro',
    name: 'Analytics Pro',
    description: 'Data-focused header with advanced metrics and charts',
    icon: Analytics,
    features: ['Advanced Metrics', 'Performance Charts', 'Data Visualization', 'Trend Analysis']
  },
  {
    id: 'trader-hub',
    name: 'Trader Hub',
    description: 'Trading-focused header with market data and quick actions',
    icon: TrendingUp,
    features: ['Market Data', 'Quick Actions', 'Trading Tools', 'Portfolio Overview']
  },
  {
    id: 'timeline-view',
    name: 'Timeline View',
    description: 'Chronological header showing trading timeline and events',
    icon: Timeline,
    features: ['Trading Timeline', 'Event History', 'Activity Feed', 'Time-based Data']
  },
  {
    id: 'holographic-v2',
    name: 'Holographic Pro',
    description: 'Advanced holographic interface with 3D elements and animations',
    icon: ViewInAr,
    features: ['3D Elements', 'Advanced Animations', 'Holographic Effects', 'Futuristic Design']
  },
  {
    id: 'minimal',
    name: 'Minimal Clean',
    description: 'Clean, simple header with essential information only',
    icon: Dashboard,
    features: ['Clean Design', 'Essential Info', 'Minimal Clutter', 'Fast Loading']
  }
];

interface DashboardStyleSelectorProps {
  selectedHeader: string;
  onHeaderChange: (headerId: string) => void;
}

const DashboardStyleSelector: React.FC<DashboardStyleSelectorProps> = ({ 
  selectedHeader, 
  onHeaderChange 
}) => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 3, color: '#00d4ff', fontWeight: 700 }}>
        🎯 Dashboard Style
      </Typography>

      <Grid container spacing={2}>
        {headerStyles.map((style) => (
          <Grid item xs={12} key={style.id}>
            <Card sx={{
              background: selectedHeader === style.id 
                ? `linear-gradient(135deg, ${alpha('#00d4ff', 0.2)} 0%, ${alpha('#00d4ff', 0.1)} 100%)`
                : `linear-gradient(135deg, ${alpha('#333', 0.3)} 0%, ${alpha('#333', 0.1)} 100%)`,
              border: selectedHeader === style.id 
                ? '2px solid #00d4ff' 
                : '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 2,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: '0 4px 15px rgba(0, 212, 255, 0.3)'
              }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{
                    p: 1,
                    borderRadius: 1,
                    backgroundColor: alpha('#00d4ff', 0.2)
                  }}>
                    <style.icon sx={{ color: '#00d4ff', fontSize: 20 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>
                        {style.name}
                      </Typography>
                      {style.recommended && (
                        <Chip 
                          label="RECOMMENDED" 
                          size="small"
                          sx={{ 
                            backgroundColor: '#4caf50',
                            color: 'white',
                            fontSize: '0.6rem',
                            height: 18
                          }}
                        />
                      )}
                      {selectedHeader === style.id && (
                        <Chip 
                          label="ACTIVE" 
                          size="small"
                          sx={{ 
                            backgroundColor: '#00d4ff',
                            color: 'white',
                            fontSize: '0.6rem',
                            height: 18
                          }}
                        />
                      )}
                    </Box>
                    <Typography variant="caption" sx={{ color: '#aaa', display: 'block', mb: 1 }}>
                      {style.description}
                    </Typography>
                    
                    {/* Features */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {style.features.slice(0, 2).map((feature, index) => (
                        <Chip
                          key={index}
                          label={feature}
                          size="small"
                          sx={{
                            backgroundColor: alpha('#00d4ff', 0.1),
                            color: '#00d4ff',
                            fontSize: '0.6rem',
                            height: 16
                          }}
                        />
                      ))}
                      {style.features.length > 2 && (
                        <Chip
                          label={`+${style.features.length - 2} more`}
                          size="small"
                          sx={{
                            backgroundColor: alpha('#aaa', 0.1),
                            color: '#aaa',
                            fontSize: '0.6rem',
                            height: 16
                          }}
                        />
                      )}
                    </Box>
                  </Box>
                </Box>

                <Button
                  variant={selectedHeader === style.id ? "contained" : "outlined"}
                  size="small"
                  fullWidth
                  onClick={() => onHeaderChange(style.id)}
                  sx={{
                    borderColor: '#00d4ff',
                    color: selectedHeader === style.id ? 'white' : '#00d4ff',
                    backgroundColor: selectedHeader === style.id ? '#00d4ff' : 'transparent',
                    '&:hover': {
                      backgroundColor: selectedHeader === style.id ? '#0099cc' : alpha('#00d4ff', 0.1)
                    }
                  }}
                >
                  {selectedHeader === style.id ? 'Currently Active' : 'Apply Style'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default DashboardStyleSelector;
