import React from 'react';
import { Box, Typography, Grid, Card, CardContent, alpha } from '@mui/material';
import PrometheusLogo from './PrometheusLogo';

/**
 * 🎨 LOGO SHOWCASE COMPONENT
 * Demonstrates all logo variants with original Prometheus logo
 */

const LogoShowcase: React.FC = () => {
  return (
    <Box sx={{ 
      p: 4, 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      color: 'white'
    }}>
      <Typography variant="h3" sx={{ 
        mb: 4, 
        textAlign: 'center',
        fontWeight: 800,
        background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent'
      }}>
        🔥 Prometheus Logo Showcase
      </Typography>

      <Typography variant="h6" sx={{ 
        mb: 6, 
        textAlign: 'center',
        color: '#aaa'
      }}>
        Using your original logo with enhanced branding: "Prometheus with NeuroForge™"
      </Typography>

      <Grid container spacing={4}>
        {/* Full Logo Variant */}
        <Grid item xs={12} md={4}>
          <Card sx={{
            background: `linear-gradient(135deg, ${alpha('#00d4ff', 0.1)} 0%, ${alpha('#00d4ff', 0.05)} 100%)`,
            border: `1px solid ${alpha('#00d4ff', 0.3)}`,
            backdropFilter: 'blur(10px)',
            p: 3,
            textAlign: 'center',
            minHeight: 300,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, color: '#00d4ff' }}>
                Full Logo (Large)
              </Typography>
              <Box sx={{ mb: 3 }}>
                <PrometheusLogo variant="full" size="large" animated={true} />
              </Box>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Complete logo with original Prometheus image, enhanced animations, and NeuroForge™ branding
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Compact Logo Variant */}
        <Grid item xs={12} md={4}>
          <Card sx={{
            background: `linear-gradient(135deg, ${alpha('#9c27b0', 0.1)} 0%, ${alpha('#9c27b0', 0.05)} 100%)`,
            border: `1px solid ${alpha('#9c27b0', 0.3)}`,
            backdropFilter: 'blur(10px)',
            p: 3,
            textAlign: 'center',
            minHeight: 300,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, color: '#9c27b0' }}>
                Compact Logo (Medium)
              </Typography>
              <Box sx={{ mb: 3 }}>
                <PrometheusLogo variant="compact" size="medium" animated={true} />
              </Box>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Perfect for navigation bars and headers. Original logo with PROMETHEUS text
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Icon Logo Variant */}
        <Grid item xs={12} md={4}>
          <Card sx={{
            background: `linear-gradient(135deg, ${alpha('#ff6b35', 0.1)} 0%, ${alpha('#ff6b35', 0.05)} 100%)`,
            border: `1px solid ${alpha('#ff6b35', 0.3)}`,
            backdropFilter: 'blur(10px)',
            p: 3,
            textAlign: 'center',
            minHeight: 300,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, color: '#ff6b35' }}>
                Icon Only (Small)
              </Typography>
              <Box sx={{ mb: 3 }}>
                <PrometheusLogo variant="icon" size="small" animated={true} />
              </Box>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                Minimal icon version for favicons, mobile apps, and compact spaces
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Size Variations */}
        <Grid item xs={12}>
          <Card sx={{
            background: `linear-gradient(135deg, ${alpha('#4caf50', 0.1)} 0%, ${alpha('#4caf50', 0.05)} 100%)`,
            border: `1px solid ${alpha('#4caf50', 0.3)}`,
            backdropFilter: 'blur(10px)',
            p: 4
          }}>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 4, color: '#4caf50', textAlign: 'center' }}>
                Size Variations
              </Typography>
              
              <Grid container spacing={4} alignItems="center" justifyContent="center">
                <Grid item>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" sx={{ mb: 2, color: '#aaa' }}>Small</Typography>
                    <PrometheusLogo variant="compact" size="small" animated={false} />
                  </Box>
                </Grid>
                
                <Grid item>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" sx={{ mb: 2, color: '#aaa' }}>Medium</Typography>
                    <PrometheusLogo variant="compact" size="medium" animated={false} />
                  </Box>
                </Grid>
                
                <Grid item>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="body2" sx={{ mb: 2, color: '#aaa' }}>Large</Typography>
                    <PrometheusLogo variant="compact" size="large" animated={false} />
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Features Summary */}
        <Grid item xs={12}>
          <Card sx={{
            background: `linear-gradient(135deg, ${alpha('#e91e63', 0.1)} 0%, ${alpha('#e91e63', 0.05)} 100%)`,
            border: `1px solid ${alpha('#e91e63', 0.3)}`,
            backdropFilter: 'blur(10px)',
            p: 4
          }}>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 3, color: '#e91e63', textAlign: 'center' }}>
                ✨ Enhanced Features
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" sx={{ color: '#00d4ff', mb: 1 }}>
                      🎨 Original Logo
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      Uses your authentic Prometheus logo image
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" sx={{ color: '#9c27b0', mb: 1 }}>
                      ⚡ Animations
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      Smooth hover effects and floating elements
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" sx={{ color: '#ff6b35', mb: 1 }}>
                      🏷️ Proper Branding
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      "Prometheus with NeuroForge™" format
                    </Typography>
                  </Box>
                </Grid>
                
                <Grid item xs={12} sm={6} md={3}>
                  <Box sx={{ textAlign: 'center' }}>
                    <Typography variant="h6" sx={{ color: '#4caf50', mb: 1 }}>
                      📱 Responsive
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#aaa' }}>
                      Perfect scaling on all devices
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default LogoShowcase;
