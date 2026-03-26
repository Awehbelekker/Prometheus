/**
 * E2E Tests for Authentication Flow
 */

import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    
    // Check for login form elements
    await expect(page.locator('text=Login')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/login');
    
    // Click submit without filling fields
    await page.click('button[type="submit"]');
    
    // Check for validation messages
    await expect(page.locator('text=/required|cannot be empty/i')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Check for error message
    await expect(page.locator('text=/invalid|incorrect|failed/i')).toBeVisible();
  });

  test('should navigate to signup page', async ({ page }) => {
    await page.goto('/login');
    
    // Click on signup link
    await page.click('text=/sign up|create account|register/i');
    
    // Check if redirected to signup page
    await expect(page).toHaveURL(/.*signup|register/);
  });

  test('should display forgot password link', async ({ page }) => {
    await page.goto('/login');
    
    // Check for forgot password link
    await expect(page.locator('text=/forgot password/i')).toBeVisible();
  });
});

test.describe('Signup', () => {
  test('should display signup form', async ({ page }) => {
    await page.goto('/signup');
    
    // Check for signup form elements
    await expect(page.locator('text=/sign up|create account/i')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should validate password strength', async ({ page }) => {
    await page.goto('/signup');
    
    // Fill in weak password
    await page.fill('input[type="password"]', '123');
    
    // Check for password strength indicator
    await expect(page.locator('text=/weak|strong|password strength/i')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/signup');
    
    // Fill in invalid email
    await page.fill('input[type="email"]', 'invalid-email');
    await page.click('button[type="submit"]');
    
    // Check for validation message
    await expect(page.locator('text=/valid email|email format/i')).toBeVisible();
  });
});

test.describe('Session Management', () => {
  test('should persist session after page reload', async ({ page }) => {
    // This test assumes user is already logged in
    await page.goto('/dashboard');
    
    // Reload page
    await page.reload();
    
    // Should still be on dashboard (not redirected to login)
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test('should logout successfully', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Click logout button
    await page.click('text=/logout|sign out/i');
    
    // Should be redirected to login page
    await expect(page).toHaveURL(/.*login/);
  });
});

test.describe('Protected Routes', () => {
  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Clear cookies to simulate logged out state
    await page.context().clearCookies();
    
    // Try to access protected route
    await page.goto('/dashboard');
    
    // Should be redirected to login
    await expect(page).toHaveURL(/.*login/);
  });

  test('should allow access to public routes', async ({ page }) => {
    // Clear cookies
    await page.context().clearCookies();
    
    // Access public route
    await page.goto('/');
    
    // Should not be redirected
    await expect(page).toHaveURL('/');
  });
});

