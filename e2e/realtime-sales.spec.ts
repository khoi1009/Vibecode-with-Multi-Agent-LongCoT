import { test, expect } from '@playwright/test';

test.describe('Real-time Global Sales Feed', () => {
  test('should display initial sales data and update in real-time', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('[data-testid="global-sales-feed"]')).toBeVisible();

    // Expect some initial sales data to be rendered (e.g., a list item or text)
    const initialSalesCount = await page.locator('[data-testid="sales-item"]').count();
    expect(initialSalesCount).toBeGreaterThan(0);

    // Wait for a few seconds to observe real-time updates (simulated via WebSocket)
    // This assumes the WebSocket simulation will push new data within a few seconds
    await page.waitForTimeout(5000); // Wait 5 seconds for updates

    // After waiting, expect the number of sales items to have increased
    const updatedSalesCount = await page.locator('[data-testid="sales-item"]').count();
    expect(updatedSalesCount).toBeGreaterThan(initialSalesCount);
    
    // Optionally, check if the latest item has a specific structure
    await expect(page.locator('[data-testid="sales-item"]').first()).toContainText(/Sale ID|Amount/);
  });
});
