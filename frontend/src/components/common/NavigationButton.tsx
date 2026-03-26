import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, alpha } from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';

interface NavigationButtonProps {
  to: string;
  icon?: React.ComponentType<any>;
  label: string;
  variant?: 'text' | 'outlined' | 'contained';
  color?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onClick?: () => void;
  sx?: any;
}

/**
 * Standardized Navigation Button Component
 * 
 * Provides consistent navigation styling and behavior across all dashboards
 */
const NavigationButton: React.FC<NavigationButtonProps> = ({
  to,
  icon: Icon,
  label,
  variant = 'outlined',
  color = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
  sx = {}
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    }
    navigate(to);
  };

  const getColorStyles = () => {
    switch (color) {
      case 'primary':
        return {
          color: '#00d4ff',
          borderColor: '#00d4ff',
          '&:hover': {
            backgroundColor: alpha('#00d4ff', 0.1),
            borderColor: '#00d4ff'
          }
        };
      case 'secondary':
        return {
          color: '#9c27b0',
          borderColor: '#9c27b0',
          '&:hover': {
            backgroundColor: alpha('#9c27b0', 0.1),
            borderColor: '#9c27b0'
          }
        };
      case 'success':
        return {
          color: '#4caf50',
          borderColor: '#4caf50',
          '&:hover': {
            backgroundColor: alpha('#4caf50', 0.1),
            borderColor: '#4caf50'
          }
        };
      case 'warning':
        return {
          color: '#ff9800',
          borderColor: '#ff9800',
          '&:hover': {
            backgroundColor: alpha('#ff9800', 0.1),
            borderColor: '#ff9800'
          }
        };
      case 'error':
        return {
          color: '#f44336',
          borderColor: '#f44336',
          '&:hover': {
            backgroundColor: alpha('#f44336', 0.1),
            borderColor: '#f44336'
          }
        };
      default:
        return {
          color: '#00d4ff',
          borderColor: '#00d4ff',
          '&:hover': {
            backgroundColor: alpha('#00d4ff', 0.1),
            borderColor: '#00d4ff'
          }
        };
    }
  };

  const colorStyles = getColorStyles();
  const baseStyles = {
    fontSize: size === 'small' ? '0.75rem' : size === 'large' ? '1rem' : '0.875rem',
    px: size === 'small' ? 2 : size === 'large' ? 4 : 3,
    py: size === 'small' ? 1 : size === 'large' ? 1.5 : 1.25,
    borderRadius: 2,
    fontWeight: 600,
    textTransform: 'none' as const,
    transition: 'all 0.2s ease-in-out',
    color: colorStyles.color,
    borderColor: colorStyles.borderColor,
    '&:hover': {
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 12px rgba(0, 212, 255, 0.3)',
      backgroundColor: colorStyles['&:hover']?.backgroundColor,
      borderColor: colorStyles['&:hover']?.borderColor || colorStyles.borderColor
    },
    ...sx
  };

  return (
    <Button
      variant={variant}
      size={size}
      startIcon={Icon ? <Icon /> : undefined}
      onClick={handleClick}
      disabled={disabled}
      sx={baseStyles}
    >
      {label}
    </Button>
  );
};

export default NavigationButton;
