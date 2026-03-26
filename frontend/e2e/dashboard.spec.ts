/**
 * E2E Tests for PROMETHEUS Dashboard
 */

import { test, expect } from '@playwright/test';

test.describe('User Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/dashboard');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
  });

  test('should load dashboard successfully', async ({ page }) => {
    // Check if dashboard title is visible
    await expect(page.locator('text=Dashboard')).toBeVisible();
    
    // Check if main navigation is present
    await expect(page.locator('[role="navigation"]')).toBeVisible();
  });

  test('should display portfolio overview', async ({ page }) => {
    // Check for portfolio card
    await expect(page.locator('text=Portfolio')).toBeVisible();
    
    // Check for portfolio value
    await expect(page.locator('text=/\\$[0-9,]+/')).toBeVisible();
  });

  test('should display trading metrics', async ({ page }) => {
    // Check for metrics cards
    await expect(page.locator('text=Total Return')).toBeVisible();
    await expect(page.locator('text=Win Rate')).toBeVisible();
  });

  test('should navigate to different sections', async ({ page }) => {
    // Click on Portfolio tab
    await page.click('text=Portfolio');
    await expect(page).toHaveURL(/.*portfolio/);
    
    // Click on Trades tab
    await page.click('text=Trades');
    await expect(page).toHaveURL(/.*trades/);
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if mobile menu button is visible
    await expect(page.locator('[aria-label="menu"]')).toBeVisible();
  });
});

test.describe('Gamification Features', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display XP and level', async ({ page }) => {
    // Check for XP display
    await expect(page.locator('text=/XP|Level/')).toBeVisible();
  });

  test('should display achievements', async ({ page }) => {
    // Navigate to achievements
    await page.click('text=Achievements');
    
    // Check for achievements list
    await expect(page.locator('[data-testid="achievement-card"]').first()).toBeVisible();
  });

  test('should display leaderboard', async ({ page }) => {
    // Navigate to leaderboard
    await page.click('text=Leaderboard');
    
    // Check for leaderboard table
    await expect(page.locator('text=Rank')).toBeVisible();
    await expect(page.locator('text=Player')).toBeVisible();
  });
});

test.describe('Trading Interface', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should open trade modal', async ({ page }) => {
    // Click on trade button
    await page.click('text=Start Trading');
    
    // Check if trade modal is visible
    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  test('should display market data', async ({ page }) => {
    // Check for stock prices
    await expect(page.locator('text=/\\$[0-9]+\\.[0-9]{2}/')).toBeVisible();
  });

  test('should filter trades', async ({ page }) => {
    // Navigate to trades
    await page.click('text=Trades');
    
    // Apply filter
    await page.click('text=Filter');
    await page.click('text=Winning Trades');
    
    // Check if filter is applied
    await expect(page.locator('text=Winning Trades')).toBeVisible();
  });
});

test.describe('Accessibility', () => {
  test('should have no accessibility violations', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Check for proper heading hierarchy
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThan(0);
    
    // Check for alt text on images
    const images = await page.locator('img').all();
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
    
    // Check for proper button labels
    const buttons = await page.locator('button').all();
    for (const button of buttons) {
      const ariaLabel = await button.getAttribute('aria-label');
      const text = await button.textContent();
      expect(ariaLabel || text).toBeTruthy();
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Check if focus is visible
    const focusedElement = await page.locator(':focus');
    await expect(focusedElement).toBeVisible();
  });
});

test.describe('Performance', () => {
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    const loadTime = Date.now() - startTime;
    
    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should have good Core Web Vitals', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Measure performance metrics
    const metrics = await page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      return {
        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
        loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
      };
    });
    
    // DOM Content Loaded should be under 2 seconds
    expect(metrics.domContentLoaded).toBeLessThan(2000);
  });
});

