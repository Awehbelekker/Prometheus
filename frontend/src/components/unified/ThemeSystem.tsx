import React from 'react';
import { Box, Typography, Grid, Card, CardContent, Button, Chip, alpha } from '@mui/material';
import { Palette, DarkMode, LightMode, AutoAwesome, Nature, LocalFireDepartment } from '@mui/icons-material';

/**
 * 🎨 THEME SYSTEM
 * Multiple theme options for the trading platform
 */

export interface Theme {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
  };
  gradient: string;
}

export const themes: Theme[] = [
  {
    id: 'dark',
    name: 'Dark Professional',
    description: 'Classic dark theme for professional trading',
    icon: DarkMode,
    colors: {
      primary: '#00d4ff',
      secondary: '#9c27b0',
      accent: '#ff6b35',
      background: '#0a0a0a',
      surface: '#1a1a2e',
      text: '#ffffff',
      textSecondary: '#aaaaaa'
    },
    gradient: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)'
  },
  {
    id: 'cyber',
    name: 'Cyber Neon',
    description: 'Futuristic neon theme with electric colors',
    icon: AutoAwesome,
    colors: {
      primary: '#00ff88',
      secondary: '#ff0080',
      accent: '#ffff00',
      background: '#000011',
      surface: '#001122',
      text: '#ffffff',
      textSecondary: '#88ffaa'
    },
    gradient: 'linear-gradient(135deg, #000011 0%, #001122 100%)'
  },
  {
    id: 'ocean',
    name: 'Ocean Blue',
    description: 'Calming ocean-inspired blue theme',
    icon: Nature,
    colors: {
      primary: '#0077be',
      secondary: '#004d7a',
      accent: '#00a8cc',
      background: '#001a2e',
      surface: '#002a3e',
      text: '#ffffff',
      textSecondary: '#b3d9ff'
    },
    gradient: 'linear-gradient(135deg, #001a2e 0%, #002a3e 100%)'
  },
  {
    id: 'fire',
    name: 'Fire Red',
    description: 'Intense red theme for aggressive trading',
    icon: LocalFireDepartment,
    colors: {
      primary: '#ff4444',
      secondary: '#cc0000',
      accent: '#ff8800',
      background: '#1a0000',
      surface: '#2a0000',
      text: '#ffffff',
      textSecondary: '#ffaaaa'
    },
    gradient: 'linear-gradient(135deg, #1a0000 0%, #2a0000 100%)'
  },
  {
    id: 'light',
    name: 'Light Professional',
    description: 'Clean light theme for day trading',
    icon: LightMode,
    colors: {
      primary: '#1976d2',
      secondary: '#7b1fa2',
      accent: '#f57c00',
      background: '#f5f5f5',
      surface: '#ffffff',
      text: '#212121',
      textSecondary: '#757575'
    },
    gradient: 'linear-gradient(135deg, #f5f5f5 0%, #ffffff 100%)'
  }
];

interface ThemeSystemProps {
  selectedTheme: string;
  onThemeChange: (themeId: string) => void;
}

const ThemeSystem: React.FC<ThemeSystemProps> = ({ selectedTheme, onThemeChange }) => {
  const currentTheme = themes.find(theme => theme.id === selectedTheme) || themes[0];

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h6" sx={{ mb: 3, color: currentTheme.colors.primary, fontWeight: 700 }}>
        🎨 Theme Settings
      </Typography>

      <Grid container spacing={2}>
        {themes.map((theme) => (
          <Grid item xs={12} key={theme.id}>
            <Card sx={{
              background: selectedTheme === theme.id 
                ? `linear-gradient(135deg, ${alpha(theme.colors.primary, 0.2)} 0%, ${alpha(theme.colors.primary, 0.1)} 100%)`
                : `linear-gradient(135deg, ${alpha('#333', 0.3)} 0%, ${alpha('#333', 0.1)} 100%)`,
              border: selectedTheme === theme.id 
                ? `2px solid ${theme.colors.primary}` 
                : '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: 2,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: `0 4px 15px ${alpha(theme.colors.primary, 0.3)}`
              }
            }}>
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                  <Box sx={{
                    p: 1,
                    borderRadius: 1,
                    backgroundColor: alpha(theme.colors.primary, 0.2)
                  }}>
                    <theme.icon sx={{ color: theme.colors.primary, fontSize: 20 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="body1" sx={{ color: 'white', fontWeight: 600 }}>
                      {theme.name}
                    </Typography>
                    <Typography variant="caption" sx={{ color: '#aaa' }}>
                      {theme.description}
                    </Typography>
                  </Box>
                  {selectedTheme === theme.id && (
                    <Chip 
                      label="ACTIVE" 
                      size="small"
                      sx={{ 
                        backgroundColor: theme.colors.primary,
                        color: 'white',
                        fontSize: '0.7rem',
                        height: 20
                      }}
                    />
                  )}
                </Box>

                {/* Color Preview */}
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Box sx={{
                    width: 20,
                    height: 20,
                    borderRadius: 1,
                    backgroundColor: theme.colors.primary,
                    border: '1px solid rgba(255, 255, 255, 0.2)'
                  }} />
                  <Box sx={{
                    width: 20,
                    height: 20,
                    borderRadius: 1,
                    backgroundColor: theme.colors.secondary,
                    border: '1px solid rgba(255, 255, 255, 0.2)'
                  }} />
                  <Box sx={{
                    width: 20,
                    height: 20,
                    borderRadius: 1,
                    backgroundColor: theme.colors.accent,
                    border: '1px solid rgba(255, 255, 255, 0.2)'
                  }} />
                </Box>

                <Button
                  variant={selectedTheme === theme.id ? "contained" : "outlined"}
                  size="small"
                  fullWidth
                  onClick={() => onThemeChange(theme.id)}
                  sx={{
                    borderColor: theme.colors.primary,
                    color: selectedTheme === theme.id ? 'white' : theme.colors.primary,
                    backgroundColor: selectedTheme === theme.id ? theme.colors.primary : 'transparent',
                    '&:hover': {
                      backgroundColor: selectedTheme === theme.id ? theme.colors.secondary : alpha(theme.colors.primary, 0.1)
                    }
                  }}
                >
                  {selectedTheme === theme.id ? 'Active Theme' : 'Apply Theme'}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default ThemeSystem;
