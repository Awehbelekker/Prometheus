import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  IconButton,
  Fade,
  Slide,
  Zoom,
  Grow,
  Collapse,
  useTheme,
  useMediaQuery,
  Theme
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Refresh,
  Star,
  Favorite,
  ThumbUp,
  TrendingUp,
  FlashOn,
  AutoAwesome,
  Psychology,
  Rocket,
  Speed
} from '@mui/icons-material';
import ModernCard from './ModernCard';
import './AdvancedAnimations.css';
import clsx from 'clsx';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  color: string;
  life: number;
  maxLife: number;
}

interface AnimationState {
  isPlaying: boolean;
  currentAnimation: string;
  particleCount: number;
  animationSpeed: number;
}

const AdvancedAnimations: React.FC = () => {
  const theme = useTheme() as Theme;
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  
  const [animationState, setAnimationState] = useState<AnimationState>({
    isPlaying: false,
    currentAnimation: 'particles',
    particleCount: 50,
    animationSpeed: 1
  });

  const [particles, setParticles] = useState<Particle[]>([]);
  const [hoveredCard, setHoveredCard] = useState<number | null>(null);
  const [clickedButton, setClickedButton] = useState<string | null>(null);
  const [progressValue, setProgressValue] = useState(0);

  const getPaletteColor = (color: string, shade: 'main' | 'light' = 'main') => {
    if (
      theme.palette &&
      Object.prototype.hasOwnProperty.call(theme.palette, color) &&
      typeof (theme.palette as any)[color] === 'object' &&
      (theme.palette as any)[color][shade]
    ) {
      return (theme.palette as any)[color][shade];
    }
    // fallback
    return shade === 'main' ? '#6366f1' : '#8b5cf6';
  };

  // Initialize particles
  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;

      const newParticles: Particle[] = [];
      for (let i = 0; i < animationState.particleCount; i++) {
        newParticles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 2,
          vy: (Math.random() - 0.5) * 2,
          size: Math.random() * 3 + 1,
          color: `hsl(${Math.random() * 360}, 70%, 60%)`,
          life: Math.random() * 100,
          maxLife: 100
        });
      }
      setParticles(newParticles);
    }
  }, [animationState.particleCount]);

  // Animation loop
  useEffect(() => {
    if (!animationState.isPlaying || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Update and draw particles
      setParticles(prevParticles => 
        prevParticles.map(particle => {
          // Update position
          particle.x += particle.vx * animationState.animationSpeed;
          particle.y += particle.vy * animationState.animationSpeed;
          particle.life -= 0.5;

          // Bounce off walls
          if (particle.x <= 0 || particle.x >= canvas.width) particle.vx *= -1;
          if (particle.y <= 0 || particle.y >= canvas.height) particle.vy *= -1;

          // Reset particle if it dies
          if (particle.life <= 0) {
            particle.x = Math.random() * canvas.width;
            particle.y = Math.random() * canvas.height;
            particle.life = particle.maxLife;
            particle.color = `hsl(${Math.random() * 360}, 70%, 60%)`;
          }

          // Draw particle
          ctx.beginPath();
          ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
          ctx.fillStyle = particle.color;
          ctx.globalAlpha = particle.life / particle.maxLife;
          ctx.fill();

          return particle;
        })
      );

      // Draw connections between nearby particles
      particles.forEach((particle1, i) => {
        particles.slice(i + 1).forEach(particle2 => {
          const dx = particle1.x - particle2.x;
          const dy = particle1.y - particle2.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance < 100) {
            ctx.beginPath();
            ctx.moveTo(particle1.x, particle1.y);
            ctx.lineTo(particle2.x, particle2.y);
            ctx.strokeStyle = `rgba(255, 255, 255, ${0.1 * (1 - distance / 100)})`;
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        });
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [animationState.isPlaying, animationState.animationSpeed, particles]);

  // Progress animation
  useEffect(() => {
    const interval = setInterval(() => {
      setProgressValue(prev => (prev + 1) % 101);
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const handleAnimationToggle = () => {
    setAnimationState(prev => ({ ...prev, isPlaying: !prev.isPlaying }));
  };

  const handleSpeedChange = (speed: number) => {
    setAnimationState(prev => ({ ...prev, animationSpeed: speed }));
  };

  const handleParticleCountChange = (count: number) => {
    setAnimationState(prev => ({ ...prev, particleCount: count }));
  };

  const renderParticleCanvas = () => (
    <Box sx={{ position: 'relative', width: '100%', height: 300, borderRadius: 2, overflow: 'hidden' }}>
      <canvas
        ref={canvasRef}
        className="particle-canvas"
      />
      <Box sx={{ 
        position: 'absolute', 
        top: 16, 
        left: 16, 
        display: 'flex', 
        gap: 1 
      }}>
        <Button
          variant="contained"
          size="small"
          onClick={handleAnimationToggle}
          startIcon={animationState.isPlaying ? <Pause /> : <PlayArrow />}
          className="animation-control-button"
        >
          {animationState.isPlaying ? 'Pause' : 'Play'}
        </Button>
        <Button
          variant="outlined"
          size="small"
          onClick={() => setAnimationState(prev => ({ ...prev, particleCount: prev.particleCount + 10 }))}
          className="particle-button"
        >
          + Particles
        </Button>
      </Box>
    </Box>
  );

  const renderInteractiveCards = () => (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {[
        { title: 'Hover Effect', icon: <Star />, color: 'primary' },
        { title: 'Click Animation', icon: <Favorite />, color: 'secondary' },
        { title: 'Progress Bar', icon: <TrendingUp />, color: 'success' },
        { title: 'Loading State', icon: <Speed />, color: 'warning' }
      ].map((card, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <Fade in={true} timeout={800 + index * 200}>
            <Card
              onMouseEnter={() => setHoveredCard(index)}
              onMouseLeave={() => setHoveredCard(null)}
              onClick={() => setClickedButton(card.title)}
              className="interactive-card"
            >
              <CardContent className="card-content">
                <div className={clsx(`icon-bg-${card.color}`, hoveredCard === index ? 'icon-transform-hovered' : 'icon-transform-normal')}>
                  <div
                    className="card-icon-container"
                  >
                    {React.cloneElement(card.icon, { 
                      sx: { 
                        fontSize: 32, 
                        color: getPaletteColor(card.color, 'main')
                      } 
                    })}
                  </div>
                </div>
                <Typography variant="h6" sx={{ mb: 1, fontWeight: 600 }}>
                  {card.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {hoveredCard === index ? 'Interactive animation active!' : 'Hover to see effect'}
                </Typography>
                {card.title === 'Progress Bar' && (
                  <Box sx={{ mt: 2 }}>
                    <div className={clsx('progress-bar-container', `progress-width-${Math.round(progressValue / 5) * 5}`, `progress-bg-${card.color}`)}>
                      <div
                        className="progress-bar-fill"
                      />
                    </div>
                    <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                      {progressValue}% Complete
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Fade>
        </Grid>
      ))}
    </Grid>
  );

  const renderAnimationControls = () => (
    <ModernCard
      title="Animation Controls"
      subtitle="Customize particle effects"
      content={
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ mb: 2 }}>
              Animation Speed: {animationState.animationSpeed}x
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
              {[0.5, 1, 1.5, 2].map((speed) => (
                <Button
                  key={speed}
                  variant={animationState.animationSpeed === speed ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleSpeedChange(speed)}
                  sx={{
                    minWidth: 60,
                    ...(animationState.animationSpeed === speed && {
                      background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
                    })
                  }}
                >
                  {speed}x
                </Button>
              ))}
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="subtitle2" sx={{ mb: 2 }}>
              Particle Count: {animationState.particleCount}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 3 }}>
              {[25, 50, 75, 100].map((count) => (
                <Button
                  key={count}
                  variant={animationState.particleCount === count ? 'contained' : 'outlined'}
                  size="small"
                  onClick={() => handleParticleCountChange(count)}
                  sx={{
                    minWidth: 60,
                    ...(animationState.particleCount === count && {
                      background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
                    })
                  }}
                >
                  {count}
                </Button>
              ))}
            </Box>
          </Grid>
        </Grid>
      }
      icon={<AutoAwesome />}
      status="info"
    />
  );

  const renderLoadingAnimations = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <ModernCard
          title="Loading Spinners"
          subtitle="Various loading animations"
          content={
            <Box sx={{ display: 'flex', gap: 3, justifyContent: 'center', alignItems: 'center', py: 2 }}>
              {/* Spinning circle */}
              <Box sx={{
                width: 40,
                height: 40,
                border: '3px solid rgba(255,255,255,0.1)',
                borderTop: '3px solid #6366f1',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              
              {/* Pulsing dots */}
              <Box sx={{ display: 'flex', gap: 1 }}>
                {[0, 1, 2].map((i) => (
                  <Box
                    key={i}
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: '#6366f1',
                      animation: `pulse 1.4s ease-in-out infinite both`,
                      animationDelay: `${i * 0.16}s`
                    }}
                  />
                ))}
              </Box>
              
              {/* Bouncing bars */}
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'end' }}>
                {[0, 1, 2, 3].map((i) => (
                  <Box
                    key={i}
                    sx={{
                      width: 4,
                      height: 20,
                      backgroundColor: '#10b981',
                      animation: `bounce 1.2s ease-in-out infinite both`,
                      animationDelay: `${i * 0.1}s`
                    }}
                  />
                ))}
              </Box>
            </Box>
          }
          icon={<Speed />}
          status="info"
        />
      </Grid>
      
      <Grid item xs={12} md={6}>
        <ModernCard
          title="Success Animations"
          subtitle="Celebration effects"
          content={
            <Box sx={{ textAlign: 'center', py: 2 }}>
              <Box sx={{ 
                display: 'flex', 
                justifyContent: 'center', 
                alignItems: 'center',
                mb: 2
              }}>
                <Box sx={{
                  width: 60,
                  height: 60,
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  animation: 'successPulse 2s ease-in-out infinite',
                  position: 'relative'
                }}>
                  <Typography variant="h4" sx={{ color: 'white', fontWeight: 'bold' }}>
                    ✓
                  </Typography>
                  {/* Success particles */}
                  {[0, 1, 2, 3, 4].map((i) => (
                    <Box
                      key={i}
                      sx={{
                        position: 'absolute',
                        width: 4,
                        height: 4,
                        borderRadius: '50%',
                        backgroundColor: '#10b981',
                        animation: `successParticle 1s ease-out infinite`,
                        animationDelay: `${i * 0.1}s`,
                        transform: `rotate(${i * 72}deg) translateY(-40px)`
                      }}
                    />
                  ))}
                </Box>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Task completed successfully!
              </Typography>
            </Box>
          }
          icon={<FlashOn />}
          status="success"
        />
      </Grid>
    </Grid>
  );

  return (
    <Fade in={true} timeout={800}>
      <Box sx={{ p: { xs: 2, md: 3 } }}>
        <Typography 
          variant="h4" 
          sx={{ 
            mb: 4, 
            fontWeight: 700,
            background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Advanced Animations
        </Typography>

        {/* Particle Animation */}
        <ModernCard
          title="AI Particle Playground"
          subtitle="Interactive particle system"
          content={renderParticleCanvas()}
          icon={<Psychology />}
          status="info"
        />

        {/* Interactive Cards */}
        <Box sx={{ my: 4 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Interactive Elements
          </Typography>
          {renderInteractiveCards()}
        </Box>

        {/* Animation Controls */}
        <Box sx={{ mb: 4 }}>
          {renderAnimationControls()}
        </Box>

        {/* Loading Animations */}
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
            Loading & Success Animations
          </Typography>
          {renderLoadingAnimations()}
        </Box>

        {/* Clicked Button Feedback */}
        {clickedButton && (
          <Fade in={true}>
            <Box sx={{ 
              position: 'fixed', 
              top: '50%', 
              left: '50%', 
              transform: 'translate(-50%, -50%)',
              zIndex: 9999,
              pointerEvents: 'none'
            }}>
              <Box sx={{
                background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
                color: 'white',
                px: 3,
                py: 2,
                borderRadius: 2,
                boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                animation: 'fadeInOut 2s ease-in-out'
              }}>
                <Typography variant="h6">
                  {clickedButton} clicked!
                </Typography>
              </Box>
            </Box>
          </Fade>
        )}
      </Box>
    </Fade>
  );
};

export default AdvancedAnimations; 