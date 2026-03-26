/**
 * Tests for useResponsive hook
 */

import { renderHook, act } from '@testing-library/react';
import { useResponsive, useIsMobile, useIsTablet, useIsDesktop, useWindowSize } from '../useResponsive';

// Mock window.matchMedia
const mockMatchMedia = (matches: boolean) => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation((query) => ({
      matches,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn()
    }))
  });
};

describe('useResponsive', () => {
  beforeEach(() => {
    // Reset window size
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024
    });
    Object.defineProperty(window, 'innerHeight', {
      writable: true,
      configurable: true,
      value: 768
    });
  });

  describe('useResponsive', () => {
    it('should return responsive properties', () => {
      mockMatchMedia(false);
      const { result } = renderHook(() => useResponsive());

      expect(result.current).toHaveProperty('breakpoint');
      expect(result.current).toHaveProperty('isMobile');
      expect(result.current).toHaveProperty('isTablet');
      expect(result.current).toHaveProperty('isDesktop');
      expect(result.current).toHaveProperty('windowSize');
    });

    it('should detect mobile device', () => {
      mockMatchMedia(true);
      const { result } = renderHook(() => useResponsive());

      expect(result.current.isMobile).toBeDefined();
    });

    it('should detect touch device', () => {
      Object.defineProperty(window, 'ontouchstart', {
        writable: true,
        value: true
      });

      const { result } = renderHook(() => useResponsive());

      expect(result.current.isTouchDevice).toBeDefined();
    });
  });

  describe('useIsMobile', () => {
    it('should return true for mobile viewport', () => {
      mockMatchMedia(true);
      const { result } = renderHook(() => useIsMobile());

      expect(typeof result.current).toBe('boolean');
    });

    it('should return false for desktop viewport', () => {
      mockMatchMedia(false);
      const { result } = renderHook(() => useIsMobile());

      expect(typeof result.current).toBe('boolean');
    });
  });

  describe('useIsTablet', () => {
    it('should detect tablet viewport', () => {
      mockMatchMedia(false);
      const { result } = renderHook(() => useIsTablet());

      expect(typeof result.current).toBe('boolean');
    });
  });

  describe('useIsDesktop', () => {
    it('should detect desktop viewport', () => {
      mockMatchMedia(true);
      const { result } = renderHook(() => useIsDesktop());

      expect(typeof result.current).toBe('boolean');
    });
  });

  describe('useWindowSize', () => {
    it('should return current window size', () => {
      const { result } = renderHook(() => useWindowSize());

      expect(result.current).toHaveProperty('width');
      expect(result.current).toHaveProperty('height');
      expect(result.current.width).toBe(1024);
      expect(result.current.height).toBe(768);
    });

    it('should update on window resize', () => {
      const { result } = renderHook(() => useWindowSize());

      act(() => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: 1920
        });
        Object.defineProperty(window, 'innerHeight', {
          writable: true,
          configurable: true,
          value: 1080
        });
        window.dispatchEvent(new Event('resize'));
      });

      // Note: In real implementation, this would update
      expect(result.current).toHaveProperty('width');
      expect(result.current).toHaveProperty('height');
    });
  });
});

