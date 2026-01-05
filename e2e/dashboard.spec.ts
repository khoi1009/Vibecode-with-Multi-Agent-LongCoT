import { test, expect } from '@playwright/test';

test.describe('Dashboard UI and Responsiveness', () => {
  test('should load the dashboard and display main elements', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Aether/); // Check title contains "Aether"
    await expect(page.locator('h1')).toContainText('AI Analytics Dashboard'); // Main heading
    await expect(page.locator('[data-testid="global-sales-feed"]')).toBeVisible(); // Real-time feed container
    await expect(page.locator('[data-testid="ai-insight-sidebar"]')).toBeVisible(); // AI Sidebar container
    await expect(page.locator('[data-testid="main-dashboard-charts"]')).toBeVisible(); // Main charts area

    // Check for at least one Recharts chart (assuming a common SVG structure)
    await expect(page.locator('svg.recharts-surface')).toBeVisible();
  });

  test('should be responsive on mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE dimensions
    await page.goto('/');

    // Check if elements adapt to mobile layout
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('[data-testid="global-sales-feed"]')).toBeVisible();
    // Assuming sidebar might be hidden or minimized on mobile
    await expect(page.locator('[data-testid="ai-insight-sidebar"]')).toBeHidden(); 
    await expect(page.locator('[data-testid="main-dashboard-charts"]')).toBeVisible();

    // Verify no horizontal scrollbar
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
  });
});
