import React, { useEffect, useState, useRef } from 'react';
import { Typography, Box } from '@mui/material';
import { motion, useSpring, useTransform } from 'framer-motion';

interface AnimatedCounterProps {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  color?: string;
  variant?: any;
  component?: any;
  showTrend?: boolean;
  previousValue?: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({
  value,
  duration = 2000,
  prefix = '',
  suffix = '',
  decimals = 2,
  color = 'inherit',
  variant = 'h4',
  component = 'span',
  showTrend = false,
  previousValue
}) => {
  const [displayValue, setDisplayValue] = useState(value);
  const prevValueRef = useRef(value);
  const [trend, setTrend] = useState<'up' | 'down' | 'neutral'>('neutral');

  // Framer Motion spring animation
  const spring = useSpring(value, {
    stiffness: 100,
    damping: 30,
    mass: 1,
  });

  const animatedValue = useTransform(spring, (latest) => {
    return latest.toFixed(decimals);
  });

  useEffect(() => {
    spring.set(value);
    
    // Determine trend
    if (showTrend && previousValue !== undefined) {
      if (value > previousValue) {
        setTrend('up');
      } else if (value < previousValue) {
        setTrend('down');
      } else {
        setTrend('neutral');
      }
    }
    
    prevValueRef.current = value;
  }, [value, spring, showTrend, previousValue]);

  const getTrendColor = () => {
    switch (trend) {
      case 'up': return '#4caf50';
      case 'down': return '#f44336';
      default: return color;
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      default: return '';
    }
  };

  return (
    <Box display="flex" alignItems="center" gap={1}>
      <motion.div
        key={value}
        initial={{ scale: 1.1, opacity: 0.8 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.3 }}
      >
        <Typography
          variant={variant}
          component={component}
          sx={{
            color: getTrendColor(),
            fontWeight: 'bold',
            transition: 'color 0.3s ease',
          }}
        >
          {prefix}
          <motion.span>
            {animatedValue}
          </motion.span>
          {suffix}
        </Typography>
      </motion.div>
      
      {showTrend && trend !== 'neutral' && (
        <motion.span
          initial={{ scale: 0, rotate: 180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.5, type: "spring" }}
          style={{ fontSize: '1.2em' }}
        >
          {getTrendIcon()}
        </motion.span>
      )}
    </Box>
  );
};

// Specialized counter for profit/loss
export const ProfitCounter: React.FC<{
  value: number;
  previousValue?: number;
  showTrend?: boolean;
}> = ({ value, previousValue, showTrend = true }) => {
  const isProfit = value >= 0;
  
  return (
    <AnimatedCounter
      value={Math.abs(value)}
      prefix={isProfit ? '+$' : '-$'}
      color={isProfit ? '#4caf50' : '#f44336'}
      variant="h3"
      decimals={2}
      showTrend={showTrend}
      previousValue={previousValue}
    />
  );
};

// Specialized counter for percentages
export const PercentageCounter: React.FC<{
  value: number;
  previousValue?: number;
  showTrend?: boolean;
}> = ({ value, previousValue, showTrend = true }) => {
  return (
    <AnimatedCounter
      value={value}
      suffix="%"
      variant="h4"
      decimals={1}
      showTrend={showTrend}
      previousValue={previousValue}
      color="#00d4ff"
    />
  );
};

// Specialized counter for large numbers (trades, etc.)
export const NumberCounter: React.FC<{
  value: number;
  previousValue?: number;
  showTrend?: boolean;
  label?: string;
}> = ({ value, previousValue, showTrend = true, label }) => {
  return (
    <Box textAlign="center">
      <AnimatedCounter
        value={value}
        variant="h4"
        decimals={0}
        showTrend={showTrend}
        previousValue={previousValue}
        color="#ff6b35"
      />
      {label && (
        <Typography variant="caption" color="textSecondary">
          {label}
        </Typography>
      )}
    </Box>
  );
};
