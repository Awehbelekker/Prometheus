import React from 'react';
import { Box, Card, CardContent, Typography, Chip, Fade } from '@mui/material';

interface ModernCardProps {
  title: string;
  subtitle?: string;
  content: React.ReactNode;
  icon?: React.ReactNode;
  status?: 'success' | 'warning' | 'error' | 'info';
  onClick?: () => void;
  elevation?: number;
  children?: React.ReactNode;
}

const ModernCard: React.FC<ModernCardProps> = ({
  title,
  subtitle,
  content,
  icon,
  status,
  onClick,
  elevation = 1,
  children
}) => {
  const statusColors = {
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6'
  };

  return (
    <Fade in={true} timeout={500}>
      <Card
        onClick={onClick}
        sx={{
          background: 'rgba(26, 26, 46, 0.8)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: 3,
          boxShadow: `0 ${elevation * 4}px ${elevation * 8}px -${elevation * 2}px rgba(0, 0, 0, 0.2)`,
          transition: 'all 0.3s ease',
          cursor: onClick ? 'pointer' : 'default',
          position: 'relative',
          overflow: 'hidden',
          '&:hover': onClick ? {
            transform: 'translateY(-4px)',
            boxShadow: `0 ${(elevation + 2) * 4}px ${(elevation + 2) * 8}px -${(elevation + 2) * 2}px rgba(0, 0, 0, 0.3)`,
            borderColor: 'rgba(255, 255, 255, 0.12)'
          } : {},
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '2px',
            background: status ? `linear-gradient(90deg, ${statusColors[status]} 0%, transparent 100%)` : 'linear-gradient(90deg, #6366f1 0%, #10b981 100%)',
            opacity: 0.8
          }
        }}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 2 }}>
            {icon && (
              <Box
                sx={{
                  p: 1,
                  borderRadius: 2,
                  backgroundColor: 'rgba(99, 102, 241, 0.1)',
                  color: 'primary.main',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                {icon}
              </Box>
            )}
            <Box sx={{ flex: 1 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 600,
                  color: 'text.primary',
                  mb: subtitle ? 0.5 : 0
                }}
              >
                {title}
              </Typography>
              {subtitle && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 1 }}
                >
                  {subtitle}
                </Typography>
              )}
            </Box>
            {status && (
              <Chip
                label={status}
                size="small"
                sx={{
                  backgroundColor: `${statusColors[status]}20`,
                  color: statusColors[status],
                  fontWeight: 500,
                  textTransform: 'capitalize'
                }}
              />
            )}
          </Box>
          
          <Box sx={{ color: 'text.primary' }}>
            {content}
          </Box>
          
          {children}
        </CardContent>
      </Card>
    </Fade>
  );
};

export default ModernCard; 