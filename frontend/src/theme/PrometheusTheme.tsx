/**
 * PROMETHEUS Theme Provider
 * Enhanced Material-UI theme with design system
 */

import React, { createContext, useContext, useState, useMemo } from 'react';
import { ThemeProvider as MuiThemeProvider, createTheme, Theme } from '@mui/material/styles';
import { designSystem } from './designSystem';

type ThemeMode = 'dark' | 'light';

interface PrometheusThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
}

const PrometheusThemeContext = createContext<PrometheusThemeContextType>({
  mode: 'dark',
  toggleTheme: () => {}
});

export const usePrometheusTheme = () => useContext(PrometheusThemeContext);

export const PrometheusThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>('dark');

  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'dark' ? 'light' : 'dark'));
  };

  const theme = useMemo(() => {
    return createTheme({
      palette: {
        mode,
        primary: {
          main: designSystem.colors.primary.main,
          light: designSystem.colors.primary.light,
          dark: designSystem.colors.primary.dark,
          contrastText: designSystem.colors.primary.contrastText
        },
        secondary: {
          main: designSystem.colors.secondary.main,
          light: designSystem.colors.secondary.light,
          dark: designSystem.colors.secondary.dark,
          contrastText: designSystem.colors.secondary.contrastText
        },
        success: {
          main: designSystem.colors.success.main,
          light: designSystem.colors.success.light,
          dark: designSystem.colors.success.dark,
          contrastText: designSystem.colors.success.contrastText
        },
        warning: {
          main: designSystem.colors.warning.main,
          light: designSystem.colors.warning.light,
          dark: designSystem.colors.warning.dark,
          contrastText: designSystem.colors.warning.contrastText
        },
        error: {
          main: designSystem.colors.error.main,
          light: designSystem.colors.error.light,
          dark: designSystem.colors.error.dark,
          contrastText: designSystem.colors.error.contrastText
        },
        info: {
          main: designSystem.colors.info.main,
          light: designSystem.colors.info.light,
          dark: designSystem.colors.info.dark,
          contrastText: designSystem.colors.info.contrastText
        },
        background: {
          default: designSystem.colors.background.default,
          paper: designSystem.colors.background.paper
        },
        text: {
          primary: designSystem.colors.text.primary,
          secondary: designSystem.colors.text.secondary,
          disabled: designSystem.colors.text.disabled
        }
      },
      typography: {
        fontFamily: designSystem.typography.fontFamily.primary,
        fontSize: designSystem.typography.fontSize.md,
        h1: {
          fontSize: designSystem.typography.fontSize.xxxl,
          fontWeight: designSystem.typography.fontWeight.bold,
          lineHeight: designSystem.typography.lineHeight.tight
        },
        h2: {
          fontSize: designSystem.typography.fontSize.xxl,
          fontWeight: designSystem.typography.fontWeight.bold,
          lineHeight: designSystem.typography.lineHeight.tight
        },
        h3: {
          fontSize: designSystem.typography.fontSize.xl,
          fontWeight: designSystem.typography.fontWeight.semibold,
          lineHeight: designSystem.typography.lineHeight.normal
        },
        h4: {
          fontSize: designSystem.typography.fontSize.lg,
          fontWeight: designSystem.typography.fontWeight.semibold,
          lineHeight: designSystem.typography.lineHeight.normal
        },
        h5: {
          fontSize: designSystem.typography.fontSize.md,
          fontWeight: designSystem.typography.fontWeight.medium,
          lineHeight: designSystem.typography.lineHeight.normal
        },
        h6: {
          fontSize: designSystem.typography.fontSize.sm,
          fontWeight: designSystem.typography.fontWeight.medium,
          lineHeight: designSystem.typography.lineHeight.normal
        },
        body1: {
          fontSize: designSystem.typography.fontSize.md,
          lineHeight: designSystem.typography.lineHeight.normal
        },
        body2: {
          fontSize: designSystem.typography.fontSize.sm,
          lineHeight: designSystem.typography.lineHeight.normal
        },
        button: {
          fontSize: designSystem.typography.fontSize.sm,
          fontWeight: designSystem.typography.fontWeight.semibold,
          textTransform: 'none'
        }
      },
      spacing: designSystem.spacing.sm,
      shape: {
        borderRadius: designSystem.borderRadius.md
      },
      shadows: [
        'none',
        designSystem.shadows.sm,
        designSystem.shadows.md,
        designSystem.shadows.lg,
        designSystem.shadows.xl,
        designSystem.shadows.xxl,
        designSystem.shadows.sm,
        designSystem.shadows.md,
        designSystem.shadows.lg,
        designSystem.shadows.xl,
        designSystem.shadows.xxl,
        designSystem.shadows.sm,
        designSystem.shadows.md,
        designSystem.shadows.lg,
        designSystem.shadows.xl,
        designSystem.shadows.xxl,
        designSystem.shadows.sm,
        designSystem.shadows.md,
        designSystem.shadows.lg,
        designSystem.shadows.xl,
        designSystem.shadows.xxl,
        designSystem.shadows.sm,
        designSystem.shadows.md,
        designSystem.shadows.lg,
        designSystem.shadows.xxl
      ],
      transitions: {
        duration: {
          shortest: designSystem.transitions.duration.fastest,
          shorter: designSystem.transitions.duration.fast,
          short: designSystem.transitions.duration.normal,
          standard: designSystem.transitions.duration.normal,
          complex: designSystem.transitions.duration.slow,
          enteringScreen: designSystem.transitions.duration.normal,
          leavingScreen: designSystem.transitions.duration.fast
        },
        easing: {
          easeInOut: designSystem.transitions.easing.easeInOut,
          easeOut: designSystem.transitions.easing.easeOut,
          easeIn: designSystem.transitions.easing.easeIn,
          sharp: designSystem.transitions.easing.sharp
        }
      },
      breakpoints: {
        values: designSystem.breakpoints
      },
      zIndex: designSystem.zIndex,
      components: {
        MuiButton: {
          styleOverrides: {
            root: {
              borderRadius: designSystem.borderRadius.md,
              padding: `${designSystem.spacing.sm}px ${designSystem.spacing.md}px`,
              transition: `all ${designSystem.transitions.duration.normal}ms ${designSystem.transitions.easing.easeInOut}`,
              '&:hover': {
                transform: 'translateY(-2px)',
                boxShadow: designSystem.shadows.md
              }
            },
            contained: {
              boxShadow: designSystem.shadows.sm
            }
          }
        },
        MuiCard: {
          styleOverrides: {
            root: {
              borderRadius: designSystem.borderRadius.lg,
              background: designSystem.gradients.card,
              border: '1px solid rgba(255, 255, 255, 0.1)',
              transition: `all ${designSystem.transitions.duration.normal}ms ${designSystem.transitions.easing.easeInOut}`,
              '&:hover': {
                borderColor: 'rgba(0, 212, 255, 0.3)',
                transform: 'translateY(-2px)',
                boxShadow: designSystem.shadows.lg
              }
            }
          }
        },
        MuiChip: {
          styleOverrides: {
            root: {
              borderRadius: designSystem.borderRadius.full,
              fontWeight: designSystem.typography.fontWeight.medium
            }
          }
        },
        MuiTextField: {
          styleOverrides: {
            root: {
              '& .MuiOutlinedInput-root': {
                borderRadius: designSystem.borderRadius.md,
                '&:hover fieldset': {
                  borderColor: designSystem.colors.primary.main
                }
              }
            }
          }
        },
        MuiPaper: {
          styleOverrides: {
            root: {
              backgroundImage: 'none'
            }
          }
        }
      }
    });
  }, [mode]);

  return (
    <PrometheusThemeContext.Provider value={{ mode, toggleTheme }}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </PrometheusThemeContext.Provider>
  );
};

export default PrometheusThemeProvider;

