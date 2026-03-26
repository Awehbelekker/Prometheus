/**
 * E2E Tests for Gamification Features
 */

import { test, expect } from '@playwright/test';

test.describe('Gamification - XP and Levels', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display user XP and level', async ({ page }) => {
    // Check for XP display
    await expect(page.locator('text=/Level [0-9]+/i')).toBeVisible();
    await expect(page.locator('text=/[0-9]+ XP/i')).toBeVisible();
  });

  test('should show XP progress bar', async ({ page }) => {
    // Check for progress bar
    await expect(page.locator('[role="progressbar"]')).toBeVisible();
  });

  test('should display XP to next level', async ({ page }) => {
    // Check for next level info
    await expect(page.locator('text=/next level|to level/i')).toBeVisible();
  });
});

test.describe('Gamification - Achievements', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to achievements page', async ({ page }) => {
    // Click on achievements
    await page.click('text=Achievements');
    
    // Check URL
    await expect(page).toHaveURL(/.*achievements/);
  });

  test('should display achievement cards', async ({ page }) => {
    await page.goto('/achievements');
    
    // Check for achievement cards
    const achievementCards = page.locator('[data-testid="achievement-card"]');
    await expect(achievementCards.first()).toBeVisible();
  });

  test('should show locked and unlocked achievements', async ({ page }) => {
    await page.goto('/achievements');
    
    // Check for locked/unlocked indicators
    await expect(page.locator('text=/locked|unlocked/i')).toBeVisible();
  });

  test('should display achievement details on click', async ({ page }) => {
    await page.goto('/achievements');
    
    // Click on first achievement
    await page.locator('[data-testid="achievement-card"]').first().click();
    
    // Check for modal or details
    await expect(page.locator('[role="dialog"]')).toBeVisible();
  });

  test('should filter achievements by category', async ({ page }) => {
    await page.goto('/achievements');
    
    // Click on filter
    await page.click('text=/filter|category/i');
    
    // Select a category
    await page.click('text=/trading|social|learning/i');
    
    // Check that filter is applied
    await expect(page.locator('text=/filtered|showing/i')).toBeVisible();
  });
});

test.describe('Gamification - Leaderboard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/leaderboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display leaderboard table', async ({ page }) => {
    // Check for table headers
    await expect(page.locator('text=Rank')).toBeVisible();
    await expect(page.locator('text=/Player|User/i')).toBeVisible();
    await expect(page.locator('text=/Score|XP/i')).toBeVisible();
  });

  test('should show top 3 with special styling', async ({ page }) => {
    // Check for trophy icons or special styling
    await expect(page.locator('[data-testid="trophy-icon"]').first()).toBeVisible();
  });

  test('should switch between leaderboard types', async ({ page }) => {
    // Click on different tabs
    await page.click('text=XP');
    await expect(page.locator('text=/total xp/i')).toBeVisible();
    
    await page.click('text=Returns');
    await expect(page.locator('text=/return|profit/i')).toBeVisible();
    
    await page.click('text=/Win Rate/i');
    await expect(page.locator('text=/win rate|%/i')).toBeVisible();
  });

  test('should highlight current user', async ({ page }) => {
    // Check if current user is highlighted
    const userRow = page.locator('[data-testid="current-user-row"]');
    await expect(userRow).toBeVisible();
  });

  test('should refresh leaderboard data', async ({ page }) => {
    // Click refresh button
    await page.click('[aria-label="refresh"]');
    
    // Check for loading indicator
    await expect(page.locator('[role="progressbar"]')).toBeVisible();
  });
});

test.describe('Gamification - Badges and Streaks', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display earned badges', async ({ page }) => {
    // Navigate to profile or badges section
    await page.click('text=/badges|profile/i');
    
    // Check for badge display
    await expect(page.locator('[data-testid="badge"]').first()).toBeVisible();
  });

  test('should show current streak', async ({ page }) => {
    // Check for streak display
    await expect(page.locator('text=/[0-9]+ day streak/i')).toBeVisible();
  });

  test('should display streak calendar', async ({ page }) => {
    // Click on streak
    await page.click('text=/streak/i');
    
    // Check for calendar view
    await expect(page.locator('[data-testid="streak-calendar"]')).toBeVisible();
  });
});

test.describe('Gamification - Challenges', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/challenges');
    await page.waitForLoadState('networkidle');
  });

  test('should display active challenges', async ({ page }) => {
    // Check for challenge cards
    await expect(page.locator('[data-testid="challenge-card"]').first()).toBeVisible();
  });

  test('should show challenge progress', async ({ page }) => {
    // Check for progress indicators
    await expect(page.locator('[role="progressbar"]')).toBeVisible();
    await expect(page.locator('text=/[0-9]+%/i')).toBeVisible();
  });

  test('should display challenge rewards', async ({ page }) => {
    // Click on challenge
    await page.locator('[data-testid="challenge-card"]').first().click();
    
    // Check for rewards display
    await expect(page.locator('text=/reward|xp|badge/i')).toBeVisible();
  });

  test('should filter challenges by status', async ({ page }) => {
    // Click on filter
    await page.click('text=/all|active|completed/i');
    
    // Select completed
    await page.click('text=Completed');
    
    // Check that filter is applied
    await expect(page.locator('text=/completed/i')).toBeVisible();
  });
});

test.describe('Gamification - Notifications', () => {
  test('should show achievement unlock notification', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Simulate achievement unlock (this would normally happen from backend)
    // Check for notification
    await expect(page.locator('text=/achievement unlocked|congratulations/i')).toBeVisible({ timeout: 10000 });
  });

  test('should show level up notification', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check for level up notification
    await expect(page.locator('text=/level up|leveled up/i')).toBeVisible({ timeout: 10000 });
  });

  test('should display XP gain animation', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Perform action that gives XP (e.g., complete a trade)
    // Check for XP animation
    await expect(page.locator('[data-testid="xp-animation"]')).toBeVisible({ timeout: 10000 });
  });
});

