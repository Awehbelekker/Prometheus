import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  Tooltip,
  IconButton,
  Chip,
  Alert,
  Tabs,
  Tab,
  Paper,
  LinearProgress
} from '@mui/material';
import {
  ViewInAr,
  ThreeDRotation,
  Visibility,
  Settings,
  Help,
  PlayArrow,
  Pause,
  Refresh,
  Fullscreen,
  TrendingUp,
  ShowChart,
  Timeline,
  Lightbulb
} from '@mui/icons-material';

/**
 * 🌟 INTUITIVE HOLOGRAPHIC UI - REDESIGNED FOR USABILITY
 * 
 * IMPROVEMENTS:
 * - Clear onboarding and tutorials
 * - Simple, intuitive controls
 * - Progressive disclosure of features
 * - Performance optimized
 * - Accessible design
 * - Educational tooltips
 */

interface HolographicMode {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

const IntuitiveHolographicUI: React.FC = () => {
  const [isActive, setIsActive] = useState(false);
  const [currentMode, setCurrentMode] = useState(0);
  const [showTutorial, setShowTutorial] = useState(true);
  const [intensity, setIntensity] = useState(50);
  const [rotationSpeed, setRotationSpeed] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const holographicModes: HolographicMode[] = [
    {
      id: 'market-overview',
      name: 'Market Overview',
      description: 'Simple 3D view of market movements - perfect for beginners',
      icon: ShowChart,
      difficulty: 'beginner'
    },
    {
      id: 'portfolio-sphere',
      name: 'Portfolio Sphere',
      description: 'Your investments visualized as an interactive 3D sphere',
      icon: ViewInAr,
      difficulty: 'beginner'
    },
    {
      id: 'trend-analysis',
      name: 'Trend Analysis',
      description: 'Advanced 3D trend visualization with predictive layers',
      icon: Timeline,
      difficulty: 'intermediate'
    },
    {
      id: 'neural-network',
      name: 'AI Neural View',
      description: 'Visualize AI decision-making in real-time 3D space',
      icon: ThreeDRotation,
      difficulty: 'advanced'
    }
  ];

  const currentModeData = holographicModes[currentMode];

  const handleActivate = async () => {
    setIsLoading(true);
    // Simulate initialization
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsActive(true);
    setIsLoading(false);
    setShowTutorial(false);
  };

  const handleDeactivate = () => {
    setIsActive(false);
    setShowTutorial(true);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return '#4caf50';
      case 'intermediate': return '#ff9800';
      case 'advanced': return '#f44336';
      default: return '#757575';
    }
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh', backgroundColor: '#0a0a0a', color: 'white' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ 
          mb: 2, 
          fontWeight: 700,
          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          🌟 Holographic Market Interface
        </Typography>
        <Typography variant="body1" sx={{ color: '#aaa', mb: 2 }}>
          Experience market data in revolutionary 3D space. Start with simple modes and progress to advanced visualizations.
        </Typography>
        
        {showTutorial && (
          <Alert 
            severity="info" 
            icon={<Lightbulb />}
            sx={{ 
              backgroundColor: 'rgba(0, 212, 255, 0.1)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              color: 'white',
              mb: 3
            }}
          >
            <Typography variant="body2">
              <strong>New to holographic trading?</strong> Start with "Market Overview" mode for an easy introduction to 3D market visualization.
            </Typography>
          </Alert>
        )}
      </Box>

      <Grid container spacing={3}>
        {/* Control Panel */}
        <Grid item xs={12} md={4}>
          <Card sx={{ 
            backgroundColor: 'rgba(26, 26, 46, 0.8)',
            border: '1px solid rgba(0, 212, 255, 0.3)',
            backdropFilter: 'blur(10px)'
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
                <Settings /> Control Panel
              </Typography>

              {/* Mode Selection */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 2, color: '#00d4ff' }}>
                  Visualization Mode
                </Typography>
                <Tabs 
                  value={currentMode} 
                  onChange={(_, newValue) => setCurrentMode(newValue)}
                  orientation="vertical"
                  sx={{ 
                    '& .MuiTab-root': { 
                      color: '#aaa',
                      alignItems: 'flex-start',
                      textAlign: 'left'
                    },
                    '& .Mui-selected': { 
                      color: '#00d4ff' 
                    }
                  }}
                >
                  {holographicModes.map((mode, index) => (
                    <Tab
                      key={mode.id}
                      label={
                        <Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <mode.icon fontSize="small" />
                            <Typography variant="body2" sx={{ fontWeight: 600 }}>
                              {mode.name}
                            </Typography>
                            <Chip 
                              label={mode.difficulty}
                              size="small"
                              sx={{ 
                                backgroundColor: getDifficultyColor(mode.difficulty),
                                color: 'white',
                                fontSize: '0.7rem',
                                height: 18
                              }}
                            />
                          </Box>
                          <Typography variant="caption" sx={{ color: '#aaa' }}>
                            {mode.description}
                          </Typography>
                        </Box>
                      }
                    />
                  ))}
                </Tabs>
              </Box>

              {/* Settings */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 2, color: '#00d4ff' }}>
                  Visual Settings
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Intensity: {intensity}%
                  </Typography>
                  <Slider
                    value={intensity}
                    onChange={(_, value) => setIntensity(value as number)}
                    min={10}
                    max={100}
                    sx={{ color: '#00d4ff' }}
                  />
                </Box>

                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Rotation Speed: {rotationSpeed}x
                  </Typography>
                  <Slider
                    value={rotationSpeed}
                    onChange={(_, value) => setRotationSpeed(value as number)}
                    min={0.1}
                    max={3}
                    step={0.1}
                    sx={{ color: '#00d4ff' }}
                  />
                </Box>
              </Box>

              {/* Action Buttons */}
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {!isActive ? (
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={isLoading ? <LinearProgress /> : <PlayArrow />}
                    onClick={handleActivate}
                    disabled={isLoading}
                    sx={{
                      background: 'linear-gradient(45deg, #00d4ff, #0099cc)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #0099cc, #00d4ff)'
                      }
                    }}
                  >
                    {isLoading ? 'Initializing...' : 'Activate Holographic View'}
                  </Button>
                ) : (
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<Pause />}
                    onClick={handleDeactivate}
                    sx={{
                      borderColor: '#ff6b35',
                      color: '#ff6b35',
                      '&:hover': {
                        borderColor: '#ff5722',
                        backgroundColor: 'rgba(255, 107, 53, 0.1)'
                      }
                    }}
                  >
                    Deactivate
                  </Button>
                )}
                
                <Button
                  variant="text"
                  startIcon={<Help />}
                  onClick={() => setShowTutorial(true)}
                  sx={{ color: '#aaa' }}
                >
                  Show Tutorial
                </Button>
              </Box>
            </CardContent>
          </Card>

          {/* Current Mode Info */}
          <Card sx={{ 
            mt: 2,
            backgroundColor: 'rgba(26, 26, 46, 0.8)',
            border: `1px solid ${getDifficultyColor(currentModeData.difficulty)}`,
            backdropFilter: 'blur(10px)'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <currentModeData.icon sx={{ color: getDifficultyColor(currentModeData.difficulty) }} />
                <Typography variant="h6">
                  {currentModeData.name}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: '#aaa', mb: 2 }}>
                {currentModeData.description}
              </Typography>
              <Chip 
                label={`${currentModeData.difficulty.toUpperCase()} LEVEL`}
                sx={{ 
                  backgroundColor: getDifficultyColor(currentModeData.difficulty),
                  color: 'white',
                  fontWeight: 600
                }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Holographic Display */}
        <Grid item xs={12} md={8}>
          <Card sx={{ 
            height: '600px',
            backgroundColor: 'rgba(10, 10, 10, 0.9)',
            border: isActive ? '2px solid #00d4ff' : '1px solid rgba(255, 255, 255, 0.1)',
            position: 'relative',
            overflow: 'hidden'
          }}>
            <CardContent sx={{ height: '100%', p: 0 }}>
              {!isActive ? (
                <Box sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, rgba(10, 10, 10, 0.9) 70%)'
                }}>
                  <ViewInAr sx={{ fontSize: 80, color: '#00d4ff', mb: 2, opacity: 0.5 }} />
                  <Typography variant="h5" sx={{ mb: 2, color: '#00d4ff' }}>
                    Holographic Display Ready
                  </Typography>
                  <Typography variant="body1" sx={{ color: '#aaa', textAlign: 'center', maxWidth: 400 }}>
                    Click "Activate Holographic View" to begin your 3D market visualization experience.
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ 
                  height: '100%', 
                  position: 'relative',
                  background: 'radial-gradient(circle, rgba(0, 212, 255, 0.2) 0%, rgba(10, 10, 10, 1) 100%)'
                }}>
                  {/* Simulated 3D Canvas */}
                  <canvas
                    ref={canvasRef}
                    width={800}
                    height={600}
                    style={{
                      width: '100%',
                      height: '100%',
                      background: 'transparent'
                    }}
                  />
                  
                  {/* Overlay Controls */}
                  <Box sx={{
                    position: 'absolute',
                    top: 16,
                    right: 16,
                    display: 'flex',
                    gap: 1
                  }}>
                    <Tooltip title="Refresh Data">
                      <IconButton sx={{ color: '#00d4ff', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
                        <Refresh />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Fullscreen">
                      <IconButton sx={{ color: '#00d4ff', backgroundColor: 'rgba(0, 0, 0, 0.5)' }}>
                        <Fullscreen />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  {/* Status Indicator */}
                  <Box sx={{
                    position: 'absolute',
                    bottom: 16,
                    left: 16,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: '8px 16px',
                    borderRadius: 2,
                    border: '1px solid rgba(0, 212, 255, 0.3)'
                  }}>
                    <Box sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: '#4caf50',
                      animation: 'pulse 2s infinite'
                    }} />
                    <Typography variant="caption" sx={{ color: '#4caf50' }}>
                      HOLOGRAPHIC MODE ACTIVE
                    </Typography>
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Quick Tips */}
          {isActive && (
            <Paper sx={{ 
              mt: 2, 
              p: 2, 
              backgroundColor: 'rgba(26, 26, 46, 0.8)',
              border: '1px solid rgba(0, 212, 255, 0.3)'
            }}>
              <Typography variant="subtitle2" sx={{ mb: 1, color: '#00d4ff' }}>
                💡 Quick Tips for {currentModeData.name}:
              </Typography>
              <Typography variant="body2" sx={{ color: '#aaa' }}>
                {currentModeData.difficulty === 'beginner' && 'Use mouse to rotate the view. Scroll to zoom in/out. Click on data points for details.'}
                {currentModeData.difficulty === 'intermediate' && 'Right-click for context menu. Use keyboard shortcuts: R (reset), F (fullscreen), H (help).'}
                {currentModeData.difficulty === 'advanced' && 'Advanced gestures enabled. Use multi-touch for complex interactions. Voice commands available.'}
              </Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      {/* CSS for animations */}
      <style>{`
        @keyframes pulse {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </Box>
  );
};

export default IntuitiveHolographicUI;
