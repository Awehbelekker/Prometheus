/**
 * PROMETHEUS Design System
 * Centralized design tokens and theme configuration
 */

export const colors = {
  // Primary Colors
  primary: {
    main: '#00d4ff',
    light: '#33ddff',
    dark: '#0099cc',
    contrastText: '#000000'
  },
  
  // Secondary Colors
  secondary: {
    main: '#ff6b35',
    light: '#ff8c5f',
    dark: '#cc5529',
    contrastText: '#ffffff'
  },
  
  // Success Colors
  success: {
    main: '#4caf50',
    light: '#6fbf73',
    dark: '#388e3c',
    contrastText: '#ffffff'
  },
  
  // Warning Colors
  warning: {
    main: '#ff9800',
    light: '#ffb333',
    dark: '#cc7a00',
    contrastText: '#000000'
  },
  
  // Error Colors
  error: {
    main: '#f44336',
    light: '#f6685e',
    dark: '#c3352b',
    contrastText: '#ffffff'
  },
  
  // Info Colors
  info: {
    main: '#2196f3',
    light: '#4dabf5',
    dark: '#1976d2',
    contrastText: '#ffffff'
  },
  
  // Neutral Colors
  neutral: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121'
  },
  
  // Background Colors
  background: {
    default: '#0a0a0a',
    paper: '#1a1a1a',
    elevated: '#2a2a2a',
    overlay: 'rgba(0, 0, 0, 0.8)'
  },
  
  // Text Colors
  text: {
    primary: '#ffffff',
    secondary: '#aaaaaa',
    disabled: '#666666',
    hint: '#888888'
  },
  
  // Gamification Colors
  gamification: {
    xp: '#ffd700',
    level: '#00d4ff',
    achievement: '#ff9800',
    badge: '#9c27b0',
    streak: '#ff6b35'
  },
  
  // Rarity Colors
  rarity: {
    common: '#9e9e9e',
    uncommon: '#4caf50',
    rare: '#2196f3',
    epic: '#9c27b0',
    legendary: '#ff9800'
  },
  
  // Trading Colors
  trading: {
    profit: '#4caf50',
    loss: '#f44336',
    neutral: '#9e9e9e',
    buy: '#00d4ff',
    sell: '#ff6b35'
  }
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48
};

export const typography = {
  fontFamily: {
    primary: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    monospace: '"Fira Code", "Courier New", monospace'
  },
  fontSize: {
    xs: 12,
    sm: 14,
    md: 16,
    lg: 18,
    xl: 20,
    xxl: 24,
    xxxl: 32
  },
  fontWeight: {
    light: 300,
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700
  },
  lineHeight: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.8
  }
};

export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999
};

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
  xxl: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  glow: {
    primary: '0 0 20px rgba(0, 212, 255, 0.5)',
    secondary: '0 0 20px rgba(255, 107, 53, 0.5)',
    success: '0 0 20px rgba(76, 175, 80, 0.5)',
    error: '0 0 20px rgba(244, 67, 54, 0.5)'
  }
};

export const transitions = {
  duration: {
    fastest: 100,
    fast: 200,
    normal: 300,
    slow: 500,
    slowest: 700
  },
  easing: {
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    sharp: 'cubic-bezier(0.4, 0, 0.6, 1)'
  }
};

export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920
};

export const zIndex = {
  mobileStepper: 1000,
  speedDial: 1050,
  appBar: 1100,
  drawer: 1200,
  modal: 1300,
  snackbar: 1400,
  tooltip: 1500
};

export const gradients = {
  primary: 'linear-gradient(45deg, #00d4ff, #0099cc)',
  secondary: 'linear-gradient(45deg, #ff6b35, #cc5529)',
  success: 'linear-gradient(45deg, #4caf50, #388e3c)',
  error: 'linear-gradient(45deg, #f44336, #c3352b)',
  dark: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 50%, #2a2a2a 100%)',
  card: 'linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(40, 40, 40, 0.95) 100%)'
};

export const animations = {
  fadeIn: {
    from: { opacity: 0 },
    to: { opacity: 1 }
  },
  slideUp: {
    from: { transform: 'translateY(20px)', opacity: 0 },
    to: { transform: 'translateY(0)', opacity: 1 }
  },
  slideDown: {
    from: { transform: 'translateY(-20px)', opacity: 0 },
    to: { transform: 'translateY(0)', opacity: 1 }
  },
  scaleIn: {
    from: { transform: 'scale(0.9)', opacity: 0 },
    to: { transform: 'scale(1)', opacity: 1 }
  },
  pulse: {
    '0%, 100%': { transform: 'scale(1)' },
    '50%': { transform: 'scale(1.05)' }
  },
  glow: {
    '0%, 100%': { boxShadow: '0 0 5px rgba(0, 212, 255, 0.5)' },
    '50%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.8)' }
  }
};

export const designSystem = {
  colors,
  spacing,
  typography,
  borderRadius,
  shadows,
  transitions,
  breakpoints,
  zIndex,
  gradients,
  animations
};

export default designSystem;

