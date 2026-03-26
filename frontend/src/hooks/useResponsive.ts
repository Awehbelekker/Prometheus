/**
 * useResponsive Hook
 * Responsive design utilities for mobile-first development
 */

import { useTheme, useMediaQuery, Breakpoint } from '@mui/material';
import { useState, useEffect } from 'react';

/**
 * Hook to check if screen is at or above a breakpoint
 */
export const useBreakpoint = (breakpoint: Breakpoint): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.up(breakpoint));
};

/**
 * Hook to get current breakpoint
 */
export const useCurrentBreakpoint = (): Breakpoint => {
  const theme = useTheme();
  const isXl = useMediaQuery(theme.breakpoints.up('xl'));
  const isLg = useMediaQuery(theme.breakpoints.up('lg'));
  const isMd = useMediaQuery(theme.breakpoints.up('md'));
  const isSm = useMediaQuery(theme.breakpoints.up('sm'));

  if (isXl) return 'xl';
  if (isLg) return 'lg';
  if (isMd) return 'md';
  if (isSm) return 'sm';
  return 'xs';
};

/**
 * Hook to check if device is mobile
 */
export const useIsMobile = (): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.down('md'));
};

/**
 * Hook to check if device is tablet
 */
export const useIsTablet = (): boolean => {
  const theme = useTheme();
  const isMd = useMediaQuery(theme.breakpoints.up('md'));
  const isLg = useMediaQuery(theme.breakpoints.down('lg'));
  return isMd && isLg;
};

/**
 * Hook to check if device is desktop
 */
export const useIsDesktop = (): boolean => {
  const theme = useTheme();
  return useMediaQuery(theme.breakpoints.up('lg'));
};

/**
 * Hook to get window dimensions
 */
export const useWindowSize = () => {
  const [windowSize, setWindowSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
};

/**
 * Hook to check if device is in portrait mode
 */
export const useIsPortrait = (): boolean => {
  const { width, height } = useWindowSize();
  return height > width;
};

/**
 * Hook to check if device is in landscape mode
 */
export const useIsLandscape = (): boolean => {
  const { width, height } = useWindowSize();
  return width > height;
};

/**
 * Hook to get responsive value based on breakpoint
 */
export const useResponsiveValue = <T,>(values: {
  xs?: T;
  sm?: T;
  md?: T;
  lg?: T;
  xl?: T;
}): T | undefined => {
  const breakpoint = useCurrentBreakpoint();

  // Return value for current breakpoint or fallback to smaller breakpoints
  if (breakpoint === 'xl' && values.xl !== undefined) return values.xl;
  if (breakpoint === 'lg' && values.lg !== undefined) return values.lg;
  if (breakpoint === 'md' && values.md !== undefined) return values.md;
  if (breakpoint === 'sm' && values.sm !== undefined) return values.sm;
  if (values.xs !== undefined) return values.xs;

  // Fallback to largest available value
  return values.xl ?? values.lg ?? values.md ?? values.sm ?? values.xs;
};

/**
 * Hook to check if touch device
 */
export const useIsTouchDevice = (): boolean => {
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    setIsTouch(
      'ontouchstart' in window ||
      navigator.maxTouchPoints > 0 ||
      (navigator as any).msMaxTouchPoints > 0
    );
  }, []);

  return isTouch;
};

/**
 * Hook to get device pixel ratio
 */
export const useDevicePixelRatio = (): number => {
  const [dpr, setDpr] = useState(window.devicePixelRatio || 1);

  useEffect(() => {
    const handleChange = () => {
      setDpr(window.devicePixelRatio || 1);
    };

    const mediaQuery = window.matchMedia(`(resolution: ${window.devicePixelRatio}dppx)`);
    mediaQuery.addEventListener('change', handleChange);

    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return dpr;
};

/**
 * Comprehensive responsive hook
 */
export const useResponsive = () => {
  const breakpoint = useCurrentBreakpoint();
  const isMobile = useIsMobile();
  const isTablet = useIsTablet();
  const isDesktop = useIsDesktop();
  const windowSize = useWindowSize();
  const isPortrait = useIsPortrait();
  const isLandscape = useIsLandscape();
  const isTouchDevice = useIsTouchDevice();
  const devicePixelRatio = useDevicePixelRatio();

  return {
    breakpoint,
    isMobile,
    isTablet,
    isDesktop,
    windowSize,
    isPortrait,
    isLandscape,
    isTouchDevice,
    devicePixelRatio,
    // Convenience flags
    isSmallScreen: isMobile,
    isMediumScreen: isTablet,
    isLargeScreen: isDesktop,
    // Breakpoint checks
    isXs: breakpoint === 'xs',
    isSm: breakpoint === 'sm',
    isMd: breakpoint === 'md',
    isLg: breakpoint === 'lg',
    isXl: breakpoint === 'xl'
  };
};

export default useResponsive;

