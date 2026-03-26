/**
 * E2E Tests for Social Features
 */

import { test, expect } from '@playwright/test';

test.describe('User Profiles', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should navigate to user profile', async ({ page }) => {
    // Click on profile link
    await page.click('text=/profile|my profile/i');
    
    // Check URL
    await expect(page).toHaveURL(/.*profile/);
  });

  test('should display user information', async ({ page }) => {
    await page.goto('/profile');
    
    // Check for user info
    await expect(page.locator('text=/username|email/i')).toBeVisible();
    await expect(page.locator('[data-testid="user-avatar"]')).toBeVisible();
  });

  test('should display user stats', async ({ page }) => {
    await page.goto('/profile');
    
    // Check for stats
    await expect(page.locator('text=/total trades|win rate|profit/i')).toBeVisible();
  });

  test('should edit profile', async ({ page }) => {
    await page.goto('/profile');
    
    // Click edit button
    await page.click('text=/edit|edit profile/i');
    
    // Check for edit form
    await expect(page.locator('input[name="username"]')).toBeVisible();
  });

  test('should upload profile picture', async ({ page }) => {
    await page.goto('/profile');
    
    // Click on avatar to upload
    await page.click('[data-testid="avatar-upload"]');
    
    // Check for file input
    await expect(page.locator('input[type="file"]')).toBeVisible();
  });
});

test.describe('Follow System', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/users');
    await page.waitForLoadState('networkidle');
  });

  test('should display list of users', async ({ page }) => {
    // Check for user cards
    await expect(page.locator('[data-testid="user-card"]').first()).toBeVisible();
  });

  test('should follow a user', async ({ page }) => {
    // Click follow button
    await page.locator('[data-testid="follow-button"]').first().click();
    
    // Check that button changes to "Following"
    await expect(page.locator('text=Following').first()).toBeVisible();
  });

  test('should unfollow a user', async ({ page }) => {
    // Click on a user that is already followed
    await page.locator('text=Following').first().click();
    
    // Check that button changes back to "Follow"
    await expect(page.locator('text=/^Follow$/').first()).toBeVisible();
  });

  test('should display followers count', async ({ page }) => {
    await page.goto('/profile');
    
    // Check for followers count
    await expect(page.locator('text=/[0-9]+ followers/i')).toBeVisible();
  });

  test('should display following count', async ({ page }) => {
    await page.goto('/profile');
    
    // Check for following count
    await expect(page.locator('text=/[0-9]+ following/i')).toBeVisible();
  });

  test('should view followers list', async ({ page }) => {
    await page.goto('/profile');
    
    // Click on followers
    await page.click('text=/followers/i');
    
    // Check for followers modal or page
    await expect(page.locator('[data-testid="followers-list"]')).toBeVisible();
  });

  test('should view following list', async ({ page }) => {
    await page.goto('/profile');
    
    // Click on following
    await page.click('text=/following/i');
    
    // Check for following modal or page
    await expect(page.locator('[data-testid="following-list"]')).toBeVisible();
  });
});

test.describe('Notifications', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display notification bell', async ({ page }) => {
    // Check for notification icon
    await expect(page.locator('[data-testid="notification-bell"]')).toBeVisible();
  });

  test('should show unread count badge', async ({ page }) => {
    // Check for badge with count
    await expect(page.locator('[data-testid="notification-badge"]')).toBeVisible();
  });

  test('should open notifications panel', async ({ page }) => {
    // Click on notification bell
    await page.click('[data-testid="notification-bell"]');
    
    // Check for notifications panel
    await expect(page.locator('[data-testid="notifications-panel"]')).toBeVisible();
  });

  test('should display different notification types', async ({ page }) => {
    await page.click('[data-testid="notification-bell"]');
    
    // Check for different notification types
    await expect(page.locator('text=/achievement|trade|follow|level/i')).toBeVisible();
  });

  test('should mark notification as read', async ({ page }) => {
    await page.click('[data-testid="notification-bell"]');
    
    // Click on a notification
    await page.locator('[data-testid="notification-item"]').first().click();
    
    // Check that notification is marked as read
    await expect(page.locator('[data-testid="notification-item"]').first()).toHaveClass(/read/);
  });

  test('should mark all as read', async ({ page }) => {
    await page.click('[data-testid="notification-bell"]');
    
    // Click mark all as read
    await page.click('text=/mark all as read/i');
    
    // Check that badge disappears
    await expect(page.locator('[data-testid="notification-badge"]')).not.toBeVisible();
  });

  test('should filter notifications by type', async ({ page }) => {
    await page.click('[data-testid="notification-bell"]');
    
    // Click on filter
    await page.click('text=/all|achievements|trades|social/i');
    
    // Select a filter
    await page.click('text=Achievements');
    
    // Check that filter is applied
    await expect(page.locator('text=/achievement/i')).toBeVisible();
  });
});

test.describe('Social Feed', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/feed');
    await page.waitForLoadState('networkidle');
  });

  test('should display social feed', async ({ page }) => {
    // Check for feed items
    await expect(page.locator('[data-testid="feed-item"]').first()).toBeVisible();
  });

  test('should show user activities', async ({ page }) => {
    // Check for different activity types
    await expect(page.locator('text=/traded|achieved|followed|leveled up/i')).toBeVisible();
  });

  test('should like a post', async ({ page }) => {
    // Click like button
    await page.locator('[data-testid="like-button"]').first().click();
    
    // Check that like count increases
    await expect(page.locator('text=/[0-9]+ likes/i')).toBeVisible();
  });

  test('should comment on a post', async ({ page }) => {
    // Click comment button
    await page.locator('[data-testid="comment-button"]').first().click();
    
    // Type comment
    await page.fill('[data-testid="comment-input"]', 'Great trade!');
    
    // Submit comment
    await page.click('[data-testid="submit-comment"]');
    
    // Check that comment appears
    await expect(page.locator('text=Great trade!')).toBeVisible();
  });

  test('should share a post', async ({ page }) => {
    // Click share button
    await page.locator('[data-testid="share-button"]').first().click();
    
    // Check for share modal
    await expect(page.locator('[data-testid="share-modal"]')).toBeVisible();
  });

  test('should filter feed by activity type', async ({ page }) => {
    // Click on filter
    await page.click('text=/filter|all activities/i');
    
    // Select a filter
    await page.click('text=/trades|achievements|follows/i');
    
    // Check that filter is applied
    await expect(page.locator('[data-testid="active-filter"]')).toBeVisible();
  });
});

test.describe('User Search', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/users');
    await page.waitForLoadState('networkidle');
  });

  test('should search for users', async ({ page }) => {
    // Type in search box
    await page.fill('[data-testid="user-search"]', 'john');
    
    // Check for search results
    await expect(page.locator('[data-testid="user-card"]').first()).toBeVisible();
  });

  test('should show no results message', async ({ page }) => {
    // Type non-existent user
    await page.fill('[data-testid="user-search"]', 'nonexistentuser12345');
    
    // Check for no results message
    await expect(page.locator('text=/no users found|no results/i')).toBeVisible();
  });

  test('should filter users by criteria', async ({ page }) => {
    // Click on filter
    await page.click('text=/filter/i');
    
    // Select criteria
    await page.click('text=/top traders|most followed|active/i');
    
    // Check that filter is applied
    await expect(page.locator('[data-testid="user-card"]').first()).toBeVisible();
  });
});

