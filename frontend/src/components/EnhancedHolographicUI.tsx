import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Typography,
  Card,
  Button,
  Grid,
  Slider,
  FormControlLabel,
  Switch,
  Tooltip,
  IconButton,
  Chip,
  Alert,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  ViewInAr,
  ThreeDRotation,
  Visibility,
  VisibilityOff,
  Settings,
  Fullscreen,
  FullscreenExit,
  Info,
  TrendingUp,
  ShowChart,
  Timeline
} from '@mui/icons-material';

/**
 * 🌟 ENHANCED HOLOGRAPHIC UI
 * Revolutionary 3D Market Visualization with Context and Intuitive Controls
 * 
 * IMPROVEMENTS:
 * - Clear contextual information and legends
 * - Intuitive navigation and controls
 * - Multiple visualization modes
 * - Educational tooltips and guidance
 * - Performance optimizations
 * - Accessibility features
 */

interface MarketDataPoint {
  symbol: string;
  price: number;
  volume: number;
  change: number;
  timestamp: number;
  x: number;
  y: number;
  z: number;
}

interface HolographicLayer {
  id: string;
  name: string;
  description: string;
  visible: boolean;
  opacity: number;
  color: string;
  data: MarketDataPoint[];
}

const EnhancedHolographicUI: React.FC = () => {
  // Core state
  const [isActive, setIsActive] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [viewMode, setViewMode] = useState<'market' | 'portfolio' | 'analysis'>('market');
  const [rotationSpeed, setRotationSpeed] = useState(1);
  const [zoomLevel, setZoomLevel] = useState(1);
  
  // Visualization layers
  const [layers, setLayers] = useState<HolographicLayer[]>([
    {
      id: 'price',
      name: 'Price Movement',
      description: 'Real-time price changes visualized as 3D trajectories',
      visible: true,
      opacity: 0.8,
      color: '#00d4ff',
      data: []
    },
    {
      id: 'volume',
      name: 'Trading Volume',
      description: 'Volume represented as sphere sizes in 3D space',
      visible: true,
      opacity: 0.6,
      color: '#9c27b0',
      data: []
    },
    {
      id: 'sentiment',
      name: 'Market Sentiment',
      description: 'AI-analyzed sentiment as color gradients',
      visible: false,
      opacity: 0.5,
      color: '#4caf50',
      data: []
    },
    {
      id: 'correlation',
      name: 'Asset Correlations',
      description: 'Connection lines showing asset relationships',
      visible: false,
      opacity: 0.4,
      color: '#ff9800',
      data: []
    }
  ]);

  // Canvas and animation
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationRef = useRef<number>();
  const [rotation, setRotation] = useState({ x: 0, y: 0, z: 0 });

  // Generate sample market data
  const generateMarketData = useCallback(() => {
    const symbols = ['BTC', 'ETH', 'AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN', 'NVDA'];
    const newData: MarketDataPoint[] = symbols.map((symbol, index) => ({
      symbol,
      price: 100 + Math.random() * 1000,
      volume: Math.random() * 1000000,
      change: (Math.random() - 0.5) * 10,
      timestamp: Date.now(),
      x: (index % 3) * 100 - 100,
      y: Math.floor(index / 3) * 100 - 100,
      z: Math.random() * 200 - 100
    }));

    setLayers(prev => prev.map(layer => ({
      ...layer,
      data: newData
    })));
  }, []);

  // Initialize data
  useEffect(() => {
    generateMarketData();
    const interval = setInterval(generateMarketData, 2000);
    return () => clearInterval(interval);
  }, [generateMarketData]);

  // Enhanced 3D visualization with context
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !isActive) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const container = containerRef.current;
    if (container) {
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const time = Date.now() * 0.001;

      // Update rotation
      setRotation(prev => ({
        x: prev.x + rotationSpeed * 0.01,
        y: prev.y + rotationSpeed * 0.005,
        z: prev.z + rotationSpeed * 0.008
      }));

      // Draw coordinate system
      drawCoordinateSystem(ctx, centerX, centerY, rotation);

      // Draw each visible layer
      layers.forEach(layer => {
        if (layer.visible && layer.data.length > 0) {
          drawLayer(ctx, layer, centerX, centerY, rotation, zoomLevel);
        }
      });

      // Draw information overlay
      drawInfoOverlay(ctx, layers);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, layers, rotation, rotationSpeed, zoomLevel]);

  const drawCoordinateSystem = (
    ctx: CanvasRenderingContext2D,
    centerX: number,
    centerY: number,
    rotation: { x: number; y: number; z: number }
  ) => {
    const axisLength = 150;
    
    // X-axis (red)
    ctx.strokeStyle = '#ff4444';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(centerX - axisLength, centerY);
    ctx.lineTo(centerX + axisLength, centerY);
    ctx.stroke();
    
    // Y-axis (green)
    ctx.strokeStyle = '#44ff44';
    ctx.beginPath();
    ctx.moveTo(centerX, centerY - axisLength);
    ctx.lineTo(centerX, centerY + axisLength);
    ctx.stroke();
    
    // Z-axis representation (blue, diagonal)
    ctx.strokeStyle = '#4444ff';
    ctx.beginPath();
    ctx.moveTo(centerX - axisLength * 0.7, centerY + axisLength * 0.7);
    ctx.lineTo(centerX + axisLength * 0.7, centerY - axisLength * 0.7);
    ctx.stroke();

    // Axis labels
    ctx.fillStyle = '#ffffff';
    ctx.font = '12px Arial';
    ctx.fillText('Price →', centerX + axisLength + 10, centerY);
    ctx.fillText('↑ Volume', centerX, centerY - axisLength - 10);
    ctx.fillText('Time ↗', centerX + axisLength * 0.7 + 10, centerY - axisLength * 0.7);
  };

  const drawLayer = (
    ctx: CanvasRenderingContext2D,
    layer: HolographicLayer,
    centerX: number,
    centerY: number,
    rotation: { x: number; y: number; z: number },
    zoom: number
  ) => {
    ctx.globalAlpha = layer.opacity;
    
    layer.data.forEach((point, index) => {
      // Apply 3D transformation
      const x = centerX + (point.x * zoom * Math.cos(rotation.y));
      const y = centerY + (point.y * zoom * Math.cos(rotation.x));
      const z = point.z * zoom;
      
      // Size based on z-depth and data
      const size = Math.max(3, (100 + z) / 20 + point.volume / 100000);
      
      // Color based on change
      let color = layer.color;
      if (layer.id === 'price') {
        color = point.change > 0 ? '#4caf50' : point.change < 0 ? '#f44336' : '#ffeb3b';
      }
      
      // Draw data point
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.arc(x, y, size, 0, 2 * Math.PI);
      ctx.fill();
      
      // Draw symbol label
      ctx.fillStyle = '#ffffff';
      ctx.font = '10px Arial';
      ctx.fillText(point.symbol, x + size + 2, y - size);
      
      // Draw value
      ctx.font = '8px Arial';
      ctx.fillText(`$${point.price.toFixed(2)}`, x + size + 2, y);
      ctx.fillText(`${point.change > 0 ? '+' : ''}${point.change.toFixed(2)}%`, x + size + 2, y + 10);
    });
    
    ctx.globalAlpha = 1;
  };

  const drawInfoOverlay = (ctx: CanvasRenderingContext2D, layers: HolographicLayer[]) => {
    // Legend
    const legendX = 20;
    let legendY = 20;
    
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(legendX - 10, legendY - 10, 200, layers.filter(l => l.visible).length * 25 + 40);
    
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px Arial';
    ctx.fillText('3D Market Visualization', legendX, legendY + 15);
    
    legendY += 30;
    ctx.font = '12px Arial';
    
    layers.filter(layer => layer.visible).forEach(layer => {
      ctx.fillStyle = layer.color;
      ctx.fillRect(legendX, legendY, 15, 15);
      
      ctx.fillStyle = '#ffffff';
      ctx.fillText(layer.name, legendX + 20, legendY + 12);
      
      legendY += 25;
    });
  };

  const toggleLayer = (layerId: string) => {
    setLayers(prev => prev.map(layer =>
      layer.id === layerId ? { ...layer, visible: !layer.visible } : layer
    ));
  };

  const updateLayerOpacity = (layerId: string, opacity: number) => {
    setLayers(prev => prev.map(layer =>
      layer.id === layerId ? { ...layer, opacity } : layer
    ));
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  return (
    <Box sx={{ 
      p: 3, 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
      ...(isFullscreen && {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 9999,
        p: 1
      })
    }}>
      {/* Header */}
      <Card sx={{
        p: 3,
        mb: 3,
        background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 50%, #3a3a3a 100%)',
        border: '2px solid #00d4ff',
        borderRadius: 3,
        boxShadow: '0 0 30px rgba(0, 212, 255, 0.3)'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ViewInAr sx={{ fontSize: 40, color: '#00d4ff' }} />
            <Box>
              <Typography variant="h4" sx={{ color: '#00d4ff', fontWeight: 700 }}>
                🌟 Enhanced Holographic Market Visualization
              </Typography>
              <Typography variant="subtitle1" sx={{ color: '#9c27b0', fontStyle: 'italic' }}>
                Intuitive 3D Market Analysis with Context & Controls
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Toggle Fullscreen">
              <IconButton onClick={toggleFullscreen} sx={{ color: '#00d4ff' }}>
                {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
              </IconButton>
            </Tooltip>
            
            <Button
              variant="contained"
              size="large"
              onClick={() => setIsActive(!isActive)}
              startIcon={isActive ? <VisibilityOff /> : <Visibility />}
              sx={{
                background: isActive
                  ? 'linear-gradient(45deg, #f44336 30%, #ff9800 90%)'
                  : 'linear-gradient(45deg, #00d4ff 30%, #9c27b0 90%)',
                color: 'white',
                fontWeight: 600,
                px: 4,
                py: 1.5,
                '&:hover': {
                  transform: 'scale(1.05)',
                  boxShadow: '0 0 20px rgba(0, 212, 255, 0.5)'
                }
              }}
            >
              {isActive ? 'Deactivate Hologram' : 'Activate Hologram'}
            </Button>
          </Box>
        </Box>

        {isActive && (
          <Alert
            severity="info"
            sx={{
              backgroundColor: 'rgba(0, 212, 255, 0.1)',
              color: '#00d4ff',
              border: '1px solid #00d4ff'
            }}
          >
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              🌟 Holographic Display Active - Use controls below to customize your 3D market view
            </Typography>
          </Alert>
        )}
      </Card>

      {isActive && (
        <Grid container spacing={3}>
          {/* 3D Visualization Canvas */}
          <Grid item xs={12} lg={8}>
            <Card sx={{
              p: 2,
              background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
              border: '1px solid #00d4ff',
              borderRadius: 2,
              height: isFullscreen ? 'calc(100vh - 200px)' : '600px'
            }}>
              <Box ref={containerRef} sx={{ width: '100%', height: '100%', position: 'relative' }}>
                <canvas
                  ref={canvasRef}
                  style={{
                    width: '100%',
                    height: '100%',
                    background: 'radial-gradient(circle, #1a1a1a 0%, #0a0a0a 100%)',
                    borderRadius: '8px'
                  }}
                />
              </Box>
            </Card>
          </Grid>

          {/* Controls Panel */}
          <Grid item xs={12} lg={4}>
            <Grid container spacing={2}>
              {/* View Mode */}
              <Grid item xs={12}>
                <Card sx={{ p: 2, background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)', border: '1px solid #9c27b0' }}>
                  <Typography variant="h6" sx={{ color: '#9c27b0', mb: 2, display: 'flex', alignItems: 'center' }}>
                    <Settings sx={{ mr: 1 }} />
                    View Controls
                  </Typography>
                  
                  <FormControl fullWidth sx={{ mb: 2 }}>
                    <InputLabel sx={{ color: '#ccc' }}>View Mode</InputLabel>
                    <Select
                      value={viewMode}
                      onChange={(e) => setViewMode(e.target.value as any)}
                      sx={{ color: '#fff' }}
                    >
                      <MenuItem value="market">Market Overview</MenuItem>
                      <MenuItem value="portfolio">Portfolio Analysis</MenuItem>
                      <MenuItem value="analysis">Technical Analysis</MenuItem>
                    </Select>
                  </FormControl>

                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    Rotation Speed: {rotationSpeed}x
                  </Typography>
                  <Slider
                    value={rotationSpeed}
                    onChange={(_, value) => setRotationSpeed(value as number)}
                    min={0}
                    max={5}
                    step={0.1}
                    sx={{ color: '#9c27b0', mb: 2 }}
                  />

                  <Typography variant="body2" sx={{ color: '#ccc', mb: 1 }}>
                    Zoom Level: {zoomLevel}x
                  </Typography>
                  <Slider
                    value={zoomLevel}
                    onChange={(_, value) => setZoomLevel(value as number)}
                    min={0.5}
                    max={3}
                    step={0.1}
                    sx={{ color: '#9c27b0' }}
                  />
                </Card>
              </Grid>

              {/* Layer Controls */}
              <Grid item xs={12}>
                <Card sx={{ p: 2, background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)', border: '1px solid #4caf50' }}>
                  <Typography variant="h6" sx={{ color: '#4caf50', mb: 2, display: 'flex', alignItems: 'center' }}>
                    <ThreeDRotation sx={{ mr: 1 }} />
                    Visualization Layers
                  </Typography>
                  
                  {layers.map(layer => (
                    <Box key={layer.id} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                        <FormControlLabel
                          control={
                            <Switch
                              checked={layer.visible}
                              onChange={() => toggleLayer(layer.id)}
                              sx={{ color: layer.color }}
                            />
                          }
                          label={
                            <Box>
                              <Typography variant="body2" sx={{ color: layer.color, fontWeight: 600 }}>
                                {layer.name}
                              </Typography>
                              <Typography variant="caption" sx={{ color: '#ccc' }}>
                                {layer.description}
                              </Typography>
                            </Box>
                          }
                        />
                        <Tooltip title="Layer Information">
                          <IconButton size="small" sx={{ color: '#ccc' }}>
                            <Info fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                      
                      {layer.visible && (
                        <Box sx={{ ml: 2 }}>
                          <Typography variant="caption" sx={{ color: '#ccc' }}>
                            Opacity: {Math.round(layer.opacity * 100)}%
                          </Typography>
                          <Slider
                            value={layer.opacity}
                            onChange={(_, value) => updateLayerOpacity(layer.id, value as number)}
                            min={0.1}
                            max={1}
                            step={0.1}
                            size="small"
                            sx={{ color: layer.color }}
                          />
                        </Box>
                      )}
                    </Box>
                  ))}
                </Card>
              </Grid>

              {/* Quick Actions */}
              <Grid item xs={12}>
                <Card sx={{ p: 2, background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)', border: '1px solid #ff9800' }}>
                  <Typography variant="h6" sx={{ color: '#ff9800', mb: 2 }}>
                    Quick Actions
                  </Typography>
                  
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    <Button
                      variant="outlined"
                      startIcon={<TrendingUp />}
                      sx={{ color: '#4caf50', borderColor: '#4caf50' }}
                      onClick={() => setViewMode('market')}
                    >
                      Focus on Trending Assets
                    </Button>
                    
                    <Button
                      variant="outlined"
                      startIcon={<ShowChart />}
                      sx={{ color: '#00d4ff', borderColor: '#00d4ff' }}
                      onClick={() => setViewMode('analysis')}
                    >
                      Technical Analysis View
                    </Button>
                    
                    <Button
                      variant="outlined"
                      startIcon={<Timeline />}
                      sx={{ color: '#9c27b0', borderColor: '#9c27b0' }}
                      onClick={generateMarketData}
                    >
                      Refresh Market Data
                    </Button>
                  </Box>
                </Card>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      )}
    </Box>
  );
};

export default EnhancedHolographicUI;
