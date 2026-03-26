import React from 'react';
import { Box, Typography, alpha } from '@mui/material';
import { Psychology, AutoAwesome, TrendingUp } from '@mui/icons-material';

/**
 * 🔥 PROMETHEUS LOGO SHOWCASE
 * Professional logo with NeuroForge™ branding using original logo
 */

interface PrometheusLogoProps {
  variant?: 'full' | 'compact' | 'icon';
  size?: 'small' | 'medium' | 'large';
  animated?: boolean;
}

const PrometheusLogo: React.FC<PrometheusLogoProps> = ({ 
  variant = 'full', 
  size = 'medium',
  animated = true 
}) => {
  const getSizes = () => {
    switch (size) {
      case 'small':
        return { logoSize: 40, titleSize: '1.2rem', subtitleSize: '0.7rem', iconSize: 16 };
      case 'large':
        return { logoSize: 80, titleSize: '2.5rem', subtitleSize: '1rem', iconSize: 32 };
      default:
        return { logoSize: 56, titleSize: '1.8rem', subtitleSize: '0.85rem', iconSize: 24 };
    }
  };

  const sizes = getSizes();

  if (variant === 'icon') {
    return (
      <Box sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: sizes.logoSize,
        height: sizes.logoSize,
        borderRadius: 2,
        animation: animated ? 'logoGlow 3s ease-in-out infinite' : 'none',
        background: 'transparent !important',
        backgroundColor: 'transparent !important',
        '&:hover': {
          transform: animated ? 'scale(1.05)' : 'none'
        },
        transition: 'all 0.3s ease'
      }}>
        <img
          src="/LogoNew.png"
          alt="Prometheus Logo"
          width={sizes.logoSize}
          height={sizes.logoSize}
          style={{
            objectFit: 'contain',
            filter: 'drop-shadow(0 4px 12px rgba(0, 212, 255, 0.3))',
            animation: animated ? 'iconPulse 2s ease-in-out infinite' : 'none',
            background: 'transparent',
            backgroundColor: 'transparent'
          }}
        />
      </Box>
    );
  }

  if (variant === 'compact') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box sx={{
          position: 'relative',
          animation: animated ? 'logoGlow 3s ease-in-out infinite' : 'none'
        }}>
          <img
            src="/LogoNew.png"
            alt="Prometheus Logo"
            width={sizes.logoSize}
            height={sizes.logoSize}
            style={{
              objectFit: 'contain',
              filter: 'drop-shadow(0 2px 8px rgba(0, 212, 255, 0.3))',
              transition: 'all 0.3s ease',
              background: 'transparent',
              backgroundColor: 'transparent'
            }}
          />
        </Box>
        <Typography variant="h6" sx={{
          fontWeight: 800,
          fontSize: sizes.titleSize,
          background: 'linear-gradient(45deg, #00d4ff, #ff6b35)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '0.5px'
        }}>
          PROMETHEUS
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{
      display: 'flex',
      alignItems: 'center',
      gap: 3,
      position: 'relative'
    }}>
      {/* Clean flame logo - no background needed */}

      {/* Original Logo with Enhanced Effects */}
      <Box sx={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2
      }}>
        {/* Clean flame logo - no glow ring needed */}

        {/* Bold Flame Logo */}
        <img
          src="/LogoNew.png"
          alt="Prometheus Logo"
          width={sizes.logoSize}
          height={sizes.logoSize}
          style={{
            objectFit: 'contain',
            filter: 'contrast(1.3) saturate(1.4) brightness(1.1) drop-shadow(0 4px 16px rgba(255, 107, 53, 0.6)) drop-shadow(0 0 20px rgba(255, 107, 53, 0.3))',
            animation: animated ? 'logoGlow 3s ease-in-out infinite' : 'none',
            transition: 'all 0.3s ease',
            zIndex: 2,
            position: 'relative',
            background: 'transparent',
            backgroundColor: 'transparent'
          }}
        />

        {/* Floating Elements */}
        {animated && (
          <>
            <Psychology sx={{
              position: 'absolute',
              top: -8,
              right: -8,
              fontSize: sizes.iconSize,
              color: '#9c27b0',
              animation: 'floatElement1 3s ease-in-out infinite',
              filter: 'drop-shadow(0 2px 8px rgba(156, 39, 176, 0.5))'
            }} />

            <AutoAwesome sx={{
              position: 'absolute',
              bottom: -8,
              left: -8,
              fontSize: sizes.iconSize,
              color: '#ff6b35',
              animation: 'floatElement2 3.5s ease-in-out infinite',
              filter: 'drop-shadow(0 2px 8px rgba(255, 107, 53, 0.5))'
            }} />
          </>
        )}
      </Box>

      {/* Text Content */}
      <Box>
        <Typography variant="h4" sx={{
          fontWeight: 900,
          fontSize: sizes.titleSize,
          background: 'linear-gradient(45deg, #00d4ff 0%, #ff6b35 50%, #9c27b0 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '1px',
          lineHeight: 1,
          textShadow: '0 0 20px rgba(0, 212, 255, 0.3)',
          animation: animated ? 'textShimmer 4s ease-in-out infinite' : 'none'
        }}>
          PROMETHEUS
        </Typography>
        
        <Typography variant="subtitle1" sx={{
          fontSize: sizes.subtitleSize,
          color: '#aaa',
          fontWeight: 600,
          letterSpacing: '1.5px',
          mt: 0.5,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5
        }}>
          WITH
          <span style={{
            background: 'linear-gradient(45deg, #00d4ff, #9c27b0)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            fontWeight: 700
          }}>
            NeuroForge™
          </span>
        </Typography>
      </Box>

      {/* CSS Animations */}
      <style>{`
        @keyframes logoGlow {
          0%, 100% { 
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
          }
          50% { 
            box-shadow: 0 0 40px rgba(0, 212, 255, 0.6), 0 0 60px rgba(255, 107, 53, 0.3);
          }
        }

        @keyframes iconPulse {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.1); }
        }

        @keyframes ringRotate {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes floatElement1 {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-8px) rotate(180deg); }
        }

        @keyframes floatElement2 {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-6px) rotate(-180deg); }
        }

        @keyframes textShimmer {
          0%, 100% { 
            background: linear-gradient(45deg, #00d4ff 0%, #ff6b35 50%, #9c27b0 100%);
            -webkit-background-clip: text;
          }
          50% { 
            background: linear-gradient(45deg, #9c27b0 0%, #00d4ff 50%, #ff6b35 100%);
            -webkit-background-clip: text;
          }
        }

        @keyframes backgroundPulse {
          0%, 100% { opacity: 0.3; }
          50% { opacity: 0.6; }
        }
      `}</style>
    </Box>
  );
};

export default PrometheusLogo;
