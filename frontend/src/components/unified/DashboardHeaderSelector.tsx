import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  alpha,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Settings,
  Close,
  CheckCircle,
  ViewInAr,
  Dashboard,
  Speed
} from '@mui/icons-material';
import TradingCommandCenter from './TradingCommandCenter';
import PrometheusLogo from './PrometheusLogo';
import Logo from '../Logo';

/**
 * 🎨 DASHBOARD HEADER SELECTOR
 * Lets users choose between 3 different header styles
 */

interface HeaderOption {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  preview: React.ReactNode;
  recommended?: boolean;
}

interface DashboardHeaderSelectorProps {
  user: {
    username: string;
    email: string;
    tier: 'demo' | 'premium' | 'admin';
  };
  selectedHeader: string;
  onHeaderChange: (headerId: string) => void;
}

const DashboardHeaderSelector: React.FC<DashboardHeaderSelectorProps> = ({
  user,
  selectedHeader,
  onHeaderChange
}) => {
  const [selectorOpen, setSelectorOpen] = useState(false);

  const headerOptions: HeaderOption[] = [
    {
      id: 'command-center',
      name: 'Trading Command Center',
      description: 'Professional dashboard with live stats, original logo, and real-time monitoring',
      icon: Speed,
      recommended: true,
      preview: (
        <Box sx={{ transform: 'scale(0.6)', transformOrigin: 'top left', width: '166%' }}>
          <TradingCommandCenter user={user} />
        </Box>
      )
    },
    {
      id: 'holographic',
      name: 'Holographic Logo',
      description: 'Futuristic header with animated logo effects and holographic elements',
      icon: ViewInAr,
      preview: (
        <Box sx={{
          background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(156, 39, 176, 0.1) 100%)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0, 212, 255, 0.3)',
          borderRadius: 3,
          p: 3,
          position: 'relative',
          overflow: 'hidden'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <PrometheusLogo variant="full" size="medium" animated={true} />
            <Chip 
              label={user.tier.toUpperCase()}
              sx={{ 
                backgroundColor: alpha('#00d4ff', 0.2),
                color: '#00d4ff',
                fontWeight: 600
              }}
            />
          </Box>
        </Box>
      )
    },
    {
      id: 'minimal',
      name: 'Minimal Professional',
      description: 'Clean, simple header with original logo and essential information only',
      icon: Dashboard,
      preview: (
        <Box sx={{
          background: 'linear-gradient(135deg, rgba(26, 26, 46, 0.8) 0%, rgba(10, 10, 10, 0.9) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          p: 2
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Logo size="small" theme="dark" />
              <Box>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                  PROMETHEUS
                </Typography>
                <Typography variant="caption" sx={{ color: '#aaa' }}>
                  with NeuroForge™
                </Typography>
              </Box>
            </Box>
            <Typography variant="body2" sx={{ color: '#aaa' }}>
              Welcome, {user.username}
            </Typography>
          </Box>
        </Box>
      )
    }
  ];

  const currentHeader = headerOptions.find(option => option.id === selectedHeader);

  const handleHeaderSelect = (headerId: string) => {
    onHeaderChange(headerId);
    setSelectorOpen(false);
  };

  return (
    <>
      {/* Header Selector Button */}
      <Box sx={{ 
        position: 'fixed', 
        top: 20, 
        right: 20, 
        zIndex: 1000 
      }}>
        <Tooltip title="Change Dashboard Header Style">
          <IconButton
            onClick={() => setSelectorOpen(true)}
            sx={{
              backgroundColor: alpha('#00d4ff', 0.1),
              border: '1px solid rgba(0, 212, 255, 0.3)',
              color: '#00d4ff',
              '&:hover': {
                backgroundColor: alpha('#00d4ff', 0.2),
                transform: 'scale(1.1)'
              },
              transition: 'all 0.3s ease'
            }}
          >
            <Settings />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Header Selection Dialog */}
      <Dialog
        open={selectorOpen}
        onClose={() => setSelectorOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: {
            backgroundColor: '#1a1a2e',
            color: 'white',
            border: '2px solid rgba(0, 212, 255, 0.3)',
            borderRadius: 3
          }
        }}
      >
        <DialogTitle sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          borderBottom: '1px solid rgba(0, 212, 255, 0.2)',
          pb: 2
        }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#00d4ff' }}>
              🎨 Choose Your Dashboard Header
            </Typography>
            <Typography variant="body2" sx={{ color: '#aaa', mt: 1 }}>
              Select the header style that best fits your preferences
            </Typography>
          </Box>
          <IconButton 
            onClick={() => setSelectorOpen(false)}
            sx={{ color: '#aaa' }}
          >
            <Close />
          </IconButton>
        </DialogTitle>

        <DialogContent sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {headerOptions.map((option) => (
              <Grid item xs={12} key={option.id}>
                <Card sx={{
                  background: selectedHeader === option.id 
                    ? `linear-gradient(135deg, ${alpha('#00d4ff', 0.2)} 0%, ${alpha('#00d4ff', 0.1)} 100%)`
                    : `linear-gradient(135deg, ${alpha('#333', 0.3)} 0%, ${alpha('#333', 0.1)} 100%)`,
                  border: selectedHeader === option.id 
                    ? '2px solid #00d4ff' 
                    : '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: 3,
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 8px 25px rgba(0, 212, 255, 0.3)'
                  }
                }}>
                  <CardContent sx={{ p: 3 }}>
                    {/* Header Info */}
                    <Box sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      alignItems: 'center',
                      mb: 2
                    }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box sx={{
                          p: 1,
                          borderRadius: 2,
                          backgroundColor: alpha('#00d4ff', 0.2)
                        }}>
                          <option.icon sx={{ color: '#00d4ff', fontSize: 24 }} />
                        </Box>
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                              {option.name}
                            </Typography>
                            {option.recommended && (
                              <Chip 
                                label="RECOMMENDED" 
                                size="small"
                                sx={{ 
                                  backgroundColor: '#4caf50',
                                  color: 'white',
                                  fontSize: '0.7rem',
                                  height: 20
                                }}
                              />
                            )}
                          </Box>
                          <Typography variant="body2" sx={{ color: '#aaa', mt: 0.5 }}>
                            {option.description}
                          </Typography>
                        </Box>
                      </Box>
                      
                      {selectedHeader === option.id && (
                        <CheckCircle sx={{ color: '#4caf50', fontSize: 28 }} />
                      )}
                    </Box>

                    {/* Preview */}
                    <Box sx={{ 
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      borderRadius: 2,
                      overflow: 'hidden',
                      backgroundColor: '#0a0a0a'
                    }}>
                      {option.preview}
                    </Box>

                    {/* Select Button */}
                    <Box sx={{ mt: 2, textAlign: 'center' }}>
                      <Button
                        variant={selectedHeader === option.id ? "contained" : "outlined"}
                        onClick={() => handleHeaderSelect(option.id)}
                        sx={{
                          borderColor: '#00d4ff',
                          color: selectedHeader === option.id ? 'white' : '#00d4ff',
                          backgroundColor: selectedHeader === option.id ? '#00d4ff' : 'transparent',
                          '&:hover': {
                            backgroundColor: selectedHeader === option.id ? '#0099cc' : alpha('#00d4ff', 0.1)
                          }
                        }}
                      >
                        {selectedHeader === option.id ? 'Currently Selected' : 'Select This Style'}
                      </Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>

        <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(0, 212, 255, 0.2)' }}>
          <Typography variant="body2" sx={{ color: '#aaa', flex: 1 }}>
            Current: <strong>{currentHeader?.name}</strong>
          </Typography>
          <Button 
            onClick={() => setSelectorOpen(false)}
            sx={{ color: '#aaa' }}
          >
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default DashboardHeaderSelector;
